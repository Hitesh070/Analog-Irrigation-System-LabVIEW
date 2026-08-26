# =========================================================================
# PYTHON SCRIPT TO GENERATE EXCEL FILE FOR SMART IRRIGATION & MIST SYSTEM
# =========================================================================
# File: build_excel_file.py
# Description: Generates 'Documentaion/Analog_Irrigation_Controller_BOM_and_Component_List.xlsx'
#              containing hardware BOM, pin connections, and parameter tables
#              for ESP32/Arduino & Analog Smart Climate Controller.
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
        [2, "Temp & Humidity Sensor", "DHT11 / DHT22 Sensor Module", "Canopy Climate Subsystem", "Measures foliage canopy relative humidity (% RH) and ambient air temperature (°C)", 1, 150],
        [3, "Soil Moisture Sensor", "Resistive Soil Sensor Module", "Root Zone Irrigation", "Stainless steel probe bridge measuring soil moisture resistance R_soil (1kΩ wet to 200kΩ dry)", 1, 60],
        [4, "Ultrasonic Mist Creators", "108kHz Piezo Transducer Discs", "Foliage Misting Subsystem", "2 Nos. ultrasonic atomizer discs converting water into micro-fine mist for leaves above soil", 2, 150],
        [5, "Submersible Water Pump", "12V DC 3W Mini Pump", "Root Zone Actuator", "Small DC water pump delivering water from storage tank to soil roots during irrigation cycle", 1, 250],
        [6, "Small Cooling Fan", "12V 0.15A Brushless DC Fan", "Thermal Ventilation", "Small DC fan providing air ventilation and thermal cooling when temperature exceeds threshold", 1, 90],
        [7, "Tank Water Level Sensor", "Reed Float Switch", "Dry-Run Safety Switch", "Detects storage tank water level to prevent pump dry-running and thermal motor burnout", 1, 50],
        [8, "Water Flow Sensor", "YF-S201 Hall-Effect Sensor", "Flow Rate Protection", "Monitors pump prime flow rate and total volume delivered; detects pipe blockages", 1, 180],
        [9, "Relay / MOSFET Module", "4-Channel Relay / MOSFET Board", "Actuator Power Drivers", "Switches high-current 12V DC loads (Water Pump, Cooling Fan, 2x Piezo Mist Creators)", 1, 150],
        [10, "Dual Op-Amp IC", "LM358 DIP-8", "Analog Signal Buffer", "Configured as unity-gain voltage follower with RC filter (fc=159.15Hz). Removes sensor noise", 1, 30],
        [11, "Quad Comparator IC", "LM339 / LM393 DIP-14", "Schmitt Trigger Comparators", "Ch 1: Soil Moisture; Ch 2: Canopy Humidity; Ch 3: NTC Temperature Threshold", 1, 40],
        [12, "Dual Precision Timer IC", "NE556 DIP-14", "Hardware Pulse Timers", "Timer 1: 30s soil pump pulse; Timer 2: 15s foliage misting pulse", 1, 35],
        [13, "NPN Transistors", "BC547 TO-92", "Safety Interlocks", "BC547 #1: Tank float switch reset; BC547 #2: Piezo atomizer driver switch", 2, 10],
        [14, "Voltage Regulator IC", "LM7812 TO-220", "Power Supply Unit", "Converts unregulated DC to stable +12.0V DC regulated supply rail for actuators and ICs", 1, 20],
        [15, "Flyback Diodes", "1N4007 (1A 1000V)", "Inductive Protection", "Anti-parallel across pump and cooling fan terminals to absorb inductive voltage kickback spikes", 2, 10],
        [16, "Bridge Rectifier & Transformer", "230V to 15V AC Transformer, W04M", "Power Supply Unit", "Steps down 230V AC mains electricity and rectifies to DC for power supply filtering", 1, 200],
        [17, "Potentiometers", "10kΩ & 270kΩ Pots", "Calibration Controls", "VR1 soil threshold; VR2 watering pulse; VR3 humidity threshold; VR4 temperature threshold", 4, 20],
        [18, "Fixed Resistors & Caps", "Resistors, Caps, LEDs, PCB", "Passives & Assembly", "Assorted resistors, electrolytic & ceramic caps, diagnostic status LEDs, and breadboard", 1, 150]
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

    # Save Workbook
    out_dir = os.path.join(os.getcwd(), "Documentaion")
    os.makedirs(out_dir, exist_ok=True)
    filename = "Analog_Irrigation_Controller_BOM_and_Component_List.xlsx"
    output_path = os.path.join(out_dir, filename)
    wb.save(output_path)
    print(f"Successfully generated Master Excel File: {output_path}")

if __name__ == '__main__':
    build_excel()
