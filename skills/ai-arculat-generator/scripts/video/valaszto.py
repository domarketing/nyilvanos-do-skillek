# -*- coding: utf-8 -*-
"""A videó-választó építése: az arculat-központ Videó füle (töredék) és egy önálló tesztoldal.

Kimenet a munkamappa video/ mappájában:
  video-toredek.html    <section id="fazis-video"> + saját CSS (#fazis-video alá szűkítve) + JS
                        (window.FAZISOK.video = {init(db)}); az `epit.py kozpont` magától beilleszti.
                        Mentés: arculat/video-v<verzio> {allapot, gepi, szoveg, frissitve, verzio, jovahagyva}.
  video-valaszto.html   önálló oldal ugyanezzel (helyi teszthez: localStorage + „Visszajelzés másolása”).
A képek (háttér, fej, logó, ikonok) WebP-ként beágyazva, így a töredék kicsi marad (kb. 0,5-1 MB).
"""
import base64
import html
import io
import json
from pathlib import Path

from PIL import Image

import katalogus as K
import tema as TM

SKILL = Path(__file__).resolve().parents[2]
ASSET = SKILL / "assets" / "video"
GSAP = "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"


def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def webp(ut, max_sz=None, minoseg=80):
    im = Image.open(ut)
    im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
    if max_sz and max(im.size) > max_sz:
        im.thumbnail((max_sz, max_sz), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "WEBP", quality=minoseg, method=6)
    return "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()


def kepek(mappa, tok, tart):
    """A beágyazandó képek: video/kepek/hatter.jpg + fej.png (a maszk.py kimenete), logó, ikonok."""
    kp = mappa / "video" / "kepek"
    K_ = {"bg": "", "fej": "", "ikonok": []}
    if (kp / "hatter.jpg").exists():
        K_["bg"] = webp(kp / "hatter.jpg", 1080, 78)
    if (kp / "fej.png").exists():
        K_["fej"] = webp(kp / "fej.png", 1000, 84)
    lg = tok.get("logo") or {}
    for kulcs, nev in (("szines", "logo"), ("feher", "logo_feher")):
        if lg.get(kulcs) and (mappa / lg[kulcs]).exists():
            K_[nev] = webp(mappa / lg[kulcs], 640, 90)
    ik = tok.get("ikon") or {}
    fajlok = ik.get("fajlok") or {}
    nevek = list(tart.get("ikonok") or []) or list(fajlok.keys())[:4]
    cimkek = {x.get("ikon"): x.get("cimke") for x in (tart.get("oldalcsempek") or []) if isinstance(x, dict)}
    for n in nevek[:4]:
        f = fajlok.get(n)
        if f and (mappa / f).exists():
            K_["ikonok"].append({"nev": n, "cimke": cimkek.get(n, ""), "src": webp(mappa / f, 220, 86)})
    return K_


def adat(mappa, verzio=1):
    mappa = Path(mappa)
    tok = json.loads((mappa / "tokenek.json").read_text(encoding="utf-8"))
    tp = mappa / "video" / "tartalom.json"
    tart = K.alap_tartalom(tok)
    if tp.exists():
        tart.update(json.loads(tp.read_text(encoding="utf-8")))
    T = TM.tema(tok)
    fej = {}
    fp = mappa / "video" / "kepek" / "fej.json"
    if fp.exists():
        fej = json.loads(fp.read_text(encoding="utf-8"))
    css_v = {}
    for sor in TM.css(T).split(":root{", 1)[1].split("}", 1)[0].strip().splitlines():
        k, _, v = sor.strip().rstrip(";").partition(":")
        css_v[k.strip()] = v.strip()
    dns = {}
    dp = mappa / (tok.get("marka_dns") or "marka-dns.json")
    if dp.exists():
        dns = json.loads(dp.read_text(encoding="utf-8"))
    kat = K.kategoriak(tok, tart, dns)
    D = {"marka": {"nev": (tok.get("marka") or {}).get("nev", ""), "slug": (tok.get("marka") or {}).get("slug", "marka")},
         "verzio": verzio, "tartalom": tart, "kategoriak": kat, "fej": fej, "cssv": css_v,
         "tema": {"motivum": T["motivum"]}, "kepek": kepek(mappa, tok, tart),
         "karakterek": {k: {"nev": (v or {}).get("nev", ""), "szo": K.KARSZO.get(k, k)} for k, v in (dns.get("karakterek") or {}).items()}}
    return D, T, tok


def orokolt(T, tok, D):
    R = T["szinek"]["szerepek"]
    sz = [("fő", R["fo"]), ("kiemelő", R["akcent"]), ("díszítő", R["akcent2"]), ("papír", R["papir"]), ("kártya", R["kartya"]),
          ("szöveg", R["szoveg_kartyan"]), ("mély", R["mely"]), ("kiemelés a felvételen", R["kiemeles_felvetelen"])]
    cs = "".join(f'<i style="background:{c};{"color:#111;text-shadow:none" if TM.lum(c) > 0.55 else ""}" title="{e(n)} {c}">{e(n)}</i>' for n, c in sz)
    B = T["betuk"]
    minta = "Árvíztűrő tükörfúrógép"
    bet = "".join(f'<div><small class="l">{e(n)}</small> <span style="font-family:\'{e(B[k]["csalad"])}\';font-weight:{B[k].get("suly", 400)}">{minta}</span> '
                  f'<small>{e(B[k]["csalad"])} {B[k].get("suly", "")}</small></div>'
                  for k, n in (("felirat", "Felirat"), ("cim", "Cím")) if B.get(k))
    ik = "".join(f'<img src="{x["src"]}" alt="">' for x in D["kepek"]["ikonok"])
    megj = " ".join(B.get("megjegyzesek") or []) + " " + " ".join(T["szinek"].get("megjegyzesek") or [])
    return (f'<section class="vv-orok"><h3>Örökölt elemek a webes arculatból (ezekre nem kérdezünk rá újra)</h3>'
            f'<span class="l">Színek</span><div class="c">{cs}</div>'
            f'<span class="l">Betűk</span><div class="b">{bet}</div>'
            f'<span class="l">Ikonok</span><div class="ik">{ik}<small style="align-self:center;color:#6b675e;margin-left:6px">{e((tok.get("ikon") or {}).get("stilus_nev", ""))}</small></div>'
            f'<span class="l">Megjegyzés</span><div class="m">{e(megj.strip())}</div></section>')


def kategoria_html(k, i):
    opts = []
    for v in k["valtozatok"]:
        ajanl = '<span class="vv-ajanl">ajánlott</span>' if v["id"] == k["ajanlott"] else ""
        miert = f'<p class="vv-miert">{e(v["miert"])}</p>' if v.get("miert") else ""
        hang = ""
        if k["kat"] == "hangulat":
            hang = ('<div class="vv-hang"><button type="button" data-h="zene">▶ Zene</button><button type="button" data-h="atmenet">▶ Átmenet</button>'
                    '<button type="button" data-h="kartya">▶ Kártya</button><button type="button" data-h="kiemeles">▶ Kiemelés</button></div>')
        kar = v.get("karakter") or {}
        kart = (f'<span class="vv-kar" title="{e(kar.get("szo", ""))} karakter">{e(kar.get("nev") or kar.get("szo"))} · {e(kar.get("szo"))}</span>'
                if kar.get("nev") else "")
        opts.append(f'<article class="vv-opt" data-id="{e(v["id"])}"><div class="vv-mini" title="Kipróbálom"></div>{kart}'
                    f'<div class="vv-nev">{e(v["nev"])} {ajanl}</div><p class="vv-le">{e(v["leiras"])}</p>{miert}{hang}'
                    f'<div class="vv-gombok"><button type="button" class="vv-prob">Kipróbálom</button><button type="button" class="vv-veg">☆ Ez legyen</button></div>'
                    f'<textarea class="vv-com" placeholder="Megjegyzés ehhez a változathoz…"></textarea></article>')
    return (f'<section class="vv-kat" id="vv-kat-{k["kat"]}" data-kat="{k["kat"]}"><header><span class="sz">{i}</span><h3>{e(k["nev"])}</h3>'
            f'<span class="st"></span><p>{e(k["leiras"])}</p></header><div class="vv-opts">{"".join(opts)}</div>'
            f'<label class="vv-ujak"><input type="checkbox"> Egyik sem az igazi, kérek újakat</label></section>')


def toredek(D, T, tok):
    css = (ASSET / "elonezet.css").read_text(encoding="utf-8")
    js = (ASSET / "elonezet.js").read_text(encoding="utf-8")
    B = T["betuk"]
    fontok = []
    for k in ("felirat", "cim", "cimke", "kez"):
        if B.get(k) and B[k].get("google_css") and B[k]["google_css"] not in fontok:
            fontok.append(B[k]["google_css"])
    linkek = "".join(f'<link rel="stylesheet" href="{e(u)}">' for u in fontok)
    figy = ""
    KR = D.get("karakterek") or {}
    if KR:
        sor = ", ".join(f"<b>{e(KR[k]['nev'])}</b> ({e(KR[k]['szo'])})" for k in K.KARSOR if k in KR and KR[k].get("nev"))
        figy += (f'<p class="vv-kar-magy">A fő kategóriák 5 változata a márkád 5 karakterét követi, ugyanabban a sorrendben, mint a webes és a '
                 f'prezentációs választóban: {sor}. Bátran keverd őket.</p>')
    if not ((tok.get("allapot") or {}).get("jovahagyva")):
        figy = ('<p class="vv-figy">Előnézet: a webes arculat még nincs jóváhagyva, ezért ezek az ajánlott webes opciókból készültek. '
                'A jóváhagyás után a választott színekkel és betűkkel frissülnek.</p>')
    fo = [k for k in D["kategoriak"] if k.get("csoport") == "fo"]
    kis = [k for k in D["kategoriak"] if k.get("csoport") != "fo"]
    katok = (''.join(kategoria_html(k, i + 1) for i, k in enumerate(fo)) +
             '<h3 class="vv-csop">Kisebb elemek, 3-3 változatban</h3>' +
             ''.join(kategoria_html(k, len(fo) + i + 1) for i, k in enumerate(kis)))
    jel = "".join(f'<button type="button" data-s="{s}">{n}</button>' for s, n in
                  (("nyito", "Nyitókép"), ("hook", "Címsor"), ("fo", "Stílus"), ("tema", "Téma"), ("nev", "Név"), ("fejezet", "Fejezet"), ("zaro", "Záró")))
    nev = D["marka"]["nev"]
    adatjson = json.dumps(D, ensure_ascii=False).replace("</", "<\\/")
    return f"""<section id="fazis-video" class="vv"><script src="{GSAP}"></script>{linkek}<style>{css}</style>
<div class="vv-in">
<header class="vv-fej"><div><span class="vv-kick">3. fázis · béta</span><h2>A videós arculat: {e(nev)}</h2>
<p>Minden elem élő, ismétlődő előnézet telefonkeretben, a saját fotóddal, színeiddel és betűiddel. Jobb oldalt az összeállítás:
ott látod, hogyan néz ki együtt az, amit kiválasztottál.</p>
<ol class="vv-lepes"><li><b>1.</b> Kattints egy telefonra: kipróbálod</li><li><b>2.</b> ★ Ez legyen: végleges</li>
<li><b>3.</b> Megjegyzés bármelyikhez</li><li><b>4.</b> A végén: Jóváhagyom</li></ol></div>
<div class="vv-eszk"><button type="button" class="vv-kap fo" id="vv-ajanlott">✓ Ajánlottak elfogadása</button><span class="vv-kap" data-k="reels">Reels-felület és safe zone</span><span class="vv-kap" data-k="lassu">Lassítás</span>
<span class="vv-kap" data-k="hang">Hang az összeállításban</span></div>
<div class="vv-mentes">mentés a böngészőben</div></header>
<p class="vv-figy vv-figy-gsap" style="display:none">Az animációs könyvtár (GSAP) nem töltődött be, ezért az előnézetek nem mozognak. Ellenőrizd a hálózatot, és töltsd újra az oldalt.</p>
{figy}{orokolt(T, tok, D)}
<div class="vv-racs"><main class="vv-katok">{katok}
<section class="vv-lab"><h3>Kész a videós arculat?</h3>
<p>Ha mindenhol megvan a végleges (★), vagy elfogadod az ajánlottakat, hagyd jóvá. Ahol nincs végleges, ott a kipróbált, ha az sincs, az ajánlott változat számít.
Ebből készül a videós arculat leírása, amiből a vágó skilled dolgozik.</p>
<textarea id="vv-altalanos" placeholder="Általános megjegyzés a videós arculathoz…"></textarea>
<div class="vv-gsor"><button type="button" class="vv-gomb" id="vv-jovahagy">Jóváhagyom a videós arculatot</button>
<button type="button" class="vv-gomb masod vv-export">Visszajelzés másolása</button></div></section></main>
<aside class="vv-elo"><h3>Összeállítás</h3><p>Nyitókép, címsor, stílus, témaválasztó, névkártya, fejezet és záró egymás után, a kiválasztott változatokkal.</p>
<div class="vv-nagy" style="display:flex;justify-content:center"></div><div class="vv-jel">{jel}</div></aside></div></div>
<div class="vv-modal"><div><h3 style="margin:0 0 8px">Visszajelzés a Claude-nak</h3><p style="margin:0 0 10px;color:#4d4a43;font-size:14px">Másold ki, és illeszd be a beszélgetésbe.</p>
<textarea readonly></textarea><div class="vv-gsor" style="margin-top:10px"><button type="button" class="vv-gomb" id="vv-masol">Másolás</button>
<button type="button" class="vv-gomb masod" data-bezar>Bezárás</button></div></div></div>
<div class="vv-toast"></div>
<script type="application/json" id="vv-adat">{adatjson}</script>
<script>{js}</script>
</section>
"""


BOOT = """<script>
(function(){function go(db){try{window.FAZISOK.video.init(db);}catch(e){}}
if(window.claude&&typeof window.claude.use==='function'){window.claude.use('db').then(function(db){go(db||null);},function(){go(null);});}else{go(null);}})();
</script>"""


def onallo(tor, nev):
    return (f'<!doctype html><html lang="hu"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(nev)} · videós arculat</title><style>html,body{{margin:0;background:#f1efe8}}</style></head><body>'
            f'<div style="background:#191b18;color:#f3f1ea;font:600 14px system-ui,sans-serif;padding:12px 22px">{e(nev)} · '
            f'<span style="color:#b9b6ab">Arculat-központ, videó fázis</span> <span style="background:#e9c46a;color:#191b18;border-radius:4px;padding:0 5px">béta</span></div>'
            f'{tor}{BOOT}</body></html>')


def epit(mappa, verzio=1):
    mappa = Path(mappa)
    D, T, tok = adat(mappa, verzio)
    vm = mappa / "video"
    vm.mkdir(exist_ok=True)
    tor = toredek(D, T, tok)
    (vm / "video-toredek.html").write_text(tor, encoding="utf-8")
    (vm / "video-valaszto.html").write_text(onallo(tor, D["marka"]["nev"]), encoding="utf-8")
    return vm / "video-toredek.html", vm / "video-valaszto.html", len(tor)
