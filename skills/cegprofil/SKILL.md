---
name: cegprofil
description: "Cégprofil készítése és frissítése: egyetlen cegprofil.md dokumentum a vállalkozásról, amiből a többi skill dolgozik (feliratkozó oldal, köszönőoldal, értékesítési levél és oldal, Facebook-poszt). Néhány csoportosított kérdéssel interjút készít, vagy kinyeri az adatokat a weboldalból, meglévő dokumentumokból, beillesztett szövegből. Nyolc rész: cég és szakértő, ideális vásárló, ajánlatok, csali vagy webinár, hangnem, arculat, elérhetőség és jogi adatok, valódi bizonyítékok. Amit nem tud, azt hiányként jelöli, és nem találja ki. Használd elsőként, a többi skill előtt, és ha ezt írják: 'készítsük el a cégprofilt', 'cégprofil', 'ismerd meg a cégemet', 'itt a weboldalam, tanuld meg', 'ideális vásárló', 'célcsoport', 'buyer persona', 'frissítsd a cégprofilt', 'új ajánlatom van', 'változott az ár', vagy ha egy másik skill nem talál cegprofil.md fájlt."
---

# Cégprofil

A cégprofil egyetlen dokumentum (`cegprofil.md`) a vállalkozásról: ki a szakértő, kinek ad el, mit és
mennyiért, milyen hangon beszél, hogyan néz ki, és mivel tudja bizonyítani, amit állít. A többi skill
innen dolgozik, így a felhasználónak nem kell minden levélnél és oldalnál újra elmondania ugyanazt.

Ez a skill elkészíti a cégprofilt, és később frissíti. A kész dokumentum szerkezete a
`references/cegprofil-sablon.md` fájlban van.

## Mikor fut

- **Az elején**, mielőtt a felhasználó először használná a többi skillt. Egyszer kell rászánni egy
  alapos beszélgetést, utána minden skill ebből dolgozik.
- **Ha egy másik skill nem talál `cegprofil.md`-t**, és felajánlja ezt.
- **Ha valami változik**: új ajánlat, új ár, új webinár-időpont, friss vélemények. Lásd: Frissítés később.

## Hol tárolódik a cegprofil.md

**Claude Code:** mentsd a munkamappa gyökerébe `cegprofil.md` néven. Ha már van ilyen fájl, ne írd felül
vakon: olvasd be, és csak a változó részeket módosítsd.

**claude.ai:** add ki a kész dokumentumot letölthető `cegprofil.md` fájlként, ha a fájlkészítés be van
kapcsolva, különben egyetlen másolható markdown blokkban. Utána mondd el a felhasználónak:
- Ha Projektben dolgozik, töltse fel a fájlt a Projekt tudásbázisába (Project knowledge). Így a projekt
  minden új beszélgetésében megtalálják a többi skillek.
- Ha nem használ Projektet, a profil maradhat ebben a beszélgetésben, egy új beszélgetés elején pedig
  elég feltölteni vagy beilleszteni.

## Hogyan használják a többi skillek

A `feliratkozo-oldal`, a `webinar-koszonooldal`, az `ertekesitesi-oldal-keszito`, az
`ertekesitesi-level-iro` és a `facebook-poszt-iro` írás előtt megkeresi a `cegprofil.md`-t: a projekt
fájljai között, a munkamappában vagy a beszélgetésben. Ha megvan, abból dolgozik. Ha nincs, csak az adott
feladathoz szükséges minimumot kérdezi meg, vagy felajánlja ezt a skillt.

Két szabály köti őket. Ezek a sablon elején is benne vannak, hogy a profil önmagában is érthető legyen:
- Ami `[[HIÁNYZIK: …]]` jelölésű, azt nem töltik ki kitalált adattal. Megkérdezik, vagy kihagyják az
  adott elemet.
- Véleményt és eredményszámot csak a 8. részből (Bizonyítékok) használnak. Ami ott nincs, az nem kerülhet
  szövegbe.

---

## A munkafolyamat

### 1. Először gyűjts forrásokat, csak utána kérdezz

Kezdd ezzel az egy kérdéssel:

> Van weboldalad, vagy meglévő anyagod a cégedről (ajánlat, értékesítési oldal, korábbi hírlevelek,
> vélemények, prezentáció)? Ha igen, küldd el a címet vagy a fájlokat, és abból indulok. Ha nincs,
> kérdésekkel haladunk.

- **Weboldal:** ha van webes eszközöd, nézd meg a főoldalt, a „rólam” vagy „rólunk” oldalt, az ajánlat-
  és szolgáltatásoldalakat, a véleményeket, a kapcsolat oldalt, az impresszumot, az adatkezelési
  tájékoztatót és az ÁSZF-et. A hangnemhez olvass bele egy-két blogbejegyzésbe vagy hírlevélbe is. Ha
  nincs webes eszközöd, kérd meg a felhasználót, hogy másolja be a fontos oldalak szövegét.
- **Dokumentum, beillesztett szöveg:** olvasd végig, és gyűjtsd ki belőle, ami a sablon valamelyik
  mezőjébe illik.
- **Arculat:** a színek és a betűk ritkán olvashatók ki pontosan egy weboldal szövegéből. Ha a
  `webdesign-arculat-generator` skill már futott, vedd át a designrendszeréből. Ha nem, kérdezd meg,
  vagy hagyd hiányként.

Utána mutasd meg röviden, mit találtál, és csak azt kérdezd meg, ami még hiányzik.

### 2. Interjú: kevés, csoportosított kérdés

- Egy üzenetben egy kérdéskör, benne legfeljebb 5-6 rövid kérdés.
- Ahol segít, adj egy példát, hogy a felhasználó lássa, milyen mélységű válasz kell.
- Amit már tudsz a forrásokból, azt ne kérdezd meg újra, legfeljebb erősíttesd meg.
- A „nem tudom” is jó válasz. Abból hiányjelölés lesz, és haladtok tovább.
- Ha a felhasználó siet, az első két kör elég az induláshoz. A többit később is pótolhatjátok.

**1. kör: a cég és az ajánlat**
- Hogy hívják a céget vagy a márkát, és ki a szakértő, akinek a nevében a levelek mennek?
- Egy mondatban: kinek segítesz, és miben? (pl. „Kisgyerekes anyukáknak tanítok jógát otthonra, napi
  20 percben.”)
- Mit adsz el, mennyiért, és mit kap érte a vásárló? Van garancia, bónusz, határidő?
- Mivel tudod alátámasztani, hogy értesz hozzá? Évek, ügyfélszám, díjak, saját eredmény, csak ami igaz.

**2. kör: az ideális vásárló**
- Ki a legjobb ügyfeled? Gondolj egy konkrét emberre: mivel foglalkozik, hol tart most?
- Mi bántja, mielőtt hozzád jön? Mit próbált már?
- Mit szeretne elérni, az ő szavaival?
- Miért nem vásárol, amikor nem vásárol? (idő, pénz, „nálam úgysem működik”, a környezete lebeszéli)
- Van tőle szó szerinti mondatod? Ügyfélüzenet, komment, kérdőívválasz, egy mondat egy hívásból. Ezek a
  legértékesebbek, mert a szövegek ezektől szólnak a vásárló nyelvén.

**3. kör: csali és hangnem**
- Mivel szerzel feliratkozót: webinárral, több napos kihívással, letölthető anyaggal, ingyenes
  konzultációval? Mi a témája, mikor lesz, mit kap, aki feliratkozik?
- Tegezed vagy magázod a vásárlóidat?
- Milyen a stílusod három-négy szóban? Van szó, amit sosem használnál?
- Hogyan köszönsz el a leveleid végén?
- Küldj egy rövid szöveget, amit te magad írtál (levél, poszt), hogy legyen mihez igazítani a hangot.

**4. kör: arculat, jogi adatok, bizonyítékok**
- Milyen színeket használsz (hex-kóddal, ha tudod), és milyen betűket? Hol érhető el a logód és a
  fotóid?
- Mi a hivatalos cégneved, hol van az adatkezelési tájékoztatód, és milyen elérhetőség szerepeljen az
  oldalakon?
- Vannak valódi véleményeid vagy eredményszámaid? Másold be őket szó szerint, a forrásukkal együtt, és
  írd mellé, hogy az ügyfél neve megjelenhet-e.

### 3. A dokumentum megírása

Töltsd ki a `references/cegprofil-sablon.md` sablont, a részek sorrendjén ne változtass. Szabályok:

- **Kitalálni tilos.** Ami nem derült ki, az `[[HIÁNYZIK: mi hiányzik]]` jelölést kap (listaelemben
  elég a rövid `[[HIÁNYZIK]]`). Egy jól jelölt hiány többet ér egy hihető, de kitalált adatnál, mert a
  többi skill így tudja, hogy rá kell kérdeznie.
- **A következtetést jelöld.** Ha a hangnemet a weboldal szövegéből olvastad ki, vagy egy színt egy
  képről becsültél, írd mögé: `(a weboldal alapján, erősítsd meg)`.
- **A vásárló szavait szó szerint hagyd.** Ne javítsd ki és ne fogalmazd át őket szebbre, a szövegíráshoz
  pont ez a nyers forma kell.
- **Bizonyíték csak valódi lehet.** A 8. részbe csak olyan vélemény és szám kerül, aminek van forrása.
  Ha a felhasználó azt kéri, hogy „írj be pár jó véleményt”, mondd el, hogy ezt nem teheted, és kérd a
  valódiakat.
- **Személyes adat.** Véleményt névvel és fotóval csak az ügyfél hozzájárulásával szabad megjeleníteni.
  Ha ez nem ismert, írd a táblázatba, hogy „nem tudjuk”. Ilyenkor a skillek monogrammal vagy név nélkül
  használják a véleményt.
- **Az árnál** mindig derüljön ki, hogy bruttó vagy nettó, és van-e rajta ÁFA.
- **A dátumot** töltsd ki a fejlécben és a változásnaplóban.

### 4. Átadás

A kész dokumentum mellé írj egy rövid összefoglalót:
- melyik rész teljes, és melyikben van még hiány,
- a hiányjelölések listáját fontossági sorrendben, azzal együtt, hogy melyik skillnek kellenek (pl. a
  webinár időpontja nélkül nem készülhet el a köszönőoldal és az emlékeztető levél),
- hol van a fájl, és mit tegyen vele a felhasználó (lásd: Hol tárolódik a cegprofil.md).

---

## Frissítés később

Ha a felhasználó azt mondja, hogy valami változott („új ajánlatom van”, „emeltem az árat”, „új
webinár-időpont”, „kaptam pár új véleményt”):

1. Olvasd be a meglévő `cegprofil.md`-t. Ha nem találod, kérd meg, hogy töltse fel vagy illessze be.
2. Csak az érintett részt kérdezd meg és írd át. A többihez ne nyúlj.
3. A lejárt határidőket és a lezárt ajánlatokat jelöld `(lezárva: ÉÉÉÉ-HH-NN)` megjegyzéssel, vagy
   töröld őket, hogy a többi skill véletlenül se használja.
4. Frissítsd a dátumot a fejlécben, és írj egy sort a változásnaplóba a fájl végén.
5. Mondd el, mi változott, és kérd, hogy cserélje le a régi fájlt. claude.ai-on törölje a régit a Projekt
   tudásbázisából, és töltse fel az újat, mert két eltérő változat összezavarja a skilleket. Claude
   Code-ban a fájl helyben frissül.

Minden kampány előtt érdemes átnézni a 3. és a 4. részt: az ár, a határidő és a webinár időpontja
változik a leggyakrabban.

---

## Ellenőrzőlista a leadás előtt

- [ ] Mind a nyolc rész szerepel, a sablon sorrendjében?
- [ ] Minden ismeretlen adat hiányjelölést kapott, és semmi sincs kitalálva?
- [ ] A 8. részben minden véleménynek és számnak van forrása?
- [ ] A vásárló szavai szó szerint, idézőjelben szerepelnek?
- [ ] Az árnál kiderül, hogy bruttó vagy nettó?
- [ ] A színek hex-kóddal szerepelnek, vagy hiányként jelölve?
- [ ] A következtetések meg vannak jelölve?
- [ ] Ki van töltve a dátum?
- [ ] A felhasználó tudja, hová tegye a fájlt?

## Kapcsolódó skillek

A cégprofilt a `feliratkozo-oldal`, a `webinar-koszonooldal`, az `ertekesitesi-oldal-keszito`, az
`ertekesitesi-level-iro` és a `facebook-poszt-iro` olvassa. Az arculati részhez a
`webdesign-arculat-generator` designrendszere jó forrás. A profil adat, ezért nem megy át a
`szovegellenorzo` skillen. A belőle készülő szövegek igen.
