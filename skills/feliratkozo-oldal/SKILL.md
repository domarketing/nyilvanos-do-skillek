---
name: feliratkozo-oldal
description: "Magyar feliratkozó (landing) oldal készítése önálló HTML-ben webinárhoz, ingyenes előadáshoz vagy több napos kihíváshoz, a vállalkozás saját arculatával. Három bevált, élesben futott minta-oldal felépítését és stílusát követi (kettő webináros, egy kihívásos), a szöveget a felhasználó adataiból írja. Webinárnál két változatot ad. Ha van cegprofil.md, abból veszi a színeket, betűket, a bemutatkozást és a valódi véleményeket. Használd, ha ezt kérik: 'csinálj feliratkozó oldalt', 'kell egy landing a webinárhoz', 'opt-in oldal', 'webinár oldal', 'kihívás oldal', 'regisztrációs oldal az előadásra', 'feliratkozó HTML', vagy ha valaki főcímet, dátumot és bullet pontokat ad meg, és HTML-t vár. Fizetős ajánlathoz az ertekesitesi-oldal-keszito, regisztráció utáni oldalhoz a webinar-koszonooldal való. Céges főoldalhoz, bloghoz, webshophoz ne használd."
---

# Feliratkozó oldal készítő

Ez a skill **három bevált, élesben futott magyar feliratkozó oldal** felépítése alapján
készít teljes, önálló feliratkozó oldalt a felhasználó adataiból, az ő arculatával.

A három minta a skill része, a `samples/` mappában van, így semmilyen külső fájl nem kell
hozzá. Részletes leírás: `samples/README.md`.

- `samples/webinar_minta_1_tizmillios_bevetel.html`: **webinár** minta #1
- `samples/webinar_minta_2_uj_vevok_futoszalagon.html`: **webinár** minta #2
- `samples/kihivas_minta_3napos_tudasbol_milliok.html`: **kihívás** minta

A bullet listákhoz kész, másolható HTML-darabok vannak a `references/snippetek.md`-ben.

## Alapelv: a minta a vázlat, a szöveg és az arculat a felhasználóé

A skill a minta **felépítését és vizuális logikáját** veszi át: a szekciók sorrendjét, az
elrendezést, a gomb- és bullet-stílust, a copywriting ritmusát. A szöveg, a színek, a betűk,
a képek és a nevek mindig a felhasználótól vagy a cégprofiljából jönnek.

## A mintákra vonatkozó szabály (kötelező)

A minták **csak a felépítéshez és a stílushoz** valók. Egy másik cég saját oldalai, ezért:

- **Soha ne másolj át** a mintákból mérőkódot, űrlap- vagy listaazonosítót, kép-URL-t,
  személynevet, véleményt (testimonialt), eredményszámot vagy marketingszöveget a felhasználó
  oldalába.
- A mintákban a képek már semleges szürke helyőrzők, a linkek és az űrlapok célja `#`.
  Ezeket se vidd át, a felhasználó saját képei és linkjei kellenek.
- A feliratkozó űrlap helyén a mintákban ez a komment áll:
  `<!-- ide jön a saját feliratkozó űrlapod beágyazó kódja -->`. A kész oldalon is ugyanígy
  jelöld a helyet, és oda a felhasználó **saját** űrlapkódja kerül (például SalesAutopilot,
  Mailchimp, MailerLite vagy más levelezőrendszer beágyazó kódja).

---

## 0. lépés: a cégprofil

Ha van `cegprofil.md` (a projekt fájljai között, a munkamappában vagy a beszélgetésben),
abból dolgozz. Ezeket veszed belőle:

- **arculat:** elsődleges, másodlagos és kiemelő szín, betűtípusok, logó;
- **ideális vásárló és hangnem:** ehhez igazítod a főcímet és a bulleteket;
- **a webinár, előadás, kihívás vagy ingyenes anyag adatai,** ha benne vannak;
- **bemutatkozás:** az előadó neve, elért eredményei, portréja a „Ki az a...” részhez;
- **valódi vélemények:** csak ezek kerülhetnek az oldalra, kitalált vélemény soha;
- **kapcsolat és jogi adatok:** cégnév, ügyfélszolgálati e-mail, ÁSZF- és adatvédelmi link
  a lábléchez.

Ha nincs cégprofil, kérdezd meg a hiányzó minimumot (lásd 2. lépés), vagy ajánld fel, hogy
előbb a `cegprofil` skillel elkészítitek.

---

## 1. lépés: a minta kiválasztása

- **Webinár (egyalkalmas előadás)** → **mindkét** webináros minta. Mindkettő stílusában
  készítesz egy-egy kész oldalt, hogy a felhasználó választhasson.
- **Több napos kihívás, sprint** → a kihívásos minta, egy oldal.
- **Ingyenes letölthető anyag (lead magnet)** → a webináros minták felépítése, dátum és
  időpont-blokk nélkül. Ilyenkor egy változat is elég, ha a felhasználó nem kér kettőt.

Ha a típus nem egyértelmű, egyszer kérdezz vissza.

---

## 2. lépés: adatgyűjtés

Ami a cégprofilban megvan, azt ne kérdezd újra. A hiányzókat egy összesített kérdésben kérd.
**Soha ne találj ki** dátumot, nevet, bullet-szöveget, eredményt vagy véleményt.

**Mindig kell:**
1. **Típus:** webinár, kihívás vagy letölthető anyag.
2. **Színek:** elsődleges és másodlagos hex kód, opcionálisan egy kiemelő szín (például a
   CTA-hoz). Ha sem a cégprofil, sem a felhasználó nem ad meg színt, semleges alap:
   sötétkék `#2F4B9A`, borostyán `#F2A93B`, éjkék `#0F1B3D`.
3. **Betűtípus:** legalább a főcímé. Ha nincs megadva: Montserrat (főcím) és Inter (szöveg).
4. **Főcím:** rövid, ütős mondat.
5. **Alcím:** zárójeles kiegészítés, például „(Néhány nap alatt, akár havonta)”.
6. **Dátum, időpont** (letölthető anyagnál nem kell).
7. **Bullet pontok** az „Ezekről lesz szó” vagy „Mire kell figyelned” részhez. Webinárnál
   5-7, kihívásnál naponként 4-6.
8. **Kép** a bullet pontok mellé, kihívásnál a hero-képhez (URL vagy feltöltött fájl).
9. **„Ki az a...” rész:** elért eredmények listája és portré.
10. **Galériaképek** (díjátadó, közönség, közös fotó): 0-3 darab, opcionális.
11. **Az űrlap:** van-e már beágyazó kódja? Ha igen, kérd el, és az űrlap helyére tedd.

**Csak kihívásnál ezek is:**
12. **Hero főcím-darabok:** a kihívás „márkaneve” (például „18M SPRINT”) és alcímkéje
    (például „kihívás”).
13. **Idézet** szerzővel (opcionális, ha nincs, kimarad).
14. **Napi blokkok** minden napra: dátum, idő, cím, bullet pontok, ajándék-blokk (cím és leírás).

**Alapértelmezett gombfeliratok,** ha a felhasználó nem ad meg sajátot: webinárhoz
„Ott akarok lenni!” vagy „Lefoglalom a helyem!”, kihíváshoz „ÉRDEKEL A KIHÍVÁS!” vagy
„IGEN, OTT AKAROK LENNI!”.

Ha valami hiányos (például három nap helyett csak kettőt adott meg), egyszer kérdezz vissza.

---

## 3. lépés: a minta beolvasása, a felépítés kinyerése

Olvasd be a kiválasztott mintá(ka)t. A minták megtisztított exportok: a mérőkódok, a
WordPress-szkriptek és a külső fájlhivatkozások már nincsenek bennük. A régi
Elementor-osztálynevek és stílusblokkok maradtak, ezért **ne másold át egy az egyben** a
fájlt, a kimenetet tisztán, elölről építsd fel.

Ezt veszed át:
- a **szekciók sorrendjét** (hero → „ezekről lesz szó” → „ki vagyok én?” → galéria → záró CTA
  és így tovább);
- a **vizuális logikát** (elrendezés, arányok, gombforma, bullet- és kártyastílus);
- a **copywriting ritmusát** (rövid ütős főcím, alcím zárójelben, bullet: erős fő gondolat
  és kifejtés).

Ezt nem veszed át: a minta szövegét, neveit, véleményeit, számait, képeit, linkjeit, az
Elementor-maradványokat és az eredeti színeket.

---

## 4. lépés: a kész oldal felépítése

Egyetlen önálló HTML-fájl, build és npm nélkül:

- **TailwindCSS CDN-ről:** `<script src="https://cdn.tailwindcss.com"></script>`, a
  felhasználó színeivel a `tailwind.config`-ban.
- **Fontok Google Fontsról,** a felhasználó betűi alapján. Példa:
  - Montserrat + Inter:
    `https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Montserrat:wght@400;700;800;900&display=swap`
  - Plus Jakarta Sans:
    `https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap`
  Ha nem tudod a súlyokat, tegyél be többet.
- **Színek:** a felhasználó színeit használd következetesen a gombokon, ikonokon és kiemeléseken.
- **Bullet listák:** a `references/snippetek.md` darabjai, annyiszor ismételve, ahány pont kell.
- **Ikonok:** inline SVG, ahogy a snippetekben. Külső ikonkönyvtár nem kell.
- **Űrlap:** a CTA gombok a `#jelentkezes` horgonyra mutassanak. Az űrlap helyén:

  ```html
  <section id="jelentkezes">
    <!-- ide jön a saját feliratkozó űrlapod beágyazó kódja -->
  </section>
  ```

  Ha a felhasználó megadta a beágyazó kódját, azt tedd a komment alá. Mérőkódot (Meta,
  Google Analytics stb.) magadtól ne tegyél az oldalba; ha a felhasználó kéri, az ő saját
  kódját illeszd be.
- **Lábléc:** cégnév, ÁSZF, adatvédelmi tájékoztató, ügyfélszolgálati e-mail a cégprofilból.
  Ha nincs megadva, `#` link és egy `<!-- TEENDŐ: ... -->` komment.

**Képek:** ha nincs meg minden kép, vagy töröld az adott blokkot (jobb, mint egy üresen
tátongó hely), vagy tegyél helyőrzőt a felhasználó színével, például:
`https://placehold.co/600x400/2F4B9A/ffffff?text=Kép`.

---

## 5. lépés: mentés és átadás

**Webinárnál két fájl:** `webinar-valtozat-1.html` és `webinar-valtozat-2.html`.
**Kihívásnál egy fájl:** `kihivas-feliratkozo.html`, vagy beszélő névvel
(például `tavaszi-sprint-kihivas.html`).

Add át a fájlokat (claude.ai-on a `present_files` eszközzel, Claude Code-ban a mentett
útvonallal), és röviden jelezd:
- webinárnál: két változat készült, két különböző bevált felépítés alapján, válassza ki,
  melyik tetszik, és azt finomítjátok;
- az űrlap helye ki van jelölve, oda kell beilleszteni a saját feliratkozó űrlap kódját;
- ha más szín vagy betű kell, elég szólni.

Ne kérdezd újra, amit egyszer már megadott. A HTML belsejét ne magyarázd hosszan.

---

## Minőségi szabályok

- **Csak akkor kérdezz, ha tényleg kell.** Ha megvan a főcím, a dátum és a bullet lista, de
  nincs portré, egy összesített kérdést tegyél fel a hiányzó képekről, vagy ajánld fel a
  helyőrzőt.
- **Nem találsz ki tartalmat.** Bulletet, eredményt, véleményt, számot nem pótolsz fejből.
- **A minták hangja copywriter-vezérelt marketing landing.** Ne told el „modernebb,
  minimálisabb” irányba, hacsak a felhasználó nem kéri.
- **A kimenet tiszta, önálló HTML:** Tailwind CDN, Google Fonts, semmi WordPress-maradvány,
  semmi más cégtől átvett adat.
- **Mobilon is olvasható:** a főcím és a gombok kis képernyőn se lógjanak ki.

---

## Példa (röviden)

> Felhasználó: „Csinálj egy webinár feliratkozó oldalt. Címe: Hogyan indítsd el az online
> vállalkozásodat? Március 15., 18:00.”
>
> Claude: [megnézi a cegprofil.md-t: onnan jön a sötétkék és sárga szín, a Poppins betű és az
> előadó bemutatkozása] „Milyen bullet pontok kerüljenek az »Ezekről lesz szó« részbe? És van
> már beágyazó kódod a feliratkozó űrlaphoz?”
>
> Felhasználó: „Bullet pontok: ... Űrlapkódom még nincs.”
>
> Claude: [beolvassa mindkét webináros mintát, felépít két tiszta HTML oldalt a felhasználó
> szövegével és arculatával, az űrlap helyére a kommentet teszi, két fájlt ad át]

---

## Kötelező zárás: szövegellenőrzés

Amikor a szöveg elkészült, **még a leadás előtt** futtasd rajta a `szovegellenorzo` skillt.
Az szedi ki azokat a mintákat, amikről a magyar olvasó ma már felismeri az AI-t. A
szerkezethez nem nyúl, csak a megfogalmazáshoz.

## Kapcsolódó skillek

- `cegprofil`: innen jönnek az arculati és a cégadatok.
- `webinar-koszonooldal`: a feliratkozás utáni köszönőoldal ugyanezzel az arculattal.
- `ertekesitesi-level-iro`: a webinárhoz tartozó emlékeztető és utánkövető levelek.
- `claude-oldalak-feltolto`: ha a kész oldalt WordPressre kell feltölteni.
