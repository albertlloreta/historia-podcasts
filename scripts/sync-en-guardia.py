#!/usr/bin/env python3
"""Sincronitza episodis nous del podcast En Guàrdia (Catalunya Ràdio) a episodis-en-guardia.json.

Font 1: feed RSS del podcast (últims ~350 episodis, amb descripció completa)
  https://dinamics.3cat.cat/public/podcast/catradio/xml/4/4/podprograma944.xml
Font 2: cercador de 3cat.cat, per resoldre id_3cat/enllaç a partir del títol
  https://www.3cat.cat/cercador/?text=<títol>

No cal scroll ni cap API interna: cada episodi nou es localitza per títol.

Ús:
  python3 scripts/sync-en-guardia.py            # mostra els episodis nous trobats (dry-run)
  python3 scripts/sync-en-guardia.py --write     # els afegeix a episodis-en-guardia.json

Nota: el camp `data_historica` es deixa a null als nous episodis — cal
assignar-lo manualment (llegint la descripció) abans de publicar, o deixar-lo
buit (la UI el classifica com "Data desconeguda").
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request

FEED_URL = "https://dinamics.3cat.cat/public/podcast/catradio/xml/4/4/podprograma944.xml"
SEARCH_URL = "https://www.3cat.cat/cercador/?text={}"
JSON_PATH = "episodis-en-guardia.json"
UA = "Mozilla/5.0"


def fetch(url, encoding="utf-8"):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode(encoding, errors="replace")


def parse_feed():
    xml = fetch(FEED_URL, encoding="iso-8859-1")
    items = re.findall(r"<item>(.*?)</item>", xml, re.S)
    out = []
    for it in items:
        titol = re.search(r"<title>(.*?)</title>", it, re.S).group(1).strip()
        desc_m = re.search(r"<description>(.*?)</description>", it, re.S)
        desc = desc_m.group(1).strip() if desc_m else ""
        num_m = re.match(r"Cap[ií]tol\s+(\d+)\.", desc)
        num = int(num_m.group(1)) if num_m else None
        out.append({"titol": titol, "descripcio": desc, "num": num})
    return out


def resolve_link(titol):
    """Retorna (id_3cat, enllac) buscant el títol al cercador de 3cat.cat."""
    url = SEARCH_URL.format(urllib.parse.quote(titol))
    html = fetch(url)
    m = re.search(r'href="(/3cat/[a-z0-9-]+/audio/(\d+)/)"', html)
    if not m:
        return None, None
    path, id_3cat = m.group(1), int(m.group(2))
    return id_3cat, f"https://www.3cat.cat{path}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Escriu els canvis a episodis-en-guardia.json")
    args = ap.parse_args()

    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    max_num = max((e["num"] for e in data if e.get("num") is not None), default=0)
    existing_titles = {e["titol"].strip().lower() for e in data}

    feed_items = parse_feed()
    nous = [
        it for it in feed_items
        if (it["num"] is not None and it["num"] > max_num)
        or (it["num"] is None and it["titol"].strip().lower() not in existing_titles)
    ]
    nous.sort(key=lambda x: (x["num"] is None, x["num"] or 0))

    if not nous:
        print("Cap episodi nou.")
        return

    print(f"{len(nous)} episodis nous trobats (num local màxim: {max_num}):\n")
    afegits = []
    for it in nous:
        id_3cat, enllac = resolve_link(it["titol"])
        status = "OK" if id_3cat else "SENSE ENLLAÇ (cal resoldre a mà)"
        print(f"  {it['num']!s:>5}  {it['titol'][:55]:<55}  {status}")
        afegits.append({
            "podcast": "en-guardia",
            "num": it["num"],
            "id_3cat": id_3cat,
            "titol": it["titol"],
            "data_historica": None,
            "descripcio": it["descripcio"],
            "enllac": enllac,
            "pendent": False,
        })
        time.sleep(0.5)  # no carregar el cercador

    sense_enllac = [a for a in afegits if not a["enllac"]]
    if sense_enllac:
        print(f"\n⚠ {len(sense_enllac)} episodis sense enllaç resolt: cal buscar-los manualment.")

    if args.write:
        data.extend(afegits)
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Escrits {len(afegits)} episodis nous a {JSON_PATH} (total: {len(data)}).")
        print("  Recorda assignar 'data_historica' als nous episodis abans de desplegar.")
    else:
        print("\n(dry-run, no s'ha escrit res — repeteix amb --write per aplicar els canvis)")


if __name__ == "__main__":
    sys.exit(main())
