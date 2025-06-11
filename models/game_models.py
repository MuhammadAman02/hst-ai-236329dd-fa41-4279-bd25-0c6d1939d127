from pydantic import BaseModel
from typing import List, Optional, Literal
from enum import Enum

class GameState(str, Enum):
    """Game state enumeration"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

class PlayerAction(str, Enum):
    """Player action types"""
    RUNNING = "running"
    JUMPING = "jumping"
    SLIDING = "sliding"

class ObstacleType(str, Enum):
    """Obstacle types"""
    HIGH = "high"  # Requires jumping
    LOW = "low"    # Requires sliding
    MOVING = "moving"  # Timing-based

class GameObject(BaseModel):
    """Base game object"""
    x: float
    y: float
    width: float
    height: float
    active: bool = True

class Player(GameObject):
    """Player character model"""
    action: PlayerAction = PlayerAction.RUNNING
    action_timer: float = 0.0
    
class Obstacle(GameObject):
    """Obstacle model"""
    obstacle_type: ObstacleType
    speed: float

class Coin(GameObject):
    """Collectible coin model"""
    collected: bool = False
    spin_angle: float = 0.0

class GameSession(BaseModel):
    """Current game session data"""
    state: GameState = GameState.MENU
    score: int = 0
    distance: int = 0
    coins_collected: int = 0
    speed: float = 2.0
    high_score: int = 0
    
    # Game objects
    player: Player = Player(x=100, y=300, width=40, height=60)
    obstacles: List[Obstacle] = []
    coins: List[Coin] = []
    
    # Timing
    last_update: float = 0.0
    game_time: float = 0.0