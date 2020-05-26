import requests
import logging
import configparser
from collections import namedtuple

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

config = configparser.ConfigParser()
config_file = config.read("config.ini")[0]

login_url = config["URL"]["login"]
refresh_url = config["URL"]["refresh_token"]


def read_config():
    global config, config_file
    Creds = namedtuple("Creds", ["email", "password", "otp", "token"])
    creds = Creds(email=config['Credentials']["email"],
                  password=config['Credentials']["password"],
                  otp=config['Credentials']["otp"],
                  token=config['Credentials']["token"]
                  )
    return creds


def write_config():
    global config, config_file
    with open(config_file, 'w') as cf:
        config.write(cf)


def ws_login(email, password, otp):
    global config
    data = {"email": email,
            "password": password,
            "otp": otp
            }
    response = requests.post(login_url, data=data)
    if response.status_code > 299:
        logging.debug(["Error fetching token", response.status_code, response.text])
        raise Exception(response.status_code, response.text)
    else:
        token = response.headers["X-Access-Token"]
        logging.info("login successful, token received: {}".format(token))
        config["Credentials"]["token"] = token
        write_config()
        return token


def ws_refresh_token(token):
    data = {"refresh_token": token}
    response = requests.post(refresh_url, data=data)
    if response.status_code == 200:
        logging.info("access token refreshed")
        return True
    else:
        logging.debug(["Error refreshing token", response.status_code, response.text])
        raise Exception(response.status_code, response.text)


# ------------------------------
creds = read_config()
access_token = (creds.token if creds.token != '' else None)
if not access_token:
    logging.debug("access token NOT present")
    if creds.otp == '':
        logging.error("otp is required but blank")
        exit(1)
    logging.debug("logging in to fetch token...")
    access_token = ws_login(email=creds.email,
                            password=creds.password,
                            otp=creds.otp)
else:
    logging.debug("access token present")
    try:
        logging.debug("refreshing access token...")
        # ws_refresh_token(access_token)
    except:
        logging.debug("error refreshing token; logging in to fetch new token...")
        if creds.otp == '':
            logging.error("otp is required but blank")
            exit(1)
        access_token = ws_login(email=creds.email,
                                password=creds.password,
                                otp=creds.otp)

headers = {"Authorization": access_token}
position_url = config["URL"]["positions"]
response = requests.get(url=position_url, headers=headers)

# parse the positions response
stocks = dict()
for item in response.json()["results"]:
    stocks.update({item["stock"]["symbol"]: item})

print(stocks)
exit(0)
