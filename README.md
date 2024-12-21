<div align="center">

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ![GitHub issues](https://img.shields.io/github/issues/dagnazty/Evil-BW16-Control-Panel) ![GitHub stars](https://img.shields.io/github/stars/dagnazty/Evil-BW16-Control-Panel?style=social) ![GitHub forks](https://img.shields.io/github/forks/dagnazty/Evil-BW16-Control-Panel?style=social)

# 🎛️ Evil-BW16 Control Panel

![Evil-BW16 Logo](icon.ico)

</div>

**⚠️ Disclaimer:**  

<div align="center">

[Evil-BW16](https://github.com/7h30th3r0n3/Evil-BW16) is crafted exclusively for **educational** and **ethical testing** purposes. **Misuse** or **illegal application** of this tool is **strictly forbidden**. The creator of Evil-BW16 **declines any liability** and is **not responsible** for any misuse or damage caused by this tool. Users must **adhere to all applicable laws** and regulations in their jurisdiction regarding network testing and ethical hacking.

---

</div>

## 📖 Table of Contents

- [✨ Introduction](#-introduction)
- [🚀 Features](#-features)
- [🛠️ Requirements](#️-requirements)
  - [💻 Software](#-software)
  - [🔧 Hardware](#-hardware)
- [📦 Installation](#-installation)
- [🎯 Usage](#-usage)
  - [🔌 Connecting to the Device](#-connecting-to-the-device)
  - [📝 Commands](#-commands)
  - [⚙️ Setting Parameters](#-setting-parameters)
  - [🎯 Targeting APs](#-targeting-aps)
  - [🛠️ Custom Commands](#-custom-commands)
  - [🔘 System Tray](#-system-tray)
- [📄 License](#-license)
- [🤝 Contributing](#-contributing)
- [📬 Contact](#-contact)

---

## ✨ Introduction

<div align="center">

Welcome to the **Evil-BW16 Control Panel** – your sleek and intuitive graphical interface built with **Tkinter** for managing the powerful **Evil-BW16** device. Designed for **WiFi network testing** and **ethical hacking**, Evil-BW16 empowers you to:

</div>

- **Scan** for WiFi networks
- **Send deauthentication frames**
- **Target specific access points (APs)**

<div align="center">
  
Whether you're a cybersecurity enthusiast or a professional tester, our control panel simplifies complex operations, making your ethical hacking endeavors both efficient and effective.

</div>

## 🚀 Features

- **🔌 Serial Port Management:**
  - Seamlessly connect/disconnect from serial ports.
  - Dynamically refresh available serial ports.

- **📝 Command Execution:**
  - Execute predefined commands: `start`, `stop`, `scan`, `results`, `info`, and `help`.
  - Send custom commands for experimental features.

- **⚙️ Parameter Configuration:**
  - Configure settings like cycle delay, scan time, number of frames, start channel, scan cycles, and LED control.
  - Apply multiple parameters simultaneously with ease.

- **🎯 Targeting APs:**
  - Specify target AP indices to focus deauthentication attacks on selected networks.

- **🔘 System Tray Integration:**
  - Minimize the application to the system tray.
  - Easily restore or quit the application from the tray icon.

- **📜 Device Output Logging:**
  - Real-time display of device responses and logs for comprehensive monitoring.

## 🛠️ Requirements

### 💻 Software

- **Python 3.6 or Higher**
- **Libraries:**
  - `tkinter` (typically included with Python)
  - `pystray`
  - `Pillow`
  - `pyserial`

#### 📥 Installation of Python Libraries

Install the necessary Python libraries using `pip`:

```bash
pip install pystray Pillow pyserial
```

### 🔧 Hardware

- **🖥️ Evil-BW16 Device:** Ensure your Evil-BW16 hardware is properly connected to your computer via a serial connection (e.g., USB).
- **🖼️ Icon File:** An `icon.ico` file is required for the application and system tray icons. Place this file in the same directory as the application script.

## 📦 Installation

1. **🔍 Clone the Repository:**

   ```bash
   git clone https://github.com/dagnazty/Evil-BW16-Control-Panel.git
   cd Evil-BW16-Control-Panel
   ```

2. **📦 Install Dependencies:**

   Ensure all required Python libraries are installed as outlined in the [Requirements](#️-requirements) section.

3. **🖼️ Prepare the Icon:**

   Make sure you have an `icon.ico` file in the project directory. This icon will represent both the application window and the system tray.

## 🎯 Usage

Launch the Evil-BW16 Control Panel with Python:

```bash
python evil_bw16_gui.py
```

### 🔌 Connecting to the Device

1. **📡 Select Serial Port:**
   - Choose the appropriate COM port from the "Serial Port" dropdown connected to your Evil-BW16 device.
   - Click the "Refresh" button to update the list of available ports.

2. **🔢 Select Baud Rate:**
   - Select the desired baud rate from the "Baud Rate" dropdown. The default is `115200`.

3. **🔗 Connect:**
   - Click the "Connect" button to establish a connection with the device.
   - On successful connection, the status label will display "Connected" in green.

### 📝 Commands

Interact with your device using predefined command buttons:

- **▶️ Start:** Initiates the attack cycle.
- **⏹️ Stop:** Halts the attack cycle.
- **🔍 Scan:** Conducts a WiFi scan to detect available networks.
- **📄 Results:** Retrieves and displays the latest scan results.
- **ℹ️ Info:** Shows the current configuration of the device.
- **❓ Help:** Lists available commands and their descriptions.

### ⚙️ Setting Parameters

Customize device parameters in the "Set Parameters" section:

- **⏱️ Cycle Delay (ms):** Time delay between scan/deauthentication cycles.
- **⏲️ Scan Time (ms):** Duration of each WiFi scan.
- **📊 Num Frames:** Number of deauthentication frames sent per AP.
- **📡 Start Channel:** Starting channel for scanning (e.g., `1` for 2.4GHz or `36` for 5GHz).
- **🔄 Scan Between Cycles:** Toggle scanning between attack cycles (`on` or `off`).
- **💡 LEDs:** Control the device LEDs (`on` or `off`).

Click the **"Apply"** button to send the configured parameters to the device.

### 🎯 Targeting APs

Focus your attacks on specific APs in the "Target APs" section:

1. **🔢 Enter Target Indices:**
   - Input comma-separated indices corresponding to the APs listed in the scan results (e.g., `1,3,5`).

2. **🎯 Set Target:**
   - Click the **"Set Target"** button to configure the device to target the specified APs.

### 🛠️ Custom Commands

Experiment with advanced features using the "Custom Command" section:

1. **✏️ Enter Command:**
   - Type any arbitrary command in the "Command" entry field.

2. **🚀 Send Command:**
   - Click the **"Send"** button to transmit the custom command to the device.

**⚠️ Note:** Use this feature with caution. Sending unknown or malformed commands may disrupt device functionality.

### 🔘 System Tray

Manage the application conveniently via the system tray icon:

- **🔽 Minimize to Tray:**
  - Click the "X" button to hide the main window in the system tray.

- **🔄 Tray Menu:**
  - **Show:** Restore the main application window.
  - **Quit:** Exit the application completely.

_All tray and window icons utilize the `icon.ico` file for a consistent look and feel._

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🤝 Contributing

We welcome contributions! Follow these steps to contribute:

1. **🍴 Fork the Repository**

2. **🌿 Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **💾 Commit Your Changes**

   ```bash
   git commit -m "Add some feature"
   ```

4. **📤 Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **🔀 Open a Pull Request**

<div align="center">

Please ensure your code adheres to the project's coding standards and includes appropriate documentation.

---

**🔒 Stay Ethical. Use Responsibly.**

</div>
