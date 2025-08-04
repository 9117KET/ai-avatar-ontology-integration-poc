"""Configuration settings for the AI Physics Tutor application."""

import os
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class SecurityConfig:
    """Security-related configuration settings."""
    jwt_secret: str
    jwt_algorithm: str = 'HS256'
    rate_limit: int = 100
    rate_limit_window: int = 60  # seconds
    allowed_origins: List[str] = None
    
    def __post_init__(self):
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET environment variable is required for security")
        
        if self.allowed_origins is None:
            origins_str = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000')
            self.allowed_origins = [origin.strip() for origin in origins_str.split(',')]


@dataclass
class APIConfig:
    """API-related configuration settings."""
    anthropic_api_key: str
    max_tokens: int = 1024
    model_name: str = "claude-3-haiku-20240307"
    timeout: int = 30
    
    def __post_init__(self):
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        if not self.anthropic_api_key.startswith("sk-ant-"):
            raise ValueError("API key appears to be in wrong format. Should start with 'sk-ant-'")


@dataclass
class AppConfig:
    """General application configuration settings."""
    host: str = '0.0.0.0'
    port: int = 5000
    debug: bool = False
    log_level: str = 'INFO'
    
    def __post_init__(self):
        # Override with environment variables if available
        self.host = os.getenv('HOST', self.host)
        self.port = int(os.getenv('PORT', str(self.port)))
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', self.log_level)


def load_config() -> Tuple[AppConfig, SecurityConfig, APIConfig]:
    """Load configuration from environment variables."""
    security_config = SecurityConfig(
        jwt_secret=os.getenv('JWT_SECRET'),
        rate_limit=int(os.getenv('RATE_LIMIT', '100')),
        rate_limit_window=int(os.getenv('RATE_LIMIT_WINDOW', '60'))
    )
    
    api_config = APIConfig(
        anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
        max_tokens=int(os.getenv('MAX_TOKENS', '1024')),
        model_name=os.getenv('MODEL_NAME', 'claude-3-haiku-20240307'),
        timeout=int(os.getenv('API_TIMEOUT', '30'))
    )
    
    app_config = AppConfig()
    
    return app_config, security_config, api_config