from flask import Flask, render_template, request, redirect, url_for
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from JoinMeet import JoinMeet
from threading import Thread
from SendMessage import SendMessage
from autotrans import download
import time
import os

messages = SendMessage()


app = Flask(__name__)
app.config['SECRET_KEY'] = "A super long secret key no one is supposed to know"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
scheduler = APScheduler()

db = SQLAlchemy(app)
PROCESSING = []


class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50))
    class_link = db.Column(db.String(50))
    class_time = db.Column(db.DateTime)
    recording_time = db.Column(db.DateTime)
    started = db.Column(db.Boolean, default=False)
    finished = db.Column(db.Boolean, default=False)


class User(db.Model):
    email = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(50))


class TranscribedVideo(db.Model):
    name = db.Column(db.String(100))
    file_name = db.Column(db.String(100), primary_key=True)


def get_meeting_list(finished=False):
    meeting_list = []
    for meeting in Meeting.query.all():
        if meeting.finished == finished:
            meeting_list.append(
                {
                    'id': meeting.id,
                    'class_name': meeting.class_name,
                    'class_link': meeting.class_link,
                    'class_time': meeting.class_time,
                    'started': meeting.started,
                    'finished': meeting.finished
                }
            )
    # Sort the list on the basis of the meeting times
    meeting_list = sorted(meeting_list, key=lambda x: x['class_time'])
    return meeting_list


MEETINGS = []


def start_recording(meeting):
    print("Starting recording")
    user = User.query.first()
    MEETINGS.append(JoinMeet(user.email, user.password))
    MEETINGS[-1].join_meet(meeting.class_link, meeting.id)
    MEETINGS[-1].record_meeting()


def checker():
    # print("Checking Right Now")
    for meeting in Meeting.query.all():
        if datetime.now() > meeting.class_time and not meeting.started:
            start_recording(meeting)
            meeting.started = True
            db.session.commit()


@app.route("/", methods=["GET", "POST"])
def home():
    videos = TranscribedVideo.query.all()
    video_list = []
    for video in videos:
        data = ""
        with open(video.file_name.replace("mp4", "txt")) as f:
            data = f.read()
        video_list.append(
            {
                'video_name': video.name,
                'video_file_name': video.file_name.replace("mp4", "txt"),
                'video_file_text': data
            }
        )
    return render_template("index.html", meeting_list=get_meeting_list(), finished_meetings=get_meeting_list(True), video_list=video_list, PROCESSING=PROCESSING)


@app.route('/add_meeting', methods=['POST'])
def add_meeting():
    class_name = request.form.get('class_name')
    class_link = request.form.get('class_link')
    class_time = request.form.get('class_time')
    class_time = datetime.strptime(class_time, "%Y-%m-%dT%H:%M")
    _id = len(Meeting.query.all())
    meeting = Meeting(id=_id+1, class_name=class_name,
                      class_link=class_link, class_time=class_time)
    db.session.add(meeting)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete_meeting', methods=['POST'])
def delete_meeting():
    class_id = request.form.get("meeting_id")
    meeting = Meeting.query.filter_by(id=class_id).first()
    db.session.delete(meeting)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/transcribe')
def transcribe():

    videos = TranscribedVideo.query.all()

    video_list = []
    for video in videos:
        data = ""
        with open(video.file_name.replace("mp4", "txt")) as f:
            data = f.read()
        video_list.append(
            {
                'video_name': video.name,
                'video_file_name': video.file_name.replace("mp4", "txt"),
                'video_file_text': data
            }
        )

    return render_template("transcribe.html", video_list=video_list, PROCESSING=PROCESSING)


@app.route('/transcribe_video', methods=["POST"])
def transcribe_video():
    def process_video(name, video_file_name):
        PROCESSING.append(video_file_name)
        messages.send_message(
            "The processing for your video has been started.")
        print("Starting processing! ")
        from Transcribe import Transcribe
        transcribed_text = Transcribe(video_file_name)
        with open(video_file_name.replace("mp4", "txt"), "w+") as f:
            f.write(transcribed_text)
        video = TranscribedVideo(name=name, file_name=video_file_name)
        db.session.add(video)
        db.session.commit()
        messages.send_message("Your video has succesfully been processed.")
        PROCESSING.pop()
        os.remove(video_file_name)
        return
    
    meeting_id = request.form.get('meeting_id')
    meet = Meeting.query.filter_by(id=meeting_id).first()
    name = meet.class_name 
    recording_time = meet.recording_time
    user = User.query.first()
    obj = download(user.email, user.password, meet.recording_time.strftime("%H:%M"), "mwx-wbnz-bnp", meet.recording_time.strftime("%Y-%m-%d"))
    obj.google_login()
    obj.downloadfile()
    filename = meet.recording_time.strftime("mwx-wbnz-bnp (%Y-%m-%d at %H_%M GMT-7).mp4")
    db.session.delete(meet)
    db.session.commit()
    thread = Thread(target=process_video, kwargs={
                    'video_file_name': filename, 'name': name})
    thread.start()
    return redirect(url_for('home'))

@app.route('/view_file/<filename>')
def view_file(filename):
    with open(filename) as f:
        return f.read()

if __name__ == "__main__":
    from StoreCred import store_password
    store_password()
    db.create_all()
    # scheduler.add_job(id="check_time", func=checker,
    #                   trigger="interval", seconds=5)
    # scheduler.start()
    port = 5045+1+1+1+1+1+1+1+1+1+1
    app.run(debug=True, port=port, use_reloader=True)
