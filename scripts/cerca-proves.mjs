// Bateria de proves del cercador (cerca.js). Ús: node scripts/cerca-proves.mjs [-v]
// Cada prova: q (consulta), mode («filtra» com el web mentre s'escriu, o «cerca» com el MCP),
// inclou (títols que hi han de sortir; a «cerca», dins dels primers «top»), exclou (títols que no),
// min / max (nombre de resultats).
import { readFileSync } from 'node:fs';
import { creaMotor } from '../cerca.js';

const D = new URL('..', import.meta.url).pathname;
const json = f => JSON.parse(readFileSync(D + f, 'utf8'));
const eps = ['episodis-portes-de-troia.json', 'episodis-en-guardia.json', 'episodis-sons-edat-mitjana.json',
  'sessions-institut-humanitats.json', 'sessions-ateneu.json'].flatMap(json);
const t0 = performance.now();
const motor = creaMotor(eps, json('alies.json'));
const tIndex = performance.now() - t0;

const PROVES = [
  // Paraules senceres i per arrel
  { q: 'vic', mode: 'cerca', inclou: ["Ato de Vic"], exclou: ['víctimes', 'Victòria'], max: 40 },
  { q: 'anibal', mode: 'cerca', inclou: ['Aníbal A Itàlia'], exclou: ['canibalisme'], top: 3 },
  { q: 'roma', mode: 'cerca', exclou: ['romanticisme', 'Romanticisme'] },
  { q: 'ibers', mode: 'cerca', inclou: ['19 - Els ibers', 'període ibèric', 'Catalunya Íbera'], top: 10 },
  { q: 'templers', mode: 'cerca', inclou: ['Templers A Catalunya'], top: 3 },
  { q: 'dones', mode: 'cerca', min: 50 },
  // Institucions dels convidats
  { q: 'girona', mode: 'cerca', max: 50, inclou: ['Girona medieval'] },
  { q: 'llull', mode: 'cerca', inclou: ['Ramon Llull'], max: 15 },
  { q: 'universitat de cervera', mode: 'cerca', inclou: ['Universitat De Cervera'], top: 3 },
  // Noms alternatius i QID (Wikidata)
  { q: 'tòquio', mode: 'cerca', inclou: ['Shogunat Tokugawa', 'aïllament del shogunat'] },
  { q: 'edo', mode: 'cerca', inclou: ['Shogunat Tokugawa'] },
  { q: 'Q1490', mode: 'cerca', inclou: ['revolució Meiji'] },
  { q: 'bonaparte', mode: 'cerca', min: 5 },
  { q: 'bizanci', mode: 'cerca', min: 3 },
  // Errors d'escriptura
  { q: 'anibbal', mode: 'cerca', inclou: ['Aníbal A Itàlia'], top: 5 },
  { q: 'carlemanu', mode: 'cerca', min: 1 },
  // Diverses paraules i frases
  { q: 'guerra civil', mode: 'cerca', inclou: ['Guerra Civil'], top: 3 },
  { q: 'guerra successio', mode: 'cerca', inclou: ['Guerra de Successió'], top: 5 },
  { q: 'carles II', mode: 'cerca', exclou: ['Carles III'], top: 5 },
  { q: '1714', mode: 'cerca', min: 10 },
  // Web: mentre s'escriu, la darrera paraula també per inici
  { q: 'barc', mode: 'filtra', min: 500 },
  { q: 'guerra civ', mode: 'filtra', min: 100 },
  { q: 'templers ', mode: 'filtra', max: 15 },
  { q: 'templ', mode: 'filtra', inclou: ['Templers A Catalunya'] },
  { q: 'vic', mode: 'filtra', exclou: ['víctimes', 'Victòria'], max: 40 },
  { q: 'napo', mode: 'filtra', inclou: ['Napoleó Envaeix Rússia'] },
  { q: '388', mode: 'filtra', min: 1 },
  // La ç: «Barça» no és «Aníbal Barca»; «barca» sense ç troba totes dues coses
  { q: 'Barça', mode: 'filtra', inclou: ['El Barça de Johan Cruyff'], exclou: ['Aníbal', 'Cannes', 'Calderón'] },
  { q: 'Barça', mode: 'cerca', inclou: ['El Barça de Johan Cruyff'], exclou: ['Aníbal', 'Cannes', 'Calderón'] },
  { q: 'barca', mode: 'cerca', inclou: ['El Barça de Johan Cruyff', 'Calderón de la Barca'] },
  { q: 'Barç', mode: 'filtra', exclou: ['Cannes'] },
];

const v = process.argv.includes('-v');
let ko = 0;
for (const p of PROVES) {
  const t = performance.now();
  let titols;
  if (p.mode === 'filtra') titols = [...(motor.filtra(p.q) || [])].map(i => eps[i].titol);
  else titols = motor.cerca(p.q).resultats.map(r => eps[r.i].titol);
  const ms = performance.now() - t;
  const errs = [];
  const finestra = p.top ? titols.slice(0, p.top) : titols;
  for (const s of p.inclou || []) if (!finestra.some(x => x.includes(s))) errs.push(`hi falta «${s}»${p.top ? ` als ${p.top} primers` : ''}`);
  for (const s of p.exclou || []) { const x = titols.find(x => x.includes(s)); if (x) errs.push(`no hi hauria de ser «${x}»`); }
  if (p.min && titols.length < p.min) errs.push(`només ${titols.length} (mínim ${p.min})`);
  if (p.max && titols.length > p.max) errs.push(`${titols.length} (màxim ${p.max})`);
  if (errs.length) ko++;
  console.log(`${errs.length ? 'KO' : 'ok'}  ${p.mode.padEnd(6)} ${JSON.stringify(p.q).padEnd(26)} ${String(titols.length).padStart(4)}  ${ms.toFixed(1)} ms  ${errs.join('; ')}`);
  if (v || errs.length) console.log('      ', titols.slice(0, 5).join(' | '));
}
console.log(`\n${PROVES.length - ko}/${PROVES.length} correctes · índex: ${motor.mida} arrels en ${tIndex.toFixed(0)} ms`);
process.exit(ko ? 1 : 0);
