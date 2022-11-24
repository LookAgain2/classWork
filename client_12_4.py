import socket
import os
from protocol import *
from importlib import reload
import uuid

clear = lambda: os.system('cls')

HOST = 'localhost'
PORT = 8000
BUFF = 1024


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clear()
    print('[CLIENT] Connecting to server...')
    while True:
        try:
            sock.connect((HOST, PORT))
            print('[CLIENT] Connected to server')
            break
        except OSError:
            print('[CLIENT] Connection Failed')
            inp = input('[CLIENT] Try again? (y/n): ')
            if inp == 'y':
                continue
            return
        
    while True:
        try:
            print('[SERVER] ' + recv(sock, BUFF))
            name = input('[CLIENT] Enter your name: ')
            send(sock=sock, mess=name, BUFF=BUFF)
            mess = recv(sock, BUFF)
            if mess == f'Welcome {name}!':
                print('[SERVER1] ' + mess)
                break
            print('[SERVER] ' + mess)
        except FatalError as e:
            print(e)
            return
        except NonFatalError as e:
            print(e)
            
    while True:
        try:
            mess = input('Send Message (LIST|RELOAD|EXIT|FILE): ')
            if mess.upper() == 'EXIT':
                print('[CLIENT] Breaking')
                send(sock=sock, mess=mess)
                break
            if mess.upper() == 'FILE':
                filename = input('Enter filename: ')
                a = send(sock=sock, file=filename, BUFF=BUFF)
            else:
                a = send(sock=sock, mess=mess, BUFF=BUFF)
            if not a:
                inp = input('[CLIENT] try again?')
            elif a == 'abort':
                print('[CLIENT] Server forcibly closed')
                break
            s = recv(sock, BUFF)
            print(f'[SERVER] {s}')
        except FatalError as e:
            print('[CLIENT]', e)
            break
        except NonFatalError as e:
            print('[CLIENT]', e)
    sock.close()


if __name__ == '__main__':
    main()
