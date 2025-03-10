import os
from datetime import timedelta

class Config:
    """Base configuration."""
    # Secret key
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///sales.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
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
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Production configuration."""
    # Make sure SECRET_KEY is set in environment for production
    if 'SECRET_KEY' not in os.environ:
        raise ValueError("SECRET_KEY environment variable is not set")
    
    # Recommended for production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}