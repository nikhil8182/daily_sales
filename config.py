import os
from datetime import timedelta

class Config:
    """Base configuration."""
    # Secret key
    SECRET_KEY = 'hardcoded-secret-key'
    
    # Security
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    
    # App settings
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True

class ProductionConfig(Config):
    """Production configuration."""
    
    # Recommended for production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}