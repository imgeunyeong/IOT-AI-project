#class login(QDialog)#큐다이얼로그의 기능을 사용하기 위해서 상속받음
from sqlite3 import dbapi2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import*
from PyQt5.QtCore import*
from PyQt5 import uic #ui연결해주는 모듈
import sys
import socket
from threading import*
import sqlite3
import datetime

sock=socket.create_connection(('127.0.0.1',9020))



class login (QDialog):
    def __init__(self):
        super().__init__() #super가 q다이얼로그임
        self.ui = uic.loadUi("login.ui", self)     
        
        self.login_button.clicked.connect(self.input_login) #pushButton 클릭시 연결하는 함수
        self.join_in.clicked.connect(self.join) #회원가입 버튼 클릭할때 실행되는 함수


    def input_login(self): #실행확인용함수

        sock.send('!login'.encode())
        id=self.idbar.text() #텍스트 가져옴
        pw=self.pwbar.text()
        info=id+'/'+pw

        if self.student.isChecked() : 
            info=info+'/stu'
        elif  self.teacher.isChecked() : 
            info=info+'/tea'

        sock.send(info.encode()) #id,pw,type
        #데이터 베이스에 있는지 서버에서 확인하고 있으면 !ok 없으면 !no
        ch=sock.recv(1024).decode() #여기서 디코드 
        print(ch) 
        chlist=ch.split('/')
        if chlist[0] =='!ok': #데이터베이스에 있으면 (데이터베이스는 !ok or !no/'stu' or 'tea' 형태로 보냄)
            print(f' 1 : {chlist}')
            if chlist[1]=='stu':
                self.close()
                student_show = studentui()
                student_show.show()

            elif chlist[1]=='tea':
                self.close() #로그인ui를닫음(self가 현재 login class임)
                teacherui_show = teacherui() # 클래스담고
                teacherui_show.exec_() #클래스실행(가입창)
            
            else: QMessageBox.warning(self, 'Warning', '아이디,비밀번호를 확인해주세요')
        
        
    def join(self):  #가입창 함수
        sock.send('!signup'.encode()) #서버에 사인업 명령어 보냄 
        self.close() #로그인ui를닫음(self가 현재 login class임)
        regit_show = regit() # 클래스담고
        regit_show.exec_() #클래스실행(가입창)
        
        

class regit(QDialog): #가입창 
    def __init__(self):
        super().__init__()
        self.ui=uic.loadUi("regit.ui",self)       

        #이벤트
        self.id_chk.clicked.connect(self.check_id)
        self.regit_button.clicked.connect(self.check_pw) #이게 눌렀을떄 연결임
               

    def check_id(self):
        id = self.idbar.text()  # 텍스트창에입력된거 id에 넣고
        sock.send(id.encode())  # 서버에 아이디 보내고 중복확인받기
        ck = sock.recv(1024).decode()
        print(ck)
        if ck == '!ok':  # 서버에서 !ok보내면
            QMessageBox.information(self, 'Message', '사용 가능한 아이디입니다')
            self.regit_button.setEnabled(True)
        else:
            QMessageBox.warning(self, 'Warning', '중복된 아이디입니다')

    def check_pw(self):
        id=self.idbar.text()
        pw1=self.pwbar1.text()
        pw2=self.pwbar2.text()

        if pw1==pw2:
            QMessageBox.information(self, 'Message', '축하합니다! 가입이 완료 되었습니다')
            name=self.namebar.text()
            infoall= id + '/' + pw1 + '/' + name + '/'
            
            
            if self.student.isChecked() : infoall=infoall+'stu'
            elif self.teacher.isChecked() :
                infoall=infoall+'tea'
            sock.sendall(infoall.encode())
            self.enter()

        else:
            QMessageBox.warning(self, 'Warning', '비밀번호를 잘못 입력했습니다')

    def enter(self):  #가입창 함수 
        self.close() #로그인ui를닫음(self가 현재 login class임)
        login_show = login() # 클래스담고
        login_show.exec_() #클래스실행(가입창)
        sock.send('!login'.encode())


class teacherui(QDialog):
    def __init__(self):
        super().__init__()
        self.ui=uic.loadUi("teacher.ui",self)   


class studentui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stu_ui=uic.loadUi("student.ui",self)
        self.setWindowTitle("학생용 클라이언트")
        self.button_click()
        self.icon = QIcon('talk.png')
        self.setWindowIcon(self.icon)
        self.study_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)


    def widget_append(self): # 학습자료 추가
        self.stackedWidget.setCurrentIndex(1)
        i = 0
        con = sqlite3.connect("stu_client.db")
        with con:
            cur = con.cursor()
            rows = cur.execute('select * from dinosaur')
            for row in rows:
                self.study_widget.setRowCount((i + 1))
                changetype = list(row)
                for j in range(7):
                    self.study_widget.setItem(i, j, QTableWidgetItem(str(changetype[j])))
                i += 1

    def enter_chatroom(self): # 채팅방으로 이동 및 상담 받고싶은 선생님 입력
        self.stackedWidget.setCurrentIndex(4)
        super().__init__()
        self.setWindowTitle("상담하고 싶은 선생님 입력 후 ENTER")
        self.setGeometry(400, 400, 400, 100)
        self.setStyleSheet("color: rgb(131, 56, 236); background-color: qlineargradient(spread:pad, x1:0.125, y1:0.892227, x2:0.865, y2:0.130727, stop:0.208333 rgba(128, 106, 174, 255), stop:0.645833 rgba(204, 106, 201, 255));border: 1.5px solid rgb(58, 134, 255);border-radius: 5px;")
        self.choice_teacher = QLineEdit(self)
        self.choice_teacher.setGeometry(60, 25, 280, 50)
        self.choice_teacher.setFont(QFont('Ubuntu', 14))
        self.choice_teacher.setStyleSheet("color:black;background-color:lavender;")
        self.choice_teacher.returnPressed.connect(self.send_choice_msg)
        self.show()

    def send_choice_msg(self): # 서버로 실시간 상담 접속 정보를 보냄
        self.close()
        sock.send('!chat'.encode())
        sock.send(f'{self.choice_teacher.text()}'.encode())
        self.counseling_browser.append("선생님을 기다리는중...")
        tea_msg = Thread(target=self.recv_msg)
        tea_msg.start()

    def recv_msg(self): # 서버에서 실시간 상담 메시지를 받음
        while True:
            a = sock.recv(1024).decode()
            self.counseling_browser.append(a)

    def send_msg(self): # 서버로 실시간 상담 메시지를 보냄
        if self.counseling_line.text() == '':
            pass
        else:
            self.counseling_browser.append(self.counseling_line.text())
            sock.send(self.counseling_line.text().encode())
            self.counseling_line.clear()

    def quiz_page(self): # 문제만 할당하고 Db에 있는 문제와 답이 일치 할 때 정답처리 리스트에 넣어서 해야하나?
        self.stackedWidget.setCurrentIndex(2)

    def upload_question(self): # 데이터 베이스에서 가져와야 함 질문을 학생 데이터베이스에 저장하면서 서버로 보내고 서버에서는 답변을 받아와서 데이터베이스에 추가를 하면서 테이블 위젯에 띄우기
        con = sqlite3.connect('stu_client.db')
        cur = con.cursor()
        cur.execute(f'insert into qna (question) value ({self.qna_line.text()}')
        con.commit()
        con.close()

    def button_click(self): # 여러가지 반응 작용 함수 모음집
        self.study_button.clicked.connect(self.widget_append)
        self.quiz_button.clicked.connect(self.quiz_page)
        self.question_button.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(3))
        self.chatroom_button.clicked.connect(self.enter_chatroom)
        self.qna_line.returnPressed.connect(self.upload_question)
        self.back_button.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.back_button_2.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.back_button_3.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.back_button_4.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.counseling_line.returnPressed.connect(self.send_msg)

        header = self.study_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.quiz_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.qna_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login1 = login() #?
    login1.show()
    app.exec()