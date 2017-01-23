import re
import requests
import csv

def requestTextFromWebsite(naslov):
    try:
        r = requests.get(naslov)
    except requests.exceptions.ConnectionError:
        print('connection error')
    else:
        return r.text

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

def cleanSmeri(route):
    ocena1_pattern = re.compile(r'<dt>Težavnost</dt>.*?<dd>(?P<ocena>.+?)</dd>', flags=re.DOTALL)
    dolzina_pattern = re.compile(r'<dt>Dolžina smeri \(m\)</dt>.*?<dd id="RouteHeigth">(?P<dolzina>\d+)</dd>', flags=re.DOTALL)
    vzponi_pattern = re.compile(r'<dt>Zabeleženih vzponov</dt>.*?<dd>(?P<vzponi>.+?)</dd>', flags=re.DOTALL)
    ocena = re.search(ocena1_pattern, route.group('tabela1'))
    dolzina = re.search(dolzina_pattern, route.group('tabela1'))
    vzponi = re.search(vzponi_pattern, route.group('tabela1'))
    out = {}
    route_dict = route.groupdict()
    out['id'] = int(route_dict['id'])
    out['ime'] = route_dict['ime'].strip()
    if ocena: out['ocena'] = ocena.groupdict()['ocena'].strip()
    else: out['ocena'] = ''
    if dolzina: out['dolzina'] = int(dolzina.groupdict()['dolzina'])
    else: out['dolzina'] = 0
    if vzponi: out['vzponi'] = vzponi.groupdict()['vzponi'].strip()
    else: out['vzponi'] = ''
    return out

def cleanOcene(tabela, smer, id):
    info_pattern = re.compile(r'<td valign="top">(?P<info>.+?)</td>', flags=re.DOTALL)
    plezalec_pattern = re.compile(r'<td valign="top">(?P<plezalec>.+?)</td>', flags=re.DOTALL)
    datum_pattern = re.compile(r'<td valign="top">(?P<datum>.+?)</td>', flags=re.DOTALL)
    out = {}
    smer_dict = smer.groupdict()
    roles = ['ocena', 'plezalec', 'datum']
    i = 0
    out['id'] = id
    out['smer_id'] = int(smer_dict['id'])
    out['ime'] = smer_dict['ime'].strip()
    out['ocena'] = ''
    out['plezalec'] = ''
    out['datum'] = ''
    for info in re.finditer(info_pattern, tabela.group('tabela3')):
        if info:
            out[roles[i]] = info.groupdict()['info'].strip()
        else:
            out[roles[i]] = ''
        i += 1
    out['valid'] = tabela.groupdict()['valid'].strip()
    return out

def extractRouteDetails(location):

    route_pattern = re.compile(r'<!DOCTYPE html PUBLIC.*?xp:id="(?P<id>\d+)".*?'
                               r'<title>Smer v plezališču: (?P<ime>.+?)</title>.*?'
                               r'<dl class="dlTable">(?P<tabela1>.+?)</dl>.*?'
                               r'<div style="clear: both;">(?P<tabela2>.*?)<div style="clear: both;">', flags=re.DOTALL)

    tabela2_pattern = re.compile(r'<tr class="(?P<valid>.*?)">(?P<tabela3>.*?)</tr>', flags=re.DOTALL)

    smeri = []
    ocene = []
    ocene_id = 1
    with open('csv/smeri.csv', 'w') as route_csv, open('csv/ocene.csv', 'w') as ocene_csv, open(location, 'r') as routes_file:
        routes_re = routes_file.read()
        for route_re in re.finditer(route_pattern, routes_re):
            print(route_re.group('ime'))
            smeri.append(cleanSmeri(route_re))
            for tabela_re in re.finditer(tabela2_pattern, route_re.group('tabela2')):
                print(tabela_re.group('tabela3'))
                ocene.append(cleanOcene(tabela_re, route_re, ocene_id))
                ocene_id += 1

        smeri_writer = csv.DictWriter(route_csv, fieldnames = ['id', 'ime', 'ocena', 'dolzina', 'vzponi'])
        smeri_writer.writeheader()
        for route_out in smeri:
            smeri_writer.writerow(route_out)

        ocene_writer = csv.DictWriter(ocene_csv, fieldnames=['id', 'smer_id', 'ime', 'ocena', 'plezalec', 'datum', 'valid'])
        ocene_writer.writeheader()
        for ocena_out in ocene:
            ocene_writer.writerow(ocena_out)



#requestCragHtml(606)
#requestDataHtml('html/miska.html')
extractRouteDetails('html/route_details.html')