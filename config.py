import os
from datetime import timedelta

class Config:
    # Set to True for development, False for production
    DEBUG = True
    
    # SQLite database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tapedeck.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for session management and CSRF protection
    SECRET_KEY = 'dev-secret-key-change-for-production'
    
    # Flask-Login settings
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    
    # Application specific settings
    APP_NAME = 'TapeDeck'
    
    # Default moods to pre-populate
    DEFAULT_MOODS = ['Happy', 'Sad', 'Energetic', 'Relaxed', 'Focused']