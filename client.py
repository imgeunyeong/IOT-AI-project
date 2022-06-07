import socket

BUFSIZE = 1024
host = '127.0.0.1'
port = 9061

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((host, port))

while True:
    msg = input('msg: ')
    socket.send(msg.encode())