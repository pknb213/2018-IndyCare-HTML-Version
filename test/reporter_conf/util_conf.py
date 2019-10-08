import sys, os, glob, json, time, signal, zipfile, requests, datetime, random, requests.exceptions, http.client
from multiprocessing import Process, Queue, set_start_method
from indyShm_conf import *


def set_proc_name(newname):
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newname) + 1)
    buff.value = newname
    libc.prctl(15, byref(buff), 0, 0, 0)


set_proc_name(b'IndyCAREReport')


def check_task_manager():
    while True:
        try:
            print("\n**************** Task Manager Checking ... **************** ")
            shm = RobotState(INDY_SHM, INDY_SHM_ROBOT_STATE_ADDR, ROBOT_STATE_SHM_SIZE)
            print(">> Task Manager : %d" % shm.check_is_task_running(shm))
            if shm.check_is_task_running(shm) is 0: raise Exception
        except Exception as e:
            print(">>>> Fail to Access from Robot SHM : ", e)
            print(">>>> Time : ", datetime.datetime.now())
            time.sleep(10)
        else:
            print(">>>> Success : ",  datetime.datetime.now())
            time.sleep(1)
            return True


def check_shm():
    t = datetime.datetime.now()
    while True:
        try:
            print("\n**************** Shared Memory Checking ... **************** ")
            print(">> Error Code SHM : ", ErrorCode(INDY_SHM, INDY_SHM_ROBOT_ERROR_CODE_ADDR, ERROR_CODE_SHM_SIZE))
            print(">> Control State SHM : ", ControlState(INDY_SHM, INDY_SHM_ROBOT_CTRL_STATUS_ADDR, ROBOT_CTRL_STATUS_SHM_SIZE))
            print(">> System State SHM : ",SystemState(NRMK_SHM, NRMK_SHM_SYSTEM_ADDR, SYSTEM_SHM_SIZE))
            print(">> MSG Counter : ", MessageCounter(MSG_COUNTER_SHM, 0, 4))
            print(">> MSG Queue : ", MessageQueue(POSIX_MSG_QUEUE, flags=O_CREAT, mode=0o666, max_messages=100, max_message_size=1024))

        except Exception as e:
                print(">>>> Fail to Initialize : ", e)
                t = datetime.datetime.now()
                print(">>>> Time : ", t)
                time.sleep(10)
        else:
            print(">>>> Success : ", t)
            time.sleep(1)
            return True


def check_robot_info():
    while True:
        try:
            print("\n**************** Robot information Checking ... **************** ")
            shm = RobotInfoData(INDY_SHM, INDY_SHM_ROBOT_INFO_ADDR, ROBOT_INFO_SHM_SIZE)
            sn = shm.get_serial_number(shm)
            print(shm.get_all_robot_info_data(shm))
        except Exception as e:
            print(">>>> Fail to Access from Robot Information SHM : ", e)
            print(">>>> Time : ", datetime.datetime.now())
            time.sleep(10)
        else:
            print(">>>> Success Serial Number : ", sn)
            time.sleep(1)
            return sn




