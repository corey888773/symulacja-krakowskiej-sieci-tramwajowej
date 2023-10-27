from bs4 import BeautifulSoup
import json, os, urllib.request, urllib.parse
from html_table_parser import HTMLTableParser

page = 'http://rozklady.mpk.krakow.pl'

def main():
    if not os.path.exists('./pages'):
        os.makedirs('./pages')

    try:
        mainBody = get_html('http://rozklady.mpk.krakow.pl/?lang=PL&akcja=index&rozklad=20200323')
        soup = BeautifulSoup(mainBody, 'html.parser')
        schedule = {'lines': []}

        lineNumbers = []
        lineUrls = []

        for el in soup.select('.linia_table_left a'):
            text = el.text
            link = el['href']
            text = text.replace(' ', '').replace('\t', '').replace('\n', '')

            if text[0].isdigit() and int(text) < 53:
                lineNumbers.append(text)
                lineUrls.append(link)

        for i in range(len(lineUrls)):
            url = lineUrls[i]
            numer = lineNumbers[i]
            body = get_html(page + url)
            print(page + url)
            line = BeautifulSoup(body, 'html.parser')

            directionUrls = []
            directionNames = []

            i = 0   
            for el in line.select('td table tr td table tr td table tr TD a'):
                directionUrls.append(el['href'])
                text = el.text.replace(' ', '').replace('\t', '').replace('\n', '')
                directionNames.append(text)
                
            direction1 = process_direction(page + directionUrls[0], directionNames[0])
            print(page + directionUrls[1])
            direction2 = process_direction(page + directionUrls[1], directionNames[1])

            line = {
                'number': numer,
                'direction1': direction1,
                'direction2': direction2
            }

            schedule['lines'].append(line)

        with open('./schedule.json', 'w', encoding='utf-8') as f:
            json.dump(schedule, f,  ensure_ascii=False, indent=True)
        print("done")
    except Exception as e:
        print(e)

def process_direction(url, name):
    try:
        body = get_html(url)
        linia = BeautifulSoup(body, 'html.parser')

        stopUrls = []
        for el in linia.select('a span'):
            stopUrls.append(el.parent['href'])

        direction = {
            'name': name,
            'stops': []
        }

        for stopUrl in stopUrls:
            stopBody = get_html(page + stopUrl)
            stop = BeautifulSoup(stopBody, 'html.parser')

            stopName = stop.select('div span')[0].text

            stopSchedule = stop.select('tr td table')[14]

            tabelaHtml = str(stopSchedule)
            parsedTable = parse_table(tabelaHtml)

            stop = {
                'name': stopName,
                'schedule': parsedTable
            }

            direction['stops'].append(stop)

        return direction
    except Exception as e:
        print(e)
        return e

def parse_table(table : str):
    p = HTMLTableParser()
    p.feed(table)
    return p.tables

def get_html(url):
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