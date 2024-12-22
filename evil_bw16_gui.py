import customtkinter as ctk
import serial
import serial.tools.list_ports
import threading
import time
from PIL import Image
import pystray
import os
import textwrap  # Import textwrap for dedent

class EvilBW16GUI:
    def __init__(self, root):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = root
        self.root.title("Evil-BW16 Control Panel")
        self.root.geometry("900x600")  # Reduced initial window size for smaller screens
        self.root.minsize(800, 500)    # Set minimum window size
        self.root.resizable(True, True)

        # Create main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True)

        # Initialize drawer state
        self.drawer_visible = True

        # Create left drawer
        self.drawer = ctk.CTkFrame(self.main_container, width=200, corner_radius=0)
        self.drawer.pack(side="left", fill="y", padx=0, pady=0)
        self.drawer.pack_propagate(False)  # Prevent drawer from shrinking

        # Create main content area
        self.content_area = ctk.CTkFrame(self.main_container)
        self.content_area.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        # Handle icon loading
        try:
            if os.path.exists("logo.png"):
                self.logo_image = Image.open("logo.png")
                # For window icon
                if os.name == 'nt':  # Windows
                    icon = self.logo_image.copy()
                    icon.save('temp_icon.ico', format='ICO')
                    self.root.iconbitmap('temp_icon.ico')
                    os.remove('temp_icon.ico')
                else:  # Linux/Mac
                    # CTkImage requires a PIL Image, but iconphoto expects a PhotoImage or similar
                    # Thus, convert using CTkImage and get the underlying image
                    ctk_icon = ctk.CTkImage(light_image=self.logo_image, dark_image=self.logo_image)
                    self.root.iconphoto(True, ctk_icon._photo_image)  # Access the internal PhotoImage
            else:
                print("Logo file not found")
                self.logo_image = None
        except Exception as e:
            print(f"Logo loading error: {e}")
            self.logo_image = None

        self.serial_port = None
        self.is_connected = False
        self.read_thread = None
        self.stop_reading = threading.Event()

        self.setup_drawer()
        self.setup_content_area()

        self.tray_icon = None
        self.setup_tray_icon()
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    def setup_drawer(self):
        # Logo at top of drawer
        if hasattr(self, 'logo_image') and self.logo_image:
            ui_logo = self.logo_image.copy()
            ui_logo.thumbnail((100, 100), Image.Resampling.LANCZOS)  # Adjusted size
            ctk_logo = ctk.CTkImage(light_image=ui_logo, dark_image=ui_logo, size=(100, 100))
            logo_label = ctk.CTkLabel(self.drawer, image=ctk_logo, text="")
            logo_label.image = ctk_logo  # Keep a reference to prevent garbage collection
            logo_label.pack(pady=(10, 5))

        # Title under logo
        title_label = ctk.CTkLabel(self.drawer, text="Evil-BW16", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))

        # Connection Frame
        conn_frame = ctk.CTkFrame(self.drawer)
        conn_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(conn_frame, text="Port:").pack(pady=2)
        self.port_combo = ctk.CTkComboBox(conn_frame, values=self.get_serial_ports(), width=180)
        self.port_combo.pack(pady=2)

        self.refresh_button = ctk.CTkButton(conn_frame, text="Refresh", command=self.refresh_ports, width=180)
        self.refresh_button.pack(pady=2)

        ctk.CTkLabel(conn_frame, text="Baud Rate:").pack(pady=2)
        self.baud_combo = ctk.CTkComboBox(conn_frame, values=["9600", "19200", "38400", "57600", "115200"], 
                                         state="readonly", width=180)
        self.baud_combo.pack(pady=2)
        self.baud_combo.set("115200")

        self.connect_button = ctk.CTkButton(conn_frame, text="Connect", command=self.toggle_connection, width=180)
        self.connect_button.pack(pady=5)

        self.status_label = ctk.CTkLabel(conn_frame, text="Not Connected", text_color="red")
        self.status_label.pack(pady=2)

        # Command Buttons Frame with Scrollbar
        cmd_frame_container = ctk.CTkScrollableFrame(self.drawer, width=200, height=400)
        cmd_frame_container.pack(fill="both", expand=True, padx=5, pady=5)

        self.cmd_frame = ctk.CTkFrame(cmd_frame_container)
        self.cmd_frame.pack(fill="both", expand=True)

        # Updated commands list with new selections
        commands = [
            ("⚡ Start Deauth", "start"),                 # Start Deauthentication Attack
            ("⏹️ Stop All", "stop"),                      # Stop All Attacks
            ("🔍 Scan Networks", "scan"),                 # Scan Networks
            ("📊 Show Results", "results"),               # Show Scan Results
            ("🛑 Disassoc Start", "disassoc"),       # Start Disassociation Attack
            ("📡 Beacon Spam Start", "beacon_spam"), # Start Beacon Spam
            ("🎲 Random Attack", "random_attack"),         # Perform Random Attack
            ("ℹ️ Info", "info"),                           # Display Info
            ("❓ Help", "help")                            # Display Help
        ]

        for text, cmd in commands:
            btn = ctk.CTkButton(self.cmd_frame, text=text, 
                              command=lambda c=cmd: self.send_command(c), 
                              width=180,
                              height=30,
                              font=("Arial", 12))
            btn.pack(pady=2, anchor="w")  # Align buttons to the left

    def setup_content_area(self):
        # Parameters Frame
        params_frame = ctk.CTkFrame(self.content_area)
        params_frame.pack(fill="x", padx=5, pady=5)

        # Parameters in a grid layout
        params = [
            ("Cycle Delay (ms):", "cycle_delay_entry", "2000"),
            ("Scan Time (ms):", "scan_time_entry", "5000"),
            ("Num Frames:", "num_frames_entry", "3"),
            ("Start Channel:", "start_channel_entry", "1")
        ]

        for i, (label, attr, default) in enumerate(params):
            row = i // 2
            col = (i % 2) * 2
            ctk.CTkLabel(params_frame, text=label).grid(row=row, column=col, padx=5, pady=2, sticky="e")
            entry = ctk.CTkEntry(params_frame, width=100)
            entry.grid(row=row, column=col+1, padx=5, pady=2, sticky="w")
            entry.insert(0, default)
            setattr(self, attr, entry)

        # Combo boxes row
        ctk.CTkLabel(params_frame, text="Scan Between Cycles:").grid(row=2, column=0, padx=5, pady=2, sticky="e")
        self.scan_cycles_var = ctk.StringVar(value="off")
        self.scan_cycles_combo = ctk.CTkComboBox(params_frame, values=["on", "off"], 
                                                variable=self.scan_cycles_var, width=100)
        self.scan_cycles_combo.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        ctk.CTkLabel(params_frame, text="LEDs:").grid(row=2, column=2, padx=5, pady=2, sticky="e")
        self.led_var = ctk.StringVar(value="on")
        self.led_combo = ctk.CTkComboBox(params_frame, values=["on", "off"], 
                                        variable=self.led_var, width=100)
        self.led_combo.grid(row=2, column=3, padx=5, pady=2, sticky="w")

        self.apply_params_button = ctk.CTkButton(params_frame, text="Apply Parameters", 
                                                command=self.apply_parameters, width=200)
        self.apply_params_button.grid(row=3, column=0, columnspan=4, pady=10)

        # Target Frame
        target_frame = ctk.CTkFrame(self.content_area)
        target_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(target_frame, text="Target Indices:").pack(side="left", padx=5)
        self.target_entry = ctk.CTkEntry(target_frame, width=150)
        self.target_entry.pack(side="left", padx=5)
        self.set_target_button = ctk.CTkButton(target_frame, text="Set Target", 
                                              command=self.set_target, width=100)
        self.set_target_button.pack(side="left", padx=5)

        # Custom Command Frame
        custom_frame = ctk.CTkFrame(self.content_area)
        custom_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(custom_frame, text="Custom Command:").pack(side="left", padx=5)
        self.custom_cmd_entry = ctk.CTkEntry(custom_frame, width=200)
        self.custom_cmd_entry.pack(side="left", padx=5)
        self.custom_cmd_button = ctk.CTkButton(custom_frame, text="Send", 
                                              command=self.send_custom_command, width=100)
        self.custom_cmd_button.pack(side="left", padx=5)

        # Terminal Output
        self.setup_output_frame()

        # Add Clear Button below the terminal output
        clear_button = ctk.CTkButton(self.content_area, text="Clear Output", 
                                     command=self.clear_output, 
                                     width=120,
                                     height=30,
                                     fg_color="red",
                                     hover_color="darkred")
        clear_button.pack(pady=(0, 10))

    def setup_output_frame(self):
        self.output_text = ctk.CTkTextbox(
            self.content_area,
            height=200,  # Adjusted height for smaller screens
            wrap="word",
            font=("Courier", 10),  # Smaller font size
            text_color="#00ff00",
            fg_color="#000000",
        )
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)

        try:
            with open("welcome_msg.txt", "r") as file:
                welcome_msg = file.read().expandtabs(4) 
        except FileNotFoundError:
            welcome_msg = "Welcome message not found."

        self.output_text.insert("1.0", welcome_msg)
        self.output_text.configure(state="disabled")

    def clear_output(self):
        """Clear the terminal output."""
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")
        self.append_output("Terminal output cleared.\n")

    def append_output(self, message):
        """Add text to the output terminal with timestamp"""
        self.output_text.configure(state="normal")
        timestamp = time.strftime("[%H:%M:%S] ", time.localtime())
        self.output_text.insert("end", f"{timestamp}{message}\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def refresh_ports(self):
        current_selection = self.port_combo.get()
        ports = self.get_serial_ports()
        self.port_combo.configure(values=ports)
        if ports:
            if current_selection in ports:
                self.port_combo.set(current_selection)
            else:
                self.port_combo.set(ports[0])
        else:
            self.port_combo.set('')

        self.append_output("Ports refreshed.")

    def toggle_connection(self):
        if not self.is_connected:
            selected_port = self.port_combo.get()
            baud_rate = self.baud_combo.get()
            if not selected_port:
                ctk.CTkMessagebox.show_error("Error", "No serial port selected.")
                return
            try:
                self.serial_port = serial.Serial(selected_port, baudrate=int(baud_rate), timeout=1)
                self.is_connected = True
                self.connect_button.configure(text="Disconnect")
                self.status_label.configure(text="Connected", text_color="green")
                self.append_output(f"Connected to {selected_port} at {baud_rate} baud.")
                self.stop_reading.clear()
                self.read_thread = threading.Thread(target=self.read_from_port, daemon=True)
                self.read_thread.start()
            except serial.SerialException as e:
                ctk.CTkMessagebox.show_error("Connection Error", str(e))
        else:
            self.disconnect_serial()

    def disconnect_serial(self):
        self.stop_reading.set()
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2)
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
                self.append_output("Serial port closed.")
            except Exception as e:
                self.append_output(f"Error closing serial port: {e}")
        self.is_connected = False
        self.connect_button.configure(text="Connect")
        self.status_label.configure(text="Not Connected", text_color="red")
        self.append_output("Disconnected.")

    def read_from_port(self):
        while not self.stop_reading.is_set():
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting).decode(errors='replace')
                    if data:
                        self.append_output(data)
                time.sleep(0.1)
            except serial.SerialException:
                self.append_output("Serial connection lost.")
                self.stop_reading.set()
                self.is_connected = False
                self.connect_button.configure(text="Connect")
                self.status_label.configure(text="Not Connected", text_color="red")
                break
            except Exception as e:
                self.append_output(f"Error reading from serial port: {e}")
                self.stop_reading.set()
                break

    def send_command(self, command):
        if self.is_connected and self.serial_port and self.serial_port.is_open:
            try:
                # Handle special commands that require parameters
                if command == "attack_time":
                    # Prompt user for duration
                    duration = self.prompt_for_duration()
                    if duration:
                        full_command = f"attack_time {duration}"
                        self.serial_port.write((full_command + "\n").encode())
                        self.append_output(f"> {full_command}")
                elif command == "disassoc":
                    full_command = "disassoc"
                    self.serial_port.write((full_command + "\n").encode())
                    self.append_output(f"> {full_command}")
                elif command == "beacon_spam":
                    full_command = "beacon_spam"
                    self.serial_port.write((full_command + "\n").encode())
                    self.append_output(f"> {full_command}")
                else:
                    self.serial_port.write((command + "\n").encode())
                    self.append_output(f"> {command}")
            except serial.SerialException as e:
                ctk.CTkMessagebox.show_error("Serial Error", str(e))
                self.disconnect_serial()
            except Exception as e:
                self.append_output(f"Error sending command: {e}")
        else:
            ctk.CTkMessagebox.show_warning("Warning", "Not connected to any serial port.")

    def prompt_for_duration(self):
        """Prompt the user to enter a duration for the timed attack."""
        duration_window = ctk.CTkToplevel(self.root)
        duration_window.title("Enter Attack Duration")
        duration_window.geometry("300x150")
        duration_window.grab_set()  # Make the window modal

        ctk.CTkLabel(duration_window, text="Enter duration in ms:", font=("Arial", 14)).pack(pady=10)

        duration_entry = ctk.CTkEntry(duration_window, width=200)
        duration_entry.pack(pady=5)
        duration_entry.focus()

        def submit_duration():
            value = duration_entry.get()
            if value.isdigit() and int(value) > 0:
                duration_window.duration = value
                duration_window.destroy()
            else:
                ctk.CTkMessagebox.show_error("Invalid Input", "Please enter a positive integer.")

        submit_button = ctk.CTkButton(duration_window, text="Submit", command=submit_duration)
        submit_button.pack(pady=10)

        self.root.wait_window(duration_window)

        return getattr(duration_window, 'duration', None)

    def send_custom_command(self):
        cmd = self.custom_cmd_entry.get().strip()
        if cmd:
            self.send_command(cmd)
        else:
            ctk.CTkMessagebox.show_warning("Warning", "Please enter a command.")

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
            ctk.CTkMessagebox.show_warning("Warning", "Not connected to any serial port.")

    def set_target(self):
        if self.is_connected and self.serial_port and self.serial_port.is_open:
            target_indices = self.target_entry.get().strip()
            if not target_indices:
                ctk.CTkMessagebox.show_error("Error", "Please enter target indices.")
                return
            command = f"set target {target_indices}"
            self.send_command(command)
        else:
            ctk.CTkMessagebox.show_warning("Warning", "Not connected to any serial port.")

    def minimize_to_tray(self):
        self.root.withdraw()
        if self.tray_icon is not None:
            self.tray_icon.visible = True

    def restore_from_tray(self):
        self.root.deiconify()
        if self.tray_icon is not None:
            self.tray_icon.visible = False

    def quit_app(self, icon=None, item=None):
        self.cleanup()
        if icon:
            icon.visible = False
            icon.stop()
        self.root.quit()

    def setup_tray_icon(self):
        try:
            # Use the already loaded logo image if available, otherwise create a default
            if hasattr(self, 'logo_image') and self.logo_image:
                tray_icon_image = self.logo_image.copy()
                # Resize for tray icon if needed
                tray_icon_image.thumbnail((64, 64), Image.Resampling.LANCZOS)
                # pystray expects a PIL Image
            else:
                tray_icon_image = Image.new('RGB', (64, 64), color='red')
        except Exception as e:
            print(f"Tray icon creation error: {e}")
            tray_icon_image = Image.new('RGB', (64, 64), color='red')

        menu = pystray.Menu(
            pystray.MenuItem('Show', lambda icon, item: self.root.after(0, self.restore_from_tray)),
            pystray.MenuItem('Exit', self.quit_app)
        )

        self.tray_icon = pystray.Icon("EvilBW16", tray_icon_image, "Evil-BW16 Control Panel", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def cleanup(self):
        """Clean up resources before exiting the application."""
        if self.is_connected:
            self.disconnect_serial()

        if self.tray_icon is not None:
            self.tray_icon.visible = False
            self.tray_icon.stop()

def main():
    app = ctk.CTk()  # Initialize the customtkinter application
    app.title("Evil-BW16 Control Panel")
    gui = EvilBW16GUI(app)  # Create an instance of your GUI class

    def on_exit():
        gui.cleanup()
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_exit)
    app.mainloop()  # Start the GUI main loop

if __name__ == "__main__":
    main()  # Run the main function if this script is executed directly
