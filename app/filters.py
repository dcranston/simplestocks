from app import app
from dateutil import parser
from datetime import datetime
import pytz
import humanize


# ----------------------------
# -- Jinja Filters
# ----------------------------
@app.template_filter('humanize')
def _jinja2_filter_datetime(date, fmt=None):
    eastern = pytz.timezone("US/Eastern")
    date = parser.parse(date)
    date = eastern.localize(date)

    utc = pytz.timezone("UTC")
    now = datetime.utcnow()
    now = utc.localize(now)
    return humanize.naturaltime(now - date)


@app.template_filter('ctime')
def _jinja2_filter_datetime(date, fmt=None):
    date = parser.parse(date)
    return date.ctime()


@app.template_filter('shorttime')
def _jinja2_filter_datetime(date, fmt=None):
    date = parser.parse(date)
    native = date.replace(tzinfo=pytz.UTC)
    return native.astimezone(pytz.timezone("America/Toronto")).strftime("%Y-%m-%d %H:%M")


@app.template_filter('currency')
def _jinja2_filter_currency(value):
    value = float(value)
    return "${:,.2f}".format(value)


@app.template_filter('currency_delta')
def _jinja2_filter_currency(value):
    value = float(value)
    dec_value = "${:,.2f}".format(abs(value))
    if value == 0:
        return dec_value
    elif value <= 0:
        return "-" + dec_value
    else:
        return "+" + dec_value
