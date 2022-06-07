import socket

BUFSIZE = 1024
host = '127.0.0.1'
port = 9061

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((host, port))

msg = input('msg:')
socket.send(msg.encode(encoding='utf-8'))

data = socket.recv(BUFSIZE)
msg = data.decode()
print('echo msg:', msg)

socket.close()