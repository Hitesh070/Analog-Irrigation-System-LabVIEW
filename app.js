/* ==========================================================================
   TERRAFLOW MULTI-ZONE ECO-ANALOG IRRIGATION, MISTING & COOLING CONTROL
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // --- DOM Elements ---
  const modeBtns = document.querySelectorAll('.mode-btn');
  const rainToggle = document.getElementById('rain-sensor-toggle');
  const tankToggle = document.getElementById('tank-level-toggle');
  const dryrunToggle = document.getElementById('dryrun-fault-toggle');

  const ledPower = document.getElementById('led-power');
  const ledDry = document.getElementById('led-dry');
  const ledPump = document.getElementById('led-pump');
  const ledFan = document.getElementById('led-fan');
  const ledMist = document.getElementById('led-mist');
  const ledFault = document.getElementById('led-fault');

  // Meter 1: Soil Moisture
  const gaugeNeedle = document.getElementById('gauge-needle');
  const gaugeResVal = document.getElementById('gauge-res-val');
  const gaugeVoltVal = document.getElementById('gauge-volt-val');

  // Meter 2: Relative Humidity
  const humidityNeedle = document.getElementById('humidity-needle');
  const gaugeRhVal = document.getElementById('gauge-rh-val');
  const gaugeRhVolt = document.getElementById('gauge-rh-volt');

  // Meter 3: Ambient Temperature
  const tempNeedle = document.getElementById('temp-needle');
  const gaugeTempVal = document.getElementById('gauge-temp-val');
  const gaugeTempVolt = document.getElementById('gauge-temp-volt');

  // Sliders
  const moistureSlider = document.getElementById('moisture-slider');
  const moistureText = document.getElementById('moisture-text');
  const humiditySlider = document.getElementById('humidity-slider');
  const humidityText = document.getElementById('humidity-text');
  const tempSlider = document.getElementById('temp-slider');
  const tempText = document.getElementById('temp-text');

  const thresholdSlider = document.getElementById('threshold-slider');
  const thresholdText = document.getElementById('threshold-text');
  const rhThresholdSlider = document.getElementById('rh-threshold-slider');
  const rhThresholdText = document.getElementById('rh-threshold-text');
  const tempThresholdSlider = document.getElementById('temp-threshold-slider');
  const tempThresholdText = document.getElementById('temp-threshold-text');

  const timerStateBadge = document.getElementById('timer-state-badge');
  const timerCountdown = document.getElementById('timer-countdown');

  const waveCanvas = document.getElementById('waveform-canvas');
  const waveCtx = waveCanvas.getContext('2d');

  // --- State Variables ---
  let opMode = 'AUTO';
  let isRaining = false;
  let hasWaterInTank = true;
  let isPumpFlowNormal = true;

  // Environmental Inputs
  let soilResistance = 100; // kΩ (1k = wet, 200k = arid)
  let canopyHumidity = 35;   // RH% (10% = dry, 90% = humid)
  let ambientTemp = 38;      // °C (0°C = cold, 60°C = hot)
  
  let refThresholdSoil = 50; // kΩ
  let refThresholdRH = 60;   // RH%
  let refThresholdTemp = 32; // °C
  
  let vcc = 12.0;            // V DC
  let rFixed = 10.0;         // kΩ

  // State Machine Flags
  let schmittSoilState = false;
  let schmittMistState = false;
  let schmittTempState = false;

  let timerActiveSoil = false;
  let timerTimeRemainingSoil = 0;

  let timerActiveMist = false;
  let timerTimeRemainingMist = 0;

  let timerCapVoltage = 0.0;

  const waveHistory = {
    sensor: new Array(140).fill(2.5),
    comp: new Array(140).fill(0),
    timerCap: new Array(140).fill(0),
    mosfet: new Array(140).fill(0),
    fanDrive: new Array(140).fill(0),
    mistPiezo: new Array(140).fill(0)
  };

  // Switch Listeners
  modeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      modeBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      opMode = btn.dataset.mode;
      runSimulationStep();
    });
  });

  rainToggle.addEventListener('change', (e) => {
    isRaining = e.target.checked;
    runSimulationStep();
  });

  tankToggle.addEventListener('change', (e) => {
    hasWaterInTank = e.target.checked;
    runSimulationStep();
  });

  dryrunToggle.addEventListener('change', (e) => {
    isPumpFlowNormal = e.target.checked;
    runSimulationStep();
  });

  moistureSlider.addEventListener('input', (e) => {
    soilResistance = parseFloat(e.target.value);
    runSimulationStep();
  });

  humiditySlider.addEventListener('input', (e) => {
    canopyHumidity = parseFloat(e.target.value);
    runSimulationStep();
  });

  tempSlider.addEventListener('input', (e) => {
    ambientTemp = parseFloat(e.target.value);
    runSimulationStep();
  });

  thresholdSlider.addEventListener('input', (e) => {
    refThresholdSoil = parseFloat(e.target.value);
    runSimulationStep();
  });

  rhThresholdSlider.addEventListener('input', (e) => {
    refThresholdRH = parseFloat(e.target.value);
    runSimulationStep();
  });

  tempThresholdSlider.addEventListener('input', (e) => {
    refThresholdTemp = parseFloat(e.target.value);
    runSimulationStep();
  });

  // --- Multi-Zone Analog Simulation Engine ---
  function runSimulationStep() {
    // 1. Root Zone Soil Moisture Signal Processing (Channel 1)
    const vSensorSoil = vcc * (soilResistance / (rFixed + soilResistance));

    const needleAngleSoil = -60 + ((soilResistance - 1) / 199.0) * 120;
    gaugeNeedle.style.transform = `rotate(${needleAngleSoil}deg)`;
    gaugeResVal.textContent = `${soilResistance} kΩ`;
    gaugeVoltVal.textContent = `${vSensorSoil.toFixed(2)} V`;

    if (soilResistance < 15) {
      moistureText.textContent = `Very Wet Soil (${soilResistance} kΩ)`;
      moistureText.className = 'state-tag wet';
    } else if (soilResistance < 40) {
      moistureText.textContent = `Moist Soil (${soilResistance} kΩ)`;
      moistureText.className = 'state-tag wet';
    } else {
      moistureText.textContent = `Dry Soil (${soilResistance} kΩ)`;
      moistureText.className = 'state-tag dry';
    }

    const vRefSoil = vcc * (refThresholdSoil / (rFixed + refThresholdSoil));
    thresholdText.textContent = `Threshold: ${refThresholdSoil} kΩ (${vRefSoil.toFixed(2)} V)`;

    const rh = 100.0;
    const rPot = 10.0;
    const vUTP_Soil = vRefSoil + (vcc - vRefSoil) * (rPot / (rh + rPot));
    const vLTP_Soil = vRefSoil - vRefSoil * (rPot / (rh + rPot));

    if (vSensorSoil >= vUTP_Soil) {
      schmittSoilState = true;  // Soil is dry -> Irrigation Demand
    } else if (vSensorSoil <= vLTP_Soil) {
      schmittSoilState = false; // Soil is wet -> End Demand
    }

    // 2. Foliage Canopy Relative Humidity Signal Processing (Channel 2)
    const vSensorRH = 0.5 + ((canopyHumidity - 10) / 80.0) * 4.0;

    const needleAngleRH = -60 + ((canopyHumidity - 10) / 80.0) * 120;
    humidityNeedle.style.transform = `rotate(${needleAngleRH}deg)`;
    gaugeRhVal.textContent = `${canopyHumidity} % RH`;
    gaugeRhVolt.textContent = `${vSensorRH.toFixed(2)} V`;

    if (canopyHumidity < 40) {
      humidityText.textContent = `Low Air Humidity (${canopyHumidity}% RH)`;
      humidityText.className = 'state-tag dry';
    } else if (canopyHumidity < 65) {
      humidityText.textContent = `Moderate Humidity (${canopyHumidity}% RH)`;
      humidityText.className = 'state-tag wet';
    } else {
      humidityText.textContent = `Optimal Canopy Mist (${canopyHumidity}% RH)`;
      humidityText.className = 'state-tag mist';
    }

    const vRefRH = 0.5 + ((refThresholdRH - 10) / 80.0) * 4.0;
    rhThresholdText.textContent = `Misting Target: ${refThresholdRH}% RH (${vRefRH.toFixed(2)} V)`;

    const vUTP_RH = vRefRH + 0.3;
    const vLTP_RH = vRefRH - 0.3;

    if (vSensorRH <= vLTP_RH) {
      schmittMistState = true;  // Low humidity -> Atomizer Misting Demand
    } else if (vSensorRH >= vUTP_RH) {
      schmittMistState = false; // High humidity -> Stop Misting
    }

    // 3. Ambient Air Temperature NTC Thermistor Signal Processing (Channel 3)
    // Temp Sensor Voltage: 0°C = 0.0V, 60°C = 6.0V (0.1V per °C)
    const vSensorTemp = (ambientTemp / 60.0) * 6.0;

    const needleAngleTemp = -60 + (ambientTemp / 60.0) * 120;
    tempNeedle.style.transform = `rotate(${needleAngleTemp}deg)`;
    gaugeTempVal.textContent = `${ambientTemp} °C`;
    gaugeTempVolt.textContent = `${vSensorTemp.toFixed(2)} V`;

    if (ambientTemp > 35) {
      tempText.textContent = `High Heat (${ambientTemp} °C)`;
      tempText.className = 'state-tag temp-hot';
    } else if (ambientTemp > 28) {
      tempText.textContent = `Warm Temp (${ambientTemp} °C)`;
      tempText.className = 'state-tag wet';
    } else {
      tempText.textContent = `Cool Temp (${ambientTemp} °C)`;
      tempText.className = 'state-tag wet';
    }

    const vRefTemp = (refThresholdTemp / 60.0) * 6.0;
    tempThresholdText.textContent = `Fan Target: ${refThresholdTemp} °C (${vRefTemp.toFixed(2)} V)`;

    if (vSensorTemp >= vRefTemp + 0.2) {
      schmittTempState = true;  // High temperature -> Trigger Cooling Fan & Misting
    } else if (vSensorTemp <= vRefTemp - 0.2) {
      schmittTempState = false; // Temp normalized -> Turn OFF Fan
    }

    // 4. Safety Interlocks & Tank Protection
    const hasFault = (!hasWaterInTank) || (!isPumpFlowNormal);

    // 5. Dual Actuator & Fan State Machine Logic
    let isPumpActive = false;
    let isFanActive = false;
    let isMistActive = false;

    if (opMode === 'OFF') {
      isPumpActive = false;
      isFanActive = false;
      isMistActive = false;
      timerActiveSoil = false;
      timerActiveMist = false;
    } else if (opMode === 'MANUAL') {
      isPumpActive = !hasFault && !isRaining;
      isFanActive = !hasFault;
      isMistActive = !hasFault && !isRaining;
    } else {
      // AUTO Mode
      // Soil Pump Triggering
      if (schmittSoilState && !hasFault && !isRaining) {
        if (!timerActiveSoil) {
          timerActiveSoil = true;
          timerTimeRemainingSoil = 30; // 30s watering pulse
        }
      }

      // Fan Triggering: High Temp turns ON Cooling Fan
      isFanActive = schmittTempState && !hasFault;

      // Mist Creator Triggering: Low Humidity OR High Temp triggers Piezo Mist Atomizer
      const mistRequired = schmittMistState || schmittTempState;
      if (mistRequired && !hasFault && !isRaining) {
        if (!timerActiveMist) {
          timerActiveMist = true;
          timerTimeRemainingMist = 15; // 15s misting pulse
        }
      }

      isPumpActive = timerActiveSoil && !hasFault && !isRaining;
      isMistActive = (timerActiveMist || schmittTempState) && !hasFault && !isRaining;
    }

    if (timerActiveSoil || timerActiveMist) {
      timerCapVoltage = Math.min(8.0, timerCapVoltage + 0.5);
    } else {
      timerCapVoltage = Math.max(0.0, timerCapVoltage - 0.8);
    }

    // Output Drive Voltages
    const vMosfetGate = isPumpActive ? 12.0 : 0.0;
    const vFanDrive = isFanActive ? 12.0 : 0.0;
    const vPiezoMist = isMistActive ? 12.0 : 0.0;

    // LED Diagnostics Update
    ledPower.className = 'led led-power on';
    ledDry.className = schmittSoilState ? 'led led-dry on' : 'led led-dry';
    ledPump.className = isPumpActive ? 'led led-pump on' : 'led led-pump';
    ledFan.className = isFanActive ? 'led led-fan on' : 'led led-fan';
    ledMist.className = isMistActive ? 'led led-mist on' : 'led led-mist';
    ledFault.className = hasFault ? 'led led-fault on' : 'led led-fault';

    if (timerActiveSoil || timerActiveMist) {
      const activeTimer = Math.max(timerTimeRemainingSoil, timerTimeRemainingMist);
      timerStateBadge.textContent = 'RUNNING';
      timerStateBadge.className = 'badge timer-badge';
      timerCountdown.textContent = `${activeTimer}s`;
    } else {
      timerStateBadge.textContent = 'IDLE';
      timerStateBadge.className = 'badge';
      timerCountdown.textContent = '--';
    }

    // Push into Waveform History Buffer
    waveHistory.sensor.shift();
    waveHistory.sensor.push(vSensorSoil);

    waveHistory.comp.shift();
    waveHistory.comp.push(schmittSoilState ? 12 : 0);

    waveHistory.timerCap.shift();
    waveHistory.timerCap.push(timerCapVoltage);

    waveHistory.mosfet.shift();
    waveHistory.mosfet.push(vMosfetGate);

    waveHistory.fanDrive.shift();
    waveHistory.fanDrive.push(vFanDrive);

    waveHistory.mistPiezo.shift();
    waveHistory.mistPiezo.push(vPiezoMist);

    drawOscilloscope();
  }

  // Interval timer ticks
  setInterval(() => {
    if (opMode === 'AUTO') {
      if (timerActiveSoil) {
        if (timerTimeRemainingSoil > 0) timerTimeRemainingSoil--;
        else timerActiveSoil = false;
      }
      if (timerActiveMist) {
        if (timerTimeRemainingMist > 0) timerTimeRemainingMist--;
        else timerActiveMist = false;
      }
      runSimulationStep();
    }
  }, 1000);

  // Oscilloscope Canvas Renderer
  function drawOscilloscope() {
    const w = waveCanvas.width;
    const h = waveCanvas.height;
    waveCtx.clearRect(0, 0, w, h);

    // Grid lines
    waveCtx.strokeStyle = 'rgba(16, 185, 129, 0.08)';
    waveCtx.lineWidth = 1;
    for (let x = 0; x < w; x += 30) {
      waveCtx.beginPath();
      waveCtx.moveTo(x, 0);
      waveCtx.lineTo(x, h);
      waveCtx.stroke();
    }
    for (let y = 0; y < h; y += 30) {
      waveCtx.beginPath();
      waveCtx.moveTo(0, y);
      waveCtx.lineTo(w, y);
      waveCtx.stroke();
    }

    const scaleY = (v) => h - (v / 12.0) * (h - 20) - 10;
    const stepX = w / (waveHistory.sensor.length - 1);

    // 1. Soil Sensor (Emerald Green)
    waveCtx.strokeStyle = '#34d399';
    waveCtx.lineWidth = 2.5;
    waveCtx.beginPath();
    for (let i = 0; i < waveHistory.sensor.length; i++) {
      const x = i * stepX;
      const y = scaleY(waveHistory.sensor[i]);
      if (i === 0) waveCtx.moveTo(x, y);
      else waveCtx.lineTo(x, y);
    }
    waveCtx.stroke();

    // 2. LM393 Comparator Ch1 (Gold)
    waveCtx.strokeStyle = '#fbbf24';
    waveCtx.lineWidth = 2;
    waveCtx.beginPath();
    for (let i = 0; i < waveHistory.comp.length; i++) {
      const x = i * stepX;
      const y = scaleY(waveHistory.comp[i]);
      if (i === 0) waveCtx.moveTo(x, y);
      else waveCtx.lineTo(x, y);
    }
    waveCtx.stroke();

    // 3. 556 Timer Cap (Terracotta / Copper)
    waveCtx.strokeStyle = '#ea580c';
    waveCtx.lineWidth = 2;
    waveCtx.beginPath();
    for (let i = 0; i < waveHistory.timerCap.length; i++) {
      const x = i * stepX;
      const y = scaleY(waveHistory.timerCap[i]);
      if (i === 0) waveCtx.moveTo(x, y);
      else waveCtx.lineTo(x, y);
    }
    waveCtx.stroke();

    // 4. MOSFET Pump Gate (Blue)
    waveCtx.strokeStyle = '#3b82f6';
    waveCtx.lineWidth = 2;
    waveCtx.beginPath();
    for (let i = 0; i < waveHistory.mosfet.length; i++) {
      const x = i * stepX;
      const y = scaleY(waveHistory.mosfet[i]);
      if (i === 0) waveCtx.moveTo(x, y);
      else waveCtx.lineTo(x, y);
    }
    waveCtx.stroke();

    // 5. Cooling Fan Drive (Cyan)
    waveCtx.strokeStyle = '#06b6d4';
    waveCtx.lineWidth = 2;
    waveCtx.beginPath();
    for (let i = 0; i < waveHistory.fanDrive.length; i++) {
      const x = i * stepX;
      const y = scaleY(waveHistory.fanDrive[i]);
      if (i === 0) waveCtx.moveTo(x, y);
      else waveCtx.lineTo(x, y);
    }
    waveCtx.stroke();

    // 6. Ultrasonic Piezo Mist Driver (Purple)
    waveCtx.strokeStyle = '#a855f7';
    waveCtx.lineWidth = 2;
    waveCtx.beginPath();
    for (let i = 0; i < waveHistory.mistPiezo.length; i++) {
      const x = i * stepX;
      const y = scaleY(waveHistory.mistPiezo[i]);
      if (i === 0) waveCtx.moveTo(x, y);
      else waveCtx.lineTo(x, y);
    }
    waveCtx.stroke();
  }

  runSimulationStep();
});
