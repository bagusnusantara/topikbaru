import select
import socket
import sys
import threading
import os

username = 'bagus'
password = '12345'

#Class Server
class Server:
    #spesifikasi dari socket ftp server
    def __init__(self):
        self.host = 'localhost'
        self.port = 2016
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []

    #inisialisasi socket ftp server    
    def open_socket(self):        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host,self.port))
        self.server.listen(5)
        print 'Server dijalankan'
        
    #menu yang akan dijalankan pertama kali saat server dimulai
    def run(self):
        self.open_socket()
        #input = [self.server, sys.stdin]
        input = [self.server]
        #running = 1
        while True:
            #select untuk socket
            inputready,outputready,exceptready = select.select(input,[],[])
            for s in inputready:
                if s == self.server:
                    # handle the server socket - menjalankan client dengan multithreading
                    #self.client_socket, self.client_address = self.server.accept()
                    #self.input.append(self.client_socket)
                    c = Client((self.server.accept()))
                    c.start()
                    self.threads.append(c)
                elif s == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    break

        # close all threads
        self.server.close()
        for c in self.threads:
            c.join()

#Class untuk Client
class Client(threading.Thread):
    #Spesifikasi untuk socket client yang berhasil terhubung
    def __init__(self,(client,address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 4096
        self.id_exit = True
        self.base = os.path.join(os.getcwd(), 'shared folder')
        self.cwd = '/'
        self.fullpath = self.base
        self.pasv_status = False

    #menu yang akan jalan pertama kali saat client berhasil terhubung    
    def run(self):
        self.welcome_message()
        self.cek_user()
        
        
    def welcome_message(self):
        self.welcome_msg = '220-FTP Server Versi 1.0\r\nRespon: 220'
        print 'Respon: ' + self.welcome_msg.strip(), self.client.getpeername()
        self.client.send(self.welcome_msg)
    #menu untuk pengecekan user           
    def cek_user(self):
        self.command = self.client.recv(self.size)
        print 'Perintah: ' + self.command.strip(), self.client.getpeername()
        if 'USER Adian\r\n' in self.command:
            self.nama_user = self.command.split(' ')
            self.login_msg = '331 Silahkan masukan password untuk ' + self.nama_user[1] + '\r\n'
            print 'Respon: ' + self.login_msg.strip(), self.client.getpeername()
            self.client.send(self.login_msg)

            self.command = self.client.recv(self.size)

            if self.command == 'PASS 1234\r\n':
                self.login_msg = '230 Anda masuk\r\n'
                self.client.send(self.login_msg)
                print 'Respon: ' + self.login_msg.strip(), self.client.getpeername()

                self.menu_log_in()
                              
            else:
                self.login_msg = 'Username atau password salah\r\n'
                self.client.send(self.login_msg)
                print 'Respon: ' + self.login_msg.strip(), self.client.getpeername()
                self.cek_user()
                #print 'E'
                            
        else:
            self.message = '500 Perintah tidak diketahui\r\n'
            self.login_msg = '530 Silahkan masuk terlebih dahulu'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            print 'Respon: ' + self.login_msg.strip(), self.client.getpeername()
            self.client.sendall(self.message + self.login_msg)
            self.cek_user()

    #menu untuk masuk ke mode pasif    
    def passive_mode(self):
        self.command = self.client.recv(self.size)
        print 'Perintah: ' + self.command.strip(), self.client.getpeername()

        if 'TYPE' in self.command:
            self.code_type = self.command.split(' ')[-1].split('\r\n')
            self.message = '220 TYPE diubah ke ', self.code_type
            self.message += '\r\n'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            self.client.send(self.message)
            self.passive_mode()

        elif self.command == 'QUIT\r\n':
            self.login_msg = '221 Anda keluar\r\n'
            self.client.send(self.login_msg)
            print 'Respon: ' + self.login_msg.strip(), self.client.getpeername()
            self.stop()
        else:
            if 'STOR' in self.command:
                self.stor()
            elif 'RETR' in self.command:
                self.retr()
            elif 'RNFR' in self.command:
                self.rnfr()
            else:
                self.message = '500 Perintah tidak diketahui\r\n'
                print 'Respon: ' + self.message.strip(), self.client.getpeername()
                self.client.send(self.message)
                self.passive_mode()

    #menu untuk user yang apabila telah berhasil login
    def menu_log_in(self):
        self.command = self.client.recv(self.size)
        print 'Perintah: ' + self.command.strip(), self.client.getpeername()

        if self.command == 'PASV\r\n':
            self.message = '227 Masuk ke mode pasif\r\n'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            self.client.send(self.message)
            ftp_data = ('localhost', 42728)
            self.server_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_data.bind(ftp_data)
            self.server_data.listen(1)
            self.client_data, self.client_data_address = self.server_data.accept()
            self.pasv_status = True
            
            self.passive_mode()
                                                                                            
        elif self.command == 'QUIT\r\n':
            self.login_msg = '221 Anda keluar\r\n'
            self.client.send(self.login_msg)
            print 'Respon: ' + self.login_msg.strip(), self.client.getpeername()
            self.stop()
            #self.input_socket.remove(self.sock)
        else:
            self.message = '500 Perintah tidak diketahui\r\n'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            self.client.send(self.message)

            self.menu_log_in()
        
    def stop(self):
        self.id_exit = False
        self.client_data.close()
        self.client.close()
        
    def stor(self):
        file_name = self.command.strip().partition(' ')[2]
        path = os.path.join(self.fullpath, file_name)
        #print path

        check = self.client.recv(4)
        file_size = int(self.client.recv(self.size))
        #print file_size
        data = ""
        status = ""
        if check == 'True':
            self.message = '150 File status okay; about to open data connection. Client may begin transferring data over the data connection.\r\n'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            self.client.send(self.message)
            with open(path, 'wb') as berkas:
                while file_size:
                    data = self.client_data.recv(self.size)
                    berkas.write(data)
                    file_size -= len(data)
            self.message = '226 Berkas ' + file_name + ' berhasil dikirim\r\n'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            self.client.send(self.message)
        else:
            self.message = '501 Syntax error in parameters or arguments. This usually results from an invalid or missing file name.\r\n'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            self.client.send(self.message)
            
        self.passive_mode()

    def retr(self):
        file_name = self.command.strip().partition(' ')[2]
        path = os.path.join(self.fullpath, file_name)
        check = os.path.isfile(path)
        file_size = os.path.getsize(path)
        print file_size
        self.client.send(str(check))
        self.client.send(str(file_size))
        data = ""
        if check:
            self.message = '150 The command was successful, data transfer starting.\r\n'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            self.client.send(self.message)
            
            with open(path, 'rb') as berkas:
                while file_size:
                    data += berkas.read()
                    file_size -= len(data)
            self.client_data.sendall(data)
            self.message = '226 Berkas ' + file_name + ' berhasil dikirim\r\n'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            self.client.send(self.message)
            
        else:
            self.message = '501 Syntax error in parameters or arguments. This usually results from an invalid or missing file name.\r\n'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            self.client.send(self.message)
        self.passive_mode()
        
    def rnfr(self):
        file_name = self.command.strip().split(' ')[1]
        path = os.path.join(self.fullpath, file_name)
        checkDir = os.path.isdir(path)
        checkFile = os.path.isfile(path)
        
        if checkDir:
            self.message = '350 Siap untuk RNTO directory\r\n'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            self.client.send(self.message)
            self.command = self.client.recv(self.size)
            if 'RNTO' in self.command:
                print 'Perintah: ' + self.command.strip(), self.client.getpeername()
                name = os.path.join(self.fullpath, self.command.strip().split(' ')[1]) 
                rename = os.rename(path, name)
                self.message = '250 Rename was successful.\r\n'
                print 'Respon: ' + self.message.strip(), self.client.getpeername()
                self.client.send(self.message)
            else:
                self.message = '501 Syntax error in parameters or arguments. This usually results from an invalid or missing file name.\r\n'
                print 'Respon: ' + self.message.strip(), self.client.getpeername()
                self.client.send(self.message)
            self.passive_mode()
                
        elif checkFile:
            self.message = '350 Siap untuk RNTO file\r\n'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            self.client.send(self.message)
            self.command = self.client.recv(self.size)
            if 'RNTO' in self.command:
                print 'Perintah: ' + self.command.strip(), self.client.getpeername()
                name = os.path.join(self.fullpath, self.command.strip().split(' ')[1])
                rename = os.rename(path, name)
                self.message = '250 Rename was successful.\r\n'
                print 'Respon: ' + self.message.strip(), self.client.getpeername()
                self.client.send(self.message)
            else:
                self.message = '501 Syntax error in parameters or arguments. This usually results from an invalid or missing file name.\r\n'
                print 'Respon: ' + self.message.strip(), self.client.getpeername()
                self.client.send(self.message)
            self.passive_mode()
        else:
            self.message = '501 Perintah tidak diketahui\r\n'
            print 'Respon: ' + self.message.strip(), self.client.getpeername()
            self.client.send(self.message)

            
        
        
        
if __name__ == "__main__":
    s = Server()
    s.run()



