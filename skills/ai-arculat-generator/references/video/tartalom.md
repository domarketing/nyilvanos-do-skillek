# `video/tartalom.json`: az előnézet szövegei és az ügyfélre szabás

A választó minden telefonja ezekből a mondatokból dolgozik. Ha a fájl hiányzik, a tokenek tényeiből (ticker, matricák,
szlogen) készül egy tartalék, de az ügyfélnek mindig a saját mondatait mutasd: így látja, hogy ez az ő videója.

**Szabályok:** minden tény az ügyfél oldaláról (`bemenet/szoveg/*.md`), betűre (ár, szám, név, szerep, szolgáltatás).
Számtartomány nagykötőjellel (`200–350`), mértékegység külön (`"egyseg": "ezer Ft"`). A nagy kiemelő szövegek végén
nincs pont. A felirat a kimondott mondat, ezért ott a pont kell. Nincs hosszú gondolatjel, nincs „nem X, hanem Y”,
nincs emoji. A felső grafika ne ismételje szó szerint a feliratot.

```jsonc
{
  "foto": "bemenet/kepek/bg-igazolvanykep.jpg",       // a portré (video.py elokeszit)
  "felirat": ["Mindenkinek", "lehet", "gyönyörű", "kertje."],   // 3-6 szó, egy igaz mondat az oldalról
  "felirat_kiemelt": 2,                                // a kulcsszó indexe (kiemelőszínű)
  "hook": {"kicker": "Tájépítész tipp", "sorok": ["Felejtsd el", "az állandó gyomlálást"], "kiemelt": 1},
  "info": {"kicker": "Kerttervezés", "szam": "200–350", "egyseg": "ezer Ft", "cimke": "egy teljes kert megtervezése"},
  "tabla_cimke": "Tab. I",                             // a keretes kártya kis címkéje (ha a webes kártyán is van ilyen)
  "temak": ["Minimális fenntartás", "Változatosság télen-nyáron", "Ökologikus szemlélet"],
  "temak_cim": "Miért egy természetes kert?",          // a témaválasztó lista címe
  "aktiv": 1,                                          // az épp tárgyalt téma indexe
  "nev": {"nev": "Koppány Lili", "szerep": "okleveles tájépítészmérnök"},
  "fejezet": {"szam": "02", "cim": "Változatosság télen-nyáron"},
  "zaro": {"social": "Ha hasznos volt",
           "cta": {"cim": "Kérj ingyenes helyszíni konzultációt", "gomb": "Ajánlatkérés", "link": "koppanylili.hu"},
           "szlogen": "…amit annyira szeretsz, hogy be sem akarsz többé menni a házba…"},
  "nyito": {"sorok": ["Öntözésmentes kert", "lehetséges?"], "kiemelt": 1},
  "kulcsszo": "KERT",                                  // a fej mögötti nagy szó (rövid: 3-7 betű)
  "kicker_pill": "Kerttervezés",
  "ikonok": ["kertterv", "novenyagy", "evszakok"],     // a tokenek ikonjai közül (az első a kártyákon, kettő a csempéken)
  "oldalcsempek": [{"ikon": "kertterv", "cimke": "Kertterv"}, {"ikon": "novenyagy", "cimke": "Növényágy"}],
  "hangnem_pelda": "Hiszek abban, hogy mindenkinek lehet gyönyörű kertje.",   // a márka-részbe (nem kötelező)

  // ügyfélre szabás: az ajánlott változatok és a nevek, leírások, indoklások a márka szavaival
  "ajanlott": {"stilus": "klasszikus", "felirat": "karaoke", "hook": "sotetitett", "nyito": "keretes"},
  "valtozatok": {
    "kartya": {"keretes": {"nev": "Botanikus tábla", "leiras": "…", "miert": "A weboldalon a botanikus tábla lett a kártyád…"}},
    "hangulat": {"akusztikus": {"nev": "Csendes kert", "leiras": "…"}}
  }
}
```

## Az ajánlott változatok
Ha a `tartalom.json` nem mondja meg, a `katalogus.ajanlott()` dönt: a kártya a webes kártyából (tábla, keret,
hajszál → keretes; üveg → üveg; papír, textúra → textúrás; telt → telt; különben lebegő), a mozgás a webes mozgásból
(lágy, bimbó, úszás → nyugodt; maszk, kirajzolódás → maszkos; ütés, villanás → kinetikus; különben rugós), a hangulat a
mozgásból. Minden más: klasszikus stílus, szavankénti felirat, sötétített hook, lista, kártya, pill, lájk és követés,
kiemelő blokkos nyitókép. Írd felül, ha a márka mást kíván (egy csendes, személyes márkánál a karaoke felirat és a
keretes nyitókép jobb), és írj `miert`-et, ami a márkáról szól.
