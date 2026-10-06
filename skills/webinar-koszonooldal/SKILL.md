---
name: webinar-koszonooldal
description: "Webinár-feliratkozás utáni köszönőoldal (thank-you page) készítése önálló HTML-ben, a vállalkozás saját arculatával: visszaszámláló, hasznos infók listája, opcionális élő csatlakozás gomb és Google Naptár link. Ha van cegprofil.md, abból veszi a színeket, betűket, a cégnevet, az ügyfélszolgálati e-mailt és a jogi linkeket; ha a feliratkozó oldal ugyanebben a beszélgetésben készült, annak arculatát követi. Használd, ha ezt kérik: 'köszönőoldal', 'koszonooldal', 'thank you page', 'visszaigazoló oldal', 'sikeres feliratkozás oldal', 'webinár megerősítés', 'registration confirmation', 'mi jelenjen meg feliratkozás után', 'oldal a regisztráció után'. A feliratkozó oldalhoz a feliratkozo-oldal, fizetős ajánlathoz az ertekesitesi-oldal-keszito való."
---

# Webinár köszönőoldal készítő

Ez a skill önálló HTML köszönőoldalt készít webinár-feliratkozás utánra, a felhasználó
arculatával és a megadott webinár-adatokkal.

---

## 1. lépés: arculat és cégadatok

Ha van `cegprofil.md` (a projekt fájljai között, a munkamappában vagy a beszélgetésben),
abból dolgozz. Ezeket veszed belőle:

- **PRIMARY_COLOR, SECONDARY_COLOR:** az elsődleges és a másodlagos márkaszín;
- **FONT_HEADING, FONT_BODY:** a főcím és a szövegtörzs betűtípusa;
- **cégnév, ügyfélszolgálati e-mail, ÁSZF-, adatvédelmi és cookie-tájékoztató link** a
  lábléchez;
- **ideális vásárló:** ehhez igazítod az „ismerős meghívása” sor szövegét.

Ha a feliratkozó oldal ugyanebben a beszélgetésben készült (például a `feliratkozo-oldal`
skillel), ugyanazokat a színeket és betűket használd, hogy a két oldal összetartozzon.

Ha egyik sincs meg, kérdezd meg a hiányzó minimumot, vagy ajánld fel a `cegprofil` skillt.
Ha a felhasználó nem akar arculatot megadni, ezek a semleges alapértékek:

- **PRIMARY_COLOR:** `#2F4B9A` (sötétkék)
- **SECONDARY_COLOR:** `#F2A93B` (borostyán)
- **FONT_HEADING:** `Montserrat`
- **FONT_BODY:** `Inter`
- **Google Fonts URL:**
  `https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Montserrat:wght@400;700;800;900&display=swap`

Más betűknél a Google Fonts URL-t a felhasználó betűiből állítsd össze.

---

## 2. lépés: adatgyűjtés

Kérdezd meg az alábbiakat. Ha elérhető kérdezős eszköz (claude.ai-on az `ask_user_input`),
azzal, különben egy összesített kérdésben. Ami a cégprofilban megvan, azt ne kérdezd újra.
**Soha ne találj ki adatot.**

1. **Mikor lesz a webinár?** Dátum és pontos időpont, például „2026. június 15. 10:00–11:30”.
2. **Van-e Google Naptár esemény link?** Igen vagy nem. Ha igen, kérd el a teljes URL-t.
3. **Van-e már élő csatlakozási link?** Igen vagy nem. Ha igen, kérd el az URL-t. Ha nem,
   csak a visszaszámláló kerül be, a gombot később kézzel be lehet kapcsolni.
4. **Mi a webinár címe?** Ez kerül a böngészőfül címébe és a hero sávba. Például: „Hogyan
   duplázd meg a bevételed 6 hónap alatt?”
5. **Mi az ügyfélszolgálati e-mail cím?** Ide írhatnak, ha nem kapták meg a visszaigazolót.
   Például: `info@pelda.hu`.
6. **Hol lesz az előadás?** Zoom, YouTube élő, saját oldal vagy más. Ebből lesz a
   „Helyszín” sor szövege.
7. **Cégnév és jogi linkek** a lábléchez, ha nincsenek a cégprofilban.

---

## 3. lépés: a visszaszámláló időpontja

A visszaszámláló a webinár kezdetét Unix-időbélyegként kapja, másodpercben.

**Kiszámítás:** a megadott magyar időpontot váltsd UTC-re (télen CET = UTC+1, nyáron
CEST = UTC+2), és abból számold az időbélyeget. Például:
`2026. június 15. 10:00 CEST` → `1781510400`.

Ha van kódfuttatás, számold ki pontosan, például Pythonban:

```python
from datetime import datetime, timezone, timedelta
int(datetime(2026, 6, 15, 10, 0, tzinfo=timezone(timedelta(hours=2))).timestamp())
```

Ha bizonytalan vagy az értékben, jelezd egy HTML-kommentben, hogy feltöltés előtt kézzel
ellenőrizni kell.

---

## 4. lépés: a placeholderek

| Placeholder | Leírás |
|---|---|
| `{{PRIMARY}}` | Elsődleges szín (hex), például `#2F4B9A` |
| `{{SECONDARY}}` | Másodlagos szín (hex), például `#F2A93B` |
| `{{FONT_HEADING}}` | Főcím betűtípusa, például `Montserrat` |
| `{{FONT_BODY}}` | Szövegtörzs betűtípusa, például `Inter` |
| `{{GOOGLE_FONTS_URL}}` | Google Fonts importáló URL |
| `{{PAGE_TITLE}}` | A böngészőfülön megjelenő cím |
| `{{WEBINAR_TITLE}}` | Az előadás címe az oldalon |
| `{{WEBINAR_DATE_TEXT}}` | Megjelenített dátum, például `2026. június 15. 10:00–11:30` |
| `{{UNIX_TIMESTAMP_SECONDS}}` | A visszaszámláló célpontja, másodpercben |
| `{{LOCATION_TEXT}}` | A „Helyszín” sor szövege, például `online, Zoomon; a csatlakozási linket e-mailben küldjük.` |
| `{{CALENDAR_LINK_HREF}}` | Google Naptár URL (vagy `#`, ha nincs) |
| `{{CALENDAR_LINK_VISIBLE}}` | `flex`, ha van Google Naptár link, `none`, ha nincs |
| `{{LIVE_BUTTON_VISIBLE}}` | `block`, ha van élő link, `none`, ha nincs |
| `{{LIVE_LINK_HREF}}` | Élő csatlakozás URL (vagy `#`, ha még nincs) |
| `{{LIVE_BUTTON_PLACEHOLDER_NOTE}}` | Ha nincs link: HTML-komment teendővel (lásd 6. lépés) |
| `{{INVITE_TEXT}}` | Az ismerős meghívása sor vége, az ideális vásárlóhoz igazítva, például `aki szintén a vállalkozását szeretné felpörgetni!` |
| `{{IMAGE_PLACEHOLDER_BG}}` | A kép-helyőrző háttérszíne (a PRIMARY-ból levezetve) |
| `{{SUPPORT_EMAIL}}` | Ügyfélszolgálati e-mail cím |
| `{{COMPANY_NAME}}` | Cégnév a láblécben |
| `{{ASZF_URL}}` | Általános szerződési feltételek URL |
| `{{PRIVACY_URL}}` | Adatvédelmi tájékoztató URL |
| `{{COOKIE_URL}}` | Cookie-tájékoztató URL |

Ha egy jogi link hiányzik, a helyére `#` kerül, és fölé egy
`<!-- TEENDŐ: add meg a ... linkjét -->` komment.

---

## 5. lépés: HTML sablon

Ezt a sablont töltsd ki a fenti placeholderekkel:

```html
<!DOCTYPE html>
<html lang="hu">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex, nofollow">
  <title>{{PAGE_TITLE}}</title>
  <link href="{{GOOGLE_FONTS_URL}}" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root {
      --primary: {{PRIMARY}};
      --secondary: {{SECONDARY}};
    }
    body {
      font-family: '{{FONT_BODY}}', sans-serif;
    }
    h1, h2, h3, .font-heading {
      font-family: '{{FONT_HEADING}}', sans-serif;
    }
    .btn-primary {
      background-color: var(--secondary);
      color: #111;
      font-family: '{{FONT_HEADING}}', sans-serif;
      font-weight: 800;
      transition: opacity 0.2s;
    }
    .btn-primary:hover { opacity: 0.88; }
    .countdown-box {
      background: var(--primary);
      color: #fff;
    }
    .icon-color { color: var(--primary); }
    .badge-bg { background: var(--secondary); }
    .hero-bg { background: var(--primary); }
    .footer-bg { background: var(--primary); }
    .image-placeholder {
      background-color: {{IMAGE_PLACEHOLDER_BG}};
      aspect-ratio: 1 / 1;
      border-radius: 1rem;
      display: flex;
      align-items: center;
      justify-content: center;
      color: rgba(255,255,255,0.4);
      font-size: 0.85rem;
      font-family: '{{FONT_BODY}}', sans-serif;
      text-align: center;
    }
    /* Visszaszámláló */
    #countdown { display: flex; gap: 0.75rem; justify-content: center; flex-wrap: wrap; }
    .countdown-item {
      display: flex; flex-direction: column; align-items: center;
      min-width: 64px;
    }
    .countdown-digits {
      background: var(--primary);
      color: #fff;
      font-family: '{{FONT_HEADING}}', sans-serif;
      font-size: 2rem;
      font-weight: 800;
      border-radius: 0.5rem;
      padding: 0.35rem 0.75rem;
      min-width: 60px;
      text-align: center;
    }
    .countdown-label {
      font-size: 0.75rem;
      color: #555;
      margin-top: 4px;
      font-weight: 600;
    }
    /* Infólista */
    .info-item { display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.6rem 0; }
    .info-icon { flex-shrink: 0; width: 22px; height: 22px; margin-top: 2px; }
    /* Élő csatlakozás gomb */
    .live-section { display: {{LIVE_BUTTON_VISIBLE}}; }
    /* Naptár link */
    .calendar-item { display: {{CALENDAR_LINK_VISIBLE}}; }
  </style>
</head>
<body class="bg-gray-50 text-gray-800">

  <!-- HERO SÁV -->
  <section class="hero-bg py-10 px-4 text-white text-center">
    <div class="max-w-2xl mx-auto">
      <div class="inline-block badge-bg text-gray-900 text-xs font-bold uppercase tracking-widest px-4 py-1 rounded-full mb-4 font-heading">
        ✓ Feliratkoztál az előadásra!
      </div>
      <h1 class="text-3xl md:text-4xl font-heading font-black leading-tight mb-3">
        Hamarosan találkozunk az előadáson!
      </h1>
      <p class="text-base md:text-lg opacity-80 mb-2">
        {{WEBINAR_TITLE}}
      </p>
    </div>
  </section>

  <!-- FŐTARTALOM -->
  <section class="max-w-5xl mx-auto px-4 py-10">
    <div class="grid md:grid-cols-2 gap-8 items-start">

      <!-- BAL OLDAL: kép-helyőrző és üzenet -->
      <div class="flex flex-col items-center gap-5">
        <!-- KÉP IDE: cseréld ki img tagra -->
        <div class="image-placeholder w-full max-w-sm">
          <span>Előadás / előadó képe<br>ide kerül</span>
        </div>
        <p class="text-sm text-gray-500 italic text-center max-w-xs">
          Ha 10 percen belül nem kapsz tőlünk e-mailt, írj a
          <a href="mailto:{{SUPPORT_EMAIL}}" class="underline" style="color: var(--primary);">{{SUPPORT_EMAIL}}</a> címre!
        </p>
        <h2 class="text-xl font-heading font-bold text-center" style="color: var(--primary);">
          Találkozunk: {{WEBINAR_DATE_TEXT}}
        </h2>
      </div>

      <!-- JOBB OLDAL: hasznos infók -->
      <div>
        <h2 class="text-xl font-heading font-bold mb-4">Hasznos infók a webinárról</h2>
        <div class="space-y-1">

          <!-- Időpont -->
          <div class="info-item">
            <svg class="info-icon icon-color" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
            </svg>
            <span><b>Időpont:</b> {{WEBINAR_DATE_TEXT}}</span>
          </div>

          <!-- Helyszín -->
          <div class="info-item">
            <svg class="info-icon icon-color" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path d="M5 13l4 4L19 7"/>
            </svg>
            <span><b>Helyszín:</b> {{LOCATION_TEXT}}</span>
          </div>

          <!-- Hívd meg ismerősöd -->
          <div class="info-item">
            <svg class="info-icon icon-color" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            <span><b>Hívd meg azt az ismerősödet is,</b> {{INVITE_TEXT}}</span>
          </div>

          <!-- Google Naptár link, csak ha van -->
          <div class="info-item calendar-item">
            <svg class="info-icon icon-color" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/><path d="M9 16l2 2 4-4"/>
            </svg>
            <a href="{{CALENDAR_LINK_HREF}}" target="_blank" class="font-bold underline" style="color: var(--primary);">
              Írd be a naptáradba az időpontot, hogy biztosan ne maradj le róla!
            </a>
          </div>

          <!-- Nyugodt hely -->
          <div class="info-item">
            <svg class="info-icon icon-color" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
            <span>Keress egy nyugodt helyet, ahol <b>senki sem zavar meg</b>, így tudod kihozni az előadásból a legtöbbet.</span>
          </div>

        </div>
      </div>

    </div>
  </section>

  <!-- VISSZASZÁMLÁLÓ SZEKCIÓ -->
  <section class="max-w-2xl mx-auto px-4 pb-4 text-center">

    <!-- Élő link gomb, csak ha van -->
    {{LIVE_BUTTON_PLACEHOLDER_NOTE}}
    <div class="live-section mb-6">
      <h2 class="text-lg font-heading font-bold mb-3">Kattints ide, és csatlakozz az élő adáshoz!</h2>
      <a href="{{LIVE_LINK_HREF}}" target="_blank"
         class="btn-primary inline-block px-8 py-3 rounded-full text-base font-heading font-black shadow-md">
        Csatlakozom →
      </a>
    </div>

    <!-- Visszaszámláló -->
    <div class="mb-2">
      <p class="text-sm text-gray-500 mb-3 font-semibold uppercase tracking-wide">Az előadásig hátravan:</p>
      <div id="countdown">
        <div class="countdown-item">
          <span class="countdown-digits" id="cd-days">00</span>
          <span class="countdown-label">nap</span>
        </div>
        <div class="countdown-item">
          <span class="countdown-digits" id="cd-hours">00</span>
          <span class="countdown-label">óra</span>
        </div>
        <div class="countdown-item">
          <span class="countdown-digits" id="cd-minutes">00</span>
          <span class="countdown-label">perc</span>
        </div>
        <div class="countdown-item">
          <span class="countdown-digits" id="cd-seconds">00</span>
          <span class="countdown-label">másodperc</span>
        </div>
      </div>
    </div>

  </section>

  <!-- LÁBLÉC -->
  <footer class="footer-bg text-white py-6 px-4 mt-6">
    <div class="max-w-3xl mx-auto text-center text-sm opacity-80 space-y-1">
      <p>{{COMPANY_NAME}} –
        <a href="{{ASZF_URL}}" class="underline">Általános szerződési feltételek</a> –
        <a href="{{PRIVACY_URL}}" class="underline">Adatvédelmi tájékoztató</a> –
        <a href="{{COOKIE_URL}}" class="underline">Cookie-tájékoztató</a>
      </p>
      <p>Ügyfélszolgálat: <a href="mailto:{{SUPPORT_EMAIL}}" class="underline">{{SUPPORT_EMAIL}}</a></p>
    </div>
  </footer>

  <!-- VISSZASZÁMLÁLÓ SZKRIPT -->
  <script>
    const targetTimestamp = {{UNIX_TIMESTAMP_SECONDS}} * 1000; // milliszekundumba

    function updateCountdown() {
      const now = Date.now();
      const diff = targetTimestamp - now;

      if (diff <= 0) {
        document.getElementById('cd-days').textContent    = '00';
        document.getElementById('cd-hours').textContent   = '00';
        document.getElementById('cd-minutes').textContent = '00';
        document.getElementById('cd-seconds').textContent = '00';
        return;
      }

      const days    = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours   = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      document.getElementById('cd-days').textContent    = String(days).padStart(2, '0');
      document.getElementById('cd-hours').textContent   = String(hours).padStart(2, '0');
      document.getElementById('cd-minutes').textContent = String(minutes).padStart(2, '0');
      document.getElementById('cd-seconds').textContent = String(seconds).padStart(2, '0');
    }

    updateCountdown();
    setInterval(updateCountdown, 1000);
  </script>

</body>
</html>
```

---

## 6. lépés: az élő link kezelése

**Ha van élő link:**
- `{{LIVE_BUTTON_VISIBLE}}` → `block`
- `{{LIVE_LINK_HREF}}` → a megadott URL
- `{{LIVE_BUTTON_PLACEHOLDER_NOTE}}` → üres szöveg

**Ha nincs élő link:**
- `{{LIVE_BUTTON_VISIBLE}}` → `none`
- `{{LIVE_LINK_HREF}}` → `#`
- `{{LIVE_BUTTON_PLACEHOLDER_NOTE}}` → ez a HTML-komment:

```html
<!-- TEENDŐ: ha megvan az élő link:
     1. a CSS-ben a .live-section display értékét állítsd "block"-ra,
     2. a gomb href="#" értékét cseréld az élő link URL-jére.
     Ha nem kell gomb, a live-section blokk törölhető. -->
```

---

## 7. lépés: a Google Naptár link kezelése

**Ha van Google Naptár link:**
- `{{CALENDAR_LINK_VISIBLE}}` → `flex` (az info-item display értéke)
- `{{CALENDAR_LINK_HREF}}` → a megadott URL

**Ha nincs:**
- `{{CALENDAR_LINK_VISIBLE}}` → `none`
- `{{CALENDAR_LINK_HREF}}` → `#`

---

## 8. lépés: a kép-helyőrző

Valódi képet ne tegyél be, maradjon a könnyen cserélhető helyőrző. A színe a PRIMARY
áttetszőbb vagy kissé sötétebb változata legyen. Fölötte ott a komment:
`<!-- KÉP IDE: cseréld ki img tagra -->`. Ha a felhasználó ad portrét vagy webinár-képet,
azt `<img>` taggel tedd a helyőrző helyére.

---

## 9. lépés: mentés és átadás

Mentsd a kész HTML-t `webinar-koszonooldal.html` néven, vagy ha tudod a dátumot:
`webinar-koszonooldal-EVHONAP.html`.

Add át a fájlt (claude.ai-on a `present_files` eszközzel, Claude Code-ban a mentett
útvonallal), és röviden jelezd:
- az oldal önálló HTML, bármilyen tárhelyre feltölthető;
- ha még nincs élő link, a HTML-kommentben leírt módon később bekapcsolható;
- a képet a `<!-- KÉP IDE -->` kommentnél kell `<img src="...">` taggel behelyettesíteni;
- a visszaszámláló magától fut a beállított időpontig.

---

## Minőségi szabályok

- **Soha ne találj ki dátumot, URL-t vagy e-mail címet.** Ha hiányzik, kérdezz vissza, vagy
  jelöld kommenttel.
- **Ne maradjon `{{...}}` placeholder** a kész HTML-ben.
- **Az arculat a felhasználóé:** a cégprofil vagy a felhasználó színei és betűi, ezek
  hiányában a semleges alapértékek.
- **Az időbélyegnél** figyelj a magyar időzónára (CET vagy CEST).
- **Az oldal önálló,** Tailwind CDN-nel, semmit nem kell hozzá telepíteni.
- **Mérőkódot magadtól ne tegyél bele.** Ha a felhasználó kéri, az ő saját kódját illeszd be.

---

## Kötelező zárás: szövegellenőrzés

Amikor a szöveg elkészült, **még a leadás előtt** futtasd rajta a `szovegellenorzo` skillt.
Az szedi ki azokat a mintákat, amikről a magyar olvasó ma már felismeri az AI-t. A
szerkezethez nem nyúl, csak a megfogalmazáshoz.

## Kapcsolódó skillek

- `cegprofil`: innen jönnek az arculati és a cégadatok.
- `feliratkozo-oldal`: a feliratkozó oldal, amelyről ide érkezik a látogató.
- `ertekesitesi-level-iro`: a visszaigazoló, emlékeztető és utánkövető levelek.
- `claude-oldalak-feltolto`: ha a kész oldalt WordPressre kell feltölteni.
