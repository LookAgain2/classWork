import os
# from qt5 import *
import sys
import time
# import ui
# from PyQt5.QtCore import QThread
# from PyQt5.QtWidgets import QMainWindow
import threading
import itertools

class UserException(Exception):
    pass


class FatalError(UserException):
    pass


class NonFatalError(UserException):
    pass


dir_path = r'.\server_files\screenshots'
if not os.path.exists(dir_path):
    os.makedirs(dir_path)

dir_path = r'.\client_files'
if not os.path.exists(dir_path):
    os.makedirs(dir_path)


def recv(sock, BUFF, name='server'):
    try:
        data_type = sock.recv(4).decode()
    except ConnectionError:
        raise FatalError('Connection forcibly closed')
    if data_type == 'mess':
        return __recv_mess(sock, BUFF)
    if data_type == 'file':
        if name == 'client':
            return __recv_file(sock, BUFF, '.\\client_files\\')
        return __recv_file(sock, BUFF)
    if data_type == '':
        raise FatalError('Connection forcibly closed')
    else:
        raise NonFatalError('Wrong Data Type')


def __recv_file(sock, BUFF=1024, path='.\\server_files\\'):
    
    if path == '.\\server_files\\':
        path += threading.current_thread().name + '\\'
        if not os.path.exists(path):
            os.makedirs(path)
    
    try:
        filename_len = sock.recv(10).decode()
    except Exception:
        raise FatalError('Client Disconnected Forcibly')

    filename = os.path.basename(sock.recv(int(filename_len)).decode())

    count = 0
    remove = 0
    while True:
        try:
            with open(f'{path}{filename}', 'x'):
                break
        except FileExistsError:
            count += 1
            if count > 1:
                if count > 10:
                    remove = (count // 10) if count // 10 == 1 else 1
                filename = f'{os.path.splitext(filename)[0][:-4 - remove]} ({count}){os.path.splitext(filename)[1]}'
            else: filename = f'{os.path.splitext(filename)[0]} ({count}){os.path.splitext(filename)[1]}'


    try:
        filesize = int(sock.recv(10).decode())
    except ValueError:
        raise FatalError('Client Disconnected Forcibly')

    # App = QApplication(sys.argv)
    # Main_win = QMainWindow()
    # uipilot = ui.Ui_MainWindow()
    # uipilot.setupUi(Main_win)
    
    # t = threading.Thread(target=uipilot.Update_Progress)
    # t.start()
    # Main_win.show()
    def animation():
        print(f'[SERVER] Receiving file {filename} ({filesize} bytes)')
        c = itertools.cycle(['⊙', '⊚', '⌾', '⊚'])
        while True:
            if threading.current_thread().name == 'done':
                print('\r[SERVER] File Received    ')
                return
            print('\r[SERVER] Recieving file ' + next(c), end = '')
            sys.stdout.flush()
            time.sleep(0.3)
    
    size = 0
    
    t = threading.Thread(target=animation)
    
    
    with open(f'{path}{filename}', 'wb') as f:
        t.start()
        while size < filesize:
            bytes_read = sock.recv(BUFF)
            
            f.write(bytes_read)
            size += len(bytes_read)
            
            # uipilot.progressBar.progress = size / filesize * 100
            
        t.setName('done')
        t.join()
            
        print(f'[CLIENT] Sent file {filename} ({size}/{filesize} bytes)')
    
    os.startfile(fr'{path}{filename}')
    return 'sent file'

    


def __recv_mess(sock, BUFF=1024):
    try:
        mess_size = int(sock.recv(10).decode())
    except ValueError:
        raise FatalError('Connection forcibly closed')

    size = 0
    message = ''

    while size < mess_size:
        bytes_read = sock.recv(BUFF)

        message += bytes_read.decode()
        size += len(bytes_read)

    return message


def send(**kwargs):
    isMess = False
    isFile = False
    BUFF = 1024
    for k, d in kwargs.items():
        if k == 'sock':
            if d == '':
                raise FatalError('Invalid Socket')
            sock = d
        elif k == 'BUFF':
            BUFF = d
        elif k == 'mess':
            mess = d
            isMess = True
        elif k == 'file':
            file_name = d
            isFile = True
        else:
            raise NonFatalError('Invalid Keyword Argument')
    if isMess:
        return __send_mess(sock, mess, BUFF)
    if isFile:
        return __send_file(sock, file_name, BUFF)


def __send_mess(sock, message, BUFF=1024):
    mess_size = len(str(message))
    try:
        sock.send('mess'.encode())
        sock.send(str(mess_size).rjust(10, '0').encode())
        for _ in range((mess_size // BUFF) + 1):
            mess_size = len(str(message))
            if mess_size < BUFF:
                sock.send(str(message).encode())
                break
            sock.send(str(message[:message[::BUFF][1].index()]).encode())
            message = message[BUFF:]

        return message

    except OSError:
        raise FatalError('Connection forcibly closed')


def __send_file(sock, filename, BUFF=1024):

    try:
        filesize = os.path.getsize(filename)
    except FileNotFoundError:
        raise NonFatalError('No such file')

    try:
        sock.send('file'.encode())
        sock.send(str(len(filename)).rjust(10, '0').encode() + filename.encode())
        sock.send(str(filesize).rjust(10, '0').encode())
        size = 0

        print(f'[SERVER] Sending file {filename} ({filesize} bytes)')
        with open(filename, 'rb') as f:
            for _ in range((filesize // BUFF) + 1):

                bytes_read = f.read(BUFF)
                sock.send(bytes_read)
                size += len(bytes_read)
            print(f'[CLIENT] Sent file {filename} ({size}/{filesize} bytes)')
            print('\033[K', end='')
            return True

    except OSError:
        print('\033[K', end='')
        raise FatalError('Connection Aborted')
    
    

