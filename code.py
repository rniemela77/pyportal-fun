import time
import board
import busio
import displayio
import terminalio
from adafruit_pyportal import PyPortal

# Set up the PyPortal with the correct parameters for your display and network connection
pyportal = PyPortal(default_bg=0xFFFFFF, url="https://ancient-mountain-86014.herokuapp.com/api/hello", json_path=["image_url", "text"]);
