import os
import time
import glob


class EventFiles:
    EVENT_DIRECTORY = os.path.join('/home/user/', 'save-videos/')
    # EVENT_DIRECTORY = os.path.join(os.getcwd(), 'save-videos\\')
    latest_log = ''

    @classmethod
    def get_directory_path(cls):
        return EventFiles.EVENT_DIRECTORY

    @classmethod
    def get_latest_clip(cls):
        check_duration = 1
        timeout = 10
        while timeout > 0:
            clips = glob.glob(EventFiles.EVENT_DIRECTORY + '*.mp4')
            if len(clips) > 0:
                return clips[0]
            time.sleep(check_duration)
            timeout -= check_duration
        print('no clip file...')
        return None

    @classmethod
    def get_latest_log(cls):
        check_duration = 1
        timeout = 10
        while timeout > 0:
            logs = glob.glob(EventFiles.EVENT_DIRECTORY + '*.tgz')
            if len(logs) > 0:
                logs.sort(key=os.path.getmtime, reverse=True)
                return logs[0]
            time.sleep(check_duration)
            timeout -= check_duration
        return ''

    @classmethod
    def check_if_new_log(cls):
        tmp = cls.get_latest_log()
        if tmp != cls.latest_log:
            if len(cls.latest_log) == 0:
                cls.latest_log = tmp
                return False
            else:
                cls.latest_log = tmp
                return True
        return False










