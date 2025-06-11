from nicegui import ui
from typing import Dict, Any
import json

class GameUI:
    """Game UI components and management"""
    
    def __init__(self):
        self.game_container = None
        self.score_elements = {}
        
    def create_game_container(self) -> ui.element:
        """Create the main game container"""
        with ui.element('div').classes('game-container') as container:
            self.game_container = container
            
            # Background elements
            ui.element('div').classes('game-background')
            ui.element('div').classes('game-ground')
            
            # Game area for dynamic objects
            with ui.element('div').classes('game-area').style('position: relative; width: 100%; height: 100%;'):
                # Player character
                ui.element('div').classes('player running').style(
                    'left: 100px; bottom: 100px;'
                )
            
            # Game UI overlay
            self.create_game_ui()
            
            # Game screens
            self.create_menu_screen()
            self.create_game_over_screen()
            
        return container
        
    def create_game_ui(self):
        """Create game UI overlay"""
        with ui.element('div').classes('game-ui'):
            # Score panel
            with ui.element('div').classes('score-panel'):
                with ui.element('div').classes('score-item'):
                    ui.element('div').classes('score-icon distance-icon')
                    with ui.element('span'):
                        ui.text('Distance: ')
                        self.score_elements['distance'] = ui.label('0m').classes('distance-value')
                        
                with ui.element('div').classes('score-item'):
                    ui.element('div').classes('score-icon coin-icon')
                    with ui.element('span'):
                        ui.text('Coins: ')
                        self.score_elements['coins'] = ui.label('0').classes('coins-value')
                        
                with ui.element('div').classes('score-item'):
                    ui.element('div').classes('score-icon speed-icon')
                    with ui.element('span'):
                        ui.text('Speed: ')
                        self.score_elements['speed'] = ui.label('2.0x').classes('speed-value')
                        
            # High score display
            with ui.element('div').classes('score-panel'):
                with ui.element('div').classes('score-item'):
                    ui.text('Score: ')
                    self.score_elements['score'] = ui.label('0').classes('score-value')
                with ui.element('div').classes('score-item'):
                    ui.text('High Score: ')
                    self.score_elements['high_score'] = ui.label('0').classes('high-score-value')
                    
    def create_menu_screen(self):
        """Create game menu screen"""
        with ui.element('div').classes('game-menu').style('display: block;'):
            ui.element('h1').classes('game-title').text('Temple Run Adventure')
            
            with ui.element('div').style('margin: 30px 0;'):
                ui.button('Start Game', on_click=self.start_game).classes('game-button')
                
            with ui.element('div').classes('controls-info'):
                ui.html('''
                    <div>Controls:</div>
                    <div style="margin-top: 10px;">
                        <span class="control-key">SPACE</span> Jump
                        <span class="control-key">↓</span> Slide
                    </div>
                    <div style="margin-top: 5px; font-size: 0.8em;">
                        Mobile: Swipe up to jump, swipe down to slide
                    </div>
                ''')
                
    def create_game_over_screen(self):
        """Create game over screen"""
        with ui.element('div').classes('game-over-screen').style('display: none;'):
            ui.element('h2').classes('game-over-title').text('Game Over!')
            
            with ui.element('div').classes('final-score'):
                with ui.element('div').style('margin-bottom: 10px;'):
                    ui.text('Final Score: ')
                    ui.label('0').classes('final-score-value')
                    
                with ui.element('div').style('margin-bottom: 10px;'):
                    ui.text('Distance: ')
                    ui.label('0m').classes('final-distance-value')
                    
                with ui.element('div'):
                    ui.text('Coins Collected: ')
                    ui.label('0').classes('final-coins-value')
                    
            ui.button('Play Again', on_click=self.restart_game).classes('game-button restart-button')
            
    def start_game(self):
        """Start the game"""
        from app.components.game_engine import game_engine
        game_engine.start_game()
        self.hide_menu()
        
    def restart_game(self):
        """Restart the game"""
        from app.components.game_engine import game_engine
        game_engine.start_game()
        self.hide_game_over()
        
    def hide_menu(self):
        """Hide menu screen"""
        ui.run_javascript('document.querySelector(".game-menu").style.display = "none";')
        
    def show_menu(self):
        """Show menu screen"""
        ui.run_javascript('document.querySelector(".game-menu").style.display = "block";')
        
    def hide_game_over(self):
        """Hide game over screen"""
        ui.run_javascript('document.querySelector(".game-over-screen").style.display = "none";')
        
    def show_game_over(self, game_data: Dict[str, Any]):
        """Show game over screen with final scores"""
        ui.run_javascript(f'''
            const gameOverScreen = document.querySelector(".game-over-screen");
            gameOverScreen.style.display = "flex";
            
            document.querySelector(".final-score-value").textContent = "{game_data['score']}";
            document.querySelector(".final-distance-value").textContent = "{game_data['distance']}m";
            document.querySelector(".final-coins-value").textContent = "{game_data['coins']}";
        ''')
        
    def update_game_display(self, game_data: Dict[str, Any]):
        """Update game display with current data"""
        # Update score elements
        if 'score' in self.score_elements:
            self.score_elements['score'].text = str(game_data['score'])
        if 'distance' in self.score_elements:
            self.score_elements['distance'].text = f"{game_data['distance']}m"
        if 'coins' in self.score_elements:
            self.score_elements['coins'].text = str(game_data['coins'])
        if 'speed' in self.score_elements:
            self.score_elements['speed'].text = f"{game_data['speed']}x"
        if 'high_score' in self.score_elements:
            self.score_elements['high_score'].text = str(game_data['high_score'])
            
        # Update game objects via JavaScript
        ui.run_javascript(f'''
            if (window.gameClient) {{
                window.gameClient.updateGameDisplay({json.dumps(game_data)});
                
                if ("{game_data['state']}" === "game_over") {{
                    window.gameClient.showGameOver({json.dumps(game_data)});
                }}
            }}
        ''')

# Global UI instance
game_ui = GameUI()