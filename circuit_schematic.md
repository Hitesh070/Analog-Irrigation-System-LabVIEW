# Hardware Engineering Guide & Circuit Schematics
## Analog Automatic Irrigation Controller (Microcontroller-Free)

This document provides complete hardware schematics, pin connections, component specifications, mathematical design formulas, and breadboard wiring netlists for constructing the **Analog Automatic Irrigation Controller**.

---

## 1. System Block Diagram & Stage Architecture

```
                                +-------------------------+
                                |  Soil Moisture Sensor   |
                                | (Probes + 10k Divider)  |
                                +------------+------------+
                                             |
                                             v (TP1)
                                +------------+------------+
                                |    Stage 2: Op-Amp      |
                                |  Signal Conditioning    |
                                |   (LM358 Unity Buffer)  |
                                +------------+------------+
                                             |
                                             v (TP2)
                                +------------+------------+
                                |  Stage 3 & 4: Comparator|
                                |   + Schmitt Trigger     |
                                | (LM393 + RHysteresis)   |
                                +------------+------------+
                                             |
                                             v (TP3)
                                +------------+------------+
                                |  Stage 5: NE555 Timer   |
                                | (Monostable Mode Pulse) |
                                +------------+------------+
                                             |
                                             v (TP4)
                                +------------+------------+
                                | Stage 6: MOSFET Driver  |
                                |  (IRFZ44N Logic Driver) |
                                +------------+------------+
                                             |
                                             v (TP5)
                                +------------+------------+
                                |    12V DC Water Pump    |
                                | + 1N4007 Flyback Diode  |
                                +-------------------------+

  [Water Tank Float Sensor] ----+
                                +---> Stage 7: Tank & Dry-Run Protection (BC547 Reset)
  [Current / Flow Switch]   ----+
```

---

## 2. Complete Component Netlist & Pin Connections

### A. Stage 8: Power Supply Unit (12V Regulated DC Rail)
- **Component:** LM7812 3-Terminal Voltage Regulator
  - **Pin 1 (Input):** Connected to Rectified Filtered DC Voltage ($+15\text{V to } +18\text{V DC}$) from Bridge Rectifier ($W04M$) and $1000\mu\text{F} / 25\text{V}$ electrolytic capacitor.
  - **Pin 2 (Ground):** Connected to Common Circuit Ground ($\text{GND}$).
  - **Pin 3 (Output):** $+12\text{V DC}$ Main Power Rail. Decoupled with $0.1\mu\text{F}$ ceramic capacitor to $\text{GND}$.

---

### B. Stage 1 & 2: Soil Moisture Sensor Bridge & LM358 Signal Conditioner
- **Components:** Stainless Steel Probes, $10\text{k}\Omega$ Fixed Resistor ($R_1$), LM358 Dual Op-Amp (IC1A).
- **Wiring Connections:**
  - $+12\text{V}$ Rail $\rightarrow$ Fixed Resistor $R_1 (10\text{k}\Omega)$ $\rightarrow$ Node **TP1**.
  - Node **TP1** $\rightarrow$ Soil Moisture Probe Pin A.
  - Soil Moisture Probe Pin B $\rightarrow$ Circuit $\text{GND}$.
  - Node **TP1** $\rightarrow$ LM358 Pin 3 ($\text{Non-Inverting Input } 1+$).
  - LM358 Pin 1 ($\text{Output } 1$) $\rightarrow$ LM358 Pin 2 ($\text{Inverting Input } 1-$) [Unity Gain Voltage Buffer configuration].
  - LM358 Pin 8 $\rightarrow +12\text{V}$ Rail; LM358 Pin 4 $\rightarrow \text{GND}$.
  - Filter Capacitor: $0.1\mu\text{F}$ between Pin 3 and $\text{GND}$ to eliminate AC noise spikes.

---

### C. Stage 3 & 4: LM393 Comparator with Schmitt Trigger Hysteresis
- **Components:** LM393 Dual Comparator (IC2A), $10\text{k}\Omega$ Potentiometer ($VR_1$), Hysteresis Resistor $R_H (100\text{k}\Omega - 470\text{k}\Omega)$, $10\text{k}\Omega$ Pull-up Resistor ($R_{pullup}$).
- **Wiring Connections:**
  - LM358 Pin 1 (Buffered Voltage **TP2**) $\rightarrow$ LM393 Pin 2 ($\text{Inverting Input } 1-$).
  - Potentiometer $VR_1$ Wiper $\rightarrow$ LM393 Pin 3 ($\text{Non-Inverting Input } 1+$).
  - Hysteresis Feedback Resistor $R_H (100\text{k}\Omega)$ connected between LM393 Pin 1 ($\text{Output } 1$) and LM393 Pin 3 ($\text{Non-Inverting Input } 1+$).
  - Pull-up Resistor $R_{pullup} (10\text{k}\Omega)$ connected between LM393 Pin 1 ($\text{Output } 1$) and $+12\text{V}$ Rail (since LM393 has an open-collector output).

#### Mathematical Threshold Equations:
$$V_{ref} = V_{CC} \times \frac{R_{pot\_bottom}}{R_{pot\_total}}$$
$$V_{UTP} = V_{ref} + (V_{CC} - V_{ref}) \times \frac{R_{pot\_parallel}}{R_H}$$
$$V_{LTP} = V_{ref} - V_{ref} \times \frac{R_{pot\_parallel}}{R_H}$$
$$\Delta V_{Hysteresis} = V_{UTP} - V_{LTP}$$

---

### D. Stage 5: NE555 Monostable Irrigation Timer
- **Components:** NE555 Precision Timer IC (IC3), Timing Potentiometer $VR_2 (250\text{k}\Omega / 470\text{k}\Omega)$, Timing Capacitor $C_T (100\mu\text{F} / 220\mu\text{F})$, $0.01\mu\text{F}$ Ceramic Cap.
- **Wiring Connections:**
  - NE555 Pin 8 ($V_{CC}$) $\rightarrow +12\text{V}$; NE555 Pin 1 ($\text{GND}$) $\rightarrow \text{GND}$.
  - NE555 Pin 4 ($\text{RESET}$) $\rightarrow$ Connected to Tank/Fault Protection Circuit (normally pulled HIGH via $10\text{k}\Omega$ to $+12\text{V}$).
  - NE555 Pin 5 ($\text{CONTROL}$) $\rightarrow 0.01\mu\text{F}$ capacitor to $\text{GND}$.
  - LM393 Pin 1 (Comparator Output **TP3**) $\rightarrow$ Differentiating Capacitor ($0.1\mu\text{F}$) $\rightarrow$ NE555 Pin 2 ($\text{TRIGGER}$).
  - NE555 Pin 6 ($\text{THRESHOLD}$) tied directly to NE555 Pin 7 ($\text{DISCHARGE}$).
  - Timing Resistor $VR_2 (270\text{k}\Omega)$ connected between $+12\text{V}$ and Pin 6/7 junction (**TP4**).
  - Timing Capacitor $C_T (100\mu\text{F})$ connected between Pin 6/7 junction (**TP4**) and $\text{GND}$.
  - NE555 Pin 3 ($\text{OUTPUT}$) $\rightarrow$ Output Pulse to MOSFET Gate Driver.

#### Monostable Pulse Duration Formula:
$$T = 1.1 \times R_T \times C_T$$
- *Example:* With $R_T = 270\text{k}\Omega$ and $C_T = 100\mu\text{F}$:
  $$T = 1.1 \times (270 \times 10^3) \times (100 \times 10^{-6}) = 29.7\text{ Seconds}$$

---

### E. Stage 6: MOSFET Driver & DC Water Pump Protection
- **Components:** IRFZ44N N-Channel Power MOSFET, $100\Omega$ Gate Resistor ($R_G$), $10\text{k}\Omega$ Gate Pull-down ($R_{GS}$), 1N4007 Flyback Rectifier Diode.
- **Wiring Connections:**
  - NE555 Pin 3 ($\text{OUTPUT}$) $\rightarrow R_G (100\Omega) \rightarrow$ IRFZ44N Gate Pin (**G**).
  - Gate Pull-down Resistor $R_{GS} (10\text{k}\Omega)$ connected between Gate (**G**) and Source (**S**).
  - IRFZ44N Source Pin (**S**) $\rightarrow \text{GND}$.
  - IRFZ44N Drain Pin (**D**) $\rightarrow$ Negative terminal of 12V DC Water Pump.
  - Positive terminal of 12V DC Water Pump $\rightarrow +12\text{V}$ Rail.
  - Flyback Protection Diode (1N4007): Anode to Drain (**D**), Cathode to $+12\text{V}$ Rail.

---

### F. Stage 7: Water Tank Protection & Dry-Run Interlock
- **Components:** BC547 NPN Transistor, $10\text{k}\Omega$ Base Resistor ($R_B$), Water Level Float Switch / Tank Probes, Red Warning LED.
- **Wiring Connections:**
  - Water Tank Float Switch connected between $+12\text{V}$ and BC547 Base resistor $R_B (10\text{k}\Omega)$.
  - When tank has water: Switch is CLOSED $\rightarrow$ BC547 Base is HIGH $\rightarrow$ Transistor ON $\rightarrow$ Collector pulls down Red Fault LED (OFF) and allows 555 Pin 4 ($\text{RESET}$) to remain pulled HIGH ($+12\text{V}$).
  - When tank is EMPTY: Switch is OPEN $\rightarrow$ BC547 Base is LOW $\rightarrow$ Transistor OFF $\rightarrow$ 555 Pin 4 ($\text{RESET}$) is pulled to $\text{GND} \rightarrow$ 555 output forced to 0V immediately $\rightarrow$ Red Tank Empty LED turns ON.

---

## 3. Status LED Color Matrix & Diagnostic Guide

| LED Name | Color | Active State | Meaning |
|---|---|---|---|
| **Power** | 🟢 Green | Continuous ON | +12V DC Supply is healthy |
| **Dry Soil** | 🟡 Yellow | ON when $V_{sensor} \ge V_{UTP}$ | Soil moisture is below threshold (needs water) |
| **Pump Running** | 🔵 Blue | ON during monostable pulse | MOSFET conducting; 12V DC Pump active |
| **Tank / Fault** | 🔴 Red | ON when tank empty or dry-run fault | Safety interlock active; pump locked OFF |

---

## 4. Hardware Verification & Calibration Procedure

1. **Power Supply Testing:**
   - Apply 230V AC to transformer primary. Measure secondary AC voltage (~15V AC).
   - Measure 7812 output pin. Ensure stable $+12.0\text{V} \pm 0.2\text{V}$ DC output.
2. **Moisture Probe Calibration:**
   - Place probes in dry soil. Measure voltage at **TP1**. Adjust $VR_1$ until Yellow LED turns ON.
   - Insert probes into moist soil. Verify that Yellow LED turns OFF only after soil reaches the lower hysteresis threshold ($V_{LTP}$).
3. **Irrigation Duration Adjustment:**
   - Adjust potentiometer $VR_2$. Verify pump runs for the desired period (e.g., 30s to 2 mins) upon dry soil trigger.
4. **Tank Protection Verification:**
   - Disconnect or open tank float switch. Confirm Red Fault LED turns ON and pump stops instantly, even if dry soil demand persists.
