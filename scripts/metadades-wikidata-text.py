"""Resol noms amb cerca de text complet de Wikidata (millor per a frases com «Abel son of Adam»).
Ús: python3 scripts/metadades-wikidata-text.py metadades/FITXER.json  ({"pers|Nom": "terme"})."""
import json, os, sys
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(f'{D}/scripts/metadades-wikidata.py').read().split('cache = json.load')[0]
ns = {'__file__': f'{D}/scripts/metadades-wikidata.py'}
exec(src, ns)
api = ns['api']
cache = json.load(open(ns['CACHE']))
for k, terme in json.load(open(sys.argv[1])).items():
    hits = api(action='query', list='search', srsearch=terme, srlimit=1, srnamespace=0).get('query', {}).get('search', [])
    if not hits:
        print(k, '→ res'); continue
    q = hits[0]['title']
    e = api(action='wbgetentities', ids=q, props='labels|descriptions|claims', languages='ca|es|en')['entities'][q]
    d = {'qid': q,
         'label': next((e['labels'][l]['value'] for l in ('ca', 'es', 'en') if l in e.get('labels', {})), terme),
         'desc': next((e['descriptions'][l]['value'] for l in ('ca', 'es', 'en') if l in e.get('descriptions', {})), '')}
    c = e.get('claims', {}).get('P625')
    v = c and c[0]['mainsnak'].get('datavalue', {}).get('value')
    if v:
        d.update(lat=round(v['latitude'], 4), lon=round(v['longitude'], 4))
    cache[k] = d
    print(k, '→', d['label'], '|', d['desc'][:60])
json.dump(cache, open(ns['CACHE'], 'w'), ensure_ascii=False, indent=0)
