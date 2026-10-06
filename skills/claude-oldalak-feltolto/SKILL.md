---
name: claude-oldalak-feltolto
description: >
  Kész HTML oldalak feltöltése és szerkesztése a saját WordPress oldaladon, a Claude Oldalak
  bővítmény REST API-jával. A feliratkozo-oldal, webinar-koszonooldal és
  ertekesitesi-oldal-keszito skill által készített oldalakat teszi élesbe: új oldal saját
  URL-en, meglévő oldal átírása, oldalak listázása, kép feltöltése a médiatárba, törlés csak
  megerősítés után. Minden írás után visszaolvassa és ellenőrzi az oldalt, és megadja az élő
  linket. Használd, ha a kérés: "töltsd fel az oldalt", "tedd fel a weboldalamra", "tedd ki
  WordPressre", "publikáld az oldalt", "írd át az oldalon", "cseréld le a főcímet az oldalon",
  "milyen oldalaim vannak", "listázd az oldalakat", "töröld az oldalt", "töltsd fel a képet a
  médiatárba", "Claude Oldalak", "WordPress bővítmény API-kulcs", vagy ha HTML fájl és URL
  érkezik együtt.
---

# Claude Oldalak feltöltő

Ez a skill a felhasználó **saját WordPress oldalára** teszi fel azokat a HTML oldalakat,
amelyeket a többi skill készít: feliratkozó oldal (`feliratkozo-oldal`), köszönőoldal
(`webinar-koszonooldal`), értékesítési oldal (`ertekesitesi-oldal-keszito`). Ehhez a
**Claude Oldalak** WordPress-bővítmény kell. Letöltés és telepítési útmutató:
https://domarketing.hu/plugin/

A munkát a `scripts/oldalak.py` segédszkript végzi (csak a Python alapkönyvtárát használja).
Az API részletei, ha kézzel kell hívni: `references/api.md`.

## Amit a bővítményről tudni kell

- Minden Claude-oldal egy WordPress-oldal a saját címén (`https://SAJATOLDALAD.hu/slug/`).
  A HTML-t a bővítmény teljes oldalként adja ki, a WordPress-sablon fejléce, menüje és
  lábléce nélkül. Ezért a feltöltött HTML legyen teljes, önálló oldal.
- A JavaScript fut az oldalon (visszaszámláló, GYIK-lenyitó, űrlap). A tartalom JavaScript
  nélkül is legyen olvasható.
- **Verziók:** minden módosításkor a bővítmény elmenti az előző állapotot. Visszaállítás a
  WordPress adminban: Claude Oldalak menü, az oldal sorában Verziók, ott Előnézet vagy
  Visszaállítás.
- Ellenőrizd az első feltöltés után, hogy a mérőkódjaid (például Facebook pixel, Google
  Analytics) betöltődnek-e a Claude-oldalon. Ha nem, a HTML-be kell tenni őket.

---

## 1. Beállítás (egyszer kell)

1. **Bővítmény:** töltsd le a `claude-oldalak.zip` fájlt a https://domarketing.hu/plugin/
   oldalról, és telepítsd: WordPress admin, Bővítmények, Új hozzáadása, Bővítmény feltöltése,
   Telepítés most, Aktiválás.
2. **API-kulcs:** a WordPress adminban a Claude Oldalak menüben generálj új kulcsot
   („Új API kulcs generálása”). A teljes kulcs **csak egyszer látszik**, rögtön másold ki.
   Érdemes külön kulcsot csinálni Claude-nak, hogy szükség esetén azt az egyet vissza
   tudd vonni.
3. **Add meg Claude-nak** az oldalad címét és a kulcsot, a környezettől függően:

### Claude Code (vagy más, a saját gépeden futó környezet)

A kulcs környezeti változóba vagy egy helyi konfigurációs fájlba kerül, **minden megosztott
vagy nyilvános mappán kívül**: soha ne a skill mappájába, ne egy git-repóba, ne közös
Drive- vagy Dropbox-mappába.

```bash
export CLAUDE_OLDALAK_SITE="https://SAJATOLDALAD.hu"
export CLAUDE_OLDALAK_API_KEY="IDE_JON_A_KULCS"
```

Vagy fájlban, amit a szkript magától megtalál: `~/.config/claude-oldalak/config.json`
(Windowson a felhasználói mappádban: `.config\claude-oldalak\config.json`):

```json
{"site": "https://SAJATOLDALAD.hu", "api_key": "IDE_JON_A_KULCS"}
```

Legjobb, ha ezt a fájlt a felhasználó maga hozza létre, így a kulcs nem megy át a
beszélgetésen.

### claude.ai

A felhasználó a beszélgetésbe másolja az oldal címét és a kulcsot. Te a kulcsot egy
ideiglenes konfigurációs fájlba írod a munkakörnyezet temp mappájában (ne a kimeneti
mappába, ne a skill mappájába), és a szkriptnek `--config` kapcsolóval adod át.

**Hálózat:** a claude.ai kódfuttató környezete nem feltétlenül éri el bármelyik weboldalt.
Ha az `info` parancs hálózati hibát ad, a beállításokban engedélyezni kell a hálózati
hozzáférést az oldalad domainjére (ha a csomagod ezt lehetővé teszi). Ha ez nem megy,
használd a Claude Desktopot vagy a Claude Code-ot; Claude Code-ban a kérések a saját
gépedről mennek.

### A kulcs kezelése

- Úgy kezeld, mint egy jelszót: aki ismeri, átírhatja az oldalaidat.
- **Soha ne írd vissza** a kulcsot a válaszaidban, ne írasd ki (`cat`, `echo`), és ne
  tedd semmilyen kimeneti fájlba. A szkript sem írja ki.
- Ha a kulcs illetéktelen helyre került, a WordPress adminban töröld, és generálj újat.

**Kapcsolat-próba:** `python scripts/oldalak.py info` (a válaszban `"status": "connected"`).

---

## 2. Munkamenet

### Új oldal feltöltése

1. Ha nincs megadva, kérdezd meg a **slugot** (az URL vége) és az oldal **címét** (ez csak a
   WordPress adminban látszik). Slug: ékezet nélküli kisbetű, szám, kötőjel, például
   `ingyenes-webinar`, `webinar-koszonjuk`, `ajanlat`.
2. Nézd meg, foglalt-e: `python scripts/oldalak.py get --slug ingyenes-webinar` (a 404 a jó
   válasz).
3. Ha a HTML-ben base64-be ágyazott képek vannak, töltsd őket a médiatárba
   (`--externalize-images`), így az oldal kicsi és gyors lesz.
4. Feltöltés:

   ```bash
   python scripts/oldalak.py create --slug ingyenes-webinar --title "Ingyenes webinár" \
       --html feliratkozo.html --externalize-images
   ```

5. A szkript visszaolvassa az oldalt, összeveti a feltöltött HTML-lel, és lekéri az élő
   címet. Add meg a felhasználónak az **élő URL-t** kattintható linkként, és kérd meg, hogy
   nézze meg mobilon is.

Ha még nem végleges az oldal, javasolj egy próba-slugot (például `webinar-proba`). A slug
később nem írható át API-ból (lásd a csapdáknál), ezért a végleges változat új oldalként
kerül a végleges címre, a próbaoldalt pedig megerősítés után törlöd.

### Meglévő oldal módosítása

1. Keresd meg: `list`, vagy `get --slug ...`. Mentsd le a mostani HTML-t:
   `python scripts/oldalak.py get --slug ingyenes-webinar --out jelenlegi.html`
2. A módosítást a lementett fájlon végezd (vagy a felhasználó új fájlt ad).
3. **Felülírás előtt kérj megerősítést**, ha az oldal élő: mondd meg, melyik oldalt
   (cím, URL) és mit cserélsz. A szkript `--yes` nélkül nem ír felül semmit.
4. Frissítés és ellenőrzés:

   ```bash
   python scripts/oldalak.py update --slug ingyenes-webinar --html uj.html --yes
   ```

5. Add meg az élő URL-t, és szólj, hogy az előző változat a WordPress adminban
   visszaállítható.

### Törlés

Csak **kifejezett felhasználói megerősítés** után, amelyben látta az oldal címét és URL-jét.
Először futtasd `--yes` nélkül (kiírja, mit törölne), mutasd meg, és csak az igen után:

```bash
python scripts/oldalak.py delete --slug webinar-proba --yes
```

A törlést kezeld visszavonhatatlannak.

### Kép a médiatárba

```bash
python scripts/oldalak.py media --file boritokep.jpg --alt "Borítókép"
python scripts/oldalak.py media --url "https://pelda.hu/kep.jpg" --alt "Kép"
```

A válaszban kapott `url`-t tedd a HTML-be. Ugyanazt a képet a bővítmény nem tölti fel
kétszer (`"dedup": true`).

### Kezdőlap

Ha a Claude-oldal legyen a főoldal: töltsd fel a szokásos módon, aztán a WordPress
adminban Beállítások, Olvasás, „Egy statikus oldal”, és ott válaszd ki kezdőlapnak.

---

## 3. A segédszkript parancsai

A parancsokat a skill mappájából futtasd, vagy add meg a szkript teljes útvonalát.
Súgó: `python scripts/oldalak.py --help` (és például `create --help`).

| Parancs | Mire való |
|---|---|
| `info` | kapcsolat és bővítményverzió |
| `list` | a Claude-oldalak listája (ID, állapot, slug, cím, URL) |
| `get --id N` / `get --slug s [--out f.html]` | egy oldal adatai, HTML mentése fájlba |
| `create --slug s --title t --html f.html` | új oldal; opcionális: `--parent`, `--externalize-images` |
| `update --id N` vagy `--slug s` `--html f.html --yes` | felülírás; `--title` is mehet |
| `delete --id N` vagy `--slug s` `--yes` | törlés |
| `media --file f.jpg` / `--url ...` `[--alt ...]` | kép a médiatárba |

Amit a szkript magától elvégez: a backslashek duplázása (lásd lent), a 4 bájtos karakterek
(emojik) HTML-entitássá alakítása, újrapróba 429-es válasz után, visszaolvasás és
összevetés minden írás után, az élő oldal HTTP-állapotának lekérése.

---

## 4. Csapdák (mind előfordult a gyakorlatban)

1. **A bővítmény elveszi a backslasheket.** Tároláskor a WordPress egy szint `\` jelet
   eltávolít (`wp_unslash`). Sima HTML-nél ez nem gond, de beágyazott JavaScriptben
   (regex, `\d`, `\+`, `\x3C/script>`) a script szintaktikai hibával leáll, és például egy
   beágyazott feliratkozó űrlap némán nem működik. **Megoldás:** küldés előtt minden `\`
   duplázva megy (a szkript ezt alapból csinálja), utána GET-tel ellenőrizd, hogy a tárolt
   HTML egyezik a szándékolttal. Ha egy későbbi bővítményverzió már nem venné el őket, a
   szkript ezt észreveszi, és duplázás nélkül újraküldi.
2. **A slug API-ból nem módosítható.** A `PUT` a `slug` mezőt csendben figyelmen kívül
   hagyja (200-as választ ad, de a cím nem változik). Átírás: WordPress admin, Oldalak,
   az oldalnál Gyors szerkesztés, ott a slug mező. Vagy: új oldal a kívánt címen, és a
   régi törlése megerősítés után. A régi címre mutató linkeket (hirdetés, e-mail, menü)
   ilyenkor frissíteni kell, vagy átirányítást kell beállítani.
3. **A médiatár kb. 10 gyors feltöltés után 429-et ad** (túl sok kérés). Várj 20-40
   másodpercet, és próbáld újra. A szkript képek között 6,5 másodpercet vár, 429 után
   20 másodpercet, és többször újrapróbál. A képek utáni oldalfeltöltés is kaphat 429-et.
4. **Lazy-load és gyorsítótár-bővítmény (például WP Rocket, LiteSpeed Cache).** Az inline
   `style="background-image:url(...)"` háttérképet ezek átírhatják, és a kép nem jelenik
   meg. A háttérképet mindig a `<style>` blokkban, osztályra add meg:
   `.hero{background-image:url('https://...')}`. A hajtás feletti (hero) `<img>` kapjon
   `loading="eager"` és `data-no-lazy="1"` attribútumot, különben üres keret maradhat a
   helyén. A folyamatosan futó inline scriptek (visszaszámláló) kapjanak
   `data-no-optimize="1" data-no-defer="1" data-cfasync="false"` attribútumot.
5. **Ha törölsz egy médiafájlt, amit egy oldal még használ, a kép eltörik** az oldalon.
   Médiatárból csak akkor törölj, ha biztos, hogy egyik oldal sem hivatkozik rá.
6. **Gyorsítótár:** ha a tárhelyen vagy egy bővítményben gyorsítótár fut, frissítés után a
   látogató még a régi változatot láthatja. Ilyenkor ürítsd a gyorsítótárat. Ellenőrzésnél
   vigyázz: egy query paraméter (`?v=2`) megkerülheti a gyorsítótárat, és friss tartalmat
   mutat, miközben a sima cím még a régit adja. A `?m=` paramétert ne használd tesztre
   (a WordPress archívumnak veszi, és 404-et ad); az `?utm_source=teszt` jó.
7. **409 (foglalt slug)** akkor is jöhet, ha egy sima WordPress-oldal vagy egy médiafájl
   foglalja azt a címet. Ezért képfeltöltésnél a fájlnév ne egyezzen egy tervezett oldal
   slugjával.

---

## 5. Tagsági oldal (csak MemberMouse-os oldalon)

Ha a WordPress oldalon MemberMouse fut, egy oldal tagsági bundle mögé zárható a
`required_bundle` mezővel (a szkriptben `--bundle`): a bundle számazonosítója, vagy
kifejezés (`"2|6"` bármelyik, `"2&6"` mindkettő, `"!4"` kivéve). Üres érték: nyilvános oldal.
A bundle azonosítóját a MemberMouse beállításaiban találod. Kijelentkezve teszteld, hogy a
védelem működik-e. MemberMouse nélkül ennek a mezőnek nincs hatása.

---

## 6. Hibakódok

| Válasz | Jelentés | Teendő |
|---|---|---|
| 401 | hiányzik a kulcs a kérésből | nézd meg a beállítást |
| 403 | érvénytelen kulcs | új kulcs a WordPress adminban (Claude Oldalak menü) |
| 404 | nincs ilyen oldal, vagy nincs aktiválva a bővítmény | ID, slug, bővítmény ellenőrzése |
| 409 | foglalt slug | `update` a meglévőre, vagy másik slug |
| 429 | túl sok kérés | várj, aztán újra |
| hálózati hiba | a környezet nem éri el az oldalt | claude.ai-on lásd a hálózati részt |

## Végrehajtási elvek

- Minden írás után GET-tel ellenőrizz, és add meg az élő URL-t.
- Törlés és élő oldal felülírása csak kifejezett megerősítés után.
- A kulcsot soha ne írd ki, és ne mentsd megosztott helyre.
- Ha az ID nem ismert, slug alapján keresd meg.
