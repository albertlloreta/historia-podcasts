# Metadades dels episodis

Extretes del títol + descripció (sense transcriure). Format brut (`metadades/brut/NN.txt`), una línia per entrada:

```
clau|tem|pais|reg|lloc|cat|pers|esdev|civ|tip|conv|idioma
```

Valors múltiples separats per `;`. Camp buit = no aplica / no se sap.

- **clau**: `pdt|eg|sons|ih:<posició al fitxer>` (només per al procés; el resultat es fusiona dins de cada episodi)
- **tem** (temàtiques, màx. 3): `pol` política · `gue` guerra i conflictes · `soc` societat · `eco` economia i treball · `rel` religió · `art` art · `arq` arquitectura i urbanisme · `lit` literatura · `mus` música · `cie` ciència i tècnica · `fil` filosofia i pensament · `quo` vida quotidiana · `arqu` arqueologia · `exp` exploracions i viatges · `gen` dones i gènere · `cul` cultura popular i mitjans · `esp` esport · `his` historiografia i memòria · `dre` dret i justícia · `med` medicina i salut · `cin` cinema i imatge
- **pais**: codis ISO 3166-1 dels estats actuals on passa la història (Catalunya → `ES`; Catalunya Nord → `FR`)
- **reg**: `EUS` Europa meridional · `EUO` Europa occidental · `EUC` Europa central · `EUN` Europa septentrional · `EUE` Europa oriental · `PO` Pròxim Orient · `NA` Nord d'Àfrica · `AS` Àfrica subsahariana · `ACM` Àsia central · `ASM` Àsia meridional · `AO` Àsia oriental · `SEA` Sud-est asiàtic · `AN` Amèrica del Nord · `AL` Amèrica Llatina · `OC` Oceania · `GLO` global
- **lloc**: un sol lloc, el més concret amb coordenades (ciutat, jaciment o regió), en català
- **cat**: `1` si és d'àmbit català (Països Catalans o catalans a fora)
- **pers**: personatges històrics protagonistes (no presentadors ni convidats), màx. 5
- **esdev**: esdeveniments amb nom propi, màx. 2
- **civ**: pobles o civilitzacions (`romans`, `ibers`...), màx. 3
- **tip**: `bio` biografia · `con` conflicte · `pro` procés polític o social · `quo` vida quotidiana · `cul` cultura i idees · `lloc` història d'un lloc · `deb` debat o historiografia
- **conv**: convidats que esmenta la descripció (a l'IH surten de `ponents`)
- **idioma**: buit = català; si no, `es`, `en`, `fr`...

Derivats per script (no es marquen a mà): gran període i segle (de `data_historica`), sèrie (títol / `curs`), Wikidata i coordenades (`scripts/metadades-wikidata.py`).

## Notes de criteri

- En Guàrdia: Josep Maria Solé i Sabaté (col·laborador fix) no es compta com a convidat.
- Quan títol i descripció no coincideixen (vegeu `incidencies.txt`), mana el títol.
- `idioma` només es marca quan el títol de la sessió és en una altra llengua; no és fiable per a l'IH.
- Dates: `-264-146` s'interpreta com a 264-146 aC (el segon nombre és menor); casos com `-43-17` (43 aC - 17 dC) queden mal interpretats.

## Procés

1. `python3 scripts/metadades-prep.py` → `metadades/lots/NN.txt`
2. Extracció (Claude) → `metadades/brut/NN.txt`; `python3 scripts/metadades-valida.py`
3. `python3 scripts/metadades-wikidata.py` → `metadades/wikidata-cache.json` (correccions a `wikidata-correccions.json`)
4. `python3 scripts/metadades-fusiona.py` → camps nous als JSON d'episodis
