import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Add any other configurations you need, such as DB configurations
    DEBUG = False
