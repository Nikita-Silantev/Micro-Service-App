import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle('Мы с Дениской программисты')
window.setGeometry(100, 100, 600, 400)
helloMsg = QLabel('Кремневая долина, Павел Дуров, Макр Цукерберг, Касперский, вам пизда', parent=window)
helloMsg.move(60, 15)
window.show()
sys.exit(app.exec())