import socket
import threading

BUFSIZE = 1024
host = '127.0.0.1'
port = 9061

def handleclnt(sock):
    while True:
        data = sock.recv(BUFSIZE)
        print('data: ' %data)
        if not data:
            break

if __name__=='__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    
    print('connected')

    while True:
        client_socket, addr = server_socket.accept()
        
        t=threading.Thread(target=handleclnt, args=(client_socket, addr))
        t.start()
#aaaaaaaaaaaaaaaa
    server_socket.close()