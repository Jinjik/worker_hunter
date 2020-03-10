import requests
from bs4 import BeautifulSoup as bs


class Parser:
    def __init__(self, headers, base_url):
        self.headers = headers
        self.base_url = base_url
        self.urls = []
        self.jobs = []

    def get_urls(self):
        self.urls.append(self.base_url)
        session = requests.Session()
        request = session.get(url=self.base_url, headers=self.headers)

        try:
            soup = bs(request.content, 'html.parser')
            pagination = soup.find_all('a', attrs={'data-qa': 'pager-page'})
            if pagination:
                count = int(pagination[-1].text)
            else:
                count = 0
            for i in range(count):
                url = f'https://tomsk.hh.ru/search/vacancy?L_is_autosearch=false&area=90&clusters=true&enable_snippets=true&text=Python&page={i}'
                if url not in self.urls:
                    self.urls.append(url)
        except ConnectionError as exc:
            print(exc)

    def parse(self):
        for url in self.urls:
            session = requests.Session()
            request = session.get(url=url, headers=self.headers)
            soup = bs(request.content, 'html.parser')
            divs = soup.find_all('div', attrs={'data-qa': 'vacancy-serp__vacancy'})

            for div in divs:
                try:
                    title = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).text
                    href = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
                    company = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
                    text1 = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}).text
                    text2 = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_requirement'}).text
                    context = f'{text1} {text2}'
                except AttributeError as exc:
                    print(exc)
                else:
                    self.jobs.append({
                        'title': title,
                        'link': href,
                        'company': company,
                        'context': context
                    })

        return self.jobs


def main():

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'accept': '*/*',
    }
    base_url = 'https://tomsk.hh.ru/search/vacancy?L_is_autosearch=false&area=90&clusters=true&enable_snippets=true&text=Python&page=0'

    parser = Parser(headers, base_url)
    parser.get_urls()
    jobs = parser.parse()

    for job in jobs:
        print(job['title'])
        print(job['link'])
        print(job['company'])
        print(job['context'])
        print('-----------------\n')


if __name__ == '__main__':
    main()
