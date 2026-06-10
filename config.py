import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'tidak_ditetapkan')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'tidak_ditetapkan')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'tidak_ditetapkan')
