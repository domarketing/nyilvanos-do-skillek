# 8 - Márka-diagnózis: `marka-dns.json` (minden futás elején, a kinyerés után)

Ebből jön minden egyedi döntés: a paletták színei, a betűk pontozása, az ikontechnikák, az 5 karakter ügyfélre írt
tartalma és a komponensek szakmai részletei. A választó tetején „Így látunk téged” címmel jelenik meg, tehát az
ügyfél is olvassa: legyen konkrét, kedves és igaz. Minden tény az oldalról jön; amit nem tudsz, azt hagyd ki.

Kitöltés előtt nézd meg: `bemenet/arculat.md`, `bemenet/szoveg/*.md`, a fotótablót és a mostani oldal képernyőképét.
Minta: Koppány Lili (tájépítész) futása, `assets/pelda-lili/marka-dns.json`.

```jsonc
{
  "verzio": 1,
  "marka": "Koppány Lili",
  "szakma": "okleveles tájépítészmérnök, kerttervező",           // köznyelven, ahogy az ügyfél mondaná
  "mit_ad": "1-2 mondat: mit kap a vevő (az oldal szavaival)",
  "kinek": "kik a vevők, milyen helyzetben vannak",
  "ar_szint": "ha az oldalon van ár: az, betűre; különben elhagyható",
  "hangnem": {"leiras": "2-3 mondat a hangjáról", "szavak": ["tegező", "kedves", "..."]},
  "targyi_vilag": {
    "targyak":   ["amit a szakma kézbe vesz: eszközök, papírok, csomagolás"],
    "novenyek":  ["opcionális: anyag-, növény-, ételnevek, ami a szakmánál értelmes"],
    "anyagok":   ["papír, fa, kerámia, fém..."],
    "formak":    ["visszatérő formák: szintvonal, perforáció, pecsét, hullám..."],
    "szinek":    [{"nev": "díszfű-szalma", "hex": "#CDB077", "forras": "honnan: fotó, tárgy, anyag"}]   // legalább 6-8
  },
  "ami_mar_megvan": {
    "szinek": [{"nev": "zsályazöld", "hex": "#ADCE8A"}],      // a mostani oldal valódi márkaszínei (nem a WordPress alapszínek!)
    "betuk": ["Montserrat", "Karla"],                         // a mostani oldal betűi (a hű karakter ezt örökölheti)
    "logo": "egy mondat", "kepek": "milyen képei vannak", "erosseg": "ami csak neki van meg"
  },
  "egyedi_jelek": ["amit csak ő tud felmutatni: saját rajz, kabala, hely, szlogen"],
  "kerulendo":    ["a szakma kliséi, és amit az ügyfél maga is kritizál"],
  "formanyelv": {"organikus": 0.85, "puha": 0.65, "harsany": 0.25, "kortars": 0.55, "kezi": 0.85, "homerseklet": 0.55},
  "hu_karakter": "opcionális: melyik karakter legyen a mostanihoz hű (alapból a generátor dönti el)",
  "sotet_karakter": "opcionális: melyik karakter kapja a sötét palettát (alapból a formanyelvből)",
  "karakterek": {
    "elegans":    {"nev": "botanikus tábla", "otlet": "1 mondat: mit jelent nála az elegáns", "reszlet": "egy szakmai részlet",
                   "szinek": ["színnevek a tárgyi világ listájából (tipp a palettagenerátornak)"]},
    "modern":     {"nev": "...", "otlet": "...", "reszlet": "...", "szinek": []},
    "meresz":     {"nev": "...", "otlet": "...", "reszlet": "...", "szinek": []},
    "baratsagos": {"nev": "...", "otlet": "...", "reszlet": "...", "szinek": []},
    "klasszikus": {"nev": "...", "otlet": "...", "reszlet": "...", "szinek": []}
  },
  "igy_latunk": "3-4 mondat, tegezve, amit az ügyfél a választó tetején olvas",
  "brief": null            // ha az ügyfél válaszolt a 3 kérdésre (lásd lent), ide kerülnek a válaszok
}
```

## A formanyelvi tengelyek (0..1)

| Tengely | 0 | 1 | Mire hat |
|---|---|---|---|
| `organikus` | szerkesztett, geometrikus | természetes, kalligrafikus | betű, ikontechnika, formák |
| `puha` | szögletes, éles | kerek, puha | lekerekítés, betű, ikon |
| `harsany` | csendes, könnyű | hangos, nehéz, plakátos | súlyok, telítettség, mozgás; melyik karakter kapja a sötét palettát |
| `kortars` | történeti, klasszikus | mai | betű, ikontechnika |
| `kezi` | digitális, gépi | kézzel készült | kézírás, ikontechnika (ceruza, festés, nyomat) |
| `homerseklet` | hideg színek | meleg színek | paletta |

## Az 5 karakter: a váz marad, a tartalom ügyfelenként más

Az 5 karakter (elegáns · modern · merész · barátságos · klasszikus) minden ügyfélnél ugyanaz a váz, mert így
könnyű választani. A **tartalmuk** viszont ügyfelenként más: írd meg, mit jelent az adott karakter ennél a
vállalkozásnál (egy szóban: `nev`, egy mondatban: `otlet`), és mi a szakmai részlete (`reszlet`). Ebből készül a
5 paletta neve, az 5 betűpár hangulata, az 5 ikonstílus csavarja és a komponensek (címsor, alcím, gomb, kártya, fotó)
részletei. Példák:

| Szakma | elegáns | modern | merész | barátságos | klasszikus |
|---|---|---|---|---|---|
| tájépítész | botanikus tábla | tervezőasztal | préri | kerti napló | arborétum |
| fogorvos | porcelán | klinikai tisztaság | mosoly-kampány | családi rendelő | régi patika |
| könyvelő | privátbanki levél | dashboard | piros tinta | konyhaasztal-tanácsadás | főkönyv |
| cukrász | patisserie-doboz | laboratóriumi recept | cukormáz-plakát | nagymama receptfüzete | cukrászda-cégtábla |

Ezek csak példák, ne másold: mindig az adott ügyfél tárgyaiból és hangjából írd. Külön „kreatív koncepció” réteg
nem kell (okt. 1-jén túlzásnak bizonyult); a karakter-név elég, hogy az opciók összetartsanak.

## Opcionális 3 kérdés (élő futásnál NEM kérdezed)

Ha van idő, és az ügyfél maga futtatja: (1) Kinek szól leginkább az oldalad? (2) Milyen érzéssel csukja be a
látogató? (3) Mit nem szeretnél semmiképp látni (szín, stílus, klisé)? A válaszok a `brief` mezőbe kerülnek, és
felülírják a levezetett feltételezéseket. Élő bemutatón és ha az ügyfél csak egy URL-t ad, ne kérdezz.

## Ellenőrzés

A `valtozatossag.py` (és a választó építése) hibát ad, ha a diagnózis hiányzik, ha a tárgyi világ színeiből 6-nál
kevesebb van, vagy ha valamelyik karakternek nincs ügyfélre írt neve.
