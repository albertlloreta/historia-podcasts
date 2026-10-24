"""Correccions verificades amb l'àudio (transcripció dels 3 primers minuts) i el feed d'iVoox, octubre 2026.

- Portes de Troia: títols i dates desplaçats (ep. 12, 34, 49, 348-363), Pirros duplicat, 389 sense àudio propi.
- En Guàrdia: 16 promocions de 30 s i 10 emissions «de 15 a 16 h» duplicades fora; eg:183 identificat.
Manté metadades/brut alineat amb les noves posicions.
"""
import glob, json, os, re, subprocess
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(D)

def load(f): return json.load(open(f))
pdt, eg = load('episodis-portes-de-troia.json'), load('episodis-en-guardia.json')

# ── Portes de Troia (índexs actuals) ──
TIT = {  # índex: (títol, data_historica)
    11: ("El naixement mític i històric de Roma", "-753"),
    33: ("Memòria de sang (la Primera Guerra d'Àfrica)", "1859-1860"),
    48: ("Pàtria i llibertat, la Guerra de Successió a Catalunya", "1704-1714"),
    347: ("L'intent d'assassinat contra Ferran el Catòlic (II)", "1492"),
    348: ("La batalla de Baecula, 208 aC", "-208"),
    349: ("Roger de Llúria (I)", "1245-1305"),
    350: ("Els grans pilots de la Primera Guerra Mundial", "1914-1918"),
    351: ("Roger de Llúria (II)", "1245-1305"),
    352: ("La SOE", "1940-1946"),
    353: ("Dones espies a la Segona Guerra Mundial", "1939-1945"),
    354: ("Fantasmes i apareguts a l'edat mitjana", "500-1500"),
    355: ("Almansor", "939-1002"),
    356: ("Els temples grecs", "-700"),
    357: ("Almansor saqueja Barcelona, 985", "985"),
    358: ("Utopia", "1516"),
    359: ("Els evangelis apòcrifs", "50-150"),
    360: ("La conquesta de Mallorca de Jaume I", "1229"),
    361: ("La febre de l'or californiana", "1848-1855"),
    362: ("La Comuna de París", "1871"),
}
for i, (t, dh) in TIT.items():
    pdt[i]['titol'] = t
    pdt[i]['data_historica'] = pdt[i]['ubicacio'] = dh
pdt[346]['titol'] = "L'intent d'assassinat contra Ferran el Catòlic (I)"
# 389: tenia l'àudio i el número del 388
pdt[388].update(num=389, ivoox='101166789', titol='Història dels crims de guerra (II)')
pdt[387]['titol'] = 'Història dels crims de guerra (I)'

# metadades (brut): files reaprofitades del tema correcte o noves
brut = {}
for f in sorted(glob.glob('metadades/brut/*.txt')):
    for l in open(f).read().splitlines():
        brut[l.split('|')[0]] = l.split('|')[1:]
vell = {k: v[:] for k, v in brut.items()}
REUS = {347: 346, 348: 347, 349: 349, 351: 349, 352: 351, 353: 352, 354: 353, 355: 354, 356: 355,
        357: 356, 358: 357, 359: 358, 360: 359, 361: 360, 362: 361}
for nou, antic in REUS.items():
    brut[f'pdt:{nou}'] = vell[f'pdt:{antic}']
brut['pdt:11'] = 'pol;rel;arqu|IT|EUS|Roma|0|Ròmul i Rem|-|romans;etruscs|deb|-|'.split('|')
brut['pdt:48'] = 'gue;pol|ES|EUS|Barcelona|1|Arxiduc Carles;Felip V|Guerra de Successió espanyola|-|con|Antonio Espino|'.split('|')
brut['pdt:388'] = vell['pdt:387']
FORA_PDT = {198}  # Pirros duplicat (tenia l'àudio dels almogàvers)

# ── En Guàrdia ──
PROMOS = {116, 124, 143, 150, 157, 163, 165, 167, 172, 173, 175, 178, 181, 184, 186, 188}
DUPS = {71, 73, 75, 79, 81, 85, 87, 89, 91, 93}
eg[183].update(titol='La invasió japonesa de Manxúria', data_historica='1931',
               descripcio="El 1931 el Japó va ocupar la regió de Manxúria, al nord de la Xina, amb l'excusa d'un atemptat contra el ferrocarril del sud de Manxúria. Era el preludi de la invasió de la Xina sis anys després. (Descripció feta a partir de l'àudio.)")
brut['eg:183'] = 'gue;pol|CN;JP|AO|Shenyang|0|-|Incident de Mukden|japonesos;xinesos|con|-|'.split('|')
FORA_EG = PROMOS | DUPS

def treu(llista, fora, pre):
    nova, mapa = [], {}
    for i, e in enumerate(llista):
        if i in fora:
            continue
        mapa[i] = len(nova)
        nova.append(e)
    for i, j in mapa.items():  # reindexa brut
        brut[f'{pre}:{j}__nou'] = brut.pop(f'{pre}:{i}')
    for i in fora:
        brut.pop(f'{pre}:{i}', None)
    for k in [k for k in brut if k.endswith('__nou')]:
        brut[k[:-5]] = brut.pop(k)
    return nova

pdt = treu(pdt, FORA_PDT, 'pdt')
eg = treu(eg, FORA_EG, 'eg')

def dump(eps, f):
    obj = lambda e: '  {\n' + ',\n'.join(f'    {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}' for k, v in e.items()) + '\n  }'
    open(f, 'w').write('[\n' + ',\n'.join(obj(e) for e in eps) + '\n]\n')
dump(pdt, 'episodis-portes-de-troia.json')
dump(eg, 'episodis-en-guardia.json')

# lots i brut tornen a quedar alineats (blocs de 100 en l'ordre dels lots)
for f in glob.glob('metadades/lots/*.txt') + glob.glob('metadades/brut/*.txt'):
    os.remove(f)
subprocess.run(['python3', '-I', 'scripts/metadades-prep.py'], check=True)
for f in sorted(glob.glob('metadades/lots/*.txt')):
    claus = [l.split(' | ')[0] for l in open(f).read().splitlines()]
    open(f.replace('/lots/', '/brut/'), 'w').write('\n'.join('|'.join([k] + brut[k]) for k in claus) + '\n')
print('PdT', len(pdt), '· EG', len(eg))
