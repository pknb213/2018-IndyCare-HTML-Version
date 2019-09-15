import sys, os, glob, json, time, signal, zipfile, requests, datetime, functools
from os import read, write, lseek, SEEK_SET
from struct import pack, unpack, calcsize
from sseclient import SSEClient
# from posix_ipc import MessageQueue, SharedMemory, O_CREAT
from multiprocessing import Process, Queue, set_start_method


def clip_uploader():
    print("Clip Uploader Start")
    messages = SSEClient("http://localhost:5000" + '/stream?channel=%s_clip' % 'D1234')
    for msg in messages:
        print("msg : ", msg)


def reporter(q):
    while True:
        t0 = datetime.datetime.now()
        print("Reporter : ", t0.timestamp())
        time.sleep(10)


if __name__ == '__main__':
    set_start_method('spawn', True)
    q = Queue()
    p1 = Process(target=clip_uploader, args=())
    p1.start()
    time.sleep(1)
    reporter(q)
    p1.close()
    p1.join_thread()
    p1.join()

