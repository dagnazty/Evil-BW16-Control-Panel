from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import serial
import serial.tools.list_ports
import json
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'evil-bw16-secret'
socketio = SocketIO(app)

class SerialManager:
    def __init__(self):
        self.serial_port = None
        self.is_connected = False
        self.read_thread = None
        self.stop_reading = threading.Event()
        self.config = {
            'cycle_delay': '2000',
            'scan_time': '5000',
            'num_frames': '3',
            'start_channel': '1',
            'scan_cycles': 'off',
            'led': 'on'
        }

    def get_serial_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    def connect(self, port, baud_rate):
        try:
            if self.serial_port and self.serial_port.is_open:
                self.disconnect()
            
            self.serial_port = serial.Serial(port, baud_rate, timeout=1)
            self.is_connected = True
            self.stop_reading.clear()
            self.read_thread = threading.Thread(target=self.read_serial)
            self.read_thread.daemon = True
            self.read_thread.start()
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self):
        self.stop_reading.set()
        if self.read_thread:
            self.read_thread.join()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.is_connected = False

    def read_serial(self):
        while not self.stop_reading.is_set() and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode().strip()
                    print(f"Sending data to client: {data}")  # Debug log
                    if "Networks found:" in data:
                        print("Found networks in data!")  # Debug log
                    socketio.emit('serial_data', {'data': data})
            except Exception as e:
                print(f"Read error: {e}")
                break
            time.sleep(0.1)

    def send_command(self, command):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(f"{command}\n".encode())
                return True
            except Exception as e:
                print(f"Send error: {e}")
        return False

    def apply_parameters(self, params):
        if self.is_connected and self.serial_port and self.serial_port.is_open:
            commands = [
                f"set cycle_delay {params['cycle_delay']}",
                f"set scan_time {params['scan_time']}",
                f"set num_frames {params['num_frames']}",
                f"set start_channel {params['start_channel']}",
                f"set scan_cycles {params['scan_cycles']}",
                f"set led {params['led']}"
            ]
            
            for cmd in commands:
                try:
                    self.serial_port.write((cmd + "\n").encode())
                    time.sleep(0.2)
                except Exception as e:
                    return False, str(e)
            return True, "Parameters applied successfully"
        return False, "Not connected to any serial port"

    def set_target(self, target_indices):
        if self.is_connected and self.serial_port and self.serial_port.is_open:
            command = f"set target {target_indices}"
            try:
                self.serial_port.write((command + "\n").encode())
                return True, "Target set successfully"
            except Exception as e:
                return False, str(e)
        return False, "Not connected to any serial port"

serial_manager = SerialManager()

@app.route('/')
def index():
    try:
        with open("static/welcome_msg.txt", "r") as file:
            welcome_msg = file.read()
    except FileNotFoundError:
        welcome_msg = "Welcome message not found."
    return render_template('index.html', welcome_msg=welcome_msg)

@socketio.on('connect')
def handle_connect():
    emit('ports_list', {'ports': serial_manager.get_serial_ports()})

@socketio.on('refresh_ports')
def handle_refresh_ports():
    emit('ports_list', {'ports': serial_manager.get_serial_ports()})

@socketio.on('connect_serial')
def handle_connect_serial(data):
    success = serial_manager.connect(data['port'], int(data['baud_rate']))
    emit('connection_status', {'connected': success})

@socketio.on('disconnect_serial')
def handle_disconnect_serial():
    serial_manager.disconnect()
    emit('connection_status', {'connected': False})

@socketio.on('send_command')
def handle_command(data):
    success = serial_manager.send_command(data['command'])
    emit('command_status', {'success': success})

@socketio.on('apply_parameters')
def handle_apply_parameters(data):
    success, message = serial_manager.apply_parameters(data)
    emit('command_status', {'success': success, 'message': message})

@socketio.on('set_target')
def handle_set_target(data):
    success, message = serial_manager.set_target(data['target'])
    emit('command_status', {'success': success, 'message': message})

if __name__ == '__main__':
    socketio.run(app, debug=True)
