from django.http import Http404
from django.shortcuts import render

import datetime

from .forms import FindVacancyFrom
from .models import Vacancy, City, Speciality


def index(request):
    form = FindVacancyFrom
    return render(request, 'scrapping/home.html', {'form': form})


def vacancy_list(request):
    today = datetime.datetime.today()
    form = FindVacancyFrom

    if request.GET:

        try:
            city_id = int(request.GET.get('city'))
            speciality_id = int(request.GET.get('speciality'))
        except ValueError:
            raise Http404('Page not found')

        context = {}
        context['form'] = form
        qs = Vacancy.objects.filter(city=city_id, speciality=speciality_id)

        if qs:
            context['jobs'] = qs
            context['city'] = qs[0].city.name
            context['speciality'] = qs[0].speciality.name
            return render(request, 'scrapping/list.html', context)

    return render(request, 'scrapping/list.html', {'form': form})
