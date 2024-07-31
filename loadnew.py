import RPi.GPIO as gpio
import time

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
    
    while True:
        count = readCount() - tare_offset  # Subtract tare offset to zero the scale
        # Replace 103 with the calibration factor determined from your calibration process
        weight_g = count / 103.0  
        weight_kg = weight_g / 1000.0
        
        print("Weight: {:.2f} g / {:.4f} kg".format(weight_g, weight_kg))
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Exiting...")
finally:
    gpio.cleanup()
