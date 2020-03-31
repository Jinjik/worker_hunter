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
)
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
SUBJECT = f'Список вакансий за {today}'
template = '<!doctype html><html lang="en"><head><meta charset="utf-8"></head><body>'
end = '</body></html>'

try:
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, host=DB_HOST, password=DB_PASSWORD)
except ConnectionError:
    log.exception(f'Unable to open DB')
else:
    log.info('Connect success!')
    cur = conn.cursor()
    cur.execute(f'SELECT city_id, speciality_id FROM subscribers_subscriber WHERE is_active={True};')
    cities_qs = cur.fetchall()

    for pair in cities_qs:
        content = ''
        city = pair[0]
        speciality = pair[1]
        cur.execute(
            f"""SELECT email FROM subscribers_subscriber 
                WHERE is_active={True} AND city_id={city} AND speciality_id={speciality};
            """
        )
        email_qs = cur.fetchall()
        emails = [i[0] for i in email_qs]
        cur.execute(f"""
                    SELECT url, title, context, company FROM scraping_vacancy 
                    WHERE city_id='{city}' AND speciality_id='{speciality}' AND timestamp='{today}';
                    """
        )
        jobs_qs = cur.fetchall()

        if jobs_qs:
            for job in jobs_qs:
                content += f'<a href="{job[0]}" target="_blank>{job[1]}</a><br/><p>{job[2]}</p><p>{job[3]}</p><br/>'
                content += f'<hr/><br/><br/>'

            html_m = f'{template}{content}{end}'

            for email in emails:
                requests.post(API, auth=("api", MAILGUN_KEY),
                    data={
                        "from": FROM_EMAIL,
                          "to": email,
                          "subject": SUBJECT,
                          "html": html_m
                    }
                )
        else:
            for email in emails:
                requests.post(API, auth=("api", MAILGUN_KEY),
                    data={
                        "from": FROM_EMAIL,
                        "to": email,
                        "subject": SUBJECT,
                        "text": 'Список вакансий по вашему профилю на сегодня пуст'
                    }
                )

        conn.commit()
        cur.close()
        conn.close()
