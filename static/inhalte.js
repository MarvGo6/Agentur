/* Inhalte-Formular für Kunden (/inhalte/?t=…): Angaben zwischenspeichern, Fotos hochladen, am Ende abschicken.
   Spricht mit der Supabase-Funktion "inhalte"; der Link (Token) ist nur für diesen Kunden gültig. */
(function () {
  'use strict';
  var f = document.getElementById('inhalte'); if (!f) return;
  var SB = document.documentElement.getAttribute('data-sb'), KEY = document.documentElement.getAttribute('data-key');
  var t = new URLSearchParams(location.search).get('t') || '', FN = SB + '/functions/v1/inhalte?t=' + encodeURIComponent(t);
  var info = document.getElementById('in-info'), liste = document.getElementById('in-dateien'), status = document.getElementById('in-status');
  function setze(text, fehler) { status.textContent = text; status.className = fehler ? 'in-msg' : 'in-ok'; }
  function daten() { var d = {}; new FormData(f).forEach(function (v, k) { if (typeof v === 'string') d[k] = v; }); return d; }
  function zeigeDateien(n) { liste.innerHTML = n.length ? n.map(function (x) { return '<li>' + x.replace(/[<>&]/g, '') + '</li>'; }).join('') : '<li class="in-muted">Noch keine Dateien.</li>'; }

  if (!t) { info.textContent = 'Dieser Link ist unvollständig. Bitte nutzen Sie den Link aus unserer E-Mail.'; f.hidden = true; return; }
  fetch(FN, { headers: { apikey: KEY } }).then(function (r) { return r.json(); }).then(function (j) {
    if (j.fehler) { info.textContent = j.fehler; f.hidden = true; return; }
    info.innerHTML = 'Für: <b>' + String(j.titel || '').replace(/[<>&]/g, '') + '</b> · bitte bis <b>' + new Date(j.frist).toLocaleDateString('de-DE') + '</b>' + (j.eingereicht ? ' · <span class="in-ok">bereits abgeschickt – Änderungen sind weiter möglich</span>' : '');
    Object.keys(j.daten || {}).forEach(function (k) { if (f.elements[k] && f.elements[k].type !== 'file') f.elements[k].value = j.daten[k]; });
    zeigeDateien(j.dateien || []); f.hidden = false;
  }).catch(function () { info.textContent = 'Das Formular konnte nicht geladen werden. Bitte später erneut versuchen.'; });

  function speichern(fertig) {
    return fetch(FN + '&aktion=speichern', { method: 'POST', headers: { apikey: KEY, 'Content-Type': 'application/json' }, body: JSON.stringify({ daten: daten(), fertig: fertig }) })
      .then(function (r) { if (!r.ok) throw new Error(); });
  }
  var timer; f.addEventListener('input', function (e) { if (e.target.type === 'file') return; clearTimeout(timer); timer = setTimeout(function () { speichern(false).then(function () { setze('Zwischengespeichert ' + new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })); }).catch(function () {}); }, 1500); });

  document.getElementById('in-upload').addEventListener('change', async function (e) {
    var files = [].slice.call(e.target.files || []), n = 0;
    for (var i = 0; i < files.length; i++) {
      var d = files[i];
      if (d.size > 15 * 1024 * 1024) { setze(d.name + ' ist größer als 15 MB und wurde übersprungen.', true); continue; }
      setze('Lade hoch: ' + d.name + ' (' + (i + 1) + '/' + files.length + ') …');
      try {
        var r = await fetch(FN + '&aktion=upload', { method: 'POST', headers: { apikey: KEY, 'Content-Type': 'application/json' }, body: JSON.stringify({ name: d.name, typ: d.type }) });
        var j = await r.json(); if (!r.ok) throw new Error(j.fehler);
        var fd = new FormData(); fd.append('cacheControl', '3600'); fd.append('', d);
        var up = await fetch(j.upload, { method: 'PUT', headers: { apikey: KEY, 'x-upsert': 'false' }, body: fd });
        if (!up.ok) throw new Error('Upload fehlgeschlagen');
        n++; liste.insertAdjacentHTML('beforeend', '<li>' + d.name.replace(/[<>&]/g, '') + ' ✓</li>');
      } catch (err) { setze((err && err.message) || ('Fehler bei ' + d.name), true); }
    }
    e.target.value = ''; if (n) setze(n + ' Datei(en) hochgeladen.');
  });

  f.addEventListener('submit', function (e) {
    e.preventDefault(); if (!f.reportValidity()) return;
    speichern(true).then(function () { setze('Vielen Dank! Ihre Angaben sind bei uns angekommen. Wir melden uns innerhalb von zwei Werktagen.'); window.scrollTo(0, 0); })
      .catch(function () { setze('Senden fehlgeschlagen – bitte erneut versuchen.', true); });
  });
})();
