from django.shortcuts import render

import datetime

from scraping.models import Speciality, City, Vacancy, Url, Site
from scraping.utils import Parser


def list_v(request):
    today = datetime.datetime.today()
    city = City.objects.get(name='Томск')
    speciality = Speciality.objects.get(name='Python')
    qs = Vacancy.objects.filter(city=city.id, speciality=speciality.id, timestamp=today)

    if qs:
        return render(request, 'scrapping/list.html', {'jobs': qs})

    return render(request, 'scrapping/list.html')


def home(request):
    city = City.objects.get(name='Томск')
    speciality = Speciality.objects.get(name='Python')
    url_qs = Url.objects.filter(city=city, speciality=speciality)
    site = Site.objects.all()
    url_hh = url_qs.get(site=site.get(name='hh.ru')).url_address
    parser = Parser()
    parser.get_urls(url_hh)
    jobs = list()
    jobs.extend(parser.parse())
    vacancy = Vacancy.objects.filter(city=city.id, speciality=speciality.id).values('url')
    url_list = [url['url'] for url in vacancy]

    for job in jobs:

        if job['link'] not in url_list:
            v = Vacancy(city=city, speciality=speciality, url=job['link'], title=job['title'],
                        description=job['context'], company=job['company'])
            v.save()

    return render(request, 'scrapping/list.html', {'jobs': jobs})

