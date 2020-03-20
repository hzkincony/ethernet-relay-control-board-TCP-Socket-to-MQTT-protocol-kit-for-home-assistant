from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from HADemo import *
from ConnectManager import *
from MyWidgets import *

class HADemoL(Ui_HADemo, QWidget):

    def __int__(self):
        super(HADemoL, self).__init__()
        return

    def setupUi(self, HADemo):
        super().setupUi(HADemo)

        self.leDeviceIp.setText("192.168.1.200")
        self.leDevicePort.setText("4196")

        self.leMQTTIp.setText("127.0.0.1")
        self.leMQTTPort.setText("1883")

        parents = [self.gb1, self.gb2, self.gb3, self.gb4]
        group = 0
        for cureent in parents:
            gridLayout = QtWidgets.QGridLayout(cureent)
            for index in range(1, 9):
                label = QLabel(cureent)
                label.setText("Relay %d" % (group * 8 + index))
                swButton = SwitchButton(cureent)
                swButton.setObjectName("SWButton" + str(index))
                swButton.setFixedHeight(30)
                swButton.setFixedWidth(48)
                gridLayout.addWidget(label, (index - 1) // 2, ((index - 1) % 2) * 2, 1, 1)
                gridLayout.addWidget(swButton, (index - 1)// 2, ((index - 1) % 2) * 2 + 1, 1, 1)
            group += 1

        for index in range(1, 9):
            pbInput = QPushButton(self.gbInput)
            pbInput.setObjectName("Input_%d" % index)
            self.glInput.addWidget(pbInput, (index - 1) // 4, (index - 1) % 4, 1, 1)
            pbInput.setText("Input C%d" % index)

            pal = pbInput.palette()
            pal.setColor(QPalette.ButtonText, Qt.white)
            pbInput.setPalette(pal);
            pbInput.setStyleSheet("background-color:gray")

        self.rbH32.click()


    def changeDeviceType(self):
        if self.sender().text() == "KC868-H2":
            self.gb1.setEnabled(True)
            self.gb2.setEnabled(False)
            self.gb3.setEnabled(False)
            self.gb4.setEnabled(False)
            for index in range(1, 9):
                swbutton = self.gb1.findChild(SwitchButton, "SWButton%d" % index)
                if index < 3:
                    swbutton.setEnabled(True)
                else:
                    swbutton.setEnabled(False)

            for index in range(1, 9):
                pbInput = self.gbInput.findChild(QPushButton, "Input_%d" % index)
                pbInput.setEnabled(False)

        elif self.sender().text() == "KC868-H4":
            self.gb1.setEnabled(True)
            self.gb2.setEnabled(False)
            self.gb3.setEnabled(False)
            self.gb4.setEnabled(False)
            for index in range(1, 9):
                swbutton = self.gb1.findChild(SwitchButton, "SWButton%d" % index)
                if index < 5:
                    swbutton.setEnabled(True)
                else:
                    swbutton.setEnabled(False)

            for index in range(1, 9):
                if index < 5:
                    pbInput = self.gbInput.findChild(QPushButton, "Input_%d" % index)
                    pbInput.setEnabled(True)
                else:
                    pbInput = self.gbInput.findChild(QPushButton, "Input_%d" % index)
                    pbInput.setEnabled(False)

        elif self.sender().text() == "KC868-H8":
            self.gb1.setEnabled(True)
            self.gb2.setEnabled(False)
            self.gb3.setEnabled(False)
            self.gb4.setEnabled(False)
            for index in range(1, 9):
                swbutton = self.gb1.findChild(SwitchButton, "SWButton%d" % index)
                swbutton.setEnabled(True)

            for index in range(1, 9):
                pbInput = self.gbInput.findChild(QPushButton, "Input_%d" % index)
                pbInput.setEnabled(True)

        elif self.sender().text() == "KC868-H16":
            self.gb1.setEnabled(True)
            self.gb2.setEnabled(True)
            self.gb3.setEnabled(False)
            self.gb4.setEnabled(False)
            for index in range(1, 9):
                swbutton = self.gb1.findChild(SwitchButton, "SWButton%d" % index)
                swbutton.setEnabled(True)

            for index in range(1, 9):
                pbInput = self.gbInput.findChild(QPushButton, "Input_%d" % index)
                pbInput.setEnabled(True)

        elif self.sender().text() == "KC868-H32":
            self.gb1.setEnabled(True)
            self.gb2.setEnabled(True)
            self.gb3.setEnabled(True)
            self.gb4.setEnabled(True)
            for index in range(1, 9):
                swbutton = self.gb1.findChild(SwitchButton, "SWButton%d" % index)
                swbutton.setEnabled(True)

            for index in range(1, 9):
                if index < 7:
                    pbInput = self.gbInput.findChild(QPushButton, "Input_%d" % index)
                    pbInput.setEnabled(True)
                else:
                    pbInput = self.gbInput.findChild(QPushButton, "Input_%d" % index)
                    pbInput.setEnabled(False)

    def sendCommand(self, command, target, topic=None):
        if type(command) == dict:
            self.pteCommand.appendPlainText(target + " || " + json.dumps(command))
            self.ConnectManager.sendCommand(command, target, topic)
        else:
            self.pteCommand.appendPlainText(target + " || " + command)
            self.ConnectManager.sendCommand(command.encode(), target, topic)

    def connect(self):
        self.deviceIp = self.leDeviceIp.text().replace(".", "")
        self.devicePort = self.leDevicePort.text()

        self.ConnectManager = ConnectManager(self.leDeviceIp.text(), self.leDevicePort.text(), self.leMQTTIp.text(),
                                             self.leMQTTPort.text())
        self.ConnectManager.receiveNewReportSignal.connect(self.reportProcess)
        self.ConnectManager.statusChangedSignal.connect(self.connectorStatusChanged)


        print("device/%s/%s/set" % (self.deviceIp, self.devicePort))
        self.ConnectManager.subscribe("device/%s/%s/set" % (self.deviceIp, self.devicePort))

        # Read the input status after connecting the device
        self.sendCommand("RELAY-GET_INPUT-255", "DEVICE")
        time.sleep(1)
        self.sendCommand("RELAY-STATE-255", "DEVICE")


    def reportProcess(self, command, source):
        self.pteCommand.appendPlainText(source + " || " + command)
        if source == "MQTT":
            ctype, relayno, state = command.split(",")
            statereport = {'ctype': ctype, 'relayno_%s' % relayno: {'state': int(state)}}

            relayno = int(relayno)
            group = (relayno - 1) // 8 + 1
            relayno = (relayno - 1) % 8 + 1

            currentgroup = self.centralwidget.findChild(QGroupBox, ("gb%d" % group))
            currentrelay = currentgroup.findChild(SwitchButton, "SWButton%d" % relayno)
            currentrelay.setSwitchState(int(state))
            self.sendCommand(command, "DEVICE")
        elif source == "DEVICE":
            # ALARM
            if command[0: 11] == "RELAY-ALARM":
                # feedback
                #self.sendCommand((command + ",OK"), "DEVICE")
                # Read input state
                self.sendCommand("RELAY-GET_INPUT-255", "DEVICE")
            elif command[0: 19] == "RELAY-GET_INPUT-255":
                ctype, state, ok = command.split(",")
                if ok[0: 2] == "OK":
                    for inputC in range(1, 9):
                        pbInput = self.gbInput.findChild(QPushButton, "Input_%d" % inputC)
                        if pbInput.isEnabled():
                            pal = pbInput.palette()
                            pbInput.setPalette(pal)
                            if 1 << (inputC - 1) & int(state) > 0:
                                pbInput.setStyleSheet("background-color:green")
                            else:
                                pbInput.setStyleSheet("background-color:red")
                else:
                    print("Device Abnormal")
            elif command[0: 15] == "RELAY-STATE-255":
                commandLists = command.split(",")
                groups = len(commandLists) - 2
                for commandIndex in range(1, groups + 1):
                    state = int(commandLists[commandIndex])
                    curGroup = groups - commandIndex + 1
                    curGroupBox = self.gbOutput.findChild(QGroupBox, "gb%d" % curGroup)

                    for relayIndex in range(1, 9):
                        swButton = curGroupBox.findChild(SwitchButton, "SWButton%d" % relayIndex)
                        curState = 1 << (relayIndex - 1) & int(state)
                        if curState > 0:
                            swButton.setSwitchState(True)

                        else:
                            swButton.setSwitchState(False)

                        statereport = {'ctype': 'RELAY-SET-255', 'relayno_%s' % ((curGroup - 1) * 8 + relayIndex): {'state': curState}}
                        self.sendCommand(statereport, "MQTT",
                                                        "device/%s/%s/state" % (self.deviceIp, self.devicePort))
            else:
                ctype, relayno, state, ok = command.split(",")
                if ok[0: 2] == "OK":
                    statereport = {'ctype': ctype, 'relayno_%s' % relayno: {'state': int(state)}}
                    self.sendCommand(statereport, "MQTT", "device/%s/%s/state" % (self.deviceIp, self.devicePort))
                else:
                    print("Device Abnormal")

    def connectorStatusChanged(self, status):
        if status:
            self.statusbar.showMessage("MQTT Server %s:%s  Connect Success!" % (self.leMQTTIp.text(), self.leMQTTPort.text()))

