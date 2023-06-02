import board
import displayio
import adafruit_touchscreen
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label

# Set up the display
display = board.DISPLAY
splash = displayio.Group()
display.show(splash)

# Set up the touch screen
touchscreen = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR, board.TOUCH_YD, board.TOUCH_YU, calibration=((5200, 59000), (5800, 57000)))

# Set up the font
font = bitmap_font.load_font("/fonts/Arial-12.bdf")
font.load_glyphs(b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')

# Set up the label
label = Label(font, text="Touch the screen!", color=0xFFFFFF, anchored_position=(0.2 * display.width, 200 * display.height))
splash.append(label)

# Main loop
while True:
    # Wait for a touch
    touch = touchscreen.touch_point

    if touch is not None:
        # Update the label with touch coordinates
        label.text = "Touch coordinates: ({}, {})".format(touch[0], touch[1])
