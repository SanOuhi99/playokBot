// PlayOK KingsRow Bot - Background Script
class KingsRowConnector {
  constructor() {
    this.port = null;
    this.isConnected = false;
    this.pendingMoves = [];
    this.gameState = {
      history: [],
      currentPosition: null,
      engineThinking: false
    };

    this.init();
  }

  init() {
    console.log('🚀 KingsRow connector initialized');
    
    // Listen for messages from content script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Keep response channel open for async responses
    });

    // Listen for extension install/startup
    chrome.runtime.onStartup.addListener(() => {
      this.connectToKingsRow();
    });

    chrome.runtime.onInstalled.addListener(() => {
      this.connectToKingsRow();
      this.initializeSettings();
    });

    // Connect to KingsRow on startup
    this.connectToKingsRow();
  }

  initializeSettings() {
    // Set default settings
    chrome.storage.sync.get(['botEnabled', 'enginePath', 'autoPlayDelay'], (data) => {
      if (data.botEnabled === undefined) {
        chrome.storage.sync.set({ botEnabled: true });
      }
      if (!data.enginePath) {
        chrome.storage.sync.set({ 
          enginePath: 'C:\\Program Files\\KingsRow\\KingsRow.exe' 
        });
      }
      if (!data.autoPlayDelay) {
        chrome.storage.sync.set({ autoPlayDelay: 1000 });
      }
    });
  }

  connectToKingsRow() {
    if (this.isConnected) {
      console.log('🔌 Already connected to KingsRow');
      return;
    }

    try {
      console.log('🔌 Connecting to KingsRow engine...');
      
      this.port = chrome.runtime.connectNative('com.playok.kingsrow');
      
      this.port.onMessage.addListener((response) => {
        this.handleKingsRowResponse(response);
      });
      
      this.port.onDisconnect.addListener(() => {
        console.log('🔌 KingsRow connection lost');
        this.isConnected = false;
        this.port = null;
        
        if (chrome.runtime.lastError) {
          console.error('Connection error:', chrome.runtime.lastError);
        }
        
        // Retry connection after delay
        setTimeout(() => {
          this.connectToKingsRow();
        }, 5000);
      });
      
      this.isConnected = true;
      console.log('✅ Connected to KingsRow engine');
      
      // Send initialization message
      this.sendToKingsRow({
        command: 'initialize',
        version: '2.0'
      });
      
    } catch (error) {
      console.error('❌ Failed to connect to KingsRow:', error);
      this.isConnected = false;
      
      // Show user notification
      this.showNotification(
        'KingsRow Connection Failed', 
        'Please ensure KingsRow connector is properly installed.'
      );
    }
  }

  sendToKingsRow(message) {
    if (!this.isConnected || !this.port) {
      console.error('❌ Cannot send to KingsRow - not connected');
      return false;
    }

    try {
      console.log('📤 Sending to KingsRow:', message);
      this.port.postMessage(message);
      return true;
    } catch (error) {
      console.error('❌ Error sending to KingsRow:', error);
      this.isConnected = false;
      return false;
    }
  }

  handleKingsRowResponse(response) {
    console.log('📥 Response from KingsRow:', response);

    switch (response.type) {
      case 'best_move':
        this.handleBestMove(response);
        break;
        
      case 'error':
        console.error('❌ KingsRow error:', response.message);
        this.handleKingsRowError(response);
        break;
        
      case 'status':
        console.log('📊 KingsRow status:', response.status);
        break;
        
      case 'analysis':
        console.log('🧠 Move analysis:', response.analysis);
        break;
        
      default:
        console.log('❓ Unknown KingsRow response type:', response.type);
    }
  }

  handleBestMove(response) {
    const bestMove = response.move;
    const confidence = response.confidence || 'unknown';
    const depth = response.depth || 'unknown';
    
    console.log(`🎯 Best move: ${bestMove} (confidence: ${confidence}, depth: ${depth})`);
    
    // Store move analysis
    this.gameState.engineThinking = false;
    
    // Get auto-play delay from settings
    chrome.storage.sync.get(['autoPlayDelay', 'botEnabled'], (data) => {
      if (data.botEnabled !== false) {
        const delay = data.autoPlayDelay || 1000;
        
        console.log(`⏰ Auto-playing move in ${delay}ms`);
        setTimeout(() => {
          this.executeMove(bestMove);
        }, delay);
      } else {
        console.log('🚫 Auto-play disabled, move not executed');
      }
    });
  }

  handleKingsRowError(error) {
    console.error('❌ KingsRow error:', error);
    
    this.showNotification(
      'KingsRow Error',
      error.message || 'An error occurred with the KingsRow engine'
    );
    
    this.gameState.engineThinking = false;
  }

  executeMove(move) {
    // Send move to content script for execution
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, {
          type: 'EXECUTE_MOVE',
          move: move
        }, (response) => {
          if (chrome.runtime.lastError) {
            console.error('❌ Error executing move:', chrome.runtime.lastError);
          } else if (response && response.success) {
            console.log('✅ Move executed successfully:', move);
            this.gameState.history.push(move);
          } else {
            console.error('❌ Failed to execute move:', move);
          }
        });
      }
    });
  }

  handleMessage(message, sender, sendResponse) {
    switch (message.type) {
      case 'OPPONENT_MOVE':
        this.processOpponentMove(message, sendResponse);
        break;
        
      case 'GET_ENGINE_STATUS':
        sendResponse({
          connected: this.isConnected,
          thinking: this.gameState.engineThinking,
          gameHistory: this.gameState.history
        });
        break;
        
      case 'RESET_GAME':
        this.resetGame();
        sendResponse({ success: true });
        break;
        
      case 'MANUAL_MOVE':
        this.requestManualMove(message.position, sendResponse);
        break;
        
      default:
        console.log('❓ Unknown message type:', message.type);
        sendResponse({ error: 'Unknown message type' });
    }
  }

  processOpponentMove(message, sendResponse) {
    const { move, gameHistory, boardState, playerColor } = message;
    
    console.log(`🎯 Processing opponent move: ${move}`);
    
    if (!this.isConnected) {
      console.error('❌ KingsRow not connected');
      sendResponse({ error: 'KingsRow not connected' });
      return;
    }

    if (this.gameState.engineThinking) {
      console.log('⏳ Engine already thinking, queuing move...');
      this.pendingMoves.push(message);
      sendResponse({ queued: true });
      return;
    }

    this.gameState.engineThinking = true;
    this.gameState.history = gameHistory;
    
    // Send position to KingsRow for analysis
    const kingsrowMessage = {
      command: 'get_best_move',
      opponent_move: move,
      game_history: gameHistory,
      board_state: boardState,
      player_color: playerColor,
      position_format: 'playok',
      time_limit: 10, // seconds
      search_depth: 12
    };

    const success = this.sendToKingsRow(kingsrowMessage);
    sendResponse({ 
      success, 
      message: success ? 'Move sent to KingsRow' : 'Failed to send to KingsRow'
    });

    // Process any pending moves after current analysis
    if (success && this.pendingMoves.length > 0) {
      setTimeout(() => {
        if (!this.gameState.engineThinking && this.pendingMoves.length > 0) {
          const nextMove = this.pendingMoves.shift();
          this.processOpponentMove(nextMove, () => {});
        }
      }, 1000);
    }
  }

  requestManualMove(position, sendResponse) {
    if (!this.isConnected) {
      sendResponse({ error: 'KingsRow not connected' });
      return;
    }

    const message = {
      command: 'analyze_position',
      position: position,
      return_best_move: true,
      analysis_depth: 15
    };

    this.sendToKingsRow(message);
    sendResponse({ success: true, message: 'Position sent for analysis' });
  }

  resetGame() {
    console.log('🔄 Resetting game state');
    
    this.gameState = {
      history: [],
      currentPosition: null,
      engineThinking: false
    };
    
    this.pendingMoves = [];

    if (this.isConnected) {
      this.sendToKingsRow({
        command: 'new_game'
      });
    }
  }

  showNotification(title, message) {
    // Create notification for user
    if (chrome.notifications && chrome.notifications.create) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon.png',
        title: title,
        message: message
      });
    } else {
      console.log(`📢 ${title}: ${message}`);
    }
  }

  // Utility method to get current tab
  getCurrentTab(callback) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs && tabs[0]) {
        callback(tabs[0]);
      } else {
        console.error('❌ No active tab found');
        callback(null);
      }
    });
  }
}

// Initialize the connector
const kingsrowConnector = new KingsRowConnector();
