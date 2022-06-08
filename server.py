import socket
import threading
import sqlite3
import sys

BUFSIZE = 1024 #버퍼사이즈
host = '10.10.20.33' 
port = 9015
userInfo = []
usercnt = 0


def getcon(): #db와 연결 함수
    con = sqlite3.connect('edu.db')
    c=con.cursor()
    return con, c

def recv_msg(clnt_sock): #메세지 수신
    sys.stdout.flush()  # 버퍼 비우기
    clnt_msg = clnt_sock.recv(BUFSIZE)  # 메세지 받아오기
    clnt_msg = clnt_msg.decode()  # 디코딩
    return clnt_msg


def send_msg(clnt_sock, msg): #메세지 송신
    sys.stdin.flush()  # 버퍼 비우기
    msg = msg.encode()  # 인코딩
    clnt_sock.send(msg)  # 메세지 보내기
   
def signup(sock): #회원가입 처리 함수
    con, c = getcon()
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
    con, c = getcon()
    
    while True:
        data = recv_msg(sock)
        print('data: '+data)
        userdata = data.split('/') # /기준으로 문자열 나누기
        print('data[2]: '+userdata[2])
        if userdata[2] == 'tea': #선생님
            print('userID: '+userdata[0])
            print('userPW: '+userdata[1])
            c.execute('select PW from teacherInfo where ID = ?', (userdata[0],)) #선생 테이블에서 정보 찾기
            dbPW = c.fetchone()
            print(dbPW)
            if (userdata[1],) == dbPW: #찾은 정보랑 입력이랑 일치시
                msg='!ok/tea'
                send_msg(sock, msg) #성공시 !ok 보내기
                userInfo.insert(usercnt, [sock, userdata[0], userdata[2], 0])
                usercnt += 1
                print('sucess 로그인: ')
                print(userInfo[usercnt-1])
                break
            else:
                msg='!no/tea'
                send_msg(sock, msg) #실패시 !no 보내기
                print('fail')
                continue   
        if userdata[2] == 'stu': #학생
            print('userID: '+userdata[0])
            print('userPW: '+userdata[1])
            c.execute('select PW from studentInfo where ID = ?', (userdata[0],)) #선생 테이블에서 정보 찾기
            dbPW = c.fetchone()
            if (userdata[1],) == dbPW: #찾은 정보랑 입력이랑 일치시
                msg='!ok/stu'
                send_msg(sock, msg) #성공시 !ok 보내기
                userInfo.insert(usercnt, [sock, userdata[0], userdata[2], 0])
                usercnt += 1
                print('sucess 로그인: ')
                print(userInfo[usercnt-1])
                break
            else:
                msg='!no/stu'
                send_msg(sock, msg) #실패시 !no 보내기
                print('fail')
                continue   
        break

#def chatmode(sock):


def handleclnt(sock): # 클라정보 수신 스레드
    while True:
        data = recv_msg(sock)
        print('data: '+data)
        if data == '!signup': #!signup 받으면 회원가입 함수 실행
            signup(sock)
        elif data == '!login': #!login 받으면 로그인 함수 실행
            login(sock)
        #elif data == '!chat':
        #    chatmode(sock)
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
        
        t=threading.Thread(target=handleclnt, args=(client_socket,))
        t.start()
        
    server_socket.close()