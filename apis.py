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


@app.route("/robots")
def robots():
    sql = "SELECT sn, company, site FROM robots"
    res = MySQL.mysql_select(sql)
    for i in res:
        i['Deploy'] = "<a href=/deployment/%s>Deployment</a>" % i['sn']
    return jsonify(res)


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
            print(cache.hgetall(sn))
            res = send_from_directory(clip_path, cache.hget(sn, 'clipname').decode('utf-8'),
                                      as_attachment=True, attachment_filename=cache.hget(sn, 'clipname').decode('utf-8'))
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
    print("Insert Mysql : ", request.json)
    sql = "INSERT INTO events(json, sn) " \
          "VALUES(\"%s\", \"%s\")" % (str(request.json), 'D1234')
    MySQL.mysql_insert(sql)
    load_sse_command('D1234', '_ev')
    return Response('ok')


@app.route("/list/events/<sn>")
def get_event_list_for_datatable(sn):
    # todo : DataTable에 출력할 용도인 API
    sql = "SELECT idx, json, file, sn, occurrence_time FROM events WHERE sn=\"%s\"" % sn
    res = MySQL.mysql_select(sql, True)

    if not res: return jsonify('')
    for i in res:
        a = i['json'].replace("\'", "\"")
        a = a.replace("\\", "\\\\")
        a = json.loads(a)
        a = a['log'].split('\\')
        i['down'] = '<a class=c_hyper href=/file/event/%s/%s>Download</a>' % (a[-1], i['sn'])

    return jsonify(res)


@app.route("/file/event/<filename>/<sn>", methods=["GET", "POST"])
def get_event_file(filename, sn):
    # todo : 버튼 클릭했을 때, 불려지는 API로 그리고 나서 SSE로 reporter에게 파일 달라고 함
    print("File : ", request.files)
    clip_path = os.path.join(os.getcwd(), 'clips')
    if request.files:
        file_name = request.files['file'].filename
        request.files['file'].save(os.path.join(clip_path, file_name))
        cache.hset(sn, 'event_log', 1)
        cache.hset(sn, 'log_name', file_name)
    else:
        cache.hset(sn, 'event_log', 0)
        print("Log를 요청하겠사와요")
        load_sse_command(sn, '_event_log', {'sn': sn, 'filename': filename})

    t1 = t0 = datetime.now()
    while t1.timestamp() - t0.timestamp() <= app.config['ROBOT_DATA_WAIT_TIMEOUT']:
        st = int(cache.hget(sn, 'event_log'))
        if st < 0:
            print("Fail")
            return Response("No Log")
        if st > 0:
            print("Succ")
            print(cache.hgetall(sn))
            return send_from_directory(clip_path, cache.hget(sn, 'log_name').decode('utf-8'),
                                       as_attachment=True, attachment_filename=cache.hget(sn, 'log_name').decode('utf-8'))

        time.sleep(1)
        t1 = datetime.now()
        print('Log Waiting', t1.timestamp() - t0.timestamp())
    return Response('Error')


@app.route("/opdata", methods=["POST"])
def opdate():
    print(request.json)
    sql = "INSERT INTO opdatas(y) VALUES (\"%s\") " % request.json['y']
    MySQL.mysql_insert(sql)
    return Response('ok')


@app.route("/opdata2")
def opdata2():

    return jsonify({"ok":"yes"})
