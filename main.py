# Import necessary modules
import board
import busio
import json
from digitalio import DigitalInOut
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi

# Define the URL we'll be sending requests to
TEXT_URL = "https://ancient-mountain-86014.herokuapp.com/api/hello"

def initialize_secrets():
    ''' 
    This function tries to import the secrets file which contains Wi-Fi credentials 
    '''
    try:
        from secrets import secrets
    except ImportError:
        print("WiFi secrets are kept in secrets.py, please add them there!")
        raise
    return secrets

def initialize_pins():
    ''' 
    This function initializes the digital pins used for the ESP32 module
    '''
    esp32_cs = DigitalInOut(board.ESP_CS)
    esp32_ready = DigitalInOut(board.ESP_BUSY)
    esp32_reset = DigitalInOut(board.ESP_RESET)
    return esp32_cs, esp32_ready, esp32_reset

def initialize_esp(esp32_cs, esp32_ready, esp32_reset):
    ''' 
    This function sets up the SPI (Serial Peripheral Interface) connection and
    creates an instance of the ESP_SPIcontrol class
    '''
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
    return esp

def connect_to_wifi(esp, secrets):
    ''' 
    This function tries to connect to the Wi-Fi network specified in the secrets module
    '''
    while not esp.is_connected:
        try:
            esp.connect_AP(secrets["ssid"], secrets["password"])
        except OSError:
            continue

def fetch_data(esp, url):
    ''' 
    This function fetches data from the specified URL and returns the response
    '''
    r = requests.get(url)
    return r

def parse_json_response(r):
    ''' 
    This function loads the response text as JSON and returns the parsed message
    '''
    json_data = json.loads(r.text)
    message_text = json_data['message']
    r.close() # Close the response here, after we've finished reading from it
    return message_text

# Main code execution
def main():
    secrets = initialize_secrets()
    esp32_cs, esp32_ready, esp32_reset = initialize_pins()
    esp = initialize_esp(esp32_cs, esp32_ready, esp32_reset)
    requests.set_socket(socket, esp)
    connect_to_wifi(esp, secrets)
    r = fetch_data(esp, TEXT_URL)
    message_text = parse_json_response(r)
    print(message_text)

# Call the main function to start the program
if __name__ == "__main__":
    main()
