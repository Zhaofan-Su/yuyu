import cv2
from PyQt5 import  QtGui, QtWidgets
from PyQt5.Qt import QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from screen_ui import Ui_MainWindow
import time
import os
import numpy as np
from CameraThread import CameraThread
from PyQt5.QtWidgets import QApplication
from PicThread import PicThread
import font_rc
from PyQt5.QtGui import QFontDatabase, QFont, QImage, QPixmap
from PyQt5.QtCore import QTimer

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None) -> None:
        super(MainWindow, self).__init__(parent)
        
        
        self.setupUi(self)

        self.setWindowStyle()
        
        self.labels = {}
        for i in range(1, 14):
            self.labels[f'screen_{i}'] = getattr(self, f'screen_{i}')
            if i == 10:
                continue
            getattr(self, f'screen_{i}_No').setFont(QFont('FZXS12'))
            # vertical-align:bottom; 
            getattr(self, f'screen_{i}_No').setStyleSheet('color: white; font-size:35px;background-color: transparent;border-bottom:2px solid white;')
            getattr(self, f'screen_{i}_time').setStyleSheet('color: white; font-weight:bold; font-size:13px;background-color: transparent;')
            getattr(self, f'screen_{i}_time').setFont(QFont('FZXS12'))
            self.labels[f'screen_{i}_No'] = getattr(self, f'screen_{i}_No')
            self.labels[f'screen_{i}_time'] = getattr(self, f'screen_{i}_time')

        self.picThread = None

        
        # 字体设置
        fontDb = QFontDatabase()
        fontID = fontDb.addApplicationFont(":resources/figures/方正像素12.TTF")
        fontFamilies = fontDb.applicationFontFamilies(fontID)
        self.setFont(QFont('FZXS12'))

        # 本地视频
        self.showLocals()
    
        # 实时视频播放器
        self.currentFrame = None
        self.executor = None
        self.shootTime = None
        self.imgFolder = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        os.mkdir(f'./{self.imgFolder}')
        self.cameraThread = CameraThread(self.screen_17, self.imgFolder)
        self.cameraThread.signal.connect(self.Change)
        self.cameraThread.start()
        
               
        # # 静态视频播放器，控制screen_14、15、16，废代码
        # self.player_14 = QMediaPlayer()
        # self.playlist_14 = QMediaPlaylist()
        # self.player_15 = QMediaPlayer()
        # self.playlist_15 = QMediaPlaylist()
        # self.player_16 = QMediaPlayer()
        # self.playlist_16 = QMediaPlaylist()
        # self.showLocalVideos()
    
    def open_vedios(self):
        self.cap_14 = cv2.VideoCapture('./figures/14.avi')
        self.cap_15 = cv2.VideoCapture('./figures/15.avi')
        self.cap_16 = cv2.VideoCapture('./figures/16.avi')
        self.timer_14 = QTimer()
        self.timer_15 = QTimer()
        self.timer_16 = QTimer()

    def open_frame(self, cap, timer, video_label):
        ret, image = cap.read()
        if ret:
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                vedio_img = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
            elif len(image.shape) == 1:
                vedio_img = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Indexed8)
            else:
                vedio_img = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)

            video_label.setPixmap(QPixmap(vedio_img))
            video_label.setScaledContents(True)  # 自适应窗口
        else:
            cap.release()
            timer.stop()

    def showLocals(self):
        self.open_vedios()
        self.timer_14.start(100)
        self.timer_14.timeout.connect(lambda: self.open_frame(self.cap_14, self.timer_14, self.screen_14))

        self.timer_15.start(100)
        self.timer_15.timeout.connect(lambda: self.open_frame(self.cap_15, self.timer_15, self.screen_15))

        self.timer_16.start(100)
        self.timer_16.timeout.connect(lambda: self.open_frame(self.cap_16, self.timer_16, self.screen_16))



    def Change(self, imgList, whetherShoot):
        QApplication.processEvents()
        if whetherShoot:
            self.picThread = PicThread(self.labels, self.imgFolder, imgList)
            self.picThread.finished.connect(self.quitPic)
            self.picThread.start()

    def quitPic(self):
        self.picThread.quit()
    
    def setWindowStyle(self) -> None:
        self.setStyleSheet("background-color: black;")
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        QtWidgets.QShortcut(QtGui.QKeySequence('Esc', ), self, self.close)
        
    
        
    # def showLocalVideos(self) -> None:
    #     for i in range(14, 17):
    #         player = getattr(self, f'player_{i}')
    #         player.setVideoOutput(getattr(self, f'screen_{i}'))
    #         playlist = getattr(self, f'playlist_{i}')
    #         playlist.addMedia(QMediaContent(QUrl(f'./figures/{i}.avi')))
    #         playlist.setCurrentIndex(0)
    #         playlist.setPlaybackMode(QMediaPlaylist.Loop)
    #         player.setPlaylist(playlist)
    #         player.play()
    #         print(f'the {i}th local video start')
            
   
    def closeEvent(self, event):
        # self.cameraThread.stop()
        # self.cap.release()
        self.cameraThread.quit()
        event.ignore()
        event.accept()
        

        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 获取形状以及长宽
        img_shape = gray_img.shape
        height, width = img_shape[0], img_shape[1]
        size = gray_img.size
        # 灰度图的直方图
        hist = cv2.calcHist([gray_img], [0], None, [256], [0, 256])
    
        # 计算灰度图像素点偏离均值(128)程序
        a = 0
        ma = 0
        reduce_matrix = np.full((height, width), 128)
        shift_value = gray_img - reduce_matrix
        shift_sum = sum(map(sum, shift_value))
    
        da = shift_sum / size
    
        # 计算偏离128的平均偏差
        for i in range(256):
            ma += (abs(i-128-da) * hist[i])
        m = abs(ma / size)
        # 亮度系数
        k = abs(da) / m
        # print(f'亮度系数{k}')
        return k[0]
        # if k[0] > 1:
        #     # 过亮
        #     if da > 0:
        #         print(f"亮度系数：{k}, 过亮")
        #     else:
        #         print(f"亮度系数：{k}, 过暗")
        # else:
        #     print(f"亮度系数：{k}, 亮度正常")