# Az élő előnézet (videó-választó) működése

- **Nem renderelünk videót** az előnézethez: minden elem élő HTML-animáció egy 1080×1920-as színpadon (a vágó skillek
  koordinátái), telefonkeretben lekicsinyítve, 3-5 másodperces ismétlődő hurokban. A háttér az ügyfél fotója
  (`video/kepek/hatter.jpg`), a kivágásos és a csak-fej stílusnál fölötte a kivágott fej (`fej.png`), így a grafika a fej
  mögé kerülhet.
- **Motor:** `assets/video/elonezet.js` + `elonezet.css` (minden szabály a `#fazis-video` alá szűkítve). GSAP 3.12.5 a
  cdnjs-ről (`https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js`). Ha nem tölt be, a választó jelzi.
- **Jelenetek:** `SC.fo` (stílus + felirat + kártya + mozgás), `SC.hook`, `SC.tema`, `SC.nev`, `SC.fejezet`, `SC.zaro`,
  `SC.nyito`, `SC.hangulat`. Minden jelenet egy GSAP-idővonalra épít a saját idejében, a többi kategória aktuális
  választásával (ezért látszik a felirat-változat a választott stílusban). A jobb oldali **összeállítás** ezeket fűzi
  egymás után (~18 mp); a jelenetgombokkal ugrani lehet.
- **Teljesítmény:** a kis telefonok csak akkor futnak, amikor látszanak (IntersectionObserver); választáskor csak az érintett
  kategóriák épülnek újra.
- **Reels-felület:** a „Reels-felület és safe zone” kapcsoló minden telefonra ráteszi a Reels kezelőfelületét és a takart
  sávokat (felül 230, alul 420, jobbra 120 px).
- **Hang:** a hangminták a böngészőben szintetizálódnak (WebAudio, `OfflineAudioContext`), és lejátszás előtt egyforma
  hangerőre normálódnak (RMS-célérték, csúcskorlát). Nincs letöltött hangfájl, így licencgond sincs. Az „Hang az
  összeállításban” kapcsoló a zenét és a jelenetváltások effektjeit is lejátssza.
- **Állókép-mód:** `video-valaszto.html?kep=<kat>:<változat>@<mp>[&val=kat:id,…][&reels=1]` egyetlen teljes méretű
  színpadot rajzol megállítva; a `video.py kepek` ezzel készít headless Chrome-mal állóképeket (`leiras.kep()`).
  Az `osszeallitas@<mp>` a teljes sorozat egy pillanata.

## Minta-videó (B-terv a bemutatóhoz)
A választott elemekből egy rövid, márkázott MP4 is készülhet a `video.py minta`-val (ha a skill-verzió tartalmazza):
az összeállítás jelenetei egy felvétel fölött, képkockánként headless Chrome-ból, ffmpeg-gel összefűzve, zenével.
Igazi vágáshoz (leirat, szóra időzítés, arckövetés) a tag vágó skillje kell; ez csak a stílus bemutatása.
