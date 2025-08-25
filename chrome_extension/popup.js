// PlayOK KingsRow Bot - Popup Script
class PopupController {
  constructor() {
    this.statusElements = {
      botStatus: document.getElementById('botStatus'),
      engineStatus: document.getElementById('engineStatus'),
      gameStatus: document.getElementById('gameStatus'),
      turnStatus: document.getElementById('turnStatus'),
      engineStatusText: document.getElementById('engineStatusText'),
      gameStatusText: document.getElementById('gameStatusText'),
      turnStatusText: document.getElementById('turnStatusText'),
      movesPlayed: document.getElementById('movesPlayed'),
      engineThinking: document.getElementById('engineThinking'),
      moveHistory: document.getElementById('moveHistory')
    };

    this.controlElements = {
      botToggle: document.getElementById('botToggle'),
      resetGameBtn: document.getElementById('resetGameBtn'),
      manualMoveBtn: document.getElementById('manualMoveBtn'),
      settingsBtn: document.getElementById('settingsBtn'),
      emergencyStopBtn: document.getElementById('emergencyStopBtn'),
      settingsPanel: document.getElementById('settingsPanel'),
      autoPlayDelay: document.getElementById('autoPlayDelay'),
      detectionInterval: document.getElementById('detectionInterval')
    };

    this.messageElements = {
      errorMessage: document.getElementById('errorMessage'),
      successMessage: document.getElementById('successMessage')
    };

    this.init();
  }

  init() {
    console.log('🎮 Popup controller initialized');
    
    // Load initial settings and status
    this.loadSettings();
    this.updateStatus();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Start status updates
    this.startStatusUpdates();
  }

  setupEventListeners() {
    // Bot toggle
    this.controlElements.botToggle.addEventListener('change', (e) => {
      this.toggleBot(e.target.checked);
    });

    // Reset game button
    this.controlElements.resetGameBtn.addEventListener('click', () => {
      this.resetGame();
    });

    // Manual move button
    this.controlElements.manualMoveBtn.addEventListener('click', () => {
      this.requestManualMove();
    });

    // Settings button
    this.controlElements.settingsBtn.addEventListener('click', () => {
      this.toggleSettingsPanel();
    });

    // Emergency stop button
    this.controlElements.emergencyStopBtn.addEventListener('click', () => {
      this.emergencyStop();
    });

    // Settings inputs
    this.controlElements.autoPlayDelay.addEventListener('change', (e) => {
      this.saveSetting('autoPlayDelay', parseInt(e.target.value));
    });

    this.controlElements.detectionInterval.addEventListener('change', (e) => {
      this.saveSetting('detectionInterval', parseInt(e.target.value));
      this.notifyContentScriptSettingsChange();
    });
  }

  loadSettings() {
    chrome.storage.sync.get([
      'botEnabled', 
      'autoPlayDelay', 
      'detectionInterval',
      'enginePath'
    ], (data) => {
      // Set toggle state
      this.controlElements.botToggle.checked = data.botEnabled !== false;
      
      // Set input values
      this.controlElements.autoPlayDelay.value = data.autoPlayDelay || 1000;
      this.controlElements.detectionInterval.value = data.detectionInterval || 500;
      
      console.log('⚙️ Settings loaded:', data);
    });
  }

  saveSetting(key, value) {
    chrome.storage.sync.set({ [key]: value }, () => {
      console.log(`💾 Setting saved: ${key} = ${value}`);
      this.showSuccessMessage(`Setting saved: ${key}`);
    });
  }

  toggleBot(enabled) {
    chrome.storage.sync.set({ botEnabled: enabled }, () => {
      console.log(`🤖 Bot ${enabled ? 'enabled' : 'disabled'}`);
      
      // Notify content script
      this.sendMessageToContentScript({
        type: 'TOGGLE_BOT',
        enabled: enabled
      });
      
      this.showSuccessMessage(`Bot ${enabled ? 'enabled' : 'disabled'}`);
      this.updateStatus();
    });
  }

  resetGame() {
    console.log('🔄 Resetting game...');
    
    // Reset background script state
    chrome.runtime.sendMessage({ type: 'RESET_GAME' }, (response) => {
      if (response && response.success) {
        this.showSuccessMessage('Game reset successfully');
      } else {
        this.showErrorMessage('Failed to reset game');
      }
    });
    
    // Clear move history display
    this.statusElements.moveHistory.textContent = 'Game reset - no moves yet...';
    this.statusElements.movesPlayed.textContent = '0';
  }

  requestManualMove() {
    console.log('🎯 Requesting manual move...');
    
    chrome.runtime.sendMessage({ 
      type: 'MANUAL_MOVE',
      position: 'current'
    }, (response) => {
      if (response && response.success) {
        this.showSuccessMessage('Move request sent to engine');
      } else {
        this.showErrorMessage('Failed to request move: ' + (response?.error || 'Unknown error'));
      }
    });
  }

  toggleSettingsPanel() {
    const panel = this.controlElements.settingsPanel;
    const isVisible = panel.style.display !== 'none';
    panel.style.display = isVisible ? 'none' : 'block';
    
    this.controlElements.settingsBtn.textContent = isVisible ? '⚙️ Settings' : '⚙️ Hide Settings';
  }

  emergencyStop() {
    console.log('🛑 Emergency stop activated');
    
    // Disable bot
    this.controlElements.botToggle.checked = false;
    this.toggleBot(false);
    
    // Send stop message to content script
    this.sendMessageToContentScript({
      type: 'EMERGENCY_STOP'
    });
    
    this.showSuccessMessage('Emergency stop activated - bot disabled');
  }

  updateStatus() {
    // Update bot status
    chrome.storage.sync.get(['botEnabled'], (data) => {
      const enabled = data.botEnabled !== false;
      this.setStatusIndicator('botStatus', enabled ? 'green' : 'red');
    });

    // Update engine status
    chrome.runtime.sendMessage({ type: 'GET_ENGINE_STATUS' }, (response) => {
      if (chrome.runtime.lastError) {
        this.setStatusIndicator('engineStatus', 'red');
        this.statusElements.engineStatusText.textContent = 'Connection Error';
        return;
      }

      if (response) {
        const connected = response.connected;
        const thinking = response.thinking;
        
        this.setStatusIndicator('engineStatus', connected ? 'green' : 'red');
        this.statusElements.engineStatusText.textContent = connected ? 
          (thinking ? 'Thinking...' : 'Ready') : 'Disconnected';
        
        this.statusElements.engineThinking.textContent = thinking ? 'Yes' : 'No';
        this.statusElements.movesPlayed.textContent = (response.gameHistory || []).length;
        
        // Update move history
        if (response.gameHistory && response.gameHistory.length > 0) {
          const recentMoves = response.gameHistory.slice(-10);
          this.statusElements.moveHistory.innerHTML = recentMoves
            .map((move, index) => `${index + 1}. ${move}`)
            .join('<br>');
        }
      }
    });

    // Update game status from content script
    this.sendMessageToContentScript({ type: 'GET_STATUS' }, (response) => {
      if (response) {
        this.setStatusIndicator('gameStatus', response.gameStarted ? 'green' : 'red');
        this.statusElements.gameStatusText.textContent = response.gameStarted ? 'Game Active' : 'No Game';
        
        this.setStatusIndicator('turnStatus', 
          response.isMyTurn === null ? 'yellow' : (response.isMyTurn ? 'green' : 'red'));
        this.statusElements.turnStatusText.textContent = 
          response.isMyTurn === null ? 'Unknown' : (response.isMyTurn ? 'My Turn' : 'Opponent Turn');
      }
    });
  }

  setStatusIndicator(elementId, status) {
    const element = this.statusElements[elementId];
    if (element) {
      element.className = `status-indicator ${status}`;
    }
  }

  sendMessageToContentScript(message, callback = null) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, message, callback);
      }
    });
  }

  notifyContentScriptSettingsChange() {
    this.sendMessageToContentScript({
      type: 'SETTINGS_CHANGED'
    });
  }

  showSuccessMessage(message) {
    this.messageElements.successMessage.textContent = message;
    this.messageElements.successMessage.style.display = 'block';
    this.messageElements.errorMessage.style.display = 'none';
    
    setTimeout(() => {
      this.messageElements.successMessage.style.display = 'none';
    }, 3000);
  }

  showErrorMessage(message) {
    this.messageElements.errorMessage.textContent = message;
    this.messageElements.errorMessage.style.display = 'block';
    this.messageElements.successMessage.style.display = 'none';
    
    setTimeout(() => {
      this.messageElements.errorMessage.style.display = 'none';
    }, 5000);
  }

  startStatusUpdates() {
    // Update status every 2 seconds
    setInterval(() => {
      this.updateStatus();
    }, 2000);
    
    // Initial update after small delay
    setTimeout(() => {
      this.updateStatus();
    }, 500);
  }
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new PopupController();
});
