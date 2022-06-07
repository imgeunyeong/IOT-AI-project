import socket
import threading
import sqlite3

BUFSIZE = 1024
host = '10.10.20.33'
port = 9015


def getcon():
    con = sqlite3.connect('edu.db')
    c=con.cursor()
    return con, c
   
#0 id 1pw 2name
def signup(sock):
    con, c = getcon()
    data = sock.recv(BUFSIZE).decode()
    print('data: '+data)
    userdata = data.split('/')
    print('data[3]: '+userdata[3])
    if userdata[3] == 'tea':
        c.execute('insert into teacherInfo values (?, ?, ?, ?)', (userdata[0], userdata[1], userdata[2], userdata[3])) 
        con.commit()
    elif userdata[3] == 'stu':
        c.execute('insert into teacherInfo values (?, ?, ?, ?)', (userdata[0], userdata[1], userdata[2], userdata[3])) 
        con.commit()

def login(sock):
    con, c = getcon()
    data = sock.recv(BUFSIZE).decode()
    print('data: '+data)

def handleclnt(sock):
    while True:
        data = sock.recv(BUFSIZE).decode()
        print('data: '+data)
        if data == '!signup':
            signup(sock)
        elif data == '!login':
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