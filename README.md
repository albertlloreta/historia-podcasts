# Història en Podcasts

Episodis de podcasts d'història en català endreçats en ordre cronològic. Disponible a [historia.allr.cat](https://historia.allr.cat).

## Podcasts

### A les Portes de Troia

[A les Portes de Troia](https://www.portesdetroia.cat) és un podcast d'història en català, emès des de Ràdio Castellar i distribuït per La Xarxa. Des del 2013, Alberto Reche, Sergio Rodríguez i Albert Abril expliquen el passat en present: batalles, revolucions, personatges i civilitzacions.

`episodis.json` conté 547 episodis (ep. 1–548) amb títol, data/període històric, descripció i enllaç (portesdetroia.cat per ep. 68+, iVoox per ep. 1–67).

### En Guàrdia

[En Guàrdia](https://www.3cat.cat/3cat/en-guardia/) és el programa d'història de Catalunya Ràdio, dirigit per l'historiador Josep Maria Solé i Sabaté.

`episodis-en-guardia.json` conté 1329 episodis. La majoria tenen descripció completa i any/període històric assignat; uns 200 episodis molt antics (números 1–199, dels primers anys del programa) no tenen descripció disponible a la pàgina d'origen i queden classificats a "Data desconeguda".

**Actualitzar amb episodis nous**: `python3 scripts/sync-en-guardia.py --write` — llegeix el feed RSS del podcast, detecta els episodis nous i en resol l'enllaç via el cercador de 3cat.cat. Cal assignar manualment `data_historica` als episodis nous (llegint la descripció) abans de desplegar.

## Funcionalitats

- Cronologia interactiva ordenada per període històric
- Navegació per èpoques: Prehistòria, Antiguitat, Edat Mitjana, Edat Moderna, Edat Contemporània
- Cerca en temps real per títol, descripció i ubicació
- Expansió de cada capítol amb descripció i enllaç per escoltar

## Execució local

```bash
python3 -m http.server 8080
# → http://localhost:8080
```

## Desplegament

Cloudflare Pages → `historia.allr.cat`
