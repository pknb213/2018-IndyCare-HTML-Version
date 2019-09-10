from utils import *


@app.route("/clip/check")
def clip_check():
    res = 'ok'
    #res = 'ready'
    # res = '1'
    return res


@app.route("/clip/<cam>")
def clip_cam(cam):
    print(cam)
    return send_from_directory(os.path.join(os.getcwd(), 'static'), 'Chronograf.mp4')


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
    
#  Real Code
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

