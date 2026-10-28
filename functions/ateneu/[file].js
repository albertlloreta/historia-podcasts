// Serveix per HTTPS els MP3 de l'Arxiu de la Paraula de l'Ateneu Barcelonès,
// que només són accessibles per HTTP (el navegador els bloquejaria com a contingut mixt).
// No guarda res: passa la petició (amb el Range, per poder saltar) i torna la resposta.
export async function onRequestGet({ params, request }) {
  const file = params.file;
  if (!/^[0-9a-f]{32}\.mp3$/.test(file)) return new Response('No trobat', { status: 404 });
  const headers = new Headers();
  const range = request.headers.get('Range');
  if (range) headers.set('Range', range);
  const r = await fetch(`http://arxiudigital.ateneubcn.cat/files/original/${file}`, { headers });
  const out = new Headers();
  for (const k of ['content-type', 'content-length', 'content-range', 'accept-ranges', 'last-modified', 'etag']) {
    const v = r.headers.get(k);
    if (v) out.set(k, v);
  }
  out.set('cache-control', 'public, max-age=86400');
  return new Response(r.body, { status: r.status, headers: out });
}
