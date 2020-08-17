import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.Qt import QLineEdit, QTextEdit
from PyQt5.QtCore import QDateTime
import YamlTool
# from robotTool_old import RobotTool
from time import sleep
import gpio
from schedulerParam import ModuleStates, RobotStates
import numpy as np
from socket import Socket
from timer import Timer


class Scheduler(QObject):
    updateModulesState = pyqtSignal()
    updateRobotsState = pyqtSignal()
    detectedNewModule = pyqtSignal(int)
    addRunMessage=pyqtSignal(str)

    def __init__(self):
        super(Scheduler, self).__init__()
        self.paramIni()
        print('param initialized!')
        self.ioIni()
        print('io initialized!')
        self.deviceIni()
        print('device initialized!')
        self.serverIni()
        print('server initialized!')
        self.signalAndSlotIni()
        print('signalAndSlot Initialized!')
        self.timerIni()
        print('timer initialized!')
        pass

    def paramIni(self):
        self.yamlTool = YamlTool.Yaml_Tool()
        self.param = self.yamlTool.getParam('configure.yaml')
        # print(self.param)
        self.serverPort = self.param['Server']['port']

        self.isOnlyCatch = False

        self.isConveyorRunning = True
        self.isEmergencyStop = False

        self.moduleSensor = self.param['Sensor']['moduleSensor']
        self.adapterSensor = self.param['Sensor']['adapterSensor']
        self.moduleSensorPosition = self.param['Sensor']['modulePosition']

        self.isDetectFallingEdge = False
        self.isLoadAdapter = False
        self.currentModuleSensorState = False
        self.prevModuleSensorState = False

        self.currentAdapterSensorState = False
        self.prevAdapterSensorState = False

        self.detectAdapterTime = 0
        self.maxDetectAdapterTime = self.param['DetectParam']['maxDetectAdapterTime']

        self.isProductTwoModel = False
        self.isStartDetect = False
        self.isValidModule = True
        self.isStopLastInLastRobot = False

        self.onlineTestRobotNum = 0
        self.isUltraValid = True
        self.isUltraOnline = False
        self.moduleNum = self.param['Module']['num']
        self.robotNum = self.param['Robot']['num']
        self.moduleArrayState = np.zeros(self.moduleNum, dtype=np.int)
        self.robotArrayState = np.zeros(self.robotNum, dtype=np.int)
        self.robotModuleNumber = {}

        self.ultrasonicIndex = 3

        self.robotFlags = self.param['Robot']['robotFlags'].split(',')
        self.ultraFlag = self.param['Robot']['ultrasonicFlag']

        self.robotModulePosition = {}
        self.robotsIp = {}
        for i in range(0, self.robotNum, 1):
            self.robotModulePosition[i] = self.param['Robot']['robot' + str(i)]['modulePosition']
            self.robotsIp[i] = self.param['Robot']['robot' + str(i)]['ip']

        self.lastOnlineTestRobotNumber = -1
        self.robotNumber = self.param['Robot']['num']

        self.robotSocketArray = {}

        self.catchOrder = self.param['Order']['catchOrder']
        self.dropOrder=self.param['Order']['dropOrder']
        self.waitOrder=self.param['Order']['waitOrder']
        self.caughtOrder=self.param['Order']['caughtOrder']
        self.unrecognizedOrder=self.param['Order']['unrecognizedOrder']
        self.clearOrder=self.param['Order']['clearOrder']
        
        self.ultra1UnrecognizedOrder=self.param['Order']['ultra1UnrecognizedOrder']
        self.ultra2UnrecognizedOrder=self.param['Order']['ultra2UnrecognizedOrder']

        self.ultraCaughtOrder=self.param['Order']['ultraCaughtOrder']
        self.ultraInsertedOrder=self.param['Order']['ultraInsertedOrder']
        self.ultraInsertedWaitOrder=self.param['Order']['ultraInsertedWaitOrder']
        self.ultraCaughtWaitOrder=self.param['Order']['ultraCaughtWaitOrder']

        self.conveyorIo = self.param['Conveyor']['io']
        self.activateConveyorState = self.param['Conveyor']['activate']
        self.closeConveyorState = self.param['Conveyor']['close']

        self.checkMsgTimerInterval = self.param['Timer']['checkMsgTimer']['interval']
        self.detectTimerInterval = self.param['Timer']['detectTimer']['interval']

        print('self.conveyorIo:' + str(self.conveyorIo))
        print('self.moduleSensor:' + str(self.moduleSensor))
        print('self.adapterSensor:' + str(self.adapterSensor))
        # exit(0)
        pass

    def timerIni(self):
        self.robotTimer = {}
        for i in range(0, self.robotNum, 1):
            timer = Timer()
            self.robotTimer[i] = timer
            self.robotTimer[i].setTimerDescriptor(i, 0)
            self.robotTimer[i].setInterval(self.checkMsgTimerInterval)
            self.robotTimer[i].timerTimeout.connect(self.robotTimerTimeout)

        self.detectTimer = QTimer()
        self.detectTimer.setInterval(self.detectTimerInterval)
        self.detectTimer.timeout.connect(self.detectModuleAndAdapter)
        self.detectTimer.start()

        self.TestTimer = QTimer()
        self.TestTimer.timeout.connect(self.testTimerTimeout)
        # self.TestTimer.start(1000)
        pass

    def testTimerTimeout(self):
        self.detectedModule(ModuleStates.MODULE_ULTRASONIC)

    def ioIni(self):
        self.gpioTool = gpio.Rap_GPIO()
        self.gpioTool.setIOInputMode(self.adapterSensor)
        self.gpioTool.setIOInputMode(self.moduleSensor)
        self.gpioTool.setIOPullDown(self.adapterSensor)
        self.gpioTool.setIOPullDown(self.moduleSensor)
        self.gpioTool.setIOPullDown(self.conveyorIo)
        self.gpioTool.setIOOutputMode(self.conveyorIo)
        pass

    def deviceIni(self):
        self.stopConveyor()
        pass

    def serverIni(self):
        self.server = QTcpServer()
        if not self.server.listen(QHostAddress.Any, self.serverPort):
            print('服务器初始化失败！')
            # QMessageBox.warning(self,'Warning','服务器初始化失败！')
            exit(0)
        else:
            self.server.newConnection.connect(self.newSocketConnection)
        pass

    def updateRobotAndModuleState(self):
        self.updateRobotsState.emit()
        self.updateModulesState.emit()

    def signalAndSlotIni(self):
        self.detectedNewModule.connect(self.detectedModule)
        pass

    def closeServer(self):
        self.server.close()
        pass

    def activateConveyor(self):
        if self.isConveyorRunning:
            return
        self.gpioTool.setIOStatus(self.conveyorIo, self.activateConveyorState)
        self.isConveyorRunning = True
        pass

    def stopConveyor(self):
        if not self.isConveyorRunning:
            return
        self.gpioTool.setIOStatus(self.conveyorIo, self.closeConveyorState)
        self.isConveyorRunning = False
        pass

    def sendOrderToRobot(self, robotNumber):
        order=''
        if self.isOnlyCatch:
            order=self.dropOrder
        else:
            order=self.catchOrder
        print('send order:'+order)
        if self.robotSocketArray[robotNumber].sendMsg(order):
            self.robotCatching(robotNumber)
        else:
            self.robotOffline(robotNumber)
        pass

    def sendOrderToUltra(self, order):
        print(QDateTime.currentDateTime().toString('mm:ss:zzz')+' send order to ultra:' + order)
        self.robotSocketArray[self.ultrasonicIndex].sendMsg(order)
        pass

    def robotTimerTimeout(self, robotNumber):
        print('robotTimerTimeout')
        self.robotTimer[robotNumber].stop()
        timerDescriptor = self.robotTimer[robotNumber].getTimerDescriptor()
        if timerDescriptor == RobotStates.ROBOT_ACK_CATCHED:
            print('robotTimerTimeout ROBOT_ACK_CATCHED')
            self.robotAckCatchError(robotNumber)
        elif timerDescriptor == RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH:
            self.ultraRobotAckError(RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH)
        elif timerDescriptor == RobotStates.ULTRA_ROBOT_ACK_INSERT:
            self.ultraRobotAckError(RobotStates.ULTRA_ROBOT_ACK_INSERT)
        elif timerDescriptor == RobotStates.ULTRA_ROBOT_ACK_CATCH:
            self.ultraRobotAckError(RobotStates.ULTRA_ROBOT_ACK_CATCH)
        else:
            print('robot in error state!')

    def checkCatchable(self):
        if (not self.isValidModule) \
                or self.detectAdapterTime > self.maxDetectAdapterTime \
                or self.detectAdapterTime == 0 \
                or self.isEmergencyStop:
            # print(self.isValidModule)
            return

        for i in range(0, self.robotNum, 1):
            if (self.moduleArrayState[self.robotModulePosition[i]] == ModuleStates.MODULE_ULTRASONIC
                or self.moduleArrayState[self.robotModulePosition[i]] == ModuleStates.MODULE_UNRECOGNIZE_ONCETIME) \
                    and self.robotArrayState[i] == RobotStates.ROBOT_WAITING \
                    and i != self.ultrasonicIndex:
                # print(str(i) + ' catchable')
                self.stopConveyor()
                self.sendOrderToRobot(i)

        if self.isUltraValid:
            self.checkUltraIsCatchable()
        pass

    def checkUltraIsCatchable(self):
        isCanCatch = False
        isCanInsert = False

        if self.robotArrayState[self.ultrasonicIndex] == RobotStates.ROBOT_WAITING and self.moduleArrayState[
            self.robotModulePosition[self.ultrasonicIndex]] == ModuleStates.MODULE_LOADED:
            isCanCatch = True

        if self.robotArrayState[self.ultrasonicIndex] == RobotStates.ROBOT_WAITING and self.moduleArrayState[
            self.robotModulePosition[self.ultrasonicIndex] + 1] == ModuleStates.MODULE_ULTRA1_CAUGHT:
            isCanInsert = True

        order = ''
        if isCanCatch:
            order += 'catch'
        if isCanInsert:
            order += 'insert'
        ultraRobotWorkState=-1
        if isCanInsert and isCanCatch:
            ultraRobotWorkState=RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH
            #self.robotArrayState[self.ultrasonicIndex] = RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH
            self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex]] = ModuleStates.MODULE_CATCHING
            self.robotTimer[self.ultrasonicIndex].setTimerDescriptor(self.ultrasonicIndex,
                                                                     RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH)
        elif isCanCatch:
            ultraRobotWorkState=RobotStates.ULTRA_ROBOT_ACK_CATCH
            #self.robotArrayState[self.ultrasonicIndex] = RobotStates.ULTRA_ROBOT_ACK_CATCH
            self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex]] = ModuleStates.MODULE_CATCHING
            self.robotTimer[self.ultrasonicIndex].setTimerDescriptor(self.ultrasonicIndex,
                                                                     RobotStates.ULTRA_ROBOT_ACK_CATCH)
        elif isCanInsert:
            ultraRobotWorkState=RobotStates.ULTRA_ROBOT_ACK_INSERT
            #self.robotArrayState[self.ultrasonicIndex] = RobotStates.ULTRA_ROBOT_ACK_INSERT
            #self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex]] = ModuleStates.MODULE_CATCHING
            self.robotTimer[self.ultrasonicIndex].setTimerDescriptor(self.ultrasonicIndex,
                                                                     RobotStates.ULTRA_ROBOT_ACK_INSERT)
        if isCanInsert or isCanCatch:
            self.sendOrderToUltra(order)
            self.robotTimer[self.ultrasonicIndex].start()
            if ultraRobotWorkState == -1:
                self.addRunMessage.emit('ultrasonic in a error state !')
            self.robotArrayState[self.ultrasonicIndex] = ultraRobotWorkState
            self.stopConveyor()
        self.updateRobotAndModuleState()

    def newSocketConnection(self):
        _socket = self.server.nextPendingConnection()
        _socketIp = _socket.peerAddress().toString()
        _socketIp = _socketIp.split(':')[-1]
        number = 0
        if _socketIp in self.robotsIp.values():
            for _ip in self.robotsIp.values():
                if _socketIp == _ip:
                    newRobotSocket = Socket()
                    newRobotSocket.setSocket(_socket)
                    newRobotSocket.setDescriptor(number)
                    self.addRobotSocket(number, newRobotSocket)
                    self.robotOnline(number)
                    newRobotSocket.receivedMsg.connect(self.robotReadMsg)
                    newRobotSocket.disconnected.connect(self.robotDisconnected)
                    break
                else:
                    number += 1
        else:
            _socket.close()
        pass

    def addRobotSocket(self, robotNumber, robotSocket):
        self.removeRobotSocket(robotNumber)
        self.robotSocketArray[robotNumber] = robotSocket
        if robotNumber == self.ultrasonicIndex:
            self.isUltraOnline = True
        else:
            self.onlineTestRobotNum += 1
            if robotNumber > self.lastOnlineTestRobotNumber:
                self.lastOnlineTestRobotNumber = robotNumber
        pass

    def removeRobotSocket(self, robotNumber):
        if robotNumber in self.robotSocketArray.keys():
            self.robotSocketArray.pop(robotNumber)
            if robotNumber == self.ultrasonicIndex:
                self.isUltraOnline = False
            else:
                self.onlineTestRobotNum -= 1
                if self.onlineTestRobotNum == 0:
                    self.lastOnlineTestRobotNumber = -1
                else:
                    self.lastOnlineTestRobotNumber = 0
                    for robotNumber in self.robotSocketArray.keys():
                        if robotNumber >= self.lastOnlineTestRobotNumber and robotNumber != self.ultrasonicIndex:
                            self.lastOnlineTestRobotNumber = robotNumber

        pass

    def robotReadMsg(self, robotNumber):
        msg = self.robotSocketArray[robotNumber].readMsg()
        self.processMsgFromRobot(robotNumber, msg)
        pass

    def robotDisconnected(self, robotNumber):
        self.robotOffline(robotNumber)

    def processMsgFromRobot(self, robotNumber, msg):
        msg=msg.replace('\n','')
        print(QDateTime.currentDateTime().toString('mm:ss:zzz')+' msg:'+msg)
        if msg == self.waitOrder:
            self.robotWaitting(robotNumber)
        elif msg == self.caughtOrder:
            self.robotCaught(robotNumber)
        elif msg == self.unrecognizedOrder:
            self.robotUnrecognized(robotNumber)
        elif msg == self.clearOrder:
            self.robotClear(robotNumber)
        elif msg == self.ultra1UnrecognizedOrder:
            self.ultraRobot1Unrecognized()
        elif msg == self.ultra2UnrecognizedOrder:
            self.ultraRobot2Unrecognized()
        elif msg == self.ultraCaughtOrder:
            self.ultraRobot1Caught()
        elif msg == self.ultraInsertedOrder:
            self.ultraRobot2Inserted()
        elif msg == self.ultraInsertedWaitOrder:
            self.ultraRobot2Inserted()
            self.robotWaitting(self.ultrasonicIndex)
        elif msg == self.ultraCaughtWaitOrder:
            self.ultraRobot1Caught()
            self.robotWaitting(self.ultrasonicIndex)
        else:
            self.addRunMessage.emit('received a error message from robot'+str(robotNumber)+':'+msg)
        pass

    def robotOnline(self, robotNumber):
        if robotNumber > self.robotNum - 1:
            exit(0)
        if robotNumber == self.ultrasonicIndex:
            self.ultrasonicRobotOnline()
        self.robotArrayState[robotNumber] = RobotStates.ROBOT_CONNECTED
        self.updateRobotAndModuleState()
        self.addRunMessage.emit('robot '+str(robotNumber)+' online')
        pass

    def robotOffline(self, robotNumber):
        # print(str(robotNumber)+'robotOffline')
        if self.robotArrayState[robotNumber] == RobotStates.ROBOT_ACK_CATCHED and robotNumber != self.ultrasonicIndex:
            self.robotAckCatchError(robotNumber)
            return
        if robotNumber == self.ultrasonicIndex:
            self.ultrasonicRobotOffline()
            return
        self.removeRobotSocket(robotNumber)
        self.robotArrayState[robotNumber] = RobotStates.ROBOT_OFFLINE
        self.updateRobotAndModuleState()
        self.addRunMessage.emit('robot ' + str(robotNumber) + ' offline')
        pass

    def robotWaitting(self, robotNumber):
        if self.robotArrayState[robotNumber] == RobotStates.ROBOT_ACK_CATCHED \
                or self.robotArrayState[robotNumber] == RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH \
                or self.robotArrayState[robotNumber] == RobotStates.ULTRA_ROBOT_ACK_INSERT \
                or self.robotArrayState[robotNumber] == RobotStates.ULTRA_ROBOT_ACK_CATCH:
            print('received a error wait order!')
            return
        self.robotArrayState[robotNumber] = RobotStates.ROBOT_WAITING
        self.updateRobotAndModuleState()
        pass

    def robotCatching(self, robotNumber):
        if self.moduleArrayState[self.robotModulePosition[robotNumber]] != ModuleStates.MODULE_UNRECOGNIZE_ONCETIME:
            self.moduleArrayState[self.robotModulePosition[robotNumber]] = ModuleStates.MODULE_CATCHING
        self.robotArrayState[robotNumber] = RobotStates.ROBOT_ACK_CATCHED

        self.robotTimer[robotNumber].setTimerDescriptor(robotNumber, RobotStates.ROBOT_ACK_CATCHED)
        self.robotTimer[robotNumber].start()
        self.updateRobotAndModuleState()
        pass

    def robotCaught(self, robotNumber):
        if self.robotArrayState[robotNumber] != RobotStates.ROBOT_ACK_CATCHED and self.robotArrayState[
            robotNumber] != RobotStates.ULTRA_ROBOT_ACK_CATCH and self.robotArrayState[
            robotNumber] != RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH:
            print('received a error Caught order!')
            return
        if robotNumber == self.ultrasonicIndex:
            self.ultraRobot1Caught()
        else:
            self.robotArrayState[robotNumber] = RobotStates.ROBOT_CATCHED
            self.moduleArrayState[self.robotModulePosition[robotNumber]] = ModuleStates.MODULE_EMPTY
            self.robotTimer[robotNumber].setTimerDescriptor(robotNumber, RobotStates.ROBOT_CATCHED)
            self.robotTimer[robotNumber].stop()
        self.updateRobotAndModuleState()
        pass

    def robotClear(self, robotNumber):
        if self.robotArrayState[robotNumber] == RobotStates.ROBOT_WAITING:
            self.robotArrayState[robotNumber] = RobotStates.ROBOT_CLEARING
        self.updateRobotAndModuleState()
        self.addRunMessage.emit('robot ' + str(robotNumber) + ' clear')

    def robotAckCatchError(self, robotNumber):
        self.moduleArrayState[self.robotModulePosition[robotNumber]] = ModuleStates.MODULE_ERROR
        self.robotArrayState[robotNumber] = RobotStates.ROBOT_ACK_CATCHED_ERROR
        self.robotTimer[robotNumber].stop()
        self.stopConveyor()
        self.removeRobotSocket(robotNumber)
        self.updateRobotAndModuleState()
        self.addRunMessage.emit('robot ' + str(robotNumber) + ' ack catch error')
        pass

    def robotUnrecognized(self, robotNumber):
        if self.robotArrayState[robotNumber] != RobotStates.ROBOT_ACK_CATCHED:
            return
        if self.moduleArrayState[self.robotModulePosition[robotNumber]] == ModuleStates.MODULE_UNRECOGNIZE_ONCETIME \
                or self.moduleArrayState[self.robotModulePosition[robotNumber]]:
            self.robotArrayState[robotNumber] = RobotStates.ROBOT_RECOGNIZE_ERROR
            if self.moduleArrayState[self.robotModulePosition[robotNumber]] == ModuleStates.MODULE_UNRECOGNIZE_ONCETIME:
                self.moduleArrayState[self.robotModulePosition[robotNumber]] = ModuleStates.MODULE_UNRECOGNIZE_TWICETIME
            else:
                self.moduleArrayState[self.robotModulePosition[robotNumber]] = ModuleStates.MODULE_UNRECOGNIZE_ONCETIME
        self.updateRobotAndModuleState()
        self.addRunMessage.emit('robot ' + str(robotNumber) + ' unrecognized')
        pass

    def detectedModule(self, newModuleState):
        for i in range(0, self.robotNum, 1):
            if self.robotArrayState[i] == RobotStates.ROBOT_RECOGNIZE_ERROR:
                self.robotArrayState[i] = RobotStates.ROBOT_WAITING
        if self.robotArrayState[self.ultrasonicIndex] == RobotStates.ULTRASONIC_ROBOT1_UNRECOGNIZED:
            self.robotArrayState[self.ultrasonicIndex] = RobotStates.ROBOT_WAITING

        sensorModulePrevState = self.moduleArrayState[self.moduleSensorPosition - 1]
        lastModuleState = self.moduleArrayState[self.moduleNum - 1]
        for i in range(self.moduleNum - 1, -1, -1):
            self.moduleArrayState[i] = self.moduleArrayState[i - 1]
        self.moduleArrayState[0] = lastModuleState

        if self.isUltraValid:
            if sensorModulePrevState == ModuleStates.MODULE_ULTRASONIC or sensorModulePrevState == ModuleStates.MODULE_UNRECOGNIZE_ONCETIME or sensorModulePrevState == ModuleStates.MODULE_UNRECOGNIZE_TWICETIME:
                if newModuleState == ModuleStates.MODULE_LOADED:
                    self.moduleArrayState[self.moduleSensorPosition] = ModuleStates.MODULE_ULTRASONIC
                elif newModuleState == ModuleStates.MODULE_EMPTY:
                    self.moduleArrayState[selfsetDescriptor.moduleSensorPosition] = ModuleStates.MODULE_EMPTY
            else:
                self.moduleArrayState[self.moduleSensorPosition] = newModuleState
        else:
            if newModuleState == ModuleStates.MODULE_LOADED:
                self.moduleArrayState[self.moduleSensorPosition] = ModuleStates.MODULE_ULTRASONIC
            elif newModuleState == ModuleStates.MODULE_EMPTY:
                self.moduleArrayState[self.moduleSensorPosition] = ModuleStates.MODULE_EMPTY

        self.checkIsActivateConveyor()
        self.checkCatchable()
        self.updateModulesState.emit()
        pass

    def ultraRobot1Caught(self):
        if self.robotArrayState[self.ultrasonicIndex] != RobotStates.ULTRA_ROBOT_ACK_CATCH \
                and self.robotArrayState[self.ultrasonicIndex] != RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH:
            print('received a error ultraRobot1Caught order!')
            return
        self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex]] = ModuleStates.MODULE_ULTRA1_CAUGHT
        if self.robotTimer[self.ultrasonicIndex].getTimerDescriptor() == RobotStates.ULTRA_ROBOT_ACK_CATCH:
            self.robotTimer[self.ultrasonicIndex].stop()
            self.robotArrayState[self.ultrasonicIndex] = RobotStates.ULTRA_ROBOT_WORKING
        elif self.robotTimer[self.ultrasonicIndex].getTimerDescriptor() == RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH:
            self.robotTimer[self.ultrasonicIndex].setTimerDescriptor(self.ultrasonicIndex,
                                                                     RobotStates.ULTRA_ROBOT_ACK_INSERT)
            self.robotArrayState[self.ultrasonicIndex] = RobotStates.ULTRA_ROBOT_ACK_INSERT
        self.updateRobotAndModuleState()
        pass

    def ultraRobot2Inserted(self):
        if self.robotArrayState[self.ultrasonicIndex] != RobotStates.ULTRA_ROBOT_ACK_INSERT \
                and self.robotArrayState[self.ultrasonicIndex] != RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH:
            print('received a error ultraRobot2Inserted order!')
            return
        if self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex] + 1] == ModuleStates.MODULE_ULTRA1_CAUGHT:
            self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex] + 1] = ModuleStates.MODULE_ULTRASONIC
            if self.robotTimer[self.ultrasonicIndex].getTimerDescriptor() == RobotStates.ULTRA_ROBOT_ACK_INSERT:
                self.robotTimer[self.ultrasonicIndex].stop()
                self.robotArrayState[self.ultrasonicIndex] = RobotStates.ULTRA_ROBOT_WORKING
            elif self.robotTimer[self.ultrasonicIndex].getTimerDescriptor() == RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH:
                self.robotTimer[self.ultrasonicIndex].setTimerDescriptor(self.ultrasonicIndex,
                                                                         RobotStates.ULTRA_ROBOT_ACK_CATCH)
        else:
            self.ultrasonicRobotOffline()
        self.updateRobotAndModuleState()
        pass

    def ultrasonicRobotOnline(self):
        if self.robotArrayState[self.ultrasonicIndex] == RobotStates.ULTRA_ROBOT_ACK_CATCH_INSERT_ERROR \
                or self.robotArrayState[self.ultrasonicIndex] == RobotStates.ULTRA_ROBOT_ACK_INSERT_ERROR:
            if self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex] + 1] == ModuleStates.MODULE_ERROR:
                self.moduleArrayState[
                    self.robotModulePosition[self.ultrasonicIndex] + 1] = ModuleStates.MODULE_ULTRASONIC
        self.updateRobotAndModuleState()
        pass

    def ultrasonicRobotOffline(self):
        if self.robotArrayState[self.ultrasonicIndex] == RobotStates.ULTRA_ROBOT_ACK_INSERT or self.robotArrayState[
            self.ultrasonicIndex] == RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH or self.robotArrayState[
            self.ultrasonicIndex] == RobotStates.ULTRA_ROBOT_ACK_CATCH:
            self.ultraRobotAckError(self.robotArrayState[self.ultrasonicIndex])
        self.robotArrayState[self.ultrasonicIndex] = RobotStates.ROBOT_OFFLINE
        self.removeRobotSocket(self.ultrasonicIndex)
        self.updateRobotAndModuleState()
        pass

    def ultraRobot1Unrecognized(self):
        if self.robotArrayState[self.ultrasonicIndex] != RobotStates.ULTRA_ROBOT_ACK_CATCH and self.robotArrayState[
            self.ultrasonicIndex] != RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH:
            print('received a error ultraRobot1Unrecognized order!')
            return
        self.robotArrayState[self.ultrasonicIndex] = RobotStates.ULTRASONIC_ROBOT1_UNRECOGNIZED
        self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex]] = ModuleStates.MODULE_ULTRA1_UNRECOGNIZED
        if self.robotTimer[self.ultrasonicIndex].getTimerDescriptor() == RobotStates.ULTRA_ROBOT_ACK_CATCH:
            self.robotTimer[self.ultrasonicIndex].stop()
        elif self.robotTimer[self.ultrasonicIndex].getTimerDescriptor() == RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH:
            self.robotTimer[self.ultrasonicIndex].setTimerDescriptor(self.ultrasonicIndex,
                                                                     RobotStates.ULTRA_ROBOT_ACK_INSERT)
        self.updateRobotAndModuleState()
        self.addRunMessage.emit('ultrasonic robot1 unrecognized')
        pass

    def ultraRobot2Unrecognized(self):
        if self.robotArrayState[self.ultrasonicIndex] != RobotStates.ULTRA_ROBOT_ACK_INSERT and self.robotArrayState[
            self.ultrasonicIndex] != RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH:
            print('received a error ultraRobot2Unrecognized order!')
            return
        if self.robotArrayState[self.ultrasonicIndex] != RobotStates.ULTRA_ROBOT_ACK_INSERT:
            self.robotTimer[self.ultrasonicIndex].stop()
        elif self.robotArrayState[self.ultrasonicIndex] != RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH:
            self.robotTimer[self.ultrasonicIndex].setTimerDescriptor(self.ultrasonicIndex,
                                                                     RobotStates.ULTRA_ROBOT_ACK_CATCH)
        self.moduleArrayState[
            self.robotModulePosition[self.ultrasonicIndex] + 1] = ModuleStates.MODULE_ULTRA2_UNRECOGNIZED
        self.updateRobotAndModuleState()
        self.addRunMessage.emit('ultrasonic robot2 unrecognized')
        pass

    def ultraRobotAckError(self, ultrasonicState):
        if ultrasonicState == RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH:
            self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex]] = ModuleStates.MODULE_ERROR
            self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex] + 1] = ModuleStates.MODULE_ERROR
            self.robotArrayState[self.ultrasonicIndex] = RobotStates.ULTRA_ROBOT_ACK_CATCH_INSERT_ERROR
        elif ultrasonicState == RobotStates.ULTRA_ROBOT_ACK_INSERT:
            self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex] + 1] = ModuleStates.MODULE_ERROR
            if self.moduleArrayState[
                self.robotModulePosition[self.ultrasonicIndex]] == ModuleStates.MODULE_ULTRA1_CAUGHT:
                self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex]] = ModuleStates.MODULE_ERROR
            self.robotArrayState[self.ultrasonicIndex] = RobotStates.ULTRA_ROBOT_ACK_INSERT_ERROR
        elif ultrasonicState == RobotStates.ULTRA_ROBOT_ACK_CATCH:
            self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex]] = ModuleStates.MODULE_ERROR
            if self.moduleArrayState[
                self.robotModulePosition[self.ultrasonicIndex] + 1] == ModuleStates.MODULE_ULTRA1_CAUGHT:
                self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex]] = ModuleStates.MODULE_ERROR
            self.robotArrayState[self.ultrasonicIndex] = RobotStates.ULTRA_ROBOT_ACK_CATCH_ERROR
        self.robotTimer[self.ultrasonicIndex].stop()
        self.stopConveyor()
        self.removeRobotSocket(self.ultrasonicIndex)
        self.updateRobotAndModuleState()
        self.addRunMessage.emit('ultrasonic robot ack error')
        pass

    def ultraRobot1InsertError(self):
        if self.robotArrayState[self.ultrasonicIndex] != RobotStates.ROBOT_WAITING:
            pass
        self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex]] = ModuleStates.MODULE_ERROR
        self.robotArrayState[self.ultrasonicIndex] = RobotStates.ULTRA_ROBOT_ACK_CATCH_ERROR

        self.robotTimer[self.ultrasonicIndex].stop()
        self.stopConveyor()
        self.removeRobotSocket(self.ultrasonicIndex)
        self.updateRobotAndModuleState()
        self.addRunMessage.emit('ultrasonic robot1 insert error')
        pass

    def detectModuleAndAdapter(self):
        if not self.isConveyorRunning:
            self.checkCatchable()

        self.currentModuleSensorState = self.gpioTool.getIOStatus(self.moduleSensor)
        # print('self.currentModuleSensorState:'+str(self.currentModuleSensorState))
        isHaveModule = self.currentModuleSensorState and self.prevModuleSensorState
        if (not self.isDetectFallingEdge) and (isHaveModule and self.isConveyorRunning):
            if not self.isEmergencyStop:
                self.detectAdapterTime += 1
            if self.detectAdapterTime < self.maxDetectAdapterTime and not self.isLoadAdapter:
                self.currentAdapterSensorState = self.gpioTool.getIOStatus(self.adapterSensor)
                # print('self.currentAdapterSensorState:'+str(self.currentAdapterSensorState))
                self.isLoadAdapter = self.currentAdapterSensorState and self.prevAdapterSensorState
                if self.isLoadAdapter:
                    if self.isProductTwoModel:
                        if not self.isStartDetect:
                            self.isStartDetect = True
                            self.isValidModule = True
                self.prevAdapterSensorState = self.currentAdapterSensorState
            elif self.detectAdapterTime >= self.maxDetectAdapterTime:
                if self.isProductTwoModel:
                    if self.isValidModule and self.isStartDetect and not self.isLoadAdapter:
                        self.detectedNewModule.emit(ModuleStates.MODULE_EMPTY)
                    elif self.isValidModule and self.isStartDetect and self.isLoadAdapter:
                        self.detectedNewModule.emit(ModuleStates.MODULE_LOADED)
                else:
                    if self.isLoadAdapter:
                        self.detectedNewModule.emit(ModuleStates.MODULE_LOADED)
                    else:
                        self.detectedNewModule.emit(ModuleStates.MODULE_EMPTY)

                self.isDetectFallingEdge = True
        if (self.isDetectFallingEdge and self.isConveyorRunning) or self.isEmergencyStop:
            isModuleLeave = not (self.prevModuleSensorState or self.currentModuleSensorState)
            if isModuleLeave:
                if self.isProductTwoModel:
                    self.isValidModule = not self.isValidModule
                self.isDetectFallingEdge = False
                self.isLoadAdapter = False
                self.prevAdapterSensorState = False
                self.detectAdapterTime = 0
        self.prevModuleSensorState = self.currentModuleSensorState
        self.checkIsActivateConveyor()
        pass

    def checkIsActivateConveyor(self):
        if self.onlineTestRobotNum == 0:
            self.stopConveyor()
            return

        if self.isUltraValid and (not self.isUltraOnline):
            self.stopConveyor()
            return

        if self.isUltraValid and self.robotArrayState[self.ultrasonicIndex] == RobotStates.ULTRA_ROBOT_ACK_CATCH \
                or self.robotArrayState[self.ultrasonicIndex] == RobotStates.ULTRA_ROBOT_ACK_INSERT \
                or self.robotArrayState[self.ultrasonicIndex] == RobotStates.ULTRA_ROBOT_ACK_INSERT_CATCH:
            if self.detectAdapterTime <= self.maxDetectAdapterTime and self.detectAdapterTime != 0:
                self.stopConveyor()
                return

        if self.robotArrayState[self.ultrasonicIndex] == RobotStates.ULTRA_ROBOT_ACK_CATCH_ERROR \
                or self.robotArrayState[self.ultrasonicIndex] == RobotStates.ULTRA_ROBOT_ACK_INSERT_ERROR \
                or self.robotArrayState[self.ultrasonicIndex] == RobotStates.ULTRA_ROBOT_ACK_CATCH_INSERT_ERROR:
            self.stopConveyor()
            return

        if self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex]+1] == ModuleStates.MODULE_ULTRA1_CAUGHT:
            self.stopConveyor()
            return

        if self.isStopLastInLastRobot:
            if self.moduleArrayState[self.robotModulePosition[self.lastOnlineTestRobotNumber]] == ModuleStates.MODULE_ULTRASONIC \
                    or (self.moduleArrayState[self.robotModulePosition[
                self.lastOnlineTestRobotNumber]] == ModuleStates.MODULE_UNRECOGNIZE_ONCETIME
                        and self.robotArrayState[self.lastOnlineTestRobotNumber] != RobotStates.ROBOT_RECOGNIZE_ERROR):
                if self.detectAdapterTime <= self.maxDetectAdapterTime and self.detectAdapterTime != 0:
                    self.stopConveyor()
                    return

        if self.moduleArrayState[self.robotModulePosition[self.ultrasonicIndex]] == ModuleStates.MODULE_LOADED:
            self.stopConveyor()
            return

        if self.isEmergencyStop:
            self.stopConveyor()
            return

        for i in range(0, self.robotNumber, 1):
            if i == self.ultrasonicIndex:
                continue
            if self.robotArrayState[i] == RobotStates.ROBOT_ACK_CATCHED_ERROR \
                    or self.robotArrayState[i] == RobotStates.ROBOT_ACK_CATCHED:
                self.stopConveyor()
                return

        self.activateConveyor()
        pass

    def clearError(self):
        self.clearAckCatchError()
        pass

    def clearAckCatchError(self):
        print('clearAckCatchError')
        for robotNumber in range(0, self.robotNum, 1):
            if self.robotArrayState[robotNumber] == RobotStates.ROBOT_ACK_CATCHED_ERROR:
                self.robotArrayState[robotNumber] = RobotStates.ROBOT_OFFLINE
        self.addRunMessage.emit('clear ack error')
        pass

    def resetConveyor(self):
        print('resetConveyor')
        for i in range(0, self.moduleNum, 1):
            if self.moduleArrayState[i] == ModuleStates.MODULE_ULTRASONIC:
                self.moduleArrayState[i] = ModuleStates.MODULE_EMPTY
        self.addRunMessage.emit('reset conveyor')
        pass

    def alterUltrasonicState(self, state):
        self.isUltraValid = state
        self.addRunMessage.emit('alter Ultrasonic State')
        print('isUltraValid:' + str(state))

    def alterLastRobotState(self, state):
        self.isStopLastInLastRobot = state
        self.addRunMessage.emit('alter Last Robot State')
        print('isStopLastInLastRobot:' + str(state))

    def alterCatchState(self, state):
        self.isOnlyCatch = state
        self.addRunMessage.emit('alter Catch State')
        print('isOnlyCatch:' + str(state))

    def manualControlConveyor(self,state):
        print('manualActivateConveyor')
        self.detectTimer.stop()
        self.closeServer()
        self.addRunMessage.emit('manual control conveyor')
        self.gpioTool.setIOStatus(self.conveyorIo, state)
        
    def closeScheduler(self):
        self.detectTimer.stop()
        self.closeServer()
        self.gpioTool.setIOStatus(self.conveyorIo, self.closeConveyorState)
