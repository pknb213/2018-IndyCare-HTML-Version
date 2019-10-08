from posix_ipc import MessageQueue, SharedMemory, O_CREAT
from os import read, write, lseek, SEEK_SET
from struct import pack, unpack, calcsize

# Todo : SSE CLIENT : 'sudo pip3 install --ignore-installed sseclient'
# Todo : Posix IPC : Only Linux library, dependency : 'apt-get install python-dev', 'pip3 install posix_ipc'

INDY_SHM = "indySHM"
INDY_SHM_LEN = 0x1000000
# [0] : Error Code
INDY_SHM_ROBOT_ERROR_CODE_ADDR = 0x061000
# [0] Task Running, [2] Conty Connected, [4] SCM Connected, [8] Program State
INDY_SHM_ROBOT_STATE_ADDR = 0x062000
# [0] Ready, [1] Emergency, [2] Collision, [3] Error, [4] Busy, [5] Move Finished, [8] Resetting
INDY_SHM_ROBOT_CTRL_STATUS_ADDR = 0x063000
# [256] Robot Model, [128] Build Version, [128] Build Data
INDY_SHM_ROBOT_INFO_ADDR = 0x065000
INDY_SHM_REPORTER_STATE_ADDR = 0x068000

NRMK_SHM = "NRMKSystemData"
NRMK_SHM_LEN = 0x8000
NRMK_SHM_SYSTEM_ADDR = 0x0000

POSIX_MSG_QUEUE = '/mq_indyCARE'
MSG_COUNTER_SHM = 'indyCAREShm'

INDY_SHM_MGR_OFFSET = 64


'''         Struct Module (pack, unpack . . .)       '''
'''     format |     C type     |    Python          '''
'''       c    |      char      |  one length string '''
'''       b    |   signed char  |     Int (1)        '''
'''       B    |  unsigned char |     Int (1)        '''
'''       h    |      short     |     Int (2)        '''
'''       H    | unsigned short |     Int (2)        '''
'''       i    |       int      |     Int (4)        '''
'''       I    |  unsigned int  |     Long (4)       '''
'''       l    |       long     |     Int (4)        '''
'''       L    | unsigned long  |     Long (4)       '''
'''       f    |      float     |     Float (4)      '''
'''       d    |     double     |     Float (8)      '''
'''       s    |      char[]    |     String (1)     '''
'''       p    |      char[]    |     String         '''
'''       P    |      void *    |     Int (1)        '''


class ShmWrapper(object):
    def __init__(self, name, offset, size, flags=O_CREAT):  # flag = 0
        self.shm = SharedMemory(name, flags=flags)
        self.offset = offset + INDY_SHM_MGR_OFFSET
        self.size = size
        # print("Shared Memory:", name, self.offset, size)

    def read(self):
        lseek(self.shm.fd, self.offset, SEEK_SET)
        return read(self.shm.fd, self.size)

    def write(self):
        lseek(self.shm.fd, self.offset, SEEK_SET)
        return write(self.shm.fd, self.size)


class ShmSecondWrapper(object):
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


class MessageCounter(ShmWrapper):
    @property
    def counter(self):
        return unpack('I', super().read())[0]

    def inc(self):
        cnt = self.counter + 1
        lseek(self.shm.fd, self.offset, SEEK_SET)
        write(self.shm.fd, pack('I', cnt))
        # print('counter increased', cnt, self.counter)

    def set(self, cnt):
        lseek(self.shm.fd, self.offset, SEEK_SET)
        write(self.shm.fd, pack('I', cnt))



