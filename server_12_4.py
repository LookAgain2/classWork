import socket
import os
from protocol import *
from funcs import *
from importlib import reload
import sys
import threading

clear = lambda: os.system('cls')


HOST = 'localhost'
PORT = 8000
BUFF = 1024

names = []    

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    clear()
    server_socket.listen(5)
    print(f'[SERVER] Listening on {HOST}:{PORT}')
    while True:
        alive_threads = threading.enumerate()
        threading.Thread(target=client_handler, args=server_socket.accept()).start()

def client_handler(client_socket, address):
    global alive_threads
    global names
    
    count = 0 
    while True:
        try:
            print('[SERVER] Connected to Client ({}:{}), asking for name:'.format(address[0], address[1]))
            send(sock=client_socket, mess='What is your name?', BUFF=BUFF)
            name = recv(client_socket, BUFF)
            print(f'[CLIENT] {name}')
            if name not in names:
                threading.current_thread().name = name
                names.append(name)
                client_addr = f':{address[1]}'
                send(sock=client_socket, mess=f'Welcome {name}!', BUFF=BUFF)
                print(f'[SERVER] Connected to Client ({name})')
                break
            else:
                send(sock=client_socket, mess='Name already taken, try again', BUFF=BUFF)
                print(f'[SERVER] Name ({name}) already taken')
        except FatalError as e:
            print(e)
            if name in names:
                names.remove(name)
            client_socket.close()
            return
        except NonFatalError as e:
            print(e)
            break
    while True:
        try:
            
            message = recv(client_socket, BUFF)
            
            print(f'[CLIENT ({name})] {message.upper()}')
            
            if message.upper() == 'EXIT':
                print(f'[SERVER ({name})] Breaking')
                client_socket.close()
                return
            
            if message.upper() == 'SENT FILE':
                send(sock = client_socket, mess = 'File recieved')
                continue
            
            if message.upper() == 'RELOAD':
                del sys.modules['funcs']
                del sys.modules['protocol']
                reload(__import__('funcs'))
                reload(__import__('protocol'))
                send(sock = client_socket, mess = 'Reloaded', BUFF=BUFF)
                continue
            
            elif message.upper() == 'LIST':
                s = '\n' + '\n'.join([i[6:] for i in dir(__import__('funcs')) if len(i) > 6 and i[:6] == 'serv__'])
            
            elif message[:4].upper() == 'RAND' and len(message.split(' ')) == 3:
                start, end = message.split()[1:]
                start, end = int(start), int(end)
                s = getattr(__import__('funcs'), 'serv__rand')(start, end)
                
            elif not hasattr(__import__('funcs'), 'serv__'+message.lower()):
                print(f'[SERVER ({client_addr})] Invalid command')
                send(sock=client_socket, mess='Invalid command', BUFF=BUFF)
                continue
            
            else: 
                s = getattr(__import__('funcs'), 'serv__'+message.lower())()
            
            print(f'[SERVER {name}] sending {s}')
            s = send(sock=client_socket, mess=s, BUFF=BUFF)
        except FatalError as e:
            print(f'[SERVER ({name})]', e)
            names.remove(name)
            alive_threads = threading.enumerate()
            return
        except NonFatalError as e:
            print(f'[SERVER ({client_addr})]', e)
            continue   

if __name__ == '__main__':
    main()