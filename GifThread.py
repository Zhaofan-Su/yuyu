from PyQt5.QtCore import QThread, pyqtSignal
import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication

class GifThread(QThread):

    def __init__(self,bg, parent=None):
        super(GifThread, self).__init__(parent)
        self.bg = bg
        

    def run(self):
        gif = QtGui.QMovie('./figures/fig.gif')
        self.bg.setMovie(gif)
        gif.setCacheMode(QtGui.QMovie.CacheAll)
        self.bg.setStyleSheet('background-color: transparent;')
        gif.start()
        while True:
            QApplication.processEvents()