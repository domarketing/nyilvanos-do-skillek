# -*- coding: utf-8 -*-
"""Arculat-központ: egyetlen oldal (artifact) a három fázissal és a kézikönyvvel.

Fülek: Web · Prezentáció · Videó · Arculati kézikönyv. A web fül a választó (mentés: arculat/web-v<verzio>), a prezi és
a videó fül a PREZI és a VIDEÓ fázis töredéke (<section id="fazis-prezi|video">, a CSS a saját id-jére szűkítve, a JS
window.FAZISOK.<nev> = {init: function(db){}}). Amíg nincs töredék, ott a kapu szövege áll. Fázisállapot:
arculat/fazisok {web|prezi|video: {allapot, ido}}; a töredékek a window.HUB.fazis(nev, allapot) hívással jelezhetnek.
"""
import json
import re
from pathlib import Path

from .alap import esc, md, g, data_uri
from . import valaszto

FULEK = [("web", "1", "Web"), ("prezi", "2", "Prezentáció"), ("video", "3", "Videó"), ("kezikonyv", "", "Arculati kézikönyv")]

HUB_CSS = r"""
.hub-fej{background:#191b18;color:#f3f1ea;font-family:system-ui,-apple-system,'Segoe UI',sans-serif;position:relative;z-index:60}
.hub-in{max-width:1500px;margin:0 auto;padding:12px 22px;display:flex;align-items:center;gap:22px;flex-wrap:wrap}
.hub-marka{display:flex;flex-direction:column;line-height:1.15;margin-right:auto}
.hub-marka b{font-size:16px;letter-spacing:-.01em}.hub-marka small{font-size:11.5px;color:#b9b6ab;letter-spacing:.04em}
.hub-marka small em{font-style:normal;background:#e9c46a;color:#191b18;border-radius:4px;padding:0 5px;margin-left:6px;font-weight:700}
.hub-fulek{display:flex;gap:6px;flex-wrap:wrap}
.hub-fulek a{display:inline-flex;align-items:center;gap:8px;padding:8px 13px;border-radius:10px;color:#e9e6dc;text-decoration:none;font-size:14px;font-weight:600;border:1px solid rgba(255,255,255,.1)}
.hub-fulek a:hover{background:rgba(255,255,255,.07)}
.hub-fulek a.aktiv{background:#f3f1ea;color:#191b18}
.hub-fulek a .sz{display:inline-grid;place-items:center;width:20px;height:20px;border-radius:50%;background:rgba(255,255,255,.14);font-size:11.5px}
.hub-fulek a.aktiv .sz{background:#191b18;color:#f3f1ea}
.hub-fulek a i{font-style:normal;font-size:11px;font-weight:600;padding:2px 7px;border-radius:999px;background:rgba(255,255,255,.12)}
.hub-fulek a.aktiv i{background:#e7e3d6}
.hub-fulek a i[data-all="jovahagyva"]{background:#2f7d4f;color:#fff}
.hub-fulek a i[data-all="dontes"]{background:#e9c46a;color:#191b18}
.hub-fulek a i[data-all="kesobb"]{background:rgba(255,255,255,.08);color:#b9b6ab}
.hub-fulek a.aktiv i[data-all="kesobb"]{background:#e7e3d6;color:#5d5a52}
.hub-fazis{display:none}.hub-fazis.hub-aktiv{display:block}
.hub-kapu{background:#fff;border:2px solid #191b18;border-radius:20px;padding:24px 28px;margin:30px 0 10px;font-family:system-ui,-apple-system,'Segoe UI',sans-serif}
.hub-kapu h2{margin:0 0 6px;font-size:22px}.hub-kapu p{margin:0 0 14px;color:#4d4a43;max-width:70ch}
.hub-gomb{font:700 15px/1 system-ui,-apple-system,'Segoe UI',sans-serif;padding:14px 22px;border-radius:12px;border:0;background:#191b18;color:#fff;cursor:pointer}
.hub-gomb.meg{background:#b5431c}
.hub-kapu .ok{display:none;color:#2f7d4f;font-weight:700}
body.hub-web-ok .hub-kapu .ok{display:block}body.hub-web-ok .hub-gomb{display:none}
.hub-zart{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;background:#f1efe8;min-height:70vh}
.hub-zart-in{max-width:760px;margin:0 auto;padding:70px 24px}
.hub-kick{display:inline-block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#7a766b;margin-bottom:8px}
.hub-zart h2{font-size:32px;margin:0 0 14px;letter-spacing:-.015em}.hub-zart p{font-size:16.5px;color:#4d4a43;line-height:1.55}
.hub-zart ul{color:#4d4a43;line-height:1.6}
.hub-ha-nyitott{display:none}body.hub-web-ok .hub-ha-nyitott{display:block}body.hub-web-ok .hub-ha-zart{display:none}
.hub-lakat{display:inline-flex;align-items:center;gap:8px;background:#fff;border:1px solid #dcd8cc;border-radius:999px;padding:6px 13px;font-size:13px;color:#4d4a43;margin-bottom:18px}
#fazis-kezikonyv{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;background:#f1efe8;color:#1f1e1b}
#fazis-kezikonyv .kk-in{max-width:1100px;margin:0 auto;padding:46px 24px 80px}
#fazis-kezikonyv h2{font-size:34px;margin:0 0 6px;letter-spacing:-.015em}
#fazis-kezikonyv h3{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#7a766b;margin:34px 0 12px}
#fazis-kezikonyv .kk-all{display:inline-block;font-size:13px;background:#e9c46a;border-radius:6px;padding:3px 9px;margin:6px 0 10px}
#fazis-kezikonyv .kk-all.ok{background:#2f7d4f;color:#fff}
#fazis-kezikonyv p{color:#4d4a43;line-height:1.55;max-width:75ch}
#fazis-kezikonyv .kk-racs{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}
#fazis-kezikonyv .kk-szin{background:#fff;border-radius:14px;overflow:hidden;border:1px solid #e1ddd2}
#fazis-kezikonyv .kk-szin i{display:block;height:84px}
#fazis-kezikonyv .kk-szin div{padding:9px 11px;font-size:13px}#fazis-kezikonyv .kk-szin b{display:block}
#fazis-kezikonyv .kk-szin code{font-size:12px;color:#6b675e}
#fazis-kezikonyv .kk-betu{background:#fff;border-radius:14px;border:1px solid #e1ddd2;padding:16px 18px;margin-bottom:10px;display:grid;grid-template-columns:150px 1fr;gap:16px;align-items:center}
#fazis-kezikonyv .kk-betu small{display:block;color:#7a766b;font-size:12px}
#fazis-kezikonyv .kk-minta{font-size:30px;line-height:1.15;overflow-wrap:anywhere}
#fazis-kezikonyv .kk-ikonok{display:flex;flex-wrap:wrap;gap:10px;background:#fff;border-radius:14px;border:1px solid #e1ddd2;padding:14px}
#fazis-kezikonyv .kk-ikonok img{width:78px;height:78px;object-fit:contain}
#fazis-kezikonyv .kk-lista{background:#fff;border-radius:14px;border:1px solid #e1ddd2;padding:6px 18px}
#fazis-kezikonyv .kk-lista div{display:grid;grid-template-columns:170px 1fr;gap:14px;padding:10px 0;border-bottom:1px solid #eeebe3;font-size:14px}
#fazis-kezikonyv .kk-lista div:last-child{border-bottom:0}
#fazis-kezikonyv .kk-lista b{color:#1f1e1b}
#fazis-kezikonyv .kk-diak{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-bottom:12px}
#fazis-kezikonyv .kk-diak img{width:100%;height:auto;border-radius:10px;border:1px solid #e1ddd2;background:#fff}
#fazis-kezikonyv .kk-kep{width:100%;height:auto;border-radius:14px;border:1px solid #e1ddd2;background:#fff;margin-bottom:12px}
#fazis-kezikonyv .kk-fazis{display:inline-block;font-size:12px;border-radius:6px;padding:2px 8px;margin-left:8px;vertical-align:middle;background:#e9c46a;color:#191b18;letter-spacing:0;text-transform:none}
#fazis-kezikonyv .kk-fazis.ok{background:#2f7d4f;color:#fff}
#fazis-kezikonyv code{font-size:12.5px;background:#f1efe8;border-radius:4px;padding:1px 5px}
@media (max-width:760px){.hub-in{padding:10px 14px}.hub-fulek a{padding:7px 9px;font-size:13px}.hub-fulek a i{display:none}
#fazis-kezikonyv .kk-betu,#fazis-kezikonyv .kk-lista div{grid-template-columns:1fr;gap:4px}}
"""

HUB_JS = r"""
(function(){
var FAZ = ['web', 'prezi', 'video', 'kezikonyv'];
var ALL = {web: null, prezi: null, video: null};
var KEZDO = window.HUB_KEZDO || {};
['web', 'prezi', 'video'].forEach(function(n){ if (KEZDO[n] === 'jovahagyva') ALL[n] = 'jovahagyva'; });
var FDOC = null;
function $$(s){ return Array.prototype.slice.call(document.querySelectorAll(s)); }
function mutat(f){
  if (FAZ.indexOf(f) < 0) f = 'web';
  FAZ.forEach(function(x){ var s = document.getElementById('fazis-' + x); if (s) s.classList.toggle('hub-aktiv', x === f); });
  $$('.hub-fulek a').forEach(function(a){ a.classList.toggle('aktiv', a.getAttribute('data-fazis') === f); });
  try { history.replaceState(null, '', '#' + f); } catch(e) {}
  window.scrollTo(0, 0);
}
$$('.hub-fulek a').forEach(function(a){ a.addEventListener('click', function(ev){ ev.preventDefault(); mutat(a.getAttribute('data-fazis')); }); });
var h = (location.hash || '').slice(1); mutat(FAZ.indexOf(h) >= 0 ? h : 'web');
function webOk(){ var s = window.WEBVAL && window.WEBVAL.allapot(); return !!(s && s.jovahagyva) || ALL.web === 'jovahagyva'; }
function pill(n, t, a){ var el = document.querySelector('.hub-fulek i[data-f="' + n + '"]'); if (el) { el.textContent = t; el.setAttribute('data-all', a); } }
function rajzol(){
  var ok = webOk();
  document.body.classList.toggle('hub-web-ok', ok);
  pill('web', ok ? 'jóváhagyva' : 'döntésre vár', ok ? 'jovahagyva' : 'dontes');
  ['prezi', 'video'].forEach(function(n){
    var van = !!document.querySelector('#fazis-' + n + ':not(.hub-zart)');
    if (ALL[n] === 'jovahagyva') pill(n, 'jóváhagyva', 'jovahagyva');
    else if (van) pill(n, 'döntésre vár', 'dontes');            /* ha a fül kész, nincs „zárva” */
    else pill(n, ok ? 'készül' : 'a web után', 'kesobb');
  });
}
function fazisIr(nev, all){
  ALL[nev] = all;
  if (!FDOC) return;
  var d = {}; d[nev] = {allapot: all, ido: new Date().toISOString()};
  FDOC.get().then(function(s){ return s.exists ? FDOC.update(d) : FDOC.set(d); }).catch(function(){});
}
var gomb = document.getElementById('hub-jovahagy'), elso = false, tt;
if (gomb) gomb.addEventListener('click', function(){
  if (!elso) { elso = true; gomb.textContent = 'Biztosan? Kattints még egyszer a jóváhagyáshoz'; gomb.classList.add('meg');
    tt = setTimeout(function(){ elso = false; gomb.textContent = 'Jóváhagyom a webes arculatot'; gomb.classList.remove('meg'); }, 4500); return; }
  clearTimeout(tt); elso = false; gomb.classList.remove('meg');
  if (window.WEBVAL) window.WEBVAL.jovahagy();
  fazisIr('web', 'jovahagyva'); rajzol();
});
window.HUB = {fazis: function(n, a){ fazisIr(n, a); rajzol(); }, mutat: mutat};
function indit(db){ Object.keys(window.FAZISOK || {}).forEach(function(n){ try { window.FAZISOK[n].init(db); } catch(e) {} }); }
if (window.claude && typeof window.claude.use === 'function') {
  window.claude.use('db').then(function(db){
    indit(db || null);
    if (!db) return;
    try { FDOC = db.doc('arculat/fazisok'); } catch(e) { return; }
    FDOC.get().then(function(s){ var d = s.exists ? s.data() : {};
      ['web', 'prezi', 'video'].forEach(function(n){ if (d[n] && d[n].allapot) ALL[n] = d[n].allapot; }); rajzol(); }).catch(function(){});
    ['prezi', 'video'].forEach(function(n){            /* a fázis saját dokumentuma is jelezheti a jóváhagyást */
      try { db.doc('arculat/' + n + '-v1').get().then(function(s){ if (s.exists && s.data().jovahagyva) { ALL[n] = 'jovahagyva'; rajzol(); } }).catch(function(){}); } catch(e) {}
    });
  });
} else { indit(null); }
document.addEventListener('webval:betoltve', rajzol);
setTimeout(rajzol, 50);
})();
"""


def toredek(ut, nev):
    """Egy fázis töredéke: a fájl tartalma, ha benne van a <section id="fazis-<nev>">."""
    if not ut:
        return None
    p = Path(ut)
    if not p.exists():
        return None
    t = p.read_text(encoding="utf-8")
    if f'id="fazis-{nev}"' not in t:
        print(f"  ! a {p.name} nem tartalmaz <section id=\"fazis-{nev}\"> elemet, kihagyva")
        return None
    # a töredék <section>-je megkapja a fül-osztályt (a fül-váltás ezzel rejti/mutatja)
    m = re.search(r'<section\b[^>]*\bid="fazis-%s"[^>]*>' % nev, t)
    if not m:
        return None
    tag = m.group(0)
    uj = tag.replace('class="', 'class="hub-fazis ', 1) if 'class="' in tag else tag[:-1] + ' class="hub-fazis">'
    return t.replace(tag, uj, 1)


JELVENY = {"jovahagyva": "jóváhagyva", "dontes": "döntésre vár", "kesobb": "a web után", "keszul": "készül"}


def kezdo_allapot(alap, tok, van_prezi, van_video):
    """A fázisok állapota építéskor (allapot.json + tokenek); futás közben az adatbázis felülírhatja."""
    try:
        a = json.loads((Path(alap) / "allapot.json").read_text(encoding="utf-8"))
    except Exception:
        a = {}
    def fazis(n):
        v = a.get(n)
        return (v.get("allapot") if isinstance(v, dict) else v) or ""
    web = "jovahagyva" if (g(tok or {}, "allapot", "jovahagyva") or fazis("web") == "jovahagyva") else "dontes"
    out = {"web": web}
    for n, van in (("prezi", van_prezi), ("video", van_video)):
        out[n] = "jovahagyva" if fazis(n) == "jovahagyva" else ("dontes" if van else ("keszul" if web == "jovahagyva" else "kesobb"))
    return out


def _md_inline(t):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(t)).replace("`", "")


def prezi_resz(alap, all_):
    md_ut = Path(alap) / "prezi" / "PREZI-ARCULAT.md"
    if not md_ut.exists():
        return ""
    sorok, bent = [], False
    for sor in md_ut.read_text(encoding="utf-8").splitlines():
        if sor.startswith("## "):
            bent = "választott" in sor.lower()
            continue
        if bent and sor.startswith("|") and not set(sor.replace("|", "").strip()) <= set("-: "):
            c = [x.strip() for x in sor.strip("|").split("|")]
            if len(c) >= 4 and c[0] != "Kategória":
                sorok.append((re.sub(r"\*\*|\(ajánlott\)", "", c[0]).strip(), re.sub(r"\*\*|\(ajánlott\)", "", c[1]).strip(), c[2], c[3]))
    lista = "".join(f'<div><b>{esc(k)}</b><span>{esc(f)} <small style="color:#7a766b">· {esc(kar)}</small><br>{esc(mit)}</span></div>'
                    for k, kar, f, mit in sorok)
    kepek = "".join(f'<img src="prezi/kepek/{n}" alt="Minta-dia" loading="lazy">' for n in ("m-01.jpg", "m-05.jpg", "m-08.jpg", "m-12.jpg")
                    if (Path(alap) / "prezi" / "kepek" / n).exists())
    jel = f'<span class="kk-fazis{" ok" if all_ == "jovahagyva" else ""}">{"jóváhagyva" if all_ == "jovahagyva" else "ajánlott, még nincs jóváhagyva"}</span>'
    return (f'<h3>Prezentáció {jel}</h3><div class="kk-diak">{kepek}</div><div class="kk-lista">{lista}'
            f'<div><b>Így kérj újat</b><span>„Készíts prezentációt az arculatom szerint ebből a vázlatból: …” A márka-skillben lévő '
            f'prezi-motor valódi, szerkeszthető PowerPointot épít ezekkel a diatípusokkal, a márkád betűivel.</span></div></div>')


def video_resz(alap, all_):
    md_ut = Path(alap) / "video" / "VIDEO-ARCULAT.md"
    if not md_ut.exists():
        return ""
    t = md_ut.read_text(encoding="utf-8")
    m = re.search(r"## Röviden\s*\n+(.+?)(?:\n\s*\n|$)", t, re.S)
    roviden = _md_inline(" ".join(m.group(1).split())) if m else ""
    kd = Path(alap) / "video" / "kepek"
    fo = ('<img class="kk-kep" src="video/kepek/tablo-valasztott.jpg" alt="A választott videós elemek" loading="lazy">'
          if (kd / "tablo-valasztott.jpg").exists() else "")
    ketto = [sorted(kd.glob(minta))[0].name for minta in ("elem-stilus-*.jpg", "elem-nyito-*.jpg") if kd.is_dir() and sorted(kd.glob(minta))]
    kepek = "".join(f'<img src="video/kepek/{n}" alt="Videós elem" loading="lazy">' for n in ketto)
    jel = f'<span class="kk-fazis{" ok" if all_ == "jovahagyva" else ""}">{"jóváhagyva" if all_ == "jovahagyva" else "ajánlott, még nincs jóváhagyva"}</span>'
    return (f'<h3>Videó {jel}</h3>{fo}' + (f'<div class="kk-diak">{kepek}</div>' if kepek else "")
            + f'<div class="kk-lista"><div><b>Röviden</b><span>{roviden}</span></div>'
            f'<div><b>Így vágj</b><span>A vágáshoz a tananyagból telepített vágó skill kell (domarketing.hu/ai-video-vagas). Írd a '
            f'Claude-nak: „Tedd be a videós arculatomat a vágó skillembe”, és add meg a márka-skillben lévő <code>video/MARKA-RESZ.md</code> '
            f'fájlt. Kitölti a vágó skill „A TE ARCULATOD” blokkját, és új ZIP-et ad, amit a Customize → Skills alatt cserélsz le. '
            f'Utána elég annyi: „Vágd meg ezt a videót a saját videós arculatommal.”</span></div></div>')


def zart(nev, sz, cim, mi_lesz, utana):
    return (f'<section id="fazis-{nev}" class="hub-fazis hub-zart"><div class="hub-zart-in">'
            f'<span class="hub-kick">{sz}. fázis</span><h2>{esc(cim)}</h2>'
            f'<div class="hub-ha-zart"><span class="hub-lakat">Zárva: előbb a webes arculatot hagyd jóvá</span>{mi_lesz}</div>'
            f'<div class="hub-ha-nyitott"><span class="hub-lakat">A webes arculat jóvá van hagyva</span>{utana}</div></div></section>')


SZIN_NEV = [("primary", "Fő szín", "gombok, kiemelések, a márka jele"), ("accent", "Kiemelő", "második hangsúly, ikonok, díszek"),
            ("accent2", "Díszítő", "csak apró díszekben"), ("paper", "Papír", "a lap alapszíne"), ("card", "Kártya", "kártyák, dobozok"),
            ("ink", "Szöveg", "címek és szöveg"), ("deep", "Mély felület", "sötét szekciók, lábléc")]


def kezikonyv(tok, dns, jovahagyva, kezdo=None):
    if not tok:
        return '<section id="fazis-kezikonyv" class="hub-fazis"><div class="kk-in"><h2>Arculati kézikönyv</h2><p>Hamarosan.</p></div></section>'
    alap = Path(tok.get("alap", "."))
    sz = tok.get("szinek") or {}
    szinek = "".join(f'<div class="kk-szin"><i style="background:{esc(sz.get(k))}"></i><div><b>{n}</b><code>{esc(sz.get(k))}</code>'
                     f'<br><small>{m}</small></div></div>' for k, n, m in SZIN_NEV if sz.get(k))
    b = tok.get("betuk") or {}
    minta = {"display": "A kerted, amit annyira szeretsz", "body": "Árvíztűrő tükörfúrógép: így néz ki a szöveg minden ékezettel.",
             "hand": "kézzel írt megjegyzés, ő és ű", "label": "CÍMKE · 2026 · ŐŰ"}
    if g(tok, "marka", "szlogen"):
        sz_ = re.sub(r"[.…]+", "", tok["marka"]["szlogen"]).strip()
        if len(sz_) > 46:
            sz_ = sz_[:46].rsplit(" ", 1)[0].rstrip(",;:")
        minta["display"] = sz_[:1].upper() + sz_[1:] if sz_ else minta["display"]
    nevek = {"display": "Címbetű", "body": "Szövegbetű", "hand": "Kézírás", "label": "Címke-betű"}
    betuk = "".join(f'<div class="kk-betu"><div><b>{nevek[k]}</b><small>{esc(b[k]["csalad"])} · {b[k]["suly"]}</small></div>'
                    f'<div class="kk-minta" style="font-family:\'{esc(b[k]["csalad"])}\';font-weight:{b[k]["suly"]}'
                    f'{";font-size:17px" if k == "body" else ""}">{esc(minta[k])}</div></div>'
                    for k in ("display", "body", "hand", "label") if isinstance(b.get(k), dict))
    ik = tok.get("ikon") or {}
    kepek = ""
    for nev, rel in list((ik.get("fajlok") or {}).items())[:10]:
        p = alap / rel
        if p.exists():
            kepek += f'<img src="{data_uri(p, max_px=160, png=True)}" alt="{esc(nev)}">'
    komp = tok.get("komponensek") or {}
    knev = {"cim": "Címsor-kiemelés", "alcim": "Alcím", "gomb": "Gomb", "kartya": "Kártya", "foto": "Fotókezelés", "mozgas": "Mozgás"}
    komp_html = "".join(f'<div><b>{knev.get(k, k)}</b><span>{esc(v.get("nev", ""))}</span></div>' for k, v in komp.items())
    f = tok.get("forma") or {}
    def _px(v):
        return "kapszula" if v and float(v) >= 99 else f"{float(v or 0):g} px"
    forma_html = (f'<div><b>Lekerekítés</b><span>kártya {_px(f.get("r_kartya"))} · gomb {_px(f.get("r_gomb"))}</span></div>'
                  f'<div><b>Árnyék</b><span>{esc({"nincs": "nincs", "lagy": "lágy", "eros": "erős, kemény"}.get(f.get("arnyek"), f.get("arnyek")))}</span></div>'
                  f'<div><b>Keret</b><span>{float(f.get("keret_px") or 0):g} px</span></div>')
    mot = tok.get("motivum") or {}
    tema = "".join(f'<div><b>{n}</b><span>{esc((mot.get(k) or {}).get("nev", "") if isinstance(mot.get(k), dict) else ", ".join(x.get("nev", "") for x in mot.get(k) or []))}</span></div>'
                   for k, n in (("textura", "Háttér-textúra"), ("dekor", "Dekor"), ("hatar", "Szekcióhatár")) if mot.get(k))
    hn = (dns or {}).get("hangnem") or {}
    if isinstance(hn, str):
        hn = {"leiras": hn}
    kerul = "".join(f"<li>{esc(x)}</li>" for x in (dns or {}).get("kerulendo") or [])
    kezdo = kezdo or {}
    mind = all(kezdo.get(n) == "jovahagyva" for n in ("web", "prezi", "video"))
    allapot = ('<span class="kk-all ok">Végleges: a jóváhagyott webes, prezentációs és videós arculatból</span>' if mind else
               '<span class="kk-all ok">Végleges webes rész; a prezentáció és a videó a jóváhagyásuk után kerül be véglegesként</span>' if jovahagyva else
               '<span class="kk-all">Előzetes: az ajánlott opciókból. A webes jóváhagyás után a választásaid alapján frissül.</span>')
    prezi_html = prezi_resz(alap, kezdo.get("prezi"))
    video_html = video_resz(alap, kezdo.get("video"))
    return f"""<section id="fazis-kezikonyv" class="hub-fazis"><div class="kk-in">
<span class="hub-kick">Ebből dolgozik minden új anyagod</span><h2>{esc(g(tok, "marka", "nev"))} · arculati kézikönyv</h2>{allapot}
<p>Ez a kézikönyv a márkád szabálykönyve: minden új aloldal, prezentáció és videó ebből a színkészletből, ezekkel a betűkkel és ebben
az ikonstílusban készül. A végén egy saját márka-skillt is kapsz (ZIP), amit a Claude-ba feltöltve bárki a csapatodból ugyanígy kérhet új anyagot.</p>
<h3>Színek</h3><div class="kk-racs">{szinek}</div>
<h3>Betűk</h3>{betuk}
<h3>Ikonstílus: {esc(ik.get("stilus_nev", ""))}</h3><div class="kk-ikonok">{kepek}</div>
<h3>Formák és elemek</h3><div class="kk-lista">{forma_html}{komp_html}{tema}</div>
{prezi_html}
{video_html}
<h3>Hangnem</h3><div class="kk-lista"><div><b>Így beszélsz</b><span>{esc(hn.get("leiras", ""))}</span></div>
<div><b>Amit kerülünk</b><span><ul style="margin:0;padding-left:18px">{kerul}</ul></span></div></div>
<h3>Így kérj új anyagot</h3><div class="kk-lista">
<div><b>Új aloldal</b><span>„Készíts egy aloldalt az arculatom szerint erről: …” (a márka-skill tudja a színeket, betűket, elemeket)</span></div>
<div><b>Új prezentáció</b><span>„Készíts prezentációt az arculatom szerint ebből a vázlatból: …”</span></div>
<div><b>Videó</b><span>A vágó skilled a videós arculat márka-részéből dolgozik (feliratok, címsorok, kártyák).</span></div>
<div><b>A márka-skill</b><span>A végén kapott ZIP-et töltsd fel a Claude-ba (Customize → Skills), vagy Claude Code-ban tedd a ~/.claude/skills/ alá: onnantól a fenti kéréseket bárki a csapatodból ugyanígy kérheti.</span></div></div>
</div></section>"""


def epit(spec, ki, tok=None, dns=None, prezi=None, video=None, engedd=False, elozo=None):
    ki = Path(ki)
    web = ki.with_name(ki.stem + "-web.html")
    valaszto.epit(spec, web, elozo=elozo, engedd=engedd, dbnev="web")
    w = web.read_text(encoding="utf-8")
    m = re.search(r"<head>(.*?)</head><body>(.*)</body></html>\s*$", w, re.S)
    if not m:
        raise SystemExit("A választó HTML-je nem a várt szerkezetű (head/body).")
    fej, test = m.group(1), m.group(2)
    nev = g(spec, "marka", "nev")
    fej = re.sub(r"<title>.*?</title>", f"<title>{esc(nev)} · arculat-központ</title>", fej, 1, re.S)
    kapu = ('<section class="hub-kapu" id="hub-kapu-web"><h2>Kész a webes arculat?</h2>'
            '<p>Ha mindenhol megvan a végleges (★), vagy elfogadod az ajánlottakat, hagyd jóvá. Ebből készül a prezentációs és a videós '
            'arculat: azok a jóváhagyott színeket, betűket és ikonokat öröklik. Ahol nincs végleges, ott az ajánlott opció számít.</p>'
            '<button class="hub-gomb" id="hub-jovahagy" type="button">Jóváhagyom a webes arculatot</button>'
            '<p class="ok">✓ A webes arculat jóvá van hagyva. Szólj a Claude-nak: „jöhet a prezentáció”.</p></section>')
    pz_t, vd_t = toredek(prezi, "prezi"), toredek(video, "video")
    alap = Path(g(tok or {}, "alap") or ki.parent)
    kezdo = kezdo_allapot(alap, tok, bool(pz_t), bool(vd_t))
    if pz_t:
        kapu = kapu.replace("Szólj a Claude-nak: „jöhet a prezentáció”.", "A Prezentáció fülön folytathatod.")
    test = test.replace("</main></div>", kapu + "</main></div>", 1)
    jovahagyva = bool(g(tok or {}, "allapot", "jovahagyva"))
    fulek = "".join(f'<a href="#{n}" data-fazis="{n}">' + (f'<span class="sz">{sz}</span>' if sz else "") + f'{c}'
                    + (f' <i data-f="{n}" data-all="{kezdo[n]}">{JELVENY[kezdo[n]]}</i>' if n != "kezikonyv" else "") + '</a>'
                    for n, sz, c in FULEK)
    fejlec = (f'<div class="hub-fej"><div class="hub-in"><div class="hub-marka"><b>{esc(nev)}</b>'
              f'<small>Arculat-központ<em>béta</em></small></div><nav class="hub-fulek">{fulek}</nav></div></div>')
    pz = pz_t or zart(
        "prezi", 2, "A prezentációs arculat",
        "<p>A webes jóváhagyás után készül el: a jóváhagyott színekből, betűkből és ikonokból 10 prezi-kategória (címdia, fejezetdia, "
        "háttér és ritmus, címsor-kiemelés, fotókeret, ikontartó, felsorolásjel, számos dia, idézet, záródia), mindegyikben 5 változat, "
        "és 12 minta-dia a saját tartalmaddal. Valódi, szerkeszthető PowerPoint lesz belőle.</p>",
        "<p>Szólj a Claude-nak, hogy jöhet a prezentáció. A változatok ide kerülnek, ugyanúgy választhatsz és megjegyzést írhatsz, mint a webnél.</p>")
    vd = vd_t or zart(
        "video", 3, "A videós arculat",
        "<p>A prezentáció után jön: felirat, címsor (hook), témaválasztó kártya, infókártya, névkártya, záró, és a vágási stílus. "
        "Minden elem élő, ismétlődő előnézet telefonkeretben, a saját fotóiddal.</p>",
        "<p>Szólj a Claude-nak, ha jöhet a videós arculat. Előbb a prezentációs fázis készül el.</p>")
    for_test = (f'<section id="fazis-web" class="hub-fazis">{test}</section>{pz}{vd}{kezikonyv(tok, dns, jovahagyva, kezdo)}')
    html = (f'<!doctype html><html lang="hu"><head>{fej}<style>{HUB_CSS}</style></head><body>{fejlec}{for_test}'
            f'<script>window.FAZISOK=window.FAZISOK||{{}};window.HUB_KEZDO={json.dumps(kezdo)};</script><script>{HUB_JS}</script></body></html>')
    ki.write_text(html, encoding="utf-8")
    try:
        web.unlink()
    except Exception:
        pass
    return len(html)
