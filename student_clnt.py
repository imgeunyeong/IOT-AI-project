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

sock=socket.create_connection(('127.0.0.1',9026))



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

    def check_pw(self): # 비번 확인
        id=self.idbar.text()
        pw1=self.pwbar1.text()
        pw2=self.pwbar2.text()

        if pw1==pw2:
            QMessageBox.information(self, 'Message', '축하합니다! 가입이 완료 되었습니다')
            name=self.namebar.text()
            infoall= id + '/' + pw1 + '/' + name + '/'
            
            
            if self.student.isChecked() : infoall=infoall+'stu' # 학생인지 선생님인지 판별
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


class teacherui(QDialog): # 선생님 ui의 흔적
    def __init__(self):
        super().__init__()
        self.ui=uic.loadUi("teacher.ui",self)   


class studentui(QMainWindow): # 학생 ui
    def __init__(self):
        super().__init__()
        self.stu_ui=uic.loadUi("student.ui",self)
        self.setWindowTitle("학생용 클라이언트")
        self.button_click() # 여러가지 작용 함수 더미
        self.icon = QIcon('talk.png') # 프로그램 아이콘 추가 (토크* 에서 가져온 아이콘) (png 파일 없으면 안뜸)
        self.setWindowIcon(self.icon)
        self.study_widget.setEditTriggers(QAbstractItemView.NoEditTriggers) # 학습 테이블 위젯 수정 불가하게 설정
        self.qna_widget.setEditTriggers(QAbstractItemView.NoEditTriggers) # qna 테이블 위젯 수정 불가하게 설정

    def widget_append(self): # 학습자료 추가
        self.stackedWidget.setCurrentIndex(1)
        i = 0
        con = sqlite3.connect("stu_client.db")
        with con: # 데이터베이스 열기
            cur = con.cursor()
            rows = cur.execute('select * from dinosaur')
            for row in rows:
                self.study_widget.setRowCount((i + 1)) # 0번째에 명, 크기, 체중 등이 들어가 있으니 건너뛰고 1번째부터 데이터 추가
                changetype = list(row) # 값을 집어넣기 위해 리스트화
                for j in range(7): # 넣을 값이 7가지 range(7)로 for문 사용
                    self.study_widget.setItem(i, j, QTableWidgetItem(str(changetype[j]))) # i 는 row값 j는 column값
                i += 1 # 1번째 row가 채워지면 다음 row를 채우기 위해 1 씩 증가

    def enter_chatroom(self): # 채팅방으로 이동 및 상담 받고싶은 선생님 입력
        self.stackedWidget.setCurrentIndex(4)
        self.counseling_browser.clear()
        sock.send('!chat'.encode())  # 채팅창 접속 신호 보냄
        super().__init__() # QMainwindow를 상속 받아서 새로 생성
        self.setWindowTitle("상담하고 싶은 선생님 입력 후 ENTER")
        self.setGeometry(400, 400, 400, 100) # mainwindow 위치 설정
        self.setStyleSheet("color: rgb(131, 56, 236); background-color: qlineargradient(spread:pad, x1:0.125, y1:0.892227, x2:0.865, y2:0.130727, stop:0.208333 rgba(128, 106, 174, 255), stop:0.645833 rgba(204, 106, 201, 255));border: 1.5px solid rgb(58, 134, 255);border-radius: 5px;")
        # pyqt에서 스타일 시트 설정 들어가서 내 맘대로 편집한다음에 코드 가져오기
        self.choice_teacher = QLineEdit(self) # 상담할 선생님을 적기 위한 라인 에딧 추가
        self.choice_teacher.setGeometry(60, 25, 280, 50) # 위치지정
        self.choice_teacher.setFont(QFont('Ubuntu', 14)) # 폰트 지정 및 크기 지정
        self.choice_teacher.setStyleSheet("color:black;background-color:lavender;") # 스타일시트
        self.choice_teacher.returnPressed.connect(self.send_choice_msg) # 선생님 이름 적은 후 enter 누를 시 작용
        self.show() # mainwindow 띄우기

    def send_choice_msg(self): # 서버로 실시간 상담 접속 정보를 보냄
        self.close() # 선생님 이름을 적었으니 창을 닫음
        sock.send(f'{self.choice_teacher.text()}'.encode()) # 적었던 상담하고 싶은 선생님 이름 서버로 전송
        self.counseling_browser.append("선생님을 기다리는중...")
        tea_msg = Thread(target=self.recv_msg) # 서버로부터 채팅방 메시지 받는 스레드 구동
        tea_msg.start()

    def recv_msg(self): # 서버에서 실시간 상담 메시지를 받음
        while True:
            a = sock.recv(1024).decode() # 상담 채팅방 메시지 받기
            self.counseling_browser.append(a) # 받은 메시지 브라우저에 추가

    def send_msg(self): # 서버로 실시간 상담 메시지를 보냄
        if self.counseling_line.text() == '': # 빈칸이면 무시
            pass
        else:
            self.counseling_browser.append(self.counseling_line.text()) # 라인에 적은 메시지 내 브라우저에 추가
            sock.send(self.counseling_line.text().encode()) # 라인에 적은 메시지 서버로 전송
            self.counseling_line.clear() # 보낸후 clear

    def quiz_page(self): # 문제만 할당하고 Db에 있는 문제와 답이 일치 할 때 정답처리 리스트에 넣어서 해야하나?
        self.stackedWidget.setCurrentIndex(2)
        sock.send('!question'.encode()) # 서버로 신호 전송

    def qna_page(self): # 페이지 이동하면서 !Q&A 신호 전송
        self.stackedWidget.setCurrentIndex(3)
        sock.send('!Q&A'.encode())

    def upload_question(self): # 질문 학생이 입력시 학생 DB에 저장하면서 서버로 질문을 보내고 테이블 위젯 최신화 (서버에서 답 받아오면 DB에 추가하고 다시 최신화 해야함)
        i = 0  # 학습하기와 동일 range값만 바꿔줌
        con = sqlite3.connect('stu_client.db')
        with con:
            cur = con.cursor()
            cur.execute(f'insert into qna values ("{self.qna_line.text()}", " ")')
            rows = cur.execute('select * from qna')
            for row in rows:
                self.qna_widget.setRowCount((i + 1))
                changetype = list(row)
                for j in range(2):
                    self.qna_widget.setItem(i, j, QTableWidgetItem(str(changetype[j])))
                i += 1
        sock.send(self.qna_line.text().encode())
        self.qna_line.clear()

    def reload(self): # qna 창 새로고침 함수 (서버에서 받아온 값 추가 되었을 때 새로고침)
        i = 0 # 값 초기화 안해주면 여름철 모기처럼 무한 증식
        con = sqlite3.connect('stu_client.db')
        with con:
            cur = con.cursor()
            rows = cur.execute('select * from qna')
            for row in rows:
                self.qna_widget.setRowCount((i + 1))
                changetype = list(row)
                for j in range(2):
                    self.qna_widget.setItem(i, j, QTableWidgetItem(str(changetype[j])))
                i += 1

    def button_click(self): # 여러가지 반응 작용 함수 모음집
        self.study_button.clicked.connect(self.widget_append)
        self.quiz_button.clicked.connect(self.quiz_page)
        self.question_button.clicked.connect(self.qna_page)
        self.chatroom_button.clicked.connect(self.enter_chatroom)
        self.qna_line.returnPressed.connect(self.upload_question)
        self.back_button.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0)) # 흔들리지 않는 편안함 lambda
        self.back_button_2.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.back_button_3.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.back_button_4.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.reload_btn.clicked.connect(self.reload)
        self.counseling_line.returnPressed.connect(self.send_msg)

        header = self.study_widget.horizontalHeader()  # 수평 헤더 반환 # 학습하기 자료 각 칼럼 가장 긴 자료 기준으로 늘림
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.quiz_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 퀴즈 위젯 퀴즈, 답변 칼럼 절반씩 나눈것
        self.qna_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # qna 위젯 question, answer 칼럼 절반씩 나눈것


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login1 = login() #?
    login1.show()
    app.exec()