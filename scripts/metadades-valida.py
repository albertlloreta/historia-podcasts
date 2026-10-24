"""Valida metadades/brut/*.txt contra el vocabulari i els lots."""
import glob, os, re, sys
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEM = set('pol gue soc eco rel art arq lit mus cie fil quo arqu exp gen cul esp his dre med cin'.split())
REG = set('EUS EUO EUC EUN EUE PO NA AS ACM ASM AO SEA AN AL OC GLO'.split())
TIP = set('bio con pro quo cul lloc deb'.split())
lots = sys.argv[1:] or [os.path.basename(f)[:-4] for f in sorted(glob.glob(f'{D}/metadades/brut/*.txt'))]
err = 0
for n in lots:
    claus = [l.split(' | ')[0] for l in open(f'{D}/metadades/lots/{n}.txt').read().splitlines()]
    files = open(f'{D}/metadades/brut/{n}.txt').read().splitlines()
    vistes = []
    for l in files:
        c = ['' if x == '-' else x for x in l.split('|')]
        if len(c) != 12: print(n, 'camps', len(c), l[:60]); err += 1; continue
        k, tem, pais, reg, lloc, cat, pers, esd, civ, tip, conv, idi = c
        vistes.append(k)
        for v, ok, nom in ((tem, TEM, 'tem'), (reg, REG, 'reg')):
            for x in filter(None, v.split(';')):
                if x not in ok: print(n, k, nom, x); err += 1
        for x in filter(None, pais.split(';')):
            if not re.fullmatch('[A-Z]{2}', x): print(n, k, 'pais', x); err += 1
        if tip and tip not in TIP: print(n, k, 'tip', tip); err += 1
        if cat not in ('0', '1', ''): print(n, k, 'cat', cat); err += 1
    if vistes != claus: print(n, 'claus no coincideixen', set(claus) ^ set(vistes)); err += 1
print('errors:', err, '| lots:', len(lots))
