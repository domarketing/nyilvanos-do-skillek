# Példa: Koppány Lili (tájépítész, koppanylili.hu) · az első teljes futás az új egyediség-eszközökkel

Sorrend, ahogy a futás ment (2026.10.19., 34 perc az első publikálásig):
1. `marka-dns.json`: a márka-diagnózis (szakma, közönség, hangnem, tárgyi világ 11 névvel ellátott színnel,
   formanyelv, az 5 karakter Lilinél: botanikus tábla · tervezőasztal · préri · kerti napló · arborétum).
2. `paletta-javaslat.json` (`paletta_gen.py`), `betu-javaslat.json` (`betu_valaszto.py`), `ikon-javaslat.json`
   (`ikon_technika.py`): a generátorok javaslatai.
3. `betu-szoveg.json`: a betűpárok finomítása (ahol a választó a régi futás betűit adta volna, cseréltünk a
   jelöltekből: Ibarra Real Nova, Funnel Display, Big Shoulders Display, Young Serif + a saját Karla, Brygada 1918).
4. `ikon-spec.json`: az öt technika (cianotípia, tervrajz-nézet, papírkivágás, ceruzaskicc, herbárium-kollázs)
   ügyfélre írt csavarral (`csavar` mező).
5. `gen_arculat.py`: az `arculat.json` írója. Nézd meg a CIM, ALCIM, GOMB, KARTYA, FOTO listákat: minden opció
   egy Lili-karakterből jön, és van `reszlet` mezője (mi jön a szakmából: Tab. 01 táblaszám, méretvonal, perforált
   magtasak, névtábla két csavarral, léptékvonal, üvegház-boltív…).

A fájlok a saját munkamappájukban futottak (bemenet/, ikonok/); itt csak mintának vannak. Ne másold szó szerint:
minden ügyfélnél az ő tárgyi világából kell megírni.
