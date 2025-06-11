import asyncio
import random
import time
from typing import List
from models.game_models import (
    GameSession, GameState, PlayerAction, 
    Obstacle, Coin, ObstacleType
)
from app.config import settings

class GameEngine:
    """Core game engine handling game logic and state"""
    
    def __init__(self):
        self.session = GameSession()
        self.running = False
        self.update_task = None
        
    def start_game(self):
        """Start a new game"""
        self.session = GameSession(
            state=GameState.PLAYING,
            speed=settings.initial_speed
        )
        self.running = True
        
    def pause_game(self):
        """Pause the current game"""
        if self.session.state == GameState.PLAYING:
            self.session.state = GameState.PAUSED
            
    def resume_game(self):
        """Resume paused game"""
        if self.session.state == GameState.PAUSED:
            self.session.state = GameState.PLAYING
            
    def game_over(self):
        """End the current game"""
        self.session.state = GameState.GAME_OVER
        if self.session.score > self.session.high_score:
            self.session.high_score = self.session.score
        self.running = False
        
    def player_jump(self):
        """Make player jump"""
        if (self.session.state == GameState.PLAYING and 
            self.session.player.action == PlayerAction.RUNNING):
            self.session.player.action = PlayerAction.JUMPING
            self.session.player.action_timer = settings.jump_duration
            
    def player_slide(self):
        """Make player slide"""
        if (self.session.state == GameState.PLAYING and 
            self.session.player.action == PlayerAction.RUNNING):
            self.session.player.action = PlayerAction.SLIDING
            self.session.player.action_timer = settings.slide_duration
            
    def update_player(self, dt: float):
        """Update player state"""
        if self.session.player.action_timer > 0:
            self.session.player.action_timer -= dt
            if self.session.player.action_timer <= 0:
                self.session.player.action = PlayerAction.RUNNING
                self.session.player.action_timer = 0
                
    def spawn_obstacle(self):
        """Spawn a new obstacle"""
        if random.random() < settings.obstacle_spawn_rate:
            obstacle_type = random.choice(list(ObstacleType))
            
            # Position based on obstacle type
            if obstacle_type == ObstacleType.HIGH:
                y = 320  # Ground level
                height = 60
            elif obstacle_type == ObstacleType.LOW:
                y = 280  # Lower position for sliding under
                height = 40
            else:  # MOVING
                y = 300
                height = 50
                
            obstacle = Obstacle(
                x=800,  # Start off-screen right
                y=y,
                width=40,
                height=height,
                obstacle_type=obstacle_type,
                speed=self.session.speed
            )
            self.session.obstacles.append(obstacle)
            
    def spawn_coin(self):
        """Spawn a collectible coin"""
        if random.random() < settings.coin_spawn_rate:
            # Random height for coins
            y_positions = [250, 280, 310]  # Different heights
            coin = Coin(
                x=800,
                y=random.choice(y_positions),
                width=20,
                height=20
            )
            self.session.coins.append(coin)
            
    def update_obstacles(self, dt: float):
        """Update obstacle positions"""
        for obstacle in self.session.obstacles[:]:
            obstacle.x -= obstacle.speed * 60 * dt  # 60 FPS reference
            
            # Remove obstacles that are off-screen
            if obstacle.x < -obstacle.width:
                self.session.obstacles.remove(obstacle)
                
    def update_coins(self, dt: float):
        """Update coin positions and animations"""
        for coin in self.session.coins[:]:
            coin.x -= self.session.speed * 60 * dt
            coin.spin_angle += 360 * dt  # Spin animation
            
            # Remove coins that are off-screen
            if coin.x < -coin.width:
                self.session.coins.remove(coin)
                
    def check_collisions(self):
        """Check for collisions between player and objects"""
        player = self.session.player
        
        # Check obstacle collisions
        for obstacle in self.session.obstacles:
            if self.objects_collide(player, obstacle):
                # Check if player can avoid obstacle
                if obstacle.obstacle_type == ObstacleType.HIGH and player.action == PlayerAction.JUMPING:
                    continue  # Player jumped over
                elif obstacle.obstacle_type == ObstacleType.LOW and player.action == PlayerAction.SLIDING:
                    continue  # Player slid under
                else:
                    self.game_over()
                    return
                    
        # Check coin collisions
        for coin in self.session.coins[:]:
            if not coin.collected and self.objects_collide(player, coin):
                coin.collected = True
                self.session.coins_collected += 1
                self.session.score += settings.coin_score
                
    def objects_collide(self, obj1, obj2) -> bool:
        """Check if two game objects collide"""
        return (obj1.x < obj2.x + obj2.width and
                obj1.x + obj1.width > obj2.x and
                obj1.y < obj2.y + obj2.height and
                obj1.y + obj1.height > obj2.y)
                
    def update_game_state(self, dt: float):
        """Update overall game state"""
        if self.session.state != GameState.PLAYING:
            return
            
        # Update game time and distance
        self.session.game_time += dt
        self.session.distance = int(self.session.game_time * 10)
        self.session.score += settings.distance_score
        
        # Increase speed over time
        if self.session.speed < settings.max_speed:
            self.session.speed += settings.speed_increment * dt
            
    async def game_loop(self):
        """Main game loop"""
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            if self.session.state == GameState.PLAYING:
                self.update_player(dt)
                self.spawn_obstacle()
                self.spawn_coin()
                self.update_obstacles(dt)
                self.update_coins(dt)
                self.check_collisions()
                self.update_game_state(dt)
                
            await asyncio.sleep(1/60)  # 60 FPS target
            
    def get_game_data(self) -> dict:
        """Get current game data for UI"""
        return {
            "state": self.session.state.value,
            "score": self.session.score,
            "distance": self.session.distance,
            "coins": self.session.coins_collected,
            "high_score": self.session.high_score,
            "speed": round(self.session.speed, 1),
            "player": {
                "x": self.session.player.x,
                "y": self.session.player.y,
                "action": self.session.player.action.value
            },
            "obstacles": [
                {
                    "x": obs.x,
                    "y": obs.y,
                    "width": obs.width,
                    "height": obs.height,
                    "type": obs.obstacle_type.value
                }
                for obs in self.session.obstacles
            ],
            "coins": [
                {
                    "x": coin.x,
                    "y": coin.y,
                    "spin": coin.spin_angle,
                    "collected": coin.collected
                }
                for coin in self.session.coins
            ]
        }

# Global game engine instance
game_engine = GameEngine()