#!/usr/bin/env python3
"""Afegeix `ivoox` a les sessions IH de vídeo que també són al pòdcast "Arxiu Institut Humanitats" d'iVoox (àudio sempre preferit).
Aparella per títol+ponents: automàtic si similitud >= 0.9; entre 0.55 i 0.9 només si el títol del feed conté una clau revisada a mà (OK).
Ús: curl -sL https://feeds.ivoox.com/feed_fg_f11428301_filtro_1.xml > feed.xml && python3 scripts/ih-video-ivoox.py feed.xml sessions-institut-humanitats.json"""
import json,re,sys,unicodedata,xml.etree.ElementTree as ET,difflib
feed,src=sys.argv[1],sys.argv[2]
OK=['Quixot i la nov','Judith Butler','Desig postcapitalista','Treballs de reproducci','Artemisia','La fi de la natura','Esgotats','Caminar la perif','El camí cap a les elegies','Susanna i els vells','Malenconia','El futur és nostre','La llibertat d\'expressió','La neuroplasticitat','Practicar la utopia','Arendt i Eichmann','Què és la música','Utopies de retorn','Fanon abans de Fanon','Qui ens mira','L\'enveja','habitació de Jacob','Happycràcia']
n=lambda s:' '.join(re.sub(r'[^a-z0-9 ]','',unicodedata.normalize('NFKD',s.lower()).encode('ascii','ignore').decode()).split())
d=json.load(open(src));v=[s for s in d if s['format']=='video']
key=lambda s:n(s['titol']+' '+' '.join(s['ponents']))
hits={}
for it in ET.parse(feed).iter('item'):
    t=re.sub(r'\s*\|\s*\d+\s*$','',it.findtext('title').strip()).lstrip('✨ ')
    i=re.search(r'_mf_(\d+)_',it.find('enclosure').get('url')).group(1)
    b=max(v,key=lambda s:difflib.SequenceMatcher(None,key(s),n(t)).ratio())
    r=difflib.SequenceMatcher(None,key(b),n(t)).ratio()
    if r>=0.9 or (r>=0.55 and any(k in t for k in OK)):
        hits.setdefault(b['nid'],[]).append((t,i))
dup={k:x for k,x in hits.items() if len(x)>1};print('dup',dup)
for s in v:
    if s['nid'] in hits and len(hits[s['nid']])==1: s['ivoox']=hits[s['nid']][0][1]
json.dump(d,open(src,'w'),ensure_ascii=False,indent=2)
print('fets',sum(1 for s in v if s.get('ivoox')))
