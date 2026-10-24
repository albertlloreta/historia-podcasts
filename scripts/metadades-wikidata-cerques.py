"""Torna a resoldre a Wikidata els noms de metadades/wikidata-cerques.json amb el terme de cerca indicat."""
import json, os, sys
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(f'{D}/scripts/metadades-wikidata.py').read().split('cache = json.load')[0]
ns = {'__file__': f'{D}/scripts/metadades-wikidata.py'}
exec(src, ns)
cache = json.load(open(ns['CACHE']))
for k, terme in json.load(open(f'{D}/metadades/' + (sys.argv[1] if len(sys.argv) > 1 else 'wikidata-cerques.json'))).items():
    t = k.split('|')[0]
    d = ns['resol'](t, terme)
    if d is None and t == 'pers':
        d = ns['resol']('esdev', terme)  # mites, grups...
    cache[k] = d
    print(k, '→', d and d['label'], '|', d and d['desc'][:60])
json.dump(cache, open(ns['CACHE'], 'w'), ensure_ascii=False, indent=0)
