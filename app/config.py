import os

class Settings:
    APP_NAME = "IoT Sensor Server"
    DEBUG = True

    # Encryption
    SECRET_KEY = os.getenv("SECRET_KEY", "iot-sensor-key-2024-secure-transmission")

    # Storage
    DATA_DIR = "data"

settings = Settings()