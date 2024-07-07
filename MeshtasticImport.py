import time
import threading
import requests
import logging
import os
from pubsub import pub
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import serial.tools.list_ports
from flask import Flask, request, jsonify
import meshtastic
import meshtastic.serial_interface

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("meshtastic.log"),
        logging.StreamHandler()
    ]
)

NODE_RED_URL = "http://127.0.0.1:1880/Fuck"  # Updated URL
FLASK_PORT = 5000  # Flask will listen on this port

app = Flask(__name__)

iface = None

def custom_serialize(obj):
    """Recursively convert the object to a JSON-serializable format"""
    if isinstance(obj, dict):
        return {k: custom_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [custom_serialize(i) for i in obj]
    elif isinstance(obj, bytes):
        return obj.hex()
    elif hasattr(obj, '__dict__'):
        return custom_serialize(obj.__dict__)
    else:
        return str(obj)

def on_receive(packet, interface):
    """Called when a packet arrives"""
    logging.info(f"Received packet: {packet}")
    try:
        # Convert the packet to a JSON-serializable format
        serializable_packet = custom_serialize(packet)
        data = {
            'packet': serializable_packet
        }
        headers = {'Content-Type': 'application/json'}
        logging.info(f"Serialized packet data: {data}")

        # Setup retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)

        # Send the POST request and log the full response
        response = http.post(NODE_RED_URL, json=data, headers=headers)
        response.raise_for_status()
        logging.info(f"Forwarded to Node-RED, response status: {response.status_code}, response text: {response.text}")
        
        # Log the response headers for additional debugging
        logging.info(f"Response headers: {response.headers}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
    except Exception as e:
        logging.error(f"Failed to forward message: {e}")

def connect_device():
    """Attempt to connect to the Meshtastic device via serial interface"""
    global iface
    logging.info("Connecting to Meshtastic device...")
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            iface = meshtastic.serial_interface.SerialInterface(devPath=port.device)
            node = iface.localNode
            # Subscribe to specific message types
            pub.subscribe(on_receive, "meshtastic.receive")
            logging.info(f"Connected to Meshtastic device on port {port.device}")
            return iface
        except Exception as e:
            logging.error(f"Failed to connect on port {port.device}: {e}")
            continue
    logging.error("Unable to connect to any Meshtastic device")
    return None

@app.route('/send_message', methods=['POST'])
def send_message():
    global iface
    try:
        content = request.get_json(force=True)
        logging.info(f"Received send_message request: {content}")
        destination = content.get('destination', '^all')
        message = content.get('message', 'Hello from Node-RED!')
        
        if iface:
            iface.sendText(message, destination)
            return jsonify({"status": "success", "message": "Message sent"})
        else:
            return jsonify({"status": "error", "message": "Meshtastic interface not connected"}), 500
    except Exception as e:
        logging.error(f"Error in send_message: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/set_channel', methods=['POST'])
def set_channel():
    global iface
    try:
        content = request.get_json(force=True)
        logging.info(f"Received set_channel request: {content}")
        channel_index = content.get('channel_index', 0)
        channel_name = content.get('channel_name', 'default')
        psk = content.get('psk', None)
        
        if iface:
            channel = iface.localNode.channels[channel_index]
            channel.settings.name = channel_name
            if psk is not None and psk.lower() != 'none':
                channel.settings.psk = psk
            iface.localNode.writeConfig(config_name="saved_channels")
            return jsonify({"status": "success", "message": "Channel settings updated"})
        else:
            return jsonify({"status": "error", "message": "Meshtastic interface not connected"}), 500
    except Exception as e:
        logging.error(f"Error in set_channel: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_channels', methods=['GET'])
def get_channels():
    global iface
    try:
        if iface:
            channels = iface.localNode.channels
            serialized_channels = custom_serialize(channels)
            return jsonify({"status": "success", "channels": serialized_channels})
        else:
            return jsonify({"status": "error", "message": "Meshtastic interface not connected"}), 500
    except Exception as e:
        logging.error(f"Error in get_channels: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def main():
    global iface
    iface = connect_device()
    while True:
        if iface is None:
            iface = connect_device()
            time.sleep(5)
            continue
        try:
            # Start Flask server to listen for incoming HTTP requests
            app.run(port=FLASK_PORT)
        except KeyboardInterrupt:
            logging.info("Stopping script...")
            break
        except Exception as e:
            logging.error(f"Error: {e}")
            iface.close()
            iface = None
            time.sleep(5)

    if iface is not None:
        iface.close()
        logging.info("Disconnected from Meshtastic device.")

if __name__ == "__main__":
    main()