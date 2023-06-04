import board
import busio
import json
from digitalio import DigitalInOut
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
import terminalio
from adafruit_touchscreen import Touchscreen

# Define the URL we'll be sending requests to
TEXT_URL = "https://message-reader-server.herokuapp.com/api/hello"
CLICK_URL = "https://message-reader-server.herokuapp.com/api/click"

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

def fetch_data(url):
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
    return json_data


def center_align(text, width):
    ''' 
    This function returns the text with leading spaces to center-align it within the specified width
    '''
    spaces = (width - len(text)) // 2
    return ' ' * spaces + text

def load_font():
    ''' 
    This function loads the font file from the CIRCUITPY drive and returns the font object
    '''
    font = bitmap_font.load_font("/fonts/Arial-12.bdf")
    return font

def hex_to_pyportal_color(hex_code):
    # Remove the '#' symbol if present
    hex_code = hex_code.lstrip("#")
    
    # Convert the hex code to an integer
    color_int = int(hex_code, 16)
    
    # Extract the individual RGB components
    red = (color_int >> 16) & 0xFF
    green = (color_int >> 8) & 0xFF
    blue = color_int & 0xFF
    
    # Convert the RGB values to the 16-bit PyPortal format
    pyportal_color = (red & 0xF8) << 8 | (green & 0xFC) << 3 | (blue & 0xF8) >> 3
    
    return pyportal_color

# Main code execution
def main():
    secrets = initialize_secrets()
    esp32_cs, esp32_ready, esp32_reset = initialize_pins()
    esp = initialize_esp(esp32_cs, esp32_ready, esp32_reset)
    requests.set_socket(socket, esp)
    connect_to_wifi(esp, secrets)
    r = fetch_data(TEXT_URL)
    parsed_response = parse_json_response(r)
    message_text = parsed_response['message']
    message_color = parsed_response['color']
    message_color = hex_to_pyportal_color(message_color)
    
    # Initialize the display
    display = board.DISPLAY
    group = displayio.Group()
    display.show(group)

    # Initialize the touchscreen
    ts = Touchscreen(board.TOUCH_XL, board.TOUCH_XR, board.TOUCH_YD, board.TOUCH_YU, calibration=((5200, 59000), (5800, 57000)), size=(display.width, display.height))
    
    # Load the font
    font = load_font()

    # Create a styled text label (use helloColor value)
    text_label = label.Label(font, text=message_text, color=message_color)
    text_label.x = display.width // 2 - text_label.width // 2 # Center the text horizontally
    text_label.y = display.height // 2 - text_label.height // 2 # Center the text vertically
    group.append(text_label)

    # Update the display
    display.refresh()

    # Wait for user input or event
    while True:
        p = ts.touch_point
        if p:
            r = fetch_data(CLICK_URL)
            parsed_response = parse_json_response(r)
            message_text = parsed_response['message']
            
            text_label.text = message_text
            text_label.x = display.width // 2 - text_label.width // 2
            text_label.y = display.height // 2 - text_label.height // 2
            display.refresh()

# Call the main function to start the program
if __name__ == "__main__":
    main()
