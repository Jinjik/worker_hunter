import logging
import datetime

import psycopg2
import requests

from workhunter.secret import (
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_USER,
    MAIL,
    MAILGUN_KEY,
    API,
    ADMIN)
from scraping.utils import Parser

log = logging.getLogger(__name__)
console = logging.StreamHandler()
logger_format = '%(asctime)s\t%(levelname)s - %(message)s'
console.setFormatter(logging.Formatter(logger_format))
log.addHandler(console)
log.setLevel(logging.INFO)
fh = logging.FileHandler('../../logs.log', mode='a')
log.addHandler(fh)
fh.setLevel(logging.INFO)
fh.setFormatter(logging.Formatter(logger_format))

parser = Parser()
today = datetime.datetime.today()
ten_days_ago = datetime.date.today() - datetime.timedelta(10)
FROM_EMAIL = 'noreply@workhunter.heroku.com'
SUBJECT = f'Недостающие урлы {today}'

try:
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, host=DB_HOST, password=DB_PASSWORD)
except ConnectionError:
    log.exception(f'Unable to open DB')
else:
    log.info('Connect success!')
    cur = conn.cursor()
    cur.execute(f'SELECT city_id, speciality_id FROM subscribers_subscriber WHERE is_active={True};')
    qs = cur.fetchall()
    cur.execute(f'SELECT * FROM scraping_city;')
    cities_qs = cur.fetchall()
    cities = {i[0]: i[1] for i in cities_qs}
    cur.execute(f'SELECT * FROM scraping_speciality;')
    sp_qs = cur.fetchall()
    sp = {i[0]: i[1] for i in sp_qs}
    mis_urls = list()
    cnt = f'На дату {today} отсутствуют урлы для следующих пар'
    for pair in qs:
        cur.execute(f'SELECT * FROM scraping_url WHERE city_id={pair[0]} AND speciality_id={pair[1]};')
        qs = cur.fetchall()

        if not qs:
            mis_urls.append({cities[pair[0]],sp[pair[1]]})

        if mis_urls:

            for pair in mis_urls:
                cnt += f'город - {pair[0]} специальность - {pair[1]}'

            requests.post(API, auth=("api", MAILGUN_KEY),
                data={
                    "from": FROM_EMAIL,
                    "to": ADMIN,
                    "subject": SUBJECT,
                    "text": cnt
                }
            )
    conn.commit()
    cur.close()
    conn.close()
