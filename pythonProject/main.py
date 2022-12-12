#-*- encoding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, pyqtSlot, QThread, pyqtSignal, QTimer
from PyQt5 import uic
from PyQt5.QtGui import *
import asyncio
from bleak import BleakClient
import qasync
import threading



address = "A90121EB-4D9E-18BA-A337-68977ECBA813"
notity_charcteristic_uuid = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
iv_value = 0
differ = []
previous_value = 0
diff_avr = 0

# 0 : 블루투스 첫 데이터 전송 이전
# 1 : 블루투스 데이터 전송 시작
# 2 : IV 용량 첫 10% 미만 도달
first_alarm_flag = 0

# ESP32가 notify로 보낸 데이터를 받는 콜백함수
def notify_callback(sender: int, data: bytearray):
    global iv_value
    global first_alarm_flag
    global previous_value
    global differ
    global diff_avr

    print('sender: ', sender, 'data: ', data)
    iv_value = float(data.decode('utf-8'))
    if previous_value != 0:
        differ.append(previous_value - iv_value)
        if len(differ) == 5:
            sum = 0
            for i in differ:
                sum += i
            diff_avr = sum / 5
            differ = []

    previous_value = iv_value

    if first_alarm_flag == 0:
        first_alarm_flag = 1


class Logic(QObject):  # Logic to run in a separate thread
    enabled = False

    @pyqtSlot()
    def start(self):
        self.enabled = True
        asyncio.create_task(self.getBLE(address))

    async def getBLE(self, address):
        async with BleakClient(address) as client:
            services = await client.get_services()
            for service in services:
                for characteristic in service.characteristics:
                    if characteristic.uuid == notity_charcteristic_uuid:
                        print('try to activate notify.')
                        await client.start_notify(characteristic, notify_callback)
                        await asyncio.sleep(100000)

class WorkerThread(QThread):
    def run(self):
        loop = qasync.QEventLoop(self)
        asyncio.set_event_loop(loop)
        loop.run_forever()


form_class = uic.loadUiType("main.ui")[0]

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.timer = QTimer(self)  # timer 변수에 QTimer 할당
        self.timer.start(1000)  # 10000msec(10sec) 마다 반복
        self.timer.timeout.connect(self.update_iv)  # start time out시 연결할 함수

        #self.btn1.clicked.connect(self.btn1Function)
        self.ConnectBtn.clicked.connect(logic.start)


    def update_iv(self):
        global iv_value
        global first_alarm_flag
        global diff_avr

        self.lcd1.display(iv_value)
        if iv_value < 10 and first_alarm_flag == 1:
            self.showDiagram()
            first_alarm_flag = 2

        if diff_avr > 5:
            self.showDiagram1()




    def showDiagram(self):
        text, ok = QInputDialog.getText(self, 'Alarm', '1번 병상 수액 교체 필요')

    def showDiagram1(self):
        text, ok = QInputDialog.getText(self, 'Alarm', '1번 병상 투약 이상 감지')


if __name__ == "__main__" :
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    logic = Logic()
    thread = WorkerThread()
    logic.moveToThread(thread)
    thread.start()

    myWindow = WindowClass()
    # 프로그램 화면을 보여주는 코드
    myWindow.show()
    app.exec_()


