from datetime import datetime
import random
import socket
import pyautogui
import glob
import os
import shutil
import threading

def serv__time():
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')


def serv__whoru():
    return socket.gethostname()


def serv__rand(start=0, end=10):
    return random.randint(start, end)


def serv__echo(message):
    return message

def serv__screenshot():
    pyautogui.screenshot(r'.\server_files\screenshots\screenshot.png')
    return r'.\server_files\screenshots\screenshot.png'
    
    
def serv__my_files():
    path = f'.\\server_files\\{threading.current_thread().name}'
    return glob.glob(path + r'\*.*')    
    
def serv__ex():
    threading.main_thread().exit()
    exit()
    
def serv__dir(path):
    return glob.glob(path+r'\*.*')

def serv__delete(path):
    return 'Deleted' if os.remove(path) else 'Failed to delete'

def serv__copy(src, dest):
    return 'Copied' if shutil.copy(src, dest) else 'Failed to copy'

def serv__execute(path):
    os.startfile(path)
    return 'Executed'

