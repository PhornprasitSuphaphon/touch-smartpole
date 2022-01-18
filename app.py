#import eventlet
from flask import Flask, render_template, Response, request, redirect, url_for, session, flash, jsonify ,make_response
from flask_socketio import SocketIO, emit
import json
import pymysql
from datetime import datetime
from flask_mqtt import Mqtt
from config import *
import cv2, queue, threading ,time
import multiprocessing as mp

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app, async_mode=async_mode)

#mqtt
app.config['MQTT_BROKER_URL'] = 'touch-mqtt.touch-ics.com'
app.config['MQTT_BROKER_PORT'] = 1883
mqtt = Mqtt(app)

async_mode = None

# bufferless VideoCapture
class VideoCapture:
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



@mqtt.on_message()
def handle_message(client, userdata, message):
    payload=json.loads(message.payload)
    #print(payload)
    socketio.emit('datas-sensor',data = payload)

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('Depa/smart_pole/id01')
    print("Connected from broker")

@app.route('/')
def showData():
    statedate=False
    countmesege=0
    datefull=None
    conn = connect_db()
    datecurent = []
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
                datecurent.append(f)
                print(datecurent)
        return render_template('index.html',datas = datecurent ,currentdate = statedate, date = datefull ,countmesege = countmesege)


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

def gen():
    yield b'--frame\r\n'
    RTSP_URL = 'rtsp://admin:Huawei@123@161.82.233.189/LiveMedia/ch1/Media1'
    cap = VideoCapture(RTSP_URL)
    # cap = Camera(RTSP_URL)
    while True:
        frame = cap.read()
        frameresize=cv2.resize(frame,(640, 480))
        # frameresize=cv2.resize(frame,(640, 480),fx = 0, fy = 0,interpolation = cv2.INTER_NEAREST)
        frameWeb = cv2.imencode('.jpg', frameresize)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frameWeb + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0',port=80,debug=True, use_reloader=False)

