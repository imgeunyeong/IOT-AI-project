import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic


#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("qt.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        
        self.btn1.clicked.connect(self.print)
        self.btn2.clicked.connect(self.clear)
        self.btn3.clicked.connect(self.font)
        self.btn4.clicked.connect(self.italic)
        self.btn5.clicked.connect(self.color)
        self.btn6.clicked.connect(self.up)
        self.btn7.clicked.connect(self.down)

    def print(self) :
        print(self.textedit.toPlainText())

    def clear(self) :
        self.textedit.clear()

    def font(self) :
        fontvar = QFont("Apple SD Gothic Neo",10)
        self.textedit.setCurrentFont(fontvar)

    def italic(self) :
        self.textedit.setFontItalic(True)

    def color(self) :
        colorvar = QColor(255,0,0)
        self.textedit.setTextColor(colorvar)

    def up(self) :
        self.fontSize = self.fontSize + 1
        self.textedit.setFontPointSize(self.fontSize)

    def down(self) :
        self.fontSize = self.fontSize - 1
        self.textedit.setFontPointSize(self.fontSize)

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
