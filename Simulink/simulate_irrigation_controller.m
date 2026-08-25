% =========================================================================
% ANALOG AUTOMATIC IRRIGATION CONTROLLER - MATLAB CONTROL SYSTEM SIMULATION
% =========================================================================
% File: simulate_irrigation_controller.m
% Description: Standalone base MATLAB simulation script for the discrete analog
%              irrigation control system. Does NOT require Control System Toolbox.
%              Computes gain blocks, Schmitt trigger hysteresis, 555 monostable timing,
%              DC pump motor dynamics using native ODE solvers, and plots waveforms.
% =========================================================================

clear; clc; close all;

fprintf('=================================================================\n');
fprintf('  ANALOG AUTOMATIC IRRIGATION CONTROLLER - CONTROL SYSTEM SIM ENGINE\n');
fprintf('=================================================================\n\n');

%% 1. SYSTEM CONSTANTS & HARDWARE PARAMETERS
Vcc = 12.0;            % Regulated Power Supply Rail (Volts DC)
R_fixed = 10e3;        % Fixed Divider Resistor (Ohms) = 10 kOhm
R_pot = 10e3;          % Reference Potentiometer Total Resistance (Ohms) = 10 kOhm
R_H = 100e3;           % Schmitt Trigger Hysteresis Feedback Resistor (Ohms) = 100 kOhm

% 555 Monostable Timing Components
R_timer = 270e3;       % Timing Potentiometer Resistor (Ohms) = 270 kOhm
C_timer = 100e-6;      % Timing Capacitor (Farads) = 100 uF

% Signal Conditioner RC Low-Pass Filter
R_filter = 10e3;       % Filter Resistor (Ohms) = 10 kOhm
C_filter = 0.1e-6;     % Filter Capacitor (Farads) = 0.1 uF
tau_filter = R_filter * C_filter; % Time Constant tau = 1 ms

% DC Pump Motor Parameters (12V DC Submersible Pump)
R_m = 4.0;             % Armature Resistance (Ohms)
L_m = 0.5e-3;          % Armature Inductance (Henries)
K_m = 0.05;            % Torque Constant (N*m / A)
K_b = 0.05;            % Back-EMF Constant (V / (rad/s))
J = 1e-5;              % Rotor Moment of Inertia (kg * m^2)
B = 1e-4;              % Viscous Friction Coefficient (N*m*s / rad)
K_flow = 0.02;         % Flow Rate Constant (Liters per minute per rad/s)

%% 2. GAIN BLOCK & THRESHOLD CALCULATIONS

% A. Stage 1: Moisture Sensor Voltage Divider Gain
R_soil_0 = 50e3;
K_div = (Vcc * R_fixed) / ((R_fixed + R_soil_0)^2); % Volts / Ohm

% B. Stage 2: LM358 Op-Amp Buffer Unity Gain
K_buf = 1.0;

% C. Stage 3 & 4: LM393 Schmitt Trigger Hysteresis Thresholds
V_ref = 2.50; % Reference Voltage set by Potentiometer (Volts)
V_UTP = V_ref + (Vcc - V_ref) * (R_pot / (R_H + R_pot)); % Upper Threshold (V)
V_LTP = V_ref - V_ref * (R_pot / (R_H + R_pot));         % Lower Threshold (V)
delta_V_Hyst = V_UTP - V_LTP;                          % Hysteresis Band (V)

% D. Stage 5: NE555 Monostable Timing Pulse Duration
T_pulse = 1.1 * R_timer * C_timer; % Duration T = 1.1 * R * C (Seconds)

% E. Stage 6: Logic MOSFET Driver Gain
K_gate = 12.0; % Logic-Level Gate Drive Gain (12V Gate Voltage)

%% 3. DISPLAY DERIVED GAINS & SYSTEM METRICS
fprintf('--- STAGE GAIN & TRANSFER FUNCTION METRICS ---\n');
fprintf('Sensor Divider Gain K_div      : %.3e V/Ohm\n', K_div);
fprintf('Op-Amp Buffer Gain K_buf       : %.2f (Unity Gain)\n', K_buf);
fprintf('Buffer Low-Pass Time Constant  : %.3f ms (Cutoff f_c = %.1f Hz)\n', tau_filter*1000, 1/(2*pi*tau_filter));
fprintf('Schmitt Trigger Upper V_UTP    : %.3f V\n', V_UTP);
fprintf('Schmitt Trigger Lower V_LTP    : %.3f V\n', V_LTP);
fprintf('Hysteresis Band delta_V_H      : %.3f V\n', delta_V_Hyst);
fprintf('555 Monostable Irrigation Pulse: %.2f Seconds\n', T_pulse);
fprintf('MOSFET Gate Driver Gain K_gate : %.1f V/V\n', K_gate);

%% 4. TIME-DOMAIN DYNAMIC SIMULATION (Toolbox-Free ODE Solvers)
dt = 0.01;
t_sim = 0:dt:60; % 60-second simulation timeline
N = length(t_sim);

% Simulate Soil Moisture Resistance Drying Trajectory
R_soil_sim = zeros(1, N);
for i = 1:N
    t = t_sim(i);
    if t <= 10
        R_soil_sim(i) = 10e3 + (110e3 / 10) * t;
    elseif t <= 40
        R_soil_sim(i) = 120e3;
    else
        R_soil_sim(i) = 120e3 - (110e3 / 20) * (t - 40);
    end
end

% Compute Sensor Voltage V_div(t)
V_sensor_sim = Vcc * (R_soil_sim ./ (R_fixed + R_soil_sim));

% Pass through Op-Amp Filter G_buf(s) using 1st-Order Euler ODE: dV_buf/dt = (V_sensor - V_buf) / tau
V_buf_sim = zeros(1, N);
V_buf_sim(1) = V_sensor_sim(1);
for i = 1:N-1
    dV = (V_sensor_sim(i) - V_buf_sim(i)) / tau_filter;
    V_buf_sim(i+1) = V_buf_sim(i) + dV * dt;
end

% Schmitt Trigger State Machine Execution
V_comp_sim = zeros(1, N);
schmitt_state = false;
for i = 1:N
    v_in = V_buf_sim(i);
    if v_in >= V_UTP
        schmitt_state = true;
    elseif v_in <= V_LTP
        schmitt_state = false;
    end
    V_comp_sim(i) = schmitt_state * Vcc;
end

% 555 Monostable Pulse Timer Simulation
V_timer_sim = zeros(1, N);
timer_active = false;
timer_start_time = 0;

for i = 2:N
    if V_comp_sim(i) > 6.0 && V_comp_sim(i-1) <= 6.0 && ~timer_active
        timer_active = true;
        timer_start_time = t_sim(i);
    end
    
    if timer_active
        elapsed = t_sim(i) - timer_start_time;
        if elapsed <= T_pulse
            V_timer_sim(i) = Vcc;
        else
            timer_active = false;
            V_timer_sim(i) = 0.0;
        end
    else
        V_timer_sim(i) = 0.0;
    end
end

% Safety Interlock (Tank Level = Full, Flow Sensor = Normal)
S_tank = 1.0;
S_flow = 1.0;
V_pump_gate = V_timer_sim * S_tank * S_flow;

% DC Pump Motor Dynamics using 2nd-Order State Space ODE (Toolbox-Free)
% d/dt [i_a; omega] = [ -R_m/L_m, -K_b/L_m; K_m/J, -B/J ] * [i_a; omega] + [ 1/L_m; 0 ] * V_gate
Omega_pump = zeros(1, N);
ia_pump = zeros(1, N);

for i = 1:N-1
    v_g = V_pump_gate(i);
    dia = (v_g - R_m * ia_pump(i) - K_b * Omega_pump(i)) / L_m;
    domega = (K_m * ia_pump(i) - B * Omega_pump(i)) / J;
    
    ia_pump(i+1) = max(0, ia_pump(i) + dia * dt);
    Omega_pump(i+1) = max(0, Omega_pump(i) + domega * dt);
end

Q_flow_sim = K_flow * Omega_pump;

%% 5. PLOT WAVEFORMS
fig = figure('Name', 'Analog Automatic Irrigation Controller - Control System Response', 'Position', [100, 100, 900, 700]);

subplot(4,1,1);
plot(t_sim, V_sensor_sim, 'b--', 'LineWidth', 1.5); hold on;
plot(t_sim, V_buf_sim, 'b-', 'LineWidth', 2);
yline(V_UTP, 'r--', 'V_{UTP} (Upper Threshold)');
yline(V_LTP, 'g--', 'V_{LTP} (Lower Threshold)');
grid on; ylabel('Voltage (V)');
title('Stage 1 & 2: Soil Sensor Voltage & Op-Amp Buffer Output (TP1 & TP2)');
legend('Raw Sensor V_{div}', 'Buffered V_{buf}', 'V_{UTP}', 'V_{LTP}', 'Location', 'northwest');

subplot(4,1,2);
plot(t_sim, V_comp_sim, 'm-', 'LineWidth', 2); grid on;
ylabel('Voltage (V)'); ylim([-1, 14]);
title('Stage 3 & 4: LM393 Schmitt Trigger Comparator Output (TP3)');

subplot(4,1,3);
plot(t_sim, V_timer_sim, 'c-', 'LineWidth', 2); hold on;
plot(t_sim, V_pump_gate, 'g--', 'LineWidth', 1.5); grid on;
ylabel('Voltage (V)'); ylim([-1, 14]);
title('Stage 5 & 6: NE555 Monostable Pulse & MOSFET Gate Voltage (TP4 & TP5)');
legend('NE555 Timer Pulse', 'MOSFET Gate Drive', 'Location', 'northwest');

subplot(4,1,4);
yyaxis left;
plot(t_sim, Omega_pump, 'r-', 'LineWidth', 2); ylabel('Motor Speed (rad/s)');
yyaxis right;
plot(t_sim, Q_flow_sim, 'b-', 'LineWidth', 2); ylabel('Flow Rate (L/min)');
grid on; xlabel('Time (Seconds)');
title('Stage 6: DC Water Pump Speed & Flow Rate Dynamic Response');

fprintf('\nSimulation completed successfully. Waveforms plotted.\n');
