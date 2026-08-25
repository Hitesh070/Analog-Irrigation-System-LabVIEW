# Analog Automatic Irrigation, Foliage Misting & Thermal Cooling Controller

Multi-Zone Discrete Analog Industrial Automation System (Microcontroller-Free)

---

## Executive Summary

The **Analog Automatic Irrigation, Foliage Misting & Thermal Cooling Controller** is a multi-zone discrete analog industrial automation system operating from a regulated +12.0V DC power rail without any digital microcontroller or software code. 

Conventional automated irrigation systems frequently suffer from rapid ON/OFF relay chattering, lack of pump dry-run protection, and high failure rates due to unbuffered sensor noise. This project resolves these issues by using operational amplifiers, Schmitt trigger comparators, dual monostable timers, power MOSFET drivers, piezoelectric ultrasonic atomizers, and hardware safety interlocks to achieve robust, noise-immune climate control.

---

## System Capabilities & Subsystems

The controller incorporates three discrete environmental feedback loops:

1. **Root Zone Soil Moisture Subsystem (Below Soil)**:
   - Measures soil probe resistance ($R_{soil} \in [1\,\text{k}\Omega, 200\,\text{k}\Omega]$).
   - Activates a 12V DC 3W submersible water pump for a 30-second watering pulse when dry soil is detected.

2. **Foliage Canopy Misting Subsystem (Above Soil)**:
   - Measures relative humidity ($10\% - 90\%\text{ RH}$) using an analog RH sensor module.
   - Activates a 108kHz Piezoelectric Ultrasonic Atomizer Disc to spray micro-fine mist onto plant leaves when air humidity drops below target threshold.

3. **Ambient Thermal Cooling Subsystem (Microclimate Control)**:
   - Measures air temperature ($0^\circ\text{C} - 60^\circ\text{C}$) using an NTC thermistor bridge.
   - Activates a 12V DC brushless ventilation cooling fan and the ultrasonic mist maker when ambient temperature exceeds the temperature threshold.

4. **Hardware Safety Interlocks**:
   - Monitors storage tank water level via a magnetic reed float switch.
   - BC547 NPN transistor pulls timer RESET pins LOW when the tank is empty or flow is blocked, locking out actuators to prevent thermal pump burnout.

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
├── create_irrigation_simulink_model.m            # MATLAB script to programmatically build Simulink .slx model
├── simulate_irrigation_controller.m              # Standalone toolbox-free MATLAB simulation script
├── Analog_Irrigation_Control_System.slx          # Programmatically generated Simulink block model
├── Analog_Irrigation_Controller_BOM_and_Component_List.xlsx # Master Excel workbook (BOM, Pin Netlists, Parameters)
├── Analog_Irrigation_Controller_Master_Guide.docx# Master Word technical documentation document
├── PROJECT_HARDWARE_AND_SIMULINK_MASTER_GUIDE.md # Comprehensive engineering specification manual
├── HOW_TO_RUN_SIMULINK_MODEL.md                 # User guide for running MATLAB scripts & Simulink models
├── circuit_schematic.md                          # Pin-by-pin hardware netlists & breadboard wiring guide
└── GAMMA_PPT_PROMPT.md                           # Gamma.app presentation deck generation prompt
```

---

## Instructions for Execution

### 1. Web Simulation Dashboard
1. Open `index.html` in any modern web browser or host using a local HTTP server:
   ```bash
   python -m http.server 8080
   ```
2. Navigate to `http://localhost:8080`.
3. Adjust the sliders for Soil Moisture, Canopy Relative Humidity, and Ambient Air Temperature to test real-time switching dynamics, LEDs, analog meters, and oscilloscope waveforms.

### 2. MATLAB & Simulink Control System Simulation
1. Launch MATLAB R2020a or newer.
2. Set working directory to project folder:
   ```matlab
   cd('c:\Users\hites\OneDrive\Documents\Projects & Research Work\Analog Automatic Irrigation Controller')
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
| 1 | Dual Op-Amp IC | LM358 DIP-8 | 1 | Stage 2 Signal Buffer & Filtering |
| 2 | Quad Comparator IC | LM339 / LM393 DIP-14 | 1 | Stage 3 & 4 Multi-Schmitt Trigger Comparators |
| 3 | Dual Precision Timer IC | NE556 DIP-14 | 1 | Stage 5 Monostable Timers (30s Soil Pump / 15s Misting) |
| 4 | Power MOSFETs | IRFZ44N N-Ch TO-220 | 2 | Stage 6 Power Drivers for 12V DC Pump & 12V DC Fan |
| 5 | Ultrasonic Atomizer Module | 108kHz Piezo Transducer Board | 1 | Foliage Misting Subsystem |
| 6 | NTC Thermistor Module | 10kΩ NTC Sensor Probe | 1 | Thermal Ventilation Subsystem |
| 7 | Analog Humidity Sensor | HR202 / HIH-4000 Analog Module | 1 | Foliage Misting Subsystem |
| 8 | 12V DC Cooling Fan | 12V 0.15A Brushless Fan | 1 | Thermal Ventilation Subsystem |
| 9 | NPN Transistors | BC547 TO-92 | 2 | Stage 7 Safety Interlocks & Drivers |
| 10 | Voltage Regulator IC | LM7812 TO-220 | 1 | Stage 8 Regulated +12.0V DC Rail |
| 11 | Submersible Water Pump | 12V DC 3W Mini Pump | 1 | Root Zone Irrigation Actuator |
| 12 | Tank Float Sensor | Reed Switch Float Sensor | 1 | Water Storage Level Safety Switch |
| 13 | Soil Moisture Probes | Stainless Steel Probes | 1 Pair | Stage 1 Soil Resistance Sensing |
| 14 | Flyback Diodes | 1N4007 (1A 1000V) | 2 | Inductive Kickback Spike Protection |
| 15 | Transformer & Rectifier | 230V to 15V AC Transformer, W04M | 1 Set | Stage 8 Power Supply Unit |
| 16 | Potentiometers | 10kΩ & 270kΩ Pots | 4 | Calibration Controls (VR1, VR2, VR3, VR4) |
| 17 | Passives & Board | Resistors, Capacitors, PCB | 1 Set | Circuit Wiring & Decoupling |

---

## License & Citation

This project is released under the MIT License. Designed for Discrete Analog Control System research, university milestones, and industrial automation applications.
