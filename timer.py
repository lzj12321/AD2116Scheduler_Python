import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import QApplication,QWidget
from PyQt5 import QtWidgets
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.Qt import QLineEdit,QTextEdit
from PyQt5.QtCore import QDateTime

class Timer(QTimer):
    timerTimeout=pyqtSignal(int)
    def __init__(self):
        super(Timer,self).__init__()
        self.timeout.connect(self.timerOutTime)
        pass

    def setTimerDescriptor(self,number,descriptor):
        self.timerNumber=number
        self.timerDescriptor=descriptor
        pass

    def getTimerDescriptor(self):
        return self.timerDescriptor
        pass

    def timerOutTime(self):
        self.timerTimeout.emit(self.timerNumber)
        pass


