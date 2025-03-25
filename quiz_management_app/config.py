import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class Config:
    SECRET_KEY = 'yash2003'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///E:/quiz_management_app/app/data/quiz_app.db'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Add this to verify the path
if __name__ == '__main__':
    print(f"Database path: {BASE_DIR/'app'/'data'/'quiz_app.db'}")