import re
import requests
import csv

def requestTextFromWebsite(naslov):
    try:
        r = requests.get(naslov)
    except requests.exceptions.ConnectionError:
        print('connection error')
    else:
        return r.text;

def requestCragHtml(id):
    with open('html/miska.html', 'w') as out:
        out.write(requestTextFromWebsite('http://www.plezanje.net/climbing/db/showCrag.asp?crag=' + str(id)))
        print('succes')


def requestDataHtml(location):
    re_id = re.compile('<a href="showRoute\.asp\?route=(?P<id>\d+)">(?!Opis)')
    with open('html/route_details.html', 'w') as details, open(location, 'r') as crag_file:
        crag = crag_file.read()
        for route_id in re.finditer(re_id, crag):
            details.write(requestTextFromWebsite('http://www.plezanje.net/climbing/db/showRoute.asp?route=' + str(route_id.group('id'))))
            #print(route_id.group('id'))

def cleanSmeri(dict):
    out = {}
    out['id'] = int(dict['id'])
    out['ime'] = dict['ime'].strip()
    out['ocena'] = dict['ocena'].strip()
    out['dolzina'] = int(dict['dolzina'])
    out['vzponi'] = dict['vzponi'].strip()
    return out

def cleanOcene(ocena, smer, id):
    out = {}
    out['id'] = id
    out['smer_id'] = int(smer['id'])
    out['ime'] = smer['ime'].strip()
    out['ocena'] = ocena['ocena'].strip()
    out['plezalec'] = ocena['plezalec'].strip()
    out['datum'] = ocena['datum'].strip()
    out['valid'] = ocena['valid'].strip()
    return out

def extractRouteDetails(location):

    route_pattern = re.compile(r'<!DOCTYPE html PUBLIC.*?xp:id="(?P<id>\d+)".*?'
                               r'<title>Smer v plezališču: (?P<ime>.+?)</title>.*?'
                               r'<dt>Težavnost</dt>.*?<dd>(?P<ocena>.+?)</dd>.*?'
                               r'<dt>Dolžina smeri \(m\)</dt>.*?<dd id="RouteHeigth">(?P<dolzina>\d+)</dd>.*?'
                               r'<dt>Zabeleženih vzponov</dt>.*?<dd>(?P<vzponi>.*?)</dd>.*?'
                               r'<div class="formSection">.*?<p class="formSectionTitle">Ocene</p>(?P<tabela>.*?)</div>', flags=re.DOTALL)

    ocena_pattern = re.compile(r'<tr class="(?P<valid>.*?)">.*?'
                               r'<td valign="top">(?P<ocena>.+?)</td>.*?'
                               r'<td valign="top">(?P<plezalec>.*?)</td>.*?'
                               r'<td valign="top">(?P<datum>.*?)</td>', flags=re.DOTALL)

    smeri = []
    ocene = []
    ocene_id = 1
    with open('csv/smeri.csv', 'w') as route_csv, open('csv/ocene.csv', 'w') as ocene_csv, open(location, 'r') as routes_file:
        routes_re = routes_file.read()
        for route_re in re.finditer(route_pattern, routes_re):
            clean_route = route_re.groupdict()
            smeri.append(cleanSmeri(clean_route))
            print(route_re.group('ime'))
            for ocena_re in re.finditer(ocena_pattern, route_re.group('tabela')):
                ocene.append(cleanOcene(ocena_re.groupdict(), clean_route, ocene_id))
                print(ocena_re.group('ocena'))
                ocene_id += 1

        smeri_writer = csv.DictWriter(route_csv, fieldnames = ['id', 'ime', 'ocena', 'dolzina', 'vzponi'])
        smeri_writer.writeheader()
        for route in smeri:
            smeri_writer.writerow(route)

        ocene_writer = csv.DictWriter(ocene_csv, fieldnames=['id', 'smer_id', 'ime', 'ocena', 'plezalec', 'datum', 'valid'])
        ocene_writer.writeheader()
        for ocena in ocene:
            ocene_writer.writerow(ocena)



#requestCragHtml(606)
#requestDataHtml('html/miska.html')
extractRouteDetails('html/route_details.html')