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
lock=threading.Lock()

def getcon(): #db와 연결 함수
    con = sqlite3.connect('edu.db')
    c=con.cursor()
    return con, c

def recv_msg(sock): #메세지 수신
    sys.stdout.flush()  # 버퍼 비우기
    clnt_msg = sock.recv(BUFSIZE)  # 메세지 받아오기
    clnt_msg = clnt_msg.decode()  # 디코딩
    return clnt_msg


def send_msg(sock, msg): #메세지 송신
    sys.stdin.flush()  # 버퍼 비우기
    msg = msg.encode()  # 인코딩
    sock.send(msg)  # 메세지 보내기

def findNum(sock):
    for i in range(0, usercnt):
        if userInfo[i][0] == sock:
            break
    return i

def delete_userInfo(sock):
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
        data = recv_msg(sock)
        print('data: '+data)
        c.execute('select teacherInfo.ID, studentInfo.ID from teacherInfo inner join studentInfo on teacherInfo.ID = studentInfo.ID')
        find = c.fetchone()       
        print(find)
        if find == None:
            send_msg(sock, '!ok/serv')
            break
        else:
            send_msg(sock, '!no/serv')
            continue
    data = recv_msg(sock)
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
    con, c = getcon()
    
    #lock.acquire()
    while True:
        data = recv_msg(sock)
        #clnt_num = findNum(sock)
        print('data: '+data)
        userdata = data.split('/') # /기준으로 문자열 나누기
        print('data[2]: '+userdata[2])
        
        if userdata[2] == 'tea': #선생님
            print('userID: '+userdata[0])
            print('userPW: '+userdata[1])
            c.execute('select PW from teacherInfo where ID = ?', (userdata[0],)) #선생 테이블에서 정보 찾기
            dbPW = c.fetchone()
            dbPW = ''.join(dbPW)
            print(dbPW)
        elif userdata[2] == 'stu': #학생
            print('userID: '+userdata[0])
            print('userPW: '+userdata[1])
            c.execute('select PW from studentInfo where ID = ?', (userdata[0],)) #학생 테이블에서 정보 찾기
            dbPW = c.fetchone()
            dbPW = ''.join(dbPW)
            print(dbPW)
            
        if userdata[1] == dbPW: #찾은 정보랑 입력이랑 일치시
            if userdata[2] == 'tea':
                msg='!ok/tea/serv'
            elif userdata[2] == 'stu':
                msg ='!ok/stu/serv'
            send_msg(sock, msg) #성공시 !ok 보내기
            # userInfo[clnt_num][1] = userdata[0] #로그인때 저장한 데이터 수정
            # userInfo[clnt_num][2] = userdata[2]
            userInfo.insert(usercnt, [sock, userdata[0], userdata[2], 0]) #sock, ID, type, 채팅속성 로그인시 저장
            usercnt += 1
            print('sucess 로그인: ')
            print(userInfo[usercnt-1])
            con.close()
            break
        else:
            send_msg(sock, '!no/tea/serv') #실패시 !no 보내기
            print('fail')
            continue   
    #lock.release()   

# 오류 ㅈㄴ 많음
# ㅅㅂ ㅈ같네 다 다시 짜야함
def chatmode(sock): #상담 요청 받아서 해당 클라이언트 속성 변경
    con, c = getcon()
    num = findNum(sock)
    if userInfo[num][2] == 'tea': # 선생
        print('선생')
        name = recv_msg(sock) #학생이름 받아오고
        print('name: '+name)
        c.execute('select ID from studentInfo where Name = ?', (name,)) #학생이름으로 db에서 아이디 찾기
        find = c.fetchone()
        if not find:
            send_msg(userInfo[num][0], '!no/serv')
            con.close()
            return
        find = ''.join(find)
        print(find)
        
    elif userInfo[num][2] == 'stu':
        print('학생')
        name = recv_msg(sock) #선생이름 받고
        print('name: '+name)
        c.execute('select ID from teacherInfo where Name = ?', (name,)) #선생이름 ID 찾고
        find = c.fetchone()
        if not find:
            send_msg(userInfo[num][0], '!no/serv')
            con.close()
            return
        find = ''.join(find)
        print(find)
     
    for i in range(0, usercnt):
        if userInfo[i][1] == find and userInfo[i][3] == 0:
            send_msg(userInfo[i][0], '!invite/serv')
            recv=recv_msg(userInfo[i][0])           
            if recv == '!ok/serv':
                userInfo[num][3] = 1
                userInfo[i][3] = 1
                #chat(i, num)
                con.close()
                return
            elif recv == '!no/serv':
                send_msg(userInfo[num][0], '!no/serv')
                con.close
                return                                  
      
def chat(clnt_num, name):
    #상담 시작한 클라이언트 소켓 받아오고
    #해당 소켓들의 메세지 받아서 다시 보내준다....?
    #안될거 같은데 해보고 안되면 수정
    #이 친구 다시 짜야함 
    while True:
        #lock.acquire()
        msg=recv_msg(userInfo[clnt_num][0])
        print('msg: '+msg)
        #splitmsg = msg.split('/') # /기준으로 문자열 나누기
        if msg == '!quit':
            for i in range(0, len(userInfo)):
                if userInfo[clnt_num][3] == userInfo[i][3]:
                    msg='!exit/serv'
                    send_msg(userInfo[i][3], '!exit/serv')
        else:
            for i in range(0, len(userInfo)):
                if userInfo[clnt_num][3] == userInfo[i][3]:
                    send_msg(userInfo[i][3], msg+name)
        #lock.release()

def QnA(sock):
    clnt_num = findNum(sock)
    con, c = getcon()
    if userInfo[clnt_num][2] == 'stu': # 학생일때
        print('아 할꺼')
        #등록된 질문 목록 보여주고
        #새질문 등록시 !update같이 받고
        #잘라서 질문만 등록....?
        #답변 확인시 해당 질문에 대한 답변만 보여줌?
    elif userInfo[clnt_num][2] == 'tea': #선생님일때
        print('많다')
        #등록된 질문 보여주고
        #답변 등록시 !update같이 받고
        #잘라서 답변만 등록....?

def updateQuestion(sock):
    clnt_num = findNum(sock)
    con, c = getcon()
    if userInfo[clnt_num][2] == 'stu': # 학생일때
        print('어디 학생이 문제를 출제할라하냐')
        #!no매세지 보내기
        msg = '!no'
        send_msg(sock, msg)
        return
    elif userInfo[clnt_num][2] == 'tea': #선생님일때
        print('잘난 선생님 문제나 내보세요')

def handleclnt(sock): # 클라정보 수신 스레드
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