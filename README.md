# Hamtastic
Using Python/Flask/Node-red to send messages from meshtastic to HF radios through js8call and FLdigi

You'll need to install the following Python packages:

Flask: For creating the web server to handle HTTP requests.
pyserial: For serial communication with the Meshtastic device.
requests: For making HTTP requests to communicate with Node-RED.
json: For handling JSON data.
Custom js8net library: For JS8Call communications (make sure this library is installed).
Install these packages using pip:

bash
Copy code
pip install flask pyserial requests json
Ensure the custom js8net library is available and installed as it is used in the JS8Call script.

Node-RED Dependencies
The following Node-RED nodes are required:

node-red-node-serialport: For serial communication.
node-red-dashboard: If using any UI components.
node-red-contrib-http-request: For making HTTP requests.
node-red-contrib-json: For handling JSON data.
Install these nodes using the Node-RED palette manager or via npm:

bash
Copy code
npm install node-red-node-serialport node-red-dashboard node-red-contrib-http-request node-red-contrib-json
Node-RED Flow Setup
The key components of my Node-RED flow include:

HTTP In and HTTP Request nodes: For handling incoming and outgoing HTTP requests.
Inject nodes: For testing purposes and automated triggers.
Function nodes: For processing and preparing payloads.
Switch nodes: For routing messages based on conditions.
Debug nodes: For logging and debugging messages.
Python Script Setup
I have two main Python scripts:

MeshtasticImport.py: Handles Meshtastic integration.
Node-red-Js8call.py: Handles JS8Call integration.
Make sure these scripts are set up to run as services or background processes on your Raspberry Pi. I recommend using systemd to manage these scripts.

Example of systemd Service File:
Create a service file for each Python script, e.g., meshtastic.service:

ini
Copy code
[Unit]
Description=Meshtastic Integration Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/MeshtasticImport.py
WorkingDirectory=/path/to
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
Enable and start the service:

bash
Copy code
sudo systemctl enable meshtastic.service
sudo systemctl start meshtastic.service
Node-RED Flow
Import the Node-redFlow.json file into Node-RED:

Open the Node-RED editor.
Go to the menu (three horizontal lines) > Import > Clipboard.
Paste the contents of the Node-redFlow.json file.
Click "Import" and then deploy the flow.

Also i dont know how to link JS8net but thanks bro for making your code, worked great. 
