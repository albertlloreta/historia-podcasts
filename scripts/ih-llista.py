import re,json,html,sys,time,urllib.request
U=sys.argv[1];out=[]
for p in range(0,68):
    for t in range(8):
        try: h=urllib.request.urlopen(urllib.request.Request(U+f"&page={p}",headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read().decode();break
        except Exception as e: print(p,e,flush=True);time.sleep(30*(t+1))
    for blk in h.split('views-row"><div data-history-node-id="')[1:]:
        nid=blk.split('"')[0]
        g=lambda r:(m:=re.search(r,blk,re.S)) and html.unescape(m.group(1)).strip()
        out.append(dict(nid=nid,tipus=g(r'field-label-type[^>]*>([^<]*)'),
          yt=g(r'youtube\.com/embed/([\w-]+)'),vimeo=g(r'player\.vimeo\.com/video/(\d+)'),
          data=g(r'datetime="([^"]+)"'),href=g(r'<h4>\s*<a href="([^"]+)"'),titol=g(r'<h4>\s*<a[^>]*>([^<]*)'),
          curs=g(r'field-course.*?field--item"><a[^>]*>([^<]*)'),curs_href=g(r'field-course.*?field--item"><a href="([^"]+)"'),
          ponents=[html.unescape(x) for x in re.findall(r'/ca/ponents/[^"]*" hreflang="ca">([^<]*)',blk)]))
    time.sleep(4);print(p,len(out),flush=True)
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
print(len(out))
