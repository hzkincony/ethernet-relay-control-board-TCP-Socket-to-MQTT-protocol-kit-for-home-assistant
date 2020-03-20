from PyQt5 import QtCore
import re
import json
import random
import hashlib
import urllib
import http
import shutil
import sys
import os
import subprocess
import re
import socket
import paho.mqtt.client as mqtt

class TCPConnector(QtCore.QThread):
    receiveNewReportSignal = QtCore.pyqtSignal(str, str)

    def __init__(self, ip, port):
        super(TCPConnector, self).__init__()
        #self.ip = ip
        #self.port = int(port)
        self.connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Non blocking mode
        #self.UdpReceiver.setblocking(False)
        self.connector.connect((ip, port))

    def sendCommand(self, command):
        self.connector.send(command)

    def start(self):
        super(TCPConnector, self).start()

    def run(self):
        while True:
            try:
                data = self.connector.recv(500)
                message = data.decode()
                self.receiveNewReportSignal.emit(message, "DEVICE")
            except:
                continue

class MQTTConnector(QtCore.QThread):
    statusChangedSignal = QtCore.pyqtSignal(bool)
    receiveNewReportSignal = QtCore.pyqtSignal(str, str)

    def __init__(self, ip, port):
        super(MQTTConnector, self).__init__()
        self.ip = ip
        self.port = int(port)

        #self.connector = mqtt.Client(client_id="HADemo019", clean_session=True)
        self.connector = mqtt.Client()
        self.connector.on_connect = self.on_connect
        self.connector.on_disconnect = self.on_disconnect
        self.connector.on_message = self.on_message
        self.connectStatus = False
        self.connected = False
        self.subscribedTopics = list()

    def on_connect(self, client, userdata, flags, rc):
        # Called when "broker" responds to our request，“flags” is a dictionary containing "broker" response parameters: flags['session present']
        # –This flag is set to "0" only for clean sessions，if set session = 0, Used to determine whether the client reconnects to the previous "broker" and still saves the previous session information，if set = 1，Session always exists.“rc”Used to determine whether the connection is successful:

        # 0: connection successful
        # 1: connection failed - Incorrect protocol version
        # 2: connection failed - Invalid client identifier
        # 3: connection failed - Server not available
        # 4: connection failed - Wrong user name or password
        # 5: connection failed - Unauthorized
        # 6 - 255: Undefined.
        self.connectStatus = True
        for topic in self.subscribedTopics:
            self.connector.subscribe(topic)
        self.statusChangedSignal.emit(True)

    def on_disconnect(self, client, userdata, rc):
        try:
            self.connector.reconnect()
        except:
            self.connectStatus = False
            self.statusChangedSignal.emit(False)

    def sendCommand(self, command, topic):
        self.connector.publish(topic, json.dumps(command).encode(), qos=1)

    def on_message(self, client, userdata, msg):
        self.receiveNewReportSignal.emit(msg.payload.decode(), "MQTT")

    def subscribe(self, topic):
        self.connector.subscribe(topic, 1)
        self.subscribedTopics.append(topic)

    def unsubscribe(self, topic):
        self.connector.unsubscribe(topic)
        self.subscribedTopics.remove(topic)

    def start(self):
        super(MQTTConnector, self).start()

    def run(self):
        while True:
            if self.connected:
                import time
                time.sleep(2)
            else:
                try:
                    self.connector.connect(self.ip, self.port, 60)
                    self.connector.loop_start()
                    self.connected = True
                except:
                    print(sys.exc_info())
                    self.statusChangedSignal.emit(False)

class ConnectManager(QtCore.QObject):
    statusChangedSignal = QtCore.pyqtSignal(bool)
    receiveNewReportSignal = QtCore.pyqtSignal(str, str)

    def __init__(self, deviceIp, devicePort, mqttIp, mqttPort):
        super(ConnectManager, self).__init__()
        self.mqttIp = mqttIp
        self.mqttPort = int(mqttPort)

        self.TCPConnector = TCPConnector(deviceIp, int(devicePort))
        self.TCPConnector.receiveNewReportSignal.connect(self.reportProcess)
        self.TCPConnector.start()
        self.MQTTConnectStatus = False

        self.MQTTConnector = MQTTConnector(self.mqttIp, int(self.mqttPort))
        self.MQTTConnector.receiveNewReportSignal.connect(self.reportProcess)
        self.MQTTConnector.statusChangedSignal.connect(self.mqttStatusChanged)
        self.MQTTConnector.start()

    def reportProcess(self, reports, source):
        self.receiveNewReportSignal.emit(reports, source)

    def sendCommand(self, command, target, topic=None):
        if target == "DEVICE":
            self.TCPConnector.sendCommand(command)
        else:
            self.MQTTConnector.sendCommand(command, topic)

    def subscribe(self, topic):
        self.MQTTConnector.subscribe(topic)

    def unsubscribe(self, topic):
        self.MQTTConnector.unsubscribe(topic)

    def mqttStatusChanged(self, status):
        self.MQTTConnectStatus = status
        self.statusChangedSignal.emit(status)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__[item]

