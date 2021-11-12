import sys
import Jetson.GPIO as GPIO
import time as time

inputs = [12, 13, 15, 16]
outputs = [18, 19, 21, 22]
GPIO.setmode(GPIO.BOARD)
GPIO.setup(inputs, GPIO.IN)
GPIO.setup(outputs, GPIO.OUT, initial=GPIO.LOW)

def in_state(_in):
    if(GPIO.input(_in) == 1):
        time.sleep(0.020)
        if(GPIO.input(_in) == 1):
            return True
    if(GPIO.input(_in) == 0):
        time.sleep(0.020)
        if(GPIO.input(_in) == 0):
            return False

while True:
    try:
        for i in range(4):
            if(in_state(inputs[i])):
                GPIO.output(outputs[i], GPIO.HIGH)
            else:
                GPIO.output(outputs[i], GPIO.LOW)
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit("\nPrograma finalizado.\n")
