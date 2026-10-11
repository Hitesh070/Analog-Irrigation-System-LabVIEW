# Smart Automatic Irrigation, Foliage Misting & Thermal Cooling System

Multi-Zone ESP32 / Arduino, NI LabVIEW & Discrete Analog System

---

## Executive Summary

The **Smart Automatic Irrigation, Foliage Misting & Thermal Cooling System** is a multi-zone agricultural climate controller designed to manage root soil moisture, foliage canopy humidity, and microclimate air temperature. It supports multi-platform deployment: **NI LabVIEW HMI Master Control**, **Microcontroller Mode (ESP32 / Arduino)**, and **Discrete Analog Mode (LM358/LM393/NE556)**.

The system prevents rapid ON/OFF relay chattering, provides water tank dry-run protection via float switch interlocks, and verifies pump prime and flow rate using a Hall-effect water flow sensor.

---

## NI LabVIEW Master HMI & Control Architecture

The system uses **National Instruments LabVIEW** as the **Master Human-Machine Interface (HMI) & Virtual Control Panel**. LabVIEW interfaces with the ESP32 / Arduino hardware via **NI VISA Serial Communication (USB UART at 115200 Baud)**.

### LabVIEW Front Panel Virtual Controls & Indicators
* **Virtual Gauges & Thermometers**:
  - Root Soil Moisture Resistance Gauge ($1\text{k}\Omega - 200\text{k}\Omega$)
  - Foliage Canopy Relative Humidity Gauge ($10\% - 90\%\text{ RH}$)
  - Ambient Air Temperature Thermometer ($0^\circ\text{C} - 60^\circ\text{C}$)
  - YF-S201 Volumetric Flow Rate Meter ($\text{L/min}$)
* **Virtual LED Diagnostic Indicators**:
  - Power 🟢, Dry Soil Demand 🟡, DC Water Pump 🔵, DC Cooling Fan 🌀, **Mist Creator #1 🟣**, **Mist Creator #2 🟣**, Tank Water Fault 🔴
* **Master Operation Mode & Control Switches**:
  - 3-Position Ring Switch (`AUTO`, `MANUAL`, `OFF`)
  - Manual Toggle Switches for Water Pump, Cooling Fan, and 2x Piezo Mist Creators
* **Virtual Threshold Sliders**:
  - Soil Moisture Dryness Threshold Slider ($VR_1$)
  - Humidity Target Misting Threshold Slider ($VR_3$)
  - Temperature Target Cooling Threshold Slider ($VR_4$)
* **Real-Time Waveform Charts**: Renders live trend plots for all sensor inputs and actuator drive signals at 10Hz sampling.

---

## Complete Hardware Components & Use

### 1. Controllers & Signal Processors
* **ESP32 DevKit V1 / Arduino Board**: Main microcontroller reading analog/digital sensor signals and driving actuator relays.
* **NI LabVIEW Software HMI**: Virtual Control Panel and HMI for system visualization and master override.
* **LM358 Dual Op-Amp (DIP-8)**: Configured as a Unity-Gain Voltage Follower Buffer ($K_{buf} = 1.0$) with an RC filter ($f_c = 159.15\,\text{Hz}$) to remove probe cable noise.
* **LM393 / LM339 Comparators (DIP-14)**: Multi-channel Schmitt trigger comparators enforcing a $0.70\,\text{V}$ hysteresis band to eliminate relay chattering.
* **NE556 Dual Timer IC (DIP-14)**: Hardware monostable pulse timers generating 30s soil watering pulses and 15s foliage misting pulses.

### 2. Sensors
* **Resistive Soil Moisture Sensor Probe**: Stainless steel probe bridge measuring soil moisture resistance $R_{soil}$ ($1\,\text{k}\Omega$ wet to $200\,\text{k}\Omega$ dry).
* **DHT11 / DHT22 Sensor Module**: Digital/analog sensor measuring foliage canopy relative humidity ($10\% - 90\%\text{ RH}$) and ambient temperature ($0^\circ\text{C} - 60^\circ\text{C}$).
* **Tank Water Level Sensor (Reed Float Switch)**: Float switch installed in storage tank. Opens when tank is empty to prevent pump dry-running.
* **YF-S201 Water Flow Sensor**: Hall-effect turbine sensor monitoring volumetric water flow rate ($\text{L/min}$) to detect pipe blockages and loss of pump prime.

### 3. Actuators & Power Drivers
* **Small Submersible DC Water Pump (12V 3W)**: Submersible mini pump for root zone soil irrigation.
* **Small DC Cooling Fan (12V 0.15A)**: Brushless DC fan providing thermal ventilation when ambient temperature exceeds threshold.
* **2 Nos. Ultrasonic Mist Creators (108kHz Piezo Transducers)**: Vibrating ceramic piezoelectric atomizer discs converting water droplets into micro-fine mist for leaves above soil.
* **4-Channel Relay / Power MOSFET Driver Module (IRFZ44N)**: Solid-state drivers switching 12V DC loads safely.

---

## Control System Architecture & Transfer Functions

### Stage 1: Soil Moisture Sensing Bridge
Raw probe voltage divider output:
$$V_{sensor}(t) = V_{CC} \cdot \frac{R_{soil}(t)}{R_{fixed} + R_{soil}(t)}$$
where $V_{CC} = 12.0\,\text{V}$ and $R_{fixed} = 10.0\,\text{k}\Omega$.

### Stage 2: Signal Conditioner & LM358 Op-Amp Buffer
LM358 operational amplifier configured as a Unity-Gain Voltage Follower ($K_{buf} = 1.0$) with an RC low-pass filter ($R_f = 10.0\,\text{k}\Omega, C_f = 0.1\,\mu\text{F}$):
$$G_{buf}(s) = \frac{1}{\tau_{filter} s + 1} = \frac{1}{0.001 s + 1}$$
Filter cutoff frequency $f_c = 159.15\,\text{Hz}$, rejecting $50\text{Hz}/100\text{Hz}$ AC mains hum and high-frequency noise spikes.

### Stage 3 & 4: LM393 Comparator with Schmitt Trigger Hysteresis
Positive feedback resistor $R_H = 100.0\,\text{k}\Omega$ creates a $0.70\,\text{V}$ hysteresis band between Upper Threshold $V_{UTP}$ and Lower Threshold $V_{LTP}$:
$$V_{UTP} = V_{ref} + (V_{CC} - V_{ref}) \cdot \frac{R_{pot}}{R_H + R_{pot}} = 2.85\,\text{V DC}$$
$$V_{LTP} = V_{ref} - V_{ref} \cdot \frac{R_{pot}}{R_H + R_{pot}} = 2.15\,\text{V DC}$$
$$\Delta V_H = V_{UTP} - V_{LTP} = 0.70\,\text{V}$$
Eliminates relay and pump chattering caused by transient sensor noise.

### Stage 5: NE556 Dual Monostable Pulse Timers
Generates fixed watering and misting pulse durations:
$$T_{pulse} = 1.1 \cdot R_{timer} \cdot C_{timer}$$
- **Timer Channel 1 (Soil Pump)**: $R_{timer} = 270\,\text{k}\Omega, C_{timer} = 100\,\mu\text{F} \implies T_{pulse1} = 29.70\,\text{s} \approx 30\,\text{s}$.
- **Timer Channel 2 (Foliage Mist)**: $R_{timer} = 270\,\text{k}\Omega, C_{timer} = 47\,\mu\text{F} \implies T_{pulse2} = 13.96\,\text{s} \approx 15\,\text{s}$.

### Stage 6: IRFZ44N MOSFET Driver & DC Pump Motor Dynamics
Transfer function relating motor angular velocity $\Omega(s)$ to applied gate voltage $V(s)$:
$$G_{pump}(s) = \frac{\Omega(s)}{V(s)} = \frac{K_m}{(L_m J) s^2 + (L_m B + R_m J) s + (R_m B + K_m K_b)}$$
Substituting physical motor parameters ($R_m = 4.0\,\Omega, L_m = 0.5\,\text{mH}, K_m = 0.05, K_b = 0.05, J = 1.0\times 10^{-5}, B = 1.0\times 10^{-4}$):
$$G_{pump}(s) = \frac{0.05}{5.0 \times 10^{-9} s^2 + 4.005 \times 10^{-5} s + 0.0029}$$

---

## Repository Structure

```text
├── index.html                                    # Main web dashboard interface (HTML5)
├── styles.css                                    # Glassmorphic eco-industrial CSS stylesheet
├── app.js                                        # Real-time Web simulation engine & canvas oscilloscope
├── README.md                                     # Main repository documentation
├── PROJECT_HARDWARE_AND_SIMULINK_MASTER_GUIDE.md # Comprehensive engineering specification manual
├── HOW_TO_RUN_SIMULINK_MODEL.md                 # User guide for running MATLAB scripts & Simulink models
├── circuit_schematic.md                          # Pin-by-pin hardware netlists & breadboard wiring guide
├── Documentaion/
│   ├── Analog-Automatic-Irrigation-Controller (1).pptx # Presentation deck
│   ├── Analog_Irrigation_Controller_BOM_and_Component_List.xlsx # Master Excel workbook (BOM, Pin Netlists, LabVIEW Spec)
│   └── Analog_Irrigation_Controller_Master_Guide.docx # Master Word technical documentation document
├── LabView/
│   └── Analog Irigation System.vi                # LabVIEW Virtual Instrument master HMI & simulation model
└── Simulink/
    ├── Analog_Irrigation_Control_System.slx      # Programmatically generated Simulink block model
    ├── create_irrigation_simulink_model.m        # MATLAB script to programmatically build Simulink .slx model
    └── simulate_irrigation_controller.m          # Standalone toolbox-free MATLAB simulation script
```

---

## Instructions for Execution

## Repository Structure

```text
Analog Automatic Irrigation Controller/
├── Arduino/
│   ├── logic/
│   │   └── logic.ino                # Production Arduino Master code (I2C LCD & LabVIEW link)
│   └── testing/
│       └── testing.ino              # Hardware component testing bench code
├── Documentation/
│   ├── Analog_Automatic_Irrigation_Controller.pptx         # Project presentation deck
│   ├── Analog_Irrigation_Controller_BOM_and_Component_List.xlsx # Master BOM & specs
│   ├── Analog_Irrigation_Controller_Master_Guide.docx       # Complete project report
│   ├── circuit_schematic.md                                 # Hardware netlists & circuit schematics
│   ├── HOW_TO_RUN_SIMULINK_MODEL.md                         # Simulink step-by-step guide
│   └── PROJECT_HARDWARE_AND_SIMULINK_MASTER_GUIDE.md        # Comprehensive integration guide
├── LabView/
│   ├── control panel.vi             # Main LabVIEW Master HMI Dashboard
│   └── Analog Irigation System.vi   # Standalone simulation VI
├── Simulink/
│   ├── Analog_Irrigation_Control_System.slx  # Simulink physical control model
│   ├── create_irrigation_simulink_model.m    # Model generator script
│   └── simulate_irrigation_controller.m      # Simulation execution script
├── Web_Simulator/
│   ├── assets/                      # UI graphics and diagrams
│   ├── index.html                   # Interactive browser simulator
│   ├── styles.css                   # Industrial styling
│   └── app.js                       # Browser state machine engine
└── README.md                        # Master project documentation
```

---

## Quick Start & Execution

### 1. Web Simulation Dashboard
1. Open `Web_Simulator/index.html` in any modern web browser or host using a local HTTP server:
   ```bash
   cd Web_Simulator
   python -m http.server 8080
   ```
2. Navigate to `http://localhost:8080`.
3. Adjust the sliders for Soil Moisture, Canopy Relative Humidity, and Ambient Air Temperature to test real-time switching dynamics, LEDs, analog meters, and oscilloscope waveforms.

### 2. NI LabVIEW Master HMI Execution
1. Connect Arduino board to PC via USB cable.
2. Launch NI LabVIEW.
3. Open `LabView/control panel.vi`.
4. Select your COM port from the `Port` dropdown and click **Run** (`Ctrl + R`) to display sensor telemetry and control all actuators in real time.

### 3. MATLAB & Simulink Control System Simulation
1. Launch MATLAB.
2. Navigate to the `Simulink` directory:
   ```matlab
   cd('Simulink')
   ```
3. Build and load the Simulink block diagram:
   ```matlab
   create_irrigation_simulink_model
   ```
4. Run the standalone numerical simulation:
   ```matlab
   simulate_irrigation_controller
   ```

---

## Hardware Bill of Materials (BOM)

| Item | Component Name | Specification | Qty | Stage & Function |
|---|---|---|---|---|
| 1 | Microcontroller Board | ESP32 DevKit V1 / Arduino | 1 | Main System Controller Board |
| 2 | LabVIEW Software HMI | NI LabVIEW VISA HMI | 1 | Master Virtual Control Panel & HMI |
| 3 | Temp & Humidity Sensor | DHT11 / DHT22 Sensor Module | 1 | Foliage Canopy Temp & Humidity Sensing |
| 4 | Soil Moisture Sensor | Resistive Soil Sensor Module | 1 | Root Zone Soil Resistance Sensing |
| 5 | Ultrasonic Mist Creators | 108kHz Piezo Transducer Discs | 2 | 2 Nos. Foliage Misting Atomizer Discs |
| 6 | Submersible Water Pump | 12V DC 3W Mini Pump | 1 | Root Zone Soil Irrigation Actuator |
| 7 | Small Cooling Fan | 12V 0.15A Brushless DC Fan | 1 | Thermal Microclimate Ventilation Fan |
| 8 | Tank Water Level Sensor | Reed Float Switch | 1 | Tank Level Dry-Run Protection Switch |
| 9 | Water Flow Sensor | YF-S201 Hall-Effect Sensor | 1 | Pump Prime & Flow Rate Monitoring |
| 10 | Relay / MOSFET Module | 4-Channel Relay / MOSFET Board | 1 | Actuator Power Switching Board |
| 11 | Dual Op-Amp IC | LM358 DIP-8 | 1 | Stage 2 Signal Buffer & Filtering |
| 12 | Quad Comparator IC | LM339 / LM393 DIP-14 | 1 | Multi-Channel Schmitt Trigger Comparators |
| 13 | Dual Precision Timer IC | NE556 DIP-14 | 1 | Monostable Pulse Duration Timers |
| 14 | NPN Transistors | BC547 TO-92 | 2 | Safety Interlocks & Transistor Drivers |
| 15 | Voltage Regulator IC | LM7812 TO-220 | 1 | Regulated +12.0V DC Power Supply Rail |
| 16 | Flyback Diodes | 1N4007 (1A 1000V) | 2 | Inductive Kickback Spike Protection |
| 17 | Transformer & Rectifier | 230V to 15V AC Transformer, W04M | 1 Set | Power Supply Rectification Unit |
| 18 | Potentiometers | 10kΩ & 270kΩ Pots | 4 | Calibration Controls (VR1, VR2, VR3, VR4) |
| 19 | Passives & Board | Resistors, Capacitors, PCB | 1 Set | Circuit Wiring & Decoupling |

---

## License & Citation

This project is released under the MIT License. Designed for Multi-Platform Control System research, university milestones, and industrial automation applications.
