import time
import threading
import requests
from flask import Flask, request, jsonify
import logging

# Import the Client and Message classes directly from the js8net repository
import sys
sys.path.append('/home/mattm/js8net')  # Update this path to the location of your js8net directory
from js8net import start_net, get_rx_text, send_message, rx_lock, rx_queue

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("js8call_interface.log"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

JS8CALL_HOST = 'localhost'
JS8CALL_PORT = 2442
MAX_MESSAGE_LENGTH = 80  # Adjust based on JS8Call's maximum allowed message length

# Initialize js8net Client
start_net(JS8CALL_HOST, JS8CALL_PORT)

def split_message(message):
    return [message[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(message), MAX_MESSAGE_LENGTH)]

@app.route('/send_message', methods=['POST'])
def send_message_route():
    data = request.json
    message = data.get('message', '')
    destination = data.get('destination', 'ALLCALL')
    try:
        parts = split_message(message)
        for part in parts:
            send_message(f"{destination}: {part}")
            logging.info(f"Sent message part: {part}")
        return jsonify({"status": "success", "response": "Message sent"}), 200
    except Exception as e:
        logging.error(f"Error in send_message: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def listen_for_messages():
    while True:
        try:
            if not rx_queue.empty():
                with rx_lock:
                    message = rx_queue.get()
                    logging.info(f"Received message: {message}")
                    try:
                        # Forward the received message to Node-RED
                        requests.post('http://localhost:1880/receive_message', json={"message": message['value']})
                        logging.info(f"Forwarded message to Node-RED")
                    except Exception as e:
                        logging.error(f"Failed to forward message to Node-RED: {e}")
        except Exception as e:
            logging.error(f"Failed to receive message: {e}")
        time.sleep(1)

if __name__ == '__main__':
    listener_thread = threading.Thread(target=listen_for_messages)
    listener_thread.daemon = True
    listener_thread.start()
    app.run(host='0.0.0.0', port=5003)  # Run on a different port from the FLDIGI interface