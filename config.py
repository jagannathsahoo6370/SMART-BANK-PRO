import os

class Config:
    SECRET_KEY = "smartbank_secret_key_2026"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "smartbank.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False