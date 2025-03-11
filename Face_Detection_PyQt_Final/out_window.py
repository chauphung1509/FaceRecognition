# Modified by Augmented Startups & Geeky Bee
# October 2020
# Facial Recognition Attendence GUI
# Full Course - https://augmentedstartups.info/yolov4release
# *-
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.uic import loadUi
from PyQt6.QtCore import pyqtSlot, QTimer, QDate, Qt
from PyQt6.QtWidgets import QDialog, QMessageBox
import cv2
import face_recognition
import numpy as np
import datetime
import os
import csv


class Ui_OutputDialog(QDialog):
    def __init__(self):
        super(Ui_OutputDialog, self).__init__()
        loadUi("./outputwindow.ui", self)

        # Update time
        now = QDate.currentDate()
        current_date = now.toString('ddd dd MMMM yyyy')
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.Date_Label.setText(current_date)
        self.Time_Label.setText(current_time)

        self.image = None

    @pyqtSlot()
    def startVideo(self, camera_name):
        """
        :param camera_name: link of camera or usb camera
        :return:
        """
        # Thêm kiểm tra và thông báo cho việc kết nối camera
        try:
            if len(camera_name) == 1:
                self.capture = cv2.VideoCapture(int(camera_name))
            else:
                self.capture = cv2.VideoCapture(camera_name)

            # Kiểm tra xem camera có mở được không
            if not self.capture.isOpened():
                print("Lỗi: Không thể mở camera. Vui lòng kiểm tra kết nối camera.")
                QMessageBox.critical(self, "Lỗi Camera", "Không thể mở camera. Vui lòng kiểm tra kết nối camera.")
                return

            ret, test_frame = self.capture.read()
            if not ret:
                print("Lỗi: Không thể đọc khung hình từ camera.")
                QMessageBox.critical(self, "Lỗi Camera", "Không thể đọc khung hình từ camera.")
                return

            print("Camera đã kết nối thành công!")
        except Exception as e:
            print(f"Lỗi khi kết nối camera: {e}")
            QMessageBox.critical(self, "Lỗi Camera", f"Lỗi khi kết nối camera: {e}")
            return

        self.timer = QTimer(self)  # Create Timer

        # Kiểm tra và tạo thư mục ImagesAttendance nếu cần
        path = 'ImagesAttendance'
        if not os.path.exists(path):
            os.mkdir(path)
            print(f"Đã tạo thư mục {path}")

        # known face encoding and known face name list
        images = []
        self.class_names = []
        self.encode_list = []
        self.TimeList1 = []
        self.TimeList2 = []

        # Kiểm tra xem thư mục có ảnh không
        attendance_list = os.listdir(path)
        if not attendance_list:
            print(f"Thư mục {path} trống. Vui lòng thêm ảnh khuôn mặt vào thư mục.")
            QMessageBox.warning(self, "Cảnh báo", f"Thư mục {path} trống. Vui lòng thêm ảnh khuôn mặt vào thư mục.")

        # Xử lý ảnh khuôn mặt
        try:
            for cl in attendance_list:
                if cl.lower().endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        cur_img = cv2.imread(f'{path}/{cl}')
                        if cur_img is None:
                            print(f"Không thể đọc file ảnh: {cl}")
                            continue
                        images.append(cur_img)
                        self.class_names.append(os.path.splitext(cl)[0])
                    except Exception as e:
                        print(f"Lỗi khi đọc ảnh {cl}: {e}")

            if not images:
                print("Không có ảnh hợp lệ trong thư mục ImagesAttendance")
                QMessageBox.warning(self, "Cảnh báo", "Không có ảnh hợp lệ trong thư mục ImagesAttendance")
            else:
                print(f"Đã tìm thấy {len(images)} ảnh khuôn mặt")

            for img in images:
                try:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    boxes = face_recognition.face_locations(img)
                    if len(boxes) > 0:
                        encodes_cur_frame = face_recognition.face_encodings(img, boxes)[0]
                        self.encode_list.append(encodes_cur_frame)
                    else:
                        print(f"Không tìm thấy khuôn mặt trong ảnh của {self.class_names[images.index(img)]}")
                except Exception as e:
                    print(f"Lỗi khi xử lý ảnh {self.class_names[images.index(img)]}: {e}")

            if not self.encode_list:
                print("Không thể mã hóa khuôn mặt từ bất kỳ ảnh nào")
                QMessageBox.warning(self, "Cảnh báo", "Không thể mã hóa khuôn mặt từ bất kỳ ảnh nào")

            print(f"Đã mã hóa {len(self.encode_list)} khuôn mặt thành công")
        except Exception as e:
            print(f"Lỗi trong quá trình xử lý ảnh: {e}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi trong quá trình xử lý ảnh: {e}")

        self.timer.timeout.connect(self.update_frame)  # Connect timeout to the output function
        self.timer.start(10)  # emit the timeout() signal at x=40ms

    def face_rec_(self, frame, encode_list_known, class_names):
        """
        :param frame: frame from camera
        :param encode_list_known: known face encoding
        :param class_names: known face names
        :return:
        """

        # csv

        def mark_attendance(name):
            """
            :param name: detected face known or unknown one
            :return:
            """
            if self.ClockInButton.isChecked():
                self.ClockInButton.setEnabled(False)
                with open('Attendance.csv', 'a') as f:
                    if (name != 'unknown'):
                        buttonReply = QMessageBox.question(self, 'Welcome ' + name, 'Are you Clocking In?',
                                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                                           QMessageBox.StandardButton.No)
                        if buttonReply == QMessageBox.StandardButton.Yes:

                            date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                            f.writelines(f'\n{name},{date_time_string},Clock In')
                            self.ClockInButton.setChecked(False)

                            self.NameLabel.setText(name)
                            self.StatusLabel.setText('Clocked In')
                            self.HoursLabel.setText('Measuring')
                            self.MinLabel.setText('')

                            # self.CalculateElapse(name)
                            # print('Yes clicked and detected')
                            self.Time1 = datetime.datetime.now()
                            # print(self.Time1)
                            self.ClockInButton.setEnabled(True)
                        else:
                            print('Not clicked.')
                            self.ClockInButton.setEnabled(True)
            elif self.ClockOutButton.isChecked():
                self.ClockOutButton.setEnabled(False)
                with open('Attendance.csv', 'a') as f:
                    if (name != 'unknown'):
                        buttonReply = QMessageBox.question(self, 'Cheers ' + name, 'Are you Clocking Out?',
                                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                                           QMessageBox.StandardButton.No)
                        if buttonReply == QMessageBox.StandardButton.Yes:
                            date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                            f.writelines(f'\n{name},{date_time_string},Clock Out')
                            self.ClockOutButton.setChecked(False)

                            self.NameLabel.setText(name)
                            self.StatusLabel.setText('Clocked Out')
                            self.Time2 = datetime.datetime.now()
                            # print(self.Time2)

                            self.ElapseList(name)
                            self.TimeList2.append(datetime.datetime.now())
                            CheckInTime = self.TimeList1[-1]
                            CheckOutTime = self.TimeList2[-1]
                            self.ElapseHours = (CheckOutTime - CheckInTime)
                            self.MinLabel.setText(
                                "{:.0f}".format(abs(self.ElapseHours.total_seconds() / 60) % 60) + 'm')
                            self.HoursLabel.setText(
                                "{:.0f}".format(abs(self.ElapseHours.total_seconds() / 60 ** 2)) + 'h')
                            self.ClockOutButton.setEnabled(True)
                        else:
                            print('Not clicked.')
                            self.ClockOutButton.setEnabled(True)

        # face recognition
        faces_cur_frame = face_recognition.face_locations(frame)
        encodes_cur_frame = face_recognition.face_encodings(frame, faces_cur_frame)
        # count = 0
        for encodeFace, faceLoc in zip(encodes_cur_frame, faces_cur_frame):
            match = face_recognition.compare_faces(encode_list_known, encodeFace, tolerance=0.50)
            face_dis = face_recognition.face_distance(encode_list_known, encodeFace)
            name = "unknown"
            best_match_index = np.argmin(face_dis)
            # print("s",best_match_index)
            if match[best_match_index]:
                name = class_names[best_match_index].upper()
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            mark_attendance(name)

        return frame

    def showdialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)

        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

    def ElapseList(self, name):
        with open('Attendance.csv', "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 2

            Time1 = datetime.datetime.now()
            Time2 = datetime.datetime.now()
            for row in csv_reader:
                for field in row:
                    if field in row:
                        if field == 'Clock In':
                            if row[0] == name:
                                # print(f'\t ROW 0 {row[0]}  ROW 1 {row[1]} ROW2 {row[2]}.')
                                Time1 = (datetime.datetime.strptime(row[1], '%y/%m/%d %H:%M:%S'))
                                self.TimeList1.append(Time1)
                        if field == 'Clock Out':
                            if row[0] == name:
                                # print(f'\t ROW 0 {row[0]}  ROW 1 {row[1]} ROW2 {row[2]}.')
                                Time2 = (datetime.datetime.strptime(row[1], '%y/%m/%d %H:%M:%S'))
                                self.TimeList2.append(Time2)
                                # print(Time2)

    def update_frame(self):
        try:
            ret, self.image = self.capture.read()
            if not ret:
                print("Lỗi: Không thể đọc khung hình từ camera")
                return
            self.displayImage(self.image, self.encode_list, self.class_names, 1)
        except Exception as e:
            print(f"Lỗi khi cập nhật khung hình: {e}")

    def displayImage(self, image, encode_list, class_names, window=1):
        """
        :param image: frame from camera
        :param encode_list: known face encoding list
        :param class_names: known face names
        :param window: number of window
        :return:
        """
        try:
            image = cv2.resize(image, (640, 480))

            # Thêm thông tin trạng thái lên khung hình
            cv2.putText(image, f"Faces loaded: {len(encode_list)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 255, 0), 2)

            if len(encode_list) > 0:
                try:
                    image = self.face_rec_(image, encode_list, class_names)
                except Exception as e:
                    print(f"Lỗi trong quá trình nhận diện khuôn mặt: {e}")
                    cv2.putText(image, f"Face recognition error: {str(e)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 0, 255), 2)
            else:
                # Hiển thị thông báo khi không có dữ liệu khuôn mặt
                cv2.putText(image, "No face data available - Add faces to ImagesAttendance folder", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            qformat = QImage.Format.Format_Indexed8
            if len(image.shape) == 3:
                if image.shape[2] == 4:
                    qformat = QImage.Format.Format_RGBA8888
                else:
                    qformat = QImage.Format.Format_RGB888
            outImage = QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
            outImage = outImage.rgbSwapped()

            if window == 1:
                self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
                self.imgLabel.setScaledContents(True)
        except Exception as e:
            print(f"Lỗi khi hiển thị hình ảnh: {e}")