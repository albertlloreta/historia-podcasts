# Història en Podcasts

Episodis de podcasts d'història en català endreçats en ordre cronològic. Disponible a [historia.allr.cat](https://historia.allr.cat).

## Podcasts

### A les Portes de Troia

[A les Portes de Troia](https://www.portesdetroia.cat) és un podcast d'història en català, emès des de Ràdio Castellar i distribuït per La Xarxa. Des del 2013, Alberto Reche, Sergio Rodríguez i Albert Abril expliquen el passat en present: batalles, revolucions, personatges i civilitzacions.

`episodis-portes-de-troia.json` (producció) conté 556 episodis (ep. 1–557) amb títol, data/període històric, descripció i enllaç (portesdetroia.cat per ep. 68–548, iVoox per ep. 1–67 i 549+). **100% complet**: cap camp buit. `episodis.json` és una variant antiga sense el camp `podcast`, ja no s'usa a producció.

### En Guàrdia

[En Guàrdia](https://www.3cat.cat/3cat/en-guardia/) és el programa d'història de Catalunya Ràdio, dirigit per l'historiador Josep Maria Solé i Sabaté.

`episodis-en-guardia.json` conté 1340 episodis, gairebé tots amb descripció i any històric assignat. Uns 300 episodis antics no tenen la sinopsi original disponible enlloc (ni a 3cat.cat ni a iVoox ni a Wayback Machine); se'ls ha escrit una nota factual breu i un any a partir del títol. Només 42 episodis (temes massa genèrics: "La sardana", "Eurovisió"...) queden sense any assignat, i 3 sense cap descripció.

**Actualitzar amb episodis nous**: `python3 scripts/sync-en-guardia.py --write` — llegeix el feed RSS del podcast, detecta els episodis nous i en resol l'enllaç via el cercador de 3cat.cat. Cal assignar manualment `data_historica` als episodis nous (llegint la descripció) abans de desplegar.

### Sons de l'edat mitjana

[Sons de l'edat mitjana](https://www.3cat.cat/3cat/sons-edat-mitjana/) és el programa de Catalunya Música sobre la música i la història medievals, presentat per Maria Montes (2016-2019, acabat).

`episodis-sons-edat-mitjana.json` conté els 130 programes complets (de `api.3cat.cat/audios?programaradio_id=1722`; les seccions soltes no s'hi inclouen). `data_historica` assignada a mà programa per programa; 10 temes contemporanis queden com a "Variable".

### Institut d'Humanitats de Barcelona

No és un podcast: són les sessions en vídeo i àudio de l'[arxiu de l'Institut d'Humanitats de Barcelona](https://www.instituthumanitats.org/ca/arxiu), filtrades per les temàtiques arquitectura, art, cinema i audiovisuals, ciutat i espai públic, ciència, filosofia, història, literatura, música, política i religió.

`sessions-institut-humanitats.json` conté 803 sessions (407 vídeos, 396 àudios; 376 amb àudio reproduïble) amb títol, curs, ponents, data de la sessió, sinopsi del curs (escurçada) i enllaç a la fitxa de l'IH. Les 3 sessions publicades en tots dos formats només hi són en vídeo. El camp `data_historica` l'ha assignat Claude a partir del títol de cada sessió (el tema que tracta, no quan es va fer); 72 queden com a `Variable`.

**Regenerar**: `python3 scripts/ih-llista.py "<URL de l'arxiu filtrat>" llista.json` (68 pàgines; l'IH limita les peticions, l'script fa pauses i reintents) i `python3 scripts/ih-cursos.py llista.json cursos.json` per a les sinopsis. Les dates s'han d'assignar a mà abans de desplegar.

## Funcionalitats

- Cronologia interactiva ordenada per període històric
- Navegació per èpoques: Prehistòria, Antiguitat, Edat Mitjana, Edat Moderna, Edat Contemporània; cada època es pot plegar i desplegar (l'estat es recorda al navegador)
- Filtre per font (A les Portes de Troia, En Guàrdia, Sons de l'edat mitjana, Institut d'Humanitats)
- Cerca en temps real per títol, descripció, ubicació, curs i ponents
- Expansió de cada capítol amb descripció i enllaç a la font
- Reproductor d'àudio integrat (un sol `<audio>` natiu, sense llibreries): ±15/30 s, velocitat, recorda la posició de cada capítol, passa al següent en ordre cronològic i s'integra amb els controls del sistema (Media Session)

## Àudio

- **A les Portes de Troia** i **Institut d'Humanitats** (sessions en àudio): camp `ivoox` (id d'episodi iVoox) → `https://www.ivoox.com/listen_mn_<id>_1.mp3`. Es genera amb `python3 scripts/ivoox-ids.py [pdt] [ih]` (PdT des del feed iVoox per número d'episodi; IH des de l'iframe de cada fitxa, amb pauses). Cal tornar-lo a executar quan s'afegeixin episodis nous.
- **En Guàrdia** i **Sons de l'edat mitjana**: no cal cap camp nou; l'URL del MP3 es resol en reproduir via `api-media.3cat.cat/pvideo/media.jsp?media=audio&idint=<id_3cat>` (CORS obert).

## Execució local

```bash
python3 -m http.server 8080
# → http://localhost:8080
```

## Desplegament

Cloudflare Pages → `historia.allr.cat`

## Llicència

El codi (`index.html` i `scripts/`) és programari lliure sota la llicència [GNU AGPL-3.0](LICENSE): el pots usar, estudiar, modificar i compartir, sempre que qualsevol versió derivada, també si s'ofereix com a web, es publiqui amb la mateixa llicència i amb el codi obert.

Els títols, descripcions i àudios dels episodis són de les persones i entitats que fan els pòdcasts (3Cat, A les Portes de Troia, Institut d'Humanitats de Barcelona); aquí només s'endrecen i s'hi enllaça. L'aquarel·la de la capçalera (Préaulx, 1814, Rijksmuseum) és de domini públic.
