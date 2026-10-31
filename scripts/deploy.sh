#!/bin/sh
# Publica a Cloudflare Pages només els fitxers que fa servir la web (sense metadades, scripts ni README).
# Ús: scripts/deploy.sh            (producció)
#     scripts/deploy.sh --branch=prova   (vista prèvia, no toca historia.allr.cat)
set -e
cd "$(dirname "$0")/.."
OUT=$(mktemp -d)
trap 'rm -rf "$OUT"' EXIT
cp index.html avis-legal.html og-image.jpg preaulx-cisterna.webp episodis-*.json sessions-*.json "$OUT"
cp -R fonts img "$OUT"
# functions/ es llegeix des d'aquí (directori de treball), no des de $OUT
npx wrangler pages deploy "$OUT" --project-name=portes-de-troia --commit-dirty=true "$@"
