from sqlite3 import dbapi2
from PyQt5.QtWidgets import *
from PyQt5 import uic #ui연결해주는 모듈
import sys
import socket 

sock=socket.create_connection(('10.10.20.33',9015))

class login (QDialog):
    def __init__(self):
        super().__init__() 
        self.ui = uic.loadUi("login.ui", self)     
        
        self.login_button.clicked.connect(self.input_login) 
        self.join_in.clicked.connect(self.join) 


    def input_login(self): 

        sock.send('!login'.encode())
        id=self.idbar.text() 
        pw=self.pwbar.text()
        info=id+'/'+pw

        if self.student.isChecked() : info=info+'/stu'
        elif  self.teacher.isChecked() : info=info+'/tea'

        sock.send(info.encode()) #id,pw,type
        #데이터 베이스에 있는지 서버에서 확인하고 있으면 !ok 없으면 !no
        ch=sock.recv(1024).decode() 
        print(ch) 
        chlist=ch.split('/')
        if chlist[0] =='!ok': #데이터베이스에 있으면 (데이터베이스는 !ok or !no/'stu' or 'tea' 형태로 보냄)
           
            if chlist[1]=='stu':
                print('stu ui 넣는 자리 여기에 넣으십셔!!!!!!')

            elif chlist[1]=='tea':
                self.close() 
                teacherui_show = teacherui()
                teacherui_show.exec_() 
            
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

    def enter(self): 
        self.close() 
        login_show = login() 
        login_show.exec_() 

class teacherui(QDialog):
    def __init__(self):
        super().__init__()
        self.ui=uic.loadUi("teacher.ui",self)   

        
   
if __name__ == '__main__':
    app = QApplication(sys.argv)
    login1 = login() 
    login1.show()
    app.exec()