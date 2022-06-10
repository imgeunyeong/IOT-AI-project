from calendar import c
from os import ctermid
from sqlite3 import dbapi2
from PyQt5.QtWidgets import *
from PyQt5 import uic #ui연결해주는 모듈
from PyQt5.QtGui import*
import sys
import socket 
import threading
import time

sock=socket.create_connection(('127.0.0.1',9025))
id=''
serv_msg=''


class login (QDialog):
    def __init__(self):
        super().__init__() 
        self.ui = uic.loadUi("login.ui", self)     
        
        self.login_button.clicked.connect(self.input_login) 
        self.join_in.clicked.connect(self.join) 


    def input_login(self): 
        global id
        sock.sendall('!login'.encode())
        id=self.idbar.text() 
        pw=self.pwbar.text()
        info=id+'/'+pw

        if self.student.isChecked() : info=info+'/stu'
        elif  self.teacher.isChecked() : info=info+'/tea'

        sock.sendall(info.encode()) #id,pw,type
        #데이터 베이스에 있는지 서버에서 확인하고 있으면 !ok 없으면 !no
        ch=sock.recv(1024).decode() 
        print(ch) 
        chlist=ch.split('/')
        if chlist[0] =='!ok': #데이터베이스에 있으면 (데이터베이스는 !ok or !no/'stu' or 'tea' 형태로 보냄)
           
            if chlist[1]=='stu':
                print('stu ui 넣는 자리')

            elif chlist[1]=='tea':
                self.close() 
                teacherui_show = teacherui()
                teacherui_show.show() 
            
            else: QMessageBox.warning(self, 'Warning', '아이디,비밀번호를 확인해주세요')
        
        
    def join(self): 
        sock.send('!signup'.encode()) 
        self.close() 
        regit_show = regit()
        regit_show.exec_() 
        
        

class regit(QDialog): #가입창 
   
    def __init__(self):
        super().__init__()
        self.ui=uic.loadUi("regit.ui",self)       

        self.id_chk.clicked.connect(self.check_id)
        self.regit_button.clicked.connect(self.check_pw) 

    def check_id(self): 
        id=self.idbar.text() #텍스트창에입력된거 id에 넣고
        sock.send(id.encode()) #서버에 아이디 보내고 중복확인받기 
        ck=sock.recv(1024).decode()
        print(ck)
        if ck=='!ok': #서버에서 !ok보내면
            QMessageBox.information(self, 'Message', '사용 가능한 아이디입니다')
            self.regit_button.setEnabled(True)
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

    def enter(self): 
        self.close() 
        login_show = login() 
        login_show.exec_() 

class teacherui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui=uic.loadUi("teacher2.ui",self)
        
        self.setWindowTitle("학습(선생용)")
        self.stackedWidget.setCurrentIndex(0) #

        self.study_button.clicked.connect(self.manage)
        self.quiz_button.clicked.connect(self.make_quiz)
        self.question_button.clicked.connect(self.QNA)
        self.chatroom_button.clicked.connect(self.chatroom)
        self.back_button_4.clicked.connect(self.userExit)#4back추가


    def manage(self):
         self.stackedWidget.setCurrentIndex(1)
         self.back_button.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
         

    def make_quiz(self):
        print('임시')
        self.stackedWidget.setCurrentIndex(2)
        self.back_button_2.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))

        self.quiz_line.returnPressed.connect(lambda:self.quiz_browser.append(self.quiz_line.text()))
        #sock.send(self.quiz_line.text().encode())
   
    def QNA(self):
        print('임시')
        self.stackedWidget.setCurrentIndex(3)
        self.back_button_3.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        #sock.send(!qna) #서버한테 qna 한다고 보내고
        #studentQ=sock.recev().decode.() #학생 질문 서버한테 받음
        #서버한테 받은 질문 띄우기 근데 이 형식이 아닌데
        self.qna_browser.append(self.studentQ.text())
        self.qna_line.returnPressed.connect(lambda:self.qna_browser.append(self.qna_line.text()))#qna채팅을화면에띄우게 추가
        #sock.send(qna_line.text().encode())
        #QMessageBox.information(self, 'Message', '답변을 등록했습니다')
        

    def chatroom(self):     
        self.stackedWidget.setCurrentIndex(4)
        self.chat_invite_button.clicked.connect(self.invitemsg)#################팝업창
        sock.sendall("!chat".encode()) 
       # sock.sendall('1003'.encode())  


        self.counseling_line.returnPressed.connect(self.send) #학생이름 서버에 보내고
        cThread=threading.Thread(target=self.recv,args=())
        cThread.demon=True
        cThread.start()
        
        if serv_msg== '!invite':  #'!invite'받으면 
            sock.send('!ok'.encode()) #서버에 다시 '!ok'보내주기         
        #cThread=threading.Thread(target=self.recv,args=())
        #cThread.demon=True
        #cThread.start()
        print('확인1')
            
            #self.counseling_line.returnPressed.connect(self.send)      
        

    def send(self):
        self.counseling_browser.append(self.counseling_line.text())
        sock.send(self.counseling_line.text().encode())
        self.counseling_line.clear()


    def recv(self):
        while(1):
            print('쓰레드 확인')
            serv_msg=sock.recv(1024).decode()    
            print(f'서버의메세지: {serv_msg}')
            self.counseling_browser.append(serv_msg)

    def userExit(self): #class에 있음
        self.stackedWidget.setCurrentIndex(0)
       # exitMsg='!quit'
        #sock.send(exitMsg.encode())
        self.cThread.join()          

    def invitemsg(self):    #########################################팝업창부분
        self.setWindowTitle("상담하려는 학생을 입력해주세요")
        self.setGeometry(400, 400, 400, 100)
        self.setStyleSheet("color: rgb(131, 56, 236); background-color: qlineargradient(spread:pad, x1:0.125, y1:0.892227, x2:0.865, y2:0.130727, stop:0.208333 rgba(128, 106, 174, 255), stop:0.645833 rgba(204, 106, 201, 255));border: 1.5px solid rgb(58, 134, 255);border-radius: 5px;")
        self.choice_teacher = QLineEdit(self)
        self.choice_teacher.setGeometry(60, 25, 280, 50)
        self.choice_teacher.setFont(QFont('Ubuntu', 14))
        self.choice_teacher.setStyleSheet("color:black;background-color:lavender;")
        self.choice_teacher.returnPressed.connect(sock.send(self.msg_line.text().encode()))
        self.show()
            

   
      
   
if __name__ == '__main__':
    app = QApplication(sys.argv)
    login1 = login() 
    login1.show()
    app.exec()