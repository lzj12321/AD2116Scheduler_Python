# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'self.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import QApplication,QWidget
from PyQt5 import QtWidgets
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.Qt import QLineEdit,QTextEdit
from PyQt5.QtCore import QDateTime
import YamlTool
import numpy as np
from  schedulerBackground import Scheduler
from schedulerParam import ModuleStates,RobotStates

class SchedulerInterface(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.iconIni()
        self.paramIni()
        self.iniModuleLabelsPosition()
        self.schedulerIni()
        self.signalAndSlotIni()
        self.updateModuleLabels()
        self.updateRobotLabels()

    def paramIni(self):
        self.yamlTool=YamlTool.Yaml_Tool()
        self.params=self.yamlTool.getParam('configure.yaml')
        self.moduleNum=self.params['Module']['num']
        self.moduleRadius=self.params['Module']['moduleRadius']
        self.robotNum=self.params['Robot']['num']
        self.robotFlags=self.params['Robot']['robotFlags'].split(',')
        self.ultraFlag=self.params['Robot']['ultrasonicFlag']
        self.sensorLabelPosition= self.params['Sensor']['modulePosition']
        self.robotModulePosition={}
        for i in range(0,self.robotNum,1):
            self.robotModulePosition[i]=self.params['Robot']['robot'+str(i)]['modulePosition']

        self.moduleArrayState=np.zeros(self.moduleNum,dtype=np.int)
        self.moduleArrayState[12]=ModuleStates.MODULE_ULTRA1_CAUGHT

        self.robotLabels=[]
        self.robotLabels.append(self.label)
        self.robotLabels.append(self.label_2)
        self.robotLabels.append(self.label_3)
        self.robotLabels.append(self.label_4)
        self.robotArrayState=np.zeros(self.robotNum,dtype=int)
        self.robotArrayState[1]=RobotStates.ROBOT_CONNECTED
        self.ultraIndex=3
        pass

    def iniModuleLabelsPosition(self):
        self.moduleLabels=[]
        for i in range(0,self.moduleNum,1):
            self.moduleLabels.append(QLabel(self.centralWidget))

        rowModuleNum=2
        lineModuleNum=int((self.moduleNum-rowModuleNum*2)/2)
        startX=self.label_5.x()
        startY=self.label_5.y()-15
        for i in range(0,self.moduleNum,1):
            if i<lineModuleNum:
                drawX=startX+((i-1)*self.moduleRadius*2)
                drawY=startY

            elif i>=lineModuleNum and i<(lineModuleNum+rowModuleNum):
                drawX=startX+(lineModuleNum-2)*self.moduleRadius*2
                drawY=startY+(i-lineModuleNum+1)*self.moduleRadius*2

            elif i>=(lineModuleNum+rowModuleNum) and i<(lineModuleNum*2+rowModuleNum):
                drawX=startX+((self.moduleNum-i-4)*self.moduleRadius*2)
                drawY=startY+120+self.moduleRadius

            else:
                drawX=startX-self.moduleRadius*2
                drawY=startY+(self.moduleNum-i)*self.moduleRadius*2

            font=QFont()
            font.setBold(True)
            self.moduleLabels[i].setFont(font)
            self.moduleLabels[i].setGeometry(drawX,drawY,self.moduleRadius+15,self.moduleRadius)
            self.moduleLabels[i].setFrameShape(QFrame.Box)
            self.moduleLabels[i].setFrameShadow(QFrame.Sunken)
            self.moduleLabels[i].setVisible(True)
            if i in self.robotModulePosition.values() or i==self.sensorLabelPosition:
                self.moduleLabels[i].setLineWidth(8)
                if i==self.robotModulePosition[self.ultraIndex]:
                    self.moduleLabels[i+1].setLineWidth(8)
        pass

    def updateModuleLabels(self):
        self.moduleArrayState=self.scheduler.moduleArrayState
        for i in range(0,self.moduleNum,1):
            if self.moduleArrayState[i]==ModuleStates.MODULE_EMPTY:
                self.moduleLabels[i].setStyleSheet("background:gray")
            elif self.moduleArrayState[i]==ModuleStates.MODULE_LOADED:
                self.moduleLabels[i].setStyleSheet("background:blue")
            elif self.moduleArrayState[i]==ModuleStates.MODULE_CATCHING:
                self.moduleLabels[i].setStyleSheet("background:yellow")
            elif self.moduleArrayState[i]==ModuleStates.MODULE_UNRECOGNIZE_ONCETIME:
                self.moduleLabels[i].setStyleSheet("background:magenta")
            elif self.moduleArrayState[i]==ModuleStates.MODULE_UNRECOGNIZE_TWICETIME:
                self.moduleLabels[i].setStyleSheet("background:darkMagenta")
            elif self.moduleArrayState[i]==ModuleStates.MODULE_ERROR:
                self.moduleLabels[i].setStyleSheet("background:red")
            elif self.moduleArrayState[i]==ModuleStates.MODULE_ULTRASONIC:
                self.moduleLabels[i].setStyleSheet("background:green")
            elif self.moduleArrayState[i]==ModuleStates.MODULE_ULTRA1_UNRECOGNIZED:
                self.moduleLabels[i].setStyleSheet("background:black")
            elif self.moduleArrayState[i]==ModuleStates.MODULE_ULTRA2_UNRECOGNIZED:
                self.moduleLabels[i].setStyleSheet("background:red")
            elif self.moduleArrayState[i]==ModuleStates.MODULE_ULTRA1_CAUGHT:
                self.moduleLabels[i].setStyleSheet("background:rgb(255, 119, 28)")
        pass

    def updateRobotLabels(self):
        self.robotArrayState=self.scheduler.robotArrayState
        for i in range(0,self.robotNum,1):
            if self.robotArrayState[i]==RobotStates.ROBOT_CONNECTED:
                self.robotLabels[i].setText("CONNECTED")
                self.robotLabels[i].setStyleSheet("background:blue")
            elif self.robotArrayState[i]==RobotStates.ROBOT_WAITING:
                self.robotLabels[i].setText("WAITTING")
                self.robotLabels[i].setStyleSheet("background:yellow")
            elif self.robotArrayState[i]==RobotStates.ROBOT_CATCHED:
                self.robotLabels[i].setText("WORKING")
                self.robotLabels[i].setStyleSheet("background:green")
            elif self.robotArrayState[i]==RobotStates.ROBOT_ACK_CATCHED:
                self.robotLabels[i].setText("WAIT CAUGHT")
                self.robotLabels[i].setStyleSheet("background:green")
            elif self.robotArrayState[i]==RobotStates.ROBOT_OFFLINE:
                self.robotLabels[i].setText("OFFLINE")
                self.robotLabels[i].setStyleSheet("background:red")
            elif self.robotArrayState[i]==RobotStates.ROBOT_ACK_CATCHED_ERROR:
                self.robotLabels[i].setText("ACK_CATCH_ERROR")
                self.robotLabels[i].setStyleSheet("background:red")
            elif self.robotArrayState[i]==RobotStates.ROBOT_RECOGNIZE_ERROR:
                self.robotLabels[i].setText("RECOGNIZE ERROR")
                self.robotLabels[i].setStyleSheet("background-color:rgb(143,89,2)")
            elif self.robotArrayState[i]==RobotStates.ROBOT_CLEARING:
                self.robotLabels[i].setText("CLEARING")
                self.robotLabels[i].setStyleSheet("background:blue")
            elif self.robotArrayState[i]==RobotStates.ULTRASONIC_ROBOT1_UNRECOGNIZED:
                self.robotLabels[i].setText("ROBOT1_UNRECOGNIZED")
                self.robotLabels[i].setStyleSheet("background-color:rgb(143,89,2)")
            elif self.robotArrayState[i]==RobotStates.ULTRASONIC_ROBOT2_UNRECOGNIZED:
                self.robotLabels[i].setText("ROBOT2_UNRECOGNIZED")
                self.robotLabels[i].setStyleSheet("background:red")
            elif self.robotArrayState[i]==RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH:
                self.robotLabels[i].setText("ULTRA_ACK_INSERT_CATCH")
                self.robotLabels[i].setStyleSheet("background:green")
            elif self.robotArrayState[i]==RobotStates.ULTRA_ROBOT_ACK_INSERT:
                self.robotLabels[i].setText("ULTRA_ACK_INSERT")
                self.robotLabels[i].setStyleSheet("background:green")
            elif self.robotArrayState[i]==RobotStates.ULTRA_ROBOT_WORKING:
                self.robotLabels[i].setText("ULTRA_ROBOT_WORKING")
                self.robotLabels[i].setStyleSheet("background:green")
            elif self.robotArrayState[i]==RobotStates.ULTRA_ROBOT_ACK_CATCH:
                self.robotLabels[i].setText("ULTRA_ACK_CATCH")
                self.robotLabels[i].setStyleSheet("background:green")
            elif self.robotArrayState[i]==RobotStates.ULTRA_ROBOT_ACK_CATCH_ERROR:
                self.robotLabels[i].setText("ACK_CATCH_ERROR")
                self.robotLabels[i].setStyleSheet("background:red")
            elif self.robotArrayState[i]==RobotStates.ULTRA_ROBOT_ACK_CATCH_INSERT_ERROR:
                self.robotLabels[i].setText("ACK_CATCH_INSERT_ERROR")
                self.robotLabels[i].setStyleSheet("background:red")
            elif self.robotArrayState[i]==RobotStates.ULTRA_ROBOT_ACK_INSERT_ERROR:
                self.robotLabels[i].setText("ACK_INSERT_ERROR")
                self.robotLabels[i].setStyleSheet("background:red")
        pass

    def closeEvent(self, event: QtGui.QCloseEvent):
        choose = QMessageBox.question(self, 'Warning', "确定退出程序?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if choose == QMessageBox.Yes:
            self.scheduler.closeScheduler()
            event.accept()
        else:
            event.ignore()

    def initUI(self):
        self.setObjectName("self")
        self.resize(1722, 799)
        self.centralWidget = QtWidgets.QWidget(self)
        self.centralWidget.setObjectName("centralWidget")
        self.label = QtWidgets.QLabel(self.centralWidget)
        self.label.setGeometry(QtCore.QRect(770, 410, 231, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setFrameShape(QtWidgets.QFrame.Panel)
        self.label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label.setLineWidth(4)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralWidget)
        self.label_2.setGeometry(QtCore.QRect(100, 410, 221, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.label_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_2.setLineWidth(4)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralWidget)
        self.label_3.setGeometry(QtCore.QRect(425, 140, 241, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setFrameShape(QtWidgets.QFrame.Panel)
        self.label_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_3.setLineWidth(4)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.label_5 = QtWidgets.QLabel(self.centralWidget)
        self.label_5.setGeometry(QtCore.QRect(80, 230, 1591, 231))
        self.label_5.setText("")
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.pushButton = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton.setGeometry(QtCore.QRect(920, 530, 191, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.textEdit = QtWidgets.QTextEdit(self.centralWidget)
        self.textEdit.setGeometry(QtCore.QRect(100, 520, 750, 241))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.textEdit.setFont(font)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.label_7 = QtWidgets.QLabel(self.centralWidget)
        self.label_7.setGeometry(QtCore.QRect(670, 30, 651, 121))
        font = QtGui.QFont()
        font.setPointSize(50)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label_7.setFont(font)
        self.label_7.setStyleSheet("color: rgb(78, 154, 6);")
        self.label_7.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton_3.setGeometry(QtCore.QRect(920, 610, 191, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        self.label_14 = QtWidgets.QLabel(self.centralWidget)
        self.label_14.setGeometry(QtCore.QRect(1420, 516, 121, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_14.setFont(font)
        self.label_14.setStyleSheet("color: rgb(204, 0, 0);")
        self.label_14.setAlignment(QtCore.Qt.AlignCenter)
        self.label_14.setObjectName("label_14")
        self.lineEdit_6 = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit_6.setGeometry(QtCore.QRect(1430, 550, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_6.setFont(font)
        self.lineEdit_6.setStyleSheet("color: rgb(204, 0, 0);")
        self.lineEdit_6.setText("")
        self.lineEdit_6.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_6.setReadOnly(True)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.lineEdit_7 = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit_7.setGeometry(QtCore.QRect(1430, 600, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_7.setFont(font)
        self.lineEdit_7.setStyleSheet("color: rgb(204, 0, 0);")
        self.lineEdit_7.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_7.setReadOnly(True)
        self.lineEdit_7.setObjectName("lineEdit_7")
        self.lineEdit_8 = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit_8.setGeometry(QtCore.QRect(1430, 650, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_8.setFont(font)
        self.lineEdit_8.setStyleSheet("color: rgb(204, 0, 0);")
        self.lineEdit_8.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_8.setReadOnly(True)
        self.lineEdit_8.setObjectName("lineEdit_8")
        self.radioButton = QtWidgets.QRadioButton(self.centralWidget)
        self.radioButton.setGeometry(QtCore.QRect(1490, 30, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.radioButton.setFont(font)
        self.radioButton.setStyleSheet("color: rgb(164, 0, 0);")
        self.radioButton.setObjectName("radioButton")
        self.radioButton_2 = QtWidgets.QRadioButton(self.centralWidget)
        self.radioButton_2.setGeometry(QtCore.QRect(1490, 70, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.radioButton_2.setFont(font)
        self.radioButton_2.setStyleSheet("color: rgb(164, 0, 0);")
        self.radioButton_2.setObjectName("radioButton_2")
        self.pushButton_4 = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton_4.setGeometry(QtCore.QRect(920, 690, 191, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton_2.setGeometry(QtCore.QRect(1200, 550, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setDefault(False)
        self.pushButton_2.setFlat(True)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_5 = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton_5.setGeometry(QtCore.QRect(1200, 600, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_5.setFont(font)
        self.pushButton_5.setFlat(True)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_6 = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton_6.setGeometry(QtCore.QRect(1200, 650, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_6.setFont(font)
        self.pushButton_6.setFlat(True)
        self.pushButton_6.setObjectName("pushButton_6")
        self.label_4 = QtWidgets.QLabel(self.centralWidget)
        self.label_4.setGeometry(QtCore.QRect(1180, 410, 261, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setStyleSheet("background-color: rgb(237, 212, 0);")
        self.label_4.setFrameShape(QtWidgets.QFrame.Panel)
        self.label_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_4.setLineWidth(4)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.label_6 = QtWidgets.QLabel(self.centralWidget)
        self.label_6.setGeometry(QtCore.QRect(1500, 400, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setStyleSheet("background-color: rgb(255, 170, 0);")
        self.label_6.setFrameShape(QtWidgets.QFrame.Panel)
        self.label_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_6.setLineWidth(3)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.label_8 = QtWidgets.QLabel(self.centralWidget)
        self.label_8.setGeometry(QtCore.QRect(70, 150, 81, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_8.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.centralWidget)
        self.label_9.setGeometry(QtCore.QRect(1580, 390, 81, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_9.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.centralWidget)
        self.label_10.setGeometry(QtCore.QRect(1500, 320, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setStyleSheet("background-color: rgb(255, 170, 0);")
        self.label_10.setFrameShape(QtWidgets.QFrame.Panel)
        self.label_10.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_10.setLineWidth(3)
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.lineEdit_9 = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit_9.setGeometry(QtCore.QRect(1310, 600, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_9.setFont(font)
        self.lineEdit_9.setStyleSheet("color: rgb(204, 0, 0);")
        self.lineEdit_9.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_9.setReadOnly(True)
        self.lineEdit_9.setObjectName("lineEdit_9")
        self.lineEdit_10 = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit_10.setGeometry(QtCore.QRect(1310, 650, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_10.setFont(font)
        self.lineEdit_10.setStyleSheet("color: rgb(204, 0, 0);")
        self.lineEdit_10.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_10.setReadOnly(True)
        self.lineEdit_10.setObjectName("lineEdit_10")
        self.label_15 = QtWidgets.QLabel(self.centralWidget)
        self.label_15.setGeometry(QtCore.QRect(1300, 516, 121, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_15.setFont(font)
        self.label_15.setStyleSheet("color: rgb(204, 0, 0);")
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.lineEdit_11 = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit_11.setGeometry(QtCore.QRect(1310, 550, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_11.setFont(font)
        self.lineEdit_11.setStyleSheet("color: rgb(204, 0, 0);")
        self.lineEdit_11.setText("")
        self.lineEdit_11.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_11.setReadOnly(True)
        self.lineEdit_11.setObjectName("lineEdit_11")
        self.lineEdit_12 = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit_12.setGeometry(QtCore.QRect(1430, 700, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_12.setFont(font)
        self.lineEdit_12.setStyleSheet("color: rgb(204, 0, 0);")
        self.lineEdit_12.setText("")
        self.lineEdit_12.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_12.setReadOnly(True)
        self.lineEdit_12.setObjectName("lineEdit_12")
        self.lineEdit_13 = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit_13.setGeometry(QtCore.QRect(1310, 700, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_13.setFont(font)
        self.lineEdit_13.setStyleSheet("color: rgb(204, 0, 0);")
        self.lineEdit_13.setText("")
        self.lineEdit_13.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_13.setReadOnly(True)
        self.lineEdit_13.setObjectName("lineEdit_13")
        self.pushButton_7 = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton_7.setGeometry(QtCore.QRect(1190, 700, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_7.setFont(font)
        self.pushButton_7.setFlat(True)
        self.pushButton_7.setObjectName("pushButton_7")
        self.checkBox = QtWidgets.QCheckBox(self.centralWidget)
        self.checkBox.setGeometry(QtCore.QRect(1460, 100, 151, 33))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.checkBox.setFont(font)
        self.checkBox.setObjectName("checkBox")
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralWidget)
        self.checkBox_2.setGeometry(QtCore.QRect(1460, 60, 151, 33))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.checkBox_2.setFont(font)
        self.checkBox_2.setObjectName("checkBox_2")

        self.checkBox_3 = QtWidgets.QCheckBox(self.centralWidget)
        self.checkBox_3.setGeometry(QtCore.QRect(1590, 60, 151, 33))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.checkBox_3.setFont(font)
        self.checkBox_3.setObjectName("checkBox_2")

        # self.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(self)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1722, 34))
        self.menuBar.setObjectName("menuBar")
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.show()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("self", "AD2116 Scheduler"))
        self.label.setText(_translate("self", "机械手"))
        self.label_2.setText(_translate("self", "机械手"))
        self.label_3.setText(_translate("self", "机械手"))
        self.pushButton.setText(_translate("self", "启动链条"))
        self.label_7.setText(_translate("self", "AD2116 调度程序"))
        self.pushButton_3.setText(_translate("self", "清除错误"))
        self.label_14.setText(_translate("self", "未识别数量"))
        self.radioButton.setText(_translate("self", "双型号模具链条"))
        self.radioButton_2.setText(_translate("self", "单型号模具链条"))

        self.radioButton.setVisible(False)
        self.radioButton_2.setVisible(False)

        self.pushButton_4.setText(_translate("self", "重置链条"))
        self.pushButton_2.setText(_translate("self", "机械手 A "))
        self.pushButton_5.setText(_translate("self", "机械手 B "))
        self.pushButton_6.setText(_translate("self", "机械手 C "))
        self.label_4.setText(_translate("self", "超声波"))
        self.label_6.setText(_translate("self", "对射传感器"))
        self.label_8.setText(_translate("self", "direction"))
        self.label_9.setText(_translate("self", "direction"))

        self.label_8.setVisible(False)
        self.label_9.setVisible(False)

        self.label_10.setText(_translate("self", "对射传感器"))
        self.label_15.setText(_translate("self", "抓机数量"))
        self.pushButton_7.setText(_translate("self", "ULTRA"))
        self.checkBox.setText(_translate("self", "ULTRASONIC"))
        self.checkBox_2.setText(_translate("self", "LAST ROBOT"))
        self.checkBox_3.setText('IsOnlyCatch')
        
        self.checkBox.setChecked(True)

        #self.pushButton_4.setEnabled(False)
        # self.pushButton.setEnabled(False)

    def schedulerIni(self):
        self.scheduler=Scheduler()
        pass

    def signalAndSlotIni(self):
        self.pushButton.clicked.connect(self.manualActivateConveyor)
        self.pushButton_3.clicked.connect(self.scheduler.clearError)
        self.pushButton_4.clicked.connect(self.scheduler.resetConveyor)
        self.scheduler.updateModulesState.connect(self.updateModuleLabels)
        self.scheduler.updateRobotsState.connect(self.updateRobotLabels)

        self.checkBox.clicked.connect(self.alterUltraState)
        self.checkBox_2.clicked.connect(self.alterLastRobotState)
        self.checkBox_3.clicked.connect(self.alterCatchState)

        self.scheduler.addRunMessage.connect(self.addRunMessage)
        pass

    def iconIni(self):
        self.logoLabel=QLabel(self)
        self.logoLabel.setGeometry(QtCore.QRect(40, 40, 251, 133))
        self.logoLabel.setVisible(True)
        logo=QPixmap('PI_LOGO.png')
        fitPixMap=logo.scaled(self.logoLabel.width(),self.logoLabel.height(),Qt.IgnoreAspectRatio,Qt.SmoothTransformation)
        self.logoLabel.setPixmap(fitPixMap)
        pass


    def alterUltraState(self,state):
        choose = QMessageBox.question(self, 'Warning', "更改超声波生产状态?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if choose == QMessageBox.Yes:
            self.scheduler.alterUltrasonicState(self.checkBox.isChecked())
        else:
            self.checkBox.setChecked(self.scheduler.isUltraValid)
        pass

    def alterLastRobotState(self,state):
        choose = QMessageBox.question(self, 'Warning', "更改链条循环状态?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if choose == QMessageBox.Yes:
            self.scheduler.alterLastRobotState(self.checkBox_2.isChecked())
        else:
            self.checkBox_2.setChecked(self.scheduler.isStopLastInLastRobot)
        pass

    def alterCatchState(self,state):
        choose = QMessageBox.question(self, 'Warning', "更改机械手生产状态?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if choose == QMessageBox.Yes:
            self.scheduler.alterCatchState(self.checkBox_3.isChecked())
        else:
            self.checkBox_3.setChecked(self.scheduler.isOnlyCatch)
        pass

    def manualActivateConveyor(self):
        choose = QMessageBox.question(self, 'Warning', "手动控制链条会停止跑拉程序！继续?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if choose == QMessageBox.Yes:
            if self.pushButton.text()=='启动链条':
                self.scheduler.manualControlConveyor(self.scheduler.activateConveyorState)
                self.pushButton.setText('关闭链条')
            elif self.pushButton.text()=='关闭链条':
                self.scheduler.manualControlConveyor(self.scheduler.closeConveyorState)
                self.pushButton.setText('启动链条')
            self.label_7.setStyleSheet("color: rgb(255, 0, 0);")
            # self.scheduler.close()
        pass

    def addRunMessage(self,msg):
        currTime=QDateTime.currentDateTime().toString('hh:mm:ss')
        self.textEdit.append(currTime+':'+msg)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SchedulerInterface()
    sys.exit(app.exec_())