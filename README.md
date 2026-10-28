# Història en Podcasts

Episodis de podcasts d'història en català endreçats en ordre cronològic. Disponible a [historia.allr.cat](https://historia.allr.cat).

## Podcasts

### A les Portes de Troia

[A les Portes de Troia](https://www.portesdetroia.cat) és un podcast d'història en català, emès des de Ràdio Castellar i distribuït per La Xarxa. Des del 2013, Alberto Reche, Sergio Rodríguez i Albert Abril expliquen el passat en present: batalles, revolucions, personatges i civilitzacions.

`episodis-portes-de-troia.json` (producció) conté 555 episodis (ep. 1–557; títols i àudios verificats amb l'àudio, octubre 2026) amb títol, data/període històric, descripció i enllaç (portesdetroia.cat per ep. 68–548, iVoox per ep. 1–67 i 549+). **100% complet**: cap camp buit. `episodis.json` és una variant antiga sense el camp `podcast`, ja no s'usa a producció.

### En Guàrdia

[En Guàrdia](https://www.3cat.cat/3cat/en-guardia/) és el programa d'història de Catalunya Ràdio, dirigit i presentat per Enric Calpena, amb l'historiador Josep Maria Solé i Sabaté.

`episodis-en-guardia.json` conté 1314 episodis (sense promocions ni reemissions duplicades), gairebé tots amb descripció i any històric assignat. Uns 300 episodis antics no tenen la sinopsi original disponible enlloc (ni a 3cat.cat ni a iVoox ni a Wayback Machine); se'ls ha escrit una nota factual breu i un any a partir del títol. Només 16 episodis (temes massa genèrics: "La sardana", "Eurovisió"...) queden sense any assignat, i 2 sense cap descripció.

**Actualitzar amb episodis nous**: `python3 scripts/sync-en-guardia.py --write` — llegeix el feed RSS del podcast, detecta els episodis nous i en resol l'enllaç via el cercador de 3cat.cat. Cal assignar manualment `data_historica` als episodis nous (llegint la descripció) abans de desplegar.

### Sons de l'edat mitjana

[Sons de l'edat mitjana](https://www.3cat.cat/3cat/sons-edat-mitjana/) és el programa de Catalunya Música sobre la música i la història medievals, presentat per Maria Montes (2016-2019, acabat).

`episodis-sons-edat-mitjana.json` conté els 130 programes complets (de `api.3cat.cat/audios?programaradio_id=1722`; les seccions soltes no s'hi inclouen). `data_historica` assignada a mà programa per programa; 10 temes contemporanis queden com a "Variable".

### Arxiu de la Paraula de l'Ateneu Barcelonès

Conferències de l'[Arxiu de la Paraula](http://arxiudigital.ateneubcn.cat/) de l'Ateneu Barcelonès (des del 1973, llicència CC BY-NC-ND), filtrades a mà: només les que tenen una temporalitat històrica identificable (fets, períodes, persones mortes de les quals es repassa la vida o l'obra, art, literatura o pensament d'una època). Fora l'actualitat del moment, els premis, els recitals i les sessions en castellà. Criteri a `historia-pendents/ateneu/CRITERI.md` (fora del repo).

`sessions-ateneu.json` conté 1152 sessions (802 àudios, 349 vídeos de YouTube) amb títol, ponents, any de la conferència, durada, descripció i enllaç a la fitxa. Es genera amb `python3 scripts/ateneu.py items.json seleccio.json` (fitxes extretes de `/items/browse?output=omeka-json`; l'API d'Omeka està desactivada). **Després cal tornar a passar `scripts/metadades-fusiona.py`**, que hi afegeix les metadades (claus `at:N` per posició).

L'arxiu només té HTTP: els MP3 es serveixen per `functions/ateneu/[file].js` (Cloudflare Pages Function), que passa les peticions (amb `Range`) a `arxiudigital.ateneubcn.cat`. Alguns vídeos estan mal enllaçats a l'arxiu (comprovat amb l'oEmbed de YouTube): `VIDEO_ERRONI` a l'script.

### Institut d'Humanitats de Barcelona

No és un podcast: són les sessions en vídeo i àudio de l'[arxiu de l'Institut d'Humanitats de Barcelona](https://www.instituthumanitats.org/ca/arxiu), filtrades per les temàtiques arquitectura, art, cinema i audiovisuals, ciutat i espai públic, ciència, filosofia, història, literatura, música, política i religió.

`sessions-institut-humanitats.json` conté 803 sessions (407 vídeos, 396 àudios; 376 amb àudio reproduïble) amb títol, curs, ponents, data de la sessió, sinopsi del curs (escurçada) i enllaç a la fitxa de l'IH. Les 3 sessions publicades en tots dos formats només hi són en vídeo. El camp `data_historica` l'ha assignat Claude a partir del títol de cada sessió (el tema que tracta, no quan es va fer); 72 queden com a `Variable`.

**Regenerar**: `python3 scripts/ih-llista.py "<URL de l'arxiu filtrat>" llista.json` (68 pàgines; l'IH limita les peticions, l'script fa pauses i reintents) i `python3 scripts/ih-cursos.py llista.json cursos.json` per a les sinopsis. Les dates s'han d'assignar a mà abans de desplegar.

## Funcionalitats

- Cronologia interactiva ordenada per període històric
- Llista agrupada per èpoques (Prehistòria, Antiguitat, Edat Mitjana, Edat Moderna, Edat Contemporània); cada època es pot plegar i desplegar, o totes alhora (l'estat es recorda al navegador)
- Filtre per font (En Guàrdia, Ateneu Barcelonès, Institut d'Humanitats, A les Portes de Troia, Sons de l'edat mitjana; ordenades per nombre de programes); se'n poden combinar diverses
- Filtre «Catalunya» (episodis d'història de Catalunya) i filtres plegables per tema, regió i tipus de relat; botó per esborrar-los tots
- Mapa dels episodis geolocalitzats (Leaflet + OpenStreetMap, es carrega només en obrir-lo)
- Etiquetes clicables de lloc, tema, personatges, esdeveniments i pobles (amb Wikidata) per trobar episodis relacionats entre pòdcasts
- Cerca en temps real per títol, descripció, ubicació, curs, ponents, personatges, llocs i convidats
- Expansió de cada capítol amb descripció i enllaç a la font
- Reproductor d'àudio integrat (un sol `<audio>` natiu, sense llibreries): ±15/30 s, velocitat, recorda la posició de cada capítol, passa al següent en ordre cronològic i s'integra amb els controls del sistema (Media Session)

## Metadades

Cada episodi porta camps extrets del títol i la descripció (temàtiques, països, regions, lloc amb coordenades, àmbit català, període, segles, personatges i esdeveniments amb Wikidata, civilitzacions, tipus de relat, convidats, sèrie, idioma). El vocabulari i el procés són a `metadades/VOCABULARI.md`; les incidències de dades, a `metadades/incidencies.txt`.

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

Els títols, descripcions i àudios dels episodis són de les persones i entitats que fan els pòdcasts (3Cat, A les Portes de Troia, Institut d'Humanitats de Barcelona, Ateneu Barcelonès); aquí només s'endrecen i s'hi enllaça. L'aquarel·la de la capçalera (Préaulx, 1814, Rijksmuseum) és de domini públic.
