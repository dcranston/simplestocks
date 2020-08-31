from app import app, db, helpers
from app.models import Quote, Stock
from sqlalchemy import exc
from flask import render_template, request, redirect, url_for, make_response, Markup
from dateutil import parser
import pytz
import time
import sys


@app.route('/')
def index():
    start = time.time()
    total_value = 0.0
    stocks = list()
    try:
        data = helpers.ws_get_positions()
    except:
        app.logger.debug("Unexpected error: {}".format(sys.exc_info()))
        return redirect(url_for('login') + "?return_to=" + request.url)
    for key, entry in data.items():
        stock = Stock(entry)
        current = helpers.get_current_quote(key)
        stock.set_quote(float(current["value"]))
        stock.quote_timestamp = current["timestamp"]
        stocks.append(stock.to_dict())
        total_value += stock.total_value

    end = time.time()
    return render_template('index.html', data=data, stocks=stocks, total_value=total_value,
                           timing=(end-start), now=time.ctime())


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


@app.route('/update', methods=['GET'])
def update():
    start = time.time()
    data = None
    try:
        data = helpers.ws_get_positions()
    except:
        app.logger.debug("Unexpected error: {}".format(sys.exc_info()))
        resp = make_response(Markup(), 500)
        return resp
    for key, entry in data.items():
        for line in entry['sparkline']:
            timestamp = parser.parse(line['date'] + " " + line['time'])
            timestamp = timestamp.replace(tzinfo=pytz.timezone("US/Eastern"))
            q = Quote(symbol=key,
                      value=line['close'],
                      timestamp=timestamp
                      )
            db.session.add(q)
            try:
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
    end = time.time()
    resp = make_response('', 200)
    resp.headers['X-Time-Elapsed'] = end-start
    return resp
