import json
import socket
import PySimpleGUI as sg  # GUI library

# Header
"""
Serverxxx.py
This script receives system data from the client and displays it in a GUI.
Author: [Your Name]
Date: [Date]
"""

# Function to start the server
def start_server():
    """Starts the server to receive data from the client."""
    HOST = "192.168.2.49"
    PORT = 65432
    BUFFER_SIZE = 1024

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            print("Server is listening...")
            conn, addr = s.accept()
            print(f"Connection established with {addr}")
            return conn
    except Exception as e:
        print(f"Server error: {e}")
        return None

# GUI
layout = [
    [sg.Text("Current Data from Client")],
    [sg.Text("Iteration:"), sg.Text("", size=(10, 1), key="-ITERATION-")],
    [sg.Text("Core Temp:"), sg.Text("", size=(10, 1), key="-TEMP-")],
    [sg.Text("GPU Freq:"), sg.Text("", size=(10, 1), key="-GPUFREQ-")],
    [sg.Text("CPU Freq:"), sg.Text("", size=(10, 1), key="-CPUFREQ-")],
    [sg.Text("Volts:"), sg.Text("", size=(10, 1), key="-VOLTS-")],
    [sg.Text("Throttled:"), sg.Text("", size=(10, 1), key="-THROTTLED-")],
    [sg.Text("Server Status:"), sg.Text("🔴", key="-LED-", size=(2, 1))],
    [sg.Button("Exit")]
]

window = sg.Window("Server", layout, finalize=True)

# Start server
conn = start_server()

if conn:
    window["-LED-"].update("🟢")

# Handle incoming data and GUI events
try:
    while True:
        event, _ = window.read(timeout=100)
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break

        data = conn.recv(BUFFER_SIZE)
        if not data:
            window["-LED-"].update("🔴")
            break

        decoded_data = json.loads(data.decode())
        window["-ITERATION-"].update(decoded_data["iteration"])
        window["-TEMP-"].update(f"{decoded_data['core_temp']}°C")
        window["-GPUFREQ-"].update(f"{decoded_data['gpu_freq']} MHz")
        window["-CPUFREQ-"].update(f"{decoded_data['cpu_freq']} MHz")
        window["-VOLTS-"].update(f"{decoded_data['volts']} V")
        window["-THROTTLED-"].update(decoded_data["throttled"])

except Exception as e:
    print(f"Error during operation: {e}")
finally:
    if conn:
        conn.close()

window.close()