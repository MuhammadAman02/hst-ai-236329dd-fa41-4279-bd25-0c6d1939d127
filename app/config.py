from pydantic_settings import BaseSettings
from typing import Optional

class GameSettings(BaseSettings):
    """Game configuration settings"""
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Game settings
    game_title: str = "Temple Run Adventure"
    initial_speed: float = 2.0
    max_speed: float = 8.0
    speed_increment: float = 0.1
    coin_score: int = 10
    distance_score: int = 1
    
    # Game mechanics
    jump_duration: float = 0.6
    slide_duration: float = 0.4
    obstacle_spawn_rate: float = 0.02
    coin_spawn_rate: float = 0.015
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = GameSettings()