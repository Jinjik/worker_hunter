from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages

from .forms import SubscriberModelForm


class SubscriberCreate(CreateView):
    model = SubscriberModelForm
    form_class = SubscriberModelForm
    template_name = 'subscribers/create.html'
    success_url = reverse_lazy('create')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            messages.success(request, 'Данные успешно сохранены!')
            return self.form_valid(form)
        else:
            messages.error(request, 'Проверьте правильность данных')
            return self.form_invalid(form)

    # def
