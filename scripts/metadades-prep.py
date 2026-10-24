"""Prepara lots compactes d'episodis per extreure'n metadades (metadades/lots/NN.txt)."""
import json, os, re
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# clau temporal = posició dins del fitxer
FONTS = [('pdt', 'episodis-portes-de-troia.json'), ('eg', 'episodis-en-guardia.json'),
         ('sons', 'episodis-sons-edat-mitjana.json'), ('ih', 'sessions-institut-humanitats.json')]
MIDA = 100

def net(t, n=500):
    t = re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ', t or '')).strip()
    return t[:n]

files = []
for pre, f in FONTS:
    for i, e in enumerate(json.load(open(f'{D}/{f}'))):
        extra = f" [curs: {e['curs']}]" if e.get('curs') else ''
        files.append(f"{pre}:{i} | {e['titol']} | dh={e.get('data_historica')}{extra} | {net(e.get('descripcio'))}")
os.makedirs(f'{D}/metadades/lots', exist_ok=True)
for i in range(0, len(files), MIDA):
    open(f'{D}/metadades/lots/{i // MIDA:02d}.txt', 'w').write('\n'.join(files[i:i + MIDA]) + '\n')
print(len(files), 'entrades,', (len(files) + MIDA - 1) // MIDA, 'lots')
