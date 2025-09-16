from dotenv import load_dotenv
from datetime import timedelta
import os
import redis

load_dotenv('.env')

class ApplicationConfig:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///./db.sqlite")
    DEBUG_MODE = os.getenv("DEBUG", "1") == "1"
    SQLALCHEMY_ECHO = DEBUG_MODE
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.from_url(os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"))
    SESSION_USE_SIGNER = True
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1)

    SESSION_COOKIE_NAME = "session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE="Lax"
    SESSION_COOKIE_SECURE = not DEBUG_MODE
    

    
    
    