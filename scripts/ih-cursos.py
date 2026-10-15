import json,re,html,time,urllib.request,sys,os
d=json.load(open(sys.argv[1]));out=sys.argv[2]
res=json.load(open(out)) if os.path.exists(out) else {}
urls={x['curs_href'] or x['href'] for x in d}
for u in sorted(urls):
    if u in res: continue
    for t in range(8):
        try: h=urllib.request.urlopen(urllib.request.Request("https://www.instituthumanitats.org"+u,headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read().decode();break
        except Exception as e: print(u,e,flush=True);time.sleep(30*(t+1))
    h=re.sub(r'<script.*?</script>|<style.*?</style>','',h,flags=re.S)
    m=re.search(r'field--name-body field--type-text-with-summary field--label-above">\s*<div[^>]*>\s*Descripci[^<]*</div>(.*?)</div>',h,re.S) or re.search(r'Sinopsi(.*?)(?:Disponible a|Programa|Ponents|<footer)',h,re.S)
    txt=lambda s:re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
    sub=re.search(r'field--name-field-subtitle[^>]*>(.*?)</div>',h,re.S)
    res[u]={"sinopsi":txt(m.group(1)) if m else None,"subtitol":txt(sub.group(1)) if sub else None}
    json.dump(res,open(out,"w"),ensure_ascii=False,indent=1);print(len(res),u,flush=True);time.sleep(4)
