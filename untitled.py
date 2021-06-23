try:
    import time
    print("{}".format(time.ctime().ljust(25)) +">>> Importing required dependencies")
    import os
    import sys
    import cv2
    import json
    import shutil
    import dbus
    import atexit
    import threading
    import subprocess
    import numpy as np
    import face_recognition
    from te import UserAddition
    from PyQt5 import QtWidgets, QtGui, QtCore
except ImportError as e:
    print("{}".format(time.ctime().ljust(25))+">>> DependencyError: {}".format(e))
    sys.exit()

class MFU:
    def __init__(self):
        users_data_file = open("sharedPreference.json", "r")
        self.data = json.load(users_data_file)
        users_data_file.close()
        self.pause = True if self.data["Status"] == "Activated" else False
        self.name = "SystemTrayIcon"
        self.setUnlock()

    def setUnlock(self):
        self.session_bus = dbus.SessionBus()
        self.each = 'org.gnome.ScreenSaver'

        self.Detector = threading.Thread(target=self.isLocked, name='isLocked')
        self.Detector.setDaemon(True)
        self.Detector.start()
        atexit.register(self.setMasterExit)

    def setMasterExit(self):
        self.MasterTerm = True

    def addNewUser(self, name, path):
        try:
            self.known_face_names.append(name)
            image = face_recognition.load_image_file(path)
            face_encode = face_recognition.face_encodings(image)[0]
            self.known_face_encodings.append(face_encode)
            return True
        except:
            return False

    def isLocked(self):
        self.known_face_names = []
        self.known_face_encodings = []
        self.MasterTerm = False
        self.Previou_State = "Unlocked"

        for user in self.data["users"]:
            self.known_face_names.append(user["name"])
            image = face_recognition.load_image_file(user["img_path"])
            face_encode = face_recognition.face_encodings(image)[0]
            self.known_face_encodings.append(face_encode)

        while True:
            if self.MasterTerm:
                break
            if self.pause:
                time.sleep(1)
                continue
            else:
                try:
                    object_path = '/{0}'.format(self.each.replace('.', '/'))
                    get_object = self.session_bus.get_object(
                        self.each, object_path)
                    get_interface = dbus.Interface(get_object, self.each)
                    STATUS = bool(get_interface.GetActive())

                    if STATUS:
                        print("\n{}".format(time.ctime().ljust(25))+">>> STATE_LOCKED")
                        cam = cv2.VideoCapture(0)
                        process_this_frame = True

                        while True:
                            ret, frame = cam.read()
                            rgb_small_frame = frame[:, :, ::-1]

                            if process_this_frame:
                                face_locations = face_recognition.face_locations(
                                    rgb_small_frame)
                                face_encodings = face_recognition.face_encodings(
                                    rgb_small_frame, face_locations)

                                for face_encoding in face_encodings:
                                    name = "Unknown"
                                    matches = face_recognition.compare_faces(
                                        self.known_face_encodings, face_encoding)
                                    face_distances = face_recognition.face_distance(
                                        self.known_face_encodings, face_encoding)
                                    best_match_index = np.argmin(
                                        face_distances)

                                    if matches[best_match_index]:
                                        name = self.known_face_names[int(
                                            best_match_index)]

                                    if name in self.known_face_names:
                                        subprocess.call(
                                            ['xdotool', 'click', '2'])
                                        time.sleep(0.5)
                                        subprocess.call(
                                            ['loginctl', 'unlock-session'])
                                        cam.release()
                                        cv2.destroyAllWindows()
                                        print("{}".format(time.ctime().ljust(25))+">>> STATE_UNLOCKED by {}".format(name))
                                        print("{}".format(time.ctime().ljust(25))+">>> STATE_UNLOCKED")
                                        break
                            process_this_frame = not process_this_frame
                    else:
                        if self.Previou_State == "Unlocked":
                            pass
                        else:
                            print("{}".format(time.ctime().ljust(25))+">>> STATE_UNLOCKED")
                except dbus.exceptions.DBusException as ee:
                    pass
                except Exception as e:
                    pass
                finally:
                    time.sleep(1)


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.mfu = MFU()

        users_data_file = open("sharedPreference.json", "r+")
        self.sharedPreference = json.load(users_data_file)
        users_data_file.close()

        menu = QtWidgets.QMenu(parent)
        menu.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.setContextMenu(menu)

        icon = None
        state = None
        if not self.mfu.pause:
            icon = "Img_DB/Default/running.png"
            state = "Pause"
        else:
            icon = "Img_DB/Default/paused.png"
            state = "Resume"

        self.PAUSE = menu.addAction(QtGui.QIcon(icon), state)
        self.PAUSE.triggered.connect(self.onPause)

        self.USERS = menu.addMenu('USERS')

        for user in self.sharedPreference["users"]:
            userAction = self.USERS.addAction(
                QtGui.QIcon(user["img_path"]), user["name"])
            userAction.triggered.connect(self.removeUser)

        self.ADD = menu.addAction(QtGui.QIcon(
            "Img_DB/Default/add.png"), "Add user")
        self.ADD.triggered.connect(self.onADD)

        self.ABOUT = menu.addAction(QtGui.QIcon(
            "Img_DB/Default/about.png"), 'About')
        self.ABOUT.triggered.connect(self.onAbout)

        self.QUIT = menu.addAction(QtGui.QIcon(
            "Img_DB/Default/quit.png"), "Quit")
        self.QUIT.triggered.connect(QtWidgets.qApp.quit)

    def onAbout(self):
        print("onHome")

    def onADD(self):
        self.ua = UserAddition()
        self.ua.OK.clicked.connect(self.onOkPressed)
        self.ua.show()

    def onOkPressed(self):
        if self.ua.Input.text() == "":
            self.ua.Status.setText("Name Field Empty")
            QtCore.QTimer.singleShot(5000, lambda: self.ua.Status.setText(""))
        else:
            if self.ua.LiveR.isChecked():
                self.ua.cap.Toggle = "Quit"
                fn = "Img_DB/{}.png".format(
                    self.ua.Input.text().replace(" ", "").lower())
                f = QtCore.QFile(fn)
                f.open(QtCore.QIODevice.WriteOnly)
                self.ua.cap.Image.save(f, "PNG")
                if self.ua.PInput.text() == "12345":
                    self.ua.close()
                    new_user = {
                        "img_path": fn,
                        "name": self.ua.Input.text()
                    }
                    self.mfu.data["users"].append(new_user)
                    if self.mfu.addNewUser(new_user["name"], new_user["img_path"]):
                        newuser = self.USERS.addAction(QtGui.QIcon(
                            new_user["img_path"]), new_user["name"])
                        newuser.triggered.connect(self.removeUser)
                        with open("sharedPreference.json", "w") as users_data_file:
                            json.dump(self.mfu.data, users_data_file, indent=4)
                        users_data_file.close()
                        print("{}".format(time.ctime().ljust(25))+">>> NEW_USER Added Successfully using LIVE_MODE")
                    else:
                        print("{}".format(time.ctime().ljust(25))+">>> NEW_USER Addition Failed")
            elif self.ua.UploadR.isChecked():
                fn = "Img_DB/{}.png".format(
                    self.ua.Input.text().replace(" ", "").lower())
                f = QtCore.QFile(fn)
                f.open(QtCore.QIODevice.WriteOnly)
                QtGui.QPixmap(self.ua.cap.Image).save(f, "PNG")
                if self.ua.PInput.text() == "12345":
                    self.ua.close()
                    new_user = {
                        "img_path": fn,
                        "name": self.ua.Input.text()
                    }
                    self.mfu.data["users"].append(new_user)
                    if self.mfu.addNewUser(new_user["name"], new_user["img_path"]):
                        newuser = self.USERS.addAction(QtGui.QIcon(
                            new_user["img_path"]), new_user["name"])
                        newuser.triggered.connect(self.removeUser)
                        with open("sharedPreference.json", "w") as users_data_file:
                            json.dump(self.mfu.data, users_data_file, indent=4)
                        users_data_file.close()
                        print("{}".format(time.ctime().ljust(25))+">>> ({}) NEW_USER Added using UPLOAD_MODE".format(new_user["name"]))
                    else:
                        print("{}".format(time.ctime().ljust(25))+">>> NEW_USER Addition Failed using UPLOAD_MODE")
            else:
                self.ua.Status.setText("Select Live/Upload Mode")
                QtCore.QTimer.singleShot(
                    5000, lambda: self.ua.Status.setText(""))

    def onPause(self):
        if self.mfu.pause:
            self.PAUSE.setText("Pause")
            self.PAUSE.setIcon(QtGui.QIcon("Img_DB/Default/running.png"))
            print("{}".format(time.ctime().ljust(25))+">>> STATE_RESUME")
            self.mfu.pause = False
            self.mfu.data["Status"] = "Activited"
            with open("sharedPreference.json", "w") as users_data_file:
                json.dump(self.mfu.data, users_data_file, indent=4)
            users_data_file.close()
        else:
            self.PAUSE.setText("Resume")
            self.PAUSE.setIcon(QtGui.QIcon("Img_DB/Default/paused.png"))
            print("{}".format(time.ctime().ljust(25))+">>> STATE_PAUSE")
            self.mfu.pause = True
            self.mfu.data["Status"] = "Deactivited"
            with open("sharedPreference.json", "w") as users_data_file:
                json.dump(self.mfu.data, users_data_file, indent=4)
            users_data_file.close()

    def removeUser(self):
        action = self.sender()
        name = action.text()
        text, ok = QtWidgets.QInputDialog.getText(
            None, "Attention", "Password?", QtWidgets.QLineEdit.Password)
        if ok and text == "12":
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Warning)
            msgBox.setText("Alert!".ljust(100))
            msgBox.setInformativeText(
                "Application is already working in background process.\n\nif you think it is not working\n        Please select No and re-run application\nelse\n        Please select Yes")
            msgBox.setStandardButtons(
                QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.RestoreDefaults)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Save)
            msgBox.button(
                QtWidgets.QMessageBox.RestoreDefaults).setText("Update")
            msgBox.button(QtWidgets.QMessageBox.Discard).setText("Discard")
            msgBox.button(QtWidgets.QMessageBox.Save).setText("Save")
            msgBox.setStyleSheet('''
                background-color: #131728;
                color: white;
                QLabel{
                    width: 5000px;
                }
            ''')
            s = msgBox.exec_()
            if s == QtWidgets.QMessageBox.Save:
                pass
            elif s == QtWidgets.QMessageBox.Discard:
                self.USERS.removeAction(action)
                print("{}".format(time.ctime().ljust(25))+">>> ({}) USER_REMOVED".format(name))
                for user in self.mfu.data["users"]:
                    if user["name"] == name:
                        os.remove(user["img_path"])
                        del self.mfu.data["users"][self.mfu.data["users"].index(
                            user)]
                        break
                with open("sharedPreference.json", "w") as users_data_file:
                    json.dump(self.mfu.data, users_data_file, indent=4)
                users_data_file.close()
            elif s == QtWidgets.QMessageBox.RestoreDefaults:
                self.updateUser(name)

    def updateUser(self, name):
        action = self.sender()
        name = action.text()
        dlg = QtWidgets.QFileDialog.getOpenFileName(
            None, os.environ["HOME"], "Select user updated image")[0]
        fname = name.replace(" ", "")+os.path.splitext(dlg)[1]
        for user in self.mfu.data["users"]:
            if user["name"] == name:
                os.remove(
                    self.mfu.data["users"][self.mfu.data["users"].index(user)]["img_path"])
                shutil.copy(dlg, os.getcwd()+"/Img_DB/{}".format(fname))
                self.mfu.data["users"][self.mfu.data["users"].index(
                    user)]["img_path"] = "Img_DB/{}".format(fname)
                break
        with open("sharedPreference.json", "w") as users_data_file:
            json.dump(self.mfu.data, users_data_file, indent=4)
        users_data_file.close()
        print("{}".format(time.ctime().ljust(25))+">>> ({}) USER_UPDATED")


def onTerminate():
    os.unlink("/tmp/MiniProjectE3S1.pid")
    print("\n\n{}").format(time.ctime().ljust(25))+">>> Instance Terminated Successfully"


def mainService(image, app):
    print("\n{}".format(time.ctime().ljust(25))+">>> Instance Initiated")
    app.setQuitOnLastWindowClosed(False)
    w = QtWidgets.QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon(image), w)
    trayIcon.show()
    print("{}".format(time.ctime().ljust(25))+">>> Activated Successfully")
    print("{}".format(time.ctime().ljust(25))+">>> STATE_UNLOCKED")
    sys.exit(app.exec_())


if __name__ == '__main__':
    pid = str(os.getpid())
    pidfile = "/tmp/MiniProjectE3S1.pid"
    logo = "Img_DB/Default/logo.png"
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Face Unlock")

    if os.path.isfile(pidfile):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setText("Alert!".ljust(100))
        msgBox.setInformativeText(
            "Application is already working in background process.\n\nif you think it is not working\n        Please select No and re-run application\nelse\n        Please select Yes")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
        msgBox.button(QtWidgets.QMessageBox.Ok).setObjectName("OK")
        msgBox.setStyleSheet('''
            background-color: #131728;
            color: white;
            QLabel{
                width: 5000px;
            }
            QPushButton#OK{
                border : 1px solid red;
            }
        ''')
        msgBox.exec_()
        QtWidgets.qApp.quit()
        sys.exit()
    else:
        atexit.register(onTerminate)
        fh = open(pidfile, 'w')
        fh.write(pid)
        fh.close()
        mainService(logo, app)
