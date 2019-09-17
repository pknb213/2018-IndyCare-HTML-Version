import sys, os
sys.path.append(os.getcwd() + os.path.sep + 'reporter_conf')
from http_conf import *
from util_conf import *
from event_conf import *


def task_server():
    print("Task Server Start")
    # todo : Message Queue 구현


def reporter(q):
    while True:
        t0 = datetime.datetime.now()
        print("Reporter : ", t0)
        s = requests.Session()
        # todo : Message Queue Receiver 구현
        while 1:
            time.sleep(10)
            if EventFiles.check_if_new_log():
                log_file = EventFiles.latest_log[len(EventFiles.EVENT_DIRECTORY):]
                print("Update Log File : ", log_file)
                # 여기서 바로 file로 event log를 보내도 된다고 생각 함
                # date = datetime.datetime.strptime(log_file[12:-4], '%m-%d-%Y-%H-%M-%S')
                # print(date)
                s.post(URL + '/event', json={'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'code': 1, 'log': EventFiles.latest_log})


def event_log_uploader():
    print("Event Log Uploader Start")

    s = requests.Session()
    messages = SSEClient(URL + '/stream?channel=%s_event_log' % 'D1234')
    for msg in messages:
        print("msg : ", msg)


def clip_uploader():
    print("Clip Uploader Start")

    s = requests.Session()
    messages = SSEClient(URL + '/stream?channel=%s_clip' % 'D1234')
    for msg in messages:
        print("msg : ", msg)
        if EventFiles.get_latest_clip():
            with open(EventFiles.get_latest_clip(), 'rb') as f:
                print(f)
                res = s.post(URL + '/clip/D1234/check', files={'file': f})
        else:
            print("No Clip")
            res = s.post(URL + '/clip/D1234/check', files={'file': ('No Camera', '')})


if __name__ == '__main__':
    set_start_method('spawn', True)
    q = Queue()
    p1 = Process(target=event_log_uploader, args=())
    p2 = Process(target=clip_uploader, args=())
    p1.start()
    p2.start()
    time.sleep(1)
    reporter(q)
    q.close()
    q.join_thread()
    p2.join()
    p1.join()

