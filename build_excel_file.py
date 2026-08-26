# =========================================================================
# PYTHON SCRIPT TO GENERATE EXCEL FILE FOR SMART IRRIGATION & MIST SYSTEM
# =========================================================================
# File: build_excel_file.py
# Description: Generates 'Documentaion/Analog_Irrigation_Controller_BOM_and_Component_List.xlsx'
#              containing hardware BOM, pin connections, parameter tables, and
#              NI LabVIEW VISA HMI serial control interface details.
# =========================================================================

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_excel():
    wb = openpyxl.Workbook()

    header_fill = PatternFill(start_color="0F2B1D", end_color="0F2B1D", fill_type="solid") # Dark Forest Green
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    
    total_fill = PatternFill(start_color="D97706", end_color="D97706", fill_type="solid") # Amber Gold
    total_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")

    zebra_even = PatternFill(start_color="F7FAFC", end_color="F7FAFC", fill_type="solid")
    zebra_odd = PatternFill(start_color="EDF2F7", end_color="EDF2F7", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # -------------------------------------------------------------------------
    # SHEET 1: BILL OF MATERIALS & COST BREAKDOWN
    # -------------------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "Bill of Materials & Cost"
    ws1.views.sheetView[0].showGridLines = True

    headers1 = [
        "Item No.", "Hardware Component Name", "Part Spec / Model", 
        "Stage & Circuit Function", "Detailed Purpose & Circuit Use", 
        "Quantity", "Unit Price (₹)", "Total Cost (₹)"
    ]
    ws1.append(headers1)

    bom_data = [
        [1, "Microcontroller Board", "ESP32 DevKit V1 / Arduino Uno", "Main System Controller", "Processes soil resistance, DHT temp & humidity, tank level & flow rate sensors to control actuators", 1, 350],
        [2, "LabVIEW VISA Software HMI", "NI LabVIEW Community / 2020+", "Master Control Panel HMI", "Provides virtual gauges, sliders, waveform charts, and serial USB command interface for ESP32", 1, 0],
        [3, "Temp & Humidity Sensor", "DHT11 / DHT22 Sensor Module", "Canopy Climate Subsystem", "Measures foliage canopy relative humidity (% RH) and ambient air temperature (°C)", 1, 150],
        [4, "Soil Moisture Sensor", "Resistive Soil Sensor Module", "Root Zone Irrigation", "Stainless steel probe bridge measuring soil moisture resistance R_soil (1kΩ wet to 200kΩ dry)", 1, 60],
        [5, "Ultrasonic Mist Creators", "108kHz Piezo Transducer Discs", "Foliage Misting Subsystem", "2 Nos. ultrasonic atomizer discs converting water into micro-fine mist for leaves above soil", 2, 150],
        [6, "Submersible Water Pump", "12V DC 3W Mini Pump", "Root Zone Actuator", "Small DC water pump delivering water from storage tank to soil roots during irrigation cycle", 1, 250],
        [7, "Small Cooling Fan", "12V 0.15A Brushless DC Fan", "Thermal Ventilation", "Small DC fan providing air ventilation and thermal cooling when temperature exceeds threshold", 1, 90],
        [8, "Tank Water Level Sensor", "Reed Float Switch", "Dry-Run Safety Switch", "Detects storage tank water level to prevent pump dry-running and thermal motor burnout", 1, 50],
        [9, "Water Flow Sensor", "YF-S201 Hall-Effect Sensor", "Flow Rate Protection", "Monitors pump prime flow rate and total volume delivered; detects pipe blockages", 1, 180],
        [10, "Relay / MOSFET Module", "4-Channel Relay / MOSFET Board", "Actuator Power Drivers", "Switches high-current 12V DC loads (Water Pump, Cooling Fan, 2x Piezo Mist Creators)", 1, 150],
        [11, "Dual Op-Amp IC", "LM358 DIP-8", "Analog Signal Buffer", "Configured as unity-gain voltage follower with RC filter (fc=159.15Hz). Removes sensor noise", 1, 30],
        [12, "Quad Comparator IC", "LM339 / LM393 DIP-14", "Schmitt Trigger Comparators", "Ch 1: Soil Moisture; Ch 2: Canopy Humidity; Ch 3: NTC Temperature Threshold", 1, 40],
        [13, "Dual Precision Timer IC", "NE556 DIP-14", "Hardware Pulse Timers", "Timer 1: 30s soil pump pulse; Timer 2: 15s foliage misting pulse", 1, 35],
        [14, "NPN Transistors", "BC547 TO-92", "Safety Interlocks", "BC547 #1: Tank float switch reset; BC547 #2: Piezo atomizer driver switch", 2, 10],
        [15, "Voltage Regulator IC", "LM7812 TO-220", "Power Supply Unit", "Converts unregulated DC to stable +12.0V DC regulated supply rail for actuators and ICs", 1, 20],
        [16, "Flyback Diodes", "1N4007 (1A 1000V)", "Inductive Protection", "Anti-parallel across pump and cooling fan terminals to absorb inductive voltage kickback spikes", 2, 10],
        [17, "Bridge Rectifier & Transformer", "230V to 15V AC Transformer, W04M", "Power Supply Unit", "Steps down 230V AC mains electricity and rectifies to DC for power supply filtering", 1, 200],
        [18, "Potentiometers", "10kΩ & 270kΩ Pots", "Calibration Controls", "VR1 soil threshold; VR2 watering pulse; VR3 humidity threshold; VR4 temperature threshold", 4, 20],
        [19, "Fixed Resistors & Caps", "Resistors, Caps, LEDs, PCB", "Passives & Assembly", "Assorted resistors, electrolytic & ceramic caps, diagnostic status LEDs, and breadboard", 1, 150]
    ]

    for row_idx, item in enumerate(bom_data, start=2):
        formula = f"=F{row_idx}*G{row_idx}"
        ws1.cell(row=row_idx, column=1, value=item[0])
        ws1.cell(row=row_idx, column=2, value=item[1])
        ws1.cell(row=row_idx, column=3, value=item[2])
        ws1.cell(row=row_idx, column=4, value=item[3])
        ws1.cell(row=row_idx, column=5, value=item[4])
        ws1.cell(row=row_idx, column=6, value=item[5])
        ws1.cell(row=row_idx, column=7, value=item[6])
        ws1.cell(row=row_idx, column=8, value=formula)

    # Add Total Row
    total_row = len(bom_data) + 2
    ws1.cell(row=total_row, column=1, value="")
    ws1.cell(row=total_row, column=2, value="TOTAL ESTIMATED HARDWARE COST")
    ws1.cell(row=total_row, column=3, value="")
    ws1.cell(row=total_row, column=4, value="")
    ws1.cell(row=total_row, column=5, value="")
    ws1.cell(row=total_row, column=6, value="")
    ws1.cell(row=total_row, column=7, value="")
    ws1.cell(row=total_row, column=8, value=f"=SUM(H2:H{total_row-1})")

    # Format Sheet 1 Headers & Cells
    for col in range(1, 9):
        c = ws1.cell(row=1, column=col)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for r in range(2, total_row):
        fill = zebra_even if r % 2 == 0 else zebra_odd
        for col in range(1, 9):
            c = ws1.cell(row=r, column=col)
            c.fill = fill
            c.border = thin_border
            if col in [1, 6]:
                c.alignment = Alignment(horizontal="center", vertical="center")
            elif col in [7, 8]:
                c.alignment = Alignment(horizontal="right", vertical="center")
                c.number_format = '₹#,##0'
            else:
                c.alignment = Alignment(horizontal="left", vertical="center")

    # Format Total Row
    ws1.merge_cells(start_row=total_row, start_column=2, end_row=total_row, end_column=5)
    for col in range(1, 9):
        c = ws1.cell(row=total_row, column=col)
        c.fill = total_fill
        c.font = total_font
        c.border = thin_border
        if col == 8:
            c.alignment = Alignment(horizontal="right", vertical="center")
            c.number_format = '₹#,##0'
        elif col == 2:
            c.alignment = Alignment(horizontal="center", vertical="center")

    # -------------------------------------------------------------------------
    # SHEET 2: LABVIEW HMI & VISA SERIAL INTERFACE SPECIFICATIONS
    # -------------------------------------------------------------------------
    ws2 = wb.create_sheet(title="LabVIEW VISA HMI Spec")
    ws2.views.sheetView[0].showGridLines = True

    headers2 = ["LabVIEW HMI Component", "Control / Indicator Type", "Data Field / Command", "VISA Serial Protocol Specification", "Engineering Function"]
    ws2.append(headers2)

    labview_data = [
        ["VISA Resource Name", "Drop-Down Control", "VISA Resource (e.g. COM3)", "Baud Rate: 115200, 8 Data Bits, No Parity, 1 Stop Bit", "Establishes USB UART serial connection between PC LabVIEW and ESP32 / Arduino"],
        ["Soil Moisture Meter", "Numeric Gauge", "Soil Moisture Resistance (kΩ)", "Parsed from telemetry string: SOIL:<val>", "Displays real-time root soil probe resistance (1kΩ wet to 200kΩ dry)"],
        ["Humidity Meter", "Numeric Gauge", "Canopy Relative Humidity (% RH)", "Parsed from telemetry string: RH:<val>", "Displays real-time foliage canopy humidity from DHT sensor"],
        ["Temperature Meter", "Numeric Thermometer", "Ambient Air Temperature (°C)", "Parsed from telemetry string: TEMP:<val>", "Displays real-time ambient temperature from DHT sensor"],
        ["Water Flow Rate Meter", "Numeric Meter", "YF-S201 Flow Rate (L/min)", "Parsed from telemetry string: FLOW:<val>", "Displays real-time volumetric flow rate of the submersible pump"],
        ["Water Tank Level LED", "Boolean LED", "Tank Level State (Full/Empty)", "Parsed from telemetry string: TANK:<1/0>", "Green = Water Available; Red = Tank Empty (Dry-Run Lockout)"],
        ["Water Pump LED", "Boolean LED", "DC Water Pump State (ON/OFF)", "Parsed from telemetry string: PUMP:<1/0>", "Blue = Pump Active; Dark = Pump OFF"],
        ["Cooling Fan LED", "Boolean LED", "Cooling Fan State (ON/OFF)", "Parsed from telemetry string: FAN:<1/0>", "Cyan = Fan Active; Dark = Fan OFF"],
        ["Mist Creator #1 LED", "Boolean LED", "Piezo Atomizer #1 State", "Parsed from telemetry string: MIST1:<1/0>", "Purple = Ultrasonic Mist Creator #1 Active"],
        ["Mist Creator #2 LED", "Boolean LED", "Piezo Atomizer #2 State", "Parsed from telemetry string: MIST2:<1/0>", "Purple = Ultrasonic Mist Creator #2 Active"],
        ["Operation Mode Switch", "3-Position Ring Switch", "SET_MODE:AUTO / MANUAL / OFF", "Sends command packet to ESP32: SET_MODE:<mode>", "Allows user to switch between automatic control, manual override, and system shutdown"],
        ["Manual Pump Switch", "Boolean Toggle Switch", "PUMP:ON / PUMP:OFF", "Sends command packet to ESP32: PUMP:<1/0>", "Allows manual override activation of small DC water pump"],
        ["Manual Fan Switch", "Boolean Toggle Switch", "FAN:ON / FAN:OFF", "Sends command packet to ESP32: FAN:<1/0>", "Allows manual override activation of small DC cooling fan"],
        ["Manual Mist Switches", "Boolean Toggle Switches", "MIST1:ON / MIST2:ON", "Sends command packet to ESP32: MIST1:<1/0>, MIST2:<1/0>", "Allows manual override activation of 2 Nos. ultrasonic mist creators"],
        ["Soil Threshold Pointer", "Pointer / Slider Control", "SET_SOIL_THRES:<val>", "Sends command packet to ESP32: SET_SOIL_THRES:<val>", "Sets root soil dryness trigger threshold"],
        ["Humidity Target Pointer", "Pointer / Slider Control", "SET_RH_THRES:<val>", "Sends command packet to ESP32: SET_RH_THRES:<val>", "Sets foliage misting target humidity threshold"],
        ["Temp Target Pointer", "Pointer / Slider Control", "SET_TEMP_THRES:<val>", "Sends command packet to ESP32: SET_TEMP_THRES:<val>", "Sets thermal cooling fan target temperature threshold"],
        ["Waveform Chart", "Multi-Trace Chart", "Real-Time Telemetry Graph", "Updates at 10 Hz (100ms interval)", "Renders live dynamic trends for Soil, RH%, Temp, Flow, and Actuator Outputs"]
    ]

    for item in labview_data:
        ws2.append(item)

    for col in range(1, 6):
        c = ws2.cell(row=1, column=col)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center")

    for r in range(2, len(labview_data) + 2):
        fill = zebra_even if r % 2 == 0 else zebra_odd
        for col in range(1, 6):
            c = ws2.cell(row=r, column=col)
            c.fill = fill
            c.border = thin_border
            if col in [2, 3]:
                c.alignment = Alignment(horizontal="center", vertical="center")
            else:
                c.alignment = Alignment(horizontal="left", vertical="center")

    # Auto-adjust column widths
    for ws in [ws1, ws2]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if len(val_str) > max_len:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 14)

    # Save Workbook
    out_dir = os.path.join(os.getcwd(), "Documentaion")
    os.makedirs(out_dir, exist_ok=True)
    filename = "Analog_Irrigation_Controller_BOM_and_Component_List.xlsx"
    output_path = os.path.join(out_dir, filename)
    wb.save(output_path)
    print(f"Successfully generated Master Excel File: {output_path}")

if __name__ == '__main__':
    build_excel()
