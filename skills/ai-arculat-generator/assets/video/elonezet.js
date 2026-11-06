/* Videó-választó, élő előnézet (AI arculat-generátor, 3. fázis).
   Minden elem GSAP-idővonal egy 1080×1920-as színpadon, telefonkeretben, ismétlődő hurokban.
   Adat: <script type="application/json" id="vv-adat"> (téma, szövegek, képek, kategóriák).
   Mentés: arculat/video-v<verzio> {allapot, gepi, szoveg, frissitve, verzio, jovahagyva}; db nélkül localStorage.
   Regisztráció: window.FAZISOK.video = {init: function(db){}} (az arculat-központ hívja). */
(function () {
'use strict';
var ROOT = document.getElementById('fazis-video');
if (!ROOT) return;
var VD = JSON.parse(document.getElementById('vv-adat').textContent);
var TX = VD.tartalom, KAT = VD.kategoriak, FEJ = VD.fej, IMG = VD.kepek, CSSV = VD.cssv, TEMA = VD.tema;
var KATI = {}; KAT.forEach(function (k) { KATI[k.kat] = k; });
var FO = ['stilus', 'felirat', 'kartya', 'mozgas', 'hangulat'];
var G = window.gsap;

function E(tag, cls, html, par) {
  var e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  if (par) par.appendChild(e);
  return e;
}
function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
function hossz(s) { return String(s || '').replace(/<[^>]+>/g, '').length; }
function illeszt(s, alap, szel, k) { return Math.round(Math.min(alap, szel / ((k || 0.6) * Math.max(1, hossz(s))))); }
function ikon(i) { var l = IMG.ikonok || []; return l.length ? l[i % l.length].src : ''; }
function ikonNev(i) { var l = IMG.ikonok || []; return l.length ? (l[i % l.length].cimke || '') : ''; }
function $$(s, r) { return Array.prototype.slice.call((r || ROOT).querySelectorAll(s)); }

/* ---------------------------------------------------------------- textúra (a márka saját textúrájából) */
var TEX = (function () {
  var t = (TEMA.motivum || {}).textura || 'motivum', szin = CSSV['--v-szoveg-kartyan'] || '#222', svg = '';
  function enc(s) { return 'url("data:image/svg+xml,' + encodeURIComponent(s) + '")'; }
  if (t === 'szintvonalak') {
    var p = '';
    for (var i = 0; i < 14; i++) {
      var r = 60 + i * 46, d = 'M';
      for (var a = 0; a <= 360; a += 10) {
        var rad = a * Math.PI / 180, rr = r * (1 + 0.08 * Math.sin(3 * rad + i * 0.7) + 0.05 * Math.cos(5 * rad + i));
        d += (a ? ' L' : '') + (540 + rr * Math.cos(rad) * 1.25).toFixed(1) + ' ' + (980 + rr * Math.sin(rad)).toFixed(1);
      }
      p += '<path d="' + d + 'Z" fill="none" stroke="' + szin + '" stroke-opacity=".16" stroke-width="3"/>';
    }
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920">' + p + '</svg>';
  } else if (t === 'pottyok') {
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48"><circle cx="8" cy="8" r="3.2" fill="' + szin + '" fill-opacity=".16"/></svg>';
  } else if (t === 'racs') {
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72"><path d="M72 0H0V72" fill="none" stroke="' + szin + '" stroke-opacity=".12" stroke-width="2"/></svg>';
  } else if (t === 'csikok') {
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><path d="M-10 50L50 -10" stroke="' + szin + '" stroke-opacity=".12" stroke-width="5"/></svg>';
  } else if (t === 'hullam') {
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="160" height="40"><path d="M0 20 Q40 0 80 20 T160 20" fill="none" stroke="' + szin + '" stroke-opacity=".14" stroke-width="3"/></svg>';
  } else if (t === 'levelek') {
    var lf = (TEMA.motivum.formak_svg || {})[TEMA.motivum.textura_forma || TEMA.motivum.jel] || '';
    var li = lf.replace(/^[\s\S]*?<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '');
    if (li) {
      var ls = '', poz = [[40, 30, 0.55, -20], [250, 60, 0.42, 35], [140, 210, 0.62, 160], [330, 260, 0.38, -70], [30, 320, 0.45, 80], [220, 340, 0.5, 15]];
      poz.forEach(function (q) { ls += '<g transform="translate(' + q[0] + ' ' + q[1] + ') rotate(' + q[3] + ' 50 50) scale(' + q[2] + ')" fill="none" stroke="' + szin + '" stroke-opacity=".2" stroke-width="' + (2.4 / q[2]).toFixed(1) + '">' + li.replace(/fill="[^"]*"/g, '') + '<path d="M50 14 L50 90" /></g>'; });
      svg = '<svg xmlns="http://www.w3.org/2000/svg" width="420" height="420" viewBox="0 0 420 420">' + ls + '</svg>';
    }
  } else if (t === 'papir') {
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .09 0"/></filter><rect width="300" height="300" filter="url(#n)"/></svg>';
  } else {
    var j = (TEMA.motivum.formak_svg || {})[TEMA.motivum.jel] || '';
    var inner = j.replace(/^[\s\S]*?<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '');
    svg = inner ? '<svg xmlns="http://www.w3.org/2000/svg" width="140" height="140" viewBox="0 0 140 140"><g transform="translate(40 40) scale(.6)" fill="' + szin + '" fill-opacity=".09">' + inner + '</g></svg>' : '';
  }
  return svg ? enc(svg) : 'none';
})();
var JEL = (function () { var j = (TEMA.motivum.formak_svg || {})[TEMA.motivum.jel] || ''; return j; })();
function texTo(el) { el.style.backgroundImage = TEX; var t = (TEMA.motivum || {}).textura; el.style.backgroundSize = (t === 'szintvonalak' || t === 'papir') ? 'cover' : (t === 'levelek' ? '420px 420px' : 'auto'); }

/* ---------------------------------------------------------------- Reels-felület */
function reelsUI() {
  var ik = function (d) { return '<svg width="66" height="62" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2">' + d + '</svg>'; };
  return '<div class="zn" style="left:0;top:0;width:1080px;height:230px"></div>' +
    '<div class="zn" style="left:0;top:1500px;width:1080px;height:420px"></div>' +
    '<div class="zn" style="left:960px;top:230px;width:120px;height:1270px;border-top:0;border-bottom:0"></div>' +
    '<div class="zl" style="left:40px;top:160px">felül 230 px</div><div class="zl" style="left:40px;top:1520px">alul 420 px</div>' +
    '<div class="zl" style="left:780px;top:640px">jobbra 120 px</div>' +
    '<div class="u" style="left:44px;top:70px;font-size:46px;font-weight:900">Reels</div>' +
    '<div class="u" style="left:972px;top:1010px;width:90px;text-align:center;line-height:1.3">' +
    ik('<path d="M12 21s-8-5.2-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 5.8-8 11-8 11z"/>') + '<br>2 418<br><br>' +
    ik('<path d="M21 12a8 8 0 1 1-3.3-6.5L21 4l-.8 4.2A8 8 0 0 1 21 12z"/>') + '<br>96<br><br>' +
    ik('<path d="M22 3 2 11l7 3 3 7z"/><path d="M9 14l13-11"/>') + '</div>' +
    '<div class="u" style="left:44px;top:1660px;width:860px"><b style="font-size:34px">' + esc(VD.marka.slug) + '</b>' +
    '<div style="font-size:29px;font-weight:600;margin-top:16px">' + esc((TX.felirat || []).join(' ')) + '… <b>több</b></div>' +
    '<div style="font-size:27px;font-weight:600;margin-top:12px">♫ eredeti hang · ' + esc(VD.marka.nev) + '</div></div>';
}

/* ---------------------------------------------------------------- színpad */
function szinpad(kont, szel, nagy) {
  var k = szel / 1080;
  var ph = E('div', 'vph' + (nagy ? ' nagy' : ''), null, kont);
  var sc = E('div', 'vscr', null, ph);
  sc.style.width = szel + 'px'; sc.style.height = Math.round(1920 * k) + 'px';
  E('div', 'isl', null, ph);
  var st = E('div', 'vst', null, sc);
  st.style.transform = 'scale(' + k + ')';
  for (var v in CSSV) st.style.setProperty(v, CSSV[v]);
  var bg = E('img', 'vbg', null, st); bg.src = IMG.bg; bg.alt = ''; bg.draggable = false;
  var be = E('div', 'vbe', null, st);
  var fej = E('div', 'vfej', null, st);
  if (IMG.fej && FEJ && FEJ.fej_doboz) {
    var fi = E('img', null, null, fej), d = FEJ.fej_doboz;
    fi.src = IMG.fej; fi.alt = ''; fi.style.left = d[0] + 'px'; fi.style.top = d[1] + 'px'; fi.style.width = d[2] + 'px'; fi.style.height = d[3] + 'px';
  }
  var fr = E('div', 'vfr', null, st);
  var ui = E('div', 'vui', reelsUI(), st);
  return {ph: ph, st: st, bg: bg, fej: fej, be: be, fr: fr, ui: ui, k: k};
}
function urit(S) { S.be.innerHTML = ''; S.fr.innerHTML = ''; if (G) G.set([S.bg, S.fej], {clearProps: 'transform,visibility'}); }

var FT = FEJ && FEJ.fejteto != null ? FEJ.fejteto : 560;
var FA = FEJ && FEJ.all != null ? FEJ.all : 1160;
var FX = FEJ && FEJ.fej_x ? FEJ.fej_x : [340, 740];
var VANFEJ = !!(IMG.fej && FEJ && FEJ.fej_doboz);
function vidP(mod) {
  if (mod === 'fel') { var cel = 300, s = Math.max(1, (1920 - cel) / (1920 - FT)); return {s: s, y: cel - FT * s}; }
  if (mod === 'le') return {s: 1, y: Math.max(0, 870 - FT)};
  return {s: 1, y: 0};
}
function vid(tl, S, mod, t) { var p = vidP(mod); tl.set([S.bg, S.fej], {scale: p.s, y: p.y, transformOrigin: '50% 0%'}, t); return p; }
function yAt(p, y) { return y * p.s + p.y; }
function jelenet(tl, S, t0, t1) {
  var f = E('div', 'jel', null, S.fr), b = E('div', 'jel', null, S.be);
  tl.set([f, b], {visibility: 'visible'}, t0);
  tl.set([f, b], {visibility: 'hidden'}, t1);
  return {f: f, b: b};
}
function fejLat(tl, S, t0, t1) { if (!VANFEJ) return; tl.set(S.fej, {visibility: 'visible'}, t0); tl.set(S.fej, {visibility: 'hidden'}, t1); }
function sav(tl, par, t0, t1) { var b = E('div', 'bar', '<i></i>', par); tl.fromTo(b.firstChild, {scaleX: 0.18}, {scaleX: 0.62, duration: t1 - t0, ease: 'none'}, t0); }

/* ---------------------------------------------------------------- mozgás-készletek */
function villan(tl, par, t) { var f = E('div', 'abs', null, par); f.style.cssText = 'left:0;top:0;width:1080px;height:1920px;background:#fff;opacity:0'; tl.fromTo(f, {opacity: 0.55}, {opacity: 0, duration: 0.22}, t); }
var MOZ = {
  nyugodt: {be: function (tl, e, t) { tl.fromTo(e, {autoAlpha: 0, y: 34, filter: 'blur(8px)'}, {autoAlpha: 1, y: 0, filter: 'blur(0px)', duration: 0.6, ease: 'power2.out'}, t); },
    ki: function (tl, e, t) { tl.to(e, {autoAlpha: 0, y: -12, filter: 'blur(6px)', duration: 0.38, ease: 'power1.in'}, t); }, punch: 0},
  maszkos: {be: function (tl, e, t) { tl.fromTo(e, {autoAlpha: 1, clipPath: 'inset(0% 100% 0% 0%)'}, {clipPath: 'inset(0% 0% 0% 0%)', duration: 0.55, ease: 'power3.inOut'}, t); },
    ki: function (tl, e, t) { tl.to(e, {clipPath: 'inset(0% 0% 0% 100%)', duration: 0.4, ease: 'power3.in'}, t); tl.set(e, {autoAlpha: 0}, t + 0.41); }, punch: 0},
  rugos: {be: function (tl, e, t) { tl.fromTo(e, {autoAlpha: 0, scale: 0.55}, {autoAlpha: 1, scale: 1, duration: 0.45, ease: 'back.out(1.9)'}, t); },
    ki: function (tl, e, t) { tl.to(e, {autoAlpha: 0, scale: 0.88, duration: 0.2, ease: 'power2.in'}, t); }, punch: 1.03},
  kinetikus: {be: function (tl, e, t) { tl.fromTo(e, {autoAlpha: 0, scale: 1.5, rotation: -3}, {autoAlpha: 1, scale: 1, rotation: 0, duration: 0.22, ease: 'expo.out'}, t); },
    ki: function (tl, e, t) { tl.to(e, {autoAlpha: 0, x: -150, duration: 0.18, ease: 'power2.in'}, t); }, punch: 1.05, villan: true},
  szerkesztosegi: {be: function (tl, e, t) { tl.fromTo(e, {autoAlpha: 0, y: 14}, {autoAlpha: 1, y: 0, duration: 0.45, ease: 'power2.out'}, t); },
    ki: function (tl, e, t) { tl.to(e, {autoAlpha: 0, duration: 0.3}, t); }, punch: 0, alahuz: true}
};
function M(c) { return MOZ[c.mozgas] || MOZ.rugos; }
function belep(tl, c, e, t, par) { var m = M(c); m.be(tl, e, t); if (m.villan && par) villan(tl, par, t); }
function kilep(tl, c, e, t) { M(c).ki(tl, e, t); }
function punch(tl, S, c, p, t) { var m = M(c); if (!m.punch) return; tl.to([S.bg, S.fej], {scale: p.s * m.punch, duration: 0.14, ease: 'power2.out', yoyo: true, repeat: 1}, t); }

/* ---------------------------------------------------------------- felirat (5 változat) */
var SZAVAK = TX.felirat || ['…'], KI = TX.felirat_kiemelt;
function szoMeret(w, alap) { var n = hossz(w); var m = n <= 9 ? 92 : n <= 12 ? 82 : n <= 15 ? 70 : n <= 18 ? 60 : 52; return Math.round(m * alap / 92); }
function felirat(tl, par, v, t0, t1, yc, ink) {
  var cap = E('div', 'cap' + (ink ? ' ink' : ''), null, par);
  cap.style.top = (yc - 90) + 'px'; cap.style.height = '180px';
  var n = SZAVAK.length, d = (t1 - t0) / n;
  if (v === 'mondatsav') {
    var ms = E('div', 'msav', SZAVAK.map(function (w) { return '<span>' + esc(w) + '</span>'; }).join(' '), par);
    ms.style.top = (yc - 64) + 'px';
    var sp = ms.querySelectorAll('span');
    tl.fromTo(ms, {autoAlpha: 0, y: 16}, {autoAlpha: 1, y: 0, duration: 0.25}, t0 - 0.05);
    SZAVAK.forEach(function (w, i) { tl.set(sp[i], {attr: {'class': i === KI ? 'on ak' : 'on'}}, t0 + i * d); });
    tl.to(ms, {autoAlpha: 0, duration: 0.2}, t1 - 0.15);
    return;
  }
  if (v === 'karaoke') {
    var gr = [], cur = [];
    SZAVAK.forEach(function (w, i) { cur.push(i); if (cur.length === 3 || /[.,!?]$/.test(w)) { gr.push(cur); cur = []; } });
    if (cur.length) gr.push(cur);
    gr.forEach(function (g) {
      var e = E('div', 'g', g.map(function (i) { return '<span>' + esc(SZAVAK[i]) + '</span>'; }).join(''), cap);
      e.style.top = '48px';
      var sp = e.querySelectorAll('span'), gs = t0 + g[0] * d, ge = t0 + (g[g.length - 1] + 1) * d;
      tl.fromTo(e, {autoAlpha: 0, y: 8}, {autoAlpha: 1, y: 0, duration: 0.1}, gs);
      g.forEach(function (i, j) { tl.set(sp[j], {attr: {'class': 'ak'}}, t0 + i * d); if (j > 0) tl.set(sp[j - 1], {attr: {'class': ''}}, t0 + i * d); });
      tl.to(e, {autoAlpha: 0, duration: 0.06}, ge - 0.07);
    });
    return;
  }
  SZAVAK.forEach(function (w, i) {
    var ts = t0 + i * d, e;
    if (v === 'doboz') {
      e = E('div', 'bx' + (i === KI ? ' ki' : ''), esc(w), cap); e.style.top = '48px';
      tl.fromTo(e, {autoAlpha: 0, scale: 0.85}, {autoAlpha: 1, scale: 1, duration: 0.12, ease: 'back.out(2)'}, ts);
    } else if (v === 'slam') {
      var tx = w.replace(/[.,!?;:]+$/, '');
      e = E('div', 'w slam' + (i === KI ? ' ki' : ''), esc(tx), cap); e.style.top = '28px'; e.style.fontSize = szoMeret(tx, 118) + 'px';
      tl.fromTo(e, {autoAlpha: 0, scale: 1.45, rotation: -4}, {autoAlpha: 1, scale: 1, rotation: 0, duration: 0.16, ease: 'expo.out'}, ts);
    } else {
      e = E('div', 'w' + (i === KI ? ' ki' : ''), esc(w), cap); e.style.top = '38px'; e.style.fontSize = szoMeret(w, 92) + 'px';
      tl.fromTo(e, {autoAlpha: 0, y: 10}, {autoAlpha: 1, y: 0, duration: 0.09, ease: 'power2.out'}, ts);
    }
    tl.to(e, {autoAlpha: 0, duration: 0.05}, ts + d - 0.06);
  });
}
function kulcsIdo(t0, t1) { var n = SZAVAK.length; return t0 + (KI != null ? KI : 0) * (t1 - t0) / n; }

/* ---------------------------------------------------------------- információs kártya (5 forma + tiszta) */
function infoKartya(par, v, tiszta) {
  var I = TX.info || {}, f = tiszta ? 'tiszta' : v;
  var e = E('div', 'k k-' + f + ' kozep', null, par);
  var szam = esc(I.szam) + (I.egyseg ? '<small>' + esc(I.egyseg) + '</small>' : '');
  var nfs = illeszt(I.szam, 100, 400, 0.55), ef = Math.round(nfs * 0.46);
  var szel = hossz(I.szam) * 0.55 * nfs + (I.egyseg ? hossz(I.egyseg) * 0.5 * ef + 10 : 0);
  var ik = ikon(0) && szel < 420, mell = hossz(I.cimke) <= 22 && szel + (ik ? 128 : 0) + 24 + 300 <= 860;
  var h = (I.kicker && !tiszta ? '<div class="kk">' + esc(I.kicker) + '</div>' : '') +
    '<div class="kr">' + (ik ? '<img class="ki2" src="' + ikon(0) + '" alt="">' : '') +
    '<div class="kn" style="font-size:' + nfs + 'px">' + esc(I.szam) + (I.egyseg ? '<small style="font-size:' + ef + 'px">' + esc(I.egyseg) + '</small>' : '') + '</div>' +
    (mell ? '<div class="kl">' + esc(I.cimke) + '</div>' : '') + '</div>' + (mell ? '' : '<div class="kl alatta">' + esc(I.cimke) + '</div>');
  if (f === 'keretes' && TX.tabla_cimke) h += '<div class="tab">' + esc(TX.tabla_cimke) + '</div>';
  e.innerHTML = h;
  if (f === 'texturas') texTo(e);
  return e;
}

/* ---------------------------------------------------------------- jelenetek */
var SC = {};
/* fő jelenet: a vágási stílus a felirattal, a kártyával és a mozgással (4,2 mp) */
SC.fo = function (S, c, tl, t0) {
  var t1 = t0 + 4.2, J = jelenet(tl, S, t0, t1), st = c.stilus, p, e, tk = kulcsIdo(t0 + 0.25, t0 + 3.6);
  if (st === 'panel') {
    p = vid(tl, S, 'le', t0);
    var pn = E('div', 'pn', '<div class="tx"></div><div class="el"></div>', J.f); texTo(pn.firstChild);
    var I = TX.info || {}, nfs = illeszt(I.szam, 150, 440, 0.55), pszel = hossz(I.szam) * 0.55 * nfs + (I.egyseg ? hossz(I.egyseg) * 0.25 * nfs : 0);
    var pc = E('div', 'abs', '<span class="pn-tag">' + esc(I.kicker || VD.marka.nev) + '</span><div class="pn-row"><div class="pn-num" style="font-size:' + nfs + 'px">' + esc(I.szam) +
      (I.egyseg ? '<small style="font-size:' + Math.round(nfs * 0.4) + 'px">' + esc(I.egyseg) + '</small>' : '') + '</div><div class="pn-lab" style="max-width:' + Math.max(240, Math.round(860 - pszel - (pszel < 420 ? 210 : 0))) + 'px">' + esc(I.cimke) + '</div>' +
      (ikon(0) && pszel < 420 ? '<div class="pn-tile"><img src="' + ikon(0) + '" alt=""></div>' : '') + '</div>', pn);
    pc.style.cssText = 'left:60px;top:235px;width:900px';
    tl.fromTo(pn, {y: -830}, {y: 0, duration: 0.5, ease: 'power3.out'}, t0);
    belep(tl, c, pc.firstChild, t0 + 0.35); belep(tl, c, pc.lastChild, t0 + 0.55);
    felirat(tl, J.f, c.felirat, t0 + 0.45, t0 + 3.6, 700, true);
    tl.to(pn, {y: -830, duration: 0.45, ease: 'power3.in'}, t1 - 0.5);
    sav(tl, J.f, t0, t1);
    return t1;
  }
  if (st === 'kivagasos' || st === 'csakfej') {
    p = vid(tl, S, 'nativ', t0); fejLat(tl, S, t0, t1);
    var cy = Math.min(1620, Math.max(1440, FA + 62)) + 40;
    if (st === 'kivagasos') {
      var kw = TX.kulcsszo || 'ARCULAT', fs = illeszt(kw, 260, 1000, 0.74);
      var bw = E('div', 'nagyszo', esc(kw), J.b); bw.style.fontSize = fs + 'px'; bw.style.top = (FT + 66 - fs * 0.8) + 'px';
      var tw = 236, ty = Math.round(FT + (FA - FT) * 0.38 - tw / 2);
      var lx = Math.max(16, FX[0] - tw - 30), rx = Math.min(1080 - tw - 16, FX[1] + 30);
      var str = E('div', 'streak', null, J.b); str.style.cssText = 'left:' + (lx + tw / 2) + 'px;width:' + (rx - lx) + 'px;top:' + (ty + tw / 2 - 9) + 'px';
      var t1e = E('div', 'tile', (ikon(0) ? '<img src="' + ikon(0) + '" alt="">' : '') + '<b>' + esc(ikonNev(0)) + '</b>', J.b);
      var t2e = E('div', 'tile', (ikon(1) ? '<img src="' + ikon(1) + '" alt="">' : '') + '<b>' + esc(ikonNev(1)) + '</b>', J.b);
      t1e.style.cssText = 'left:' + lx + 'px;top:' + ty + 'px'; t2e.style.cssText = 'left:' + rx + 'px;top:' + ty + 'px';
      var kp = E('div', 'abs kozep', '<span class="kpill">' + esc(TX.kicker_pill || (TX.hook || {}).kicker || VD.marka.nev) + '</span>', J.f);
      kp.style.top = Math.max(250, FT + 66 - fs * 0.8 - 130) + 'px';
      belep(tl, c, kp, t0 + 0.15, J.f);
      tl.fromTo(bw, {autoAlpha: 0, scale: 0.82, transformOrigin: '50% 100%'}, {autoAlpha: 1, scale: 1, duration: 0.5, ease: 'power3.out'}, t0 + 0.35);
      belep(tl, c, t1e, t0 + 0.95); belep(tl, c, t2e, t0 + 1.15);
      tl.fromTo(str, {scaleX: 0, autoAlpha: 0}, {scaleX: 1, autoAlpha: 1, duration: 0.5, ease: 'power2.out'}, t0 + 1.3);
      [kp, bw, t1e, t2e, str].forEach(function (x) { tl.to(x, {autoAlpha: 0, duration: 0.25}, t1 - 0.4); });
    } else {
      var H = TX.hook || {}, so = H.sorok || ['', ''];
      var f1 = illeszt(so[0], 92, 900, 0.66), f2 = illeszt(so[1], 92, 900, 0.66);
      var mk = E('div', 'mkst', '<div><span class="mk f" style="font-size:' + f1 + 'px">' + esc(so[0]) + '</span></div><div><span class="mk p" style="font-size:' + f2 + 'px">' + esc(so[1]) + '</span></div>', J.b);
      mk.style.top = (FT + 28 - (f1 * 1.02 + 24) - 18 - (f2 * 1.02 + 24)) + 'px';
      var b1 = mk.children[0].firstChild, b2 = mk.children[1].firstChild;
      tl.fromTo(b1, {autoAlpha: 0, x: -60}, {autoAlpha: 1, x: 0, duration: 0.4, ease: 'power3.out'}, t0 + 0.3);
      tl.fromTo(b2, {autoAlpha: 0, x: 60}, {autoAlpha: 1, x: 0, duration: 0.4, ease: 'power3.out'}, t0 + 0.55);
      tl.to([b1, b2], {autoAlpha: 0, duration: 0.25}, t1 - 0.4);
    }
    var cc = E('div', 'capc', null, J.f); cc.style.top = (cy - 40) + 'px';
    karaokeSor(tl, cc, t0 + 0.3, t1 - 0.4);
    return t1;
  }
  /* klasszikus és tiszta */
  p = vid(tl, S, 'fel', t0);
  var sa = E('div', 's-alul', null, J.f); if (st === 'tiszta') sa.style.opacity = '1';
  felirat(tl, J.f, c.felirat, t0 + 0.25, t0 + 3.6, 1225);
  e = infoKartya(J.f, c.kartya, st === 'tiszta');
  e.style.top = (e.querySelector('.alatta') ? 1296 : 1320) + (c.felirat === 'mondatsav' ? 14 : 0) + 'px';
  belep(tl, c, e, tk, J.f);
  if (M(c).alahuz) { var kl = e.querySelector('.kn'); if (kl) { kl.style.position = 'relative'; var u = E('i', 'alahuz', null, kl); tl.fromTo(u, {scaleX: 0}, {scaleX: 1, duration: 0.5, ease: 'power2.out'}, tk + 0.45); } }
  punch(tl, S, c, p, tk);
  kilep(tl, c, e, t0 + 3.7);
  sav(tl, J.f, t0, t1);
  return t1;
};
function karaokeSor(tl, cc, t0, t1) {
  var n = SZAVAK.length, d = (t1 - t0) / n, gr = [], cur = [];
  SZAVAK.forEach(function (w, i) { cur.push(i); if (cur.length === 3 || /[.,!?]$/.test(w)) { gr.push(cur); cur = []; } });
  if (cur.length) gr.push(cur);
  gr.forEach(function (g) {
    var e = E('div', 'abs', g.map(function (i) { return '<span>' + esc(SZAVAK[i]) + '</span>'; }).join(''), cc);
    e.style.cssText = 'left:0;right:0;top:0;visibility:hidden';
    var sp = e.querySelectorAll('span');
    tl.set(e, {autoAlpha: 1}, t0 + g[0] * d);
    g.forEach(function (i, j) { tl.set(sp[j], {attr: {'class': 'ak'}}, t0 + i * d); if (j > 0) tl.set(sp[j - 1], {attr: {'class': ''}}, t0 + i * d); });
    tl.set(e, {autoAlpha: 0}, t0 + (g[g.length - 1] + 1) * d - 0.02);
  });
}

/* címsor (3 mp) */
SC.hook = function (S, c, tl, t0) {
  var t1 = t0 + 3.0, J = jelenet(tl, S, t0, t1), v = c.hook, H = TX.hook || {}, so = H.sorok || ['', ''], ki = H.kiemelt != null ? H.kiemelt : 1;
  vid(tl, S, 'nativ', t0);
  var e;
  if (v === 'sotetitett') {
    var sf = E('div', 's-felul', null, J.f); tl.fromTo(sf, {autoAlpha: 0}, {autoAlpha: 1, duration: 0.3}, t0);
    var fs = Math.min(illeszt(so[0], 96, 900, 0.56), illeszt(so[1], 96, 900, 0.56));
    e = E('div', 'abs', '<div class="h-kick">' + esc(H.kicker || '') + '</div><div class="h-cim" style="font-size:' + fs + 'px">' +
      so.map(function (s, i) { return '<span class="' + (i === ki ? 'ak' : '') + '">' + esc(s) + '</span>'; }).join('') + '</div>', J.f);
    e.style.cssText = 'left:60px;top:250px;width:900px';
    belep(tl, c, e.firstChild, t0 + 0.15, J.f);
    $$('span', e.lastChild).forEach(function (s, i) { belep(tl, c, s, t0 + 0.35 + i * 0.2); });
    tl.to([e, sf], {autoAlpha: 0, duration: 0.3}, t1 - 0.4);
  } else if (v === 'blokkok') {
    var f1 = illeszt(so[0], 96, 940, 0.66), f2 = illeszt(so[1], 96, 940, 0.66);
    e = E('div', 'mkst', '<div><span class="mk ' + (ki === 0 ? 'p' : 'f') + '" style="font-size:' + f1 + 'px">' + esc(so[0]) + '</span></div><div><span class="mk ' + (ki === 1 ? 'p' : 'f') + '" style="font-size:' + f2 + 'px">' + esc(so[1]) + '</span></div>', J.f);
    e.style.top = '270px';
    tl.fromTo(e.children[0].firstChild, {autoAlpha: 0, x: -80}, {autoAlpha: 1, x: 0, duration: 0.4, ease: 'power3.out'}, t0 + 0.15);
    tl.fromTo(e.children[1].firstChild, {autoAlpha: 0, x: 80}, {autoAlpha: 1, x: 0, duration: 0.4, ease: 'power3.out'}, t0 + 0.4);
    tl.to(e, {autoAlpha: 0, duration: 0.3}, t1 - 0.4);
  } else if (v === 'uveg') {
    var fs2 = Math.min(illeszt(so[0], 60, 600, 0.56), illeszt(so[1], 60, 600, 0.56));
    e = E('div', 'uveg', '<div class="jelk">' + (JEL || '') + '</div><div><div class="gk">' + esc(H.kicker || '') + '</div><div class="gt" style="font-size:' + fs2 + 'px">' +
      so.map(function (s, i) { return '<span class="' + (i === ki ? 'ak' : '') + '">' + esc(s) + '</span>'; }).join('<br>') + '</div></div>', J.f);
    e.style.top = '250px';
    belep(tl, c, e, t0 + 0.15, J.f);
    tl.to(e, {autoAlpha: 0, duration: 0.3}, t1 - 0.4);
  } else if (v === 'fejmogott') {
    fejLat(tl, S, t0, t1);
    var kw = TX.kulcsszo || so[ki] || '', fs3 = illeszt(kw, 260, 1000, 0.74);
    var bw = E('div', 'nagyszo', esc(kw), J.b); bw.style.fontSize = fs3 + 'px'; bw.style.top = (FT + 66 - fs3 * 0.8) + 'px';
    var kp = E('div', 'abs kozep', '<span class="kpill">' + esc(H.kicker || so[0]) + '</span>', J.f); kp.style.top = Math.max(250, FT + 66 - fs3 * 0.8 - 130) + 'px';
    belep(tl, c, kp, t0 + 0.1, J.f);
    tl.fromTo(bw, {autoAlpha: 0, y: 60}, {autoAlpha: 1, y: 0, duration: 0.55, ease: 'power3.out'}, t0 + 0.3);
    tl.to([bw, kp], {autoAlpha: 0, duration: 0.3}, t1 - 0.4);
  } else {
    var fs4 = Math.min(illeszt(so[0], 100, 900, 0.56), illeszt(so[1], 100, 900, 0.56));
    e = E('div', 'derenges', so.map(function (s, i) { return '<span class="' + (i === ki ? 'ak' : '') + '">' + esc(s) + '</span>'; }).join(''), J.f);
    e.style.top = '260px'; e.style.fontSize = fs4 + 'px';
    $$('span', e).forEach(function (s, i) { belep(tl, c, s, t0 + 0.15 + i * 0.22); });
    tl.to(e, {autoAlpha: 0, duration: 0.3}, t1 - 0.4);
  }
  return t1;
};

/* témaválasztó (2,8 mp) */
SC.tema = function (S, c, tl, t0) {
  var t1 = t0 + 2.8, J = jelenet(tl, S, t0, t1), v = c.tema, L = (TX.temak || []).slice(0, 4), ak = TX.aktiv != null ? TX.aktiv : 1;
  vid(tl, S, 'nativ', t0);
  var e;
  if (v === 'pillsor') {
    e = E('div', 'tpills', L.map(function (x, i) { return '<span class="p">' + (i + 1) + '. ' + esc(x) + '</span>'; }).join(''), J.f);
    e.style.top = '270px';
    var ps = e.querySelectorAll('.p');
    belep(tl, c, e, t0 + 0.1, J.f);
    if (ak > 0) tl.set(ps[ak - 1], {attr: {'class': 'p on'}}, t0 + 0.1);
    tl.set(ps[ak - 1] || ps[0], {attr: {'class': 'p'}}, t0 + 1.0);
    tl.set(ps[ak], {attr: {'class': 'p on'}}, t0 + 1.0);
    tl.fromTo(ps[ak], {scale: 0.92}, {scale: 1, duration: 0.35, ease: 'back.out(2)'}, t0 + 1.0);
    tl.to(e, {autoAlpha: 0, duration: 0.3}, t1 - 0.4);
  } else if (v === 'lepcso') {
    var cfs = illeszt(L[ak], 66, 900, 0.56);
    e = E('div', 'lepcso', '<div class="sor"><div class="vo"><i></i></div>' + L.map(function (x, i) { return '<div class="pt">' + (i + 1) + '</div>'; }).join('') +
      '</div><div class="ct" style="font-size:' + cfs + 'px">' + esc(L[ak]) + '</div>', J.f);
    e.style.top = '280px';
    var pts = e.querySelectorAll('.pt'), fill = e.querySelector('.vo i'), ct = e.querySelector('.ct');
    belep(tl, c, e.firstChild, t0 + 0.1, J.f);
    for (var i = 0; i < ak; i++) tl.set(pts[i], {attr: {'class': 'pt kesz'}}, t0 + 0.1);
    tl.fromTo(fill, {width: (ak - 1 < 0 ? 0 : (ak - 1) / Math.max(1, L.length - 1) * 100) + '%'}, {width: ak / Math.max(1, L.length - 1) * 100 + '%', duration: 0.5, ease: 'power2.inOut'}, t0 + 0.6);
    tl.set(pts[ak], {attr: {'class': 'pt on'}}, t0 + 1.0);
    belep(tl, c, ct, t0 + 1.05);
    tl.to(e, {autoAlpha: 0, duration: 0.3}, t1 - 0.4);
  } else {
    var rows = L.map(function (x, i) { return '<div class="t"><div class="n">' + (i < ak ? '✓' : (i + 1)) + '</div><div class="d">' + esc(x) + '</div>' + (i === ak ? '<span class="most">MOST</span>' : '') + '</div>'; }).join('');
    e = E('div', 'tm', '<div class="k1">' + esc(TX.temak_cim || 'Miről lesz szó') + '</div><div class="hl"></div>' + rows, J.f);
    var rowH = 74, top = Math.max(236, FT - 14 - (24 + 40 + L.length * (rowH + 6) + 14));
    e.style.top = top + 'px';
    var ts = e.querySelectorAll('.t'), hl = e.querySelector('.hl'), most = e.querySelector('.most');
    G.set(ts, {height: rowH, padding: '0 16px'});
    var sorY = function (i) { return ts[i] ? ts[i].offsetTop : 64 + i * (rowH + 6); };
    tl.set(ts, {opacity: function (i) { return i === ak - 1 ? 1 : 0.38; }}, t0);
    if (most) tl.set(most, {autoAlpha: 0}, t0);
    tl.set(hl, {top: sorY(Math.max(0, ak - 1)), height: rowH, autoAlpha: ak > 0 ? 1 : 0}, t0);
    belep(tl, c, e, t0 + 0.1, J.f);
    tl.to(hl, {top: sorY(ak), duration: 0.45, ease: 'power3.inOut', autoAlpha: 1}, t0 + 0.95);
    tl.to(ts[ak - 1] || ts[0], {opacity: ak > 0 ? 0.38 : 1, duration: 0.3}, t0 + 0.95);
    tl.to(ts[ak], {opacity: 1, duration: 0.3}, t0 + 1.0);
    if (most) tl.fromTo(most, {autoAlpha: 0, scale: 0.6}, {autoAlpha: 1, scale: 1, duration: 0.3, ease: 'back.out(2)'}, t0 + 1.25);
    tl.to(e, {autoAlpha: 0, duration: 0.3}, t1 - 0.4);
  }
  return t1;
};

/* névkártya (2,6 mp) */
SC.nev = function (S, c, tl, t0) {
  var t1 = t0 + 2.6, J = jelenet(tl, S, t0, t1), v = c.nev, N = TX.nev || {}, e;
  vid(tl, S, 'fel', t0);
  if (v === 'vonal') { var sa = E('div', 's-alul', null, J.f); sa.style.opacity = '.85'; }
  if (v === 'tabla') e = E('div', 'nv nv-tabla', '<div><div class="nm">' + esc(N.nev) + '</div><div class="vl"></div><div class="rl">' + esc(N.szerep) + '</div></div>', J.f);
  else if (v === 'vonal') e = E('div', 'nv nv-vonal', '<div class="nm">' + esc(N.nev) + '</div><div class="vl"></div><div class="rl">' + esc(N.szerep) + '</div>', J.f);
  else e = E('div', 'nv nv-kartya', '<div class="sav"></div><div class="tx"><div class="nm">' + esc(N.nev) + '</div><div class="rl">' + esc(N.szerep) + '</div></div>', J.f);
  e.style.top = '1300px';
  belep(tl, c, e, t0 + 0.3, J.f);
  var vl = e.querySelector('.vl'); if (vl) tl.fromTo(vl, {scaleX: 0}, {scaleX: 1, duration: 0.5, ease: 'power2.out'}, t0 + 0.7);
  kilep(tl, c, e, t1 - 0.5);
  return t1;
};

/* fejezetkártya (2,2 mp) */
SC.fejezet = function (S, c, tl, t0) {
  var t1 = t0 + 2.2, J = jelenet(tl, S, t0, t1), v = c.fejezet, F = TX.fejezet || {}, e;
  if (v === 'takeover') {
    vid(tl, S, 'nativ', t0);
    var cf = illeszt(F.cim, 88, 900, 0.56);
    e = E('div', 'fj-take', '<div class="tx"></div><div class="k">Fejezet</div><div class="n">' + esc(F.szam) + '</div><div class="c" style="font-size:' + cf + 'px">' + esc(F.cim) + '</div>', J.f);
    texTo(e.firstChild);
    tl.fromTo(e, {autoAlpha: 0}, {autoAlpha: 1, duration: 0.12}, t0 + 0.3);
    tl.fromTo(e.querySelector('.n'), {y: 60, autoAlpha: 0}, {y: 0, autoAlpha: 1, duration: 0.45, ease: 'power3.out'}, t0 + 0.35);
    tl.fromTo(e.querySelector('.c'), {y: 30, autoAlpha: 0}, {y: 0, autoAlpha: 1, duration: 0.45, ease: 'power3.out'}, t0 + 0.5);
    tl.to(e, {autoAlpha: 0, duration: 0.1}, t0 + 1.5);
  } else if (v === 'szam') {
    vid(tl, S, 'fel', t0);
    E('div', 's-alul', null, J.f);
    var n = E('div', 'fj-szam', esc(F.szam), J.f); n.style.left = '-30px'; n.style.top = '1010px';
    var tc = E('div', 'fj-szc', '<small>Fejezet</small>' + esc(F.cim), J.f); tc.style.top = '1290px'; tc.style.fontSize = illeszt(F.cim, 76, 820, 0.56) + 'px';
    tl.fromTo(n, {autoAlpha: 0, x: -120}, {autoAlpha: 0.9, x: 0, duration: 0.5, ease: 'power3.out'}, t0 + 0.2);
    belep(tl, c, tc, t0 + 0.45, J.f);
    tl.to([n, tc], {autoAlpha: 0, duration: 0.3}, t1 - 0.45);
  } else {
    vid(tl, S, 'fel', t0);
    e = E('div', 'fj-pill', '<b>' + esc(F.szam) + '</b><span>' + esc(F.cim) + '</span>', J.f);
    e.style.left = '60px'; e.style.top = '250px';
    belep(tl, c, e, t0 + 0.2, J.f);
    kilep(tl, c, e, t1 - 0.5);
  }
  return t1;
};

/* zárás (3 mp) */
SC.zaro = function (S, c, tl, t0) {
  var t1 = t0 + 3.0, J = jelenet(tl, S, t0, t1), v = c.zaro, Z = TX.zaro || {}, e;
  if (v === 'cta') {
    var p = vid(tl, S, 'fel', t0); E('div', 's-alul', null, J.f);
    var C = Z.cta || {}, cf = illeszt(C.cim, 62, 1500, 0.56);
    e = E('div', 'zcta', '<div class="c" style="font-size:' + cf + 'px">' + esc(C.cim) + '</div><div class="g">' + esc(C.gomb) + '</div><div class="u">' + esc(C.link) + '</div>', J.f);
    e.style.top = '1110px';
    belep(tl, c, e, t0 + 0.2, J.f);
    tl.to(e.querySelector('.g'), {scale: 1.07, duration: 0.35, yoyo: true, repeat: 3, ease: 'sine.inOut'}, t0 + 0.8);
    kilep(tl, c, e, t1 - 0.45);
  } else if (v === 'logo') {
    vid(tl, S, 'nativ', t0);
    var sa = E('div', 's-alul', null, J.f); sa.style.top = '760px'; sa.style.height = '1160px';
    var lg = IMG.logo_feher || IMG.logo || '';
    e = E('div', 'zlogo', (lg ? '<img src="' + lg + '" alt="">' : '<div class="sz" style="font-size:80px;font-style:normal">' + esc(VD.marka.nev) + '</div>') +
      (Z.szlogen ? '<div class="sz">' + esc(Z.szlogen) + '</div>' : '') + '<div class="u">' + esc((Z.cta || {}).link || VD.marka.slug) + '</div>', J.f);
    e.style.top = '1180px';
    tl.fromTo(sa, {autoAlpha: 0}, {autoAlpha: 1, duration: 0.5}, t0 + 0.1);
    belep(tl, c, e, t0 + 0.35, J.f);
    tl.to([e, sa], {autoAlpha: 0, duration: 0.3}, t1 - 0.4);
  } else {
    vid(tl, S, 'nativ', t0);
    tl.fromTo([S.bg, S.fej], {scale: 1}, {scale: 1.07, duration: 3.0, ease: 'none'}, t0);
    var kp = E('div', 'abs kozep', '<span class="kpill">' + esc(Z.social || 'Ha hasznos volt') + '</span>', J.f); kp.style.top = Math.max(250, FT - 290) + 'px';
    e = E('div', 'zlk', '<span class="l l1">♥ Lájk</span><span class="l l2">+ Követés</span>', J.f); e.style.top = Math.max(360, FT - 180) + 'px';
    belep(tl, c, kp, t0 + 0.2, J.f);
    var ls = e.querySelectorAll('.l');
    belep(tl, c, ls[0], t0 + 0.45); belep(tl, c, ls[1], t0 + 0.6);
    tl.to(ls[0], {scale: 1.12, duration: 0.22, yoyo: true, repeat: 3, ease: 'sine.inOut'}, t0 + 1.2);
    tl.to([kp, e], {autoAlpha: 0, duration: 0.3}, t1 - 0.4);
  }
  return t1;
};

/* nyitókép (1,8 mp) */
SC.nyito = function (S, c, tl, t0) {
  var t1 = t0 + 1.8, J = jelenet(tl, S, t0, t1), v = c.nyito, N = TX.nyito || {}, so = N.sorok || ['', ''], ki = N.kiemelt != null ? N.kiemelt : 1, e;
  if (v === 'nagyszo') {
    vid(tl, S, 'nativ', t0);
    e = E('div', 'ny-sav', '<div class="w" style="font-size:' + illeszt(so[0], 132, 960, 0.56) + 'px">' + esc(so[0]) + '</div>' + (so[1] ? '<div class="s">' + esc(so[1]) + '</div>' : ''), J.f);
    e.style.top = '1190px';
  } else if (v === 'keretes') {
    vid(tl, S, 'nativ', t0);
    e = E('div', 'ny-papir', '<div class="tx"></div>', J.f); texTo(e.firstChild);
    var cim = E('div', 'ny-cim', so.map(function (s, i) { return '<span class="' + (i === ki ? 'ak' : '') + '">' + esc(s) + '</span>'; }).join('<br>'), e);
    cim.style.fontSize = Math.min(illeszt(so[0], 104, 920, 0.56), illeszt(so[1], 104, 920, 0.56)) + 'px';
    var ft = E('div', 'ny-foto', '<div></div><i>' + esc(VD.marka.nev) + '</i>', e);
    ft.firstChild.style.backgroundImage = 'url(' + IMG.bg + ')';
    ft.firstChild.style.backgroundPosition = '50% ' + Math.round(Math.max(0, Math.min(100, (FT - 120) / 1920 * 100 * 1.3))) + '%';
    if (JEL) { var j = E('div', 'ny-jel', JEL, e); j.style.left = '820px'; j.style.top = '560px'; }
  } else {
    vid(tl, S, 'nativ', t0);
    var f1 = illeszt(so[0], 100, 940, 0.66), f2 = illeszt(so[1], 100, 940, 0.66);
    e = E('div', 'mkst', '<div><span class="mk ' + (ki === 0 ? 'p' : 'f') + '" style="font-size:' + f1 + 'px">' + esc(so[0]) + '</span></div>' +
      (so[1] ? '<div><span class="mk ' + (ki === 1 ? 'p' : 'f') + '" style="font-size:' + f2 + 'px">' + esc(so[1]) + '</span></div>' : ''), J.f);
    e.style.top = '270px';
  }
  tl.fromTo([S.bg, S.fej], {scale: 1.04}, {scale: 1, duration: 1.8, ease: 'power1.out'}, t0);
  tl.to(e, {autoAlpha: 0, duration: 0.25}, t1 - 0.3);
  return t1;
};

/* hangulat: a fő jelenet hangszalaggal (4,2 mp) */
SC.hangulat = function (S, c, tl, t0) {
  var t1 = SC.fo(S, c, tl, t0), J = jelenet(tl, S, t0, t1), P = HANG.preset[c.hangulat] || HANG.preset.meleg;
  var hs = E('div', 'hsav', '<i></i><i></i><i></i><i></i><i></i><i></i><i></i>', J.f); hs.style.top = (c.stilus === 'panel' ? 1500 : 250) + 'px';
  if (c.stilus === 'kivagasos' || c.stilus === 'csakfej') hs.style.top = '1640px';
  var beat = 60 / P.bpm;
  $$('i', hs).forEach(function (b, i) {
    tl.fromTo(b, {height: 30}, {height: 60 + ((i * 37) % 80), duration: beat / 2, yoyo: true, repeat: Math.floor((t1 - t0) / beat) * 2 - 1, ease: 'sine.inOut'}, t0 + i * 0.05);
  });
  return t1;
};
['stilus', 'felirat', 'kartya', 'mozgas'].forEach(function (k) { SC[k] = SC.fo; });

/* ---------------------------------------------------------------- hangok: szintetizálva, egyforma hangerőre normálva */
var HANG = (function () {
  var preset = {
    akusztikus: {bpm: 72, hang: ['pluck', 'whoosh', 'paper', 'chime']},
    meleg: {bpm: 88, hang: ['marimba', 'swish', 'knock', 'bell']},
    modern: {bpm: 100, hang: ['pad', 'whoosh', 'pop', 'click']},
    lendulet: {bpm: 118, hang: ['beat', 'whooshhi', 'pop', 'impact']},
    filmes: {bpm: 84, hang: ['drone', 'riser', 'knock', 'boom']}
  };
  var C = window.OfflineAudioContext || window.webkitOfflineAudioContext, AC = null, cache = {};
  function ctx() { var K = window.AudioContext || window.webkitAudioContext; if (!K) return null; if (!AC) AC = new K(); if (AC.state === 'suspended') AC.resume(); return AC; }
  function zaj(a, dur) { var b = a.createBuffer(1, Math.ceil(a.sampleRate * dur), a.sampleRate), d = b.getChannelData(0); for (var i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; return b; }
  function env(g, t, a, d, csucs) { g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(csucs || 1, t + a); g.gain.exponentialRampToValueAtTime(0.0001, t + a + d); }
  function osc(a, out, tip, f, t, at, dec, csucs, f2) {
    var o = a.createOscillator(), g = a.createGain(); o.type = tip; o.frequency.setValueAtTime(f, t); if (f2) o.frequency.exponentialRampToValueAtTime(f2, t + at + dec);
    env(g, t, at, dec, csucs); o.connect(g); g.connect(out); o.start(t); o.stop(t + at + dec + 0.05);
  }
  function zajhang(a, out, t, dur, f1, f2, q, csucs, tip) {
    var s = a.createBufferSource(); s.buffer = zaj(a, dur + 0.1);
    var f = a.createBiquadFilter(); f.type = tip || 'bandpass'; f.Q.value = q || 1; f.frequency.setValueAtTime(f1, t); f.frequency.exponentialRampToValueAtTime(f2, t + dur);
    var g = a.createGain(); g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(csucs || 1, t + dur * 0.45); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    s.connect(f); f.connect(g); g.connect(out); s.start(t); s.stop(t + dur + 0.05);
  }
  var HZ = function (m) { return 440 * Math.pow(2, (m - 69) / 12); };
  var V = {
    pluck: function (a, o, t) { osc(a, o, 'triangle', HZ(64), t, 0.005, 0.5, 0.8); osc(a, o, 'sine', HZ(76), t, 0.005, 0.3, 0.25); },
    marimba: function (a, o, t) { osc(a, o, 'sine', HZ(72), t, 0.004, 0.45, 0.9); osc(a, o, 'sine', HZ(72) * 4, t, 0.002, 0.08, 0.25); },
    whoosh: function (a, o, t) { zajhang(a, o, t, 0.55, 300, 2400, 0.9, 0.9); },
    whooshhi: function (a, o, t) { zajhang(a, o, t, 0.35, 800, 5000, 1.2, 1.0); },
    swish: function (a, o, t) { zajhang(a, o, t, 0.3, 2400, 600, 1.4, 0.8); },
    riser: function (a, o, t) { zajhang(a, o, t, 1.1, 200, 4000, 2, 0.7); osc(a, o, 'sine', 220, t, 0.9, 0.2, 0.25, 880); },
    paper: function (a, o, t) { for (var i = 0; i < 5; i++) zajhang(a, o, t + i * 0.035 + Math.random() * 0.02, 0.05, 3000, 6000, 0.7, 0.5 + Math.random() * 0.4, 'highpass'); },
    knock: function (a, o, t) { osc(a, o, 'sine', 820, t, 0.002, 0.07, 0.9, 500); zajhang(a, o, t, 0.03, 2000, 1500, 2, 0.4); },
    click: function (a, o, t) { osc(a, o, 'square', 1800, t, 0.001, 0.025, 0.35, 1400); },
    pop: function (a, o, t) { osc(a, o, 'sine', 900, t, 0.004, 0.09, 0.9, 260); },
    chime: function (a, o, t) { [1, 2.76, 5.4].forEach(function (k, i) { osc(a, o, 'sine', HZ(84) * k, t, 0.004, 1.4 / (i + 1), 0.5 / (i + 1)); }); },
    bell: function (a, o, t) { [1, 2.0, 3.01].forEach(function (k, i) { osc(a, o, 'sine', HZ(79) * k, t, 0.003, 1.0 / (i + 1), 0.55 / (i + 1)); }); },
    impact: function (a, o, t) { osc(a, o, 'sine', 140, t, 0.003, 0.35, 1, 45); zajhang(a, o, t, 0.12, 900, 200, 0.8, 0.6, 'lowpass'); },
    boom: function (a, o, t) { osc(a, o, 'sine', 90, t, 0.01, 1.1, 1, 32); zajhang(a, o, t, 0.5, 400, 60, 0.7, 0.5, 'lowpass'); },
    pad: function (a, o, t, d) { [60, 64, 67, 71].forEach(function (m) { var x = a.createOscillator(), y = a.createOscillator(), f = a.createBiquadFilter(), g = a.createGain();
      x.type = y.type = 'sawtooth'; x.frequency.value = HZ(m); y.frequency.value = HZ(m) * 1.006; f.type = 'lowpass'; f.frequency.value = 1100;
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.12, t + 0.6); g.gain.setValueAtTime(0.12, t + d - 0.7); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
      x.connect(f); y.connect(f); f.connect(g); g.connect(o); x.start(t); y.start(t); x.stop(t + d); y.stop(t + d); }); },
    drone: function (a, o, t, d) { [36, 43, 48].forEach(function (m) { var x = a.createOscillator(), f = a.createBiquadFilter(), g = a.createGain(); x.type = 'sawtooth'; x.frequency.value = HZ(m);
      f.type = 'lowpass'; f.frequency.value = 500; g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.2, t + 1.2); g.gain.setValueAtTime(0.2, t + d - 0.8); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
      x.connect(f); f.connect(g); g.connect(o); x.start(t); x.stop(t + d); }); },
    beat: function (a, o, t, d, bpm) { var b = 60 / bpm; for (var i = 0; i * b < d - 0.05; i++) { var tt = t + i * b; osc(a, o, 'sine', 120, tt, 0.002, 0.22, 1, 45);
      if (i % 2) zajhang(a, o, tt, 0.12, 1600, 1200, 0.9, 0.6); osc(a, o, 'sawtooth', HZ(i % 4 < 2 ? 36 : 38), tt + b / 2, 0.005, b / 2.4, 0.25); } }
  };
  /* zenei minták: 2 ütem (t0: kezdés) */
  function zene(a, o, p, t0) {
    var b = 60 / p.bpm, d = b * 8, nev = p.hang[0], s0 = (t0 || 0) + 0.05;
    if (nev === 'pad' || nev === 'drone') V[nev](a, o, s0, d);
    if (nev === 'beat') V.beat(a, o, s0, d, p.bpm);
    if (nev === 'pluck') [64, 67, 71, 74, 72, 67, 64, 60].forEach(function (m, i) { osc(a, o, 'triangle', HZ(m), s0 + i * b, 0.005, b * 1.4, 0.6); osc(a, o, 'sine', HZ(m - 12), s0 + i * b, 0.01, b * 1.2, 0.25); });
    if (nev === 'marimba') [72, 76, 79, 76, 74, 77, 81, 77, 72, 76, 79, 84, 81, 79, 76, 72].forEach(function (m, i) { osc(a, o, 'sine', HZ(m), s0 + i * b / 2, 0.004, 0.35, 0.7); osc(a, o, 'sine', HZ(m) * 4, s0 + i * b / 2, 0.002, 0.06, 0.15); if (i % 2 === 0) zajhang(a, o, s0 + i * b / 2, 0.04, 5000, 7000, 0.7, 0.18, 'highpass'); });
    if (nev === 'pad') for (var i = 0; i < 8; i++) osc(a, o, 'square', 1500, s0 + i * b, 0.001, 0.02, 0.12, 1200);
    if (nev === 'drone') for (var j = 0; j < 4; j++) osc(a, o, 'sine', 70, s0 + j * 2 * b, 0.01, 0.6, 0.5, 40);
    return d;
  }
  /* teljes hangsáv egy minta-videóhoz: zene végig (ütemenként ismételve) + effektek; 16 bites WAV, base64 */
  function mix(pnev, dur, esem) {
    var p = preset[pnev] || preset.meleg, sr = 44100;
    if (!C) return Promise.reject('nincs OfflineAudioContext');
    var a = new C(1, Math.ceil(sr * dur), sr), z = a.createGain(), e = a.createGain(), m = a.createGain();
    z.gain.value = 0.32; e.gain.value = 0.9; z.connect(m); e.connect(m); m.connect(a.destination);
    var b8 = 60 / p.bpm * 8;
    for (var t = 0; t < dur; t += b8) zene(a, z, p, t);
    m.gain.setValueAtTime(0.0001, 0); m.gain.exponentialRampToValueAtTime(1, 1.0); m.gain.setValueAtTime(1, Math.max(1.1, dur - 1.6)); m.gain.exponentialRampToValueAtTime(0.0001, dur);
    (esem || []).forEach(function (x) { var hn = {atmenet: p.hang[1], kartya: p.hang[2], kiemeles: p.hang[3]}[x.tipus] || p.hang[1]; V[hn](a, e, x.t); });
    return a.startRendering().then(function (buf) {
      var d = buf.getChannelData(0), pk = 0, i;
      for (i = 0; i < d.length; i++) pk = Math.max(pk, Math.abs(d[i]));
      var g = 0.89 / (pk || 1), n = d.length, ab = new ArrayBuffer(44 + n * 2), v = new DataView(ab);
      function str(o, s) { for (var k = 0; k < s.length; k++) v.setUint8(o + k, s.charCodeAt(k)); }
      str(0, 'RIFF'); v.setUint32(4, 36 + n * 2, true); str(8, 'WAVEfmt '); v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
      v.setUint32(24, sr, true); v.setUint32(28, sr * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true); str(36, 'data'); v.setUint32(40, n * 2, true);
      for (i = 0; i < n; i++) { var s = Math.max(-1, Math.min(1, d[i] * g)); v.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true); }
      var bin = '', u = new Uint8Array(ab), CH = 0x8000;
      for (i = 0; i < u.length; i += CH) bin += String.fromCharCode.apply(null, u.subarray(i, i + CH));
      return btoa(bin);
    });
  }
  function render(kulcs, fn, hossz) {
    if (cache[kulcs]) return cache[kulcs];
    if (!C) return Promise.reject();
    var sr = 44100, a = new C(1, Math.ceil(sr * hossz), sr), o = a.createGain(); o.connect(a.destination);
    fn(a, o);
    cache[kulcs] = a.startRendering().then(function (buf) {
      var d = buf.getChannelData(0), s = 0, pk = 0;
      for (var i = 0; i < d.length; i++) { s += d[i] * d[i]; pk = Math.max(pk, Math.abs(d[i])); }
      var rms = Math.sqrt(s / d.length) || 1e-6, cel = 0.12, g = Math.min(cel / rms, 0.89 / (pk || 1));
      for (var j = 0; j < d.length; j++) d[j] *= g;
      return buf;
    });
    return cache[kulcs];
  }
  var aktiv = null;
  function lejatsz(buf, loop) { var a = ctx(); if (!a) return; if (aktiv) { try { aktiv.stop(); } catch (e) {} } var s = a.createBufferSource(); s.buffer = buf; s.loop = !!loop; s.connect(a.destination); s.start(); aktiv = s; return s; }
  function minta(pnev, tipus, loop) {
    var p = preset[pnev] || preset.meleg;
    if (tipus === 'zene') return render(pnev + ':zene', function (a, o) { zene(a, o, p, 0); }, 60 / p.bpm * 8 + 0.3).then(function (b) { return lejatsz(b, loop); });
    var hn = {atmenet: p.hang[1], kartya: p.hang[2], kiemeles: p.hang[3]}[tipus] || p.hang[1];
    return render(pnev + ':' + hn, function (a, o) { V[hn](a, o, 0.03); }, 1.6).then(function (b) { return lejatsz(b, false); });
  }
  function stop() { if (aktiv) { try { aktiv.stop(); } catch (e) {} aktiv = null; } }
  return {preset: preset, minta: minta, stop: stop, mix: mix};
})();

/* ---------------------------------------------------------------- állapot és mentés */
var KEY = 'vv:' + VD.marka.slug + ':v' + VD.verzio, ST = null;
try { ST = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) {}
if (!ST || !ST.val) ST = {val: {}, alt: '', jovahagyva: false};
KAT.forEach(function (k) { if (!ST.val[k.kat]) ST.val[k.kat] = {veg: null, elo: null, megj: {}, ujakat: false}; });
function kontextus(fel) {
  var c = {};
  KAT.forEach(function (k) { var v = ST.val[k.kat]; c[k.kat] = v.elo || v.veg || k.ajanlott; });
  for (var x in fel) c[x] = fel[x];
  return c;
}
var DBDOC = null, dbKesz = false, dbT = null, dbFut = false, dbUjra = false;
function jel(c, t) { var m = ROOT.querySelector('.vv-mentes'); if (m) { m.className = 'vv-mentes ' + (c || ''); m.textContent = t; } }
function ment() { try { localStorage.setItem(KEY, JSON.stringify(ST)); } catch (e) {} dbMent(); }
function dbMent() {
  if (!DBDOC || !dbKesz) return;
  clearTimeout(dbT);
  dbT = setTimeout(function () {
    if (dbFut) { dbUjra = true; return; }
    dbFut = true; jel('', 'mentés…');
    var x = exportAdat();
    DBDOC.set({allapot: JSON.stringify(ST), gepi: JSON.stringify(x.json), szoveg: x.szoveg, frissitve: new Date().toISOString(), verzio: VD.verzio, jovahagyva: ST.jovahagyva || false})
      .then(function () { dbFut = false; jel('ok', '✓ mentve a Claude-nál'); if (dbUjra) { dbUjra = false; dbMent(); } },
        function (err) { dbFut = false; jel('hiba', 'a mentés nem sikerült (' + ((err && err.code) || '?') + '), a böngésző megőrzi'); });
  }, 600);
}
function exportAdat() {
  var d = new Date(), k2 = function (n) { return (n < 10 ? '0' : '') + n; };
  var json = {marka: VD.marka.slug, fazis: 'video', verzio: VD.verzio, datum: d.getFullYear() + '-' + k2(d.getMonth() + 1) + '-' + k2(d.getDate()) + ' ' + k2(d.getHours()) + ':' + k2(d.getMinutes()),
    valasztas: {}, altalanos: ST.alt || '', jovahagyva: ST.jovahagyva || false};
  var sor = ['=== VIDEÓS ARCULAT: ' + VD.marka.nev + ' (v' + VD.verzio + ') · ' + json.datum + ' ==='];
  var kesz = KAT.filter(function (k) { return ST.val[k.kat].veg; }).length;
  sor.push('Végleges döntés: ' + kesz + ' / ' + KAT.length + ' elemnél.' + (ST.jovahagyva ? ' JÓVÁHAGYVA.' : ''), '');
  KAT.forEach(function (k, i) {
    var v = ST.val[k.kat], nv = function (id) { var o = k.valtozatok.filter(function (x) { return x.id === id; })[0]; return o ? '„' + o.nev + '” (' + id + ')' : id; };
    var f = '[' + (i + 1) + '] ' + k.nev + ' → ' + (v.veg ? 'VÉGLEGES: ' + nv(v.veg) : (v.elo ? 'nincs végleges (kipróbálva: ' + nv(v.elo) + ')' : 'nincs döntés (ajánlott: ' + nv(k.ajanlott) + ')'));
    if (v.ujakat) f += '   ⚠ ÚJ VÁLTOZATOKAT KÉR';
    sor.push(f);
    var mj = {};
    Object.keys(v.megj || {}).forEach(function (id) { var t = (v.megj[id] || '').trim(); if (t) { mj[id] = t; sor.push('    • ' + nv(id) + ': ' + t.replace(/\n+/g, ' / ')); } });
    var vk = k.valtozatok.filter(function (x) { return x.id === v.veg; })[0];
    json.valasztas[k.kat] = {vegleges: v.veg, vegleges_karakter: vk && vk.kar ? vk.kar : null, elonezet: v.elo, ajanlott: k.ajanlott, megjegyzesek: mj, ujakat: !!v.ujakat, opciok: k.valtozatok.map(function (x) { return x.id; })};
  });
  if ((ST.alt || '').trim()) sor.push('', 'Általános megjegyzés: ' + ST.alt.trim());
  sor.push('', '--- GÉPI ADAT (ezt ne töröld, ebből dolgozik tovább a Claude) ---', JSON.stringify(json));
  return {szoveg: sor.join('\n'), json: json};
}
function toast(t) { var e = ROOT.querySelector('.vv-toast'); if (!e) return; e.textContent = t; e.classList.add('on'); clearTimeout(e._t); e._t = setTimeout(function () { e.classList.remove('on'); }, 2600); }

/* ---------------------------------------------------------------- előnézetek: kicsik és a nagy */
var MINIK = [], NAGY = null, LATHATO = typeof IntersectionObserver === 'function' ? new IntersectionObserver(function (es) {
  es.forEach(function (e) { var m = e.target._mini; if (!m) return; m.lat = e.isIntersecting; if (m.lat && m.piszkos) epitMini(m); if (m.tl) { if (m.lat) m.tl.play(); else m.tl.pause(); } });
}, {rootMargin: '120px'}) : null;
function epitMini(m) {
  if (!G) return;
  if (m.tl) m.tl.kill();
  urit(m.S);
  var fel = {}; fel[m.kat] = m.id;
  var c = kontextus(fel), tl = G.timeline({paused: true, repeat: -1, repeatDelay: 0.35});
  var veg = SC[m.kat](m.S, c, tl, 0.05);
  tl.set({}, {}, veg + 0.05);
  m.tl = tl; m.piszkos = false;
  if (m.lat || !LATHATO) tl.play();
}
var SOR = ['nyito', 'hook', 'fo', 'tema', 'nev', 'fejezet', 'zaro'], SORNEV = {nyito: 'Nyitókép', hook: 'Címsor', fo: 'Stílus és kártya', tema: 'Témaválasztó', nev: 'Névkártya', fejezet: 'Fejezet', zaro: 'Záró'};
var NAGYIDO = {};
function epitNagy() {
  if (!G || !NAGY) return;
  var pos = NAGY.tl ? NAGY.tl.time() : 0;
  if (NAGY.tl) NAGY.tl.kill();
  urit(NAGY.S);
  var c = kontextus({}), tl = G.timeline({paused: true, repeat: -1, repeatDelay: 0.2}), t = 0.05;
  SOR.forEach(function (s) { NAGYIDO[s] = t; t = SC[s](NAGY.S, c, tl, t) + 0.05; if (HANGON) tl.call(hangJel, [c, s], NAGYIDO[s] + 0.12); });
  tl.set({}, {}, t);
  tl.eventCallback('onUpdate', function () { var tt = tl.time(), ak = null; SOR.forEach(function (s) { if (tt >= NAGYIDO[s]) ak = s; }); $$('.vv-jel button').forEach(function (b) { b.classList.toggle('on', b.getAttribute('data-s') === ak); }); });
  NAGY.tl = tl;
  tl.time(Math.min(pos, t - 0.1));
  tl.play();
}
var HANGON = false;
function hangJel(c, s) { if (!HANGON) return; HANG.minta(c.hangulat, s === 'fo' ? 'kartya' : (s === 'zaro' ? 'kiemeles' : 'atmenet')); }
var ujraT = null;
function ujraepit(kat) {
  clearTimeout(ujraT);
  ujraT = setTimeout(function () {
    MINIK.forEach(function (m) {
      if (m.kat === kat) return;
      var fugg = FO.indexOf(kat) >= 0 || kat === 'mozgas';
      if (!fugg) return;
      m.piszkos = true;
      if (m.lat || !LATHATO) epitMini(m);
    });
    epitNagy();
  }, 120);
}

/* ---------------------------------------------------------------- felület */
function frissit() {
  KAT.forEach(function (k) {
    var v = ST.val[k.kat], box = document.getElementById('vv-kat-' + k.kat); if (!box) return;
    $$('.vv-opt', box).forEach(function (o) {
      var id = o.getAttribute('data-id');
      o.classList.toggle('elo', v.elo === id && v.veg !== id);
      o.classList.toggle('veg', v.veg === id);
      var vb = o.querySelector('.vv-veg'); if (vb) vb.textContent = v.veg === id ? '★ Végleges' : '☆ Ez legyen';
    });
    var st = box.querySelector('header .st');
    if (st) { var o = k.valtozatok.filter(function (x) { return x.id === v.veg; })[0]; st.textContent = o ? '★ ' + o.nev : 'ajánlott: ' + ((k.valtozatok.filter(function (x) { return x.id === k.ajanlott; })[0] || {}).nev || ''); st.classList.toggle('veg', !!o); }
    var cb = box.querySelector('.vv-ujak input'); if (cb) cb.checked = !!v.ujakat;
  });
  var jg = ROOT.querySelector('#vv-jovahagy');
  if (jg) { jg.textContent = ST.jovahagyva ? '✓ A videós arculat jóvá van hagyva' : 'Jóváhagyom a videós arculatot'; jg.classList.toggle('kesz', !!ST.jovahagyva); }
}
function felulet() {
  KAT.forEach(function (k) {
    var box = document.getElementById('vv-kat-' + k.kat); if (!box) return;
    $$('.vv-opt', box).forEach(function (o) {
      var id = o.getAttribute('data-id'), mk = o.querySelector('.vv-mini');
      var S = szinpad(mk, 190, false), m = {kat: k.kat, id: id, S: S, tl: null, lat: false, piszkos: true};
      mk._mini = m; MINIK.push(m);
      if (LATHATO) LATHATO.observe(mk); else epitMini(m);
      var probal = function () { var v = ST.val[k.kat]; v.elo = id; ment(); frissit(); ujraepit(k.kat); };
      mk.addEventListener('click', probal);
      o.querySelector('.vv-prob').addEventListener('click', probal);
      o.querySelector('.vv-veg').addEventListener('click', function () { var v = ST.val[k.kat]; v.veg = v.veg === id ? null : id; v.elo = id; ment(); frissit(); ujraepit(k.kat); });
      var ta = o.querySelector('.vv-com'), mT;
      ta.value = (ST.val[k.kat].megj || {})[id] || ''; ta.classList.toggle('van', !!ta.value.trim());
      ta.addEventListener('input', function () { ST.val[k.kat].megj[id] = ta.value; ta.classList.toggle('van', !!ta.value.trim()); clearTimeout(mT); mT = setTimeout(ment, 400); });
      $$('.vv-hang button', o).forEach(function (b) { b.addEventListener('click', function (ev) { ev.stopPropagation(); HANG.minta(id, b.getAttribute('data-h')).catch(function () { toast('A böngésző nem tud hangot lejátszani.'); }); }); });
    });
    var cb = box.querySelector('.vv-ujak input');
    if (cb) cb.addEventListener('change', function () { ST.val[k.kat].ujakat = cb.checked; ment(); });
  });
  var nk = ROOT.querySelector('.vv-nagy');
  if (nk) { NAGY = {S: szinpad(nk, 360, true), tl: null}; }
  $$('.vv-jel button').forEach(function (b) { b.addEventListener('click', function () { if (NAGY && NAGY.tl) NAGY.tl.time(NAGYIDO[b.getAttribute('data-s')] || 0); }); });
  $$('.vv-kap').forEach(function (b) {
    b.addEventListener('click', function () {
      var f = b.getAttribute('data-k'); b.classList.toggle('on'); var on = b.classList.contains('on');
      if (f === 'reels') ROOT.classList.toggle('vv-reels', on);
      if (f === 'lassu' && G) G.globalTimeline.timeScale(on ? 0.4 : 1);
      if (f === 'hang') { HANGON = on; if (on) HANG.minta(kontextus({}).hangulat, 'zene', true).catch(function () {}); else HANG.stop(); epitNagy(); }
    });
  });
  var aj = ROOT.querySelector('#vv-ajanlott');
  if (aj) aj.addEventListener('click', function () {
    var n = 0;
    KAT.forEach(function (k) { var v = ST.val[k.kat]; if (!v.veg) { v.veg = k.ajanlott; n++; } });
    ment(); frissit(); FO.concat(['tema', 'nev', 'fejezet', 'zaro', 'nyito']).forEach(function (k) { ujraepit(k); });
    toast(n ? n + ' elemnél elfogadtad az ajánlottat. Ha kész, hagyd jóvá lent.' : 'Már mindenhol van végleges.');
  });
  var alt = ROOT.querySelector('#vv-altalanos'), aT;
  if (alt) { alt.value = ST.alt || ''; alt.addEventListener('input', function () { ST.alt = alt.value; clearTimeout(aT); aT = setTimeout(ment, 400); }); }
  var modal = ROOT.querySelector('.vv-modal'), mt = modal && modal.querySelector('textarea');
  $$('.vv-export').forEach(function (b) { b.addEventListener('click', function () { mt.value = exportAdat().szoveg; modal.classList.add('on'); }); });
  if (modal) modal.addEventListener('click', function (e) { if (e.target === modal || e.target.closest('[data-bezar]')) modal.classList.remove('on'); });
  var mg = ROOT.querySelector('#vv-masol');
  if (mg) mg.addEventListener('click', function () {
    var ok = function () { toast('Kimásolva. Illeszd be a Claude-os beszélgetésbe.'); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(mt.value).then(ok, function () { mt.select(); document.execCommand('copy'); ok(); });
    else { mt.select(); document.execCommand('copy'); ok(); }
  });
  var jg = ROOT.querySelector('#vv-jovahagy'), elso = false, jt;
  if (jg) jg.addEventListener('click', function () {
    if (ST.jovahagyva) { toast('Már jóvá van hagyva. Ha módosítanál, írd meg a megjegyzésekben.'); return; }
    if (!elso) { elso = true; jg.textContent = 'Biztosan? Kattints még egyszer a jóváhagyáshoz'; jg.classList.add('meg');
      jt = setTimeout(function () { elso = false; jg.classList.remove('meg'); frissit(); }, 4500); return; }
    clearTimeout(jt); elso = false; jg.classList.remove('meg');
    KAT.forEach(function (k) { var v = ST.val[k.kat]; if (!v.veg) v.veg = v.elo || k.ajanlott; });
    ST.jovahagyva = new Date().toISOString(); ment(); frissit();
    if (window.HUB && window.HUB.fazis) window.HUB.fazis('video', 'jovahagyva');
    toast('Jóváhagyva. Szólj a Claude-nak: „kész a videós arculat”.');
  });
  frissit();
  epitNagy();
}

/* képkészítő mód: ?kep=<kat>:<változat>@<mp>[&val=kat:id,kat:id] -> egy teljes méretű színpad, megállítva (headless képernyőképhez) */
function kepMod(spec) {
  var m = spec.match(/^(\w+):(\w+)@([\d.]+)$/); if (!m || !G) return false;
  var fel = {}, vq = (location.search.match(/[?&]val=([^&]+)/) || [])[1];
  if (vq) decodeURIComponent(vq).split(',').forEach(function (x) { var p = x.split(':'); if (p[1]) fel[p[0]] = p[1]; });
  fel[m[1]] = m[2];
  var c = kontextus(fel), in_ = ROOT.querySelector('.vv-in'); if (in_) in_.style.display = 'none';
  document.documentElement.style.margin = '0'; document.body.style.margin = '0'; ROOT.style.minHeight = '0'; ROOT.style.background = 'transparent';
  var kont = E('div', null, null, ROOT); kont.style.cssText = 'position:fixed;left:0;top:0;width:1080px;height:1920px;z-index:99999';
  var S = szinpad(kont, 1080, false); S.ph.style.cssText = 'padding:0;border-radius:0;background:none;box-shadow:none'; S.ph.firstChild.style.borderRadius = '0';
  if (/[?&]reels=1/.test(location.search)) ROOT.classList.add('vv-reels');
  var tl = G.timeline({paused: true}), kat = m[1] === 'osszeallitas' ? null : m[1], esem = [];
  if (kat) { SC[kat](S, c, tl, 0.05); }
  else { var t = 0.05; SOR.forEach(function (s) { esem.push({t: t + 0.12, tipus: s === 'zaro' ? 'kiemeles' : 'atmenet', jelenet: s}); if (s === 'fo') esem.push({t: t + 1.9, tipus: 'kartya'}); t = SC[s](S, c, tl, t) + 0.05; }); tl.set({}, {}, t); }
  tl.time(parseFloat(m[3]));
  window.__vv = {seek: function (x) { tl.time(x); return tl.time(); }, hossz: tl.duration(), esemenyek: esem, hangulat: c.hangulat,
    hang: function (dur) { return HANG.mix(c.hangulat, dur || tl.duration(), esem); }};
  document.documentElement.setAttribute('data-kesz', '1');
  return true;
}
var indult = false;
function indit() {
  if (indult) return; indult = true;
  var q = (location.search || '').match(/[?&]kep=([^&]+)/);
  if (q && kepMod(decodeURIComponent(q[1]))) return;
  if (!G) {
    var f = ROOT.querySelector('.vv-figy-gsap'); if (f) f.style.display = 'block';
  }
  felulet();
}
if (document.fonts && document.fonts.ready) document.fonts.ready.then(indit); else indit();
setTimeout(indit, 1500);

window.FAZISOK = window.FAZISOK || {};
window.FAZISOK.video = {init: function (db) {
  if (!db) { jel('', 'mentés a böngészőben (a „Visszajelzés másolása” gombbal küldd el)'); return; }
  try { DBDOC = db.doc('arculat/video-v' + VD.verzio); } catch (e) { return; }
  jel('', 'kapcsolódás…');
  DBDOC.get().then(function (snap) {
    var d = snap.exists ? snap.data() : null;
    if (d && d.allapot) { try { var r = JSON.parse(d.allapot); if (r && r.val) { ST = r; KAT.forEach(function (k) { if (!ST.val[k.kat]) ST.val[k.kat] = {veg: null, elo: null, megj: {}, ujakat: false}; });
      $$('.vv-opt').forEach(function (o) { var kk = o.closest('.vv-kat').getAttribute('data-kat'), id = o.getAttribute('data-id'), ta = o.querySelector('.vv-com'); ta.value = (ST.val[kk].megj || {})[id] || ''; ta.classList.toggle('van', !!ta.value.trim()); });
      var alt = ROOT.querySelector('#vv-altalanos'); if (alt) alt.value = ST.alt || '';
      frissit(); MINIK.forEach(function (m) { m.piszkos = true; if (m.lat) epitMini(m); }); epitNagy(); } } catch (e) {} }
    dbKesz = true; jel('ok', '✓ mentés a Claude-nál bekapcsolva');
    if (!d) dbMent();
  }, function () { jel('hiba', 'az adatbázis nem elérhető (marad a böngésző)'); });
}};
})();
