import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import serial
import serial.tools.list_ports
import threading
import time
from PIL import Image
import pystray

class EvilBW16GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Evil-BW16 Control Panel")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.root.iconbitmap('icon.ico')

        self.serial_port = None
        self.is_connected = False
        self.read_thread = None
        self.stop_reading = threading.Event()

        self.setup_connection_frame()
        self.setup_command_frame()
        self.setup_output_frame()

        self.tray_icon = None
        self.setup_tray_icon()

        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

    def setup_connection_frame(self):
        frame = ttk.LabelFrame(self.root, text="Connection")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Serial Port:").grid(column=0, row=0, padx=5, pady=5, sticky="W")
        self.port_combo = ttk.Combobox(frame, values=self.get_serial_ports(), state="readonly")
        self.port_combo.grid(column=1, row=0, padx=5, pady=5, sticky="W")
        if self.port_combo['values']:
            self.port_combo.current(0)

        self.refresh_button = ttk.Button(frame, text="Refresh", command=self.refresh_ports)
        self.refresh_button.grid(column=2, row=0, padx=5, pady=5, sticky="W")

        ttk.Label(frame, text="Baud Rate:").grid(column=3, row=0, padx=5, pady=5, sticky="W")
        self.baud_combo = ttk.Combobox(frame, values=[9600, 19200, 38400, 57600, 115200], state="readonly")
        self.baud_combo.grid(column=4, row=0, padx=5, pady=5, sticky="W")
        self.baud_combo.set(115200)

        self.connect_button = ttk.Button(frame, text="Connect", command=self.toggle_connection)
        self.connect_button.grid(column=5, row=0, padx=5, pady=5, sticky="W")

        self.status_label = ttk.Label(frame, text="Not Connected", foreground="red")
        self.status_label.grid(column=6, row=0, padx=5, pady=5, sticky="W")

    def setup_command_frame(self):
        frame = ttk.LabelFrame(self.root, text="Commands")
        frame.pack(fill="x", padx=10, pady=5)

        self.start_button = ttk.Button(frame, text="Start", command=lambda: self.send_command("start"))
        self.start_button.grid(column=0, row=0, padx=5, pady=5)

        self.stop_button = ttk.Button(frame, text="Stop", command=lambda: self.send_command("stop"))
        self.stop_button.grid(column=1, row=0, padx=5, pady=5)

        self.scan_button = ttk.Button(frame, text="Scan", command=lambda: self.send_command("scan"))
        self.scan_button.grid(column=2, row=0, padx=5, pady=5)

        self.results_button = ttk.Button(frame, text="Results", command=lambda: self.send_command("results"))
        self.results_button.grid(column=3, row=0, padx=5, pady=5)

        self.info_button = ttk.Button(frame, text="Info", command=lambda: self.send_command("info"))
        self.info_button.grid(column=4, row=0, padx=5, pady=5)

        self.help_button = ttk.Button(frame, text="Help", command=lambda: self.send_command("help"))
        self.help_button.grid(column=5, row=0, padx=5, pady=5)

        param_frame = ttk.LabelFrame(frame, text="Set Parameters")
        param_frame.grid(column=0, row=1, columnspan=6, padx=5, pady=5, sticky="W")

        ttk.Label(param_frame, text="Cycle Delay (ms):").grid(column=0, row=0, padx=5, pady=2, sticky="E")
        self.cycle_delay_entry = ttk.Entry(param_frame, width=10)
        self.cycle_delay_entry.grid(column=1, row=0, padx=5, pady=2, sticky="W")
        self.cycle_delay_entry.insert(0, "2000")

        ttk.Label(param_frame, text="Scan Time (ms):").grid(column=2, row=0, padx=5, pady=2, sticky="E")
        self.scan_time_entry = ttk.Entry(param_frame, width=10)
        self.scan_time_entry.grid(column=3, row=0, padx=5, pady=2, sticky="W")
        self.scan_time_entry.insert(0, "5000")

        ttk.Label(param_frame, text="Num Frames:").grid(column=4, row=0, padx=5, pady=2, sticky="E")
        self.num_frames_entry = ttk.Entry(param_frame, width=10)
        self.num_frames_entry.grid(column=5, row=0, padx=5, pady=2, sticky="W")
        self.num_frames_entry.insert(0, "3")

        ttk.Label(param_frame, text="Start Channel:").grid(column=0, row=1, padx=5, pady=2, sticky="E")
        self.start_channel_entry = ttk.Entry(param_frame, width=10)
        self.start_channel_entry.grid(column=1, row=1, padx=5, pady=2, sticky="W")
        self.start_channel_entry.insert(0, "1")

        ttk.Label(param_frame, text="Scan Between Cycles:").grid(column=2, row=1, padx=5, pady=2, sticky="E")
        self.scan_cycles_var = tk.StringVar(value="off")
        self.scan_cycles_combo = ttk.Combobox(param_frame, textvariable=self.scan_cycles_var, values=["on", "off"], state="readonly", width=8)
        self.scan_cycles_combo.grid(column=3, row=1, padx=5, pady=2, sticky="W")

        ttk.Label(param_frame, text="LEDs:").grid(column=4, row=1, padx=5, pady=2, sticky="E")
        self.led_var = tk.StringVar(value="on")
        self.led_combo = ttk.Combobox(param_frame, textvariable=self.led_var, values=["on", "off"], state="readonly", width=8)
        self.led_combo.grid(column=5, row=1, padx=5, pady=2, sticky="W")

        self.apply_params_button = ttk.Button(param_frame, text="Apply", command=self.apply_parameters)
        self.apply_params_button.grid(column=6, row=0, padx=5, pady=2)

        target_frame = ttk.LabelFrame(frame, text="Target APs")
        target_frame.grid(column=0, row=2, columnspan=6, padx=5, pady=5, sticky="W")

        ttk.Label(target_frame, text="Target Indices (comma-separated):").grid(column=0, row=0, padx=5, pady=2, sticky="E")
        self.target_entry = ttk.Entry(target_frame, width=30)
        self.target_entry.grid(column=1, row=0, padx=5, pady=2, sticky="W")

        self.set_target_button = ttk.Button(target_frame, text="Set Target", command=self.set_target)
        self.set_target_button.grid(column=2, row=0, padx=5, pady=2, sticky="W")

        custom_cmd_frame = ttk.LabelFrame(frame, text="Custom Command")
        custom_cmd_frame.grid(column=0, row=3, columnspan=6, padx=5, pady=5, sticky="W")

        ttk.Label(custom_cmd_frame, text="Command:").grid(column=0, row=0, padx=5, pady=2, sticky="E")
        self.custom_cmd_entry = ttk.Entry(custom_cmd_frame, width=50)
        self.custom_cmd_entry.grid(column=1, row=0, padx=5, pady=2, sticky="W")

        self.custom_cmd_button = ttk.Button(custom_cmd_frame, text="Send", command=self.send_custom_command)
        self.custom_cmd_button.grid(column=2, row=0, padx=5, pady=2, sticky="W")

    def setup_output_frame(self):
        frame = ttk.LabelFrame(self.root, text="Device Output")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.output_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, state='disabled', height=25)
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def refresh_ports(self):
        current_selection = self.port_combo.get()
        ports = self.get_serial_ports()
        self.port_combo['values'] = ports
        if ports:
            if current_selection in ports:
                self.port_combo.set(current_selection)
            else:
                self.port_combo.current(0)
        else:
            self.port_combo.set('')

        self.log_output("Ports refreshed.\n")

    def toggle_connection(self):
        if not self.is_connected:
            selected_port = self.port_combo.get()
            baud_rate = self.baud_combo.get()
            if not selected_port:
                messagebox.showerror("Error", "No serial port selected.")
                return
            try:
                self.serial_port = serial.Serial(selected_port, baudrate=int(baud_rate), timeout=1)
                self.is_connected = True
                self.connect_button.config(text="Disconnect")
                self.status_label.config(text="Connected", foreground="green")
                self.log_output(f"Connected to {selected_port} at {baud_rate} baud.\n")
                # Start reading thread
                self.stop_reading.clear()
                self.read_thread = threading.Thread(target=self.read_from_port, daemon=True)
                self.read_thread.start()
            except serial.SerialException as e:
                messagebox.showerror("Connection Error", str(e))
        else:
            self.stop_reading.set()
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join()
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.is_connected = False
            self.connect_button.config(text="Connect")
            self.status_label.config(text="Not Connected", foreground="red")
            self.log_output("Disconnected.\n")

    def read_from_port(self):
        while not self.stop_reading.is_set():
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting).decode(errors='replace')
                    if data:
                        self.log_output(data)
                time.sleep(0.1)
            except serial.SerialException:
                self.log_output("Serial connection lost.\n")
                self.toggle_connection()
                break

    def log_output(self, message):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, message)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')

    def send_command(self, command):
        if self.is_connected and self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write((command + "\n").encode())
                self.log_output(f"> {command}\n")
            except serial.SerialException as e:
                messagebox.showerror("Serial Error", str(e))
        else:
            messagebox.showwarning("Warning", "Not connected to any serial port.")

    def send_custom_command(self):
        cmd = self.custom_cmd_entry.get().strip()
        if cmd:
            self.send_command(cmd)
        else:
            messagebox.showwarning("Warning", "Please enter a command.")

    def apply_parameters(self):
        if self.is_connected and self.serial_port and self.serial_port.is_open:
            cycle_delay = self.cycle_delay_entry.get()
            scan_time = self.scan_time_entry.get()
            num_frames = self.num_frames_entry.get()
            start_channel = self.start_channel_entry.get()
            scan_cycles = self.scan_cycles_var.get()
            leds = self.led_var.get()

            commands = [
                f"set cycle_delay {cycle_delay}",
                f"set scan_time {scan_time}",
                f"set num_frames {num_frames}",
                f"set start_channel {start_channel}",
                f"set scan_cycles {scan_cycles}",
                f"set led {leds}"
            ]

            for cmd in commands:
                self.send_command(cmd)
                time.sleep(0.2)
        else:
            messagebox.showwarning("Warning", "Not connected to any serial port.")

    def set_target(self):
        if self.is_connected and self.serial_port and self.serial_port.is_open:
            target_indices = self.target_entry.get().strip()
            if not target_indices:
                messagebox.showerror("Error", "Please enter target indices.")
                return
            command = f"set target {target_indices}"
            self.send_command(command)
        else:
            messagebox.showwarning("Warning", "Not connected to any serial port.")

    def minimize_to_tray(self):
        self.root.withdraw()
        if self.tray_icon is not None:
            self.tray_icon.visible = True

    def restore_from_tray(self):
        self.root.deiconify()
        if self.tray_icon is not None:
            self.tray_icon.visible = False

    def quit_app(self, icon, item):
        icon.visible = False
        icon.stop()
        self.root.quit()

    def setup_tray_icon(self):
        image = Image.open('icon.ico')
        menu = pystray.Menu(
            pystray.MenuItem('Show', lambda icon, item: self.root.after(0, self.restore_from_tray)),
            pystray.MenuItem('Quit', self.quit_app)
        )

        self.tray_icon = pystray.Icon("EvilBW16", image, "Evil-BW16 Control Panel", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

def main():
    root = tk.Tk()
    app = EvilBW16GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
