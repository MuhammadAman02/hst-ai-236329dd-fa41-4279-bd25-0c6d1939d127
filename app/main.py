import asyncio
from nicegui import ui, app
from app.components.game_engine import game_engine
from app.components.ui_components import game_ui
from app.config import settings

# Add CSS and JavaScript files
ui.add_head_html('<link rel="stylesheet" href="/static/css/game.css">')
ui.add_head_html('<script src="/static/js/game.js"></script>')

@ui.page('/')
async def index():
    """Main game page"""
    ui.page_title(settings.game_title)
    
    # Create game container
    game_ui.create_game_container()
    
    # Start game update loop
    asyncio.create_task(game_update_loop())
    
    # Add JavaScript to expose game engine to client
    ui.run_javascript('''
        window.gameEngine = {
            player_jump: () => fetch('/api/player/jump', {method: 'POST'}),
            player_slide: () => fetch('/api/player/slide', {method: 'POST'}),
            start_game: () => fetch('/api/game/start', {method: 'POST'}),
            session: {state: 'menu'}
        };
    ''')

async def game_update_loop():
    """Main game update loop"""
    while True:
        if game_engine.session.state.value == "playing":
            # Start game engine loop if not running
            if not game_engine.running:
                game_engine.running = True
                asyncio.create_task(game_engine.game_loop())
                
        # Get current game data
        game_data = game_engine.get_game_data()
        
        # Update UI
        game_ui.update_game_display(game_data)
        
        # Check for game over
        if game_data['state'] == 'game_over':
            game_ui.show_game_over(game_data)
            
        await asyncio.sleep(1/30)  # 30 FPS UI updates

# API endpoints for game controls
@app.get('/api/game/data')
def get_game_data():
    """Get current game data"""
    return game_engine.get_game_data()

@app.post('/api/game/start')
def start_game():
    """Start a new game"""
    game_engine.start_game()
    return {"status": "started"}

@app.post('/api/game/pause')
def pause_game():
    """Pause the game"""
    game_engine.pause_game()
    return {"status": "paused"}

@app.post('/api/game/resume')
def resume_game():
    """Resume the game"""
    game_engine.resume_game()
    return {"status": "resumed"}

@app.post('/api/player/jump')
def player_jump():
    """Make player jump"""
    game_engine.player_jump()
    return {"action": "jump"}

@app.post('/api/player/slide')
def player_slide():
    """Make player slide"""
    game_engine.player_slide()
    return {"action": "slide"}

# Health check endpoint for deployment
@app.get('/health')
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "game_state": game_engine.session.state.value,
        "version": "1.0.0"
    }