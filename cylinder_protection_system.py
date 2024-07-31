import RPi.GPIO as gpio
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import I2C_LCD_driver

mylcd = I2C_LCD_driver.lcd()

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Optionally, you can adjust the gain to change the range of the ADC
# ads.gain = 2

# Create single-ended input on channel 0
channel1 = AnalogIn(ads, ADS.P0)
channel2 = AnalogIn(ads, ADS.P1)

# Define GPIO pins
DT = 5
SCK = 6

# GPIO setup
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
gpio.setup(DT, gpio.IN)
gpio.setup(SCK, gpio.OUT)

def readCount():
    Count = 0
    gpio.output(SCK, 0)
    
    while gpio.input(DT) == 1:
        pass
    
    for i in range(24):
        gpio.output(SCK, 1)
        Count = Count << 1
        gpio.output(SCK, 0)
        if gpio.input(DT) == 0:
            Count = Count + 1
    
    gpio.output(SCK, 1)
    Count = Count ^ 0x800000  # Convert to signed value
    gpio.output(SCK, 0)
    
    return Count  

def tare():
    # This function will zero the load cell
    count = readCount()
    print("Taring... current count:", count)
    return count

try:
    print("Starting weight measurement...")
    
    # Tare the load cell
    tare_offset = tare()
    
    # Calibration factor - adjust as necessary
    calibration_factor = 103.0
    
    while True:
        count = readCount() - tare_offset  # Subtract tare offset to zero the scale
        
        # Check if count is negative and correct if necessary
        if count < 0:
            count = 0
        
        # Replace 103 with the calibration factor determined from your calibration process
        weight_g = count / calibration_factor  
        weight_kg = weight_g / 1000.0
        
        print("Weight: {:.2f} g / {:.4f} kg".format(weight_g, weight_kg))
       
        # Read sensor values
        gas_value = channel1.value
        rain_value = channel2.value
        
        # Ensure rain sensor value is not negative
        if rain_value < 0:
            rain_value = 0
        
        print("gas sensor: ", gas_value)
        print("rain sensor: ", rain_value)
        
        # Display values on LCD
        mylcd.lcd_display_string("Weight:{:.4f}KG".format(weight_kg), 1, 0)
        mylcd.lcd_display_string("gas:", 2, 0)
        mylcd.lcd_display_string(str(gas_value), 2, 5)
        
        time.sleep(0.5)
        
        mylcd.lcd_clear()
        
        mylcd.lcd_display_string("rain sensor:", 1, 0)
        mylcd.lcd_display_string(str(rain_value), 2, 7)
        
        time.sleep(0.5)
        
        mylcd.lcd_clear()
        
except KeyboardInterrupt:
    print("Exiting...")
finally:
    gpio.cleanup()
