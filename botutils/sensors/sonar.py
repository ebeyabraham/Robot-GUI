import RPi.GPIO as GPIO
import time
from threading import Thread
import random

class Sonar:
    def __init__(self, echoPin, trigPin):
        GPIO.setmode(GPIO.BOARD)
        self.min_distance = 50
        self.TRIG = trigPin
        self.ECHO = echoPin
        #set the GPIO pins
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
    '''	
    def trigger(self):
        GPIO.output(self.TRIG, False)
        #wait for sensor to settle
        time.sleep(1.5)
        
        GPIO.output(self.TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG, False)
        
    def getDistance(self):
        while GPIO.input(self.ECHO) == 0:
            pulse_start = time.time()
        
        while GPIO.input(self.ECHO) == 1:
            pulse_end = time.time()
		
        pulse_duration = pulse_end - pulse_start
        
        distance = pulse_duration * 17150
        
        distance = round(distance, 2)
        
        if distance > self.min_distance:
            return 'g'
        else:
            return 'r'
    '''		
    def getDistance(self):
        GPIO.output(self.TRIG, False)
        #wait for sensor to settle
        time.sleep(2)
		
        GPIO.output(self.TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG, False)
        
        while GPIO.input(self.ECHO) == 0:
            pulse_start = time.time()
			
        while GPIO.input(self.ECHO) == 1:
            pulse_end = time.time()
			
        pulse_duration = pulse_end - pulse_start
		
        distance = pulse_duration * 17150
		
        distance = round(distance, 2)
        
        if distance > self.min_distance:
            return 'g'
        else:
            return 'r'
    
    def close(self):
        GPIO.cleanup()

