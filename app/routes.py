from app import app, db, helpers
from app.models import Quote, Stock
from sqlalchemy import exc
from flask import render_template, request, redirect, url_for, make_response, Markup, jsonify, flash
from dateutil import parser
import pytz
import time
import sys
import json


@app.route('/')
def index():
    start = time.time()
    portfolios = {}
    stocks = list()
    try:
        data = helpers.ws_get_positions()
    except:
        app.logger.debug("Unexpected error: {}".format(sys.exc_info()))
        return redirect(url_for('login') + "?return_to=" + request.url)
    for key, entry in data.items():
        try:
            stock = Stock(entry)
            current = helpers.get_current_quote(key)
            stock.set_quote(float(current["value"]))
            stock.quote_timestamp = current["timestamp"]
            stocks.append(stock.to_dict())
            # total_value += stock.total_value
        except:
            flash(f"There was an error processing: {key}", "error")
            app.logger.debug("There was an error processing an entry: ", exc_info=True)
            app.logger.debug(entry)
    stock = None
    for stock in stocks:
        if stock['portfolio'] not in portfolios.keys():
            portfolios.update({stock['portfolio']: {"total_value": 0}})
        portfolios[stock['portfolio']]["total_value"] = stock['total_value']

    # portfolios = sorted(portfolios, reverse=True)
    app.logger.debug(json.dumps(portfolios))
    debug = False
    if request.args.get('debug'):
        debug = True
    dump = False
    if request.args.get('dump') and debug:
        return jsonify(data)
    end = time.time()
    return render_template('index.html', portfolios=portfolios, stocks=stocks,
                           timing=(end-start), debug=debug, now=time.ctime())


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
        try:
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
        except KeyError:
            app.logger.debug("There was an error updating...\n", exc_info=True)
            return make_response(jsonify(entry), 500)
    end = time.time()
    resp = make_response('', 200)
    resp.headers['X-Time-Elapsed'] = end-start
    return resp
