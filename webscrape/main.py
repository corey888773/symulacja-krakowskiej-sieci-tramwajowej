from bs4 import BeautifulSoup
import json, os, re, httpx, urllib.request, urllib.parse
from html_table_parser import HTMLTableParser

strona = 'http://rozklady.mpk.krakow.pl'

def main():
    if not os.path.exists('./pages'):
        os.makedirs('./pages')

    try:
        mainBody = getQuote('http://rozklady.mpk.krakow.pl/?lang=PL&akcja=index&rozklad=20200323')
        soup = BeautifulSoup(mainBody, 'html.parser')
        rozklad = {'lines': []}

        numeryLinii = []
        linkiLinii = []

        for el in soup.select('.linia_table_left a'):
            text = el.text
            link = el['href']
            text = text.replace(' ', '').replace('\t', '').replace('\n', '')

            # print(el)

            if text[0].isdigit() and int(text) < 53:
                numeryLinii.append(text)
                linkiLinii.append(link)

        # print(linkiLinii)

        for i in range(len(linkiLinii)):
            link = linkiLinii[i]
            numer = numeryLinii[i]
            body = getQuote(strona + link)
            print(strona + link)
            linia = BeautifulSoup(body, 'html.parser')

            linkiKierunkow = []
            nazwyKierunkow = []

            i = 0   
            for el in linia.select('td table tr td table tr td table tr TD a'):
                linkiKierunkow.append(el['href'])
                text = el.text.replace(' ', '').replace('\t', '').replace('\n', '')
                nazwyKierunkow.append(text)
                
            kierunek1 = przetworzKierunek(strona + linkiKierunkow[0], nazwyKierunkow[0])
            print(strona + linkiKierunkow[1])
            kierunek2 = przetworzKierunek(strona + linkiKierunkow[1], nazwyKierunkow[1])

            linia = {
                'number': numer,
                'direction1': kierunek1,
                'direction2': kierunek2
            }

            rozklad['lines'].append(linia)

        with open('./schedule.json', 'w', encoding='utf-8') as f:
            json.dump(rozklad, f,  ensure_ascii=False, indent=True)
        print("Koniec")
    except Exception as e:
        print(e)

def przetworzKierunek(link, nazwa):
    try:
        body = getQuote(link)
        linia = BeautifulSoup(body, 'html.parser')

        linkiPrzystankow = []
        for el in linia.select('a span'):
            linkiPrzystankow.append(el.parent['href'])

        kierunek = {
            'name': nazwa,
            'stops': []
        }

        for linkPrzystanku in linkiPrzystankow:
            bodyPrzystanku = getQuote(strona + linkPrzystanku)
            przystanek = BeautifulSoup(bodyPrzystanku, 'html.parser')

            nazwaPrzystanku = przystanek.select('div span')[0].text

            rozkladPrzystanku = przystanek.select('tr td table')[14]

            tabelaHtml = str(rozkladPrzystanku)
            parsedTable = parseTable(tabelaHtml)

            przystanek = {
                'name': nazwaPrzystanku,
                'schedule': parsedTable
            }

            kierunek['stops'].append(przystanek)

        return kierunek
    except Exception as e:
        print(e)
        return e

def parseTable(table : str):
    p = HTMLTableParser()
    p.feed(table)
    return p.tables

def getQuote(url):
    headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': 'ROZKLADY_AB=0; ROZKLADY_JEZYK=PL; ROZKLADY_OSTATNIA=1698344828; ROZKLADY_WIDTH=2000; ROZKLADY_WIZYTA=87; __utma=174679166.1548628989.1697730056.1697730056.1697730056.1; __utmz=174679166.1697730056.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)',
    'Host': 'rozklady.mpk.krakow.pl',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Referer': 'https://rozklady.mpk.krakow.pl/?lang=PL&rozklad=20231026&linia=1__1__1'
    }

    url2 = url
    for c in ['\\', '//', '/', '?', '%', '*', ':', '|', '"', '<', '>']:
        url2 = url2.replace(c, '-')
    fsUrl = './pages/' + url2

    try:
        if os.path.exists(fsUrl):
            with open(fsUrl, 'r') as f:
                data = f.read()
            return data
        else:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                body = response.read().decode('utf-8')
                with open(fsUrl, 'w') as f:
                    print(len(body))
                    f.write(body)
                return body
    except Exception as e:
        print(e)
        return e

main()