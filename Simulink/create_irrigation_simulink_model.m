% =========================================================================
% PROGRAMMATIC SIMULINK MODEL GENERATOR FOR ANALOG IRRIGATION CONTROLLER
% =========================================================================
% File: create_irrigation_simulink_model.m
% Description: Automatically builds, configures parameters for, connects,
%              and saves the complete Simulink model 'Analog_Irrigation_Control_System.slx'
%              using native Simulink library blocks and exact function parameters.
% =========================================================================

clear; clc;

modelName = 'Analog_Irrigation_Control_System';

% Close model if already loaded to ensure clean build
if bdIsLoaded(modelName)
    close_system(modelName, 0);
end

% Create and open new Simulink system
new_system(modelName);
open_system(modelName);

fprintf('=================================================================\n');
fprintf('  BUILDING SIMULINK CONTROL MODEL: %s.slx\n', modelName);
fprintf('=================================================================\n\n');

%% 1. PARAMETER DEFINITIONS (Determined from Physical Calculations)
Vcc = 12.0;           % Regulated DC Power Supply Rail (V)
R_fixed = 10000;      % Fixed Divider Resistor (Ohms)
R_pot = 10000;        % Reference Potentiometer Resistance (Ohms)
R_H = 100000;         % Hysteresis Feedback Resistor (Ohms)
V_ref = 2.50;         % Potentiometer Reference Voltage (V)

% Calculated Schmitt Trigger Thresholds
V_UTP = V_ref + (Vcc - V_ref) * (R_pot / (R_H + R_pot)); % 2.85V
V_LTP = V_ref - V_ref * (R_pot / (R_H + R_pot));         % 2.15V

% 555 Monostable Timing Parameters
R_timer = 270000;     % Timing Potentiometer (Ohms)
C_timer = 100e-6;     % Timing Capacitor (Farads)
T_pulse = 1.1 * R_timer * C_timer; % 29.7 Seconds

% DC Pump Motor Dynamic Parameters
K_m = 0.05;           % Torque Constant (N*m/A)
K_b = 0.05;           % Back-EMF Constant (V/(rad/s))
R_m = 4.0;            % Armature Resistance (Ohms)
L_m = 0.5e-3;         % Armature Inductance (H)
J = 1e-5;             % Moment of Inertia (kg*m^2)
B = 1e-4;             % Friction Coefficient (N*m*s/rad)
K_flow = 0.02;        % Flow Rate Conversion Constant (L/min per rad/s)

%% 2. ADD SIMULINK BLOCKS WITH EXACT FUNCTION PARAMETERS

% Block 1: Soil Moisture Drying Simulation Source (Ramp)
add_block('simulink/Sources/Ramp', [modelName, '/Soil_Moisture_Drying_Ramp'], ...
    'Position', [30, 75, 75, 115], ...
    'Slope', '2000', ...        % Soil drying rate: +2 kOhm/s
    'Start', '5', ...           % Starts drying at t = 5s
    'InitialOutput', '10000');  % Initial resistance: 10 kOhm (Wet Soil)

% Block 2: Stage 1 Sensor Voltage Divider Math (Fcn Block)
add_block('simulink/User-Defined Functions/Fcn', [modelName, '/Sensor_Divider_Bridge'], ...
    'Position', [115, 75, 195, 115], ...
    'Expr', '12 * u(1) / (10000 + u(1))');

% Block 3: Stage 2 LM358 Op-Amp Buffer & RC Low-Pass Filter (Transfer Fcn)
% G_buf(s) = 1 / (0.001 s + 1)
add_block('simulink/Continuous/Transfer Fcn', [modelName, '/OpAmp_Buffer_LM358'], ...
    'Position', [235, 75, 325, 115], ...
    'Numerator', '[1]', ...
    'Denominator', '[0.001 1]');

% Block 4: Stage 3 & 4 LM393 Schmitt Trigger Comparator (Relay with Hysteresis)
add_block('simulink/Discontinuities/Relay', [modelName, '/LM393_Schmitt_Trigger'], ...
    'Position', [365, 75, 425, 115], ...
    'OnSwitchValue', sprintf('%.2f', V_UTP), ...   % Switch ON at V_UTP = 2.85V
    'OffSwitchValue', sprintf('%.2f', V_LTP), ...  % Switch OFF at V_LTP = 2.15V
    'OnOutputValue', '1', ...
    'OffOutputValue', '0');

% Block 5: Stage 5 NE555 Monostable Timing Pulse Integrator (Integrator Subsystem)
add_block('simulink/Discrete/Discrete-Time Integrator', [modelName, '/NE555_Monostable_Pulse'], ...
    'Position', [465, 75, 525, 115], ...
    'SampleTime', '0.01');

% Block 6: Stage 7 Water Tank Level Float Sensor (Constant = 1 for Tank Full, 0 for Empty)
add_block('simulink/Sources/Constant', [modelName, '/Water_Tank_Level_Sensor'], ...
    'Position', [465, 155, 505, 175], ...
    'Value', '1'); % 1 = Water Available, 0 = Tank Empty

% Block 7: Stage 7 Safety Protection Interlock (Product / AND Gate)
add_block('simulink/Math Operations/Product', [modelName, '/Safety_Interlock_AND'], ...
    'Position', [565, 85, 595, 145], ...
    'Inputs', '2');

% Block 8: Stage 6 IRFZ44N MOSFET Driver Gate Drive Gain (Gain = 12.0)
add_block('simulink/Math Operations/Gain', [modelName, '/MOSFET_IRFZ44N_Driver'], ...
    'Position', [635, 100, 695, 130], ...
    'Gain', '12'); % Converts logic to 12V gate drive

% Block 9: Stage 6 DC Water Pump Motor Dynamic Model (Transfer Fcn)
% G_pump(s) = 0.05 / (5e-9 s^2 + 4.005e-5 s + 0.0029)
num_pump = sprintf('[%.2f]', K_m);
den_pump = sprintf('[%.1e %.4e %.4f]', (L_m*J), (L_m*B + R_m*J), (R_m*B + K_m*K_b));

add_block('simulink/Continuous/Transfer Fcn', [modelName, '/DC_Pump_Motor_Dynamics'], ...
    'Position', [735, 95, 845, 135], ...
    'Numerator', num_pump, ...
    'Denominator', den_pump);

% Block 10: Pump Water Flow Rate Calculation Gain (Gain K_flow)
add_block('simulink/Math Operations/Gain', [modelName, '/Flow_Rate_Converter'], ...
    'Position', [885, 100, 935, 130], ...
    'Gain', sprintf('%.3f', K_flow));

% Block 11: Multi-Channel System Oscilloscope (Scope)
add_block('simulink/Sinks/Scope', [modelName, '/System_Oscilloscope'], ...
    'Position', [975, 95, 1015, 135], ...
    'NumInputPorts', '1');

%% 3. WIRE BLOCK SIGNAL NETS

add_line(modelName, 'Soil_Moisture_Drying_Ramp/1', 'Sensor_Divider_Bridge/1');
add_line(modelName, 'Sensor_Divider_Bridge/1', 'OpAmp_Buffer_LM358/1');
add_line(modelName, 'OpAmp_Buffer_LM358/1', 'LM393_Schmitt_Trigger/1');
add_line(modelName, 'LM393_Schmitt_Trigger/1', 'NE555_Monostable_Pulse/1');

add_line(modelName, 'NE555_Monostable_Pulse/1', 'Safety_Interlock_AND/1');
add_line(modelName, 'Water_Tank_Level_Sensor/1', 'Safety_Interlock_AND/2');

add_line(modelName, 'Safety_Interlock_AND/1', 'MOSFET_IRFZ44N_Driver/1');
add_line(modelName, 'MOSFET_IRFZ44N_Driver/1', 'DC_Pump_Motor_Dynamics/1');
add_line(modelName, 'DC_Pump_Motor_Dynamics/1', 'Flow_Rate_Converter/1');
add_line(modelName, 'Flow_Rate_Converter/1', 'System_Oscilloscope/1');

%% 4. CONFIGURE SIMULATION SOLVER & SAVE MODEL
set_param(modelName, 'StopTime', '60');         % 60-second total simulation
set_param(modelName, 'Solver', 'ode45');        % Runge-Kutta variable step solver
set_param(modelName, 'MaxStep', '0.001');       % Maximum step size 1 ms
set_param(modelName, 'SaveOutput', 'on');
set_param(modelName, 'OutputSaveName', 'vout');

save_system(modelName);

fprintf('Simulink Model "%s.slx" created, configured with function parameters, and saved successfully.\n', modelName);
