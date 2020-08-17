from PyQt5 import QtNetwork
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import *
from  PyQt5.QtNetwork import QTcpSocket

class Socket(QObject):
    receivedMsg=pyqtSignal(int)
    disconnected=pyqtSignal(int)

    def __init__(self):
        super(Socket,self).__init__()
        pass

    def setSocket(self,sock):
        # print('set socket start')

        self.sock=sock
        self.sock.disconnected.connect(self.disconnectedFromServer)
        self.sock.readyRead.connect(self.receivedMsgFromServer)
        # print('set socket end')

    def setDescriptor(self,descriptor):
        self.descriptor=descriptor

    def readMsg(self):
        #print('read msg111111111')
        msg=str(self.sock.readLine(),encoding='utf-8')
        return msg

    def sendMsg(self,msg):
        self.sock.write(msg.encode('utf-8'))
        #self.sock.flush()
        if self.sock.waitForBytesWritten(1000):
            return True
        else:
            print('send data timeout!')
            return False

    def disconnectedFromServer(self):
        # print('test disconnect')
        self.disconnected.emit(self.descriptor)
        # print('test disconnect1111111111111')

    def receivedMsgFromServer(self):
        self.receivedMsg.emit(self.descriptor)



