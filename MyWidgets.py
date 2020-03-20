import os
from PyQt5 import QtCore, QtGui, QtWidgets, QtWinExtras
from PyQt5.QtGui import QIcon, QDrag
from PyQt5.QtWidgets import *
from PyQt5.QtCore import (QByteArray, QDataStream, QIODevice, QMimeData, QSettings,
        QPoint, QSize, Qt, QModelIndex)
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import re
import time
from enum import Enum

class MyMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)

    def closeEvent(self, event):
        result = QtWidgets.QMessageBox.question(self,
                                            "Exit OK?...",
                                            "Exit OK,OK?",
                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            # Before closing the main window, close all sub windows to touch "CloseEvent" of the sub window
            #mdiarea = self.findChildren(QMdiArea)
            #for i in range(0, len(mdiarea[0].findChildren(QMdiSubWindow))):
            #    mdiarea[0].findChildren(QMdiSubWindow)[i].close()

            # save window geometry and state
            settings = QSettings("AimingSun", "BillingAssistant")
            settings.setValue("geometry", self.saveGeometry())
            settings.setValue("windowState", self.saveState())
            event.accept()

    def resizeEvent(self, event):
        pass
        #self.width = self.height * 2
        #self.setGeometry()

class ButtonStyle(Enum):
    ButtonStyle_Rect = 0
    ButtonStyle_CircleIn = 1
    ButtonStyle_CircleOut = 2

def qMin(a, b):
    if a < b:
        return a
    else:
        return b

class SwitchButton(QWidget):
    # Define clicked
    clicked = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super(SwitchButton, self).__init__(parent)
        self.setAttribute()
        # Timer
        from PyQt5.QtCore import QTimer
        self.timer = QTimer()

    def setAttribute(self, space=2, rectRadius=5, checked=False, showText=True, showCircle=False, animation=True,
                     buttonStyle=ButtonStyle(0), bgColorOff=QColor(125, 125, 125), bgColorOn=QColor(75, 100, 200),
                     sliderColorOff=QColor(255, 255, 255), sliderColorOn=QColor(255, 255, 255), textColorOff=QColor(255, 255, 255),
                     textColorOn=QColor(255, 255, 255), textOff="Off", textOn="On", step=1, startX=1, endX=0):
        self.space = space
        self.rectRadius = rectRadius
        self.checked = checked
        self.showText = showText
        self.showCircle = showCircle
        self.animation = animation
        self.buttonStyle = buttonStyle
        self.bgColorOff = bgColorOff
        self.bgColorOn = bgColorOn
        self.sliderColorOff = sliderColorOff
        self.sliderColorOn = sliderColorOn
        self.textColorOff = textColorOff
        self.textColorOn = textColorOn
        self.textOff = textOff
        self.textOn = textOn
        self.step = step
        self.startX = startX
        self.endX = endX

    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.checked = not self.checked
            self.update()
            self.clicked.emit()

    def setSwitchState(self, status, trigger=True):
        self.checked = status
        self.update()
        if trigger:
            self.clicked.emit()

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        self.drawBg(painter)
        self.drawSlider(painter)

    def drawBg(self, painter):
        painter.save()
        painter.setPen(Qt.NoPen)

        if self.checked:
            bgColor = self.bgColorOn
        else:
            bgColor = self.bgColorOff

        if not self.isEnabled():
            bgColor.setAlpha(60)

        painter.setBrush(bgColor)

        if self.buttonStyle == ButtonStyle.ButtonStyle_Rect:
            painter.drawRoundedRect(self.rect(), self.rectRadius, self.rectRadius)
        elif self.buttonStyle == ButtonStyle.ButtonStyle_CircleIn:
            rect = QtCore.QRect(0, 0, self.width(), self.height())
            # Radius is half of height
            side = qMin(rect.width(), rect.height())

            # Left circle
            path1 = QPainterPath()
            path1.addEllipse(rect.x(), rect.y(), side, side)
            # Right circle
            path2 = QPainterPath()
            path2.addEllipse(rect.width() - side, rect.y(), side, side)
            # Middle rectangle
            path3 = QPainterPath()
            path3.addRect(rect.x() + side / 2, rect.y(), rect.width() - side, rect.height())

            path = path3 + path1 + path2;
            painter.drawPath(path)
        elif self.buttonStyle == ButtonStyle.ButtonStyle_CircleOut:
            rect = QtCore.QRect(self.height() / 2, self.space, self.width() - self.height(), self.height() - self.space * 2)
            painter.drawRoundedRect(rect, self.rectRadius, self.rectRadius)

        if self.buttonStyle == ButtonStyle.ButtonStyle_Rect or self.buttonStyle == ButtonStyle.ButtonStyle_CircleIn:
            # Drawing text and small circles, mutually exclusive
            if self.showText:
                sliderWidth = qMin(self.width(), self.height()) - self.space * 2
                if self.buttonStyle == ButtonStyle.ButtonStyle_Rect:
                    sliderWidth = self.width() / 2 - 5
                elif self.buttonStyle == ButtonStyle.ButtonStyle_CircleIn:
                    sliderWidth -= 5

                if self.checked:
                    textRect = QtCore.QRect(0, 0, self.width() - sliderWidth, self.height())
                    painter.setPen(self.textColorOn)
                    painter.drawText(textRect, Qt.AlignCenter, self.textOn)
                else:
                    textRect = QtCore.QRect(sliderWidth, 0, self.width() - sliderWidth, self.height())
                    painter.setPen(self.textColorOff)
                    painter.drawText(textRect, Qt.AlignCenter, self.textOff)
            elif self.showCircle:
                side = qMin(self.width(), self.height()) / 2;
                y = (self.height() - side) / 2

                if self.checked:
                    circleRect= QtCore.QRect(side / 2, y, side, side)
                    pen = QPen(self.textColorOn, 2)
                    painter.setPen(pen)
                    painter.setBrush(Qt.NoBrush)
                    painter.drawEllipse(circleRect)
                else:
                    circleRect = QtCore.QRect(self.width() - (side * 1.5), y, side, side)
                    pen = QPen(self.textColorOff, 2)
                    painter.setPen(pen)
                    painter.setBrush(Qt.NoBrush)
                    painter.drawEllipse(circleRect)
        painter.restore()

    def drawSlider(self, painter):
        painter.save()
        painter.setPen(Qt.NoPen)

        if self.checked:
            painter.setBrush(self.sliderColorOn)
        else:
            painter.setBrush(self.sliderColorOff)

        if self.buttonStyle == ButtonStyle.ButtonStyle_Rect:
            sliderWidth = self.width() / 2 - self.space * 2
            sliderHeight = self.height() - self.space * 2
            if self.checked:
                sliderRect = QtCore.QRect(self.width() / 2 + self.startX + self.space, self.space, sliderWidth, sliderHeight)
            else:
                sliderRect = QtCore.QRect(self.startX + self.space, self.space, sliderWidth, sliderHeight)
            painter.drawRoundedRect(sliderRect, self.rectRadius, self.rectRadius)
        elif self.buttonStyle == ButtonStyle.ButtonStyle_CircleIn:
            rect = QtCore.QRect(0, 0, self.width(), self.height())
            sliderWidth = qMin(rect.width(), rect.height()) - self.space * 2
            sliderRect = QtCore.QRect(self.startX + self.space, self.space, sliderWidth, sliderWidth)
            painter.drawEllipse(sliderRect)
        elif self.buttonStyle == ButtonStyle.ButtonStyle_CircleOut:
            sliderWidth = self.height()
            sliderRect = self.QRect(self.startX, 0, sliderWidth, sliderWidth)

            radialGradient = QRadialGradient(sliderRect.center(), sliderWidth / 2)
            if self.checked:
                color1 = self.bgColorOn
                color2 = self.sliderColorOn
                radialGradient.setColorAt(0, color1)
                radialGradient.setColorAt(0.5, color1)
                radialGradient.setColorAt(0.6, color2)
                radialGradient.setColorAt(1.0, color2)
            else:
                color1 = self.bgColorOff
                color2 = self.sliderColorOff
                radialGradient.setColorAt(0, color2)
                radialGradient.setColorAt(0.5, color2)
                radialGradient.setColorAt(0.6, color1)
                radialGradient.setColorAt(1.0, color1)
            painter.setBrush(radialGradient);
            painter.drawEllipse(sliderRect);
        painter.restore()

class MyGroupBox(QGroupBox):
    # Define clicked
    doubleClicked = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super(MyGroupBox, self).__init__(parent)

    def mouseDoubleClickEvent(self, *args, **kwargs):
        self.doubleClicked.emit()
        #return super(MyGroupBox, self).mouseDoubleClickEvent(args, kwargs)

