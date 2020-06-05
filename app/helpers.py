import json
import sys
import logging
from collections import namedtuple
import requests
from app import config, config_file
from app.models import Quote

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

login_url = config["URL"]["login"]
refresh_url = config["URL"]["refresh_token"]


def read_config():
    global config, config_file
    config_file = config.read("config.ini")[0]
    Creds = namedtuple("Creds", ["email", "password", "otp", "token", "refresh_token"])
    creds = Creds(email=config['Credentials']["email"],
                  password=config['Credentials']["password"],
                  otp=config['Credentials']["otp"],
                  token=config['Credentials']["token"],
                  refresh_token=config['Credentials']["refresh_token"]
                  )
    return creds


def write_config():
    global config, config_file
    with open(config_file, 'w') as cf:
        config.write(cf)


def update_config(section, key, value):
    global config, config_file
    config[section][key] = value
    write_config()


def ws_login(email, password, otp):
    global config
    data = {"email": email,
            "password": password,
            "otp": otp
            }
    response = requests.post(login_url, data=data)
    update_config("Credentials", "otp", '')  # expire the otp immediately
    if response.status_code > 299:
        logging.debug(["Error fetching token", response.status_code, response.text])
        update_config("Credentials", "otp", '')
        raise Exception(response.status_code, response.text)
    else:
        token = response.headers["X-Access-Token"]
        refresh_token = response.headers["X-Refresh-Token"]
        logging.info("login successful, token received: {}".format(token))
        update_config("Credentials", "token", token)
        update_config("Credentials", "refresh_token", refresh_token)
        return token


def ws_refresh_token(token):
    data = {"refresh_token": token}
    response = requests.post(refresh_url, data=data)
    if response.status_code == 200:
        token = response.headers["X-Access-Token"]
        refresh_token = response.headers["X-Refresh-Token"]
        update_config("Credentials", "token", token)
        update_config("Credentials", "refresh_token", refresh_token)
        logging.info("access token refreshed")
        return token
    else:
        logging.debug(["Error refreshing token", response.status_code, response.text])
        raise Exception(response.status_code, response.text)


def ws_get_positions():
    creds = read_config()
    if not creds.token:
        logging.debug("access token NOT present")
        if creds.otp == '':
            logging.error("otp is required but blank")
            update_config("Credentials", "token", '')
            update_config("Credentials", "refresh_token", '')
            raise Exception("otp is required but blank")
        logging.debug("logging in to fetch token...")
        creds.token = ws_login(email=creds.email,
                                password=creds.password,
                                otp=creds.otp)
    else:
        logging.debug("access token present")
        try:
            logging.debug("refreshing access token...")
            ws_refresh_token(creds.refresh_token)
            creds = read_config()
        except:
            logging.debug("Unexpected error: {}".format(sys.exc_info()))
            logging.debug("error refreshing token; logging in to fetch new token...")
            if creds.otp == '':
                logging.error("otp is required but blank")
                update_config("Credentials", "token", '')
                update_config("Credentials", "refresh_token", '')
                raise Exception("otp is required but blank")
            creds.token = ws_login(email=creds.email,
                                    password=creds.password,
                                    otp=creds.otp)

    headers = {"Authorization": creds.token}
    position_url = config["URL"]["positions"]
    response = requests.get(url=position_url, headers=headers)
    with open("debug.json", "w") as debug_output:
        debug_output.write(json.dumps(response.json(), indent=4))
    # parse the positions response
    stocks = dict()
    for item in response.json()["results"]:
        stocks.update({item["stock"]["symbol"]: item})

    return stocks


def get_current_quote(symbol):
    quote = Quote.query.filter_by(symbol=symbol).order_by(Quote.timestamp.desc()).first()
    logging.debug(quote.to_json())