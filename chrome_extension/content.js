// PlayOK KingsRow Bot - Content Script
class PlayOKMoveDetector {
  constructor() {
    this.isEnabled = true;
    this.gameHistory = [];
    this.lastProcessedMove = null;
    this.isProcessing = false;
    this.detectionInterval = 500;
    this.boardState = new Map();
    this.gameStarted = false;
    this.isMyTurn = false;
    this.opponentColor = null;
    this.myColor = null;
    
    this.init();
  }

  init() {
    console.log('🎯 PlayOK KingsRow Bot initialized');
    
    // Load settings from storage
    chrome.storage.sync.get(['botEnabled', 'detectionInterval'], (data) => {
      this.isEnabled = data.botEnabled !== false;
      this.detectionInterval = data.detectionInterval || 500;
    });

    // Start monitoring
    this.startMonitoring();
    
    // Listen for messages from background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
    });

    // Detect game start/restart
    this.detectGameState();
  }

  startMonitoring() {
    // Monitor DOM changes
    const observer = new MutationObserver((mutations) => {
      if (this.isEnabled && !this.isProcessing) {
        this.detectMoves();
        this.updateGameState();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: true,
      attributeFilter: ['class', 'style']
    });

    // Periodic check as fallback
    setInterval(() => {
      if (this.isEnabled && !this.isProcessing) {
        this.detectMoves();
        this.updateGameState();
      }
    }, this.detectionInterval);

    console.log('📡 Move monitoring started');
  }

  detectGameState() {
    // Detect if we're in a checkers game
    const gameElements = document.querySelectorAll([
      '.game-board',
      '#game-board', 
      '.board',
      '[class*="board"]',
      '[id*="board"]'
    ].join(','));

    if (gameElements.length > 0) {
      this.gameStarted = true;
      this.detectPlayerColors();
      console.log('🎲 Checkers game detected');
    }
  }

  detectPlayerColors() {
    // Try to determine which color we're playing
    const playerInfoElements = document.querySelectorAll([
      '.player-info',
      '.player-name',
      '[class*="player"]',
      '.game-info'
    ].join(','));

    // Look for indicators of player colors
    playerInfoElements.forEach(element => {
      const text = element.textContent.toLowerCase();
      const classes = element.className.toLowerCase();
      
      if (text.includes('red') || classes.includes('red')) {
        if (text.includes('you') || classes.includes('current')) {
          this.myColor = 'red';
          this.opponentColor = 'white';
        }
      } else if (text.includes('white') || classes.includes('white')) {
        if (text.includes('you') || classes.includes('current')) {
          this.myColor = 'white';
          this.opponentColor = 'red';
        }
      }
    });

    console.log(`👤 Player colors - Me: ${this.myColor}, Opponent: ${this.opponentColor}`);
  }

  updateGameState() {
    // Check whose turn it is
    const turnIndicators = document.querySelectorAll([
      '.turn-indicator',
      '.current-player',
      '[class*="turn"]',
      '.player-active'
    ].join(','));

    let newTurnState = false;
    turnIndicators.forEach(element => {
      const text = element.textContent.toLowerCase();
      const classes = element.className.toLowerCase();
      
      if ((text.includes('your') && text.includes('turn')) ||
          (text.includes('you') && text.includes('move')) ||
          classes.includes('your-turn') ||
          classes.includes('active')) {
        newTurnState = true;
      }
    });

    if (newTurnState !== this.isMyTurn) {
      this.isMyTurn = newTurnState;
      console.log(`🔄 Turn changed - My turn: ${this.isMyTurn}`);
      
      // If it's not my turn, opponent just moved
      if (!this.isMyTurn) {
        setTimeout(() => this.detectMoves(), 100);
      }
    }
  }

  detectMoves() {
    if (this.isProcessing) return;

    const moves = this.extractMovesFromPage();
    const newMoves = moves.filter(move => !this.gameHistory.includes(move));

    if (newMoves.length > 0) {
      // Process the latest move
      const latestMove = newMoves[newMoves.length - 1];
      
      if (latestMove !== this.lastProcessedMove) {
        console.log('🎯 New move detected:', latestMove);
        this.processOpponentMove(latestMove);
        this.lastProcessedMove = latestMove;
        this.gameHistory.push(...newMoves);
      }
    }
  }

  extractMovesFromPage() {
    const moves = [];
    const movePatterns = [
      /\b\d{1,2}[-x]\d{1,2}(?:x\d{1,2})*\b/g,  // Standard notation
      /\b[a-h][1-8][-x][a-h][1-8]\b/gi,         // Algebraic notation
      /\b\d{1,2}\s*[-x]\s*\d{1,2}(?:\s*x\s*\d{1,2})*\b/g // Spaced notation
    ];

    // Check multiple locations for move history
    const searchSelectors = [
      '.move-history',
      '.game-moves', 
      '.moves-list',
      '.history',
      '[class*="move"]',
      '[class*="history"]',
      'td', 'div', 'span'
    ];

    searchSelectors.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      
      elements.forEach(element => {
        const text = element.textContent;
        
        movePatterns.forEach(pattern => {
          const matches = text.match(pattern);
          if (matches) {
            matches.forEach(match => {
              const cleanMove = match.trim().replace(/\s+/g, '');
              if (this.isValidMove(cleanMove)) {
                moves.push(cleanMove);
              }
            });
          }
        });
      });
    });

    return [...new Set(moves)]; // Remove duplicates
  }

  isValidMove(move) {
    // Validate move format
    const validPatterns = [
      /^\d{1,2}[-x]\d{1,2}(?:x\d{1,2})*$/,  // 12-16, 12x19, 12x19x26
      /^[a-h][1-8][-x][a-h][1-8]$/i         // a3-b4, a3xb4
    ];

    return validPatterns.some(pattern => pattern.test(move));
  }

  processOpponentMove(move) {
    if (this.isProcessing) return;
    
    this.isProcessing = true;
    console.log('⚡ Processing opponent move:', move);

    // Send to background script for KingsRow processing
    chrome.runtime.sendMessage({
      type: 'OPPONENT_MOVE',
      move: move,
      gameHistory: [...this.gameHistory],
      boardState: this.getCurrentBoardState(),
      playerColor: this.myColor
    }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('❌ Error sending move:', chrome.runtime.lastError);
      } else {
        console.log('✅ Move sent successfully');
      }
      
      // Reset processing flag after delay
      setTimeout(() => {
        this.isProcessing = false;
      }, 2000);
    });
  }

  getCurrentBoardState() {
    const boardState = {
      pieces: {},
      squares: {},
      lastMove: this.lastProcessedMove
    };

    // Try to capture current board state
    const boardElements = document.querySelectorAll([
      '[class*="square"]',
      '[id*="square"]',
      '[data-square]',
      '.piece',
      '[class*="piece"]'
    ].join(','));

    boardElements.forEach(element => {
      const rect = element.getBoundingClientRect();
      const classes = element.className;
      const id = element.id;
      
      // Extract square number/position
      const squareMatch = (classes + ' ' + id).match(/(?:square|pos|sq)[-_]?(\d+|[a-h][1-8])/i);
      if (squareMatch) {
        const square = squareMatch[1];
        boardState.squares[square] = {
          element: element.tagName,
          classes: classes,
          position: { x: rect.x, y: rect.y, width: rect.width, height: rect.height }
        };

        // Check for pieces
        if (classes.includes('piece') || element.querySelector('.piece')) {
          const pieceType = classes.includes('king') ? 'king' : 'man';
          const pieceColor = classes.includes('red') ? 'red' : 'white';
          boardState.pieces[square] = { type: pieceType, color: pieceColor };
        }
      }
    });

    return boardState;
  }

  executeMove(move) {
    console.log('🎮 Executing move:', move);

    // Parse move notation
    const parts = move.split(/[-x]/);
    if (parts.length < 2) {
      console.error('❌ Invalid move format:', move);
      return false;
    }

    const fromSquare = parts[0];
    const toSquare = parts[parts.length - 1];
    const captures = parts.slice(1, -1);

    // Find and click squares
    setTimeout(() => this.clickSquare(fromSquare), 100);
    
    if (captures.length > 0) {
      // Handle multi-jump moves
      captures.forEach((captureSquare, index) => {
        setTimeout(() => this.clickSquare(captureSquare), 300 + (index * 200));
      });
      setTimeout(() => this.clickSquare(toSquare), 300 + (captures.length * 200));
    } else {
      // Simple move
      setTimeout(() => this.clickSquare(toSquare), 300);
    }

    return true;
  }

  clickSquare(squareId) {
    const selectors = [
      `[data-square="${squareId}"]`,
      `[id*="${squareId}"]`,
      `[class*="square-${squareId}"]`,
      `[class*="sq${squareId}"]`,
      `.square${squareId}`,
      `#square${squareId}`,
      `#sq${squareId}`
    ];

    let element = null;
    for (const selector of selectors) {
      element = document.querySelector(selector);
      if (element) break;
    }

    if (element) {
      console.log(`🖱️ Clicking square ${squareId}`);
      
      // Simulate human-like click
      const rect = element.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      
      const clickEvent = new MouseEvent('click', {
        view: window,
        bubbles: true,
        cancelable: true,
        clientX: centerX,
        clientY: centerY
      });
      
      element.dispatchEvent(clickEvent);
      
      // Also try other common events
      element.dispatchEvent(new Event('mousedown', { bubbles: true }));
      element.dispatchEvent(new Event('mouseup', { bubbles: true }));
      
      return true;
    } else {
      console.error(`❌ Could not find square element for: ${squareId}`);
      return false;
    }
  }

  handleMessage(message, sender, sendResponse) {
    switch (message.type) {
      case 'EXECUTE_MOVE':
        const success = this.executeMove(message.move);
        sendResponse({ success });
        break;
        
      case 'TOGGLE_BOT':
        this.isEnabled = message.enabled;
        chrome.storage.sync.set({ botEnabled: this.isEnabled });
        console.log(`🤖 Bot ${this.isEnabled ? 'enabled' : 'disabled'}`);
        sendResponse({ enabled: this.isEnabled });
        break;
        
      case 'GET_STATUS':
        sendResponse({
          enabled: this.isEnabled,
          gameStarted: this.gameStarted,
          isMyTurn: this.isMyTurn,
          gameHistory: this.gameHistory,
          lastMove: this.lastProcessedMove
        });
        break;
        
      default:
        console.log('Unknown message type:', message.type);
    }
  }
}

// Initialize when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new PlayOKMoveDetector());
} else {
  new PlayOKMoveDetector();
}
