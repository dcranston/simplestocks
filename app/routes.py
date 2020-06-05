from app import app, db, helpers
from app.models import Quote
from sqlalchemy import exc
from flask import render_template, request, redirect, url_for
from dateutil import parser
import pytz
import time


@app.route('/')
def index():
    start = time.time()
    try:
        data = helpers.ws_get_positions()
    except:
        return redirect(url_for('login') + "?return_to=" + request.url)
    for key, entry in data.items():
        for line in entry['sparkline']:
            timestamp = parser.parse(line['date']+" "+line['time'])
            timestamp = timestamp.replace(tzinfo=pytz.UTC)
            q = Quote(symbol=key,
                      value=line['close'],
                      timestamp=timestamp
                      )
            db.session.add(q)
            try:
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
        current = helpers.get_current_quote(key)
    end = time.time()
    return render_template('index.html', data=data, timing=(end-start), now=time.ctime())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html', redir_url=request.args.get('return_to'))
    else:
        otp = request.form['otp']
        redir_url = request.form['redir_url']
        helpers.update_config("Credentials", "otp", otp)
        helpers.update_config("Credentials", "token", '')
        if redir_url and not redir_url == "None":
            return redirect(redir_url)
        else:
            return redirect(url_for('index'))
