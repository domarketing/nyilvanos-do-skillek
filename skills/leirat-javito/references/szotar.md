# Leirat-szótár

Ez a saját szótárad. Ide kerülnek azok a nevek, márkák, terméknevek és szavak, amiket az automatikus
felirat a te felvételeiden rendszeresen félrehall vagy rosszul ír. A `leirat-javito` skill minden
leirat előtt elolvassa: ami itt szerepel, azt kérdés nélkül javítja, és csak azt kérdezi meg, ami
nincs benne.

Alapból üres. Háromféleképpen tölthető fel:

1. **A cégprofilból.** Ha van `cegprofil.md`, Claude kiírja belőle a cég, a vezető és a csapat
   nevét, a termékeket, a szolgáltatásokat és a programokat az 1. és a 3. szakaszba.
2. **Leiratról leiratra.** Amit a névkérdéskörben megerősítesz, az a félrehallott alakkal együtt
   ide kerül. Pár leirat után a legtöbb nevet már kérdés nélkül javítja.
3. **Kézzel.** Bármikor beírhatod a gyakran előforduló neveket és szavakat.

Csak a név, a vállalkozás és a félrehallás kerüljön ide. Személyes történet, pénzügyi adat vagy
elérhetőség ne. Ha a skillt másokkal is megosztod, a szótárad ügyfélneveket tartalmazhat: előtte
nézd át.

---

## Formátum

Minden táblázat ugyanígy épül fel, mert a `scripts/felrehallas_scan.py` ebből olvassa ki, mit
keressen a kész leiratban:

```markdown
| Helyes | Félrehallott alakok | Megjegyzés |
|---|---|---|
| **Kovács Anna** | „Kovács Ana”, „Kovác Anna” | ügyfél, Napfény Jóga |
| **Make** | „mék”? | automatizáló szoftver |
| **Napfény Jóga** | | külön írva, mindkettő nagy kezdőbetűvel |
```

(A fenti sorok csak példák, a kódblokkban lévő sorokat a szkript nem olvassa.)

- **Helyes:** a helyes írásmód, félkövérrel. Becenév mehet mellé idézőjelben: **Kovács Anna „Panni”**.
- **Félrehallott alakok:** ahogy a felirat írja, „…” idézőjelben, vesszővel elválasztva. A szkript
  ezeket keresi kis- és nagybetűtől függetlenül; négy betűtől a toldalékos alakot is megtalálja.
- **Kérdőjel a záró idézőjel után** („mék”?): az alak helyes szó is lehet, ezért a szkript csak
  `FIGYELJ` szinten jelzi. Kérdőjel nélkül `HIBA`.
- Ha nincs ismert félrehallás, csak a helyes írásmód a lényeg: a második oszlop maradjon üres.
- Ütközés vagy bizonytalanság a 8. szakaszba kerül.

---

## 1. Saját csapat

Vezető, előadók, munkatársak, állandó közreműködők.

| Helyes | Félrehallott alakok | Megjegyzés |
|---|---|---|

## 2. Ügyfelek, vendégek, kérdezők

Akik a felvételeken bemutatkoznak, kérdeznek, ajánlást mondanak. Ábécérendben.

| Helyes | Félrehallott alakok | Megjegyzés |
|---|---|---|

## 3. Saját márkák, termékek, szolgáltatások, programok

A cégnév, a termékek és programok neve, a saját fogalmak és módszerek neve, a weboldal aloldalai
(linkek, ékezet nélküli slugok).

| Helyes | Félrehallott alakok | Megjegyzés |
|---|---|---|

## 4. Szoftverek és eszközök

A gyakori szoftverneveket (Claude, ChatGPT, Canva, ClickUp, ManyChat és társaik) a szkript magától
is keresi. Ide azt írd, amit te használsz, és a felirat rendszeresen elront.

| Helyes | Félrehallott alakok | Megjegyzés |
|---|---|---|

## 5. Külső nevek, helyszínek, rendezvények

Szakmai szereplők, akikre gyakran hivatkozol, külföldi nevek, konferenciák, helyszínek.

| Helyes | Félrehallott alakok | Megjegyzés |
|---|---|---|

## 6. Házi írásmód

Az egységes írásmód szabályai: hogyan írjátok a márkaneveket toldalékkal, a pénzösszegeket, a
százalékot, a rövidítéseket. Ha egy szabály géppel ellenőrizhető, a táblázatba is írd be (például:
helyes **AI-val**, félrehallott alak „AI-jal”).

Szabályok:

-

| Helyes | Félrehallott alakok | Megjegyzés |
|---|---|---|

## 7. Az előadó beszédstílusa: ezeket NE javítsd

Az előadó jellegzetes szófordulatai és töltelékszavai, amik könnyű szerkesztésnél maradnak, mert
ezektől ismerhető fel a szövege (például „ugye”, „na”, „hát”, „szóval”, „nagyon-nagyon-nagyon”).

-

## 8. Nyitott kérdések és ütközések

Amit a következő leiratnál meg kell kérdezni, és ahol a felhasználó válasza ellentmondott a
szótárnak. A választ írd vissza a megfelelő szakaszba, innen pedig töröld.

-
