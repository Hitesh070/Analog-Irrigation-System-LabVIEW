# Step-by-Step Manual: How to Run the Simulink Model
## Analog Automatic Irrigation Controller (`Analog_Irrigation_Control_System.slx`)

This guide provides step-by-step instructions on generating, running, inspecting, and modifying the **Analog Automatic Irrigation Controller** Simulink block model in MATLAB and Simulink.

---

## 1. System Requirements & Setup

- **Software:** MATLAB R2020a or newer with standard Simulink library installed.
- **Toolboxes:** Standard Simulink Base Library (No external 3rd-party toolboxes needed).
- **Project Folder Path:**
  `c:\Users\hites\OneDrive\Documents\Projects & Research Work\Analog Automatic Irrigation Controller`

---

## 2. Step-by-Step Execution Guide

### Step 1: Open MATLAB and Set Working Directory
1. Launch MATLAB.
2. In the MATLAB Command Window, execute:
   ```matlab
   cd('c:\Users\hites\OneDrive\Documents\Projects & Research Work\Analog Automatic Irrigation Controller')
   ```

### Step 2: Programmatically Generate the Simulink Model
To automatically build, configure all block function parameters, wire signal connections, and open the model:
1. In the MATLAB Command Window, run:
   ```matlab
   create_irrigation_simulink_model
   ```
2. **What Happens Automatically:**
   - MATLAB initializes a new Simulink model named `Analog_Irrigation_Control_System.slx`.
   - Native library blocks (`Ramp`, `Fxn`, `Transfer Fcn`, `Relay`, `Discrete-Time Integrator`, `Product`, `Gain`, `Scope`) are instantiated.
   - Calculated function parameters ($V_{UTP} = 2.85\,\text{V}, V_{LTP} = 2.15\,\text{V}, T_{pulse} = 29.7\,\text{s}, G_{pump}(s)$) are set.
   - Signal nets are connected and the model is saved to disk.
   - The Simulink graphical editor window opens displaying the block diagram.

---

### Step 3: Inspecting the Simulink Block Diagram

Once the Simulink window opens, you will observe 8 interconnected block stages:

```
[Soil_Moisture_Drying_Ramp]
         │
         ▼
[Sensor_Divider_Bridge] (V_sensor = 12 * R / (10000 + R))
         │
         ▼
[OpAmp_Buffer_LM358] (G(s) = 1 / (0.001s + 1))
         │
         ▼
[LM393_Schmitt_Trigger] (Relay: On = 2.85V, Off = 2.15V)
         │
         ▼
[NE555_Monostable_Pulse] (29.7s Duration Pulse)
         │
         ▼
[Safety_Interlock_AND] <─── [Water_Tank_Level_Sensor] (Constant = 1)
         │
         ▼
[MOSFET_IRFZ44N_Driver] (Gain K = 12.0)
         │
         ▼
[DC_Pump_Motor_Dynamics] (Transfer Fcn G_pump(s))
         │
         ▼
[Flow_Rate_Converter] ───► [System_Oscilloscope]
```

---

### Step 4: Configuring Solver Settings & Running Simulation

1. **Verify Solver Settings:**
   - In Simulink menu, go to **Modeling** ➔ **Model Settings** (`Ctrl + E`).
   - **Stop Time:** `60` seconds.
   - **Solver Type:** Variable-step, `ode45` (Dormand-Prince).
   - **Max Step Size:** `0.001` ($1.0\,\text{ms}$, matches filter time constant $\tau = 1\,\text{ms}$).
2. **Run Simulation:**
   - Click the green **Run** button in the Simulink toolbar (or press `Ctrl + T`).
   - The progress bar at the bottom will complete to 100%.

---

### Step 5: Viewing Scopes & Dynamic Waveforms

1. Double-click the **`System_Oscilloscope`** block in the Simulink canvas.
2. A scope window will open showing the output flow rate response.
3. **Observing Dynamic Behavior:**
   - From $t = 0\text{s}$ to $t = 5\text{s}$, soil resistance is $10\,\text{k}\Omega$ (moist), $V_{sensor} = 6.0\,\text{V}$ (below $V_{UTP}$), comparator remains LOW, pump stays OFF.
   - From $t = 5\text{s}$ onwards, soil dries out ($+2\,\text{k}\Omega/\text{s}$).
   - When sensor voltage reaches **$V_{UTP} = 2.85\,\text{V}$**, the LM393 Schmitt trigger switches **HIGH**.
   - The NE555 timer triggers, producing a **$29.7\,\text{second}$ irrigation pulse**.
   - IRFZ44N MOSFET gate receives $12\,\text{V}$, driving the DC pump motor up to nominal speed ($\approx 50\,\text{rad/s}$) and delivering water flow ($\approx 1.0\,\text{L/min}$).

---

### Step 6: How to Modify Simulation Function Parameters

You can double-click any block in Simulink to modify its parameters:

- **To Change Watering Duration:**
  - Double-click `NE555_Monostable_Pulse` or edit `R_timer` / `C_timer` in `create_irrigation_simulink_model.m`.
- **To Change Soil Dryness Trigger Threshold:**
  - Double-click `LM393_Schmitt_Trigger` and change `OnSwitchValue` ($V_{UTP}$) or `OffSwitchValue` ($V_{LTP}$).
- **To Test Water Tank Empty Fault:**
  - Double-click `Water_Tank_Level_Sensor` and change `Value` from `1` to `0`. Run simulation to confirm pump remains locked OFF.

---

### Step 7: Running Standalone MATLAB Simulation & Plotting

To run the simulation directly in MATLAB without opening Simulink graphics:
1. In MATLAB Command Window, execute:
   ```matlab
   simulate_irrigation_controller
   ```
2. A 4-panel MATLAB figure will immediately open displaying:
   - Panel 1: Sensor & Op-Amp Buffer Voltages ($V_{sensor}, V_{buf}, V_{UTP}, V_{LTP}$).
   - Panel 2: LM393 Schmitt Trigger Comparator Output.
   - Panel 3: NE555 Monostable Pulse & MOSFET Gate Voltage.
   - Panel 4: DC Water Pump Speed ($\text{rad/s}$) & Flow Rate ($\text{L/min}$).

---

## 3. Troubleshooting & FAQs

- **Q: Simulink gives an error "Model name already open"?**
  - Solution: Run `close_system('Analog_Irrigation_Control_System', 0)` in MATLAB and re-run `create_irrigation_simulink_model`.
- **Q: Scope display looks blank or frozen?**
  - Solution: Click the **Autoscale** icon (binoculars icon) in the Scope window toolbar.
