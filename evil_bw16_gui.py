import customtkinter as ctk
import serial
import serial.tools.list_ports
import threading
import time
from PIL import Image, ImageTk
import pystray
import os

class EvilBW16GUI:
    def __init__(self, root):
        ctk.set_appearance_mode("dark")  # Set dark mode as default
        ctk.set_default_color_theme("blue")  # Themes: "blue", "dark-blue", "green"

        self.root = root
        self.root.title("Evil-BW16 Control Panel")
        self.root.geometry("928x1000")  # Initial window size
        self.root.resizable(True, True)  # Make window resizable

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
                    self.root.iconphoto(True, ImageTk.PhotoImage(self.logo_image))
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

        self.setup_theme_switch()
        self.setup_logo_frame()
        self.setup_connection_frame()
        self.setup_command_frame()
        self.setup_target_frame()
        self.setup_output_frame()

        self.tray_icon = None
        self.setup_tray_icon()

        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    def setup_theme_switch(self):
        # Create a frame for the theme switch in the top-right corner
        self.theme_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.theme_frame.pack(side="top", anchor="ne", padx=10, pady=5)

        self.theme_switch_var = ctk.StringVar(value="dark")  # Set initial value to dark
        
        self.theme_switch = ctk.CTkSwitch(
            self.theme_frame,
            text="Dark Mode",
            command=self.toggle_theme,
            variable=self.theme_switch_var,
            onvalue="dark",
            offvalue="light",
            font=("Arial", 12)
        )
        self.theme_switch.pack(padx=10, pady=5)
        self.theme_switch.select()  # Start with dark mode selected

    def toggle_theme(self):
        if self.theme_switch_var.get() == "dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def setup_logo_frame(self):
        frame = ctk.CTkFrame(self.root, corner_radius=10)
        frame.pack(fill="x", padx=10, pady=(2, 2))  # Reduced padding

        if self.logo_image:
            ui_logo = self.logo_image.copy()
            ui_logo.thumbnail((120, 120), Image.Resampling.LANCZOS)  # 120x120 logo size
            logo_label = ctk.CTkLabel(frame, image=ImageTk.PhotoImage(ui_logo), text="")
            logo_label.pack(pady=2)  # Reduced padding

        title_label = ctk.CTkLabel(frame, text="Evil-BW16 Control Panel", font=("Arial", 24, "bold"))
        title_label.pack(pady=2)  # Reduced padding

    def setup_connection_frame(self):
        frame = ctk.CTkFrame(self.root, corner_radius=10)
        frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame, text="Serial Port:").grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.port_combo = ctk.CTkComboBox(frame, values=self.get_serial_ports())
        self.port_combo.grid(column=1, row=0, padx=5, pady=5, sticky="w")
        if self.port_combo.get():
            self.port_combo.set(self.port_combo.get())

        self.refresh_button = ctk.CTkButton(frame, text="Refresh", command=self.refresh_ports)
        self.refresh_button.grid(column=2, row=0, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(frame, text="Baud Rate:").grid(column=3, row=0, padx=5, pady=5, sticky="w")
        self.baud_combo = ctk.CTkComboBox(frame, values=["9600", "19200", "38400", "57600", "115200"], state="readonly")
        self.baud_combo.grid(column=4, row=0, padx=5, pady=5, sticky="w")
        self.baud_combo.set("115200")

        self.connect_button = ctk.CTkButton(frame, text="Connect", command=self.toggle_connection)
        self.connect_button.grid(column=5, row=0, padx=5, pady=5, sticky="w")

        self.status_label = ctk.CTkLabel(frame, text="Not Connected", text_color="red")
        self.status_label.grid(column=6, row=0, padx=5, pady=5, sticky="w")

    def setup_command_frame(self):
        frame = ctk.CTkFrame(self.root, corner_radius=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Button frame for command buttons
        button_frame = ctk.CTkFrame(frame, corner_radius=0)
        button_frame.pack(fill="x", padx=5, pady=5)

        # Create buttons with equal width
        self.start_button = ctk.CTkButton(button_frame, text="Start", command=lambda: self.send_command("start"))
        self.start_button.pack(side="left", padx=5, expand=True)

        self.stop_button = ctk.CTkButton(button_frame, text="Stop", command=lambda: self.send_command("stop"))
        self.stop_button.pack(side="left", padx=5, expand=True)

        self.scan_button = ctk.CTkButton(button_frame, text="Scan", command=lambda: self.send_command("scan"))
        self.scan_button.pack(side="left", padx=5, expand=True)

        self.results_button = ctk.CTkButton(button_frame, text="Results", command=lambda: self.send_command("results"))
        self.results_button.pack(side="left", padx=5, expand=True)

        self.info_button = ctk.CTkButton(button_frame, text="Info", command=lambda: self.send_command("info"))
        self.info_button.pack(side="left", padx=5, expand=True)

        self.help_button = ctk.CTkButton(button_frame, text="Help", command=lambda: self.send_command("help"))
        self.help_button.pack(side="left", padx=5, expand=True)

        # Parameters frame
        params_frame = ctk.CTkFrame(frame, corner_radius=0)
        params_frame.pack(fill="x", padx=5, pady=5)

        # First row of parameters
        row1_frame = ctk.CTkFrame(params_frame, corner_radius=0)
        row1_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(row1_frame, text="Cycle Delay (ms):").pack(side="left", padx=5)
        self.cycle_delay_entry = ctk.CTkEntry(row1_frame, width=100)
        self.cycle_delay_entry.pack(side="left", padx=5)
        self.cycle_delay_entry.insert(0, "2000")

        ctk.CTkLabel(row1_frame, text="Scan Time (ms):").pack(side="left", padx=5)
        self.scan_time_entry = ctk.CTkEntry(row1_frame, width=100)
        self.scan_time_entry.pack(side="left", padx=5)
        self.scan_time_entry.insert(0, "5000")

        ctk.CTkLabel(row1_frame, text="Num Frames:").pack(side="left", padx=5)
        self.num_frames_entry = ctk.CTkEntry(row1_frame, width=100)
        self.num_frames_entry.pack(side="left", padx=5)
        self.num_frames_entry.insert(0, "3")

        # Add Apply button aligned with Help button
        self.apply_params_button = ctk.CTkButton(row1_frame, text="Apply", command=self.apply_parameters)
        self.apply_params_button.pack(side="right", padx=5)

        # Second row of parameters
        row2_frame = ctk.CTkFrame(params_frame, corner_radius=0)
        row2_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(row2_frame, text="Start Channel:").pack(side="left", padx=5)
        self.start_channel_entry = ctk.CTkEntry(row2_frame, width=100)
        self.start_channel_entry.pack(side="left", padx=5)
        self.start_channel_entry.insert(0, "1")

        ctk.CTkLabel(row2_frame, text="Scan Between Cycles:").pack(side="left", padx=5)
        self.scan_cycles_var = ctk.StringVar(value="off")
        self.scan_cycles_combo = ctk.CTkComboBox(row2_frame, values=["on", "off"], variable=self.scan_cycles_var)
        self.scan_cycles_combo.pack(side="left", padx=5)

        ctk.CTkLabel(row2_frame, text="LEDs:").pack(side="left", padx=5)
        self.led_var = ctk.StringVar(value="on")
        self.led_combo = ctk.CTkComboBox(row2_frame, values=["on", "off"], variable=self.led_var)
        self.led_combo.pack(side="left", padx=5)

    def setup_target_frame(self):
        frame = ctk.CTkFrame(self.root, corner_radius=10)
        frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame, text="Target Indices (comma-separated):").grid(column=0, row=0, padx=5, pady=5, sticky="e")
        self.target_entry = ctk.CTkEntry(frame, width=200)
        self.target_entry.grid(column=1, row=0, padx=5, pady=5, sticky="w")

        self.set_target_button = ctk.CTkButton(frame, text="Set Target", command=self.set_target)
        self.set_target_button.grid(column=2, row=0, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Custom Command:").grid(column=0, row=1, padx=5, pady=5, sticky="e")
        self.custom_cmd_entry = ctk.CTkEntry(frame, width=200)
        self.custom_cmd_entry.grid(column=1, row=1, padx=5, pady=5, sticky="w")

        self.custom_cmd_button = ctk.CTkButton(frame, text="Send", command=self.send_custom_command)
        self.custom_cmd_button.grid(column=2, row=1, padx=5, pady=5)

    def setup_output_frame(self):
        frame = ctk.CTkFrame(self.root, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Configure text widget with cyberpunk styling
        self.output_text = ctk.CTkTextbox(
            frame,
            height=400,
            wrap="none",
            font=("Fira Code", 12),  # Primary font choice
            text_color="#00ff00",  # Matrix green
            fg_color="#000000",    # Black background
        )
        
        try:
            self.output_text.configure(font=("Fira Code", 12))
        except:
            try:
                self.output_text.configure(font=("Cascadia Code", 12))
            except:
                self.output_text.configure(font=("Consolas", 12))
        
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add ASCII art welcome message
        welcome_msg = """
 /$$$$$$$$ /$$    /$$ /$$$$$$ /$$         /$$$$$$$  /$$      /$$   /$$    /$$$$$$  
| $$_____/| $$   | $$|_  $$_/| $$        | $$__  $$| $$  /$ | $$ /$$$$   /$$__  $$
| $$      | $$   | $$  | $$  | $$        | $$  \\ $$| $$ /$$$| $$|_  $$  | $$  \\__/
| $$$$$   |  $$ / $$/  | $$  | $$ /$$$$$$| $$$$$$$ | $$/$$ $$ $$  | $$  | $$$$$$$ 
| $$__/    \\  $$ $$/   | $$  | $$|______/| $$__  $$| $$$$_  $$$$  | $$  | $$__  $$
| $$        \\  $$$/    | $$  | $$        | $$  \\ $$| $$$/ \\  $$$  | $$  | $$  \\ $$
| $$$$$$$$   \\  $/    /$$$$$$| $$$$$$$$  | $$$$$$$/| $$/   \\  $$ /$$$$$$|  $$$$$$/
|________/    \\_/    |______/|________/  |_______/ |__/     \\__/|______/ \\______/ 

Evil-BW16 Firmware Dev: 7h30th3r0n3
https://github.com/7h30th3r0n3/Evil-BW16

Evil-BW16 CP Original Author: dagnazty
https://github.com/dagnazty/Evil-BW16-Control-Panel

Fork Editor: Hosseios
https://github.com/Hosseios

                    [ System Initialized - Ready for Input ]
                    [ Type 'help' for available commands ]
"""
        self.output_text.insert("1.0", welcome_msg)
        self.output_text.configure(state="disabled")  # Make read-only initially

    def append_output(self, message):
        """Add text to the output terminal with timestamp"""
        self.output_text.configure(state="normal")
        timestamp = time.strftime("[%H:%M:%S] ", time.localtime())
        self.output_text.insert("end", f"\n{timestamp}{message}")
        self.output_text.see("end")  # Auto-scroll to bottom
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

        self.append_output("Ports refreshed.\n")

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
                self.append_output(f"Connected to {selected_port} at {baud_rate} baud.\n")
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
                self.append_output("Serial port closed.\n")
            except Exception as e:
                self.append_output(f"Error closing serial port: {e}\n")
        self.is_connected = False
        self.connect_button.configure(text="Connect")
        self.status_label.configure(text="Not Connected", text_color="red")
        self.append_output("Disconnected.\n")

    def read_from_port(self):
        while not self.stop_reading.is_set():
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting).decode(errors='replace')
                    if data:
                        self.append_output(data)
                time.sleep(0.1)
            except serial.SerialException:
                self.append_output("Serial connection lost.\n")
                self.stop_reading.set()
                self.is_connected = False
                self.connect_button.configure(text="Connect")
                self.status_label.configure(text="Not Connected", text_color="red")
                break
            except Exception as e:
                self.append_output(f"Error reading from serial port: {e}\n")
                self.stop_reading.set()
                break

    def send_command(self, command):
        if self.is_connected and self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write((command + "\n").encode())
                self.append_output(f"> {command}\n")
            except serial.SerialException as e:
                ctk.CTkMessagebox.show_error("Serial Error", str(e))
                self.disconnect_serial()
            except Exception as e:
                self.append_output(f"Error sending command: {e}\n")
        else:
            ctk.CTkMessagebox.show_warning("Warning", "Not connected to any serial port.")

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
