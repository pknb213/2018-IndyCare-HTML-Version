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
    res = MySQL.select(sql)
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
            datetime.now().timestamp() - float(cache.hget(sn, 'clip')) > 60:
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
    MySQL.insert(sql)
    load_sse_command('D1234', '_ev')
    return Response('ok')


@app.route("/list/events/<sn>")
def get_event_list_for_datatable(sn):
    # todo : DataTable에 출력할 용도인 API
    sql = "SELECT idx, json, file, sn, occurrence_time FROM events WHERE sn=\"%s\" LIMIT 5 " % sn
    res = MySQL.select(sql, True)

    if not res: return jsonify('')
    for i in res:
        a = i['json'].replace("\'", "\"")
        a = a.replace("\\", "\\\\")
        a = json.loads(a)
        a = a['log'].split('\\')
        i['down'] = '<a class=c_hyper href=/file/event/%s/%s>' \
                    '<img src="../static/img/icon-dropdown-menu.svg" alt="dropdown_menu" /></a>' % (a[-1], i['sn'])

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


@app.route("/opdata/<sn>/<key>/recent/<period>")
@app.route("/opdata", methods=["POST"])
def opdate(sn='TEST1234', key='', period=''):
    if request.method == 'GET':
        print("SN : %s, Key : %s, Time : %s" % (sn, key, datetime.now().strftime(fmtAll)))
        if key == 'count':
            sql = "SELECT concat(" \
                  "date(opdatas.x) , ' ', sec_to_time(time_to_sec(x)-time_to_sec(x)%%(15*60)+(15*60))) as division_date, " \
                  "COUNT(y) from opdatas " \
                  "WHERE x >= \"%s\" AND x < \"%s\" group by division_date" \
                  % ((datetime.utcnow() - timedelta(minutes=60)).strftime(fmtAll), datetime.utcnow().strftime(fmtAll))
            res = MySQL.select(sql)
            print("Res : ", res)
            if res is not False:
                for i in res:
                    i['x'] = i['division_date']
                    i['y'] = i['COUNT(y)']
                    del i['division_date'], i['COUNT(y)']
        elif key == 'mean':
            sql = "SELECT x, msg, joint0, joint1, joint2, joint3, joint4, joint5 FROM temperature_opdatas " \
                  "WHERE x >= \"%s\" AND x < \"%s\" ORDER by x DESC LIMIT 50" \
                  % ((datetime.utcnow() - timedelta(hours=1)).strftime(fmtAll), datetime.utcnow().strftime(fmtAll))
            res = MySQL.select(sql)
            # print("Res : ", res)

            az = []
            bz = []
            cz = []
            dz = []
            ez = []
            fz = []

            if res is None: return jsonify(res)
            for i in res:
                a = {'x': i['x'].strftime(fmtAll), 'y': i['joint0']}
                b = {'x': i['x'].strftime(fmtAll), 'y': i['joint1']}
                c = {'x': i['x'].strftime(fmtAll), 'y': i['joint2']}
                d = {'x': i['x'].strftime(fmtAll), 'y': i['joint3']}
                e = {'x': i['x'].strftime(fmtAll), 'y': i['joint4']}
                f = {'x': i['x'].strftime(fmtAll), 'y': i['joint5']}
                az.append(a)
                bz.append(b)
                cz.append(c)
                dz.append(d)
                ez.append(e)
                fz.append(f)

            aa = [az, bz, cz, dz, ez, fz]
            return jsonify(aa)
        else:
            res = None
        return jsonify(res)

    if request.method == 'POST':
        # todo : Message Type에 따른 Count, Mean 등 조건으로 나눠서 Query를 변환해야 함
        # mtype, msg, mdata
        if request.json['mtype'] is 1:
            print(request.json)
            sql = "INSERT INTO opdatas(msg, y) VALUES (\"%s\", \"%s\") " % (request.json['msg'], request.json['mdata'])
            MySQL.insert(sql)
        elif request.json['mtype'] is 2:
            print(request.json)
            temp = request.json['mdata'].split(',')
            sql = "INSERT INTO temperature_opdatas(msg, joint0, joint1, joint2, joint3, joint4, joint5) " \
                  "VALUES (\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\") " \
                  % (request.json['msg'], temp[0], temp[1], temp[2], temp[3], temp[4], temp[5])
            MySQL.insert(sql)
        else:
            print("Insert Fail : ", request.json)
        return Response('ok')
        # sql = "INSERT INTO opdatas(x, y) VALUES (\"%s\", \"%s\") " % (request.json['x'], request.json['y'])
        # MySQL.insert(sql)


@app.route("/reporter/kpi", methods=["POST"])
def post_reporter_kpi():
    pass


@app.route("/reporter/robot/status", methods=["POST"])
def post_reporter_robot_status():
    pass


@app.route("/robot/status")
def get_robot_status():
    pass

# Todo : 만들어야하는 API :
#  report_robot_opdata : 위의 Opdata에 들어오는 값으로 조건 걸고 mean, count를 구별해야 함
#  report_kpi_string : KPI Mysql에 저장하는 용도
#  report_robot_status : 전의 코드는 Redis에 저장하고, get API를 통해 Redis에서 가져와서 AJAX해서 페이지가 가져감.


@app.route("/kpi/<sn>")
def get_kpi(sn):
    sql = "SELECT kpi0,kpi1,kpi2,kpi3,kpi4 FROM robots WHERE sn = \"%s\" " % sn
    res = MySQL.select(sql, multi=False)
    print("Res : ", res)
    lis = []
    if res is not None:
        for k, v in res.items():
            if v is not None:
                v = v.split(',')
                k = {'sn': sn, 'kpi': v[0], 'label': v[1], 'period': v[2], 'key': v[3], 'axis': v[4]}
            else:
                k = {'sn': None, 'kpi': None, 'label': None, 'period': None, 'key': None, 'axis': None}
            lis.append(k)
    return jsonify(lis)


# todo : Opdata Test 용도
@app.route("/opdata2")
def opdata2():
    res = [
        {"x": datetime.now(), "y": random.randrange(0, 50)},
        {"x": datetime.now() + timedelta(hours=1), "y": random.randrange(0, 50)},
        {"x": datetime.now() + timedelta(hours=2), "y": random.randrange(0, 50)},
        {"x": datetime.now() + timedelta(hours=3), "y": random.randrange(0, 50)},
        {"x": datetime.now() + timedelta(hours=4), "y": random.randrange(0, 50)},
        {"x": datetime.now() + timedelta(hours=5), "y": random.randrange(0, 50)},
        {"x": datetime.now() + timedelta(hours=6), "y": random.randrange(0, 50)},
        {"x": datetime.now() + timedelta(hours=7), "y": random.randrange(0, 50)},
        {"x": datetime.now() + timedelta(hours=8), "y": random.randrange(0, 50)},
        {"x": datetime.now() + timedelta(hours=9), "y": random.randrange(0, 50)},
    ]
    return jsonify(res)
