import eventlet
from flask import Flask, render_template, Response, request, redirect, url_for, session, flash, jsonify ,make_response
from flask_socketio import SocketIO, emit
import json
import pymysql
from datetime import datetime
from flask_mqtt import Mqtt
import time
from config import *
import cv2, queue, threading

eventlet.monkey_patch(os=False, select=False, socket=False, thread=True,time=False)
async_mode = None
eventlet.monkey_patch()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app, async_mode=async_mode)

#mqtt
app.config['MQTT_BROKER_URL'] = 'touch-mqtt.touch-ics.com'
app.config['MQTT_BROKER_PORT'] = 1883
mqtt = Mqtt(app)


# bufferless VideoCapture


@mqtt.on_message()
def handle_message(client, userdata, message):
    payload=json.loads(message.payload)
    # print(payload)
    socketio.emit('datas-sensor',data = payload)
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('Depa/smart_pole/id01')
    # print("Connected from broker")

@app.route('/')
def showData():
    statedate=False
    countmesege=0
    datefull=None
    conn = connect_db()
    with conn:
        cur = conn.cursor()
        cur.execute("select * from  history_alarm")
        rows = cur.fetchall()
        cur.close()
        now = datetime.now() 
        date = now.strftime("%m/%d/%Y")
        datefull  = now.strftime("%d %B %Y")
        for f in rows:
            if str(f[1]) == date :
                countmesege = countmesege+1
        return render_template('index.html',datas = rows ,currentdate = statedate, date = datefull ,countmesege = countmesege)

def connect_db():
    return pymysql.connect(host=DBHOST, user=DBUSER, port=DBPORT, password=DBPASS, db=DBNAME)

@app.route('/reload', methods=['GET'])
def reload():
    if request.method == 'GET' :
        socketio.emit('datas-event',"end_call1")
        return '',200

@app.route('/Webhook', methods=['POST','GET'])
def Webhook():
    if request.method == 'POST' or request.method == 'GET' :
        print("webhook success")
        status = request.args.get('status')
        print(status)
        now = datetime.now() 
        date = now.strftime("%m/%d/%Y")
        time = now.strftime("%H:%M")
        location = "depa Thailand"
        conn = connect_db()
        if status == "alarm_sos1" :
            with conn.cursor() as cursor :
                sql = "insert into `history_alarm` (date,`time`,location) values(%s,%s,%s)"
                cursor.execute(sql,(date,time,location))
                conn.commit()
                cursor.close()
                print("insert database success")
        if (status == "end_call1") :
            cv2.destroyAllWindows()
        socketio.emit('datas-event',status)
        return '',200


class VideoCaptureyy:
  def __init__(self, name):
    self.cap = cv2.VideoCapture(name)
    self.q = queue.Queue()
    t = threading.Thread(target=self._reader)
    t.daemon = True
    t.start()

  # read frames as soon as they are available, keeping only most recent one
  def _reader(self):
    while True:
      ret, frame = self.cap.read()
      if not ret:
        break
      if not self.q.empty():
        try:
          self.q.get_nowait()   # discard previous (unprocessed) frame
        except queue.Empty:
          pass
      self.q.put(frame)

  def read(self):
    return self.q.get()


def gen():
    
    # RTSP_URL = 'rtsp://admin:t0uchiot@161.82.233.180/unicast/c2/s2/live' 
    # RTSP_URL = 'rtsp://192.168.1.128/user=admin&password=tlJwpbo6&channel=1&stream=0.sdp?real_stream'   
    RTSP_URL = 'rtsp://admin:T0UCHics@161.82.233.182:14432/LiveMedia/ch1/Media1/trackID=4'
    cap = cv2.VideoCapture(RTSP_URL)
    # cap.set(CV_CAP_PROP_BUFFERSIZE, 3)
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret: #if vid finish repeat
            print("Can't receive frame (stream end?). Exiting ...")
            cap = cv2.VideoCapture(RTSP_URL)
            continue
        if ret:
            frame = cv2.imencode('.jpg', frame)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    # cap = VideoCaptureyy('rtsp://admin:T0UCHics@161.82.233.182:14432/LiveMedia/ch1/Media1/trackID=4')
    # while True:
    #     # time.sleep(.5)   # simulate time between events
    #     ret, frame = cap.read()
    #     if ret:
    #         frame = cv2.imencode('.jpg', frame)[1].tobytes()
    #         yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
      
        
        


@app.route('/video_feed')
def video_feed():
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0',port=80,debug=True, use_reloader=False)
