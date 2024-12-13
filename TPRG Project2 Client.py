import os
import json
import time
import socket
import PySimpleGUI as sg  # GUI library

# Header
"""
Clientxxx.py
This script collects system data using vcgencmd, sends the data to a server, and features a GUI.
Author: [Doyun Kim]
Date: [December 9th 2024]
"""

# Check if running on a Raspberry Pi
def is_running_on_pi():
    return os.uname().machine.startswith("arm")

if not is_running_on_pi():
    print("This script must be run on a Raspberry Pi.")
    exit(0)

# Function to gather data from the Pi
def get_pi_data(iteration):
    """Collates system data from the Raspberry Pi using vcgencmd."""
    try:
        data = {
            "iteration": iteration,
            "core_temp": float(os.popen("vcgencmd measure_temp").readline().strip()[5:-2]),
            "gpu_freq": float(os.popen("vcgencmd measure_clock core").readline().split("=")[1]) / 1_000_000,
            "cpu_freq": float(os.popen("vcgencmd measure_clock arm").readline().split("=")[1]) / 1_000_000,
            "volts": float(os.popen("vcgencmd measure_volts").readline().strip()[5:-1]),
            "throttled": os.popen("vcgencmd get_throttled").readline().strip()
        }
        return data
    except Exception as e:
        print(f"Error gathering data: {e}")
        return None

# GUI
layout = [
    [sg.Text("Client Status:"), sg.Text("🔴", key="-LED-", size=(2, 1))],
    [sg.Button("Exit")]
]

window = sg.Window("Client", layout, finalize=True)

# Networking setup
HOST = "192.168.2.49"
PORT = 65432
BUFFER_SIZE = 1024

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        for i in range(50):  # Send 50 iterations
            data = get_pi_data(i)
            if data:
                json_data = json.dumps(data)
                s.sendall(json_data.encode())
                print(f"Sent: {json_data}")
                window["-LED-"].update("🟢")
                time.sleep(2)  # 2-second interval
            else:
                print("No data to send.")

        print("Completed data transmission.")
        window["-LED-"].update("🔴")
except Exception as e:
    print(f"Connection error: {e}")

# Handle GUI events
while True:
    event, _ = window.read(timeout=100)
    if event == sg.WINDOW_CLOSED or event == "Exit":
        break

window.close()