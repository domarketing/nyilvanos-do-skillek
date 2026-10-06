#!/usr/bin/env python3
"""Claude Oldalak segédszkript: oldalak kezelése a saját WordPress oldaladon.

A Claude Oldalak WordPress-bővítmény REST API-ját hívja
({SITE}/wp-json/claude-oldalak/v1). Csak a Python standard könyvtárát használja.

Kapcsolati adatok (ebben a sorrendben keresi):
  1. --config JSON fájl: {"site": "https://SAJATOLDALAD.hu", "api_key": "..."}
  2. környezeti változók: CLAUDE_OLDALAK_SITE és CLAUDE_OLDALAK_API_KEY
  3. ~/.config/claude-oldalak/config.json (ha létezik)

Az API-kulcsot a szkript soha nem írja ki.

Példák:
  python oldalak.py info
  python oldalak.py list
  python oldalak.py get --slug webinar --out webinar.html
  python oldalak.py create --slug webinar --title "Webinár" --html oldal.html
  python oldalak.py update --slug webinar --html oldal.html --yes
  python oldalak.py delete --id 123 --yes
  python oldalak.py media --file kep.jpg --alt "Borítókép"
"""
import argparse
import base64
import hashlib
import http.client
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_PATH = "/wp-json/claude-oldalak/v1"
KEY_HEADER = "X-Claude-API-Key"
USER_AGENT = "claude-oldalak-feltolto/1.0"
DEFAULT_CONFIG = Path.home() / ".config" / "claude-oldalak" / "config.json"

RETRY_429 = 6          # ennyiszer próbálja újra 429 (túl sok kérés) után
WAIT_429 = 20          # másodperc várakozás 429 után
MEDIA_PAUSE = 6.5      # másodperc szünet két képfeltöltés között


class ApiError(Exception):
    def __init__(self, status, body):
        self.status = status
        self.body = body
        super().__init__(f"HTTP {status}: {body}")


# ---------------------------------------------------------------- beállítás

def load_config(config_path=None):
    site = key = None
    path = Path(config_path).expanduser() if config_path else None
    if path is None and not (os.environ.get("CLAUDE_OLDALAK_SITE") and os.environ.get("CLAUDE_OLDALAK_API_KEY")):
        if DEFAULT_CONFIG.exists():
            path = DEFAULT_CONFIG
    if path is not None:
        if not path.exists():
            sys.exit(f"Nem találom a konfigurációs fájlt: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            sys.exit(f"A konfigurációs fájl nem érvényes JSON: {path}")
        site = data.get("site")
        key = data.get("api_key")
    site = site or os.environ.get("CLAUDE_OLDALAK_SITE")
    key = key or os.environ.get("CLAUDE_OLDALAK_API_KEY")
    if not site or not key:
        sys.exit("Hiányzik az oldal címe vagy az API-kulcs. Add meg a CLAUDE_OLDALAK_SITE és "
                 "CLAUDE_OLDALAK_API_KEY környezeti változót, vagy egy --config JSON fájlt.")
    site = site.strip().rstrip("/")
    if not re.match(r"^https?://", site):
        site = "https://" + site
    return site, key.strip()


# ---------------------------------------------------------------- HTML-előkészítés

def safe_html(html):
    """4 bájtos karakterek (emoji) HTML-entitássá, mert sok WordPress-adatbázis nem tárolja őket."""
    return "".join(f"&#{ord(c)};" if ord(c) > 0xFFFF else c for c in html)


def double_backslashes(html):
    """A bővítmény tároláskor egy szint backslasht eltávolít (wp_unslash), ezért előre duplázzuk."""
    return html.replace("\\", "\\\\")


def first_difference(a, b):
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return i
    return n if len(a) != len(b) else -1


def normalize(text):
    return (text or "").replace("\r\n", "\n")


# ---------------------------------------------------------------- kliens

class Client:
    def __init__(self, site, key, timeout=90):
        self.site = site
        self.base = site + API_PATH
        self._key = key
        self.timeout = timeout

    def call(self, method, path, payload=None):
        data = None
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        for attempt in range(RETRY_429 + 1):
            req = urllib.request.Request(self.base + path, data=data, method=method, headers={
                KEY_HEADER: self._key,
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            })
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    raw = r.read().decode("utf-8", errors="replace")
                    return json.loads(raw) if raw.strip() else {}
            except urllib.error.HTTPError as e:
                raw = e.read().decode("utf-8", errors="replace")
                if e.code == 429 and attempt < RETRY_429:
                    print(f"  429 (túl sok kérés), várok {WAIT_429} mp-et, aztán újrapróbálom...", file=sys.stderr)
                    time.sleep(WAIT_429)
                    continue
                try:
                    body = json.loads(raw)
                except ValueError:
                    body = raw[:500]
                raise ApiError(e.code, body)
            except urllib.error.URLError as e:
                raise ApiError(0, f"Hálózati hiba: {e.reason}. Ha claude.ai-on futsz, lehet, hogy "
                                  f"a kódfuttató környezet nem éri el ezt a domaint.")
            except (http.client.HTTPException, OSError) as e:
                raise ApiError(0, f"A kapcsolat megszakadt ({e.__class__.__name__}). Nézd meg, hogy "
                                  f"a kérés átment-e (list vagy get), mielőtt újrapróbálod.")
        raise ApiError(429, "Tartósan túl sok kérés, próbáld újra pár perc múlva.")

    # --- végpontok
    def info(self):
        return self.call("GET", "/info")

    def list_pages(self):
        return self.call("GET", "/pages")

    def get_page(self, page_id):
        return self.call("GET", f"/pages/{int(page_id)}")

    def get_by_slug(self, slug):
        return self.call("GET", "/pages/slug/" + urllib.parse.quote(slug.strip("/"), safe="/"))

    def create_page(self, payload):
        return self.call("POST", "/pages", payload)

    def update_page(self, page_id, payload):
        return self.call("PUT", f"/pages/{int(page_id)}", payload)

    def delete_page(self, page_id):
        return self.call("DELETE", f"/pages/{int(page_id)}")

    def upload_media(self, payload):
        return self.call("POST", "/media", payload)


# ---------------------------------------------------------------- segédek

def read_html(path):
    p = Path(path).expanduser()
    if not p.exists():
        sys.exit(f"Nem találom a HTML fájlt: {p}")
    return p.read_text(encoding="utf-8")


def resolve_id(client, args):
    if getattr(args, "id", None):
        return int(args.id)
    if getattr(args, "slug", None):
        page = client.get_by_slug(args.slug)
        return int(page["id"])
    sys.exit("Adj meg --id vagy --slug értéket.")


def check_live(url):
    """Az élő oldal HTTP-állapota, kulcs nélkül, ahogy egy látogató látja."""
    if not url:
        return None
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            r.read(2048)
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # noqa: BLE001
        return f"nem elérhető ({e.__class__.__name__})"


def verify(client, page_id, intended, sent_doubled, payload_extra):
    """Visszaolvassa az oldalt, és összeveti a szándékolt HTML-lel.

    Ha a tárolt HTML pont a duplázott változat, akkor a bővítmény már nem vesz el
    backslasht: ekkor duplázás nélkül újraküldi.
    """
    page = client.get_page(page_id)
    stored = normalize(page.get("html"))
    want = normalize(intended)
    if stored == want:
        print("Ellenőrzés: a tárolt HTML pontosan egyezik a feltöltöttel.")
        return page, True
    if sent_doubled and stored == normalize(double_backslashes(intended)):
        print("A bővítmény most nem vette el a backslasheket, ezért duplázás nélkül újraküldöm...")
        payload = dict(payload_extra)
        payload["html"] = intended
        client.update_page(page_id, payload)
        page = client.get_page(page_id)
        if normalize(page.get("html")) == want:
            print("Ellenőrzés: a tárolt HTML most pontosan egyezik.")
            return page, True
        stored = normalize(page.get("html"))
    pos = first_difference(stored, want)
    print("FIGYELEM: a tárolt HTML eltér a feltöltöttől.", file=sys.stderr)
    print(f"  Első eltérés a(z) {pos}. karakternél.", file=sys.stderr)
    print(f"  Feltöltött: {want[max(0, pos - 40):pos + 40]!r}", file=sys.stderr)
    print(f"  Tárolt:     {stored[max(0, pos - 40):pos + 40]!r}", file=sys.stderr)
    print(f"  Backslashek száma: feltöltött {want.count(chr(92))}, tárolt {stored.count(chr(92))}", file=sys.stderr)
    return page, False


DATA_URI = re.compile(r"data:(?P<mime>image/[a-zA-Z0-9.+-]+);base64,(?P<data>[A-Za-z0-9+/=\s]+?)(?=[\"')])")
EXT = {"jpeg": "jpg", "jpg": "jpg", "png": "png", "gif": "gif", "webp": "webp", "avif": "avif", "svg+xml": "svg"}


def externalize_images(client, html, prefix="kep"):
    """A HTML-be ágyazott base64 képeket feltölti a médiatárba, és valódi URL-re cseréli."""
    cache = {}
    state = {"uploaded": 0}

    def repl(m):
        data = re.sub(r"\s+", "", m.group("data"))
        digest = hashlib.sha256(data.encode("ascii")).hexdigest()   # a TELJES tartalom hash-e
        if digest in cache:
            return cache[digest]
        ext = EXT.get(m.group("mime").split("/")[-1].lower(), "png")
        if state["uploaded"]:
            time.sleep(MEDIA_PAUSE)
        try:
            res = client.upload_media({"base64": data, "filename": f"{prefix}-{digest[:10]}.{ext}"})
            state["uploaded"] += 1
            cache[digest] = res["url"]
            print(f"  kép feltöltve: {res['url']}")
            return res["url"]
        except ApiError as e:
            print(f"  egy képet nem sikerült feltölteni, base64-ben marad ({e.status})", file=sys.stderr)
            return m.group(0)

    return DATA_URI.sub(repl, html)


def build_payload(client, args, html_text):
    payload = {}
    intended = None
    if html_text is not None:
        if getattr(args, "externalize_images", False):
            html_text = externalize_images(client, html_text)
        intended = safe_html(html_text)
        payload["html"] = intended if args.no_double else double_backslashes(intended)
    if getattr(args, "title", None):
        payload["title"] = args.title
    if getattr(args, "status", None):
        payload["status"] = args.status
    if getattr(args, "bundle", None) is not None:
        payload["required_bundle"] = args.bundle
    return payload, intended


def report(page, live=True):
    url = page.get("url")
    print(f"ID: {page.get('id')}  slug: {page.get('slug')}  cím: {page.get('title')}")
    if url:
        print(f"Élő cím: {url}")
        if live:
            print(f"Élő oldal HTTP-állapota: {check_live(url)}")


# ---------------------------------------------------------------- parancsok

def cmd_info(client, args):
    print(json.dumps(client.info(), ensure_ascii=False, indent=2))


def cmd_list(client, args):
    pages = client.list_pages()
    if isinstance(pages, dict):
        pages = pages.get("pages", [])
    if args.json:
        print(json.dumps(pages, ensure_ascii=False, indent=2))
        return
    if not pages:
        print("Még nincs Claude-oldal ezen a webhelyen.")
        return
    print(f"{'ID':>6}  {'állapot':<8}  {'slug':<30}  cím / URL")
    for p in pages:
        print(f"{p.get('id', ''):>6}  {str(p.get('status', '')):<8}  {str(p.get('slug', '')):<30}  "
              f"{p.get('title', '')}  {p.get('url', '')}")


def cmd_get(client, args):
    page = client.get_page(args.id) if args.id else client.get_by_slug(args.slug or sys.exit("Adj meg --id vagy --slug értéket."))
    html = page.get("html") or ""
    if args.out:
        Path(args.out).expanduser().write_text(html, encoding="utf-8")
        print(f"HTML elmentve: {args.out} ({len(html)} karakter)")
    meta = {k: v for k, v in page.items() if k != "html"}
    print(json.dumps(meta, ensure_ascii=False, indent=2))


def cmd_create(client, args):
    slug = args.slug.strip("/")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)*", slug):
        sys.exit("A slug csak ékezet nélküli kisbetű, szám és kötőjel lehet (pl. ingyenes-webinar).")
    html = read_html(args.html)
    payload, intended = build_payload(client, args, html)
    payload["slug"] = slug
    payload["title"] = args.title
    if args.parent:
        payload["parent_slug"] = args.parent.strip("/")
    try:
        res = client.create_page(payload)
    except ApiError as e:
        if e.status == 409:
            sys.exit(f"A '{slug}' cím már foglalt (409). Ha ez a te Claude-oldalad, frissítsd az "
                     f"update paranccsal; ha más (WordPress-oldal vagy médiafájl) foglalja, válassz másik "
                     f"slugot. Válasz: {e.body}")
        raise
    print("Oldal létrehozva.")
    extra = {k: v for k, v in payload.items() if k not in ("html", "slug", "parent_slug")}
    page, ok = verify(client, res["id"], intended, not args.no_double, extra)
    report({**res, **{k: page.get(k) for k in ("id", "slug", "title", "url") if page.get(k)}})
    if not ok:
        sys.exit(3)


def cmd_update(client, args):
    page_id = resolve_id(client, args)
    current = client.get_page(page_id)
    html = read_html(args.html) if args.html else None
    if html is None and not (args.title or args.status or args.bundle is not None):
        sys.exit("Nincs mit frissíteni: adj meg --html, --title, --status vagy --bundle értéket.")
    if not args.yes:
        print(f"Ezt az oldalt írnám felül: ID {page_id}, '{current.get('title')}', {current.get('url')}")
        print("Kérj megerősítést a felhasználótól, és utána futtasd újra --yes kapcsolóval.")
        sys.exit(2)
    payload, intended = build_payload(client, args, html)
    client.update_page(page_id, payload)
    print("Oldal frissítve. (Az előző állapot a WordPress adminban visszaállítható.)")
    ok = True
    page = client.get_page(page_id)
    if intended is not None:
        extra = {k: v for k, v in payload.items() if k != "html"}
        page, ok = verify(client, page_id, intended, not args.no_double, extra)
    report(page)
    if not ok:
        sys.exit(3)


def cmd_delete(client, args):
    page_id = resolve_id(client, args)
    page = client.get_page(page_id)
    if not args.yes:
        print(f"Ezt az oldalt törölném: ID {page_id}, '{page.get('title')}', {page.get('url')}")
        print("Kérj kifejezett megerősítést a felhasználótól, és utána futtasd újra --yes kapcsolóval.")
        sys.exit(2)
    res = client.delete_page(page_id)
    print(f"Törölve: ID {page_id}, '{page.get('title')}'")
    if res:
        print(json.dumps(res, ensure_ascii=False, indent=2))


def cmd_media(client, args):
    if bool(args.file) == bool(args.url):
        sys.exit("Adj meg pontosan egyet: --file vagy --url.")
    if args.url:
        payload = {"url": args.url}
    else:
        p = Path(args.file).expanduser()
        if not p.exists():
            sys.exit(f"Nem találom a képet: {p}")
        payload = {"base64": base64.b64encode(p.read_bytes()).decode("ascii"),
                   "filename": args.filename or p.name}
        mime = mimetypes.guess_type(p.name)[0] or ""
        if not mime.startswith("image/"):
            print(f"Figyelem: ez nem tűnik képnek ({mime or 'ismeretlen típus'}).", file=sys.stderr)
    if args.alt:
        payload["alt"] = args.alt
    res = client.upload_media(payload)
    print(json.dumps(res, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- CLI

def build_parser():
    ap = argparse.ArgumentParser(
        prog="oldalak.py",
        description="Claude Oldalak: oldalak kezelése a saját WordPress oldaladon (REST API).",
        epilog="Kapcsolat: CLAUDE_OLDALAK_SITE + CLAUDE_OLDALAK_API_KEY környezeti változó, vagy --config JSON.")
    ap.add_argument("--config", help="JSON fájl: {\"site\": \"https://...\", \"api_key\": \"...\"}")
    sub = ap.add_subparsers(dest="cmd", metavar="parancs")
    sub.required = True

    sub.add_parser("info", help="kapcsolat és bővítményverzió ellenőrzése")

    p = sub.add_parser("list", help="a Claude-oldalak listája")
    p.add_argument("--json", action="store_true", help="nyers JSON kimenet")

    p = sub.add_parser("get", help="egy oldal lekérése (HTML mentése fájlba)")
    p.add_argument("--id", type=int)
    p.add_argument("--slug")
    p.add_argument("--out", help="ide menti a HTML-t")

    def write_opts(p):
        p.add_argument("--status", help="WordPress-állapot (ha a bővítményed támogatja)")
        p.add_argument("--bundle", help="MemberMouse bundle (csak MemberMouse-os oldalon; üres = nyilvános)")
        p.add_argument("--externalize-images", action="store_true",
                       help="a beágyazott base64 képeket a médiatárba tölti, és URL-re cseréli")
        p.add_argument("--no-double", action="store_true",
                       help="ne duplázza a backslasheket (alapból duplázza, mert a bővítmény elvesz egy szintet)")

    p = sub.add_parser("create", help="új oldal létrehozása")
    p.add_argument("--slug", required=True, help="az URL vége, pl. ingyenes-webinar")
    p.add_argument("--title", required=True, help="az oldal címe a WordPress adminban")
    p.add_argument("--html", required=True, help="a feltöltendő HTML fájl")
    p.add_argument("--parent", help="szülőoldal slugja (aloldalhoz)")
    write_opts(p)

    p = sub.add_parser("update", help="meglévő oldal felülírása (--yes kell hozzá)")
    p.add_argument("--id", type=int)
    p.add_argument("--slug", help="az oldal megkeresése slug alapján (a slugot nem változtatja meg)")
    p.add_argument("--html", help="az új HTML fájl")
    p.add_argument("--title")
    p.add_argument("--yes", action="store_true", help="a felhasználó jóváhagyta a felülírást")
    write_opts(p)

    p = sub.add_parser("delete", help="oldal törlése (--yes kell hozzá)")
    p.add_argument("--id", type=int)
    p.add_argument("--slug")
    p.add_argument("--yes", action="store_true", help="a felhasználó kifejezetten jóváhagyta a törlést")

    p = sub.add_parser("media", help="kép feltöltése a médiatárba")
    p.add_argument("--file", help="helyi képfájl")
    p.add_argument("--url", help="kép URL-je az internetről")
    p.add_argument("--filename", help="fájlnév a médiatárban (ne egyezzen egy oldal slugjával)")
    p.add_argument("--alt", help="helyettesítő szöveg")
    return ap


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    args = build_parser().parse_args(argv)
    site, key = load_config(args.config)
    client = Client(site, key)
    commands = {"info": cmd_info, "list": cmd_list, "get": cmd_get, "create": cmd_create,
                "update": cmd_update, "delete": cmd_delete, "media": cmd_media}
    try:
        commands[args.cmd](client, args)
    except ApiError as e:
        hint = {401: "hiányzik az API-kulcs a kérésből",
                403: "érvénytelen API-kulcs: generálj újat a WordPress adminban (Claude Oldalak menü)",
                404: "nincs ilyen oldal (ellenőrizd az ID-t vagy a slugot), vagy nincs aktiválva a bővítmény",
                429: "túl sok kérés, várj pár percet"}.get(e.status, "")
        sys.exit(f"Hiba: HTTP {e.status} {hint}\n{json.dumps(e.body, ensure_ascii=False) if not isinstance(e.body, str) else e.body}")


if __name__ == "__main__":
    main()
