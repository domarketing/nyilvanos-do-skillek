# Claude Oldalak REST API

Akkor kell, ha a `scripts/oldalak.py` valamiért nem futtatható, vagy olyat kell csinálni,
amit a szkript nem tud. Minden más esetben a szkriptet használd.

## Alapok

- **Alapcím:** `https://SAJATOLDALAD.hu/wp-json/claude-oldalak/v1`
- **Hitelesítés:** `X-Claude-API-Key: <kulcs>` fejléc minden kérésben
- **Törzs:** JSON, `Content-Type: application/json; charset=utf-8`

## Végpontok

| Metódus | Útvonal | Törzs | Válasz |
|---|---|---|---|
| GET | `/info` | | kapcsolat és verzió (`"status": "connected"`) |
| GET | `/pages` | | lista: `[{id, title, slug, url, status}, ...]` |
| POST | `/pages` | `slug`, `title`, `html`; opcionális `parent_slug`, `required_bundle` | 201: `{id, url, slug, title}`; 409: `slug_exists` |
| GET | `/pages/{id}` | | az oldal adatai, benne a `html` |
| PUT | `/pages/{id}` | bármelyik: `html`, `title`, `status`, `required_bundle` | a frissített oldal adatai |
| DELETE | `/pages/{id}` | | törlés |
| GET | `/pages/slug/{slug}` | | az oldal adatai slug alapján (404, ha nincs) |
| POST | `/media` | `{url}` vagy `{base64, filename, alt}` | `{id, url, mime, dedup}` |

Megjegyzések:

- A `PUT` a `slug` mezőt nem veszi figyelembe (lásd a SKILL.md csapdáit).
- A `required_bundle` csak MemberMouse-os oldalon csinál bármit.
- A `/media` azonos képnél a meglévő URL-t adja vissza (`dedup: true`).
- Gyors egymás utáni hívásoknál bármelyik végpont adhat 429-et.

## Minimális Python-minta (csak alapkönyvtár)

```python
import json, os, time, urllib.request, urllib.error

SITE = os.environ["CLAUDE_OLDALAK_SITE"].rstrip("/")
BASE = SITE + "/wp-json/claude-oldalak/v1"
HEADERS = {
    "X-Claude-API-Key": os.environ["CLAUDE_OLDALAK_API_KEY"],
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "claude-oldalak-feltolto/1.0",
}

def call(method, path, payload=None):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    for _ in range(6):
        req = urllib.request.Request(BASE + path, data=data, method=method, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.status, json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(20)
                continue
            return e.code, json.loads(e.read().decode() or "{}")
    return 429, {}

def safe_html(html):
    """Emojik (4 bájtos karakterek) HTML-entitássá."""
    return "".join(f"&#{ord(c)};" if ord(c) > 0xFFFF else c for c in html)

def to_send(html):
    """A bővítmény tároláskor egy szint backslasht elvesz, ezért duplázzuk."""
    return html.replace("\\", "\\\\")

html = safe_html(open("oldal.html", encoding="utf-8").read())
status, page = call("POST", "/pages", {"slug": "ingyenes-webinar",
                                       "title": "Ingyenes webinár",
                                       "html": to_send(html)})
# Ellenőrzés: a tárolt HTML egyezzen a szándékolttal
_, stored = call("GET", f"/pages/{page['id']}")
assert stored["html"].replace("\r\n", "\n") == html.replace("\r\n", "\n"), "eltérés a tárolt HTML-ben"
print(page["url"])
```

A kulcsot ne írd bele a kódba: környezeti változóból vagy helyi konfigurációs fájlból jöjjön.
