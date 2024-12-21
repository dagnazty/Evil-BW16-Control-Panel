# Evil-BW16 Control Panel

![Evil-BW16 Logo](icon.ico)

**Disclaimer:**  
[Evil-BW16](https://github.com/7h30th3r0n3/Evil-BW16), is developed for educational and ethical testing purposes only. Any misuse or illegal use of this tool is strictly prohibited. The creator of Evil-BW16 assumes no liability and is not responsible for any misuse or damage caused by this tool. Users are required to comply with all applicable laws and regulations in their jurisdiction regarding network testing and ethical hacking.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Connecting to the Device](#connecting-to-the-device)
  - [Commands](#commands)
  - [Setting Parameters](#setting-parameters)
  - [Targeting APs](#targeting-aps)
  - [Custom Commands](#custom-commands)
  - [System Tray](#system-tray)
- [License](#license)
- [Contributing](#contributing)
- [Contact](#contact)

## Introduction

Evil-BW16 Control Panel is a user-friendly graphical interface developed with Tkinter for managing and controlling the Evil-BW16 device. The device is designed for WiFi network testing and ethical hacking purposes, allowing users to perform actions such as scanning for WiFi networks, sending deauthentication frames, and targeting specific access points (APs).

## Features

- **Serial Port Management:**
  - Connect to and disconnect from serial ports.
  - Refresh available serial ports dynamically.

- **Command Execution:**
  - Send predefined commands like `start`, `stop`, `scan`, `results`, `info`, and `help`.
  - Send custom commands for experimental features.

- **Parameter Configuration:**
  - Set parameters such as cycle delay, scan time, number of frames, start channel, scan cycles, and LED control.
  - Apply multiple parameters simultaneously.

- **Targeting APs:**
  - Specify target AP indices to focus deauthentication attacks on selected networks.

- **System Tray Integration:**
  - Minimize the application to the system tray.
  - Restore or quit the application from the tray icon.

- **Device Output Logging:**
  - Real-time display of device responses and logs.

## Requirements

### Software

- **Python 3.6 or higher**
- **Libraries:**
  - `tkinter` (usually included with Python)
  - `pystray`
  - `Pillow`
  - `pyserial`

### Installation of Python Libraries

Install the required Python libraries using `pip`:

```bash
pip install pystray Pillow pyserial
```

### Hardware

- **Evil-BW16 Device:** Ensure you have the Evil-BW16 hardware properly connected to your computer via a serial connection (e.g., USB).

- **Icon File:** An `icon.ico` file is required for the application icon and system tray icon. Place this file in the same directory as the application script.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/dagnazty/Evil-BW16-Control-Panel.git
   cd Evil-BW16-Control-Panel
   ```

2. **Ensure Dependencies are Installed:**

   Install the required Python libraries as mentioned in the [Requirements](#requirements) section.

3. **Prepare the Icon:**

   Ensure you have an `icon.ico` file in the project directory. This icon will be used for the application window and system tray.

## Usage

Run the application using Python:

```bash
python evil_bw16_gui.py
```

### Connecting to the Device

1. **Select Serial Port:**
   - Use the "Serial Port" dropdown to select the appropriate COM port connected to the Evil-BW16 device.
   - Click the "Refresh" button to update the list of available ports.

2. **Select Baud Rate:**
   - Choose the baud rate from the "Baud Rate" dropdown. The default is set to `115200`.

3. **Connect:**
   - Click the "Connect" button to establish a connection with the device.
   - Upon successful connection, the status label will display "Connected" in green.

### Commands

Use the predefined command buttons to interact with the device:

- **Start:** Initiates the attack cycle.
- **Stop:** Stops the attack cycle.
- **Scan:** Performs a WiFi scan to detect available networks.
- **Results:** Retrieves and displays the latest scan results.
- **Info:** Displays the current configuration of the device.
- **Help:** Shows a list of available commands and their descriptions.

### Setting Parameters

Configure device parameters in the "Set Parameters" section:

- **Cycle Delay (ms):** Time delay between scan/deauthentication cycles.
- **Scan Time (ms):** Duration of each WiFi scan.
- **Num Frames:** Number of deauthentication frames sent per AP.
- **Start Channel:** Starting channel for scanning (e.g., `1` for 2.4GHz or `36` for 5GHz).
- **Scan Between Cycles:** Toggle scanning between attack cycles (`on` or `off`).
- **LEDs:** Control the device LEDs (`on` or `off`).

Click the "Apply" button to send the configured parameters to the device.

### Targeting APs

Specify target APs in the "Target APs" section:

1. **Enter Target Indices:**
   - Input comma-separated indices corresponding to the APs listed in the scan results (e.g., `1,3,5`).

2. **Set Target:**
   - Click the "Set Target" button to configure the device to focus attacks on the specified APs.

### Custom Commands

Experiment with custom commands using the "Custom Command" section:

1. **Enter Command:**
   - Type any arbitrary command in the "Command" entry field.

2. **Send Command:**
   - Click the "Send" button to transmit the custom command to the device.

**Note:** Use this feature with caution. Sending unknown or malformed commands may disrupt device functionality.

### System Tray

Manage the application using the system tray icon:

- **Minimize to Tray:**
  - Close the main window using the "X" button to hide it in the system tray.

- **Tray Menu:**
  - **Show:** Restore the main application window.
  - **Quit:** Exit the application completely.

All tray and window icons use the `icon.ico` file for consistency.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add some feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

Please ensure your code adheres to the project's coding standards and includes appropriate documentation.

---

**Stay Ethical. Use responsibly.**
