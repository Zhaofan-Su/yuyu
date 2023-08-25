from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
from PyQt5 import QtGui
from datetime import datetime
import time
import os

class PicThread(QThread):
    # signal = pyqtSignal(list, bool)
    finished = pyqtSignal(bool)
    def __init__(self, label_dict:dict, imgFolder, imgList, parent=None):
        super(PicThread, self).__init__(parent)
        for key, value in label_dict.items():
            self.__setattr__(key, value)
        
        self.imgFolder = imgFolder
        self.imgList = imgList

        self.font = QtGui.QFont()
        self.font.setFamily("Microsoft YaHei")
    

    def run(self):
        for i in range(0, len(self.imgList)):
            frame = QImage()
            img_path  = f'./{self.imgFolder}/{self.imgList[i]}.png'
            QImage.load(frame, img_path)
            label = getattr(self, f'screen_{i+1}')
            label.setPixmap(QtGui.QPixmap(frame).scaled(label.width(), label.height()))

            if i + 1 == 10:
                continue
            label_no =  getattr(self, f'screen_{i+1}_No')
            label_no.setText(f'No.#{str(self.imgList[i]).rjust(7, "0")}')
            birth_time = time.ctime(os.stat(img_path).st_mtime)
            print(type(birth_time))
            btime = datetime.strptime(str(birth_time), '%a %b %d %H:%M:%S %Y')
            # btime = datetime.strptime(birth_time,"%a %b %d %H:%M:%S %Y")
            
            label_time =  getattr(self, f'screen_{i+1}_time')
            label_time.setText(f'//  TIME: {btime.strftime("%Y-%m-%d %H:%M:%S")}')
           
            
        self.finished.emit(True)