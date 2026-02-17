import sys
import socket
import json 
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton,  QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QComboBox)
from PyQt6.QtCore import QThread, pyqtSignal

class CalcSocketThread(QThread):
    result_received = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.client_socket = None

    def run(self):
       
        while True:  # Цикл бесконечных попыток подключения
            try:
                # 1. Создаем сокет и пробуем соединиться
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.host, self.port))
                
                # Сообщаем в UI, что связь установлена
                self.result_received.emit("Готов к вычислениям")
                
                # 2. Внутренний цикл ожидания ответов от C#
                while True:
                    data = self.client_socket.recv(1024).decode('utf-8')
                    if not data: 
                        break # Если данные пустые — сервер отключился
                    
                    # Отправляем полученный от C# результат в интерфейс
                    self.result_received.emit(data)
                    
            except Exception as e:
                # 3. Если сервер не найден (WinError 10061) или связь прервалась
                self.result_received.emit(f"Связь... (ошибка: {e})")
                time.sleep(2)  # Ждем 2 секунды перед новой попыткой
                
            finally:
                # 4. Всегда закрываем сокет перед новой попыткой в цикле
                if self.client_socket:
                    self.client_socket.close()

    def send_calc_request(self, n1, n2, op):
        if self.client_socket:
            # Упаковываем данные в формат JSON
            data = {"num1": n1, "num2": n2, "operation": op}
            message = json.dumps(data) 
            self.client_socket.send(message.encode('utf-8'))

class CalculatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Micro Calc ")
        self.setFixedSize(900, 400)
       
        # Поля ввода
        self.num1 = QLineEdit()
        self.num2 = QLineEdit()
        self.op_box = QComboBox()
        self.op_box.addItems(["+", "-", "*", "/"])
        self.result_display = QLineEdit()
        self.result_display.setReadOnly(True)
        
        self.calc_btn = QPushButton("Посчитать в C#")
        self.calc_btn.clicked.connect(self.on_calc_clicked)

        # Верстка
        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.num1)
        h_layout.addWidget(self.op_box)
        h_layout.addWidget(self.num2)
        layout.addLayout(h_layout)
        layout.addWidget(self.calc_btn)
        layout.addWidget(self.result_display)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Сеть
        self.net_thread = CalcSocketThread("127.0.0.1", 5000)
        self.net_thread.result_received.connect(self.show_result)
        self.net_thread.start()

    def on_calc_clicked(self):
        # Берем данные из полей и отправляем в поток
        n1 = self.num1.text()
        n2 = self.num2.text()
        op = self.op_box.currentText()
        self.net_thread.send_calc_request(n1, n2, op)

    def show_result(self, res):
        self.result_display.setText(res)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = CalculatorWindow()
    w.show()
    sys.exit(app.exec())