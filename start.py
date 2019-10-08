# _*_ coding:utf-8 _*_
import base64
import sys
from urllib.parse import quote_plus, unquote_plus

import os

import shutil

import time

import suds
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QProcess
from PyQt5.QtGui import QTextCursor, QIcon, QCursor, QPainter
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QGroupBox, \
    QTextEdit, QGridLayout, QFileDialog, QTabWidget, QScrollArea, QCheckBox
from suds.client import Client

from imgs import icon, base64_to_pixmap, pointer


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.path = ""
        self.save_path = ""
        self.timer = QTimer(self)

        self.box_h_tips = QHBoxLayout()
        self.l_tips = QLabel()

        self.l_tips.setStyleSheet("color:red")
        self.l_tips.setLayout(self.box_h_tips)

        # ======== tap 1 ==============================
        self.l_img_path = QLabel("图片路径：")
        self.e_img_path = QLineEdit()
        self.e_img_path.setReadOnly(True)
        self.b_open_to_select_img_path = QPushButton("...")
        self.b_open_to_select_img_path.setToolTip("选择文件")

        def open_to_select_img_path():
            pre_path = self.path
            self.path = QFileDialog.getOpenFileName(self, "选择文件...", self.path)[0]
            if self.path == "":
                self.path = pre_path
                return
            self.e_img_path.setText(self.path)
            self.img_to_b64str()
            self.b64str_to_img()

        self.b_open_to_select_img_path.clicked.connect(open_to_select_img_path)

        # ================= convert ========================
        self.b_img_to_b64str = QPushButton("图片转base64")

        self.b_img_to_b64str.clicked.connect(self.img_to_b64str)

        self.e_img_result = QTextEdit()
        self.e_img_result.setAcceptRichText(False)

        def text_change():
            self.e_img_result.moveCursor(QTextCursor.End)
            self.b64str_to_img()

        self.e_img_result.textChanged.connect(text_change)

        self.b_b64str_to_img = QPushButton("base64转图片")

        self.b_b64str_to_img.clicked.connect(self.b64str_to_img)

        self.b_save = QPushButton("保存原图")

        def save():
            try:
                self.save_path = QFileDialog.getSaveFileName(self, "保存图片", self.save_path)[0]
                if self.save_path == "":
                    self.alert("取消保存")
                    return
                img = base64_to_pixmap(self.e_img_result.toPlainText())
                if img.save(self.save_path):
                    self.alert("保存成功,路径:" + self.save_path)
                else:
                    self.alert("保存失败!")
            except Exception as e:
                self.alert(str(e))

        self.b_save.clicked.connect(save)

        self.b_clear = QPushButton("清空")
        self.b_clear.clicked.connect(self.e_img_result.clear)

        self.box_v_img_to_b64str = QVBoxLayout()
        self.l_img = QLabel()
        self.box_v_img_to_b64str.addWidget(self.l_img)
        self.l_img.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.g_b64str_to_img = QGroupBox("转换缩略图")
        self.g_b64str_to_img.setLayout(self.box_v_img_to_b64str)

        self.box_g_img_to_b64str = QGridLayout()
        self.box_g_img_to_b64str.addWidget(self.l_img_path, 0, 0)
        self.box_g_img_to_b64str.addWidget(self.e_img_path, 0, 1)
        self.box_g_img_to_b64str.addWidget(self.b_open_to_select_img_path, 0, 2)
        self.box_g_img_to_b64str.addWidget(self.b_img_to_b64str, 0, 3)
        self.box_g_img_to_b64str.addWidget(self.b_b64str_to_img, 0, 4)
        self.box_g_img_to_b64str.addWidget(self.b_save, 0, 5)
        self.box_g_img_to_b64str.addWidget(self.b_clear, 0, 6)
        self.box_g_img_to_b64str.addWidget(self.e_img_result, 1, 0, 1, 3)
        self.box_g_img_to_b64str.addWidget(self.g_b64str_to_img, 1, 3, 1, 4)

        self.g_img_to_b64str = QGroupBox("图片与base64互转")
        self.g_img_to_b64str.setLayout(self.box_g_img_to_b64str)
        # ======== tap 1 ==============================
        # ======== tap 2 ==============================

        self.e_url_string = QTextEdit()
        self.e_url_string.setAcceptRichText(False)
        self.e_url_string_result = QTextEdit()
        self.e_url_string_result.setReadOnly(True)
        self.b_url_string_encode = QPushButton("url编码")

        def url_string_encode():
            try:
                self.e_url_string_result.clear()
                self.e_url_string_result.setText(quote_plus(self.e_url_string.toPlainText()))
            except Exception as e:
                self.alert(str(e))

        self.b_url_string_encode.clicked.connect(url_string_encode)
        self.b_url_string_decode = QPushButton("url解码")

        def url_string_decode():
            try:
                self.e_url_string_result.clear()
                self.e_url_string_result.setText(unquote_plus(self.e_url_string.toPlainText()))
            except Exception as e:
                self.alert(str(e))

        self.b_url_string_decode.clicked.connect(url_string_decode)

        self.b_url_string_paste_decode = QPushButton("粘贴并解码")

        def url_string_paste_decode():
            self.e_url_string.setText(QApplication.clipboard().text())
            url_string_decode()

        self.b_url_string_paste_decode.clicked.connect(url_string_paste_decode)
        self.b_url_string_paste_encode = QPushButton("粘贴并编码")

        def url_string_paste_encode():
            self.e_url_string.setText(QApplication.clipboard().text())
            url_string_encode()

        self.b_url_string_paste_encode.clicked.connect(url_string_paste_encode)

        self.b_url_string_clear = QPushButton("清空")

        self.b_url_string_clear.clicked.connect(self.e_url_string.clear)

        self.box_g_url_string = QGridLayout()
        self.box_g_url_string.addWidget(self.e_url_string, 0, 0, 7, 1)
        self.box_g_url_string.addWidget(self.b_url_string_encode, 1, 1, 1, 1)
        self.box_g_url_string.addWidget(self.b_url_string_decode, 2, 1, 1, 1)
        self.box_g_url_string.addWidget(self.b_url_string_paste_encode, 3, 1, 1, 1)
        self.box_g_url_string.addWidget(self.b_url_string_paste_decode, 4, 1, 1, 1)
        self.box_g_url_string.addWidget(self.b_url_string_clear, 5, 1, 1, 1)
        self.box_g_url_string.addWidget(self.e_url_string_result, 0, 2, 7, 1)

        self.g_url_string = QGroupBox("url编解码")
        self.g_url_string.setLayout(self.box_g_url_string)
        # ======== tap 2 ==============================

        # ======== tap 3 ==============================
        self.l_webservice_test_url = QLabel("WebService Url:")
        self.e_webservice_test_url = QLineEdit()
        self.e_webservice_test_result = QTextEdit()
        self.e_webservice_test_result.setReadOnly(True)
        self.e_webservice_test_result.textChanged.connect(
            lambda: self.e_webservice_test_result.moveCursor(QTextCursor.End))
        self.content_webservice_test = self.e_webservice_test_result.toPlainText()

        self.b_webservice_test = QPushButton("测试webservice")

        def webservice_test():
            client = Client(self.e_webservice_test_url.text(), autoblend=True)
            self.e_webservice_test_result.setText(str(client))

        self.b_webservice_test.clicked.connect(lambda: self.catch_to_alert(webservice_test))

        self.l_webservice_test_method = QLabel("方法名:")
        self.e_webservice_test_method = QLineEdit()

        self.box_g_webservice_test_params = QGridLayout()

        self.box_g_webservice_test_params.addWidget(self.l_webservice_test_method, 0, 0)
        self.box_g_webservice_test_params.addWidget(self.e_webservice_test_method, 0, 1)
        self.params_count = 13
        for i in range(1, self.params_count):
            setattr(self, "l_webservice_test_param%d" % i, QLabel("参数%d" % i))
            setattr(self, "e_webservice_test_param%d" % i, QLineEdit())
            l = getattr(self, "l_webservice_test_param%d" % i)
            e = getattr(self, "e_webservice_test_param%d" % i)
            self.box_g_webservice_test_params.addWidget(l, i, 0)
            self.box_g_webservice_test_params.addWidget(e, i, 1)

        self.s_webservice_test_params = QScrollArea()
        self.s_webservice_test_params.setLayout(self.box_g_webservice_test_params)

        self.b_webservice_test_send_request = QPushButton("发送请求")

        def webservice_test_send_request():
            client = Client(self.e_webservice_test_url.text(), autoblend=True)
            method = getattr(client.service, self.e_webservice_test_method.text())
            params = []
            for i in range(1, self.params_count):
                e_param = getattr(self, "e_webservice_test_param%d" % i)
                param = e_param.text()
                params.append(param)
            try:
                resp = method(tuple(params))
            except suds.TypeNotFound:
                resp = method(*params)
            self.content_webservice_test = resp
            result = unquote_plus(resp) if self.c_b_webservice_test_result_url_decode.isChecked() else resp
            self.e_webservice_test_result.setText(result)

        self.b_webservice_test_send_request.clicked.connect(lambda: self.catch_to_alert(webservice_test_send_request))

        self.c_b_webservice_test_result_url_decode = QCheckBox("返回结果Url解码")

        def webservice_test_result_url_decode_or_encode():
            result = self.content_webservice_test \
                if not self.c_b_webservice_test_result_url_decode.isChecked() else unquote_plus(
                self.content_webservice_test)
            self.e_webservice_test_result.setText(result)

        self.c_b_webservice_test_result_url_decode.stateChanged.connect(
            lambda: self.catch_to_alert(webservice_test_result_url_decode_or_encode))
        self.box_g_webservice_test = QGridLayout()
        self.box_g_webservice_test.addWidget(self.l_webservice_test_url, 0, 0, 1, 1)
        self.box_g_webservice_test.addWidget(self.e_webservice_test_url, 0, 1, 1, 8)
        self.box_g_webservice_test.addWidget(self.b_webservice_test, 0, 9, 1, 1)
        self.box_g_webservice_test.addWidget(self.s_webservice_test_params, 1, 0, 5, 3)
        self.box_g_webservice_test.addWidget(self.b_webservice_test_send_request, 3, 3, 1, 1)
        self.box_g_webservice_test.addWidget(self.c_b_webservice_test_result_url_decode, 1, 3, 1, 1)
        self.box_g_webservice_test.addWidget(self.e_webservice_test_result, 1, 4, 5, 6)

        self.g_webservice_test = QGroupBox("webservice测试")
        self.g_webservice_test.setLayout(self.box_g_webservice_test)
        # ======== tap 3 ==============================

        # ======== tap 4 ==============================

        self.c_b_box_screen_record_full_screen = QCheckBox("录制全屏")
        self.c_b_box_screen_record_full_screen.setChecked(True)

        self.c_b_box_screen_record_pointer = QCheckBox("录制指针")
        self.c_b_box_screen_record_pointer.setChecked(True)

        self.b_screen_record_select_area = QPushButton("选取区域")
        self.b_screen_record_start = QPushButton("开始录制")
        self.e_screen_record_result = QTextEdit()
        self.e_screen_record_result.setReadOnly(True)
        self.e_screen_record_result.textChanged.connect(lambda: self.e_screen_record_result.moveCursor(QTextCursor.End))

        def screen_record_start():
            if not os.path.exists("ffmpeg.exe"):
                self.alert("目录下未找到[ffmpeg.exe]!")
                return
            self.e_screen_record_result.clear()
            if self.t_screen_record_recording.running:
                if self.t_screen_record_recording.is_pause:
                    self.b_screen_record_start.setText("暂停录制")
                    self.t_screen_record_recording.is_pause = False
                else:
                    self.b_screen_record_start.setText("继续录制")
                    self.t_screen_record_recording.is_pause = True
            else:
                self.l_screen_record_time.setText("0s")
                self.b_screen_record_start.setText("暂停录制")
            self.c_b_box_screen_record_pointer.setEnabled(False)
            self.c_b_box_screen_record_full_screen.setEnabled(False)
            self.b_screen_record_stop.setEnabled(True)
            self.l_screen_record_time.setVisible(True)
            self.t_screen_record_recording.full_screen = self.c_b_box_screen_record_full_screen.isChecked()
            self.t_screen_record_recording.record_pointer = self.c_b_box_screen_record_pointer.isChecked()
            self.t_screen_record_recording.start()

        self.b_screen_record_start.clicked.connect(screen_record_start)
        self.t_screen_record_recording = ScreenRecordThread()

        self.p_screen_record_save = QProcess()

        self.screen_record_save_path = ""

        def p_screen_record_save_finished(code, status):
            if code == 0:
                self.alert("保存成功>" + self.screen_record_save_path)
            else:
                self.alert("保存失败 code:%s,status:%s" % (code, status))

            screen_record_reset()

        def p_screen_record_save_read():
            self.e_screen_record_result.append(str(self.p_screen_record_save.readAllStandardError(), encoding="gbk"))
            self.e_screen_record_result.append(str(self.p_screen_record_save.readAllStandardOutput(), encoding="gbk"))

        self.p_screen_record_save.readyReadStandardError.connect(p_screen_record_save_read)
        self.p_screen_record_save.readyReadStandardOutput.connect(p_screen_record_save_read)
        self.p_screen_record_save.finished.connect(p_screen_record_save_finished)

        def screen_record_reset():
            shutil.rmtree(self.t_screen_record_recording.temp_path)
            self.b_screen_record_start.setText("开始录制")
            self.b_screen_record_start.setEnabled(True)
            self.c_b_box_screen_record_pointer.setEnabled(True)
            self.c_b_box_screen_record_full_screen.setEnabled(True)
            self.b_screen_record_stop.setEnabled(False)
            self.l_screen_record_time.clear()
            self.l_screen_record_time.setVisible(False)

        def screen_record_stop(path, fps):
            save_path = QFileDialog.getSaveFileName(self, "保存视频")[0]
            if save_path == "":
                self.alert("取消保存")
                screen_record_reset()
                return
            else:
                if not save_path.endswith(".mp4"):
                    save_path = save_path + ".mp4"
                self.screen_record_save_path = save_path

                self.b_screen_record_start.setEnabled(False)
                command = "./ffmpeg.exe -f image2 -r " + str(fps) + " -i ./" + path + '/%d.jpg -y "' + save_path + '"'

                self.p_screen_record_save.start(command)

        def screen_record_time():
            self.l_screen_record_time.setText(str(self.t_screen_record_recording.record_time) + "s")


        self.t_screen_record_recording.stop_trigger.connect(screen_record_stop)
        self.t_screen_record_recording.record_trigger.connect(screen_record_time)

        self.b_screen_record_stop = QPushButton("结束录制")
        self.b_screen_record_stop.setEnabled(False)
        self.l_screen_record_time = QLabel()
        self.l_screen_record_time.setVisible(False)

        def screen_record_stop():
            self.b_screen_record_stop.setEnabled(False)
            self.t_screen_record_recording.stop()

        self.b_screen_record_stop.clicked.connect(screen_record_stop)

        self.box_g_screen_record = QGridLayout()
        self.box_g_screen_record.addWidget(self.c_b_box_screen_record_pointer, 0, 0)
        self.box_g_screen_record.addWidget(self.c_b_box_screen_record_full_screen, 0, 1)
        self.box_g_screen_record.addWidget(self.b_screen_record_select_area, 0, 2)
        self.box_g_screen_record.addWidget(self.b_screen_record_start, 0, 3)
        self.box_g_screen_record.addWidget(self.b_screen_record_stop, 0, 4)
        self.box_g_screen_record.addWidget(self.l_screen_record_time, 0, 5)
        self.box_g_screen_record.addWidget(self.e_screen_record_result, 1, 0, 1, 10)

        self.g_screen_record = QGroupBox("屏幕录制")
        self.g_screen_record.setLayout(self.box_g_screen_record)
        # ======== tap 4 ==============================

        self.tab_box = QTabWidget()

        self.tab_box.addTab(self.g_img_to_b64str, "base64转换")
        self.tab_box.addTab(self.g_url_string, "url转换")
        self.tab_box.addTab(self.g_webservice_test, "webservice测试")
        self.tab_box.addTab(self.g_screen_record, "屏幕录制")
        # self.tab_box.setTabEnabled(3, False)

        self.box_v_window = QVBoxLayout()
        self.box_v_window.addWidget(self.tab_box)
        self.box_v_window.addWidget(self.l_tips, alignment=Qt.AlignBottom | Qt.AlignVCenter)

        self.setLayout(self.box_v_window)

        self.resize(900, 500)
        self.setFixedSize(self.size())
        self.setWindowIcon(QIcon(base64_to_pixmap(icon)))
        self.setWindowTitle("Tools v1.0.3 atsushinee@outlook.com/lichun")

    def alert(self, msg):
        def timeout():
            self.l_tips.clear()
            self.timer.stop()

        self.l_tips.setText(msg)
        self.timer.stop()
        self.timer.start(5000)
        self.timer.timeout.connect(timeout)

    def catch_to_alert(self, func):
        try:
            func()
        except Exception as e:
            self.alert(str(e))

    def dragEnterEvent(self, event):
        if self.tab_box.currentIndex() == 0:
            event.acceptProposedAction()

    def dropEvent(self, event):
        file_name = event.mimeData().urls()[0].toLocalFile()
        self.path = file_name
        self.e_img_path.setText(file_name)
        self.img_to_b64str()

    def img_to_b64str(self):
        try:
            with open(self.path, "rb") as f:
                self.e_img_result.clear()
                self.e_img_result.setText(str(base64.b64encode(f.read()), encoding="utf-8"))
        except Exception as e:
            self.alert(str(e))

    def b64str_to_img(self):
        try:
            self.l_img.setPixmap(
                base64_to_pixmap(self.e_img_result.toPlainText()).scaled(300, 270, Qt.KeepAspectRatio))
        except Exception as e:
            self.l_img.clear()
            self.alert(str(e))


class ScreenRecordThread(QThread):
    stop_trigger = pyqtSignal(str, int)
    record_trigger = pyqtSignal()

    def __init__(self):
        super(ScreenRecordThread, self).__init__()
        self.running = False
        self.temp_path = "screen_record_temp"
        self.record_pointer = None
        self.is_pause = False
        self.screen = QApplication.primaryScreen()
        self.full_screen = True
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.record_time = 0

    def run(self):
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)
        os.mkdir(self.temp_path)
        self.running = True
        self.is_pause = False
        i = 1
        t = time.time()
        painter = QPainter()
        pointer_img = base64_to_pixmap(pointer)
        self.record_time = 0
        while self.running:
            start_time = time.time()
            while (not self.is_pause) and self.running:
                if time.time() - start_time > 1:
                    self.record_time += 1
                    self.record_trigger.emit()
                    start_time = time.time()

                if self.full_screen:
                    image = self.screen.grabWindow(0)
                else:
                    image = self.screen.grabWindow(0, self.x, self.y, self.w, self.h)

                if self.record_pointer:
                    x = QCursor.pos().x()
                    y = QCursor.pos().y()
                    if self.full_screen:
                        painter.begin(image)
                        painter.drawPixmap(x, y,
                                           pointer_img.width(), pointer_img.height(), pointer_img)
                        painter.end()
                    else:
                        if (x >= self.x or x <= (self.x + self.w)) and (y >= self.y or y <= (self.y + self.h)):
                            painter.begin(image)
                            painter.drawPixmap(x - self.x, y - self.y,
                                               pointer_img.width(), pointer_img.height(), pointer_img)
                            painter.end()

                image_name = self.temp_path + "/" + str(i) + ".jpg"
                i += 1
                image.save(image_name, "jpg")

        fps = i // (time.time() - t)
        self.stop_trigger.emit(self.temp_path, fps)

    def stop(self):
        self.running = False


class ScreenLabel(QWidget):
    def __init__(self):
        super(ScreenLabel, self).__init__()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.setAcceptDrops(True)
    window.show()
    sys.exit(app.exec_())
