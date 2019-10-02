from posix_ipc import MessageQueue, SharedMemory, O_CREAT
from os import read, write, lseek, SEEK_SET
from struct import pack, unpack, calcsize

# Todo : SSE CLIENT : 'sudo pip3 install --ignore-installed sseclient'
# Todo : Posix IPC : Only Linux library, dependency : 'apt-get install python-dev', 'pip3 install posix_ipc'

INDY_SHM = "indySHM"
INDY_SHM_LEN = 0x1000000
# [0] : Error Code
INDY_SHM_ROBOT_ERROR_CODE_ADDR = 0x061000
ERROR_CODE_SHM_SIZE = 4
# [0] Task Running, [2] Conty Connected, [4] SCM Connected, [8] Program State
INDY_SHM_ROBOT_STATE_ADDR = 0x062000
ROBOT_STATE_SHM_SIZE = 9
# [0] Ready, [1] Emergency, [2] Collision, [3] Error, [4] Busy, [5] Move Finished, [6] Home, [7] Zero, [8] Resetting
INDY_SHM_ROBOT_CTRL_STATUS_ADDR = 0x063000
ROBOT_CTRL_STATUS_SHM_SIZE = 9
# [256] Robot Model, [128] Build Version, [128] Build Data, [128] Robot SN, [128] CtrlBox SN, [128] STEP SN
INDY_SHM_ROBOT_INFO_ADDR = 0x065000
ROBOT_INFO_SHM_SIZE = 0x000380
# [0] Reporter Running, [1] Server Connected
INDY_SHM_REPORTER_STATE_ADDR = 0x068000
REPORTER_STATE_SHM_SIZE = 2

NRMK_SHM = "NRMKSystemData"
NRMK_SHM_LEN = 0x8000
# [0] Running Time, [8] RT Cycle Time, [10] RT Cycle Jitter
# [18] Task Exec Period, [20] Task Exec Period Max, [28] Overrun Count
NRMK_SHM_SYSTEM_ADDR = 0x0000
SYSTEM_SHM_SIZE = 0x002c

MSG_COUNTER_SHM = 'indyCAREShm'
POSIX_MSG_QUEUE = '/mq_indyCARE'

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

'------------------ mtype description ----------------------'
'        mtype Range    |     Description                   '
'           1 ~ 99      |     Operation command             '
'         100 ~ 199     | Server configuration information  '
'         200 ~ 299     |     IndySW information            '
'-----------------------------------------------------------'
'             1         |        Count                      '
'             2         |        Mean                       '
'           100         |        KPI configuration          '
'           101         |        IP address                 '
'           102         |        Robot S/N                  '
'           200         |        IndySW version             '
'-----------------------------------------------------------'


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


class ErrorCode(ShmWrapper):
    @property
    def error_code(self):
        return unpack('i', super().read()[0:4])[0]

    @staticmethod
    def get_all_error(indyshm):
        keys = ['error_code']
        st = {}
        for key in keys: st[key] = getattr(indyshm, key)
        return st


class RobotState(ShmWrapper):
    @property
    def is_task_running(self):
        return super().read()[0]

    @property
    def conty_connected(self):
        return super().read()[2]

    @property
    def scm_connected(self):
        return super().read()[4]

    @property
    def program_state(self):
        return super().read()[8]

    @staticmethod
    def get_all_state(indyshm):
        keys = ['is_task_running', 'conty_connected', 'scm_connected', 'program_state']
        st = {}
        for key in keys: st[key] = getattr(indyshm, key)
        return st

    @staticmethod
    def check_is_task_running(indyshm):
        key = 'is_task_running'
        return getattr(indyshm, key)


class ControlState(ShmWrapper):
    @property
    def ready(self):
        return super().read()[0]

    @property
    def emergency(self):
        return super().read()[1]

    @property
    def collision(self):
        return super().read()[2]

    @property
    def error(self):
        return super().read()[3]

    @property
    def busy(self):
        return super().read()[4]

    @property
    def finish(self):
        return super().read()[5]

    @property
    def home(self):
        return super().read()[6]

    @property
    def zero(self):
        return super().read()[7]

    @property
    def resetting(self):
        return super().read()[8]

    @staticmethod
    def get_all_robot_state(indyshm):
        keys = ['busy', 'collision', 'emergency', 'error', 'home', 'finish', 'ready', 'resetting', 'zero']
        st = {}
        for key in keys: st[key] = getattr(indyshm, key)
        return st


class RobotInfoData(ShmWrapper):
    @property
    def robot_model(self):
        return super().read()[0: super().read()[0:].index(0)].decode()

    @property
    def robot_build_version(self):
        return super().read()[256: 256 + super().read()[256:].index(0)].decode()

    @property
    def robot_build_data(self):
        return super().read()[0x000180: 0x000180 + super().read()[0x000180:].index(0)].decode()

    @property
    def robot_serial_number(self):
        return super().read()[0x000200: 0x000200 + super().read()[0x000200:].index(0)].decode()

    @property
    def robot_control_box_serial_number(self):
        return super().read()[0x000280: 0x000280 + super().read()[0x000280:].index(0)].decode()

    @property
    def step_serial_number(self):
        return super().read()[0x000300: 0x000300 + super().read()[0x000300:].index(0)].decode()

    @staticmethod
    def get_all_robot_info_data(indyshm):
        keys = ['robot_model', 'robot_build_version', 'robot_build_data', 'robot_serial_number',
                'robot_control_box_serial_number', 'step_serial_number']
        st = {}
        for key in keys: st[key] = getattr(indyshm, key)
        return st

    @staticmethod
    def get_serial_number(indyshm):
        return getattr(indyshm, 'robot_serial_number')


class ReporterState(ShmWrapper):
    def __del__(self):
        lseek(self.shm.fd, self.offset, SEEK_SET)
        write(self.shm.fd, pack('b', 0))
        lseek(self.shm.fd, self.offset + 1, SEEK_SET)
        write(self.shm.fd, pack('b', 0))

    @property
    def is_reporter_running(self):
        return super().read()[0]

    @property
    def is_server_connected(self):
        return super().read()[1]

    @staticmethod
    def turn_on_reporter(indyshm):
        lseek(indyshm.shm.fd, indyshm.offset, SEEK_SET)
        return write(indyshm.shm.fd, pack('b', 1))

    @staticmethod
    def turn_on_server(indyshm):
        lseek(indyshm.shm.fd, indyshm.offset + 1, SEEK_SET)
        return write(indyshm.shm.fd, pack('b', 1))

    @staticmethod
    def turn_off_reporter(indyshm):
        lseek(indyshm.shm.fd, indyshm.offset, SEEK_SET)
        return write(indyshm.shm.fd, pack('b', 0))

    @staticmethod
    def turn_off_server(indyshm):
        lseek(indyshm.shm.fd, indyshm.offset + 1, SEEK_SET)
        return write(indyshm.shm.fd, pack('b', 0))

    @staticmethod
    def get_all_reporter_state(indyshm):
        keys = ['is_reporter_running', 'is_server_connected']
        st = {}
        for key in keys: st[key] = getattr(indyshm, key)
        return st


class SystemState(ShmWrapper):
    @property
    def running_time(self):
        return unpack('d', super().read()[0:8])[0]

    @property
    def rt_cycle_time(self):
        return unpack('I', super().read()[0x0008:0x000c])[0]

    @property
    def rt_cycle_Jitter(self):
        return unpack('I', super().read()[0x0010:0x0014])[0]

    @property
    def task_exec_period(self):
        return unpack('I', super().read()[0x0018:0x001c])[0]

    @property
    def task_exec_period_max(self):
        return unpack('I', super().read()[0x0020:0x0024])[0]

    @property
    def overrun_count(self):
        return unpack('I', super().read()[0x0028:0x002c])[0]

    @staticmethod
    def get_all_sys_state(indyshm):
        keys = ['running_time', 'rt_cycle_time', 'rt_cycle_Jitter', 'task_exec_period',
                'task_exec_period_max', 'overrun_count']
        st = {}
        for key in keys: st[key] = getattr(indyshm, key)
        return st

