console.log('Script initialized!');

const socket = io();
let isConnected = false;

// DOM Elements
const portSelect = document.getElementById('portSelect');
const baudSelect = document.getElementById('baudSelect');
const connectButton = document.getElementById('connectButton');
const refreshButton = document.getElementById('refreshPorts');
const terminal = document.getElementById('terminal');
const commandInput = document.getElementById('commandInput');
const sendCommandButton = document.getElementById('sendCommand');
const quickCommandButtons = document.querySelectorAll('.command-btn');
const scanResultsContainer = document.getElementById('scanResultsContainer');
const scanResultsBody = document.getElementById('scanResultsBody');

// Configuration Elements
const cycleDelay = document.getElementById('cycleDelay');
const scanTime = document.getElementById('scanTime');
const numFrames = document.getElementById('numFrames');
const startChannel = document.getElementById('startChannel');
const scanCycles = document.getElementById('scanCycles');
const led = document.getElementById('led');
const applyParamsButton = document.getElementById('applyParams');

// Target Elements
const targetIndices = document.getElementById('targetIndices');
const setTargetButton = document.getElementById('setTarget');

// Socket event handlers
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('ports_list', (data) => {
    portSelect.innerHTML = '';
    data.ports.forEach(port => {
        const option = document.createElement('option');
        option.value = port;
        option.textContent = port;
        portSelect.appendChild(option);
    });
});

socket.on('connection_status', (data) => {
    isConnected = data.connected;
    updateConnectionStatus();
});

let networks = [];
let isCollectingNetworks = false;

socket.on('serial_data', (data) => {
    console.log('Raw data received:', data.data);
    appendToTerminal(data.data);
    
    const line = data.data;
    
    // Start collecting networks
    if (line.includes('Detected networks:')) {
        networks = [];
        isCollectingNetworks = true;
        return;
    }
    
    // Parse network line
    if (isCollectingNetworks && line.match(/^\d+\t/)) {
        const parts = line.split('\t');
        if (parts.length >= 5) {
            const id = parts[0];
            const ssid = parts[1].replace('SSID: ', '');
            const channel = parts[3].replace('Channel: ', '');
            const rssi = parseInt(parts[4].replace('RSSI: ', '').replace(' dBm', ''));
            const type = parts[5] || 'Unknown';

            networks.push({ id, ssid, channel, rssi, type });
            console.log('Added network:', { id, ssid, channel, rssi, type });
        }
    }
    
    // End of scan, display networks
    if (line.includes('[INFO] Scan completed.')) {
        isCollectingNetworks = false;
        console.log('Found networks:', networks);
        if (networks.length > 0) {
            displayNetworks(networks);
        }
    }
});

socket.on('command_status', (data) => {
    if (!data.success) {
        appendToTerminal('Error: ' + (data.message || 'Failed to send command'));
    } else if (data.message) {
        appendToTerminal(data.message);
    }
});

// Button click handlers
refreshButton.addEventListener('click', () => {
    socket.emit('refresh_ports');
});

connectButton.addEventListener('click', () => {
    if (!isConnected) {
        socket.emit('connect_serial', {
            port: portSelect.value,
            baud_rate: baudSelect.value
        });
    } else {
        socket.emit('disconnect_serial');
    }
});

sendCommandButton.addEventListener('click', sendCommand);
commandInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendCommand();
    }
});

quickCommandButtons.forEach(button => {
    button.addEventListener('click', () => {
        const command = button.dataset.command;
        if (isConnected) {
            socket.emit('send_command', { command: command });
            appendToTerminal(`> ${command}`);
        } else {
            appendToTerminal('Not connected to device');
        }
    });
});

// Configuration handlers
applyParamsButton.addEventListener('click', () => {
    if (isConnected) {
        const params = {
            cycle_delay: cycleDelay.value,
            scan_time: scanTime.value,
            num_frames: numFrames.value,
            start_channel: startChannel.value,
            scan_cycles: scanCycles.value,
            led: led.value
        };
        socket.emit('apply_parameters', params);
        appendToTerminal('> Applying parameters...');
    } else {
        appendToTerminal('Not connected to device');
    }
});

// Target handlers
setTargetButton.addEventListener('click', () => {
    if (isConnected) {
        const target = targetIndices.value.trim();
        if (target) {
            socket.emit('set_target', { target: target });
            appendToTerminal(`> Setting target: ${target}`);
        } else {
            appendToTerminal('Error: Please enter target indices');
        }
    } else {
        appendToTerminal('Not connected to device');
    }
});

// Add collapse event handlers
document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(button => {
    button.addEventListener('click', () => {
        const icon = button.querySelector('i');
        if (icon) {
            icon.classList.toggle('fa-chevron-up');
            icon.classList.toggle('fa-chevron-down');
        }
    });
});

// Helper functions
function sendCommand() {
    const command = commandInput.value.trim();
    if (command && isConnected) {
        socket.emit('send_command', { command: command });
        appendToTerminal(`> ${command}`);
        commandInput.value = '';
    } else if (!isConnected) {
        appendToTerminal('Not connected to device');
    }
}

function appendToTerminal(text) {
    const line = document.createElement('pre');
    line.className = 'terminal-line';
    line.textContent = text;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
}

function updateConnectionStatus() {
    connectButton.textContent = isConnected ? 'Disconnect' : 'Connect';
    connectButton.className = isConnected ? 'btn btn-danger w-100' : 'btn btn-primary w-100';
    portSelect.disabled = isConnected;
    baudSelect.disabled = isConnected;
    
    const elements = [
        ...quickCommandButtons,
        applyParamsButton,
        setTargetButton,
        sendCommandButton
    ];
    
    elements.forEach(element => {
        if (element) {
            element.disabled = !isConnected;
        }
    });
    
    if (!isConnected) {
        appendToTerminal('Disconnected from device');
    }
}

function displayNetworks(networks) {
    console.log('Displaying networks:', networks);
    scanResultsBody.innerHTML = '';
    networks.forEach(network => {
        const row = document.createElement('tr');
        
        // Calculate RSSI percentage (assuming -100dB is 0% and -50dB is 100%)
        const rssiPercentage = Math.min(100, Math.max(0, (network.rssi + 100) * 2));
        
        row.innerHTML = `
            <td>${network.id}</td>
            <td>${network.ssid}</td>
            <td>${network.channel}</td>
            <td>
                <div class="rssi-indicator">
                    <div class="rssi-level" style="width: ${rssiPercentage}%"></div>
                </div>
                ${network.rssi} dBm
            </td>
            <td>${network.type}</td>
            <td>
                <button class="btn btn-sm btn-primary scan-action-btn" onclick="setTarget(${network.id})">
                    Select
                </button>
            </td>
        `;
        
        scanResultsBody.appendChild(row);
    });
    
    scanResultsContainer.style.display = 'block';
    console.log('Table should be visible now');
}

function setTarget(id) {
    if (isConnected) {
        socket.emit('set_target', { target: id.toString() });
        appendToTerminal(`> Setting target: ${id}`);
    } else {
        appendToTerminal('Not connected to device');
    }
}
