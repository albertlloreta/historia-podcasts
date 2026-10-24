"""Fusiona metadades/brut/*.txt + wikidata-cache.json dins dels JSON d'episodis.

Camps afegits a cada episodi (només si tenen valor):
  tematiques, paisos, regions (codis, vegeu metadades/VOCABULARI.md), lloc {nom, qid, lat, lon},
  ambit_catala, periodes, segles [inici, fi], personatges / esdeveniments [{nom, qid}],
  civilitzacions, tipus, convidats, serie, idioma.
"""
import glob, json, os, re, sys
from collections import Counter

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = {'pdt': 'episodis-portes-de-troia.json', 'eg': 'episodis-en-guardia.json',
         'sons': 'episodis-sons-edat-mitjana.json', 'ih': 'sessions-institut-humanitats.json'}
CAMPS = ['tematiques', 'paisos', 'regions', 'lloc', 'ambit_catala', 'periodes', 'segles', 'personatges',
         'esdeveniments', 'civilitzacions', 'tipus', 'convidats', 'serie', 'idioma']
wd = json.load(open(f'{D}/metadades/wikidata-cache.json'))
# correccions manuals de Wikidata: metadades/wikidata-correccions.json {"pers|Nom": {"qid": ..} o null}
corr_f = f'{D}/metadades/wikidata-correccions.json'
if os.path.exists(corr_f):
    wd.update(json.load(open(corr_f)))


def anys(dh):
    """'1095-1291' -> (1095, 1291); '-264-146' -> (-264, -146); '-1000 400' -> (-1000, 400)."""
    if dh is None:
        return None
    s = str(dh).replace('–', '-').replace('dC', '').strip()
    m = re.fullmatch(r'(-?\d+)\s*(?:(-|\s)\s*(-?\d+))?', s)
    if not m:
        m2 = re.fullmatch(r'(-?\d+)\s*-\s*(-?\d+)', s.replace(' ', ''))
        if not m2:
            return None
        m = m2
        a, b = int(m.group(1)), int(m.group(2))
        return (a, b)
    a = int(m.group(1))
    if m.group(3) is None:
        return (a, a)
    b = int(m.group(3))
    if a < 0 and m.group(2) == '-' and b > 0 and b < -a:  # '-264-146': tots dos aC
        b = -b
    return (min(a, b), max(a, b))


def segle(a):
    return (a - 1) // 100 + 1 if a > 0 else -((-a - 1) // 100 + 1)


PER = [('prehistoria', -10**9, -3000), ('antiga', -3000, 476), ('medieval', 476, 1492),
       ('moderna', 1492, 1789), ('contemporania', 1789, 3000)]


def periodes(r):
    a, b = r
    return [n for n, i, f in PER if a < f and b >= i]


def ent(tipus, noms):
    out = []
    for n in noms:
        d = wd.get(f'{tipus}|{n}')
        e = {'nom': n}
        if d and d.get('qid'):
            e['qid'] = d['qid']
        out.append(e)
    return out


def llista(v):
    return [x.strip() for x in v.split(';') if x.strip() and x.strip() != '-']


brut = {}
for f in sorted(glob.glob(f'{D}/metadades/brut/*.txt')):
    for l in open(f).read().splitlines():
        c = ['' if x == '-' else x for x in l.split('|')]
        brut[c[0]] = c

for pre, fitxer in FONTS.items():
    eps = json.load(open(f'{D}/{fitxer}'))
    # sèries: títol sense numeral final, si n'hi ha 2 o més
    def clau_serie(t):
        t = re.sub(r'^\d+\.\s*', '', t or '')
        t = re.sub(r'^\d+/\d+\s+', '', t)
        t2 = re.sub(r'\s*[\(\[]?\s*(?:part\s+)?(?:I{1,3}|IV|V|VI{0,3}|\d+|primer capítol|segon capítol)\s*[\)\]]?\s*$', '', t, flags=re.I)
        t2 = re.sub(r'\s*\((?:[^()]*?)\s\d+\)\s*$', '', t2)  # «(Successió 3)», «(Imperi romà 4)»
        return t2.strip(' :-–') if t2 != t else None
    series = Counter(clau_serie(e['titol']) for e in eps)
    for i, e in enumerate(eps):
        for k in CAMPS:
            e.pop(k, None)
        c = brut.get(f'{pre}:{i}')
        if not c:
            continue
        _, tem, pais, reg, lloc, cat, pers, esd, civ, tip, conv, idi = c
        nou = {
            'tematiques': llista(tem), 'paisos': llista(pais), 'regions': llista(reg),
            'civilitzacions': llista(civ), 'tipus': tip or None, 'idioma': idi or None,
            'ambit_catala': True if cat == '1' else None,
            'personatges': ent('pers', llista(pers)), 'esdeveniments': ent('esdev', llista(esd)),
            'convidats': llista(conv) if pre != 'ih' else [],
        }
        if lloc:
            d = wd.get(f'lloc|{lloc}') or {}
            nou['lloc'] = {'nom': lloc, **{k: d[k] for k in ('qid', 'lat', 'lon') if k in d}}
        r = anys(e.get('data_historica'))
        if r:
            nou['periodes'] = periodes(r)
            nou['segles'] = [segle(r[0]), segle(r[1])]
        s = clau_serie(e['titol'])
        if s and series[s] > 1:
            nou['serie'] = s
        for k in CAMPS:
            if nou.get(k) not in (None, [], ''):
                e[k] = nou[k]
    # mateix format que l'original (2 espais), però amb els valors nous en una sola línia
    def obj(e):
        return '  {\n' + ',\n'.join(f'    {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}'
                                      for k, v in e.items()) + '\n  }'
    open(f'{D}/{fitxer}', 'w').write('[\n' + ',\n'.join(obj(e) for e in eps) + '\n]\n')
    print(fitxer, len(eps), 'amb lloc:', sum('lloc' in e and 'lat' in e['lloc'] for e in eps),
          'sèries:', len({e['serie'] for e in eps if 'serie' in e}))
