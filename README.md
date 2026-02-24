# A les Portes de Troia — Cronologia

Visualització cronològica dels episodis del podcast d'història en català [A les Portes de Troia](https://www.portesdetroia.cat).

## Què és

[A les Portes de Troia](https://www.portesdetroia.cat) és un podcast d'història en català, emès des de Ràdio Castellar i distribuït per La Xarxa. Des del 2013, Alberto Reche, Sergio Rodríguez i Albert Abril expliquen el passat en present: batalles, revolucions, personatges i civilitzacions.

Aquesta pàgina endreça els capítols en ordre cronològic —no quan es van emetre, sinó quan van passar els fets que expliquen— organitzats per èpoques, des de la prehistòria fins avui.

## Funcionalitats

- Cronologia interactiva ordenada per període històric
- Navegació per èpoques: Prehistòria, Antiguitat, Edat Mitjana, Edat Moderna, Edat Contemporània
- Cerca en temps real per títol, descripció i ubicació
- Expansió de cada capítol amb descripció i enllaç per escoltar

## Dades

`episodis.json` conté 529 episodis (ep. 1–530) amb:
- Títol, data/període històric, descripció
- Enllaç a portesdetroia.cat (ep. 68+) o iVoox (ep. 1–67)

**Font de les dades**: portesdetroia.cat, iVoox

## Execució local

```bash
python3 -m http.server 8080
# → http://localhost:8080
```

## Desplegament

Cloudflare Pages → `allr.cat/historia`
