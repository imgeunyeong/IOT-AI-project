#class login(QDialog)#큐다이얼로그의 기능을 사용하기 위해서 상속받음
from sqlite3 import dbapi2
from PyQt5.QtWidgets import *
from PyQt5 import uic #ui연결해주는 모듈
import sys
import socket
from threading import*

sock=socket.create_connection(('127.0.0.1',9016))
sock_2 = socket.create_connection(('127.0.0.1', 9017))
#sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#sock.connect((IP,port))


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
        id=self.idbar.text() #텍스트창에입력된거 id에 넣고
        sock.send(id.encode()) #서버에 아이디 보내고 중복확인받기 
        ck=sock.recv()
        if ck=='!ok': #서버에서 !ok보내면
            QMessageBox.information(self, 'Message', '사용 가능한 아이디입니다')

        else: QMessageBox.warning(self, 'Warning', '중복된 아이디입니다')

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
        self.setWindowTitle("학습(학생용)")
        self.button_click()
        self.recv_thread = Thread(target=self.chatroom_recv, args=(sock_2,))
        self.recv_thread.start()


    def chatroom_recv(self, s):
            data = s.recv(1024).decode()
            print(data)

    def chatroom_send(self):
            sock_2.send(self.qna_line.text().encode())
            self.qna_line.clear()


    def button_click(self): # 클릭 작용 함수 모음
        self.study_button.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(1))
        self.quiz_button.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(2))
        self.question_button.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(3))
        self.back_button.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.back_button_2.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.back_button_3.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.quiz_line.returnPressed.connect(lambda:self.quiz_browser.append(self.quiz_line.text()))  # 수정 할 예정
        self.qna_line.returnPressed.connect(self.chatroom_send)  # 수정 할 예정




        

   
if __name__ == '__main__':
    app = QApplication(sys.argv)
    login1 = login() #?
    login1.show()
    app.exec()