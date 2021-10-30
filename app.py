from flask import Flask, render_template, request, redirect, url_for
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = "A super long secret key no one is supposed to know"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
scheduler = APScheduler()

db = SQLAlchemy(app)


class Meeting(db.Model):
    class_name = db.Column(db.String(50))
    class_link = db.Column(db.String(50))
    class_time = db.Column(db.DateTime, primary_key=True)
    started = db.Column(db.Boolean, default=False)
    finished = db.Column(db.Boolean, default=False)


def get_meeting_list():
    meeting_list = []
    for meeting in Meeting.query.all():
        meeting_list.append(
            {
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


def start_recording(meeting):
    # meeting.class_name
    # meeting.class_time
    # meeting.class_link
    print(
        f"Starting the recording of {meeting.class_name} at {meeting.class_time}")


def checker():
    for meeting in Meeting.query.all():
        if datetime.now() > meeting.class_time and not meeting.started:
            start_recording(meeting)
            meeting.started = True
            db.session.commit()


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html", meeting_list=get_meeting_list())


@app.route('/add_meeting', methods=['POST'])
def add_meeting():
    class_name = request.form.get('class_name')
    class_link = request.form.get('class_link')
    class_time = request.form.get('class_time')
    class_time = datetime.strptime(class_time, "%Y-%m-%dT%H:%M")
    meeting = Meeting(class_name=class_name,
                      class_link=class_link, class_time=class_time)
    db.session.add(meeting)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete_meeting', methods=['POST'])
def delete_meeting():
    class_time = request.form.get("meeting_time")
    class_time = datetime.strptime(class_time, "%Y-%m-%d %H:%M:%S")
    meeting = Meeting.query.filter_by(class_time=class_time).first()
    db.session.delete(meeting)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    db.create_all()
    scheduler.add_job(id="check_time", func=checker,
                      trigger="interval", seconds=5)
    scheduler.start()
    app.run(debug=True, port=5006)
