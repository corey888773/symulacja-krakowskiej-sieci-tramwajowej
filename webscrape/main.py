from bs4 import BeautifulSoup
import json, os, requests, re
import html_table_parser.parser as parser

strona = 'http://rozklady.mpk.krakow.pl'

def main():
    if not os.path.exists('./pages'):
        os.makedirs('./pages')

    # try:
    mainBody = getQuote('http://rozklady.mpk.krakow.pl/?lang=PL&akcja=index&rozklad=20200323')
    soup = BeautifulSoup(mainBody, 'html.parser')
    rozklad = {'lines': []}

    numeryLinii = []
    linkiLinii = []

    for el in soup.select('.linia_table_left a'):
        text = el.text
        link = el['href']
        text = text.replace(' ', '').replace('\t', '').replace('\n', '')

        if text[0].isdigit() and int(text) < 53:
            numeryLinii.append(text)
            linkiLinii.append(link)

    for i in range(len(linkiLinii)):
        link = linkiLinii[i]
        numer = numeryLinii[i]
        body = getQuote(strona + link)
        linia = BeautifulSoup(body, 'html.parser')

        linkiKierunkow = []
        nazwyKierunkow = []

        linkiKierunkow[0] = strona + linkiLinii[i] + '_1'
        linkiKierunkow[1] = strona + linkiLinii[i] + '_2'
        # for el in linia.select('TBODY TR TD table tr td tr td a'):
        #     linkiKierunkow.append(el['href'])
        #     nazwyKierunkow.append(el.text)
        #     # print(link)

        kierunek1 = przetworzKierunek(linkiKierunkow[0], nazwyKierunkow[0])
        kierunek2 = przetworzKierunek(linkiKierunkow[1], nazwyKierunkow[1])

        linia = {
            'number': numer,
            'direction1': kierunek1,
            'direction2': kierunek2
        }

        rozklad['lines'].append(linia)

    with open('./schedule.json', 'w') as f:
        json.dump(rozklad, f)
    print("Koniec")
    # except Exception as e:
    #     print(e)

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
            parsed_table = parser.make2d(tabelaHtml)

            przystanek = {
                'name': nazwaPrzystanku,
                'schedule': parsed_table
            }

            kierunek['stops'].append(przystanek)

        return kierunek
    except Exception as e:
        print(e)
        return e

def getQuote(url):
    headers = {
        'Host': 'rozklady.mpk.krakow.pl',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'http://rozklady.mpk.krakow.pl/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': 'ROZKLADY_JEZYK=PL; ROZKLADY_WIDTH=2000; ROZKLADY_AB=0; __utma=174679166.140374276.1585039119.1585039119.1585039119.1; __utmc=174679166; __utmz=174679166.1585039119.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); ROZKLADY_WIZYTA=23; ROZKLADY_OSTATNIA=1585093785'
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
            print("odwiedzam " + url)
            response = requests.get(url, headers=headers)
            with open(fsUrl, 'w') as f:
                f.write(response.text)
            return response.text
    except Exception as e:
        print(e)
        return e

main()