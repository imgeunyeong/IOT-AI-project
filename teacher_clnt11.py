from calendar import c
from os import ctermid
from posixpath import split
from sqlite3 import dbapi2
from PyQt5.QtWidgets import *
from PyQt5 import uic #ui연결해주는 모듈
from PyQt5.QtCore import *
from PyQt5.QtGui import*
import sys
import socket 
import threading
import time

sock=socket.create_connection(('127.0.0.1',9026))
id=''
serv_msg=''
i=0
k=0


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


class recv(QThread):
         #사용자 정의 시그널 만드는 형식  (str은 emit으로 전달할 데이터의 타입)
    sig = pyqtSignal(str) #사용자 정의 시그널 sig를 만듬 전달할 데이터의 타입이 str이다.
    sig2 = pyqtSignal(str)
    sig3 = pyqtSignal(str)
    def __init__(self): 
        super().__init__()  #쓰레드 쓸려고 상속받음
        print('q쓰레드 확인')
    def run(self):
        while True:
            print('q쓰레드 확인222')
            serv_msg=sock.recv(1024).decode()  
            print(f'서버의메세지: {serv_msg}')
            if serv_msg== '!invite/serv':      #채팅초대
                classinst=teacherui()
                teacherui.request(classinst)
            elif "!quiz" in serv_msg:       #퀴즈출제
                self.sig2.emit(serv_msg)   
            elif "!QnA" in serv_msg:       #QNA
                self.sig3.emit(serv_msg)                

            else:
                self.sig.emit(serv_msg) #serv_msg를 다른 클래스로 전송 emit으로 시그널을 발생시킴
         
                # 전달하고 싶은 데이터가 있으면 데이터를 넣어주고 데이터에 맞는 타입을 정의한다.

class teacherui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui=uic.loadUi("teacher4.ui",self)
        
        self.setWindowTitle("학습(선생용)")
        self.stackedWidget.setCurrentIndex(0) 
        
        print('실행과정확인')

        self.qThread = recv()  
        self.qThread.sig.connect(self.print_data) #sig 라는 이벤트가 발생하면
        self.qThread.sig2.connect(self.recv_quiz) #sig2라는 이벤트가 발생하면 recv_quiz 함수 실행
        self.qThread.sig3.connect(self.recv_QNA) #sig3 라는 이벤트가 발생하면 recv_QNA 함수 실행
       
        self.qThread.demon=True
        self.qThread.start()
        #버튼들
        self.study_button.clicked.connect(self.manage)
        self.quiz_button.clicked.connect(self.make_quiz)
        self.question_button.clicked.connect(self.QNA)
        self.chatroom_button.clicked.connect(self.chatroom)
        self.back_button_4.clicked.connect(self.userExit)#4back추가
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 퀴즈 위젯 퀴즈, 답변 로우 절반씩 나눈것
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) #QNA 위젯 "
        

    @pyqtSlot(str) # 전달 받은 데이터의 타입이 str이다
    def print_data(self, data): # 전달 받은 데이터를 data에 넣는다.
        self.counseling_browser.append(data)#recv한 데이터 상담 화면에 추가
        

    def manage(self):
         print('임시')
         self.stackedWidget.setCurrentIndex(1)
         self.back_button.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
         

    def make_quiz(self):
        print('임시1')
        self.stackedWidget.setCurrentIndex(2)
        sock.sendall("!quiz".encode())
        self.back_button_2.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.tableWidget.setRowCount(10)

        self.quiz_line.returnPressed.connect(self.send_quiz) #등록버튼 누르면

    
    def send_quiz(self): # 전달 받은 데이터를 data에 넣는다.
        quiz=self.quiz_line.text()
        sock.sendall(quiz.encode())
        self.quiz_line.clear()

    @pyqtSlot(str) # 서버에서 !quiz 보내주면 실행됨(sig2 라는 시그널 받으면)
    def recv_quiz(self,data):
        global i
        servdata = data.split('/')
        self.tableWidget.setItem(i, 0, QTableWidgetItem(str(servdata[2]))) #문제    
        #for j in range(0, 1):
        self.tableWidget.setItem(i,1,QTableWidgetItem(str(servdata[3]))) #답 
        i+=1
   

    def QNA(self):
        print('임시')
        self.stackedWidget.setCurrentIndex(3)
        self.back_button_3.clicked.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.tableWidget_2.setRowCount(10)
        sock.send("!QnA".encode()) #서버한테 qna 한다고 보내고   
        self.qna_line.returnPressed.connect(self.send_QNA) #엔터키누르면 
     
    def send_QNA(self):
        QNA=self.qna_line.text()
        sock.sendall(QNA.encode())
        self.tableWidget_2.setItem(self.tableWidget_2.currentRow(),1,QTableWidgetItem(QNA))#입력창에 쓴거 답변창에 바로 등록
        self.qna_line.clear()    
     
    @pyqtSlot(str)
    def recv_QNA(self,data):
        global k
        qnadata=data.split('/')
        #for j in len(qnadata:    
        self.tableWidget_2.setItem(k,0,QTableWidgetItem(str(qnadata[1]))) #질문만등록
        k+=1
    

    def chatroom(self):     
        self.stackedWidget.setCurrentIndex(4)
        self.chat_invite_button.clicked.connect(self.invitemsg)#################팝업창
        sock.sendall("!chat".encode()) 
       

        self.counseling_line.returnPressed.connect(self.send) #학생이름 서버에 보내고
        #serv_msg=sock.recv(1024).decode()
        #print(f'메세지 확인: {serv_msg}')
        ##cThread=threading.Thread(target=self.recv,args=())
        ##cThread.demon=True
        ##cThread.start()
                    
        #cThread=threading.Thread(target=self.recv,args=())
        #cThread.demon=True
        #cThread.start()
        print('확인1')
            
            #self.counseling_line.returnPressed.connect(self.send)      
        

    def send(self):
        self.counseling_browser.append(self.counseling_line.text())
        sock.send(self.counseling_line.text().encode())
        self.counseling_line.clear()


    def userExit(self): #class에 있음
        self.stackedWidget.setCurrentIndex(0)
        self.counseling_browser.clear()
        exitMsg='!quit'
        sock.send(exitMsg.encode())
       # self.qThread.stop()          
    
    def invitemsg(self):  #########################################팝업창부분
        super().__init__() # 추가 QMainwindow 상속받아서 창을 띄우기 위해 추가
        self.setWindowTitle("상담하려는 학생을 입력해주세요")
        self.setGeometry(400, 400, 400, 100)
        self.setStyleSheet(
            "color: rgb(131, 56, 236); background-color: qlineargradient(spread:pad, x1:0.125, y1:0.892227, x2:0.865, y2:0.130727, stop:0.208333 rgba(128, 106, 174, 255), stop:0.645833 rgba(204, 106, 201, 255));border: 1.5px solid rgb(58, 134, 255);border-radius: 5px;")
        self.choice_student = QLineEdit(self) # 학생 선택 choice_student로 변수명 변경
        self.choice_student.setGeometry(60, 25, 280, 50)
        self.choice_student.setFont(QFont('Ubuntu', 14))
        self.choice_student.setStyleSheet("color:black;background-color:lavender;")
        self.choice_student.returnPressed.connect(self.send_msg) # 학생 초대 하면서 열린 초대 창 닫기 위해 함수 연결
        self.show()

    def send_msg(self): # 학생 초대창 닫으면서 서버로 학생 이름 전송
        self.close()
        sock.send(self.choice_student.text().encode())

    def request(self):   #초대 수락거절 팝업창 
        request=ok_no()
        request.exec_()
    

class ok_no(QDialog):
    def __init__(self):
        super().__init__()
        self.ui=uic.loadUi("request.ui",self)
        self.reButton1.clicked.connect(self.send_ok)
        self.reButton2.clicked.connect(self.send_no)
    
    def send_ok(self):
        self.close()
        sock.send("!ok".encode())

    def send_no(self):
        self.close()
        sock.send("!no".encode())    


   
if __name__ == '__main__':
    app = QApplication(sys.argv)
    login1 = login() 
    login1.show()
    app.exec()
    print('메인')


