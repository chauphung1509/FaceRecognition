# Modified by Augmented Startups & Geeky Bee
# October 2020
# Facial Recognition Attendence GUI
# Full Course - https://augmentedstartups.info/yolov4release
# *-
import sys
from PyQt6.uic import loadUi
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
import resource
# from model import Model
from out_window import Ui_OutputDialog


class Ui_Dialog(QDialog):
    def __init__(self):
        super(Ui_Dialog, self).__init__()
        loadUi("mainwindow.ui", self)

        self.runButton.clicked.connect(self.runSlot)

        self._new_window = None
        self.Videocapture_ = None

    def refreshAll(self):
        """
        Set the text of lineEdit once it's valid
        """
        self.Videocapture_ = "0"

    @pyqtSlot()
    def runSlot(self):
        """
        Called when the user presses the Run button
        """
        print("Clicked Run")
        try:
            self.refreshAll()
            print(f"Camera source: {self.Videocapture_}")
            ui.hide()  # hide the main window
            self.outputWindow_()  # Create and open new output window
        except Exception as e:
            print(f"Lỗi khi khởi động ứng dụng: {e}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi khởi động ứng dụng: {e}")

    def outputWindow_(self):
        """
        Created new window for vidual output of the video in GUI
        """
        try:
            self._new_window = Ui_OutputDialog()
            self._new_window.show()
            self._new_window.startVideo(self.Videocapture_)
            print("Video Played")
        except Exception as e:
            print(f"Lỗi khi mở cửa sổ đầu ra: {e}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi mở cửa sổ đầu ra: {e}")
            ui.show()  # Hiển thị lại cửa sổ chính nếu có lỗi


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Ui_Dialog()
    ui.show()
    sys.exit(app.exec())