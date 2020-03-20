import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiSubWindow
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSettings
from HADemoL import *

if __name__ == '__main__':
    '''
    Main
    '''
    app = QApplication(sys.argv)
    app.setOrganizationName("AimingSun")
    app.setApplicationName("AutoPrinter")
    ui = HADemoL()
    mainWindow = QtWidgets.QMainWindow()
    #splash = QtWidgets.SplashScreen()
    #splash.effect()
    app.processEvents()
    ui.setupUi(mainWindow)

    settings = QSettings("AutoPrinter", "Genernal")
    try:
        pass
        #mainWindow.restoreGeometry(settings.value("geometry", ""))
        #mainWindow.restoreState(settings.value("windowState", ""))
    except:
        pass
    mainWindow.show()
    #splash.finish(mainWindow)
    sys.exit(app.exec_())