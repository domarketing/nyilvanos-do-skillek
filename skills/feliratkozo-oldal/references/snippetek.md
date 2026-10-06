# HTML FRAGMENT SNIPPETEK A BULLET LISTÁKHOZ

Itt vannak a kész, másolható HTML darabkák a különböző bullet listákhoz
(pipa-ikonos, számozott, csillag-ikonos, napi lista). Amikor a minta
alapján felépíted az oldalt, ezeket a fragmenteket használd a felsorolásos
szekciókhoz. Mindegyiket annyiszor ismételd, ahány pont kell: egyszerűen
másold a `<li>...</li>` (vagy `<div>...</div>`) blokkot.

Megjegyzés: a class-nevekben szereplő `brandPrimary` / `brandSecondary`
a user által megadott elsődleges/másodlagos színt jelenti. Állítsd be a
Tailwind configban, vagy cseréld a megfelelő szín-class-ra / inline stílusra.

---

## 1. WEBINÁR: pipa-ikonos lista ("Ezekről a titkokról lesz szó" szekció)

```html
<li class="flex gap-3 items-start">
  <span class="flex-shrink-0 mt-1 text-brandPrimary">
    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7"/>
    </svg>
  </span>
  <span class="text-gray-700 text-base md:text-lg leading-snug">
    <strong class="text-gray-900">RÖVID FŐBB GONDOLAT</strong> – részletező / kifejtő szöveg.
  </span>
</li>
```

**Felhasználás:** Ennek a `<li>` blokknak a sokszorozása. Erős részt
`<strong>`-ba tedd, a többit hagyd normálban.

---

## 2. KIHÍVÁS: számozott lista a "Mire kell figyelned?" szekcióhoz

```html
<div class="bg-white p-5 rounded-xl flex gap-5 items-start shadow-sm border border-gray-100 hover:border-brandSecondary transition-all duration-300 group">
  <div class="flex-shrink-0 w-10 h-10 rounded-lg step-number flex items-center justify-center text-white font-black group-hover:scale-110 transition-transform mt-0.5 shadow-md">SZÁM</div>
  <p class="text-gray-700 text-base md:text-lg leading-snug font-semibold">
    BULLET SZÖVEGE.<span class="text-gray-500 font-normal"> Kiegészítő rész normál súllyal, ha kell.</span>
  </p>
</div>
```

**Felhasználás:** A `SZÁM` helyére tedd 1, 2, 3, ... A fő mondatot
hagyd `font-semibold`-on, a magyarázó részt rakd `<span>`-be.

---

## 3. KIHÍVÁS: pipa-ikonos napi lista (a napi blokkokhoz)

```html
<li class="flex items-start gap-2">
  <span class="text-brandPrimary font-bold flex-shrink-0">✓</span>
  <span>BULLET SZÖVEG</span>
</li>
```

**Felhasználás:** Egyszerű, csak ezt sokszorozzuk a 3 napi blokkban.
Az első bulletet ki lehet emelni `font-bold text-gray-900`-cel a parent
`<li>`-n, hogy hangsúlyosabb legyen.

---

## 4. WEBINÁR + KIHÍVÁS: csillag-ikonos eredmény-bullet ("Ki vagy te?" szekció)

```html
<li class="flex gap-3 items-start">
  <span class="flex-shrink-0 mt-1 text-brandSecondary">
    <svg class="w-5 h-5" viewBox="0 0 576 512" fill="currentColor">
      <path d="M259.3 17.8L194 150.2 47.9 171.5c-26.2 3.8-36.7 36.1-17.7 54.6l105.7 103-25 145.5c-4.5 26.3 23.2 46 46.4 33.7L288 439.6l130.7 68.7c23.2 12.2 50.9-7.4 46.4-33.7l-25-145.5 105.7-103c19-18.5 8.5-50.8-17.7-54.6L382 150.2 316.7 17.8c-11.7-23.6-45.6-23.9-57.4 0z"/>
    </svg>
  </span>
  <span class="text-gray-700 text-base md:text-lg leading-snug font-medium">
    EREDMÉNY / TAPASZTALAT MONDATBAN.
  </span>
</li>
```

**Felhasználás:** A "Ki az a ..." szekcióban lévő eredmények
felsorolásához. Mindegyik egy konkrét tény / eredmény legyen.

---

## EMOJI HASZNÁLAT

Az ikonok mellett a főcímek mellé bátran tehetsz emojikat a felhasználói
input alapján. A "Ezekről a titkokról lesz szó" cím elé pl. 🧠, az
ajándék blokkok elé 🎁. Csak akkor használd őket, ha a user is használt
emojit, vagy ha a mintában is szerepel (pl. 🧠 a bullet-szekció címe
elé van rakva alapból).
