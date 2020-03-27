import logging

import psycopg2

from workhunter.secret import (
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_USER
)

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

try:
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, host=DB_HOST, password=DB_PASSWORD)
except ConnectionError:
    log.exception(f'Unable to open DB')
else:
    log.info('Connect success!')
    cur = conn.cursor()
    cur.execute(f'SELECT city_id, speciality_id FROM subscribers_subscriber WHERE is_active={True};')
    cities_qs = cur.fetchall()
    print(cities_qs)

    conn.commit()
    cur.close()
    conn.close()
