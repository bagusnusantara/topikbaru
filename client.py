import socket
import time
import os

ftp_address = ('10.181.1.239', 2016)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(ftp_address)

msg = client_socket.recv(4096)
print msg.strip()
pasv_status = False

while True:
    command = raw_input()
    command += '\r\n'
    client_socket.send(command)
    cmd = command.strip().partition(' ')[0]
    
    if cmd == 'QUIT':
        user_msg = client_socket.recv(10000)
        print user_msg.strip(), client_socket.getpeername()
        break
    elif cmd == 'PASV':
        if pasv_status == False:
            ftp_data = ('10.181.1.239', 42728)
            client_socket_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket_data.connect(ftp_data)
            pasv_status = True
        user_msg = client_socket.recv(10000)
        print user_msg.strip(), client_socket_data.getpeername()
    elif cmd == 'STOR':
        file_name = command.strip().partition(' ')[2]
        local = os.getcwd()
        path = os.path.join(local, 'download')
        upload = os.path.join(path, file_name)
        check = os.path.isfile(upload)
        file_size = os.path.getsize(upload)
        client_socket.send(str(check))
        client_socket.send(str(file_size))
        #print file_size          
        data = ""
        if check:
            user_msg = client_socket.recv(4096)
            print user_msg.strip(), client_socket.getpeername()           
            with open(upload, 'rb') as f:
                while file_size:
                    data += f.read()
                    #print file_size
                    file_size -= len(data)
            client_socket_data.sendall(data)
            
        user_msg = client_socket.recv(4096)
        print user_msg.strip(), client_socket.getpeername()
    elif cmd == 'RETR':
        file_name = command.strip().partition(' ')[2]
        local = os.getcwd()
        path = os.path.join(local, 'download')
        download = os.path.join(path, file_name)
        check = client_socket.recv(4)
        file_size = int(client_socket.recv(4096))
        data=""
        #print file_size
        if check == 'True':
            user_msg = client_socket.recv(4096)
            print user_msg.strip(), client_socket.getpeername()
            with open(download, 'wb') as f:
                while file_size:
                    data = client_socket_data.recv(4096)
                    f.write(data)
                    file_size -= len(data)
            #client_socket.send('Ok')
            #print 'Ok'
                    
        user_msg = client_socket.recv(4096)
        print user_msg.strip(), client_socket.getpeername()
    elif cmd == 'RNFR':
        user_msg = client_socket.recv(10000)
        print user_msg.strip(), client_socket.getpeername()

        if '350' in user_msg:
            command = raw_input()
            command += '\r\n'
            client_socket.send(command)
        
        user_msg = client_socket.recv(10000)
        print user_msg.strip(), client_socket.getpeername()
                    
    else:
        user_msg = client_socket.recv(10000)
        print user_msg.strip(), client_socket.getpeername()


client_socket.close()
