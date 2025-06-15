console.log("Script geladen!");

let isConnected = false;
let lastUpdateTime = null;
let currentSensorData = {
  weight: 0,
  temperatuur: 20.0,
  humidity: 50.0,
  distance: 0.0
};
let currentStatsData = {
  totaal_volume_liters: 0.0,
  aantal_keren_gebruikt: 0,
  dagen_achter_elkaar: 0
};

const btn = document.getElementById('statusButton');
if (btn) {
  btn.addEventListener('click', () => {
    showPasswordPopup();
  });
}

document.addEventListener('DOMContentLoaded', function () {
  console.log("DOM geladen!");

  initializeMenu();
  

  console.log("Checking dashboard elementen...");
  checkDashboardElements();


  updateDashboardFromSQL({
    totaal_volume_liters: 0.0,
    aantal_keren_gebruikt: 0,
    dagen_achter_elkaar: 0,
    aantal_cola: 0,
    aantal_water: 0,
    totaal_cola_ml: 0.0,
    totaal_water_ml: 0.0,
    gemiddelde_temperatuur: 20.0,
    gemiddelde_vochtigheid: 50.0
  });
});

function initializeMenu() {
  const burgerToggle = document.getElementById('burger-toggle');
  const sideMenu = document.getElementById('side-menu');
  const closeMenu = document.getElementById('close-menu');
  const overlay = document.getElementById('menu-overlay');

  if (burgerToggle && sideMenu && closeMenu && overlay) {
    burgerToggle.addEventListener('click', () => {
      sideMenu.classList.add('open');
      overlay.classList.add('show');
    });

    closeMenu.addEventListener('click', () => {
      sideMenu.classList.remove('open');
      overlay.classList.remove('show');
    });

    overlay.addEventListener('click', () => {
      sideMenu.classList.remove('open');
      overlay.classList.remove('show');
    });
  }
}

// Dashboard elementen controleren
function checkDashboardElements() {
  const elements = {
    totaalVolume: document.querySelector('.bottom-text-totaal'),
    gewichtGlas: document.querySelector('.bottom-text-gewicht-glas'),
    aantalKeer: document.querySelector('.bottom-text-aantal-keer-gebruikt'),
    temperatuur: document.querySelector('.bottom-text-favoriet-drank'),
    vochtigheid: document.querySelector('.bottom-text-goal'),
    streak: document.querySelector('.bottom-text-streak')
  };

  console.log("Dashboard elementen check:", elements);
  return elements;
}

// Connection status updaten
function updateConnectionStatus(connected) {
  isConnected = connected;
  const statusElement = document.querySelector('#statusButton');
  
  if (statusElement) {
    if (connected) {
      statusElement.classList.remove('off');
      statusElement.classList.add('on');
      statusElement.title = 'Verbonden met server';
    } else {
      statusElement.classList.remove('on');
      statusElement.classList.add('off');
      statusElement.title = 'Niet verbonden met server';
    }
  }
  
  console.log("Connection status updated:", connected ? "Connected" : "Disconnected");
}

// Dashboard updaten vanuit SQL data
function updateDashboardFromSQL(sqlStats) {
  console.log("updateDashboardFromSQL aangeroepen met:", sqlStats);
  
  // Update connection status
  updateConnectionStatus(true);
  lastUpdateTime = new Date();

  //  TOTAAL VOLUME 
  const totaalVolumeElement = document.querySelector('.bottom-text-totaal');
  if (totaalVolumeElement && sqlStats.totaal_volume_liters !== undefined) {
    const volumeInLiters = parseFloat(sqlStats.totaal_volume_liters).toFixed(1);
    console.log(`SQL Volume update: ${volumeInLiters}l`);
    totaalVolumeElement.textContent = `${volumeInLiters}l`;
    animateElement(totaalVolumeElement, '#4CAF50');
    
    // Update cache
    currentStatsData.totaal_volume_liters = parseFloat(sqlStats.totaal_volume_liters);
  }

  const aantalKeerElement = document.querySelector('.bottom-text-aantal-keer-gebruikt');
  if (aantalKeerElement && sqlStats.aantal_keren_gebruikt !== undefined) {
    const totalUses = parseInt(sqlStats.aantal_keren_gebruikt);
    console.log(`SQL Aantal keer gebruikt: ${totalUses}`);
    aantalKeerElement.textContent = `${totalUses} keer`;
    animateElement(aantalKeerElement, '#2196F3');
    
    currentStatsData.aantal_keren_gebruikt = totalUses;
  }

  // STREAK/DAGEN 
  const streakElement = document.querySelector('.bottom-text-streak');
  if (streakElement && sqlStats.dagen_achter_elkaar !== undefined) {
    const streak = parseInt(sqlStats.dagen_achter_elkaar);
    console.log(`SQL Streak: ${streak} dagen`);
    streakElement.textContent = `${streak} dagen`;
    animateElement(streakElement, '#FF9800');
    
    // Update cache
    currentStatsData.dagen_achter_elkaar = streak;
  }

  //  WEIGHT SENSOR
  const gewichtGlasElement = document.querySelector('.bottom-text-gewicht-glas');
  if (gewichtGlasElement) {
    const weight = Math.round(parseFloat(currentSensorData.weight) || 0);
    gewichtGlasElement.textContent = `${weight}g`;
  }

  //  TEMPERATUUR SENSOR
  const temperatuurElement = document.querySelector('.bottom-text-favoriet-drank');
  if (temperatuurElement) {
    const temperatuur = Math.round(parseFloat(currentSensorData.temperatuur) || 20);
    temperatuurElement.textContent = `${temperatuur}°C`;
  }

  //  VOCHTIGHEID SENSOR
  const vochtigheidElement = document.querySelector('.bottom-text-goal');
  if (vochtigheidElement) {
    const humidity = Math.round(parseFloat(currentSensorData.humidity) || 50);
    vochtigheidElement.textContent = `${humidity}%`;
  }
}

// Sensor data updaten
function updateSensorData(sensorData) {
  console.log("updateSensorData aangeroepen met:", sensorData);
  
  // Update sensor cache
  if (sensorData.weight !== undefined) currentSensorData.weight = sensorData.weight;
  if (sensorData.temperatuur !== undefined) currentSensorData.temperatuur = sensorData.temperatuur;
  if (sensorData.temperature !== undefined) currentSensorData.temperatuur = sensorData.temperature;
  if (sensorData.humidity !== undefined) currentSensorData.humidity = sensorData.humidity;
  if (sensorData.distance !== undefined) currentSensorData.distance = sensorData.distance;

  
  // WEIGHT
  const gewichtGlasElement = document.querySelector('.bottom-text-gewicht-glas');
  if (gewichtGlasElement && sensorData.weight !== undefined) {
    const weight = Math.round(parseFloat(sensorData.weight) || 0);
    console.log("Updating weight:", weight + "g");
    gewichtGlasElement.textContent = `${weight}g`;
  }

  // TEMPERATUUR
  const temperatuurElement = document.querySelector('.bottom-text-favoriet-drank');
  if (temperatuurElement && (sensorData.temperatuur !== undefined || sensorData.temperature !== undefined)) {
    const temperatuur = Math.round(parseFloat(sensorData.temperatuur || sensorData.temperature) || 20);
    console.log("Updating temperatuur:", temperatuur + "°C");
    temperatuurElement.textContent = `${temperatuur}°C`;
  }

  // VOCHTIGHEID
  const vochtigheidElement = document.querySelector('.bottom-text-goal');
  if (vochtigheidElement && sensorData.humidity !== undefined) {
    const humidity = Math.round(parseFloat(sensorData.humidity) || 50);
    console.log("Updating vochtigheid:", humidity + "%");
    vochtigheidElement.textContent = `${humidity}%`;
  }
}

// Element animatie
function animateElement(element, color) {
  if (element) {
    element.style.transition = 'color 0.3s ease';
    element.style.color = color;
    setTimeout(() => {
      element.style.color = '';
    }, 1000);
  }
}

// Notificatie weergeven
function showNotification(message) {
  const notification = document.createElement('div');
  notification.className = 'notification';
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background-color: #4CAF50;
    color: white;
    padding: 15px;
    border-radius: 5px;
    z-index: 1000;
    transition: opacity 0.5s ease;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  `;

  document.body.appendChild(notification);
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => {
      if (notification.parentNode) {
        document.body.removeChild(notification);
      }
    }, 500);
  }, 3000);
}

// Session code ophalen
async function getSessionCode() {
  try {
    const response = await fetch('/api/device/1/status');
    const data = await response.json();
    return data.session_code;
  } catch (error) {
    console.error('Error getting session code:', error);
    return null;
  }
}

// Device toggle functie
async function toggleDevice() {
  const sessionCode = await getSessionCode();
  
  if (!sessionCode) {
    alert('Could not get security code');
    return;
  }
  
  try {
    const response = await fetch('/api/device/1/toggle', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code: sessionCode
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      //Voor button te veranderen
      const button = document.getElementById('toggleButton');
      if (button) {
        button.textContent = data.status ? 'Device ON' : 'Device OFF';
        button.className = data.status ? 'btn-success' : 'btn-danger';
      }
      
      console.log(' Device toggled:', data.message);
    } else {
      alert('Error: ' + data.error);
    }
    
  } catch (error) {
    console.error(' Toggle error:', error);
    alert('Network error occurred');
  }
}

// Socket.IO integratie
if (typeof io !== 'undefined') {
  console.log("Socket.IO beschikbaar, probeer verbinding te maken...");
  const socket = io('http://192.168.168.169:5501');

  socket.on('connect', function() {
    console.log('Verbonden met server via Socket.IO');
    updateConnectionStatus(true);
    
    socket.emit('F2B_request_sensor_data');
    socket.emit('F2B_request_stats');
  });

  socket.on('disconnect', function() {
    console.log('Socket.IO verbinding verbroken');
    updateConnectionStatus(false);
  });

  // SENSOR DATA (weight, temperatuur, vochtigheid)
  socket.on('B2F_sensor_data', function(data) {
    console.log('Sensor data ontvangen via Socket.IO:', data);
    const sensors = data.sensors || data;
    updateSensorData(sensors);
  });

  // STATISTIEKEN DATA (totaal volume, aantal keer gebruikt, streek)
  socket.on('B2F_stats_data', function(data) {
    console.log('Statistieken ontvangen via Socket.IO:', data);
    
    let stats = null;
    if (data.stats) {
      stats = data.stats;
    } else if (data.totaal_volume_liters !== undefined) {
      stats = data;
    }
    
    if (stats) {
      // Convert van app.py format naar verwachte format
      const sqlStats = {
        totaal_volume_liters: stats.totaal_volume_liters || 0.0,
        aantal_keren_gebruikt: stats.aantal_keren_gebruikt || 0,
        dagen_achter_elkaar: stats.dagen_achter_elkaar || 0,
        aantal_cola: stats.Aantal_Cola || 0,
        aantal_water: stats.Aantal_Water || 0,
        totaal_cola_ml: stats.Volume_Cola || 0.0,
        totaal_water_ml: stats.Volume_Water || 0.0,
        gemiddelde_temperatuur: stats.Temperatuur || 20.0,
        gemiddelde_vochtigheid: stats.Vochtigheid || 50.0
      };
      
      updateDashboardFromSQL(sqlStats);
    }
  });

  // DRANK GEREGISTREERD
  socket.on('B2F_drank_geregistreerd', function(data) {
    console.log(`${data.type} geregistreerd: ${data.volume}ml`);
    showNotification(`${data.type.charAt(0).toUpperCase() + data.type.slice(1)} geregistreerd: ${data.volume}ml`);
    
    setTimeout(() => {
      socket.emit('F2B_request_stats');
    }, 1000);
  });

  // updates
  setInterval(() => {
    if (socket.connected) {
      socket.emit('F2B_request_sensor_data');
    }
  }, 5000); // Elke 5 seconden sensor data

  setInterval(() => {
    if (socket.connected) {
      socket.emit('F2B_request_stats');
    }
  }, 30000); // Elke 30 seconden stats

  // Connection timeout checker
  setInterval(() => {
    if (lastUpdateTime && (new Date() - lastUpdateTime) > 60000) {
      console.log("Geen updates ontvangen in 30 seconden");
      updateConnectionStatus(false);
    }
  }, 5000);

} else {
  console.log("Socket.IO niet beschikbaar");
  updateConnectionStatus(false);
}

// Debug functie
function testSQLUpdate() {
  console.log("Test SQL update aangeroepen!");
  updateDashboardFromSQL({
    totaal_volume_liters: 2.5,
    aantal_keren_gebruikt: 13,
    dagen_achter_elkaar: 5,
    aantal_cola: 5,
    aantal_water: 8,
    totaal_cola_ml: 1250,
    totaal_water_ml: 1250,
    gemiddelde_temperatuur: 24.0,
    gemiddelde_vochtigheid: 60.0
  });
}

function testSensorUpdate() {
  console.log("Test sensor update aangeroepen!");
  updateSensorData({
    weight: 180,
    temperatuur: 26.5,
    humidity: 65,
    distance: 8.2
  });
}

// Password popup functions (Onder constructie)
function showPasswordPopup() {
  const popup = document.getElementById('passwordPopup');
  if (popup) {
    popup.style.display = 'flex';
    const input = document.getElementById('passwordInput');
    if (input) {
      input.focus();
      input.value = '';
    }
  }
}

function hidePasswordPopup() {
  const popup = document.getElementById('passwordPopup');
  if (popup) {
    popup.style.display = 'none';
  }
}

function confirmToggle() {
  const passwordInput = document.getElementById('passwordInput');
  const password = passwordInput ? passwordInput.value : '';
  
  if (password.trim() === '') {
    alert('Voer een geldige beveiligingscode in');
    return;
  }
  
  console.log(' Attempting toggle with password');
  hidePasswordPopup();
  
  //  function
  toggleDeviceWithPassword(password);
}

// API Functions
async function toggleDeviceWithPassword(code) {
  try {
    console.log(` Toggling device ${DEVICE_ID} with code: ${code}`);
    
    const response = await fetch(`${API_BASE}/device/${DEVICE_ID}/toggle`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code: code
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log(' Device toggle successful:', data);
      alert(`Device ${data.status ? 'ingeschakeld' : 'uitgeschakeld'}!`);
      
      // Update UI
      updateDeviceUI(data.status);
    } else {
      console.error(' Device toggle failed:', data.error);
      
      // Handle specific error cases
      if (response.status === 401) {
        alert(' Onjuiste beveiligingscode!');
      } else if (response.status === 429) {
        alert(' Te veel verzoeken. Wacht 5 seconden.');
      } else {
        alert(` Fout: ${data.error}`);
      }
    }
    
    // Refresh status regardless of success/failure
    await refreshDeviceStatus();
    
  } catch (error) {
    console.error(' Network error:', error);
    alert(' Netwerkfout. Controleer of de server draait.');
  }
}

async function refreshDeviceStatus() {
  try {
    console.log(` Refreshing device ${DEVICE_ID} status...`);
    
    const response = await fetch(`${API_BASE}/device/${DEVICE_ID}/status`, {
      method: 'GET'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    if (data.success) {
      console.log(' Status refresh successful:', data);
      updateDeviceUI(data.status);
      
      // Store session code if provided
      if (data.session_code) {
        console.log(' Session code updated:', data.session_code);
      }
    } else {
      console.error(' Status refresh failed:', data.error);
    }
    
  } catch (error) {
    console.error(' Status refresh error:', error);
    
    // Update offline status
    updateDeviceUI(null, true);
  }
}

function updateDeviceUI(status, isOffline = false) {
  // Update button
  const deviceButton = document.getElementById('deviceButton');
  const statusIndicator = document.getElementById('statusIndicator');
  const statusText = document.getElementById('statusText');
  
  if (isOffline) {
    // Server offline
    if (deviceButton) {
      deviceButton.className = 'device-offline';
      deviceButton.disabled = true;
    }
    if (statusIndicator) {
      statusIndicator.className = 'status-offline';
    }
    if (statusText) {
      statusText.textContent = 'OFFLINE';
    }
  } else {
    // Server online
    if (deviceButton) {
      deviceButton.className = status ? 'device-on' : 'device-off';
      deviceButton.disabled = false;
    }
    if (statusIndicator) {
      statusIndicator.className = status ? 'status-on' : 'status-off';
    }
    if (statusText) {
      statusText.textContent = status ? 'AAN' : 'UIT';
    }
  }
  
  console.log(` Page updated - Status: ${status}, Offline: ${isOffline}`);
}

// Test API connection
async function testApiConnection() {
  try {
    console.log(' Testing API connection...');
    
    const response = await fetch(`${API_BASE}/test`);
    const data = await response.json();
    
    if (data.success) {
      console.log(' API connection successful:', data);
      return true;
    } else {
      console.error(' API test failed:', data);
      return false;
    }
  } catch (error) {
    console.error(' API connection error:', error);
    return false;
  }
}

// Event listeners
document.addEventListener('DOMContentLoaded', async function() {
  console.log(' Initializing device controller...');
  
  // Setup password input
  const passwordInput = document.getElementById('passwordInput');
  if (passwordInput) {
    passwordInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        confirmToggle();
      }
    });
  }
  
  // Test API connection 
  const apiWorking = await testApiConnection();
  
  if (apiWorking) {
    await refreshDeviceStatus();
    
    //refresh 30 seconds
    setInterval(refreshDeviceStatus, 30000);
  } else {
    console.error(' Cannot connect to API server');
    updateDeviceUI(null, true);
  }
});

// Export functions for global use
window.toggleDevice = showPasswordPopup;
window.showPasswordPopup = showPasswordPopup;
window.hidePasswordPopup = hidePasswordPopup;
window.confirmToggle = confirmToggle;
window.toggleDeviceWithPassword = toggleDeviceWithPassword;
window.refreshDeviceStatus = refreshDeviceStatus;
window.testApiConnection = testAp