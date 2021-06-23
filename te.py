import os
import sys
import cv2
import threading
from PyQt5 import QtWidgets, QtGui, QtCore

class Capture(QtWidgets.QWidget):
    def __init__(self):
        super(Capture, self).__init__()
        self.Image = None
        self.Toggle = None
        self.Temp_Frame=None
        self.Flag = None
        self.pause=False
        self.vid=None
        self.setObjectName("Capture")
        self.Layout = QtWidgets.QHBoxLayout(self)
        self.Layout.setSpacing(0)
        self.Layout.setContentsMargins(0,0,0,0)

        self.Live = QtWidgets.QWidget()
        self.Live.setVisible(False)
        
        self.Live_Layout = QtWidgets.QHBoxLayout(self.Live)
        self.Live_Layout.setSpacing(10)
        self.Live_Layout.setContentsMargins(10,10,0,0)
        
        self.Live_BLayout = QtWidgets.QVBoxLayout()
        self.Live_BLayout.setSpacing(0)
        self.Live_BLayout.setContentsMargins(0,0,10,0)

        self.Live_Layout_Image = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        self.Live_Layout_Image.setObjectName("IMAGE")
        self.Live_Layout_Image.setPixmap(QtGui.QPixmap("Img_DB/Default/add.png").scaledToWidth(100))
        self.Live_Layout_Image.setMaximumHeight(200)
        
        self.Live_BLayout_Capture = QtWidgets.QPushButton("Capture")
        self.Live_BLayout_Capture.clicked.connect(self.onCapture)
        
        self.Live_BLayout_Pause = QtWidgets.QPushButton("Pause")
        self.Live_BLayout_Pause.clicked.connect(self.onPause)
        self.Live_BLayout_Pause.setEnabled(False)
        
        self.Live_BLayout.addWidget(self.Live_BLayout_Capture)
        self.Live_BLayout.addWidget(self.Live_BLayout_Pause)

        self.Live_Layout.addWidget(self.Live_Layout_Image,1)
        self.Live_Layout.addLayout(self.Live_BLayout)

        self.Upload = QtWidgets.QWidget()
        self.Upload.setVisible(False)
        self.Upload_Layout = QtWidgets.QVBoxLayout(self.Upload)
        self.Upload_Layout.setSpacing(0)
        self.Upload_Layout.setContentsMargins(10,10,10,0)
        self.Upload_Layout_Image = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        self.Upload_Layout_Image.setObjectName("IMAGE")
        self.Upload_Layout_Image.setMaximumHeight(200)
        self.Upload_Layout_Image.setPixmap(QtGui.QPixmap("Img_DB/Default/add.png").scaledToWidth(100))
        self.Upload_Layout_Browse = QtWidgets.QPushButton("Browse..")
        self.Upload_Layout_Browse.clicked.connect(self.onBrowse)
        self.Upload_Layout.addWidget(self.Upload_Layout_Image)
        self.Upload_Layout.addWidget(self.Upload_Layout_Browse)

        self.Layout.addWidget(self.Live)
        self.Layout.addWidget(self.Upload)

        self.setStyleSheet("""
            QLabel#IMAGE{
                border: 2px solid gray;
                background-color: gray;
            }
        """)


    def onPause(self):
        self.pause=not self.pause
            
    def onBrowse(self):
        self.Image = QtWidgets.QFileDialog.getOpenFileName(self, os.environ["HOME"], "Select user updated image")[0]
        self.Upload_Layout_Image.setPixmap(QtGui.QPixmap(self.Image).scaled(400,200))

    def onCapture(self):
        if self.Flag:
            return
        else:
            x = threading.Thread(target=self.onLive)
            x.start()
            self.Live_BLayout_Pause.setEnabled(True)

    def onLive(self):
        self.Flag=True
        self.vid = cv2.VideoCapture(0)
        while self.Toggle=="Live":
            if self.pause:
                continue
            """
            ret, frame self.Temp_Frame= self.vid.read()
            rgb_small_frame = self.Temp_Frame[:, :, ::-1]
            rgb_image = cv2.cvtColor(rgb_small_frame, cv2.COLOR_BGR2RGB)
            """
            ret, self.Temp_Frame= self.vid.read()
            rgb_image = cv2.cvtColor(self.Temp_Frame, cv2.COLOR_BGR2RGB)



            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.Image=convert_to_Qt_format
            p = convert_to_Qt_format.scaled(400, 200, QtCore.Qt.KeepAspectRatio)
            self.Live_Layout_Image.setPixmap(QtGui.QPixmap.fromImage(p))
        self.vid.release()
        self.Flag=False


class UserAddition(QtWidgets.QWidget):
    def __init__(self):
        super(UserAddition, self).__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.SplashScreen)
        self.setMinimumWidth(400)

        self.Layout = QtWidgets.QVBoxLayout(self)
        self.Layout.setSpacing(0)
        self.Layout.setContentsMargins(0,0,0,0)

        self.cap = Capture()
        
        self.Title = QtWidgets.QLabel("Face Unlocker",alignment=QtCore.Qt.AlignCenter)
        self.Title.setObjectName("Title")
        self.Title.setFixedHeight(40)

        self.Hint = QtWidgets.QLabel("* Enter Name",alignment=QtCore.Qt.AlignBottom)
        self.Hint.setObjectName("Hint")
        self.Hint.setMaximumHeight(25)
        self.Input = QtWidgets.QLineEdit()
        self.Input.setPlaceholderText("Enter new user Name")
        self.Input.setObjectName("Input")

        self.PHint = QtWidgets.QLabel("* Master Password",alignment=QtCore.Qt.AlignBottom)
        self.PHint.setObjectName("Hint")
        self.PHint.setMaximumHeight(25)
        self.PInput = QtWidgets.QLineEdit()
        self.PInput.setEchoMode(QtWidgets.QLineEdit.Password)
        self.PInput.setPlaceholderText("Password")
        self.PInput.setObjectName("PInput")

        self.LRadio = QtWidgets.QHBoxLayout()
        self.LRadio.setSpacing(0)
        self.LRadio.setContentsMargins(0,0,0,0)
        self.LiveR   = QtWidgets.QRadioButton("Live Capture")
        self.LiveR.toggled.connect(self.onToggle)
        self.UploadR = QtWidgets.QRadioButton("Upload Image")
        self.UploadR.toggled.connect(self.onToggle)
        self.LRadio.addWidget(self.LiveR)
        self.LRadio.addWidget(self.UploadR)

        self.LButton = QtWidgets.QHBoxLayout()
        self.LButton.setSpacing(0)
        self.LButton.setContentsMargins(10,10,10,10)
        self.OK= QtWidgets.QPushButton("Ok")
        self.OK.setObjectName("OK")
        self.Cancel= QtWidgets.QPushButton("Cancel")
        self.Cancel.setObjectName("CANCLE")
        self.Cancel.clicked.connect(self.onCancel)
        self.LButton.addWidget(self.Cancel)
        self.LButton.addWidget(QtWidgets.QLabel(),1)
        self.LButton.addWidget(self.OK)

        self.Status = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        self.Status.setObjectName("Status")
        self.Status.setFixedHeight(20)

        self.Layout.addWidget(self.Title)
        self.Layout.addWidget(self.Status)
        self.Layout.addWidget(self.Hint)
        self.Layout.addWidget(self.Input)
        self.Layout.addLayout(self.LRadio)
        self.Layout.addWidget(self.PHint)
        self.Layout.addWidget(self.PInput)
        self.Layout.addWidget(self.cap)
        self.Layout.addLayout(self.LButton)

        self.setStyleSheet("""
            QLabel#Status{
                font-weight: bold;
                color: red;
            }
            QLabel#Title{
                color: white;
                font-weight: bold;
                background-color: #131728;
            }
            QLabel#Hint{
                margin-left: 10px;
            }
            QPushButton#CANCLE{
                height: 30px;
                width : 100px;
                border: none;
                color: white;
                border-radius: 10px;
                background-color: red;
            }
            QPushButton#OK{
                height: 30px;
                width : 100px;
                border: none;
                border-radius: 10px;
                color: white;
                background-color: green;
            }
            QRadioButton{
                height: 50px;
                padding-left: 10px;
            }
            QLineEdit{
                padding: 5px;
                margin-left: 10px;
                margin-right: 10px;
            }
        """)

    def onCancel(self):
        try:
            self.cap.Toggle="Quit"
        except Exception as e:
            print(e)
        finally:
            self.close()

    def onToggle(self):
        if self.LiveR.isChecked():
            self.cap.Upload.setVisible(False)
            self.cap.Live.setVisible(True)
            self.cap.Toggle="Live"

        elif self.UploadR.isChecked():
            self.cap.Live.setVisible(False)
            self.cap.Upload.setVisible(True)
            self.cap.Toggle="Upload"
