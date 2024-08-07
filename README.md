# Hamtastic
Using Python/Flask/Node-red to send messages from meshtastic to HF radios through js8call and FLdigi

## You'll need to setup a venv and install the following Python packages:
- venv keeps your python packages isolated so you dont have to worry about falling into library hell.
- Flask: For creating the web server to handle HTTP requests.
- pyserial: For serial communication with the Meshtastic device.
- requests: For making HTTP requests to communicate with Node-RED.
- json: For handling JSON data.
- Js8net library: For JS8Call communications (make sure this library is installed).
- Install these packages using pip:


```
mkdir -p ~/src/                                          # -p says to create the parent directories and not to die if the dir already exists.
cd ~/src
git clone https://github.com/TheWatchMker/Hamtastic      # clone the repo
cd Hamtastic
python -m venv .                                         # create the venv
. bin/activate                                           # makes some env changes so we can pip install to our local venv.
pip install flask pyserial requests json                 # install the stuff
pip install pip@git+https://github.com/jfrancis42/js8net # Ensure the custom js8net library is available and installed as it is used in the JS8Call script.
```

## Node-RED Dependencies
The following Node-RED nodes are required:

- node-red-node-serialport: For serial communication.
- node-red-dashboard: If using any UI components.
- node-red-contrib-http-request: For making HTTP requests.
- node-red-contrib-json: For handling JSON data.
Install these nodes using the Node-RED palette manager or via npm:

```
npm install node-red-node-serialport node-red-dashboard node-red-contrib-http-request node-red-contrib-json
```

## Node-RED Flow Setup
The key components of my Node-RED flow include:

- HTTP In and HTTP Request nodes: For handling incoming and outgoing HTTP requests.
- Inject nodes: For testing purposes and automated triggers.
- Function nodes: For processing and preparing payloads.
- Switch nodes: For routing messages based on conditions.
- Debug nodes: For logging and debugging messages.

## Python Script Setup
I have two main Python scripts:
- MeshtasticImport.py: Handles Meshtastic integration.
- Node-red-Js8call.py: Handles JS8Call integration.
- Make sure these scripts are set up to run as services or background processes on your Raspberry Pi. I recommend using systemd to manage these scripts.

## Systemd setup
### Example of systemd Service File:
Create a service file for each Python script, e.g., /lib/systemd/system/meshtastic.service:

```
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
```
### Enable and start the service:

```
sudo systemctl enable meshtastic.service
sudo systemctl start meshtastic.service
```

## Node-RED Flow
Import the Node-redFlow.json file into Node-RED:

- Open the Node-RED editor.
- Go to the menu (three horizontal lines) > Import > Clipboard.
- Paste the contents of the Node-redFlow.json file.
- Click "Import" and then deploy the flow.

Thanks to [JFrancis42](https://github.com/jfrancis42) for making [JS8Net](https://github.com/jfrancis42/js8net) - It's worked great. 
