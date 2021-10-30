from flask import Flask, render_template, request, redirect
from flask_apscheduler import APScheduler
import time 
import threading


app = Flask(__name__)
app.config['SECRET_KEY'] = "A super long secret key no one is supposed to know"
scheduler = APScheduler()


meeting_list = []


def checker():
    print(time.time())

    
@app.route("/", methods=["GET", "POST"])
def home():
    
    if request.method == "POST":
        class_name = request.form.get("class_name")
        class_time = request.form.get("class_time")
        class_link = request.form.get("class_link")
        meeting_list.append(
            {
                'class_name': class_name,
                'class_link': class_link,
                'class_time': class_time,
            }
        )
    return render_template("index.html", meeting_list=meeting_list)

if __name__ == "__main__":
    scheduler.add_job(id="check_time", func=checker, trigger="interval", seconds=5)
    scheduler.start()
    app.run(debug=True, port=5003)
    