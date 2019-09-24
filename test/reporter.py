import sys, os
sys.path.append(os.getcwd() + os.path.sep + 'reporter_conf')
from http_conf import *
from util_conf import *
from event_conf import *
from indyShm_conf import *
from reporterShm_conf import *
ROBOT_SERIAL_NUMBER = 'GLOBALTEST12'


def task_server():
    print("Task Server Start")
    # todo : Message Queue 구현
    # todo : Test
    s = requests.Session()
    s.post(URL + '/login', {'id': 'D1234', 'pwd': 'D1234'})
    while True:
        s.post(URL + '/opdata', json={"x": str(datetime.datetime.now()), "y": random.randrange(20, 70)})
        time.sleep(5)


def reporter(q):
    while True:
        s = requests.Session()
        s.post(URL + '/login', {'id': 'D1234', 'pwd': 'D1234'})
        # todo : Message Queue Receiver 구현
        while 1:
            t0 = datetime.datetime.now()
            print("Reporter : ", t0)
            time.sleep(10)
            if EventFiles.check_if_new_log():
                log_file = EventFiles.latest_log[len(EventFiles.EVENT_DIRECTORY):]
                print("Update Log File : ", log_file)
                # 여기서 바로 file로 event log를 보내도 된다고 생각 함
                date = str(datetime.datetime.strptime(log_file[12:-4], '%m-%d-%Y-%H-%M-%S'))
                code = int(log_file[:2])
                print(date)
                s.post(URL + '/event', json={"time": date, "code": code, "log": EventFiles.latest_log})


def event_log_uploader():
    print("Event Log Uploader Start")

    s = requests.Session()
    s.post(URL + '/login', {'id': 'D1234', 'pwd': 'D1234'})
    messages = SSEClient(URL + '/stream?channel=%s_event_log' % 'D1234')
    for msg in messages:
        print("msg : ", msg.data)
        data = json.loads(msg.data)
        if EventFiles.get_directory_path():
            with open(EventFiles.get_directory_path() + data['filename'], 'rb') as f:
                print(f)
                res = s.post(URL + '/file/event/%s/%s' % (data['filename'], data['sn']), files={'file': f})


def clip_uploader():
    print("Clip Uploader Start")

    s = requests.Session()
    s.post(URL + '/login', {'id': 'D1234', 'pwd': 'D1234'})
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

    check_task_manager()
    check_shm()
    sn = check_serial_number()
    shm = ReporterState(REPORTER_SHM, REPORTER_STATE_ADDR, REPORTER_SHM_SIZE)
    shm.write_serial_number(shm, sn)
    ROBOT_SERIAL_NUMBER = sn
    print("Robot SerialNumber : ", shm.get_serial_number_value(shm))

    q = Queue()
    p1 = Process(target=event_log_uploader, args=())
    p2 = Process(target=clip_uploader, args=())
    p3 = Process(target=task_server, args=())
    p1.start()
    p2.start()
    p3.start()
    time.sleep(1)
    reporter(q)
    q.close()
    q.join_thread()
    p3.join()
    p2.join()
    p1.join()

