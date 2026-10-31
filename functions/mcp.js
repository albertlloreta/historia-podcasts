// Servidor MCP (Model Context Protocol) de historia.allr.cat.
// Transport «Streamable HTTP» sense estat: cada POST porta un missatge JSON-RPC
// i la resposta és JSON. Només lectura: cerca dins dels mateixos JSON que fa servir el web.
import pdt from '../episodis-portes-de-troia.json';
import eg from '../episodis-en-guardia.json';
import sons from '../episodis-sons-edat-mitjana.json';
import ih from '../sessions-institut-humanitats.json';
import ateneu from '../sessions-ateneu.json';

const SITE = 'https://historia.allr.cat';
const VERSIONS = ['2025-06-18', '2025-03-26', '2024-11-05'];

const FONTS = {
  'portes-de-troia':     { nom: 'A les Portes de Troia', prefix: 'pdt', clau: 'num' },
  'en-guardia':          { nom: 'En Guàrdia (Catalunya Ràdio)', prefix: 'eg', clau: 'id_3cat' },
  'sons-edat-mitjana':   { nom: "Sons de l'edat mitjana (Catalunya Música)", prefix: 'sons', clau: 'id_3cat' },
  'institut-humanitats': { nom: "Institut d'Humanitats de Barcelona", prefix: 'ih', clau: 'nid' },
  'ateneu':              { nom: 'Ateneu Barcelonès (Arxiu de la Paraula, CC BY-NC-ND)', prefix: 'at', clau: 'nid' },
};

const TEMATIQUES = {
  pol: 'política', gue: 'guerra i conflictes', soc: 'societat', eco: 'economia i treball', rel: 'religió',
  art: 'art', arq: 'arquitectura i urbanisme', lit: 'literatura', mus: 'música', cie: 'ciència i tècnica',
  fil: 'filosofia i pensament', quo: 'vida quotidiana', arqu: 'arqueologia', exp: 'exploracions i viatges',
  gen: 'dones i gènere', cul: 'cultura popular i mitjans', esp: 'esport', his: 'historiografia i memòria',
  dre: 'dret i justícia', med: 'medicina i salut', cin: 'cinema i imatge',
};
const REGIONS = {
  EUS: 'Europa meridional', EUO: 'Europa occidental', EUC: 'Europa central', EUN: 'Europa septentrional',
  EUE: 'Europa oriental', PO: 'Pròxim Orient', NA: "Nord d'Àfrica", AS: 'Àfrica subsahariana',
  ACM: 'Àsia central', ASM: 'Àsia meridional', AO: 'Àsia oriental', SEA: 'Sud-est asiàtic',
  AN: 'Amèrica del Nord', AL: 'Amèrica Llatina', OC: 'Oceania', GLO: 'global',
};
const TIPUS = {
  bio: 'biografia', con: 'conflicte', pro: 'procés polític o social', quo: 'vida quotidiana',
  cul: 'cultura i idees', lloc: "història d'un lloc", deb: 'debat o historiografia',
};

// Text per cercar: minúscules i sense accents («catala» troba «català»)
const norm = t => String(t ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

// "1925" → [1925,1925] · "1098-1179" · "-264-146" (tot aC) · "-49 -48" · "60-61 dC" · "Variable" → null
function parseRange(raw) {
  if (raw == null) return null;
  const s = String(raw).trim();
  const m = s.match(/^(-?\d+)\s*(aC|dC)?(?:\s*[-–]?\s*(-?\d+)\s*(aC|dC)?)?$/i);
  if (!m) {
    const n = s.match(/-?\d+/);
    return n ? [+n[0], +n[0]] : null;
  }
  const ac = x => x && /aC/i.test(x);
  let a = +m[1], b = m[3] != null ? +m[3] : a;
  if (ac(m[2])) a = -Math.abs(a);
  if (ac(m[4])) { b = -Math.abs(b); if (!m[2] && a > 0) a = -a; } // "218-202 aC"
  // "-264-146": el segon nombre és menor que el primer en valor absolut → també és aC
  if (a < 0 && b > 0 && b < -a) b = -b;
  return a <= b ? [a, b] : [b, a];
}

const fmtAny = n => (n < 0 ? `${-n} aC` : n < 1000 ? `${n} dC` : String(n));
const fmtRang = r => (!r ? 'sense data' : r[0] === r[1] ? fmtAny(r[0]) : `${fmtAny(r[0])} – ${fmtAny(r[1])}`);

function audio(e) {
  if (e.mp3) return `${SITE}/ateneu/${e.mp3}.mp3`;
  if (e.ivoox) return `https://www.ivoox.com/listen_mn_${e.ivoox}_1.mp3`;
  return null;
}
function video(e) {
  if (e.youtube) return `https://www.youtube.com/watch?v=${e.youtube}`;
  if (e.vimeo) return `https://vimeo.com/${e.vimeo}`;
  return null;
}

// Índex: es construeix en carregar el mòdul (un cop per instància)
const EPISODIS = [];
const PER_ID = new Map();
for (const llista of [pdt, eg, sons, ih, ateneu]) {
  llista.forEach((e, i) => {
    const f = FONTS[e.podcast];
    if (!f) return;
    const id = `${f.prefix}:${e[f.clau] ?? `p${i}`}`;
    const noms = [...(e.personatges || []), ...(e.esdeveniments || [])].map(p => p.nom);
    const rec = {
      e, id,
      rang: parseRange(e.data_historica),
      tTitol: norm(e.titol),
      tNoms: norm([...noms, ...(e.civilitzacions || []), e.lloc?.nom, e.serie, e.curs].join(' ')),
      tResta: norm([e.descripcio, ...(e.ponents || []), ...(e.convidats || []), e.tema_ateneu].join(' ')),
    };
    EPISODIS.push(rec);
    PER_ID.set(id, rec);
  });
}
EPISODIS.sort((x, y) => (x.rang?.[0] ?? Infinity) - (y.rang?.[0] ?? Infinity));

function fitxa(rec, llarga) {
  const e = rec.e;
  const o = {
    id: rec.id,
    titol: e.titol,
    font: FONTS[e.podcast].nom,
    num: e.num ?? undefined,
    quan: e.data_historica === 'Variable' ? 'sense data específica' : fmtRang(rec.rang),
    descripcio: llarga || !e.descripcio || e.descripcio.length <= 280 ? e.descripcio : e.descripcio.slice(0, 277).trimEnd() + '…',
    personatges: e.personatges?.map(p => p.nom),
    lloc: e.lloc?.nom,
    enllac: e.enllac,
    audio: audio(e) ?? undefined,
    video: video(e) ?? undefined,
  };
  if (llarga) {
    Object.assign(o, {
      esdeveniments: e.esdeveniments?.map(p => p.nom),
      civilitzacions: e.civilitzacions,
      tematiques: e.tematiques?.map(t => TEMATIQUES[t] || t),
      regions: e.regions?.map(r => REGIONS[r] || r),
      paisos: e.paisos,
      tipus: TIPUS[e.tipus] || e.tipus,
      ambit_catala: e.ambit_catala || undefined,
      convidats: e.convidats || e.ponents,
      curs: e.curs, serie: e.serie, durada: e.durada,
      data_emissio: e.data_emissio || e.data_sessio || undefined,
      idioma: e.idioma,
      wikidata: [...(e.personatges || []), ...(e.esdeveniments || [])].filter(p => p.qid).map(p => `${p.nom}: ${p.qid}`),
      llicencia: e.podcast === 'ateneu' ? 'CC BY-NC-ND, Ateneu Barcelonès' : undefined,
    });
    if (!o.audio && e.id_3cat) o.audio_api = `https://api-media.3cat.cat/pvideo/media.jsp?media=audio&idint=${e.id_3cat}`;
  }
  return o;
}

function cerca(a) {
  // Cada paraula ha de coincidir a l'inici d'un mot («anibal» no troba «canibalisme»)
  // i es treu la terminació («ibers», «iberic», «ibera» → «iber»)
  const arrel = m => (m.length < 5 ? m : m.replace(/(iques|ics|ica|ic|es|s|a)$/, ''));
  const mots = norm(a.text).split(/[^a-z0-9·]+/).filter(m => m.length > 1).map(m => (arrel(m).length >= 4 ? arrel(m) : m))
    .map(m => new RegExp(`(^|[^a-z0-9·])${m.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`));
  const fonts = a.fonts?.length ? new Set(a.fonts) : null;
  const des = Number.isFinite(a.des_de) ? a.des_de : null;
  const fins = Number.isFinite(a.fins_a) ? a.fins_a : null;
  const pers = a.personatge ? norm(a.personatge) : null;
  const limit = Math.min(Math.max(a.limit ?? 20, 1), 50);
  const offset = Math.max(a.offset ?? 0, 0);

  const res = [];
  for (const rec of EPISODIS) {
    const e = rec.e;
    if (fonts && !fonts.has(e.podcast)) continue;
    if (des != null || fins != null) {
      if (!rec.rang) continue;
      if (des != null && rec.rang[1] < des) continue;
      if (fins != null && rec.rang[0] > fins) continue;
    }
    if (a.tematica && !e.tematiques?.includes(a.tematica)) continue;
    if (a.regio && !e.regions?.includes(a.regio)) continue;
    if (a.pais && !e.paisos?.includes(a.pais.toUpperCase())) continue;
    if (a.tipus && e.tipus !== a.tipus) continue;
    if (a.ambit_catala && !e.ambit_catala) continue;
    if (pers && !rec.tNoms.includes(pers)) continue;
    let punts = 0;
    for (const m of mots) {
      const p = (m.test(rec.tTitol) ? 4 : 0) + (m.test(rec.tNoms) ? 3 : 0) + (m.test(rec.tResta) ? 1 : 0);
      if (!p) { punts = -1; break; }
      punts += p;
    }
    if (punts < 0) continue;
    // Quina part del capítol cau dins del període demanat (1 = tot)
    let ajust = 1;
    if (rec.rang && (des != null || fins != null)) {
      const ini = Math.max(rec.rang[0], des ?? -Infinity), fi = Math.min(rec.rang[1], fins ?? Infinity);
      ajust = (fi - ini + 1) / (rec.rang[1] - rec.rang[0] + 1);
    }
    res.push({ rec, punts: punts * (0.5 + ajust / 2), ajust });
  }
  const anys = des != null || fins != null;
  const ordre = a.ordre || (mots.length ? 'rellevancia' : anys ? 'ajust' : 'cronologic');
  // sort és estable: dins del mateix pes, queda l'ordre cronològic
  if (ordre === 'rellevancia') res.sort((x, y) => y.punts - x.punts);
  if (ordre === 'ajust') res.sort((x, y) => y.ajust - x.ajust);
  return {
    total: res.length,
    mostrats: `${Math.min(offset + 1, res.length)}-${Math.min(offset + limit, res.length)}`,
    ordre,
    resultats: res.slice(offset, offset + limit).map(r => fitxa(r.rec, false)),
  };
}

function fonts() {
  const n = {};
  for (const r of EPISODIS) n[r.e.podcast] = (n[r.e.podcast] || 0) + 1;
  return {
    total: EPISODIS.length,
    web: SITE,
    fonts: Object.entries(FONTS).map(([id, f]) => ({ id, nom: f.nom, prefix_id: f.prefix, capitols: n[id] || 0 })),
    tematiques: TEMATIQUES, regions: REGIONS, tipus: TIPUS,
    nota: "Anys negatius = aC. Els capítols sense data concreta («Variable») queden fora dels filtres d'anys.",
  };
}

const TOOLS = [
  {
    name: 'cerca',
    title: 'Cerca capítols',
    description: "Cerca entre gairebé 4.000 capítols de pòdcasts i conferències d'història en català (A les Portes de Troia, En Guàrdia, Sons de l'edat mitjana, Institut d'Humanitats, Ateneu Barcelonès). Filtra per text, període històric (anys; negatius = aC), font, temàtica, regió, país o personatge. Sense text, retorna els capítols en ordre cronològic de la història que expliquen. Escriu el text en català.",
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Paraules a cercar (títol, descripció, personatges, llocs, ponents). Totes han de sortir-hi. Sense accents també funciona.' },
        des_de: { type: 'integer', description: "Any inicial del període històric que tracta el capítol (negatiu = aC). Ex.: -218" },
        fins_a: { type: 'integer', description: 'Any final del període (negatiu = aC). Ex.: -201' },
        fonts: { type: 'array', items: { type: 'string', enum: Object.keys(FONTS) }, description: 'Limita a aquestes fonts.' },
        tematica: { type: 'string', enum: Object.keys(TEMATIQUES), description: 'Codi de temàtica (vegeu l’eina «fonts»).' },
        regio: { type: 'string', enum: Object.keys(REGIONS), description: 'Codi de regió del món.' },
        pais: { type: 'string', description: "Codi ISO 3166-1 alfa-2 de l'estat actual on passa la història (Catalunya = ES)." },
        tipus: { type: 'string', enum: Object.keys(TIPUS) },
        ambit_catala: { type: 'boolean', description: 'Només capítols d’àmbit català (Països Catalans o catalans a fora).' },
        personatge: { type: 'string', description: 'Personatge, esdeveniment, civilització o lloc etiquetat (coincidència parcial).' },
        ordre: { type: 'string', enum: ['rellevancia', 'cronologic', 'ajust'], description: "Per defecte: rellevància si hi ha text; si només hi ha anys, «ajust» (primer els capítols que cauen sencers dins del període); si no, cronològic." },
        limit: { type: 'integer', minimum: 1, maximum: 50, default: 20 },
        offset: { type: 'integer', minimum: 0, default: 0, description: 'Per paginar.' },
      },
    },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
  {
    name: 'capitol',
    title: 'Fitxa d’un capítol',
    description: 'Retorna la fitxa completa d’un capítol (descripció sencera, metadades, convidats, Wikidata, enllaç i àudio) a partir del seu id (p. ex. «pdt:12», «eg:1258680», «at:17»).',
    inputSchema: {
      type: 'object',
      properties: { id: { type: 'string', description: 'Id retornat per «cerca».' } },
      required: ['id'],
    },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
  {
    name: 'fonts',
    title: 'Fonts i vocabulari',
    description: 'Llista les fonts (pòdcasts i arxius) amb el nombre de capítols, i els codis de temàtica, regió i tipus que accepta «cerca».',
    inputSchema: { type: 'object', properties: {} },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
];

function crida(nom, args = {}) {
  if (nom === 'cerca') return cerca(args);
  if (nom === 'fonts') return fonts();
  if (nom === 'capitol') {
    const rec = PER_ID.get(String(args.id || '').trim());
    if (!rec) throw new Error(`No hi ha cap capítol amb id «${args.id}». Fes servir els id que retorna «cerca».`);
    return fitxa(rec, true);
  }
  throw new Error(`Eina desconeguda: ${nom}`);
}

function gestiona(msg) {
  const { id, method, params } = msg || {};
  const ok = result => ({ jsonrpc: '2.0', id, result });
  const ko = (code, message) => ({ jsonrpc: '2.0', id: id ?? null, error: { code, message } });
  if (!msg || msg.jsonrpc !== '2.0' || typeof method !== 'string') return ko(-32600, 'Petició invàlida');
  if (id === undefined) return null; // notificació (p. ex. notifications/initialized)

  switch (method) {
    case 'initialize': {
      const v = VERSIONS.includes(params?.protocolVersion) ? params.protocolVersion : VERSIONS[0];
      return ok({
        protocolVersion: v,
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: 'historia-allr-cat', title: 'Història en pòdcasts', version: '1.0.0', websiteUrl: SITE },
        instructions: "Índex de capítols de pòdcasts i conferències d'història en català, ordenats per l'època que expliquen. Fes servir «cerca» (amb text i/o anys) i «capitol» per a la fitxa completa. Cita sempre l'enllaç del capítol. Els anys negatius són aC.",
      });
    }
    case 'ping': return ok({});
    case 'tools/list': return ok({ tools: TOOLS });
    case 'resources/list': return ok({ resources: [] });
    case 'prompts/list': return ok({ prompts: [] });
    case 'tools/call':
      try {
        const r = crida(params?.name, params?.arguments);
        return ok({ content: [{ type: 'text', text: JSON.stringify(r) }], structuredContent: r });
      } catch (err) {
        return ok({ content: [{ type: 'text', text: err.message }], isError: true });
      }
    default: return ko(-32601, `Mètode no suportat: ${method}`);
  }
}

const CORS = {
  'access-control-allow-origin': '*',
  'access-control-allow-methods': 'POST, GET, OPTIONS',
  'access-control-allow-headers': 'content-type, accept, mcp-protocol-version, mcp-session-id, authorization',
};

export async function onRequest({ request }) {
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
  if (request.method !== 'POST') {
    return new Response(
      `Servidor MCP de ${SITE} (només lectura, sense autenticació).\nAfegeix-lo al teu client com a servidor remot: ${SITE}/mcp\n`,
      { status: 405, headers: { ...CORS, allow: 'POST, OPTIONS', 'content-type': 'text/plain; charset=utf-8' } });
  }
  let body;
  try { body = await request.json(); } catch {
    return Response.json({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'JSON invàlid' } }, { status: 400, headers: CORS });
  }
  const out = Array.isArray(body) ? body.map(gestiona).filter(Boolean) : gestiona(body);
  if (!out || (Array.isArray(out) && !out.length)) return new Response(null, { status: 202, headers: CORS });
  return Response.json(out, { headers: CORS });
}
