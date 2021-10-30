from flask import Flask, render_template, request, redirect, url_for
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time 
import threading


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


def checker():
    print(time.time())


@app.route("/", methods=["GET", "POST"])
def home():
    meeting_list = []
    for meeting in Meeting.query.all():
        meeting_list.append(
            {
                'class_name': meeting.class_name,
                'class_link': meeting.class_link,
                'class_time': meeting.class_time
            }
        )
    return render_template("index.html", meeting_list=meeting_list)


@app.route('/add_meeting', methods=['POST'])
def add_meeting():
    class_name = request.form.get('class_name')
    class_link = request.form.get('class_link')
    class_time = request.form.get('class_time')
    class_time = datetime.strptime(class_time, "%Y-%m-%dT%H:%M")
    meeting = Meeting(class_name=class_name, class_link=class_link, class_time=class_time)
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
    scheduler.add_job(id="check_time", func=checker, trigger="interval", seconds=5)
    scheduler.start()
    app.run(debug=True, port=5005)
    