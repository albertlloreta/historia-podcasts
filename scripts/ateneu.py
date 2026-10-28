#!/usr/bin/env python3
"""Genera sessions-ateneu.json a partir de l'Arxiu de la Paraula de l'Ateneu Barcelonès.

Entrades:
  items.json      totes les fitxes (extretes de /items/browse?output=omeka-json)
  seleccio.json   {id: data_historica} de les sessions amb temporalitat històrica
                  (classificades a mà; criteri a historia-pendents/ateneu/CRITERI.md)

Ús: python3 scripts/ateneu.py ITEMS.json SELECCIO.json > sessions-ateneu.json
L'àudio es serveix via /ateneu/<hash>.mp3 (functions/ateneu/[file].js), perquè l'Ateneu no té HTTPS.
"""
import html
import json
import re
import sys

items = {i['id']: i for i in json.load(open(sys.argv[1]))}
sel = json.load(open(sys.argv[2]))


ENTITAT = re.compile(r'^Barcelona \(|\d\. \w|\(\d{4}|\)\.|\bCicle\b|\bCurs\b|\(Grup|\(Associació|^(Symposium|Edicions|Sociedad|KRTU|EspaiNANO|L\'Avenç|Residencia|Societat|Institut|Institució|Universitat|Fundació|Associació|Secció|Centre|Grup|Xarxa|Liceu|Col·legi|Ajuntament|Generalitat|Diputació|Consell|Taula|Plataforma|Amics|Escola|Editorial|Òmnium|Acadèmia|Cercle|Comissió|Federació|Casa|Museu|PEN|Club)\b')


def clean(t):
    t = (t or '').replace('\ufeff', '').replace('\u200e', '').replace('\u200f', '')
    return re.sub(r'\s+', ' ', t).strip()


def text(t):
    """Desfà l'HTML que l'arxiu ja porta codificat (&lt;p&gt;, &amp;egrave;) i treu etiquetes."""
    t = clean(t)
    for _ in range(3):
        t = html.unescape(t)
    return clean(re.sub(r'<[^>]+>', ' ', t))


def nom(autoritat):
    """'Figueres, Josep M. (Josep Maria), 1950-' -> 'Josep Maria Figueres'."""
    t = clean(autoritat)
    t = re.sub(r'^([^,]+),\1,', r'\1,', t)                    # «Barrera,Barrera, Heribert»
    t = re.sub(r',?\s*\d{3,4}\s*-?\s*(\d{3,4})?\.?$', '', t)    # dates de vida
    t = re.sub(r',\s*ed\.?$', '', t).strip(' ,.')
    parts = [p.strip() for p in t.split(',')]
    if len(parts) == 2 and parts[1]:
        cognom, nom_ = parts
        m = re.match(r'^(.*?)\s*\(([^)]*)\)$', nom_)
        if m:   # «Josep M. (Josep Maria)» -> forma desplegada; «Joan (Pagès Blanch)» -> Joan
            nom_ = m.group(2) if m.group(2).split()[0][:1] == m.group(1)[:1] and '.' in m.group(1) else m.group(1)
        return f'{nom_} {cognom}'
    return t


def titol(t):
    t = clean(t)
    return t[0].upper() + t[1:] if t else t


# Vídeos de YouTube que l'arxiu enllaça malament (comprovat amb l'oEmbed de YouTube, 2026-10-28)
VIDEO_ERRONI = {3350}  # porta el vídeo de la 3349

out = []
for iid, data in sel.items():
    i = items[iid]
    persones = [*i.get('Creator', []), *i.get('Contributor', [])]
    ponents = list(dict.fromkeys(nom(p) for p in persones if p and not clean(p).startswith('Ateneu Barcelon') and not ENTITAT.search(clean(p)) and '. ' not in clean(p).split(',')[0]))
    any_sessio = re.search(r'\d{4}', (i.get('Date Created') or [''])[0])
    yt = re.search(r'embed/([\w-]{11})', ' '.join(i.get('Vídeo a Youtube', [])))
    mp3 = next((re.search(r'/([0-9a-f]{32})\.mp3$', f).group(1) for f in i['files'] if f.lower().endswith('.mp3')), None)
    e = {
        'podcast': 'ateneu',
        'num': None,
        'nid': int(iid),
        'format': 'video' if yt and not mp3 else 'audio',
        'titol': titol(text(i['Title'][0])).replace('<', '‹').replace('>', '›'),
        'ponents': ponents,
        'data_sessio': any_sessio.group(0) if any_sessio else None,
        'data_historica': data,
        'descripcio': html.escape(text((i.get('Description') or [''])[0]), quote=False) or None,
        'enllac': f'http://arxiudigital.ateneubcn.cat/items/show/{iid}',
        'tema_ateneu': i.get('collection_title'),
        'durada': (i.get('Durada') or [None])[0],
    }
    if mp3:
        e['mp3'] = mp3
    elif yt and int(iid) not in VIDEO_ERRONI:
        e['youtube'] = yt.group(1)
    out.append(e)

out.sort(key=lambda e: e['nid'])
json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
print(f'{len(out)} sessions ({sum(1 for e in out if "mp3" in e)} àudio, {sum(1 for e in out if "youtube" in e)} vídeo)', file=sys.stderr)
