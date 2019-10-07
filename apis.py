from utils import *


# cache.hset(sn, 'ts', datetime.datetime.now().timestamp())
# cam = True
#
# if cache.hget(sn, 'clip') is None:  # 클립이 없으면, 아래로
#     cache.hset(sn, 'clip', 0 if cam else -1)  # cam 값이 있으면 0, 없으면 -1


@app.route("/ping", methods=["POST"])
def ping():
    print("Pong")
    return Response(status=200)


@app.route("/date/now")
def current_date():
    # print(datetime.now().astimezone(KST).strftime(fmt))
    return datetime.now().astimezone(KST).strftime(fmt)


@app.route("/reporter/robot/info", methods=["POST"])
def add_robot_info_from_reporter():
    print("INSET SN : ", request.json['sn'])
    sql = "INSERT INTO robots(sn) VALUES (\"%s\") " \
          "ON DUPLICATE KEY UPDATE sn = \"%s\"" % (request.json['sn'], request.json['sn'])
    MySQL.insert(sql)
    return Response("ok")


@app.route("/kpi/<sn>")
def get_kpi(sn):
    sql = "SELECT kpi0,kpi1,kpi2,kpi3,kpi4 FROM robots WHERE sn = \"%s\" " % sn
    res = MySQL.select(sql, multi=False)
    print("KPI Res : ", res)
    lis = []
    if res is not None and res is not False:
        for k, v in res.items():
            if v is not None:
                v = v.split(',')
                k = {'sn': sn, 'kpi': v[0], 'label': v[1], 'period': v[2], 'key': v[3], 'axis': v[4]}
            else:
                k = {'sn': None, 'kpi': None, 'label': None, 'period': None, 'key': None, 'axis': None}
            lis.append(k)
    return jsonify(lis)


@app.route("/robots")
def robots():
    sql = "SELECT sn, company, site, kpi0, kpi1, kpi2, kpi3, kpi4, model, header FROM robots"
    res = MySQL.select(sql)
    print(res)
    if res is not None and res is not False:
        for i in res:
            for k, v in i.items():
                if v is None:
                    i[k] = ''
            robot_state(i['sn'])
            print("Rstate [", i['sn'], "] :", cache.hget(i['sn'], 'state'))
            if not cache.hget(i['sn'], 'state'): i['state'] = "<img src='../static/img/icon_stoppage.svg' alt='btn_image' />"
            else:
                state = eval(cache.hget(i['sn'], 'state').decode())
                if state['error'] or state['collision'] > 0:
                    i['state'] = "<img src='../static/img/icon_error_occurred.svg' alt='btn_image' />"
                elif state['ready'] > 0 or state['busy'] > 0:
                    i['state'] = "<img src='../static/img/icon_operation.svg' alt='btn_image' />"
                else:
                    i['state'] = "<img src='../static/img/icon_stoppage.svg' alt='btn_image' />"
            i['kpi'] = i['kpi0'] + ', ' + i['kpi1'] + ', ' + i['kpi2'] + ', ' + i['kpi3'] + ', ' + i['kpi4']
            i['deploy'] = '<a href=/display?sn=%s>' \
                          '<img src="../static/img/icon_monitoring.svg" alt="download_menu" /></a>' % i['sn']
            del i['kpi0'], i['kpi1'], i['kpi2'], i['kpi3'], i['kpi4']

    return jsonify(res)


@app.route("/clip/<sn>/check", methods=["GET", "POST"])
def clip_check(sn):
    res = 'ok'
    # res = 'ready'
    # res = '1'

    # sn (clip) set -1 :  -1은 file이 없을 떄 (None)
    # file_name = 'Chronograf.mp4'
    # clip_path = os.path.join(os.getcwd(), 'static', file_name)
    if cache.hget(sn, 'clipname') is None: print("Clip is None")
    else:
        path = os.path.join(os.getcwd(), 'clips', cache.hget(sn, 'clipname').decode('utf-8'))
        if os.path.exists(path):
            try:
                os.unlink(path)
            except Exception as e:
                print("다른 프로세스가 파일을 사용 중입니다.")

    print("File : ", request.files)
    if request.files and request.method == "POST":
        if request.files['file'].name == 'No Camera':
            cache.hset(sn, 'clip', -1)
            # return Response("Fail", status=404)
            return 'Fail'
    else:
        if not cache.exists('clipname', 'clip'):
            cache.hset(sn, 'clipname', 'No Clip')
            print("hset : ", sn, 'clipname', 'No Clip')
            time.sleep(0.02)  # for scheduling
            cache.hset(sn, 'clip', -1)
            print("hset : ", sn, 'clip', -1)
            return 'ok'

    file_name = request.files['file'].filename
    clip_path = os.path.join(os.getcwd(), 'clips', request.files['file'].filename)
    # Clip Save
    request.files['file'].save(clip_path)
    time.sleep(0.1)
    print("< Check > Clip Path : ", clip_path)
    # added file.save
    cache.hset(sn, 'clipname', file_name)
    print("hset : ", sn, 'clipname', file_name)
    time.sleep(0.02)  # for scheduling
    cache.hset(sn, 'clip', datetime.now().timestamp())
    print("hset : ", sn, 'clip', datetime.now().timestamp())

    time.sleep(10)

    clip = cache.hget(sn, 'clip')
    if clip is None: clip = 0
    if float(clip) < 0:
        cache.hset(sn, 'clip', 0)
        print("No Camera : sn (clip) set 0")
    else:
        print("Check OK")

    return 'ok'


@app.route("/clip/<sn>/<cam>")
def clip_cam(sn, cam):
    print(sn, cam, request.args['ts'])
    clip_path = os.path.join(os.getcwd(), 'clips')
    print("Clip Path : ", clip_path)

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
                                      as_attachment=True,
                                      attachment_filename=cache.hget(sn, 'clipname').decode('utf-8'))
            return res

        t1 = datetime.now()
        print('Clip Waiting', t1.timestamp() - t0.timestamp())
        time.sleep(1)

    return Response("Error", status=404)


@app.route("/clip/poster")
def clip_poster():
    clip_path = os.path.join(os.getcwd(), 'clips')
    return send_from_directory(clip_path, "video_loading.jpg")


@app.route("/clip/poster/error")
def error_clip_poster():
    clip_path = os.path.join(os.getcwd(), 'clips')
    return send_from_directory(clip_path, "pung.jpg")


# todo : Event Function
@app.route("/event/<sn>", methods=["POST"])
def add_event(sn):
    # todo : DB에 저장 ( 테이블 만들기 위한 용도 ), 여기서 Javascript에게 SSE로 테이블 로딩 할 수 있음
    print("Insert Mysql : ", request.json)
    sql = "INSERT INTO events(json, sn) " \
          "VALUES(\"%s\", \"%s\")" % (str(request.json), sn)
    MySQL.insert(sql)
    load_sse_command(sn, '_event')
    return Response('ok')


@app.route("/list/events/<sn>")
def get_event_list_for_datatable(sn):
    # todo : DataTable에 출력할 용도인 API
    sql = "SELECT idx, json, file, sn, " \
          "DATE_FORMAT(CONVERT_TZ(occurrence_time, '+00:00', '+09:00'), '%%Y-%%m-%%d %%H:%%i') " \
          "as occurrence_time " \
          "FROM events " \
          "WHERE sn=\"%s\" ORDER BY occurrence_time DESC LIMIT 5 " % sn
    res = MySQL.select(sql, True)

    if not res: return jsonify('')
    for i in res:
        a = i['json'].replace("\'", "\"")
        a = a.replace("\\", "\\\\")
        a = json.loads(a)
        i['code'] = get_robot_code_description(a['code'])
        # a = a['log'].split('\\')  # For Window
        a = a['log'].split('/')  # For Linux
        i['down'] = '<a class=c_hyper href=/file/event/%s/%s>' \
                    '<img src="../static/img/icon-download.svg" alt="download_menu" /></a>' % (a[-1], i['sn'])

    return jsonify(res)


@app.route("/list/events2/<sn>")
def get_event_list_for_datatable2(sn):
    # todo : DataTable에 출력할 용도인 API
    sql = "SELECT idx, json, file, sn, " \
          "DATE_FORMAT(CONVERT_TZ(occurrence_time, '+00:00', '+09:00'), '%%Y-%%m-%%d %%H:%%i') " \
          "as occurrence_time " \
          "FROM events " \
          "WHERE sn=\"%s\" ORDER BY occurrence_time DESC " % sn
    res = MySQL.select(sql, True)

    if not res: return jsonify('')
    for i in res:
        a = i['json'].replace("\'", "\"")
        a = a.replace("\\", "\\\\")
        a = json.loads(a)
        i['code'] = get_robot_code_description(a['code'])
        # a = a['log'].split('\\')  # For Window
        a = a['log'].split('/')  # For Linux
        i['down'] = '<a class=c_hyper href=/file/event/%s/%s>' \
                    '<img src="../static/img/icon-download.svg" alt="download_menu" /></a>' % (a[-1], i['sn'])

    return jsonify(res)


@app.route("/file/event/<filename>/<sn>", methods=["GET", "POST"])
def get_event_file(filename, sn):
    # todo : 버튼 클릭했을 때, 불려지는 API로 그리고 나서 SSE로 reporter에게 파일 달라고 함
    print("File : ", request.files)
    clip_path = os.path.join(os.getcwd(), 'clips')
    if request.method == "GET":
        cache.hset(sn, 'event_log', 0)
        print("Log를 요청하겠사와요")
        load_sse_command(sn, '_event_log', {'sn': sn, 'filename': filename})
    elif request.method == "POST":
        if request.files:
            file_name = request.files['file'].filename
            request.files['file'].save(os.path.join(clip_path, file_name))
            cache.hset(sn, 'event_log', 1)
            cache.hset(sn, 'log_name', file_name)
            return Response('ok')
        else:
            return Response("Empty the File", status=404)
    else:
        return Response("Undefined Http Method Type")

    t1 = t0 = datetime.now()
    while t1.timestamp() - t0.timestamp() <= app.config['ROBOT_DATA_WAIT_TIMEOUT']:
        st = int(cache.hget(sn, 'event_log'))
        if st < 0:
            print("Fail")
            return Response("No Log", status=404)
        if st > 0:
            res = send_from_directory(clip_path, cache.hget(sn, 'log_name').decode('utf-8'),
                                      as_attachment=True,
                                      attachment_filename=cache.hget(sn, 'log_name').decode('utf-8'))
            print("Succ :", res)
            print(cache.hgetall(sn))
            return res

        time.sleep(1)
        t1 = datetime.now()
        print('Log Waiting', t1.timestamp() - t0.timestamp())
    return load_sse_command(sn, '_event', {"fail": "저장된 Event 파일을 가져오는 것을 실패했습니다. ㅜㅁㅜ"})


# Todo : Reporter Server API
@app.route("/report/robot/state/<sn>", methods=["POST"])
def report_robot_state(sn):
    print("Reporter State :", request.json)
    sql = "INSERT INTO robot_states(serial_number, state) VALUES (\"%s\", \"%s\") " \
          % (sn, request.json)
    MySQL.insert(sql)
    return Response("ok")


@app.route("/robot/state/<sn>")
def robot_state(sn):
    sql = "SELECT state FROM robot_states " \
          "WHERE serial_number = \"%s\" AND date >= \"%s\" AND date < \"%s\" " \
          "ORDER BY date DESC LIMIT 1 " \
          % (sn, (datetime.utcnow() - timedelta(seconds=30)).strftime(fmtAll), datetime.utcnow().strftime(fmtAll))
    res = MySQL.select(sql, False)
    print("State Loop Res [%s]: " % sn, res)
    if res is False:
        dic = str({'busy': 0, 'collision': 0, 'emergency': 0, 'error': 0, 'home': 0,
                   'finish': 0, 'ready': 0, 'resetting': 0, 'zero': 0, 'is_server_connected': 1})
        cache.hset(sn, 'state', dic)
        return jsonify(dic)

    cache.hset(sn, 'state', res['state'])
    return jsonify(res['state'])


@app.route("/opdata/<sn>/<axis>/<key>/recent/<period>")
@app.route("/opdata/<sn>", methods=["POST"])
def opdate(sn, axis=1, key='', period=''):
    if request.method == 'GET':
        print("Opdata Loop SN : %s, Axis : %s, Key : %s, Time : %s" % (sn, axis, key, datetime.now().strftime(fmtAll)))
        if key == 'count':
            sql = "SELECT DATE_FORMAT(CONVERT_TZ(MAX(x), '+00:00', '+09:00'), '%%m-%%d %%H:%%i') m, " \
                  "COUNT(y) from opdatas " \
                  "WHERE x >= \"%s\" AND x < \"%s\" AND serial_number = \"%s\" " \
                  "GROUP BY ROUND(UNIX_TIMESTAMP(x) / 600) ORDER BY m DESC LIMIT 10" \
                  % ((datetime.utcnow() - timedelta(minutes=180)).strftime(fmtAll), datetime.utcnow().strftime(fmtAll), sn)
            res = MySQL.select(sql)
            # print("Res : ", res)
            if res is not False and res is not None:
                for i in res:
                    i['x'] = i['m']
                    i['y'] = i['COUNT(y)']
                    del i['m'], i['COUNT(y)']
        elif key == 'mean' and axis == '1':
            sql = "SELECT DATE_FORMAT(CONVERT_TZ(x, '+00:00', '+09:00'), '%%m-%%d %%H:%%i') m, ROUND(AVG(y), 2) " \
                  "FROM analog_opdatas " \
                  "WHERE x >= \"%s\" AND x < \"%s\" AND serial_number = \"%s\" GROUP BY m ORDER by m DESC LIMIT 80" \
                  % ((datetime.utcnow() - timedelta(hours=2)).strftime(fmtAll), datetime.utcnow().strftime(fmtAll), sn)
            res = MySQL.select(sql)
            if res is not False and res is not None:
                for i in res:
                    i['x'] = i['m']
                    i['y'] = i['ROUND(AVG(y), 2)']
                    del i['m'], i['ROUND(AVG(y), 2)']
        elif key == 'mean' and axis == '6':
            sql = "SELECT DATE_FORMAT(CONVERT_TZ(x, '+00:00', '+09:00'), '%%m-%%d %%H:%%i') m, " \
                  "ROUND(AVG(joint0), 2), ROUND(AVG(joint1), 2), " \
                  "ROUND(AVG(joint2), 2), ROUND(AVG(joint3), 2), " \
                  "ROUND(AVG(joint4), 2), ROUND(AVG(joint5), 2) FROM temperature_opdatas " \
                  "WHERE x >= \"%s\" AND x < \"%s\" AND serial_number = \"%s\" GROUP BY m ORDER by m DESC LIMIT 80" \
                  % ((datetime.utcnow() - timedelta(hours=2)).strftime(fmtAll), datetime.utcnow().strftime(fmtAll), sn)
            res = MySQL.select(sql)
            # print("Res : ", res)

            az = []
            bz = []
            cz = []
            dz = []
            ez = []
            fz = []

            if res is None or type(res) is bool: return jsonify(res)
            for i in res:
                a = {'x': i['m'], 'y': i['ROUND(AVG(joint0), 2)']}
                b = {'x': i['m'], 'y': i['ROUND(AVG(joint1), 2)']}
                c = {'x': i['m'], 'y': i['ROUND(AVG(joint2), 2)']}
                d = {'x': i['m'], 'y': i['ROUND(AVG(joint3), 2)']}
                e = {'x': i['m'], 'y': i['ROUND(AVG(joint4), 2)']}
                f = {'x': i['m'], 'y': i['ROUND(AVG(joint5), 2)']}
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
            sql = "INSERT INTO opdatas(msg, y, serial_number) " \
                  "VALUES (\"%s\", \"%s\", \"%s\") " % (request.json['msg'], request.json['mdata'], sn)
            MySQL.insert(sql)
        elif request.json['mtype'] is 2:
            print(request.json, len(request.json['mdata']))
            if len(request.json['mdata']) == 1:
                sql = 'INSERT INTO analog_opdatas(msg, serial_number, y) VALUES (\"%s\", \"%s\", \"%s\") ' \
                      % (request.json['msg'], sn, request.json['mdata'])
            else:
                temp = request.json['mdata'].split(',')
                sql = "INSERT INTO temperature_opdatas(msg, serial_number, joint0, joint1, joint2, joint3, joint4, joint5) " \
                      "VALUES (\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\") " \
                      % (request.json['msg'], sn, temp[0], temp[1], temp[2], temp[3], temp[4], temp[5])
            MySQL.insert(sql)
        else:
            print("Insert Fail : ", request.json)
        return Response('ok')
        # sql = "INSERT INTO opdatas(x, y) VALUES (\"%s\", \"%s\") " % (request.json['x'], request.json['y'])
        # MySQL.insert(sql)


@app.route("/reporter/kpi/<sn>", methods=["POST"])
def post_reporter_kpi(sn):
    # todo : 존재하면 Update로 해야함
    print("Reporter KPI :", request.json)
    if request.json is not None or request.json is not False:
        kpi_num = request.json['mdata'].split(',')[0]
    else:
        return Response('Fail')
    sql = "INSERT INTO robots (sn, %s) " \
          "VALUES (\"%s\", \"%s\") " \
          "ON DUPLICATE KEY UPDATE %s=\"%s\" " \
          % (kpi_num, sn, request.json['mdata'], kpi_num, request.json['mdata'])
    MySQL.insert(sql)
    return Response('ok')


