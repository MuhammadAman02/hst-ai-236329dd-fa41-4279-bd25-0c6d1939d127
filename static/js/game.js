// Temple Run Game Client-Side Logic

class GameClient {
    constructor() {
        this.gameData = null;
        this.updateInterval = null;
        this.keyStates = {};
        this.touchStartY = 0;
        this.touchStartX = 0;
        
        this.initializeControls();
    }
    
    initializeControls() {
        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this.jump();
            } else if (e.code === 'ArrowDown') {
                e.preventDefault();
                this.slide();
            } else if (e.code === 'Enter') {
                e.preventDefault();
                this.handleAction();
            }
        });
        
        // Touch controls for mobile
        document.addEventListener('touchstart', (e) => {
            this.touchStartY = e.touches[0].clientY;
            this.touchStartX = e.touches[0].clientX;
        });
        
        document.addEventListener('touchend', (e) => {
            if (!this.touchStartY || !this.touchStartX) return;
            
            const touchEndY = e.changedTouches[0].clientY;
            const touchEndX = e.changedTouches[0].clientX;
            
            const deltaY = this.touchStartY - touchEndY;
            const deltaX = Math.abs(this.touchStartX - touchEndX);
            
            // Vertical swipe detection
            if (Math.abs(deltaY) > Math.abs(deltaX)) {
                if (deltaY > 30) {
                    this.jump(); // Swipe up
                } else if (deltaY < -30) {
                    this.slide(); // Swipe down
                }
            }
            
            this.touchStartY = 0;
            this.touchStartX = 0;
        });
        
        // Prevent default touch behaviors
        document.addEventListener('touchmove', (e) => {
            e.preventDefault();
        }, { passive: false });
    }
    
    jump() {
        if (window.gameEngine) {
            window.gameEngine.player_jump();
        }
    }
    
    slide() {
        if (window.gameEngine) {
            window.gameEngine.player_slide();
        }
    }
    
    handleAction() {
        if (window.gameEngine) {
            const state = window.gameEngine.session.state;
            if (state === 'menu' || state === 'game_over') {
                window.gameEngine.start_game();
            }
        }
    }
    
    updateGameDisplay(gameData) {
        this.gameData = gameData;
        
        // Update player position and animation
        this.updatePlayer(gameData.player);
        
        // Update obstacles
        this.updateObstacles(gameData.obstacles);
        
        // Update coins
        this.updateCoins(gameData.coins);
        
        // Update UI
        this.updateUI(gameData);
    }
    
    updatePlayer(playerData) {
        const player = document.querySelector('.player');
        if (player) {
            player.style.left = `${playerData.x}px`;
            player.style.bottom = `${400 - playerData.y - 60}px`; // Adjust for ground level
            
            // Update animation class
            player.className = `player ${playerData.action}`;
        }
    }
    
    updateObstacles(obstacles) {
        const gameArea = document.querySelector('.game-area');
        if (!gameArea) return;
        
        // Remove existing obstacles
        const existingObstacles = gameArea.querySelectorAll('.obstacle');
        existingObstacles.forEach(obs => obs.remove());
        
        // Add current obstacles
        obstacles.forEach(obstacle => {
            const obstacleEl = document.createElement('div');
            obstacleEl.className = `obstacle ${obstacle.type}`;
            obstacleEl.style.left = `${obstacle.x}px`;
            obstacleEl.style.bottom = `${400 - obstacle.y - obstacle.height}px`;
            obstacleEl.style.width = `${obstacle.width}px`;
            obstacleEl.style.height = `${obstacle.height}px`;
            gameArea.appendChild(obstacleEl);
        });
    }
    
    updateCoins(coins) {
        const gameArea = document.querySelector('.game-area');
        if (!gameArea) return;
        
        // Remove existing coins
        const existingCoins = gameArea.querySelectorAll('.coin');
        existingCoins.forEach(coin => coin.remove());
        
        // Add current coins
        coins.forEach(coin => {
            if (!coin.collected) {
                const coinEl = document.createElement('div');
                coinEl.className = 'coin';
                coinEl.style.left = `${coin.x}px`;
                coinEl.style.bottom = `${400 - coin.y - 20}px`;
                coinEl.style.transform = `rotateY(${coin.spin}deg)`;
                gameArea.appendChild(coinEl);
            }
        });
    }
    
    updateUI(gameData) {
        // Update score display
        const scoreEl = document.querySelector('.score-value');
        if (scoreEl) scoreEl.textContent = gameData.score;
        
        const distanceEl = document.querySelector('.distance-value');
        if (distanceEl) distanceEl.textContent = `${gameData.distance}m`;
        
        const coinsEl = document.querySelector('.coins-value');
        if (coinsEl) coinsEl.textContent = gameData.coins;
        
        const speedEl = document.querySelector('.speed-value');
        if (speedEl) speedEl.textContent = `${gameData.speed}x`;
        
        // Update high score
        const highScoreEl = document.querySelector('.high-score-value');
        if (highScoreEl) highScoreEl.textContent = gameData.high_score;
    }
    
    showGameOver(gameData) {
        const gameOverScreen = document.querySelector('.game-over-screen');
        if (gameOverScreen) {
            gameOverScreen.style.display = 'flex';
            
            // Update final scores
            const finalScoreEl = gameOverScreen.querySelector('.final-score-value');
            if (finalScoreEl) finalScoreEl.textContent = gameData.score;
            
            const finalDistanceEl = gameOverScreen.querySelector('.final-distance-value');
            if (finalDistanceEl) finalDistanceEl.textContent = `${gameData.distance}m`;
            
            const finalCoinsEl = gameOverScreen.querySelector('.final-coins-value');
            if (finalCoinsEl) finalCoinsEl.textContent = gameData.coins;
        }
    }
    
    hideGameOver() {
        const gameOverScreen = document.querySelector('.game-over-screen');
        if (gameOverScreen) {
            gameOverScreen.style.display = 'none';
        }
    }
    
    showMenu() {
        const menuScreen = document.querySelector('.game-menu');
        if (menuScreen) {
            menuScreen.style.display = 'block';
        }
    }
    
    hideMenu() {
        const menuScreen = document.querySelector('.game-menu');
        if (menuScreen) {
            menuScreen.style.display = 'none';
        }
    }
}

// Initialize game client when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.gameClient = new GameClient();
});

// Utility functions for particle effects
function createCoinCollectEffect(x, y) {
    const effect = document.createElement('div');
    effect.className = 'coin-collect-effect';
    effect.style.position = 'absolute';
    effect.style.left = `${x}px`;
    effect.style.bottom = `${y}px`;
    effect.style.width = '20px';
    effect.style.height = '20px';
    effect.style.background = 'radial-gradient(circle, #fbbf24, #f59e0b)';
    effect.style.borderRadius = '50%';
    effect.style.animation = 'coinCollect 0.5s ease-out forwards';
    effect.style.zIndex = '100';
    
    document.querySelector('.game-area').appendChild(effect);
    
    setTimeout(() => {
        effect.remove();
    }, 500);
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GameClient;
}