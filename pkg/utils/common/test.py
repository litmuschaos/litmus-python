#!/usr/bin/env python
import signal
import threading
import sys
import time
def printName1(name,abc):
    print(abc+' '+name)
# def signal_handler1(sig, frame):
#     print('You pressed Ctrl+C!')
#     sender.start()
#     sys.exit(0)


def starts():
    sender = threading.Thread(target=printName1, args=('shubham','oye'))
    def signal_handler1(sig, frame):
        print('You pressed Ctrl+C!')
        sender.start()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler1)
    print('Press Ctrl+C')
    signal.pause()
    sender.join()
starts()