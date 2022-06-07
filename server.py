import socket
import threading
import sqlite3

BUFSIZE = 1024 #버퍼사이즈
host = '10.10.20.33' 
port = 9015


def getcon(): #db와 연결 함수
    con = sqlite3.connect('edu.db')
    c=con.cursor()
    return con, c
   
def signup(sock): #회원가입 처리 함수
    con, c = getcon()
    data = sock.recv(BUFSIZE).decode()
    print('data: '+data)
    userdata = data.split('/') #/기준으로 문자열 나누기
    print('data[3]: '+userdata[3])
    if userdata[3] == 'tea': #선생님
        c.execute('insert into teacherInfo values (?, ?, ?, ?)', (userdata[0], userdata[1], userdata[2], userdata[3])) #선생 테이블에 데이터 저장
        con.commit()
    elif userdata[3] == 'stu': #학생
        c.execute('insert into studentInfo values (?, ?, ?, ?)', (userdata[0], userdata[1], userdata[2], userdata[3])) #학생 테이블에 데이터 저장
        con.commit()

def login(sock): #로그인 처리 함수
    con, c = getcon()
    while True:
        data = sock.recv(BUFSIZE).decode()
        print('data: '+data)
        userdata = data.split('/') # /기준으로 문자열 나누기
        print('data[2]: '+userdata[2])
        if userdata[2] == 'tea': #선생님
            c.execute('select ID, PW from teacherInfo') #선생 테이블에서 정보 찾기
            userInfo = c.fetchall()
            for search in userInfo:
                if userdata[0] == search[0] and userdata[1] == search[1]: #찾은 정보랑 입력이랑 일치시
                    sock.send(('!ok/tea').encode()) #성공시 !ok보내기
                    break
                else:
                    sock.send(('!no/tea').encode()) #실패시 !no 보내기
                    continue
        elif userdata[2] == 'stu': #학생
            c.execute('select ID, PW from studentInfo') #학생 테이블에서 정보 찾기
            userInfo = c.fetchall()
            for search in userInfo:
                if userdata[0] == search[0] and userdata[1] == search[1]: #찾은 정보랑 입력이랑 일치시
                    sock.send(('!ok/stu').encode()) #성공시 !ok 보내기
                    break
                else:
                    sock.send(('!no/stu').encode()) #실패시 !no 보내기
                    continue    
        break       
def handleclnt(sock): # 클라정보 수신 스레드
    while True:
        data = sock.recv(BUFSIZE).decode()
        print('data: '+data)
        if data == '!signup': #!signup 받으면 회원가입 함수 실행
            signup(sock)
        elif data == '!login': #!login 받으면 로그인 함수 실행
            login(sock)
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