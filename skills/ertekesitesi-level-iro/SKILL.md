---
name: ertekesitesi-level-iro
description: "Magyar értékesítési és kampánylevelek írása: tárgysor, betekintő, teljes levélszöveg és Ui. Bevált, valódi kampánylevelek szerkezetére épít (kampánynyitó, értékadó, záró és sorozatépítő levél), és a webináros futószalag leveleit is megírja, a webinár utáni visszanézős levéltől az értékesítési sorozaton át a zárásig. Ha van cegprofil.md, abból dolgozik (ideális vásárló, ajánlat, hangnem, valódi bizonyítékok). Használd, ha a felhasználó ezt kéri: 'írj egy emailt', 'értékesítési levél', 'kampánylevél', 'sales email', 'hírlevél', 'promóciós levél', 'email sorozat', 'email kampány', 'levelet írnál', 'email vázlat', 'írd meg emailként ezt a vázlatot', 'webinár utáni levelek', 'emlékeztető levél', 'záró levél', 'utolsó esély levél'. A kész szöveget a végén a szovegellenorzo skillen futtatja át."
---

# Értékesítési levél író

Ez a skill értékesítési, kampány- és marketingleveleket ír magyarul egy vállalkozás nevében. A levelek a
feladó (jellemzően a cégvezető vagy a szakértő) személyes, közvetlen hangján szólnak, és az ideális
vásárló problémáira és vágyaira épülnek.

## Előfeltételek: ezeket olvasd be írás előtt

1. **A cégprofil.** Ha van `cegprofil.md` (a projekt fájljai között, a munkamappában vagy a
   beszélgetésben), abból dolgozz: ideális vásárló, ajánlat, csali vagy webinár, hangnem, aláírás,
   valódi bizonyítékok. Ha nincs, kérdezd meg a hiányzó minimumot, vagy ajánld fel a `cegprofil` skillt.

   A hiányzó minimum, egy üzenetben megkérdezve:
   - Ki a feladó (név, cég)?
   - Mit adunk el: mi a neve, mennyibe kerül, mit kap érte a vásárló?
   - Kinek szól a levél, egy-két mondatban?
   - Van határidő, bónusz, garancia?
   - Tegezés vagy magázás?

   Ha a cégprofilban egy mező `[[HIÁNYZIK: …]]` jelölésű, azt ne töltsd ki kitalált adattal. Kérdezd meg,
   vagy hagyd ki a levélből azt az elemet.

2. **`references/email-mintak.md`**: korábbi, bevált értékesítési levelek teljes szövege és elemzése.
   **Mindig olvasd be írás előtt**, ez adja a stílus, a szerkezet és az érvelés mintáit. A minták egy
   másik vállalkozás levelei. A szerkezetet, a ritmust és a technikákat vedd át belőlük, az ajánlatot,
   a neveket és a számokat soha.

---

## A munkafolyamat

### 1. Input fogadása

A felhasználó jellemzően ezt adja:
- **Vázlat**: nyers gondolatok, kulcsüzenetek, amelyekből levelet kell írni
- **Az ajánlat megjelölése**: melyik terméket vagy szolgáltatást adjuk el
- Opcionálisan: célszegmens, a kampány helyzete (hányadik levél a sorozatban), határidők, bónuszok

Ha nem derül ki, melyik ajánlatot adjuk el, és a cégprofilban több is szerepel, **kérdezz rá**, mielőtt
írnál.

Ha a célszegmens nincs megadva, a cégprofilban elsődlegesnek jelölt ideális vásárlónak írj.

### 2. A levél megírása

A vázlat alapján írd meg a teljes levelet az alábbi szerkezeti és stílusszabályok szerint. A cél az, hogy
a felhasználónak minimálisan kelljen szerkesztenie.

### 3. Output

Add ki:
- **Tárgysor**
- **Betekintő** (preheader: a rövid szöveg, amit a levelezőprogram a tárgy alatt mutat)
- **A levél teljes szövege**

Sorozatnál minden levélhez külön, és írd fölé, mikor menjen ki (pl. „a webinár után 1 órával”,
„a zárás napján reggel”).

---

## A levél szerkezete

Minden értékesítési levél ezekből a részekből áll.

### 1. Tárgysor
- Ideálisan legfeljebb 60 karakter, de 80 is elfogadható
- Kíváncsiságot kelt, VAGY konkrét hasznot ígér, VAGY meglepő állítást tesz
- Emoji opcionális (legfeljebb egy, az elején), ha a cégprofil hangneme engedi
- Kerüld a kattintásvadászatot: a levél tartsa be, amit a tárgy ígér
- Bevált formák a mintákban: zárójeles kontextus, kérdés, emoji és konkrétum

### 2. Betekintő
- Egy mondat, ami kiegészíti a tárgysort, és nem ismétli
- Kedvet csinál a megnyitáshoz
- Legfeljebb 90 karakter

### 3. Hook: az első 2-5 mondat
- Ez dönti el, hogy az olvasó tovább olvas-e
- Típusok a mintákból:
  - **Empátia hook:** megfogalmazza a frusztrációt, amit az olvasó is érez („Ismered azt az érzést, amikor...”)
  - **Meglepő tény hook:** figyelemfelkeltő állítás („A Facebook csendben átírta a szabályokat”)
  - **Lendület hook:** egy élő esemény friss energiájából indul („Most lett vége... még mindig pörgök!”)
  - **Döntés hook:** egyenesen a lényegre tér, és kimondja, hogy most döntés jön (a 4. minta nyitása)

### 4. Értékadó középrész
Ez a levél „húsa”. Ide kerül:
- **Történet**: személyes élmény, a kulisszák mögötti munka, konkrét eset
- **Tanítás**: trend, újdonság, szemléletváltás
- **Érvelés**: miért éri meg az ajánlat, mit old meg, hogyan működik
- **Társadalmi bizonyíték**: számok, eredmények, ügyfélsztorik, kizárólag a cégprofil bizonyítékok
  részéből vagy a felhasználótól

A forma a tartalomtól függ:
- **Számozott pontok**, ha 2-3 értékpontot mutatsz be (2. minta)
- **Régi és új összehasonlítása**, ha trendváltásról szól a levél (3. minta)
- **Kifogáskezelő blokkok**, ha az olvasó ellenvetéseit veszed sorra (4. minta)
- **Lineáris történet**, ha egy sztorin vezeted végig az olvasót (1. minta)

### 5. CTA
- Természetes átvezetés, erőltetés nélkül
- A link szövege cselekvésre hív („Csatlakozz most”, „Itt tudsz jelentkezni”, „Kattints ide, és lépj be”)
- Ha van határidő, emeld ki (félkövérrel, a mintákban órajellel)
- Ha a zárás után történik valami (pl. csak várólistára lehet feliratkozni), mondd el. Ez tény, és az
  olvasónak joga van tudni.

### 6. Zárlat
- Köszönés: „Csodás napot,” vagy a cégprofilban megadott köszönés
- A feladó keresztneve
- Ha csapat dolgozik mögötte: „és a [cég neve] csapata”

### 7. Ui.
- Ide kerül a levél legerősebb érzelmi mondata
- Rövid (1-3 mondat), tömör, motiváló
- Gyakran egy utolsó CTA-linket is tartalmaz
- **Kötelező**: minden értékesítési levélben legyen Ui.

---

## Stílusszabályok

### A levél hangja

Úgy szól, mintha a feladó személyesen írná: egy tapasztalt vállalkozó barát, aki őszintén megosztja,
amit tud. Ha a cégprofil hangnem-része mást mond (magázás, visszafogottabb stílus, tiltott szavak),
az az erősebb.

### Használd:
- **Tegeződés** végig, következetesen (vagy magázás, ha a cégprofil azt kéri)
- **Rövid mondatok**, néha csak 2-3 szó („Ez most pont az.”)
- **Sok sortörés**: minden gondolat külön bekezdés, mobilon is könnyen olvasható
- **Nagybetűs kiemelés** egy-egy kulcsszón: NEM, STABILAN, IGAZÁN
- **Idézőjeles belső párbeszéd**: az olvasó fejében forgó mondatok („Oké… de működni fog nálam?”)
- **Kérdések az olvasóhoz**, amelyek gondolkodásra késztetik
- **Konkrét számok**: „sokkal olcsóbb” helyett „napi 330 Ft”
- **Hasonlatok**, amelyek egyszerűvé teszik a bonyolultat (a mintában: számfestő készlet)
- **Funkcionális jelölők** (nyíl, pipa, ajándékdoboz, óra) jelölésre, díszítés nélkül, ha a cégprofil
  hangneme engedi
- **Magyar nyelv**: kerüld a fölösleges angol szavakat, a szakszavak rendben vannak

### Kerüld:
- A formális, tanácsadói nyelvet („javasolt megoldás”, „érdemes megfontolni”)
- A hosszú, kanyargós mondatokat
- A manipulatív, nyomulós hangnemet
- A motivációs coach stílust (lelkesítés tartalom nélkül)
- A túl sok felsorolásjelet: ha 3-nál több pont van, mindegyiknek legyen tartalma
- A „Kedves [Név]” típusú formális megszólítást: a levelek megszólítás nélkül, rögtön a hookkal indulnak

---

## Levéltípusok, és mikor melyiket használd

### 1. Kampánynyitó levél
- **Mikor:** a kampány első levele, amikor megnyílik az ajánlat
- **Fókusz:** mi ez, miért jó, mit kapsz, hogyan kezdj bele
- **Minta:** 1.
- **Hossz:** hosszabb (800-1200 szó), itt kell a legrészletesebben bemutatni az ajánlatot

### 2. Értékadó, tanító levél
- **Mikor:** a kampány közepén, amikor az olvasó már ismeri az ajánlatot
- **Fókusz:** egy konkrét tananyag, szolgáltatáselem vagy technika bemutatása, ami az ajánlat része
- **Minta:** 2. és 3.
- **Hossz:** közepes (500-800 szó)
- **Tipp:** kulisszák mögötti történetek, konkrét, kipróbálható szakmai technikák

### 3. Záró, utolsó esély levél
- **Mikor:** a kampány utolsó napja, pár órával a zárás előtt
- **Fókusz:** kifogáskezelés, végső összefoglalás, sürgősség
- **Minta:** 4.
- **Hossz:** közepes-hosszú (600-1000 szó)
- **Tipp:** sorra, őszintén végigmész az olvasó kérdésein. Tiszteletteljes, de határozott.

### 4. Cliffhanger, sorozatépítő levél
- **Mikor:** egy sorozat közben, hogy kíváncsiságot építs a következő levélre
- **Minta:** a 2. minta vége és az átvezetés a 3.-ba
- **Tipp:** a levél végén mondd meg, mi jön legközelebb, és miért érdemes figyelni rá

---

## A webináros sorozat

A minták egy webináros kampányból valók. Egy több napos online előadássorozat második napja után nyílt
meg az ajánlat, és a zárásig levelek sorozata ment ki. A négy minta ennek az 1., 3., 4. és 7. (záró)
levele. Ha webinár köré kérnek leveleket, a típusokat így illeszd a sorozatba:

| Mikor megy ki | Levéltípus | Minta |
|---|---|---|
| A webinár után, még aznap | Visszanézős és kampánynyitó levél: friss lendület, valódi számok az élő alkalomról, visszanézési link, az ajánlat megnyitása | 1. |
| A sorozat közepén | Értékadó levelek, a végükön cliffhangerrel | 2., 3. |
| A zárás előtti napon | A határidő kimondva, és az is, mi lesz utána | 3. |
| A zárás napján, pár órával előtte | Záró, kifogáskezelő levél | 4. |

A webinár előtti leveleknek (visszaigazoló, emlékeztető) nincs saját mintájuk. Rájuk is ugyanaz a
szerkezet érvényes, csak rövidebben: tárgysor, betekintő, hook, egy CTA, Ui. Az időpontot, a belépés
módját és azt, hogy mit kap a résztvevő, a cégprofil csali/webinár részéből vedd, vagy kérdezd meg.
Ezeket sem szabad kitalálni.

---

## A célközönség megszólítása

A cégprofil ideális vásárló részéből dolgozz. A levél az ő szavaival írja le a problémát és a vágyat,
úgy, ahogy ő érzékeli. Amit ő nem lát magáról (például egy hiányzó tudást), azt ne mondd ki egyenesen:
csomagold történetbe vagy példába, és vezesd rá.

Ha a cégprofilban több vásárlói csoport szerepel, döntsd el, melyiknek szól a levél. A minták mögötti
tapasztalat szerint a vásárlók három tipikus helyzetben vannak, és mindegyiknél más hat.

**Kezdő, árérzékeny vállalkozó:**
- Az ő nyelve: időhiány, „nem tudom, hogyan induljak el”, „egyedül csinálok mindent”
- Azt érezze: van rendszer, ami működik, és nem kell mindent egyszerre
- Árérzékeny, ezért számold át napi vagy heti árra (a mintában a havidíjból napi 330 Ft lett), és mutasd
  meg, hogyan termeli ki az árát
- Ne mondd neki, hogy hiányzik a tudása, vezesd rá történetekkel

**Már működő, de elakadt vállalkozó:**
- Az ő nyelve: „jól megy, de nem tudok továbblépni”, „nem akarok többet dolgozni”, magányosság
- A közösség ereje kiemelten fontos: mutasd meg, hogy nem lesz egyedül
- A gyakorlati, rendszerszemléletű érvek hatnak rá

**Nagy, tapasztalt cégvezető:**
- Rövid, lényegre törő levél; inspiráld, győzködni nem kell
- Mélyebb összefüggések, alapozás nélkül
- A személyes hozzáférés és az exkluzivitás motiválja

Ezek kiindulópontok. Ha a cégprofil mást mond a felhasználó vásárlóiról, az az erősebb.

---

## Fontos figyelmeztetések

1. **Soha ne találj ki számot, árat, bónuszt, ajánlatelemet vagy véleményt.** Mindig a cégprofilból vagy
   a felhasználótól dolgozz. Ha bizonytalan vagy, kérdezz.
2. **Az árak és a feltételek kampányonként változhatnak.** Ha a cégprofil régebbi, kérdezd meg, érvényes-e
   még az ár. A mintákban szereplő árak, bónuszok és határidők egy másik cég régebbi kampányából valók,
   ezeket ne használd.
3. **A bónuszok kampányhoz kötöttek.** Nem minden kampányban ugyanazok, ezért kérdezd meg, vagy várd meg,
   amíg a felhasználó megadja.
4. **A linket mindig [link szövege] formában add meg**, a tényleges címet a felhasználó illeszti be.
5. **Ne használj „Kedves [Név]” megszólítást.** A levelek személyesek, és rögtön a hookkal indulnak.

---

## Gyors ellenőrzőlista a levél kiadása előtt

- [ ] A tárgysor kíváncsiságot kelt? Legfeljebb 60-80 karakter?
- [ ] A betekintő kiegészíti a tárgysort, és nem ismétli?
- [ ] A hook az első 2-5 mondatban megfogja a figyelmet?
- [ ] A levél az olvasó nyelvén szól, a megfelelő vásárlói csoportnak?
- [ ] Van benne értékadó rész az eladás mellett?
- [ ] A CTA természetes, erőltetés nélküli?
- [ ] Van Ui. erős záró gondolattal?
- [ ] Rövid mondatok, sok sortörés, könnyű olvasás?
- [ ] Minden szám konkrét, és a cégprofilból vagy a felhasználótól származik?
- [ ] A hang a feladó személyes hangjára hasonlít, a cégprofil hangnem-része szerint?
- [ ] Nem maradt benne semmi a mintákból: név, ajánlat, ár, szám?

---

## Kötelező zárás: szövegellenőrzés

Amikor a szöveg elkészült, **még a leadás előtt** futtasd rajta a `szovegellenorzo` skillt. Az szedi ki
azokat a mintákat, amikről a magyar olvasó ma már felismeri az AI-t, és az írja ki a mérést is.
A szerkezetet érintetlenül hagyja, csak a megfogalmazáson javít.

Az emojit és a nagybetűs kiemelést a szövegellenőrző alapból kiveszi. Ha a cégprofil hangnem-része
engedi őket, a levélben maradhatnak, és a szövegellenőrzés csak a megfogalmazást javítja.

## Kapcsolódó skillek

- `cegprofil`: ebből dolgozik ez a skill. Ha még nincs cégprofil, ezzel készítsétek el.
- `szovegellenorzo`: minden kész levél ezen megy át a végén.
- `feliratkozo-oldal` és `webinar-koszonooldal`: a webinár feliratkozó- és köszönőoldala. A levelekben
  szereplő időpont és link egyezzen velük.
- `ertekesitesi-oldal-keszito`: a kampánylevelek CTA-ja általában erre az oldalra mutat. Az ajánlat, az ár
  és a határidő legyen ugyanaz a levelekben és az oldalon.
