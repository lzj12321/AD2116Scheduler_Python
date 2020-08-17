import sys
import RPi.GPIO as GPIO
from time import sleep

class Rap_GPIO:
    def __init__(self):
        #GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        #GPIO.setmode(GPIO.BOARD)
        pass

    def getIOStatus(self,io):
        #self.setIOInputMode(io)
        return GPIO.input(io)
        #return True
        pass

    def setIOStatus(self,io,state):
        #print('set '+str(io)+' state '+str(state))
        GPIO.output(io,state)
        pass

    def setIOInputMode(self,io):
        GPIO.setup(io, GPIO.IN)
        pass

    def setIOOutputMode(self,io):
        GPIO.setup(io, GPIO.OUT)
        pass

    def setIOPullUp(self,io):
        GPIO.setup(io, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        pass

    def setIOPullDown(self,io):
        GPIO.setup(io, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        pass

if __name__=='__main__':
    io=7
    testGpio=Rap_GPIO()
    testGpio.setIOInputMode(io)
    testGpio.setIOPullDown(io)
    #testGpio.setIOPullUp(io)
    while True:
        print(testGpio.getIOStatus(io))
        sleep(0.5)
    #for i in range(1,10,1):
    #   testGpio.setIOOutputMode(i)
    #    print(testGpio.getIOStatus(i))
