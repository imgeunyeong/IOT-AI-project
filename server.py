from collections import UserDict
from concurrent.futures import thread
import socket
import threading
import sqlite3
import sys

BUFSIZE = 1024 #버퍼사이즈
host = '10.10.20.33' 
port = 9020
userInfo = [] #로그인 성공시 유저 정보 저장 
usercnt = 0 #연결 유저 카운트
QnAnum = 1
lock=threading.Lock()

def getcon(): #db와 연결 함수
    con = sqlite3.connect('edu.db') #db연결
    c=con.cursor() #커서획득
    return con, c #커서 반환

def recv_msg(sock): #메세지 수신 함수
    sys.stdout.flush()  # 버퍼 비우기
    clnt_msg = sock.recv(BUFSIZE)  # 메세지 받아오기
    clnt_msg = clnt_msg.decode()  # 디코딩
    return clnt_msg #받은 메세지 반환


def send_msg(sock, msg): #메세지 송신 함수
    sys.stdin.flush()  # 버퍼 비우기
    msg = msg.encode()  # 인코딩
    sock.send(msg)  # 메세지 보내기

def findNum(sock): #클라이언트 번호 찾는 함수
    for i in range(0, usercnt): 
        if userInfo[i][0] == sock:
            break
    return i

def delete_userInfo(sock): # 유저정보 삭제 함수
    global usercnt
    for i in range(0, usercnt):
        if sock == userInfo[i][0]: #종료요청한 클라이언트 찾기
            print('exit')
            while i <usercnt-1: #종료한 클라이언트 뒤의 클라이언트 정보 한칸씩 당겨오기
                userInfo[i]=userInfo[i+1]
                i+=1
            break
    usercnt-=1 #종료했으니 총 유저수 -1
   
def signup(sock): #회원가입 처리 함수
    con, c = getcon()
    while True:
        data = recv_msg(sock) #ID 받기
        print('data: '+data)
        c.execute('select t.ID, s.ID from teacherInfo t, studentInfo s where t.ID = ? or s.Id = ?',(data,data)) #db에서 해당 아이디 있나 중복확인
        find = c.fetchone()       
        print(find)
        if find == None: #중복없으면
            send_msg(sock, '!ok') #클라한테 메세지 전송
            break
        else:
            send_msg(sock, '!no') #클라한테 메세지 전송
            continue #아이디 다시 받기
    data = recv_msg(sock) #/구분자로 ID, PW, Name, type 받기
    print('data: '+data)
    userdata = data.split('/') #/기준으로 문자열 나누기
    print('data[3]: '+userdata[3])
    
    if userdata[3] == 'tea': #선생님
        c.execute('insert into teacherInfo (ID, PW, Name, type) values (?, ?, ?, ?)', (userdata[0], userdata[1], userdata[2], userdata[3])) #선생 테이블에 데이터 저장
        con.commit()
        con.close()
        print('succes 회원가입')
        
    elif userdata[3] == 'stu': #학생
        c.execute('insert into studentInfo (ID, PW, Name, type) values (?, ?, ?, ?)', (userdata[0], userdata[1], userdata[2], userdata[3])) #학생 테이블에 데이터 저장
        con.commit()
        con.close()
        print('succes 회원가입')

def login(sock): #로그인 처리 함수
    global usercnt
    con, c = getcon() #커서획득
    
    #lock.acquire()
    while True:
        data = recv_msg(sock) #/구분자로 ID, PW 받기
        #clnt_num = findNum(sock)
        print('data: '+data)
        userdata = data.split('/') # /기준으로 문자열 나누기
        print('data[2]: '+userdata[2])
        
        if userdata[2] == 'tea': #선생님
            print('userID: '+userdata[0])
            print('userPW: '+userdata[1])
            c.execute('select PW from teacherInfo where ID = ?', (userdata[0],)) #선생 테이블에서 정보 찾기
            dbPW = c.fetchone()
            dbPW = ''.join(dbPW) #문자열로 바꾸기
            print(dbPW)
        elif userdata[2] == 'stu': #학생
            print('userID: '+userdata[0])
            print('userPW: '+userdata[1])
            c.execute('select PW from studentInfo where ID = ?', (userdata[0],)) #학생 테이블에서 정보 찾기
            dbPW = c.fetchone()
            dbPW = ''.join(dbPW) #문자열로 바꾸기
            print(dbPW)
            
        if userdata[1] == dbPW: #db 정보랑 보낸 정보랑 일치시
            if userdata[2] == 'tea': #type이 선생님이면
                msg='!ok/tea/serv' #클라한테 메세지 전송
            elif userdata[2] == 'stu': #type이 학생이면
                msg ='!ok/stu/serv' #클라한테 메세지 전송
            send_msg(sock, msg) #성공시 !ok 보내기
            # userInfo[clnt_num][1] = userdata[0] #로그인때 저장한 데이터 수정
            # userInfo[clnt_num][2] = userdata[2]
            userInfo.insert(usercnt, [sock, userdata[0], userdata[2], 0]) #sock, ID, type, 채팅속성 로그인시 저장
            usercnt += 1 #로그인 성공시 접속 유저수 +1
            print('sucess 로그인: ')
            print(userInfo[usercnt-1]) 
            con.close()
            break
        else:
            send_msg(sock, '!no/tea') #실패시 !no 보내기
            print('fail')
            continue   
    #lock.release()   

def chatmode(sock): #상담 요청 받아서 해당 클라이언트 속성 변경
    #수정중
    con, c = getcon() #db 커서 가져오고
    clnt_num = findNum(sock) #클라이언트 번호 가져오기
    if userInfo[clnt_num][2] == 'tea': # 선생님
        print('선생님')
        name = recv_msg(sock) #학생이름 받아오기
        print('name: '+name)
        c.execute('select ID from studentInfo where Name = ?', (name,)) #학생이름으로 db에서 아이디 찾기
        find = c.fetchone()
        if not find: #찾는 사람이 없으면
            send_msg(userInfo[clnt_num][0], '!no/serv') #클라한테 메세지전송
            con.close()
            return
        find = ''.join(find) #문자열로 바꿔주고
        print(find)
        
    elif userInfo[clnt_num][2] == 'stu':#학생
        print('학생')
        name = recv_msg(sock) #선생님이름 받기
        print('name: '+name)
        c.execute('select ID from teacherInfo where Name = ?', (name,)) #선생님이름으로 db에서 ID 찾기
        find = c.fetchone()
        if not find: #없으면
            send_msg(userInfo[clnt_num][0], '!no/serv') #클라한테 메세지 전송
            con.close()
            return
        find = ''.join(find) #문자열로 바꿔주고
        print(find)
     
    for i in range(0, usercnt):
        if userInfo[i][1] == find and userInfo[i][3] == 0: #찾은사람이 온라인이고 채팅중이 아닐때
            send_msg(userInfo[i][0], '!invite/serv') #초대메세지 전송
            recv=recv_msg(userInfo[i][0])
            print(recv)           
            if recv == '!ok': #초대 수락시
                userInfo[clnt_num][3] = 1 #채팅모드 변경
                userInfo[i][3] = 1
                chat(clnt_num)
                con.close()
                return
            elif recv == '!no': #초대 거부시
                send_msg(userInfo[clnt_num][0], '!no/serv') #클라한테 메세지 전송
                con.close()
                return                                  
      
def chat(clnt_num): # 채팅 함수
    #수정중
    con, c = getcon() #커서 획득
    type = userInfo[clnt_num][2] #선생님인지 학생인지 확인
    if type == 'tea': #선생님
        c.execute('select Name from teacherInfo where ID = ?', (userInfo[clnt_num][1])) #db에서 이름가져오기
    elif type == 'stu': #학생
        c.execute('select Name from studentInfo where ID = ?', (userInfo[clnt_num][1]))  
    name = c.fetchone() 
    name = ''.join(name) #문자열로 바꿔주기
    print(name)
    while True:
        #lock.acquire()
        msg = recv_msg(userInfo[clnt_num][0])
        if msg == '!quit':
            userInfo[clnt_num][3] = 0
            break
        else:
            for i in range(0, usercnt):
                if userInfo[clnt_num][3] == userInfo[i][3]:
                    send_msg(userInfo[i][0], name+':'+msg)
                    break          
    con.close()
    return
        #lock.release()

def QnA(sock): #Q&A 등록 함수
    #수정중
    global QnAnum
    clnt_num = findNum(sock)
    con, c = getcon()
    QnAlist = []
    c.execute('select * from QnA')
    QnA = c.fetchall()
    if QnA !=None: #등록된 Q&A가 있을때
        for i in QnA:
            i = list(i)
            i[0] = str(i[0])
            i = '/'.join(i) 
            QnAlist.append(i)  
        print(QnAlist)
        send_msg(sock, QnAlist) #등록된 Q&A 리스트 보내주기
    else:
        send_msg(sock, '!no') #없으면 !no 보내기
    while True:
        msg = recv_msg(sock)
        if msg == '!update':
            if userInfo[clnt_num][2] == 'stu': # 학생일때
                msg = recv_msg(sock) #등록할 질문 받기
                c.execute('insert into QnA (Num, Question, Answer, studentID, teacherID) values (?, ?, ?, ?, ?)', (QnAnum, msg, None, userInfo[clnt_num][1], None)) #Q&A 테이블에 질문 등록
                QnAnum+=1 #질문 등록후 번호+1
            elif userInfo[clnt_num][2] == 'tea': #선생님일때
                msg = recv_msg(sock) #등록할 답변과 질문 번호 받기
                splitmsg = msg.split('/')
                c.execute('update QnA set Answer = ? where Num = ?', (splitmsg[1], splitmsg[0],))
        elif msg == '!quit':
            con.close()
            return

def updateQuestion(sock): #문제등록 함수
    #수정중
    clnt_num = findNum(sock)
    con, c = getcon()
    if userInfo[clnt_num][2] == 'stu': # 학생일때
        print('학생')
        send_msg(sock, '!no') #메세지 보내기
        return
    elif userInfo[clnt_num][2] == 'tea': #선생님일때
        print('선생님')
        data = recv_msg(sock)

def handleclnt(sock): # 클라정보 수신 스레드
    if sock in userInfo:
        clnt_num = findNum(sock)
        if userInfo[clnt_num][3] == 1:
            chat(clnt_num)
    while True:
        data = recv_msg(sock)
        print('data: '+data)
        if data == '!signup': #!signup 받으면 회원가입 함수 실행
            signup(sock)
        elif data == '!login': #!login 받으면 로그인 함수 실행
            login(sock)
        elif data == '!chat': #!chat 받으면 상담모드 변경 함수 실행
            chatmode(sock)
        elif data == '!Q&A':# Q&A 받으면 Q&A 함수 실행
            QnA(sock)
        elif data == '!question': #!question받으면 문제출제 함수 실행
            updateQuestion(sock)
        elif data == '!quit': #!quit 받으면 해당 클라이언트 정보 삭제 후 뒤에있는 정보 당겨오기
            delete_userInfo(sock)
        elif not data:
            break

if __name__=='__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    
    print('connected')

    while True:
        client_socket, addr = server_socket.accept()
        
        # userInfo.insert(usercnt, [client_socket, 0, 0, 0]) #sock, ID, type, 채팅속성 접속시 저장
        # usercnt += 1
        
        t=threading.Thread(target=handleclnt, args=(client_socket,))
        t.start()
        
    server_socket.close()