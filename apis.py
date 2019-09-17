from utils import *

# cache.hset(sn, 'ts', datetime.datetime.now().timestamp())
# cam = True
#
# if cache.hget(sn, 'clip') is None:  # 클립이 없으면, 아래로
#     cache.hset(sn, 'clip', 0 if cam else -1)  # cam 값이 있으면 0, 없으면 -1


@app.route("/ping")
def ping():
    print("Pong")
    return 1


@app.route("/clip/<sn>/check", methods=["GET", "POST"])
def clip_check(sn):
    res = 'ok'
    #res = 'ready'
    # res = '1'

    # sn (clip) set -1 :  -1은 file이 없을 떄 (None)
    # file_name = 'Chronograf.mp4'
    # clip_path = os.path.join(os.getcwd(), 'static', file_name)

    # todo : 여기다 request.file을 넣어야 함

    print("File : ", request.files)
    if request.files:
        if request.files['file'].name == 'No Camera':
            cache.hset(sn, 'clip', -1)
            return res
    else:
        if not cache.exists('clipname', 'clip'):
            cache.hset(sn, 'clipname', 'No Clip')
            print("hset : ", sn, 'clipname', 'No Clip')
            time.sleep(0.02)  # for scheduling
            cache.hset(sn, 'clip', -1)
            print("hset : ", sn, 'clip', -1)
            return res

    file_name = request.files['file'].filename
    clip_path = os.path.join(os.getcwd(), 'clips', request.files['file'].filename)
    request.files['file'].save(clip_path)

    print("< Check > Clip Path : ", clip_path)
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

    print(datetime.now().timestamp() - float(cache.hget(sn, 'clip')))
    if not os.path.exists(clip_path) or \
        'clip'.encode('utf-8') not in cache.hkeys(sn) or \
            datetime.now().timestamp() - float(cache.hget(sn, 'clip')) > 30:
        print("Clip을 SSE에게 요청하겠사와요")
        cache.hset(sn, 'clip', 0)
        sse.publish({"message": str(cam)}, channel=sn + '_clip')

    # cache.hset(sn, 'clip', 0)  # 클립이 0이면 Waiting 반복, -1이면 Fail, 0보다 크면 영상 존재
    print("hget SN (clip) : ", cache.hget(sn, 'clip'))
    t0 = t1 = datetime.now()
    while t1.timestamp() - t0.timestamp() <= app.config['ROBOT_DATA_WAIT_TIMEOUT']:
        st = float(cache.hget(sn, 'clip'))

        if st < 0:
            print("Fail")
            return Response("Fail")
        if st > 0:
            print("Succ")
            print(cache.keys())
            print(cache.hgetall('D1234'))
            res = send_from_directory(clip_path, cache.hget(sn, 'clipname').decode('utf-8'))
            print("Res : ", res)
            return res

        time.sleep(1)
        t1 = datetime.now()
        print('Clip Waiting', t1.timestamp() - t0.timestamp())

    return Response("Error", status=404)


@app.route("/clip/poster")
def clip_poster():
    clip_path = os.path.join(os.getcwd(), 'clips')
    return send_from_directory(clip_path, "pung.jpg")


# todo : Event Function
@app.route("/event", methods=["POST"])
def add_event():
    # todo : DB에 저장 ( 테이블 만들기 위한 용도 ), 여기서 Javascript에게 SSE로 테이블 로딩 할 수 있음
    print(request.json)
    sql = "INSERT INTO events(json, sn) " \
          "VALUES(\"%s\", \"%s\")" % (str(request.json), 'D1234')
    MySQL.mysql_insert(sql)
    load_sse_command('D1234')
    return Response('ok')


@app.route("/list/events")
def get_event_list_for_datatable():
    # todo : DataTable에 출력할 용도인 API
    sql = "SELECT idx, json, file, sn, occurrence_time FROM events"
    res = MySQL.mysql_select(sql, True)

    return res


@app.route("/1")
def get_event_file():
    # todo : 버튼 클릭했을 때, 불려지는 API로 그리고 나서 SSE로 reporter에게 파일 달라고 함
    return 1


@app.route("/2", methods=["POST"])
def new_event_file_from_reporter():
    # todo : Reporter의 SSE가 수행한 후, POST 파일 받는 API, request.file 개발
    return 1


# todo 근데 add event에서 uploader에게 파일 보내라고 하면 끝 아님? 그러면 get event file 필요없을거 같은데
# todo 아니면 용도를 버튼 api로만 바꾸든가, 버튼은 내부 저장소의 파일 전송하는 용도로만 쓰고, 총 api 수는 같네.