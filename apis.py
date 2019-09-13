from utils import *

# cache.hset(sn, 'ts', datetime.datetime.now().timestamp())
# cam = True
#
# if cache.hget(sn, 'clip') is None:  # 클립이 없으면, 아래로
#     cache.hset(sn, 'clip', 0 if cam else -1)  # cam 값이 있으면 0, 없으면 -1


@app.route("/clip/<sn>/check")
def clip_check(sn):
    res = 'ok'
    #res = 'ready'
    # res = '1'

    # todo : Reporter 함수
    def get_latest_clip():
        check_duration = 0.5
        timeout = 10
        while timeout > 0:
            clips = glob.glob(os.path.join(os.getcwd(), 'clips/')  + '*.mp4')
            if len(clips) > 0:
                print(clips)
                return clips[0]
            time.sleep(check_duration)
            timeout -= check_duration
        print('no file...')
        return None

    # sn (clip) set -1 :  -1은 file이 없을 떄 (None)
    # file_name = 'Chronograf.mp4'
    # clip_path = os.path.join(os.getcwd(), 'static', file_name)

    # todo : 여기다 request.file을 넣어야 함

    print("Get Lastest Clip : ", get_latest_clip())
    if get_latest_clip() is None:
        file_name = 'No FIle'
    else:
        file_name = get_latest_clip().split('\\')[-1]
    clip_path = get_latest_clip()
    print(clip_path)
    # added file.save
    cache.hset(sn, 'clipname', file_name)
    print("hset : ", sn, 'clipname', file_name)
    time.sleep(0.02)  # for scheduling
    cache.hset(sn, 'clip', datetime.now().timestamp())
    print("hset : ", sn, 'clip', datetime.now().timestamp())

    time.sleep(10)

    clip = cache.hget(sn, 'clip')
    if float(clip) < 0:
        cache.hset(sn, 'clip', 0)
        print("No Camera : sn (clip) set 0")
    else:
        print("Check OK")

    return res


@app.route("/clip/<sn>/<cam>")
def clip_cam(sn, cam):
    print(sn, cam)
    clip_path = os.path.join(os.getcwd(), 'clips')
    print("Clip Path : ", clip_path)

    t0 = t1 = datetime.now()
    # cache.hset(sn, 'clip', 0)  # 클립이 0이면 Waiting 반복, -1이면 Fail, 0보다 크면 영상 존재
    print("hget SN (clip) : ", cache.hget(sn, 'clip'))
    while t1.timestamp() - t0.timestamp() <= app.config['ROBOT_DATA_WAIT_TIMEOUT']:
        st = float(cache.hget(sn, 'clip'))

        if st < 0:
            print("Fail")
            return Response("Fail")
        if st > 0:
            print("Succ")
            print(cache.keys())
            print(cache.hgetall('D1234'))
            return send_from_directory(clip_path, cache.hget(sn, 'clipname').decode('utf-8'))

        time.sleep(1)
        t1 = datetime.now()
        print('Clip Waiting', t1.timestamp() - t0.timestamp())

    return Response("Error", status=404)


@app.route("/clip/poster")
def clip_poster():
    clip_path = os.path.join(os.getcwd(), 'clips')
    return send_from_directory(clip_path, "pung.jpg")

'''
# 원래 카메라 확인 함수
@app.route("/clips/<sn>/check")
def get_blackbox_camera_check(sn):
    return Robot.check_camera(sn)
    
def check_camera(sn):
    r_log('check camera', sn, 'clip', cache.hget(sn, 'clip'))
    hget_clip = cache.hget(sn, 'clip')
    if not Robot.is_connected(sn):
        return Response("Not connected")
    elif float(hget_clip) < 0:  # 누가 clip을 설정해 주지? 카메라가 없는 경우, 카메라가 고장난 경우, ... 그냥 카메라 상태를 report하게 할까?
        cache_set(sn, 'clip', 0)
        print("No Camera")
        return Response("No camera")
    else:
        print("OK")
        return Response('OK')
        
#  Test Code 
@app.route("/clips/<sn>")
def get_blackbox_clip(sn):
    print(">> get_blackbox_clip")
    return Robot.get_blackbox_clip(sn, 1)

@app.route("/clips/<sn>/<cam>")
def get_blackbox_clip_cam(sn, cam):
    print(">> get_blackbox_clip_cam %s" % cam)
    return Robot.get_blackbox_clip(sn, cam)

def get_blackbox_clip(sn, cam=1):
    r_log('get clip', sn, cam)
    clippath = get_clip_path(clipname(sn))
    print("GET Clip Nmae : %s" % clipname(sn))
    print("GET Clip Path : %s" % clippath)
    if not path.exists(clippath) or \
            'clip'.encode('utf-8') not in cache.hkeys(sn) or \
            datetime.now().timestamp() - float(cache.hget(sn, 'clip')) > CLIP_INVALID_TIME:
        cache_set(sn, 'clip', 0)
        print('sse event : clip', str(cam))
        sse.publish({"message": str(cam)}, channel=sn + '_clip')
    t1 = t0 = datetime.now()
    while t1.timestamp() - t0.timestamp() <= app.config['ROBOT_DATA_WAIT_TIMEOUT']:
        st = float(cache.hget(sn, 'clip'))
        # 영상이 제대로 저장되면 시간으로 clip field의 값이 되므로 st < 0이면 영상 없음
        if st < 0:
            return Response('No camera')
        if st > 0:
            clip = clipname(sn)
            print('Send clip...', get_clip_path(clip))
            res = send_from_directory(app.config['BLACKBOX_CLIP_PATH'], clip)
            print('res:', res)
            return res
        time.sleep(ROBOT_DATA_POLLING)
        t1 = datetime.now()
        print('clip waiting...', t1.timestamp() - t0.timestamp())

    return Response('Error')

'''

