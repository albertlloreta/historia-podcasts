// Motor de cerca compartit pel web (index.html) i pel servidor MCP (functions/mcp.js).
// Sense dependències. Un índex invertit de paraules (per arrel) amb tres usos:
//  - filtra(): conjunt de capítols que contenen totes les paraules (el web; la darrera
//    paraula també per inici, perquè vagi filtrant mentre s'escriu)
//  - cerca(): els mateixos capítols ordenats per rellevància (BM25), per al MCP
// Proves: node scripts/cerca-proves.mjs

// Minúscules i sense accents, però la ç es manté: «Barça» no és «Aníbal Barca»
export const norm = t => String(t ?? '').normalize('NFD').replace(/[\u0300-\u0326\u0328-\u036f]/g, '').normalize('NFC').toLowerCase();
// Sense ç: qui escriu «barca» troba també «Barça»
const plega = w => w.replace(/ç/g, 'c');

// «ibers», «ibèric», «íbera» → «iber»; «roma», «romans», «romana» → «rom»; «vic» ≠ «víctimes»
export const arrel = w => {
  const s = w.replace(/(iques|ics|ica|ic|ianes|ians|iana|ia|anes|ans|ana|es|s|a|e)$/, '');
  return s.length >= 3 ? s : w;
};

const BUIDES = new Set(('a al als amb aquest aquesta com d de del dels el els en entre es i l la les lo los ' +
  'o per que qui s se sobre the of and un una uns unes y').split(' '));

// Expressions que no s'han de partir: «península Ibèrica» no és dels ibers
const COMPOSTOS = [[/peninsula iberica/g, 'peninsulaiberica']];
const paraules = t => {
  let n = norm(t);
  for (const [re, x] of COMPOSTOS) n = n.replace(re, x);
  return n.split(/[^a-z0-9·ç]+/).filter(w => w && !BUIDES.has(w));
};

// Institucions amb nom de persona («Llull» no ha de trobar la Universitat Ramon Llull)
const INSTITUCIONS = /(Universitat|Institut|Fundació(?: Universitària)?|Museu|Biblioteca|Escola|Col·legi|Casa) (Ramon Llull|Pompeu Fabra|Rovira i Virgili|Jaume I|Ramon Muntaner|Martí l'Humà|Pere Mata|Josep Irla|Rafael Campalans|Carles Pi i Sunyer|Ramon Trias Fargas|Joan Maragall|Abat Oliba(?: CEU)?|Francesc Macià|Josep Pallach)/g;
// I on treballen els convidats («Girona» no ha de trobar cada professora de la UdG).
// El títol es cerca sencer: un capítol sobre la Universitat de Cervera es continua trobant.
const AFILIACIONS = /(?:Universitat|Facultat|Departament|Institut|Museu|Arxiu|Fundació|Biblioteca|Centre|Reial Acadèmia|Acadèmia|Grup|Càtedra|Escola Superior|Editorial|Edicions|Ateneu|Servei|Consorci|Associació|Col·legi Oficial|Hospital|Agència)(?:\s(?:de|d['’]|del|dels|de la|de les|i|per a la|La)?\s?(?:\p{Lu}[\p{L}·'’-]+|UB|UAB|UPF|UdG|UdL|URV|UOC|CSIC))+/gu;
export const senseInstitucions = t => (t ? t.replace(INSTITUCIONS, ' ').replace(AFILIACIONS, ' ') : '');

// Camps i pes: títol > personatges i llocs > noms alternatius (Wikidata) > la resta
const CAMPS = [
  [3, e => [e.titol]],
  [2, e => [...(e.personatges || []), ...(e.esdeveniments || [])].map(p => p.nom)
    .concat(e.civilitzacions || [], e.lloc?.nom, e.serie, e.curs)],
  [1.5, (e, alies) => [...(e.personatges || []), ...(e.esdeveniments || []), e.lloc || {}]
    .filter(p => p.qid).flatMap(p => [p.qid, ...(alies[p.qid] || [])])],
  [1, e => [senseInstitucions(e.descripcio), e.ubicacio, e.data_historica, e.num, e.tema_ateneu,
    ...(e.ponents || []), ...(e.convidats || [])]],
];

// Distància d'edició (amb transposicions) limitada: retorna max + 1 si la supera
function distancia(a, b, max) {
  if (Math.abs(a.length - b.length) > max) return max + 1;
  let prev2 = null, prev = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    let min = i;
    for (let j = 1; j <= b.length; j++) {
      let v = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      if (prev2 && i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) v = Math.min(v, prev2[j - 2] + 1);
      cur.push(v);
      if (v < min) min = v;
    }
    if (min > max) return max + 1;
    prev2 = prev; prev = cur;
  }
  return prev[b.length];
}

export function creaMotor(episodis, alies = {}) {
  const N = episodis.length;
  const index = new Map();          // arrel → Map(capítol → freqüència ponderada)
  const llargada = new Float32Array(N);
  const textos = new Array(N);      // títol + descripció normalitzats, per a les frases exactes

  episodis.forEach((e, i) => {
    let ll = 0;
    for (const [pes, camp] of CAMPS) {
      for (const valor of camp(e, alies)) {
        if (valor == null || valor === '') continue;
        for (const w of paraules(valor)) {
          const a = arrel(w);
          let p = index.get(a);
          if (!p) index.set(a, (p = new Map()));
          p.set(i, (p.get(i) || 0) + pes);
          ll += pes;
        }
      }
    }
    llargada[i] = ll;
    textos[i] = ' ' + norm(`${e.titol} ${senseInstitucions(e.descripcio)}`).replace(/[^a-z0-9·ç]+/g, ' ') + ' ';
  });

  const vocab = [...index.keys()].sort();
  // Les mateixes arrels sense ç («barc» → barc, barç)
  const plecs = new Map();
  for (const t of vocab) { const k = plega(t); plecs.has(k) ? plecs.get(k).push(t) : plecs.set(k, [t]); }
  const vocabPlec = [...plecs.keys()].sort();
  const mitjana = llargada.reduce((s, x) => s + x, 0) / (N || 1);

  function perInici(pre) {
    const v = pre.includes('ç') ? vocab : vocabPlec;
    let lo = 0, hi = v.length;
    while (lo < hi) { const m = (lo + hi) >> 1; if (v[m] < pre) lo = m + 1; else hi = m; }
    const out = [];
    for (let k = lo; k < v.length && v[k].startsWith(pre); k++) out.push(...(v === vocab ? [v[k]] : plecs.get(v[k])));
    return out;
  }
  // Amb ç, només aquella paraula; sense, també les que la porten
  const exactes = a => (a.includes('ç') ? (index.has(a) ? [a] : []) : plecs.get(a) || []);

  // Si una paraula no existeix, les més semblants (Aníbbal → Aníbal). Només paraules llargues.
  function semblants(a) {
    if (a.length < 5) return [];
    const max = a.length >= 9 ? 2 : 1;
    const p = plega(a);
    return vocabPlec.filter(v => v[0] === p[0] && distancia(p, v, max) <= max).flatMap(v => plecs.get(v));
  }

  // Arrels candidates per a cada paraula de la consulta: [{termes, exacte}]
  function analitza(text, inici) {
    let ws = paraules(text);
    if (!ws.length) ws = norm(text).split(/[^a-z0-9·ç]+/).filter(Boolean);
    const obert = inici && !/\s$/.test(text);
    return ws.map((w, k) => {
      const a = arrel(w);
      const termes = new Set(exactes(a));
      // Mentre s'escriu, la darrera paraula també per inici: a partir de 4 lletres o quan
      // ja n'hi ha una altra davant («templ» → templers, «guerra civ» → civil;
      // «vic» sol es queda en Vic i no troba «víctimes»)
      if (obert && k === ws.length - 1 && (w.length >= 4 || k > 0)) for (const t of perInici(w)) termes.add(t);
      if (termes.size) return { termes: [...termes], exacte: true };
      return { termes: semblants(a), exacte: false };
    });
  }

  function conjunt(termes) {
    const s = new Set();
    for (const t of termes) for (const i of index.get(t).keys()) s.add(i);
    return s;
  }

  // Web: capítols que contenen totes les paraules (null = no hi ha res a cercar)
  function filtra(text, { inici = true } = {}) {
    const q = analitza(text, inici);
    if (!q.length) return null;
    const sets = q.map(x => conjunt(x.termes)).sort((a, b) => a.size - b.size);
    const [primer, ...resta] = sets;
    const out = new Set();
    for (const i of primer) if (resta.every(s => s.has(i))) out.add(i);
    return out;
  }

  // MCP: els mateixos capítols, ordenats per rellevància. Si cap capítol té totes les paraules,
  // retorna els que en tenen alguna (parcial: true).
  function cerca(text) {
    const q = analitza(text, false);
    if (!q.length) return { resultats: [], parcial: false };
    const k1 = 1.2, b = 0.75;
    const punts = new Map(), quantes = new Map();
    for (const { termes, exacte } of q) {
      const vist = new Map();
      for (const t of termes) {
        const p = index.get(t);
        const idf = Math.log(1 + (N - p.size + 0.5) / (p.size + 0.5));
        for (const [i, tf] of p) {
          const s = idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * llargada[i] / mitjana)) * (exacte ? 1 : 0.6);
          if (s > (vist.get(i) || 0)) vist.set(i, s);
        }
      }
      for (const [i, s] of vist) { punts.set(i, (punts.get(i) || 0) + s); quantes.set(i, (quantes.get(i) || 0) + 1); }
    }
    const totes = [...punts.keys()].filter(i => quantes.get(i) === q.length);
    const parcial = !totes.length;
    const ids = parcial ? [...punts.keys()] : totes;
    // Frase exacta («guerra civil» seguides) puja
    const frase = ws => ' ' + ws.join(' ') + ' ';
    const f = q.length > 1 ? frase(norm(text).split(/[^a-z0-9·ç]+/).filter(Boolean)) : null;
    const res = ids.map(i => ({ i, punts: punts.get(i) * (f && textos[i].includes(f) ? 1.5 : 1) * (parcial ? quantes.get(i) / q.length : 1) }));
    res.sort((x, y) => y.punts - x.punts || x.i - y.i);
    return { resultats: res, parcial };
  }

  return { filtra, cerca, mida: vocab.length };
}
