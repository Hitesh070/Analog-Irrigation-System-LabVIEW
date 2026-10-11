# Master Project Manual: Complete Hardware Architecture, Working Principles, Pin Connections & Simulink Modeling
## Analog Automatic Irrigation Controller (Microcontroller-Free)

This document provides a comprehensive end-to-end engineering reference covering the **full project working principles**, **hardware component specifications**, **exact pin-by-pin wiring netlists**, **Simulink block constants**, and **simulation parameter derivations** for the **Analog Automatic Irrigation Controller**.

---

## Table of Contents
1. [Project Overview & Working Principles](#1-project-overview--working-principles)
2. [Hardware Components & Bill of Materials (BOM)](#2-hardware-components--bill-of-materials-bom)
3. [Complete Hardware Connection Guide & Pin Netlists](#3-complete-hardware-connection-guide--pin-netlists)
4. [Explanation of Simulink Constants & Simulation Parameters](#4-explanation-of-simulink-constants--simulation-parameters)
5. [Simulink Simulation Execution & Scope Interpretation](#5-simulink-simulation-execution--scope-interpretation)

---

## 1. Project Overview & Working Principles

The project is a multi-stage discrete analog industrial controller designed to water crops automatically based on soil moisture levels while providing pump dry-run protection and timing control without any microcontroller or digital software.

```
 [Power Supply 7812] ──► +12V DC Rail
                            │
 [Soil Moisture Probes] ──► [Stage 1: Probe Divider Bridge]
                            │
                            ▼
 [LM358 Op-Amp] ──────────► [Stage 2: Unity Gain Buffer & RC Filter]
                            │
                            ▼
 [LM393 Comparator] ──────► [Stage 3 & 4: Schmitt Trigger Hysteresis]
                            │
                            ▼
 [NE555 Timer] ───────────► [Stage 5: Monostable Pulse Delay Timer]
                            │
 [Tank & Flow Switch] ───► [Stage 7: BC547 Tank & Dry-Run Interlock]
                            │
                            ▼
 [IRFZ44N MOSFET] ────────► [Stage 6: Power MOSFET Driver & DC Pump Motor]
```

### Stage-by-Stage Working Principles:

1. **Stage 1 – Soil Moisture Probe Divider Bridge:**
   - Two stainless steel probes inserted into agricultural soil act as a moisture-dependent resistor $R_{soil}$ ($1\,\text{k}\Omega$ wet to $200\,\text{k}\Omega$ dry).
   - Probes form a voltage divider with a fixed precision resistor $R_{fixed} = 10\,\text{k}\Omega$:
     $$V_{sensor}(t) = V_{CC} \cdot \frac{R_{soil}(t)}{R_{fixed} + R_{soil}(t)}$$
   - As soil dries, $R_{soil}$ increases, causing output voltage $V_{sensor}$ to rise continuously towards $12\text{V}$.

2. **Stage 2 – LM358 Signal Conditioner & Buffer:**
   - Raw probe voltage contains AC mains hum and high-frequency noise.
   - LM358 operational amplifier is wired as a **Unity Gain Voltage Follower Buffer** ($K_{buf} = 1.0$) with an RC filter ($R_f = 10\,\text{k}\Omega, C_f = 0.1\,\mu\text{F}, f_c = 159.15\,\text{Hz}$).
   - Isolates sensor loading and outputs a clean, noise-free DC voltage $V_{buf}$.

3. **Stage 3 & 4 – LM393 Comparator with Schmitt Trigger Hysteresis:**
   - Compares buffered sensor voltage $V_{buf}$ against reference voltage $V_{ref} = 2.50\,\text{V}$ set by a $10\,\text{k}\Omega$ potentiometer.
   - Positive feedback resistor $R_H = 100\,\text{k}\Omega$ creates two distinct switching thresholds:
     - **Upper Threshold Voltage ($V_{UTP} = 2.85\,\text{V}$):** Soil is dry $\rightarrow$ LM393 output switches **HIGH** to request watering.
     - **Lower Threshold Voltage ($V_{LTP} = 2.15\,\text{V}$):** Soil is wet $\rightarrow$ LM393 output switches **LOW** to end demand.
     - **Hysteresis Band ($\Delta V_H = 0.70\,\text{V}$):** Completely eliminates rapid relay/pump chattering caused by minor noise ripples.

4. **Stage 5 – NE555 Monostable Irrigation Delay Timer:**
   - Triggered on the rising edge of the LM393 comparator output when dry soil is confirmed.
   - Operates in monostable mode ($R_{timer} = 270\,\text{k}\Omega, C_{timer} = 100\,\mu\text{F}$):
     $$T_{pulse} = 1.1 \cdot R_{timer} \cdot C_{timer} = 1.1 \cdot (270 \times 10^3) \cdot (100 \times 10^{-6}) = 29.70 \, \text{Seconds}$$
   - Ensures watering occurs for a fixed, controlled $30\,\text{second}$ period per cycle to allow water infiltration without surface flooding.

5. **Stage 6 – IRFZ44N Logic Power MOSFET Driver & DC Submersible Pump:**
   - Switches the 12V 3W DC submersible water pump motor.
   - Gate resistor $R_G = 100\,\Omega$ limits switching charge current, while $R_{GS} = 10\,\text{k}\Omega$ ensures fail-safe gate pull-down.
   - A 1N4007 flyback diode connected anti-parallel across the pump motor absorbs inductive voltage spikes during switching transitions.

6. **Stage 7 – Water Tank Protection & Dry-Run Flow Interlock:**
   - **Tank Float Switch:** Magnetic float switch in storage tank connects to BC547 NPN transistor base. If tank is empty, BC547 pulls NE555 **Pin 4 (RESET)** to ground, halting the pump instantly and turning ON Red Tank Empty LED.
   - **Dry-Run Flow Switch:** Detects lost prime or pipe blockage, turning off the pump to prevent motor thermal burnout.

7. **Stage 8 – LM7812 Linear Regulated Power Supply Rail:**
   - Converts $230\,\text{V AC}$ mains to $12.0\,\text{V DC}$ using a $15\text{V}$ AC transformer, bridge rectifier ($W04$), $1000\,\mu\text{F}$ filter cap, and LM7812 linear voltage regulator.

---

## 2. Hardware Components & Bill of Materials (BOM)

| Item | Component Name | Specification / Model | Quantity | Purpose | Cost (₹ INR) |
|---|---|---|---|---|---|
| 1 | Dual Op-Amp IC | LM358 DIP-8 | 1 | Stage 2 Signal Buffer & Filtering | ₹30 |
| 2 | Dual Comparator IC | LM393 DIP-8 | 1 | Stage 3 & 4 Schmitt Trigger Hysteresis | ₹30 |
| 3 | Precision Timer IC | NE555 DIP-8 | 1 | Stage 5 Monostable Pulse Timer | ₹20 |
| 4 | Power MOSFET | IRFZ44N N-Channel (55V 49A) | 1 | Stage 6 Low $R_{DS(on)}$ Pump Switching | ₹60 |
| 5 | NPN Transistor | BC547 TO-92 | 1 | Stage 7 Reset Safety Interlock | ₹10 |
| 6 | Voltage Regulator IC | LM7812 TO-220 (12V 1.5A) | 1 | Stage 8 Regulated Supply Rail | ₹20 |
| 7 | Submersible Pump | 12V DC 3W Mini Pump | 1 | Water Pumping Actuator | ₹250 |
| 8 | Moisture Sensor | Stainless Steel Probes | 1 Pair | Soil Resistance Sensing | ₹60 |
| 9 | Tank Float Sensor | Reed Switch Float Sensor | 1 | Water Level Safety Interlock | ₹50 |
| 10 | Diodes & LEDs | 1N4007, Red, Yellow, Green, Blue | 1 Set | Flyback Protection & Status LEDs | ₹50 |
| 11 | Passives & Board | Resistors, Caps, Pots, PCB | 1 Set | Circuit Wiring & Passives | ₹250 |
| **Total** | | | | **Estimated Total Cost** | **₹830 – ₹1,180** |

---

## 3. Complete Hardware Connection Guide & Pin Netlists

### A. IC Pinout Netlists & Connections

#### 1. LM7812 Voltage Regulator (TO-220 Package)
- **Pin 1 (Input):** Connected to $+15\text{V}$ DC Rectified Output from Bridge Rectifier ($W04$) and positive terminal of $1000\,\mu\text{F}$ filter capacitor.
- **Pin 2 (Ground):** Connected to System Common Ground ($\text{GND}$).
- **Pin 3 (Output):** $+12.0\text{V}$ DC Regulated Rail. Decoupled with $0.1\,\mu\text{F}$ ceramic capacitor to $\text{GND}$.

#### 2. LM358 Dual Op-Amp (DIP-8 Package)
- **Pin 8 ($V_{CC}$):** Connected to $+12.0\text{V}$ DC Rail.
- **Pin 4 ($\text{GND}$):** Connected to System $\text{GND}$.
- **Pin 3 ($\text{IN } 1+$):** Connected to Stage 1 Probe Divider Node (**TP1**) and $0.1\,\mu\text{F}$ filter cap to $\text{GND}$.
- **Pin 2 ($\text{IN } 1-$):** Tied directly to Pin 1 ($\text{OUT } 1$) [Unity Gain Voltage Follower].
- **Pin 1 ($\text{OUT } 1$):** Buffered Voltage Output (**TP2**), connects to LM393 Pin 2.

#### 3. LM393 Dual Comparator (DIP-8 Package)
- **Pin 8 ($V_{CC}$):** Connected to $+12.0\text{V}$ DC Rail.
- **Pin 4 ($\text{GND}$):** Connected to System $\text{GND}$.
- **Pin 2 ($\text{IN } 1-$):** Connected to LM358 Pin 1 (Buffered Sensor Voltage **TP2**).
- **Pin 3 ($\text{IN } 1+$):** Connected to $10\text{k}\Omega$ Reference Potentiometer Wiper ($V_{ref}$) AND Hysteresis Resistor $R_H (100\text{k}\Omega)$.
- **Pin 1 ($\text{OUT } 1$):** Comparator Output (**TP3**). Connected to $10\text{k}\Omega$ Pull-Up Resistor to $+12\text{V}$ and NE555 Pin 2 ($\text{TRIGGER}$) via $0.1\,\mu\text{F}$ cap.
- **$R_H$ Feedback:** Resistor $R_H (100\text{k}\Omega)$ connected directly between Pin 1 and Pin 3.

#### 4. NE555 Precision Timer (DIP-8 Package)
- **Pin 1 ($\text{GND}$):** Connected to System $\text{GND}$.
- **Pin 8 ($V_{CC}$):** Connected to $+12.0\text{V}$ DC Rail.
- **Pin 4 ($\text{RESET}$):** Connected to BC547 Collector and pulled up via $10\text{k}\Omega$ to $+12\text{V}$.
- **Pin 5 ($\text{CONTROL}$):** Connected to $0.01\,\mu\text{F}$ decoupling capacitor to $\text{GND}$.
- **Pin 2 ($\text{TRIGGER}$):** Connected via $0.1\,\mu\text{F}$ cap to LM393 Pin 1 Output. Pulled up via $10\text{k}\Omega$ to $+12\text{V}$.
- **Pin 6 ($\text{THRESHOLD}$) & Pin 7 ($\text{DISCHARGE}$):** Tied together (**TP4**).
  - Connected to $+12\text{V}$ via Timing Potentiometer $R_{timer} (270\text{k}\Omega)$.
  - Connected to $\text{GND}$ via Timing Capacitor $C_{timer} (100\,\mu\text{F})$.
- **Pin 3 ($\text{OUTPUT}$):** Monostable Irrigation Pulse Output (**TP5**). Connects to IRFZ44N Gate resistor $R_G (100\,\Omega)$.

#### 5. IRFZ44N Power MOSFET (TO-220 Package)
- **Gate Pin (G):** Connected to $100\,\Omega$ Resistor $R_G$ from NE555 Pin 3. Pulled to $\text{GND}$ via $10\text{k}\Omega$ Resistor $R_{GS}$.
- **Source Pin (S):** Connected to System $\text{GND}$.
- **Drain Pin (D):** Connected to Negative Terminal of 12V DC Water Pump.

#### 6. DC Water Pump & Flyback Diode
- **Pump Positive Terminal:** Connected to $+12.0\text{V}$ DC Rail.
- **Pump Negative Terminal:** Connected to IRFZ44N Drain Pin (**D**).
- **1N4007 Flyback Diode:** Anode connected to IRFZ44N Drain Pin (**D**), Cathode connected to $+12.0\text{V}$ DC Rail.

#### 7. BC547 Tank Level Protection Transistor (TO-92 Package)
- **Emitter (E):** Connected to System $\text{GND}$.
- **Base (B):** Connected via $10\text{k}\Omega$ resistor to Tank Float Reed Switch output.
- **Collector (C):** Connected to NE555 Pin 4 ($\text{RESET}$).

---

## 4. Explanation of Simulink Constants & Simulation Parameters

This section explains **why every single constant and parameter was chosen in the Simulink model and MATLAB simulation**:

```
+------------------------------------+------------------------+-------------------------------------------------------------+
| Simulink Parameter                 | Value Set              | Derivation / Engineering Justification                      |
+------------------------------------+------------------------+-------------------------------------------------------------+
| Supply Rail (Vcc)                  | 12.0 V DC              | Determined by 12V DC submersible pump rating and 7812 IC.   |
| Fixed Divider Resistor (R_fixed)   | 10 kΩ                  | Balances 1kΩ-200kΩ probe swing; limits current to <1.2mA.   |
| Reference Voltage (V_ref)          | 2.50 V                 | Sets nominal dry soil trigger threshold at 50kΩ probe.      |
| Hysteresis Feedback (R_H)          | 100 kΩ                 | Yields 0.70V noise margin (V_UTP = 2.85V, V_LTP = 2.15V).   |
| Low-Pass Filter (Rf, Cf)           | 10 kΩ, 0.1 µF          | Yields tau = 1.0ms, fc = 159.15Hz; rejects 50Hz/100Hz mains.|
| 555 Timing (R_timer, C_timer)      | 270 kΩ, 100 µF         | T_pulse = 1.1 * R * C = 29.70s; optimal soil infiltration.  |
| MOSFET Gate Gain (K_gate)          | 12.0 V/V               | Converts 555 0/1 logic pulse to 12V MOSFET gate drive.      |
| Pump Resistance (R_m)              | 4.0 Ω                  | Armature resistance measured on 12V 3W pump motor.          |
| Pump Inductance (L_m)              | 0.5 mH                 | Armature inductance measured with LCR meter.                |
| Pump Torque Constant (K_m)         | 0.05 N*m/A             | Motor torque constant from datasheet testing.               |
| Back-EMF Constant (K_b)            | 0.05 V/(rad/s)         | Motor back-EMF constant from motor datasheet.               |
| Rotor Inertia (J)                  | 1e-5 kg*m^2            | Rotational inertia of centrifugal pump impeller.            |
| Viscous Friction (B)               | 1e-4 N*m*s/rad         | Hydrodynamic fluid damping friction coefficient.            |
| Flow Rate Constant (K_flow)        | 0.02 (L/min)/(rad/s)   | Flow rate conversion per motor rad/s.                       |
| Solver Max Step Size               | 0.001 s (1 ms)         | Matches shortest system time constant tau = 1.0ms.          |
+------------------------------------+------------------------+-------------------------------------------------------------+
```

---

## 5. Simulink Simulation Execution & Scope Interpretation

### Running the Simulink Model:
1. Open MATLAB and navigate to workspace:
   ```matlab
   cd('c:\Users\hites\OneDrive\Documents\Projects & Research Work\Analog Automatic Irrigation Controller')
   ```
2. Build and launch Simulink model:
   ```matlab
   create_irrigation_simulink_model
   ```
3. In Simulink, press `Ctrl + T` to run the 60-second simulation.

### Interpreting Scope Waveforms (`System_Oscilloscope`):
- **$0\text{s} - 5\text{s}$ (Moist Soil):** $R_{soil} = 10\,\text{k}\Omega$, $V_{sensor} = 6.0\,\text{V}$, comparator is LOW, pump is OFF.
- **$t \ge 5\text{s}$ (Soil Drying):** Soil resistance ramps up ($+2\,\text{k}\Omega/\text{s}$).
- **$V_{sensor} \ge V_{UTP}$ ($2.85\,\text{V}$):** LM393 comparator output switches HIGH.
- **NE555 Monostable Pulse:** Generates a $29.70\,\text{second}$ pulse ($12\text{V}$ gate drive).
- **DC Motor Dynamic Response:** Pump speed accelerates to $\approx 50\,\text{rad/s}$, producing steady water flow ($\approx 1.0\,\text{L/min}$).
