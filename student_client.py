#class login(QDialog)#큐다이얼로그의 기능을 사용하기 위해서 상속받음
from PyQt5.QtWidgets import *
from PyQt5.QtGui import*
from PyQt5.QtCore import*
from PyQt5 import uic #ui연결해주는 모듈
import sys
import socket
from threading import*
import sqlite3
from time import*

sock=socket.create_connection(('127.0.0.1',9020))



class login (QDialog):
    def __init__(self):
        super().__init__() #super가 q다이얼로그임
        self.ui = uic.loadUi("login.ui", self)
        
        self.login_button.clicked.connect(self.input_login) #pushButton 클릭시 연결하는 함수
        self.join_in.clicked.connect(self.join) #회원가입 버튼 클릭할때 실행되는 함수

    def input_login(self): #실행확인용함수
        global id
        sock.sendall('!login'.encode())
        id = self.idbar.text() #텍스트 가져옴
        pw = self.pwbar.text()
        info = id + '/' + pw

        if self.student.isChecked() : 
            info = info + '/stu'
        elif self.teacher.isChecked() :
            info = info + '/tea'

        sock.sendall(info.encode()) #id,pw,type
        # 데이터 베이스에 있는지 서버에서 확인하고 있으면 !ok 없으면 !no
        ch = sock.recv(1024).decode() #여기서 디코드
        print(ch) 
        chlist = ch.split('/')
        if chlist[0] == '!ok': #데이터베이스에 있으면 (데이터베이스는 !ok or !no/'stu' or 'tea' 형태로 보냄)
            if chlist[1] == 'stu':
                self.close()
                student_show = studentui()
                student_show.show()

            elif chlist[1]=='tea':
                print("teacher.ui 넣는 자리")
            
            else:
                QMessageBox.warning(self, 'Warning', '아이디,비밀번호를 확인해주세요')

    def join(self):
        sock.send('!signup'.encode())
        self.close()
        regit_show = regit()
        regit_show.exec_()
        

class regit(QDialog): #가입창 
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("regit.ui",self)

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
        id = self.idbar.text()
        pw1 = self.pwbar1.text()
        pw2 = self.pwbar2.text()

        if pw1 == pw2:
            QMessageBox.information(self, 'Message', '축하합니다! 가입이 완료 되었습니다')
            name = self.namebar.text()
            infoall = id + '/' + pw1 + '/' + name + '/'

            if self.student.isChecked():
                infoall = infoall + 'stu' # 학생인지 선생님인지 판별
            elif self.teacher.isChecked():
                infoall = infoall + 'tea'
            sock.sendall(infoall.encode())
            self.enter()

        else:
            QMessageBox.warning(self, 'Warning', '비밀번호를 잘못 입력했습니다')

    def enter(self):  #가입창 함수 
        self.close() #로그인ui를닫음(self가 현재 login class임)
        login_show = login() # 클래스담고
        login_show.exec_() #클래스실행(가입창)


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
        self.main_page_label.setPixmap(QPixmap("image/항목선택.png"))
        self.study_page_label.setPixmap(QPixmap("image/스터디.png"))
        self.quiz_page_label.setPixmap(QPixmap("image/문제풀이.png"))
        self.qna_page_label.setPixmap(QPixmap("image/QnA.png"))
        self.counseling_page_label.setPixmap(QPixmap("image/상담.png"))
        self.study_widget.setEditTriggers(QAbstractItemView.NoEditTriggers) # 학습 테이블 위젯 읽기 모드로 변경 (수정모드로 바꾸려면 NoEdit --> AllEdit 으로 변경)
        self.qna_widget.setEditTriggers(QAbstractItemView.NoEditTriggers) # qna 테이블 위젯 읽기 모드로 변경
        self.quiz_list = [] # 퀴즈 문제 담기용 리스트
        self.answer_list = [] # 퀴즈 답 담기용 리스트
        self.q_list = [] # 질문 담기용 리스트
        self.a_list = [] # 답변 담기용 리스트
        self.final_answer_list = [] # 학생이 적은 답 담기 리스트
        self.score = 0 # 학생이 푼 문제 점수 할당용
        self.timer = QTimer(self) # 문제풀이 제한시간용 타이머
        self.time_mm = 19 # 제한시간 분 설정
        self.time_ss = 60 # 제한시간 초 설정
        self.qna_count =0 # qna 카운트
        self.quiz_count = 0 # 퀴즈 카운트
        self.count_quiz = 0 # 맞춘 문제 수 카운트
        tea_msg = Thread(target=self.recv_msg)  # 서버로부터 채팅방 메시지 받는 스레드 구동
        tea_msg.start()

    def widget_append(self): # 학습자료 추가
        self.stackedWidget.setCurrentIndex(1)
        i = 0
        con = sqlite3.connect("stu_client.db")
        with con: # 데이터베이스 열기
            cur = con.cursor()
            rows = cur.execute('select * from dinosaur')
            for row in rows:
                self.study_widget.setRowCount((i + 1)) # 행의 길이 지정 (행이랑 열의 개념을 잘못 알고 있었던 나)
                changetype = list(row) # 값을 집어넣기 위해 리스트화
                print(changetype)
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

    def recv_msg(self): # 서버에서 메시지 받음
        while True:
            msg = sock.recv(1024).decode()
            print(msg)
            r_msg = msg.split('/')
            if msg == '!invite/serv':
                invite = QMessageBox.information(self, "채팅 초대", "초대가 도착했습니다\n수락하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
                if invite == QMessageBox.Yes:
                    sock.send("!ok".encode())
                    self.stackedWidget.setCurrentIndex(4)
                    sleep(1)
                    sock.send('!chat'.encode())  # 채팅창 접속 신호 보냄
                else:
                    sock.send("!no".encode())
            elif r_msg[0] == '!QnA': # r_msg[1], r_msg[2] 넣어야 함 반복문으로 추가
                print("성공")
                self.qna_count+=1
                self.qna_widget.setRowCount(self.qna_count)
                self.qna_widget.setItem(self.qna_count-1, 0, QTableWidgetItem(r_msg[2]))# [1/q/a]
                self.qna_widget.setItem(self.qna_count-1, 1, QTableWidgetItem(r_msg[3]))
            elif r_msg[0] == '!quiz':
                print("성공")
                self.quiz_count += 1
                self.quiz_widget.setRowCount(self.quiz_count)
                self.quiz_widget.setItem(self.quiz_count-1, 0, QTableWidgetItem(r_msg[2]))
                self.quiz_list.append(r_msg[2])
                self.answer_list.append(r_msg[3])
            else:
                self.counseling_browser.append(msg)  # 받은 메시지 브라우저에 추가

    def send_msg(self): # 서버로 실시간 상담 메시지를 보냄
        if self.counseling_line.text() == '': # 빈칸이면 무시
            pass
        else:
            self.counseling_browser.append(self.counseling_line.text()) # 라인에 적은 메시지 내 브라우저에 추가
            sock.send(self.counseling_line.text().encode()) # 라인에 적은 메시지 서버로 전송
            self.counseling_line.clear() # 보낸후 clear

    def quiz_page(self): # 문제만 할당하고 Db에 있는 문제와 답이 일치 할 때 정답처리 리스트에 넣어서 해야하나?
        self.stackedWidget.setCurrentIndex(2)
        self.quiz_count = 0
        sock.send('!quiz'.encode()) # 서버로 신호 전송
        self.quiz_start_btn.clicked.connect(self.quiz_start) # 퀴즈 페이지로 넘어온 신호랑 겹칠거 같아서 분리 (시작버튼 누르면 넘어감)

    def quiz_start(self): # 시작 버튼 누르면 퀴즈 할당
        self.back_button_2.setEnabled(False) # 돌아가기 버튼 비활성화
        start = QMessageBox.information(self, "문제 풀이", "제한시간은 20분입니다\n시작합니다!", QMessageBox.Yes)
        if start == QMessageBox.Yes:
            self.timer.start(1000) # 1초마다 타이머 작동
            self.timer.timeout.connect(self.time_time) # 1초마다 타이머 작동 함수 연결
            self.quiz_start_btn.setEnabled(False) # 시작 버튼 비활성화 # 활성화 비활성화 구분이 안가요 기능구현 끝나면 손봐야 할듯?
            self.quiz_complete_btn.setEnabled(True) # 제출 버튼 활성화
            self.score = 0 # 점수 초기화
            self.lcdNumber.display(self.score) # 점수 표시 디스플레이

    def complete(self): # 문제 풀이 후 제출 완료
        self.back_button_2.setEnabled(True)  # 돌아가기 버튼 활성화
        self.quiz_start_btn.setEnabled(True)  # 시작 버튼 활성화
        self.quiz_complete_btn.setEnabled(False)  # 제출 버튼 비활성화
        self.timer.stop() # 문제 풀이 완료 타이머 스탑
        check_time = self.time_mm * 60 + self.time_ss
        print(check_time)
        for i in range(self.quiz_widget.rowCount()): # 퀴즈 위젯의 행 카운트
            answer = self.quiz_widget.item(i, 1) # 퀴즈 위젯에 적은 답을 가져옴
            try:
                final_ans = answer.text() # 텍스트로 변경 후 지정
                self.final_answer_list.append(final_ans) # 텍스트로 변경 된 답 리스트에 추가
            except:
                self.final_answer_list.append('') # 추가할 답이 없다면 빈칸으로 리스트에 추가 (없으면 오류 남)
            if self.answer_list[i] == self.final_answer_list[i]: # 문제 할당 할 때 넣어놓은 답 리스트와 학생이 적은 답 리스트 비교
                print(f'{i + 1}번 정답')
                self.score += 5  # 20문제 기준 1문제 당 5점 추가
                self.lcdNumber.display(self.score) # 점수 표시
                self.count_quiz += 1
            else:
                print(f'{i + 1}번 오답') # 오답이야~

        if -1 < self.score < 20: # 각 점수별로 뜨는 메시지 박스 (그냥 만들긴 했는데 필요있는지는 모르겠구요)
            QMessageBox.information(self, "놀았니?", f'{self.score}점\n공부 안했나요?')
        elif 19 < self.score < 40:
            QMessageBox.information(self, "공부해라", f'{self.score}점\n아직 멀었네요')
        elif 39 < self.score < 60:
            QMessageBox.information(self, "아쉬워요", f'{self.score}점\n합격하지 못했어요')
        elif 59 < self.score < 80:
            QMessageBox.information(self, "합격!", f'{self.score}점\n합격했습니다!')
        elif 79 < self.score < 101:
            QMessageBox.information(self, "선생님은 만족했다", f'{self.score}점')
        sock.send(f'{self.count_quiz}/{len(self.quiz_list)}/{check_time}'.encode())
        self.time_mm = 19  # 변수 값 초기화
        self.time_ss = 60
        self.timer_label.setText("20 : 00")  # 라벨 텍스트 재설정
        self.quiz_widget.setRowCount(0)

    def qna_page(self): # 페이지 이동하면서 !Q&A 신호 전송
        self.qna_count = 0
        self.stackedWidget.setCurrentIndex(3)
        sock.send('!QnA'.encode())

    def time_time(self): # 문제 풀이 타이머
        if self.time_ss == 0: # 초가 -1로 바뀔때 값 재설정
            self.time_ss = 59
            self.time_mm -= 1
            self.timer_label.setText(f'{self.time_mm} : {self.time_ss}')
        elif self.time_ss < 11: # 초가 1자리로 바뀔 때 부터 0을 붙여서 출력하기 위한 것
            self.time_ss -= 1
            self.timer_label.setText(f'{self.time_mm} : 0{self.time_ss}')
        else:
            self.time_ss -= 1
            self.timer_label.setText(f'{self.time_mm} : {self.time_ss}')
        if self.time_mm == 0 and self.time_ss == -1: # 시간이 다 되었을때 타이머 멈추고 값 초기화
            QMessageBox.information(self, "시간종료","다음에 다시 풀어보세요")
            self.timer.stop()
            self.time_mm = 19
            self.time_ss = 60
            self.timer_label.setText("20 : 00")

    def upload_question(self): # 질문 학생이 입력시 학생 DB에 저장하면서 서버로 질문을 보내고 테이블 위젯 최신화 (서버에서 답 받아오면 DB에 추가하고 다시 최신화 해야함)
        if self.qna_line.text() == '':
            pass
        else:
            check = QMessageBox.information(self, "질문 등록", f'<{self.qna_line.text()}>\n등록하시는 질문이 맞나요?', QMessageBox.Yes | QMessageBox.No)
            if check == QMessageBox.Yes:
                sock.send(f'!update{self.qna_line.text()}'.encode())  # 서버로 질문 내용 전송
                sleep(0.5)
                sock.send(self.qna_line.text().encode()) # 질문 내용 서버로 전송
                self.qna_line.clear()
                QMessageBox.information(self, "등록완료", "질문이 등록되었습니다", QMessageBox.Yes)
            else:
                QMessageBox.information(self, "미 등록","질문을 다시 입력해주세요", QMessageBox.Yes)
                self.qna_line.clear()

    def reload(self): # qna 창 새로고침 함수 (서버에서 받아온 값 추가 되었을 때 새로고침) #########################수정
        exitMsg = '!quit'
        sock.send(exitMsg.encode())
        sleep(0.5)
        self.qna_count = 0
        sock.send('!Q&A'.encode())

    def test(self): # 테스트용 함수
        print("test1")

    def button_click(self): # 여러가지 반응 작용 함수 모음집
        self.study_button.clicked.connect(self.widget_append)
        self.quiz_button.clicked.connect(self.quiz_page)
        self.question_button.clicked.connect(self.qna_page)
        self.chatroom_button.clicked.connect(self.enter_chatroom)
        self.qna_line.returnPressed.connect(self.upload_question)
        self.qna_pushbutton.clicked.connect(self.upload_question)
        self.quiz_complete_btn.clicked.connect(self.complete)
        self.back_button.clicked.connect(self.userExit)
        self.back_button_2.clicked.connect(self.userExit)
        self.back_button_3.clicked.connect(self.userExit)
        self.back_button_4.clicked.connect(self.userExit)
        self.reload_btn.clicked.connect(self.reload)
        self.counseling_line.returnPressed.connect(self.send_msg)
        self.c_button.clicked.connect(self.send_msg)
        self.quiz_complete_btn.setEnabled(False) # 퀴즈 시작 버튼 누르기 전까지 제출버튼 비활성화

        header = self.study_widget.horizontalHeader()  # 수평 헤더 반환 # 학습하기 자료 각 칼럼 가장 긴 자료 기준으로 늘림
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.quiz_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 퀴즈 위젯 퀴즈, 답변 column 절반씩 나눈것
        self.qna_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # qna 위젯 question, answer column 절반씩 나눈것

    def userExit(self): # 선택 메뉴로 이동
        self.stackedWidget.setCurrentIndex(0)
        self.counseling_browser.clear()
        exitMsg = '!quit'
        sock.send(exitMsg.encode())
        self.quiz_widget.setRowCount(0)
        self.qna_widget.setRowCount(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login1 = login() #?
    login1.show()
    app.exec()