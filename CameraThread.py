from PyQt5.QtCore import QThread, pyqtSignal
import cv2
from PyQt5.QtGui import QImage
from PyQt5 import QtGui
import time
import numpy as np

class CameraThread(QThread):
    signal = pyqtSignal(list, bool)

    def __init__(self, screen, imgFolder, parent=None):
        super(CameraThread, self).__init__(parent)
        self.cap = None
        self.shootTime = None
        self.currentTime = None
        self.screen_17 = screen
        self.width = self.screen_17.width()
        self.height = self.screen_17.height()

        # 照片计数器
        self.imgFolder = imgFolder
        self.currentImg = 0
        self.allImgs = 0
        self.imgList = []


    def run(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1920)
        self.cap.set(4, 1080)

        while self.cap.isOpened():
            
            success, frame = self.cap.read()
            
            # RGB转BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            #中间可以放一些操作视频的代码，比如放大、变换颜色或者放深度学习中提取目标的代码
            frame=cv2.resize(frame,(self.width, self.height),interpolation=cv2.INTER_CUBIC)
            frame1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame1, frame1.shape[1], frame1.shape[0], frame1.strides[0], QImage.Format_RGB888).rgbSwapped()
            img_temp = image.copy()
            pixmap = QtGui.QPixmap.fromImage(img_temp)
            self.screen_17.setPixmap(pixmap)
            
            # 亮度系数
            k = self.checkBright(frame)
            now = time.time()
            # if k > 4:
            print(k)
            if True:
                
                if self.shootTime == None:
                    self.shoot(frame1)
                    self.signal.emit(self.imgList, True)
                    self.shootTime = time.time()
                elif (now - self.shootTime) >= 1:
                    self.shoot(frame1)
                    self.signal.emit(self.imgList, True)
                    self.shootTime = now
            else:
                self.shootTime = None
                self.signal.emit([], False)


    def shoot(self, img) -> None:
        self.allImgs += 1 
        img_name = f'./{self.imgFolder}/{self.allImgs}.png'
        cv2.imwrite(img_name, img)
        self.pushImg(self.allImgs)
    
    def pushImg(self, imgindex) -> None:
        if len(self.imgList) < 13:
            self.imgList.append(imgindex)
        else:
            self.imgList.pop(0)
            self.imgList.append(imgindex)
    
    def checkBright(self, img) -> float:
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