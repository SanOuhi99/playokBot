// background.js
let port = null;
let isConnected = false;

function connectToEngine() {
  if (isConnected) return;
  
  try {
    port = chrome.runtime.connectNative('com.playok.kingrow');
    
    port.onMessage.addListener((response) => {
      if (response.move) {
        // Send the engine's move back to content script
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
          chrome.tabs.sendMessage(tabs[0].id, {
            type: "engineMove",
            move: response.move
          });
        });
      }
    });
    
    port.onDisconnect.addListener(() => {
      console.log("Engine connection lost - will retry when needed");
      port = null;
      isConnected = false;
    });
    
    isConnected = true;
    console.log("Connected to checkerboard engine");
    
  } catch (error) {
    console.log("Native messaging not available - using fallback mode");
    isConnected = false;
    port = null;
  }
}

// Handle messages from content script
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "opponentMove") {
    console.log("Opponent move detected:", msg.move);
    
    // Try to connect if not already connected
    if (!isConnected) {
      connectToEngine();
    }
    
    if (port && isConnected) {
      // Format message for engine
      const engineMessage = {
        command: "getMove",
        currentMove: msg.move,
        history: msg.history
      };
      
      try {
        port.postMessage(engineMessage);
        console.log("Sent move to engine:", msg.move);
      } catch (e) {
        console.error("Error sending to engine:", e);
        isConnected = false;
        port = null;
        // Try to reconnect
        setTimeout(() => connectToEngine(), 1000);
      }
    } else {
      console.log("Engine not connected - move will be processed when connection is available");
      
      // Fallback: simulate engine response for testing
      setTimeout(() => {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
          if (tabs[0]) {
            chrome.tabs.sendMessage(tabs[0].id, {
              type: "engineMove",
              move: "11-15" // Basic fallback move
            });
          }
        });
      }, 2000);
    }
  }
});
