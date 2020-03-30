import logging
import datetime

import psycopg2

from workhunter.secret import (
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_USER
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

try:
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, host=DB_HOST, password=DB_PASSWORD)
except ConnectionError:
    log.exception(f'Unable to open DB')
else:
    log.info('Connect success!')
    cur = conn.cursor()
    cur.execute(f'SELECT city_id, speciality_id FROM subscribers_subscriber WHERE is_active={True};')
    cities_qs = cur.fetchall()

    todo_list = {i[0]: set() for i in cities_qs}

    for i in cities_qs:
        todo_list[i[0]].add(i[1])

    cur.execute('SELECT * FROM scraping_site;')
    sites_qs = cur.fetchall()
    sites = {i[0]: i[1] for i in sites_qs}
    url_list = list()

    for city in todo_list:

        for sp in todo_list[city]:
            tmp = {}
            cur.execute(f'SELECT site_id, url_address FROM scraping_url WHERE city_id={city} AND speciality_id={sp};')
            qs = cur.fetchall()

            if qs:
                tmp['city'] = city
                tmp['speciality'] = sp

                for item in qs:
                    site_id = item[0]
                    tmp[sites[site_id]] = item[1]

                url_list.append(tmp)

    all_data = list()

    if url_list:

        for url in url_list:
            tmp = {}
            tmp_content = list()
            parser.get_urls(url['hh.ru'])
            tmp_content.extend(parser.parse())
            tmp['city'] = url['city']
            tmp['speciality'] = url['speciality']
            tmp['content'] = tmp_content
            all_data.append(tmp)

    log.info('get data')

    if all_data:

        for data in all_data:
            for job in data['content']:
                cur.execute(f"""SELECT * FROM scraping_vacancy WHERE url='{job["link"]}';""")
                qs = cur.fetchone()

                if not qs:
                    cur.execute(
                        """INSERT INTO scraping_vacancy (city_id, speciality_id, title, url, description, company, 
                            timestamp ) VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """, (data['city'], data['speciality'], job['title'], job['link'], job['context'],
                              job['company'], today)
                    )

    cur.execute("""DELETE FROM scraping_vacancy WHERE timestamp<=%s;""", (ten_days_ago, ))

    conn.commit()
    cur.close()
    conn.close()
