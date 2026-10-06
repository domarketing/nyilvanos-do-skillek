# Beágyazott minta-oldalak (samples)

Három valódi, élesben futott magyar feliratkozó oldal mentett, megtisztított változata.
A skill ezekből a felépítést és a vizuális logikát veszi át. A szöveg, az arculat, a képek
és a nevek mindig a felhasználótól vagy a `cegprofil.md`-ből jönnek.

A fájlok a skill részei, külső mappa vagy feltöltés nem kell hozzájuk.

## A három minta

| Fájl | Típus | Mire való |
|------|-------|-----------|
| `webinar_minta_1_tizmillios_bevetel.html` | **webinár** | „Hogyan csinálhatsz több tízmilliós bevételt néhány nap alatt”: egynapos webinár, előadás oldal |
| `webinar_minta_2_uj_vevok_futoszalagon.html` | **webinár** | „Új Vevők Futószalagon”: egynapos webinár, másik elrendezés, felugró űrlapos gombokkal |
| `kihivas_minta_3napos_tudasbol_milliok.html` | **kihívás** | „Tudásból milliók, 3 napos ingyenes kihívás”: több napos kihívás, sprint oldal |

## Mit tisztítottunk ki belőlük

Az eredeti „Weboldal mentése” exportokból kikerült:

- minden szkript: mérőkódok (Google Ads, Google Analytics, Tag Manager, Meta (Facebook)
  és társaik), sütikezelő, WordPress- és bővítményszkriptek;
- a feliratkozó űrlapok célcíme és rejtett lista-, illetve űrlapazonosítói. Az űrlap
  célja `#`, a helyén ez a komment áll:
  `<!-- ide jön a saját feliratkozó űrlapod beágyazó kódja -->`;
- a mentéskor keletkezett, de a skillben nem létező helyi fájlokra mutató hivatkozások,
  a WordPress admin-sáv és a felugró ablakok;
- a képek: semleges szürke helyőrzők, az eredeti arányokkal;
- a linkek: mindegyik `#`-ra mutat; az e-mail-címek helyén helyőrző szöveg áll;
- az eredeti márkaszínek helyén semleges alapszínek vannak (`#2F4B9A`, `#F2A93B`, `#0F1B3D`).

A látható szövegek és a stílusblokkok maradtak, hogy a felépítés és a copy ritmusa
látszódjon. A két webináros mintánál az eredeti oldal egyes stílusfájljai külső fájlban
voltak, ezért böngészőben megnyitva ezek nyersebbnek látszanak. Szövegként olvasva a
felépítés így is jól követhető.

## Használat

- **Webinár-kéréskor mindkét webináros mintát** használd: mindkettőből készül egy-egy oldal,
  hogy a felhasználó választhasson.
- **Kihívás-kéréskor** a `kihivas_minta_3napos_tudasbol_milliok.html` a minta.
- **Ne másold be egy az egyben** egyik fájlt sem. A kimenet tiszta, elölről felépített HTML.
- **A mintákból semmilyen tartalmat ne vigyél át** a felhasználó oldalába: se nevet, se
  véleményt, se számot, se szöveget, se képet, se linket. A minta csak a vázat mutatja.
