from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_apscheduler import APScheduler
from flask_login import LoginManager
import logging as log
from flask_bcrypt import Bcrypt

# configure database
class Config:
    SCHEDULER_API_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///databass.db'
    
    # Logging config
    log.basicConfig(level=log.DEBUG)

# Initialise app and scheduler
app = Flask(__name__)
app.config.from_object(Config())

sched = APScheduler()


with app.app_context():
    db = SQLAlchemy(app)
    bcrypt = Bcrypt(app)

class links(db.Model):
    # create the links table within the db
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(200), nullable = False)
    url = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    schedule_datetime = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Link %r>' % self.id
    

@app.route('/', methods=['POST','GET'])
def index():
    # function relating to index.html, you can view links or on this page
    print(datetime.now())
    links_active = links.query.filter(links.schedule_datetime <= datetime.now())
    '''if request.method == 'POST':
        return redirect("/admin")
    else:'''
    return render_template("index.html", links=links_active)

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    # admin.html functionality where you can add new links. 
    links_all = links.query.all()
    if request.method == 'POST':
        link_label = request.form['label']
        link_url = request.form['url'] 
        link_schedule = dates_processor(request.form['schedule_datetime'])

        new_link = links(label=link_label, url=link_url, schedule_datetime=link_schedule)

        try:
            db.session.add(new_link)
            db.session.commit()
            return redirect('/admin')
        except:
            return 'There was an issue adding your link.'
        
    else:
        links_all = links.query.all()
        return render_template('admin.html', links=links_all)


@app.route('/delete/<int:id>')
def delete(id):
    # a function to delete existing links from website / db when on admin.html
    link_to_delete = links.query.get_or_404(id)

    try:
        db.session.delete(link_to_delete)
        db.session.commit()
        return redirect('/admin')
    except:
        return "There was a problem deleting that link."
    

@app.route('/modify/<int:id>', methods=['POST', 'GET'])
def modify(id):
    # A function to modify existing links on the db / website from admin.html to modify.html
    link_to_modify = links.query.get_or_404(id)
    if request.method == 'POST':
        link_to_modify.label = request.form['label']
        link_to_modify.url = request.form['url']
        link_to_modify.schedule_datetime = dates_processor(request.form['schedule_datetime'])
        try:
            db.session.commit()
            return redirect('/admin')
        except:
            return 'There was an issue updating your link.'
    else:
        return render_template('modify.html',links=link_to_modify)
    
@app.route('/login_accnt', methods=['POST', 'GET'])
def login_accnt():
    return render_template('login.html')

def dates_processor(input_datetime):
    # A function to process dates so they are in the right format to be added to the database
    if input_datetime == '':
        output_datetime = str(datetime.now())
        output_datetime = output_datetime[:-10]
    else:
        output_datetime = input_datetime.replace('T', ' ')
    output_datetime = datetime.strptime(output_datetime, '%Y-%m-%d %H:%M')
    return output_datetime


if __name__ == "__main__":
    app.run()

