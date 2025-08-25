// content.js
const movePattern = /^\d{1,2}[-x]\d{1,2}(x\d{1,2})*$/;
let previousMoves = [];
let isProcessing = false;

function extractMoves() {
  if (isProcessing) return;
  
  const tds = Array.from(document.querySelectorAll("td"));
  let newMoves = [];

  tds.forEach(td => {
    const move = td.textContent.trim();
    if (movePattern.test(move) && !previousMoves.includes(move)) {
      newMoves.push(move);
    }
  });

  if (newMoves.length > 0) {
    previousMoves.push(...newMoves);
    isProcessing = true;
    
    chrome.runtime.sendMessage({ 
      type: "opponentMove", 
      move: newMoves[newMoves.length - 1], 
      history: previousMoves 
    });
    
    // Reset processing flag after a delay
    setTimeout(() => {
      isProcessing = false;
    }, 2000);
  }
}

function executeMove(move) {
  console.log("Executing move:", move);
  
  // Enhanced move execution for PlayOK's interface
  // First try standard data-square attributes
  const moveParts = move.split(/[-x]/);
  const from = moveParts[0];
  const to = moveParts[moveParts.length - 1];
  
  // Try multiple selector strategies for PlayOK interface
  const selectors = [
    `[data-square='${from}']`,
    `[data-pos='${from}']`,
    `[id*='${from}']`,
    `[onclick*='${from}']`,
    `.square-${from}`,
    `#square${from}`
  ];
  
  let fromElement = null;
  for (const selector of selectors) {
    fromElement = document.querySelector(selector);
    if (fromElement) break;
  }
  
  if (!fromElement) {
    console.error("Could not find from square:", from);
    return;
  }
  
  // Simulate click on the "from" square
  fromElement.click();
  
  // Handle captures and multi-jumps
  if (move.includes('x')) {
    const jumps = move.split('x');
    jumps.slice(1).forEach((jumpSquare, index) => {
      setTimeout(() => {
        let jumpElement = null;
        for (const selector of selectors) {
          const jumpSelector = selector.replace(from, jumpSquare);
          jumpElement = document.querySelector(jumpSelector);
          if (jumpElement) break;
        }
        
        if (jumpElement) {
          jumpElement.click();
        } else {
          console.error("Could not find jump square:", jumpSquare);
        }
      }, 200 * (index + 1));
    });
  } else {
    // Simple move
    setTimeout(() => {
      let toElement = null;
      for (const selector of selectors) {
        const toSelector = selector.replace(from, to);
        toElement = document.querySelector(toSelector);
        if (toElement) break;
      }
      
      if (toElement) {
        toElement.click();
      } else {
        console.error("Could not find to square:", to);
      }
    }, 200);
  }
}

// Listen for engine moves
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "engineMove") {
    executeMove(msg.move);
  }
});

// Monitor for new moves every 500ms
setInterval(extractMoves, 500);

// Also monitor for DOM changes (more responsive)
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.type === 'childList' || mutation.type === 'characterData') {
      extractMoves();
    }
  });
});

// Start observing the document
observer.observe(document.body, {
  childList: true,
  subtree: true,
  characterData: true
});

console.log("PlayOK AutoMove Bot content script loaded");
