from django.shortcuts import render
from ..scraping.utils import Parser

def home(request):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'accept': '*/*',
    }
    base_url = 'https://hh.ru/search/vacancy?L_is_autosearch=false&area=113&clusters=true&enable_snippets=true&text=Python&page=0'

    parser = Parser(headers, base_url)
    parser.get_urls()
    jobs = parser.parse()
    return render(request, 'base.html')