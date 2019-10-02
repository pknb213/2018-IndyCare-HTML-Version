from posix_ipc import MessageQueue, SharedMemory, O_CREAT
from os import read, write, lseek, SEEK_SET
from struct import pack, unpack, calcsize

REPORTER_PROCESS_SHM = 'reporterShm'
REPORTER_PROCESS_STATE_ADDR = 0
REPORTER_PROCESS_SHM_SIZE = 20
INDY_SHM_MGR_OFFSET = 64
ROBOT_SN_LENGHT_MAX = 15  # Todo : ???


class ShmWrapperForReporter(object):
    def __init__(self, name, offset, size, flags=O_CREAT):
        self.shm = SharedMemory(name, flags=flags)
        self.offset = offset + INDY_SHM_MGR_OFFSET
        self.size = size + ROBOT_SN_LENGHT_MAX
        self.fmt = 'bbbbb%ss' % ROBOT_SN_LENGHT_MAX
        lseek(self.shm.fd, self.offset, SEEK_SET)

        self.write(0, 0, 0, 0, 0, 'INIT12345678'.encode('utf-8'))

    def read(self):
        lseek(self.shm.fd, self.offset, SEEK_SET)
        return read(self.shm.fd, self.size)
        # return unpack(self.fmt, read(self.shm.fd, self.size))

    def write(self, b1, b2, b3, b4, b5, s):
        lseek(self.shm.fd, self.offset, SEEK_SET)
        # return write(self.shm.fd, self.size)
        write(self.shm.fd, pack(self.fmt, b1, b2, b3, b4, b5, s))


class ReporterProcessState(ShmWrapperForReporter):
    def __del__(self):
        lseek(self.shm.fd, self.offset, SEEK_SET)
        write(self.shm.fd, pack('b', 0))
        lseek(self.shm.fd, self.offset + 1, SEEK_SET)
        write(self.shm.fd, pack('b', 0))
        lseek(self.shm.fd, self.offset + 2, SEEK_SET)
        write(self.shm.fd, pack('b', 0))
        lseek(self.shm.fd, self.offset + 3, SEEK_SET)
        write(self.shm.fd, pack('b', 0))
        lseek(self.shm.fd, self.offset + 4, SEEK_SET)
        write(self.shm.fd, pack('b', 0))

    @property
    def task_process(self):
        return super().read()[0]

    @property
    def clip_process(self):
        return super().read()[1]

    @property
    def log_process(self):
        return super().read()[2]

    @property
    def zip_process(self):
        return super().read()[3]

    @property
    def serial_number_register(self):
        return super().read()[4]

    @property
    def serial_number_value(self):
        # data = super().read()[5:17]
        data = super().read()[5:5 + super().read()[5:].index(0)]
        return unpack('%ss' % len(data), data)[0]

    @staticmethod
    def on_task_process_state(indyshm):
        lseek(indyshm.shm.fd, indyshm.offset, SEEK_SET)
        return write(indyshm.shm.fd, pack('b', 1))

    @staticmethod
    def on_clip_process_state(indyshm):
        lseek(indyshm.shm.fd, indyshm.offset + 1, SEEK_SET)
        return write(indyshm.shm.fd, pack('b', 1))

    @staticmethod
    def on_log_process_state(indyshm):
        lseek(indyshm.shm.fd, indyshm.offset + 2, SEEK_SET)
        return write(indyshm.shm.fd, pack('b', 1))

    @staticmethod
    def on_zip_process_state(indyshm):
        lseek(indyshm.shm.fd, indyshm.offset + 3, SEEK_SET)
        return write(indyshm.shm.fd, pack('b', 1))

    @staticmethod
    def on_serial_number_register_state(indyshm):
        lseek(indyshm.shm.fd, indyshm.offset + 4, SEEK_SET)
        return write(indyshm.shm.fd, pack('b', 1))

    @staticmethod
    def off_task_process_state(indyshm):
        lseek(indyshm.shm.fd, indyshm.offset, SEEK_SET)
        return write(indyshm.shm.fd, pack('b', 0))

    @staticmethod
    def off_clip_process_state(indyshm):
        lseek(indyshm.shm.fd, indyshm.offset + 1, SEEK_SET)
        return write(indyshm.shm.fd, pack('b', 0))

    @staticmethod
    def off_log_process_state(indyshm):
        lseek(indyshm.shm.fd, indyshm.offset + 2, SEEK_SET)
        return write(indyshm.shm.fd, pack('b', 0))

    @staticmethod
    def off_zip_process_state(indyshm):
        lseek(indyshm.shm.fd, indyshm.offset + 3, SEEK_SET)
        return write(indyshm.shm.fd, pack('b', 0))

    @staticmethod
    def off_serial_number_register_state(indyshm):
        lseek(indyshm.shm.fd, indyshm.offset + 4, SEEK_SET)
        return write(indyshm.shm.fd, pack('b', 0))

    @staticmethod
    def get_all_reporter_state(indyshm):
        keys = ['task_process', 'clip_process', 'log_process', 'zip_process']
        st = {}
        for key in keys: st[key] = getattr(indyshm, key)
        return st

    @staticmethod
    def get_reporter_state_check(indyshm):
        keys = ['task_process', 'clip_process', 'log_process', 'zip_process']
        result = 0
        for key in keys:
            result += getattr(indyshm, key)
        return True if result != 0 else False

    @staticmethod
    def get_serial_number_register_state_check(indyshm):
        key = 'serial_number_register'
        return getattr(indyshm, key)

    @staticmethod
    def get_serial_number_value(indyshm):
        key = 'serial_number_value'
        return getattr(indyshm, key).decode('utf-8')

    @staticmethod
    def write_serial_number(indyshm, _str):
        lseek(indyshm.shm.fd, indyshm.offset + 5, SEEK_SET)
        return write(indyshm.shm.fd, pack('%ss' % len(_str.encode()), _str.encode()))

