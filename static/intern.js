/* Lotwerk Steuerzentrale (/intern/) – nur für Admins. Spricht direkt mit Supabase (Auth + REST); der Zugriff ist über
   Row Level Security geschützt (nur Konten in der Tabelle "admins"). Rechnungen/Zahlungen folgen später (Lexware, GoCardless). */
(function () {
  'use strict';
  var H = document.documentElement, SB = H.getAttribute('data-sb'), KEY = H.getAttribute('data-key'), app = document.getElementById('app');
  if (!app || !SB) return;
  var S = {}, tab = 'cockpit', CACHE = {}, ZURUECK = location.origin + '/intern/';
  var PRODUKTE = {  // Vorgaben je Produkt: einmalig, monatlich, Mindestlaufzeit, Verlängerung, Kündigungsfrist (Monate)
    web_start: ['Website Start', 1790, 0, 0, 0, 0], web_wachstum: ['Website Wachstum', 3490, 0, 0, 0, 0],
    pflege_start: ['Pflege Start', 0, 59, 12, 12, 3], pflege_wachstum: ['Pflege Wachstum', 0, 99, 12, 12, 3],
    seo_lokal: ['SEO Lokal', 0, 490, 6, 0, 1], seo_plus: ['SEO Plus', 0, 890, 6, 0, 1], ads: ['Google Ads', 490, 290, 0, 0, 0],
    programm: ['Wachstumsprogramm', 1490, 1390, 12, 0, 3], recruiting: ['Recruiting Komplett', 1490, 790, 1, 0, 1],
    recruiting_basis: ['Recruiting Basis', 990, 490, 1, 0, 1, 'recruiting']  // 7. Wert: Produkt in der Datenbank
  };
  var BESCHR = {  // Kurzbeschreibung je Produkt für das Vertragsdokument (wie auf der Website)
    web_start: 'Website mit bis zu 5 Seiten, Texte und Struktur, Google-Unternehmensprofil eingerichtet, Kontakt- oder Buchungsformular.',
    web_wachstum: 'Website mit bis zu 15 Seiten: eigene Seiten je Leistung und Ort, Karriere- oder Bewerbungsbereich, Ratgeber-Bereich, Anruf- und Formularmessung.',
    pflege_start: 'Hosting, Updates, Sicherheit, Datensicherung und kleine Änderungen.',
    pflege_wachstum: 'Wie Pflege Start, zusätzlich 1 Stunde Änderungen pro Monat.',
    seo_lokal: 'Google-Profil, Verzeichnisse, Technik, 1 neue Seite oder Erweiterung pro Monat, monatliches Reporting.',
    seo_plus: 'Wie SEO Lokal, zusätzlich 2–3 Inhalte pro Monat und Bewertungsablauf.',
    ads: 'Einrichtung und Betreuung der Google-Ads-Kampagnen inkl. Zielseite und Messung, monatlicher Bericht. Werbebudget zahlt der Kunde direkt an Google.',
    programm: 'Website Wachstum, Pflege, SEO Plus und Google-Ads-Betreuung mit gemeinsamem Ziel und Monatsbericht. Werbebudget separat.',
    recruiting: 'Karriereseiten für mehrere Stellen, Kurzbewerbung, Anzeigen auf Instagram, Facebook und Google, wöchentliche Optimierung, Stellenwechsel für 30 % der Einrichtung. Werbebudget separat.',
    recruiting_basis: 'Karriereseite für 1 Stelle, Kurzbewerbung, Anzeigen auf Instagram und Facebook, monatliche Anpassung. Werbebudget separat.'
  };
  function laufzeit(p) {
    if (!p[2]) return 'einmalige Leistung';
    if (!p[3]) return 'monatlich kündbar';
    return p[3] + (p[3] === 1 ? ' Monat' : ' Monate') + ' Mindestlaufzeit, ' + (p[4] ? 'danach Verlängerung um je ' + p[4] + ' Monate, ' : 'danach monatlich kündbar, ') + 'Kündigungsfrist ' + p[5] + (p[5] === 1 ? ' Monat' : ' Monate') + (p[4] ? ' zum Laufzeitende' : '');
  }
  function vertragHtml(k, keys, start, extra) {
    var A = {}; try { A = JSON.parse(app.dataset.anbieter || '{}'); } catch (e) {}
    var ein = 0, mon = 0;
    var zeilen = keys.map(function (key) { var p = PRODUKTE[key]; ein += p[1]; mon += p[2];
      return '<tr><td><b>' + x(p[0]) + '</b><br><span class=m>' + x(BESCHR[key] || '') + '</span><br><span class=m>Laufzeit: ' + x(laufzeit(p)) + '</span></td><td class=r>' + (p[1] ? eur(p[1]) : '–') + '</td><td class=r>' + (p[2] ? eur(p[2]) : '–') + '</td></tr>'; }).join('');
    var css = 'body{font:11pt/1.5 Arial,sans-serif;color:#111;max-width:760px;margin:30px auto;padding:0 24px}h1{font-size:18pt;margin:0 0 4px}h2{font-size:12pt;margin:22px 0 6px}.m{color:#555;font-size:9.5pt}table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid #ccc;padding:7px 6px;vertical-align:top;text-align:left}.r{text-align:right;white-space:nowrap}.parteien{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:16px 0}.box{border:1px solid #ccc;padding:10px 12px}.hinweis{background:#fff4e5;border:1px solid #f0b46a;padding:8px 12px;font-size:9.5pt;margin:12px 0}.sig{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-top:48px}.sig div{border-top:1px solid #111;padding-top:6px;font-size:9.5pt}@media print{.hinweis{break-inside:avoid}}';
    return '<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Auftrag ' + x(k.firma) + '</title><style>' + css + '</style></head><body>' +
      '<div class="hinweis">Entwurf aus der Steuerzentrale. Vor dem ersten Einsatz anwaltlich prüfen lassen (zusammen mit den AGB). Platzhalter in eckigen Klammern ausfüllen.</div>' +
      '<h1>Auftrag über Leistungen</h1><p class=m>Datum: ' + new Date().toLocaleDateString('de-DE') + ' · Leistungsbeginn: ' + datum(start) + '</p>' +
      '<div class="parteien"><div class="box"><b>Auftragnehmer</b><br>' + x(A.name || 'Lotwerk') + '<br>' + x(A.inhaber || '') + '<br>' + x(A.strasse || '') + '<br>' + x(A.ort || '') + '<br>' + x(A.email || '') + '</div>' +
      '<div class="box"><b>Auftraggeber</b><br>' + x(k.firma) + '<br>' + x(k.ansprechpartner || '[Ansprechpartner]') + '<br>[Straße Hausnummer]<br>[PLZ Ort]<br>' + x(k.email || '[E-Mail]') + (k.telefon ? '<br>' + x(k.telefon) : '') + '</div></div>' +
      '<h2>1. Leistungen</h2><table><tr><th>Leistung</th><th class=r>einmalig</th><th class=r>monatlich</th></tr>' + zeilen +
      '<tr><td><b>Summe</b></td><td class=r><b>' + eur(ein) + '</b></td><td class=r><b>' + eur(mon) + '</b></td></tr></table><p class=m>' + x(A.ust || '') + '</p>' +
      '<h2>2. Zahlung</h2><p>Einmalige Leistungen: 50 % bei Auftrag, 50 % nach Freigabe des Entwurfs durch den Auftraggeber. Monatliche Leistungen: [PRÜFEN: Abrechnungsweise, z. B. monatlich im Voraus per SEPA-Lastschrift]. Rechnungen sind innerhalb von 14 Tagen ohne Abzug fällig [PRÜFEN]. Werbebudgets für Google oder Meta zahlt der Auftraggeber direkt an die Plattform.</p>' +
      '<h2>3. Laufzeit und Kündigung</h2><p>Die Laufzeit gilt je Leistung wie in Abschnitt 1 angegeben und beginnt mit dem Leistungsbeginn. Kündigungen bedürfen der Textform (z. B. E-Mail).</p>' +
      '<h2>4. Mitwirkung</h2><p>Der Auftraggeber stellt Inhalte, Fotos und Zugänge innerhalb von 7 Tagen nach Auftrag bereit (Inhalte-Formular) und benennt eine Person für Freigaben. Verzögerungen verschieben den Zeitplan entsprechend.</p>' +
      '<h2>5. Nutzungsrechte</h2><p>Nach vollständiger Zahlung erhält der Auftraggeber die zeitlich und räumlich unbeschränkten Nutzungsrechte an Website, Texten und Gestaltung. Domain und Inhalte gehören dem Auftraggeber. Bei Vertragsende werden alle Dateien übergeben.</p>' +
      '<h2>6. Datenschutz</h2><p>Soweit der Auftragnehmer personenbezogene Daten im Auftrag verarbeitet (z. B. Formularanfragen, Bewerbungen), schließen die Parteien einen Vertrag zur Auftragsverarbeitung nach Art. 28 DSGVO als Anlage zu diesem Auftrag. [PRÜFEN: Vorlage AV-Vertrag]</p>' +
      '<h2>7. Allgemeine Geschäftsbedingungen</h2><p>Ergänzend gelten die AGB des Auftragnehmers in der bei Auftrag gültigen Fassung (' + x(location.origin) + '/agb/).</p>' +
      (extra ? '<h2>8. Besondere Vereinbarungen</h2><p>' + x(extra).replace(/\n/g, '<br>') + '</p>' : '') +
      '<div class="sig"><div>Ort, Datum, Unterschrift Auftraggeber</div><div>Ort, Datum, Unterschrift Auftragnehmer</div></div></body></html>';
  }
  var STATUS = ['neu', 'vorschau', 'kontaktiert', 'termin', 'angebot', 'gewonnen', 'verloren', 'pausiert'];
  var TAET = ['vertrieb', 'umsetzung', 'pflege', 'seo', 'ads', 'recruiting', 'verwaltung'];

  function x(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function eur(v) { return Math.round(Number(v) || 0).toLocaleString('de-DE') + ' €'; }
  function datum(d) { return d ? new Date(d).toLocaleDateString('de-DE') : '–'; }
  function heute() { return new Date().toISOString().slice(0, 10); }
  function monatsanfang() { var d = new Date(); return new Date(Date.UTC(d.getFullYear(), d.getMonth(), 1)).toISOString(); }

  // ------------------------------------------------------------ Anmeldung (Supabase Auth, ohne Bibliothek)
  function lade() { try { S = JSON.parse(localStorage.getItem('lw-sitzung') || '{}'); } catch (e) { S = {}; } }
  function sichere() { try { localStorage.setItem('lw-sitzung', JSON.stringify(S)); } catch (e) {} }
  function setze(j) { S = { access: j.access_token, refresh: j.refresh_token, ablauf: Date.now() + j.expires_in * 1000, email: j.user && j.user.email }; sichere(); }
  async function auth(pfad, body) {
    var r = await fetch(SB + '/auth/v1/' + pfad, { method: 'POST', headers: { apikey: KEY, 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    var j = await r.json().catch(function () { return {}; });
    if (!r.ok) throw new Error(j.error_description || j.msg || j.message || ('Fehler ' + r.status));
    return j;
  }
  async function token() {
    if (S.access && S.ablauf > Date.now() + 60000) return S.access;
    if (S.refresh) { setze(await auth('token?grant_type=refresh_token', { refresh_token: S.refresh })); return S.access; }
    throw new Error('abgemeldet');
  }
  async function api(pfad, opt) {
    opt = opt || {};
    var h = { apikey: KEY, Authorization: 'Bearer ' + await token(), 'Content-Type': 'application/json' };
    if (opt.prefer) h.Prefer = opt.prefer;
    var r = await fetch(SB + '/rest/v1/' + pfad, { method: opt.method || 'GET', headers: h, body: opt.body ? JSON.stringify(opt.body) : undefined });
    var t = await r.text();
    if (!r.ok) throw new Error(t.slice(0, 240));
    return t ? JSON.parse(t) : null;
  }
  var neu = function (tabelle, daten) { return api(tabelle, { method: 'POST', body: daten, prefer: 'return=representation' }); };
  var aendere = function (tabelle, id, daten) { return api(tabelle + '?id=eq.' + id, { method: 'PATCH', body: daten, prefer: 'return=minimal' }); };

  function anmeldung(hinweis) {
    app.innerHTML = '<div class="in-login"><h1>Steuerzentrale</h1><p class="in-muted">Nur für den Inhaber. Erstes Mal? „Konto anlegen“, E-Mail bestätigen, dann anmelden.</p>' +
      (hinweis ? '<p class="in-msg">' + x(hinweis) + '</p>' : '') +
      '<form id="in-login"><label>E-Mail<input name="email" type="email" autocomplete="username" required></label>' +
      '<label>Passwort<input name="pw" type="password" autocomplete="current-password" minlength="10" required></label>' +
      '<div class="in-row"><button class="btn" data-a="login">Anmelden</button><button class="btn ghost" data-a="signup">Konto anlegen</button>' +
      '<button class="in-link" data-a="reset" type="button">Passwort vergessen</button></div></form></div>';
  }
  app.addEventListener('submit', function (ev) { if (ev.target.id === 'in-login') ev.preventDefault(); });

  // ------------------------------------------------------------ Ansichten
  var TABS = [['cockpit', 'Cockpit'], ['aufgaben', 'Aufgaben'], ['freigaben', 'Freigaben'], ['pipeline', 'Pipeline'], ['kunden', 'Kunden'],
    ['websites', 'Websites'], ['zeiten', 'Zeiten'], ['anfragen', 'Anfragen'], ['berichte', 'Berichte'], ['links', 'Links']];

  async function zeige(t) {
    tab = t || tab;
    try { location.hash = tab; } catch (e) {}
    app.innerHTML = '<div class="in-head"><nav class="in-tabs">' + TABS.map(function (a) { return '<button data-tab="' + a[0] + '"' + (a[0] === tab ? ' aria-current="page"' : '') + '>' + a[1] + '</button>'; }).join('') +
      '</nav><button class="in-link" data-a="logout">Abmelden</button></div><div id="in-view" class="in-view"><p class="in-muted">Lädt …</p></div>';
    var v = document.getElementById('in-view');
    try { v.innerHTML = await ANSICHT[tab](); }
    catch (e) { if (/abgemeldet|JWT|401/.test(e.message)) { S = {}; sichere(); return anmeldung('Bitte erneut anmelden.'); } v.innerHTML = '<p class="in-msg">Fehler: ' + x(e.message) + '</p>'; }
  }

  function kachel(wert, text) { return '<div class="in-k"><b>' + wert + '</b><span>' + text + '</span></div>'; }
  function zaehl(a, f) { var m = {}; a.forEach(function (o) { m[o[f]] = (m[o[f]] || 0) + 1; }); return m; }

  var ANSICHT = {
    // Wichtige Links (Rechtstexte für Kunden, AV-Verträge, Gesetze, eigene Werkzeuge) – Tabelle "links", archivieren statt löschen
    links: async function () {
      var l = await api('links?select=id,kategorie,titel,url,notiz,kosten&archiviert=eq.false&order=kategorie,titel');
      var kat = []; l.forEach(function (a) { if (kat.indexOf(a.kategorie) < 0) kat.push(a.kategorie); });
      return '<form class="in-form in-inline" data-form="link"><input name="titel" placeholder="Titel" required><input name="url" type="url" placeholder="https://…" pattern="https://.*" required>' +
        '<input name="kategorie" list="in-kat" placeholder="Kategorie" required><datalist id="in-kat">' + kat.map(function (k) { return '<option value="' + x(k) + '">'; }).join('') + '</datalist>' +
        '<input name="notiz" placeholder="Notiz (optional)"><button class="btn">Speichern</button></form>' +
        (kat.length ? kat.map(function (k) {
          return '<h2>' + x(k) + '</h2><ul class="in-list">' + l.filter(function (a) { return a.kategorie === k; }).map(function (a) {
            return '<li><a href="' + x(a.url) + '" target="_blank" rel="noopener noreferrer"><b>' + x(a.titel) + '</b></a>' + (a.kosten ? ' <span class="in-muted">· ' + x(a.kosten) + '</span>' : '') +
              (a.notiz ? '<br><span class="in-muted">' + x(a.notiz) + '</span>' : '') + ' <button class="in-link" data-a="link-weg" data-id="' + a.id + '">archivieren</button></li>';
          }).join('') + '</ul>';
        }).join('') : '<p class="in-muted">Noch keine Links.</p>');
    },

    cockpit: async function () {
      var w7 = new Date(Date.now() - 7 * 864e5).toISOString(), mon = monatsanfang();
      var r = await Promise.all([api('mrr_aktuell?select=mrr,kunden'), api('aufgaben?select=id&erledigt_am=is.null'), api('entwuerfe?select=id&status=eq.offen'),
        api('kundenberichte?select=id&status=eq.entwurf'), api('agentur_anfragen?select=id&created_at=gte.' + w7), api('interessenten?select=status,potenzial'),
        api('ki_laeufe?select=kosten_eur&zeit=gte.' + mon), api('zeiten?select=minuten&start=gte.' + mon), api('websites?select=id&status=eq.live'),
        api('aufgaben?select=titel,prioritaet&erledigt_am=is.null&order=prioritaet,angelegt&limit=5')]);
      var mrr = Number((r[0][0] || {}).mrr || 0), p = zaehl(r[5], 'status'), ki = r[6].reduce(function (s, a) { return s + Number(a.kosten_eur || 0); }, 0);
      var std = r[7].reduce(function (s, a) { return s + (a.minuten || 0); }, 0) / 60;
      return '<div class="in-grid">' + kachel(eur(mrr), 'MRR · ' + ((r[0][0] || {}).kunden || 0) + ' Kunden') + kachel(Math.round(mrr / 100) + ' %', 'Ziel 10.000 € MRR') +
        kachel(r[1].length, 'offene Aufgaben') + kachel(r[2].length + r[3].length, 'warten auf Freigabe') + kachel(r[4].length, 'Anfragen (7 Tage)') +
        kachel(r[5].filter(function (i) { return i.status === 'neu' && (i.potenzial || 0) >= 60; }).length, 'starke Interessenten offen') +
        kachel(r[8].length, 'Websites live') + kachel(std.toFixed(1) + ' h', 'erfasste Zeit diesen Monat') + kachel(ki.toFixed(2) + ' €', 'KI-Kosten diesen Monat') + '</div>' +
        '<div class="in-bar"><i style="width:' + Math.min(100, mrr / 100) + '%"></i></div>' +
        '<h2>Pipeline</h2><p>' + STATUS.map(function (s) { return s + ': <b>' + (p[s] || 0) + '</b>'; }).join(' · ') + '</p>' +
        '<h2>Wichtigste Aufgaben</h2>' + (r[9].length ? '<ul class="in-list">' + r[9].map(function (a) { return '<li><span class="in-p' + a.prioritaet + '">P' + a.prioritaet + '</span> ' + x(a.titel) + '</li>'; }).join('') + '</ul>' : '<p class="in-muted">Nichts offen.</p>');
    },

    aufgaben: async function () {
      var a = await api('aufgaben?select=id,titel,prioritaet,faellig,quelle,angelegt&erledigt_am=is.null&order=prioritaet,faellig.nullslast,angelegt');
      return '<form class="in-form in-inline" data-form="aufgabe"><input name="titel" placeholder="Neue Aufgabe" required><input name="faellig" type="date"><select name="prioritaet"><option value="1">P1</option><option value="2" selected>P2</option><option value="3">P3</option></select><button class="btn">Anlegen</button></form>' +
        (a.length ? '<ul class="in-list">' + a.map(function (t) {
          return '<li><span class="in-p' + t.prioritaet + '">P' + t.prioritaet + '</span> ' + x(t.titel) + ' <span class="in-muted">· ' + x(t.quelle) + (t.faellig ? ' · fällig ' + datum(t.faellig) : '') +
            '</span> <button class="in-link" data-a="erledigt" data-id="' + t.id + '">erledigt</button></li>';
        }).join('') + '</ul>' : '<p class="in-muted">Keine offenen Aufgaben.</p>');
    },

    freigaben: async function () {
      var r = await Promise.all([api('entwuerfe?select=id,art,titel,text,angelegt&status=eq.offen&order=angelegt.desc'),
        api('kundenberichte?select=id,monat,text,websites(domain)&status=eq.entwurf&order=monat.desc')]);
      var e = r[0].map(function (d) {
        return '<article class="in-card"><p class="in-muted">' + x(d.art) + ' · ' + datum(d.angelegt) + '</p><h3>' + x(d.titel || d.art) + '</h3><textarea rows="7" id="t-' + d.id + '">' + x(d.text) + '</textarea>' +
          '<div class="in-row"><button class="btn" data-a="freigeben" data-t="entwuerfe" data-id="' + d.id + '">Freigeben</button><button class="btn ghost" data-a="kopieren" data-id="' + d.id + '">Kopieren</button><button class="in-link" data-a="verwerfen" data-id="' + d.id + '">Verwerfen</button></div></article>';
      }).join('');
      var k = r[1].map(function (d) {
        return '<article class="in-card"><p class="in-muted">Monatsbericht ' + datum(d.monat) + '</p><h3>' + x(d.websites && d.websites.domain) + '</h3><textarea rows="9" id="t-' + d.id + '">' + x(d.text) + '</textarea>' +
          '<div class="in-row"><button class="btn" data-a="freigeben" data-t="kundenberichte" data-id="' + d.id + '">Freigeben</button><button class="btn ghost" data-a="kopieren" data-id="' + d.id + '">Kopieren</button></div></article>';
      }).join('');
      return (e || k) ? e + k : '<p class="in-muted">Nichts zu prüfen. Entwürfe (Nachrichten, Berichte, Beiträge) erscheinen hier, sobald die KI sie vorbereitet hat.</p>';
    },

    pipeline: async function () {
      var f = CACHE.filter || 'offen';
      var q = f === 'offen' ? '&status=not.in.(gewonnen,verloren)' : f === 'alle' ? '' : '&status=eq.' + f;
      var a = await api('interessenten?select=id,name,branche,ort,website_alt,telefon,potenzial,status,befund,nachricht_entwurf,naechster_schritt,vorschau_url,bewertung,bewertungen_anzahl&order=potenzial.desc.nullslast&limit=150' + q);
      return '<form class="in-form in-inline" data-form="interessent"><input name="name" placeholder="Betrieb" required><input name="branche" placeholder="Branche"><input name="ort" placeholder="Ort"><input name="website_alt" placeholder="Website (optional)"><button class="btn">Hinzufügen</button></form>' +
        '<p class="in-muted">Mit Website wird der Betrieb innerhalb von 30 Minuten automatisch analysiert. Filter: ' +
        ['offen', 'alle'].concat(STATUS).map(function (s) { return '<button class="in-link' + (s === f ? ' on' : '') + '" data-a="filter" data-f="' + s + '">' + s + '</button>'; }).join(' ') + '</p>' +
        a.map(function (i) {
          var bef = (i.befund && i.befund.befund) || [];
          return '<article class="in-card"><div class="in-row in-between"><h3>' + x(i.name) + ' <span class="in-muted">' + x(i.branche || '') + ' · ' + x(i.ort || '') + '</span></h3><b class="in-pot">' + (i.potenzial == null ? '–' : i.potenzial) + '</b></div>' +
            '<p class="in-muted">' + (i.website_alt ? '<a href="' + x(i.website_alt) + '" target="_blank" rel="noopener">' + x(i.website_alt) + '</a>' : 'keine Website') + (i.telefon ? ' · <a href="tel:' + x(i.telefon) + '">' + x(i.telefon) + '</a>' : '') +
            (i.bewertung ? ' · ★ ' + i.bewertung + ' (' + (i.bewertungen_anzahl || 0) + ')' : '') + (i.vorschau_url ? ' · <a href="' + x(i.vorschau_url) + '" target="_blank" rel="noopener">Vorschau</a>' : '') + '</p>' +
            (bef.length ? '<details><summary>Befund (' + bef.length + ')</summary><ul>' + bef.map(function (b) { return '<li>' + x(b) + '</li>'; }).join('') + '</ul></details>' : '') +
            (i.nachricht_entwurf ? '<details><summary>Nachricht-Entwurf</summary><textarea rows="6" id="t-' + i.id + '">' + x(i.nachricht_entwurf) + '</textarea><button class="btn ghost" data-a="kopieren" data-id="' + i.id + '">Kopieren</button></details>' : '') +
            '<div class="in-row"><select data-a="status" data-id="' + i.id + '">' + STATUS.map(function (s) { return '<option' + (s === i.status ? ' selected' : '') + '>' + s + '</option>'; }).join('') + '</select>' +
            '<label class="in-muted">nächster Schritt <input type="date" data-a="schritt" data-id="' + i.id + '" value="' + x(i.naechster_schritt || '') + '"></label></div></article>';
        }).join('');
    },

    kunden: async function () {
      var r = await Promise.all([api('kunden?select=id,firma,ansprechpartner,email,telefon,status,seit,vertraege(id,produkt,einmalig,monatlich,start,mindestlaufzeit_monate,ende)&order=firma'),
        api('inhalte_formulare?select=id,titel,token,frist,eingereicht_am,kunde_id,dateien&order=angelegt.desc')]);
      CACHE.kunden = r[0];
      var opt = Object.keys(PRODUKTE).map(function (k) { return '<option value="' + k + '">' + PRODUKTE[k][0] + '</option>'; }).join('');
      return '<form class="in-form in-inline" data-form="kunde"><input name="firma" placeholder="Firma" required><input name="ansprechpartner" placeholder="Ansprechpartner"><input name="email" type="email" placeholder="E-Mail"><input name="telefon" placeholder="Telefon"><button class="btn">Kunde anlegen</button></form>' +
        r[0].map(function (k) {
          var mtl = (k.vertraege || []).filter(function (v) { return !v.ende; }).reduce(function (s, v) { return s + Number(v.monatlich || 0); }, 0);
          var forms = r[1].filter(function (f) { return f.kunde_id === k.id; });
          return '<article class="in-card"><div class="in-row in-between"><h3>' + x(k.firma) + ' <span class="in-muted">' + x(k.status) + ' · seit ' + datum(k.seit) + '</span></h3><b>' + eur(mtl) + '/Monat</b></div>' +
            '<p class="in-muted">' + x([k.ansprechpartner, k.email, k.telefon].filter(Boolean).join(' · ')) + '</p>' +
            '<ul class="in-list">' + (k.vertraege || []).map(function (v) { return '<li>' + x((PRODUKTE[v.produkt] || [v.produkt])[0]) + ' · ' + eur(v.monatlich) + '/Monat' + (Number(v.einmalig) ? ' + ' + eur(v.einmalig) + ' einmalig' : '') + ' · ab ' + datum(v.start) + (v.mindestlaufzeit_monate ? ' · ' + v.mindestlaufzeit_monate + ' Monate' : '') + (v.ende ? ' · beendet ' + datum(v.ende) : '') + '</li>'; }).join('') + '</ul>' +
            '<form class="in-form in-inline" data-form="vertrag" data-kunde="' + k.id + '"><select name="produkt">' + opt + '</select><input name="start" type="date" value="' + heute() + '"><button class="btn ghost">Vertrag hinzufügen</button></form>' +
            '<div class="in-row"><button class="btn ghost" data-a="inhalte" data-kunde="' + k.id + '" data-firma="' + x(k.firma) + '">Inhalte-Link erzeugen</button><button class="btn ghost" data-a="vertragsdoc" data-kunde="' + k.id + '">Vertrag vorbereiten</button></div><div class="in-vd" id="vd-' + k.id + '" hidden></div>' +
            forms.map(function (f) { return '<p class="in-muted">Inhalte-Formular: ' + (f.eingereicht_am ? '✓ eingegangen ' + datum(f.eingereicht_am) + ' · ' + (f.dateien || []).length + ' Dateien' : 'offen, Frist ' + datum(f.frist)) + ' · <a href="/inhalte/?t=' + x(f.token) + '" target="_blank" rel="noopener">Link</a></p>'; }).join('') +
            '</article>';
        }).join('');
    },

    websites: async function () {
      var r = await Promise.all([api('websites?select=id,domain,status,formular_email,formular_schluessel,live_seit,kunde_id,kunden(firma)&order=domain'),
        api('checks?select=website_id,art,ok,wert,zeit&order=zeit.desc&limit=300'), api('kunden?select=id,firma&order=firma')]);
      var letzte = {}; r[1].forEach(function (c) { var k = c.website_id + c.art; if (!letzte[k]) letzte[k] = c; });
      return '<form class="in-form in-inline" data-form="website"><input name="domain" placeholder="domain.de" required><select name="kunde_id"><option value="">– ohne Kunde –</option>' +
        r[2].map(function (k) { return '<option value="' + k.id + '">' + x(k.firma) + '</option>'; }).join('') + '</select><select name="status"><option>entwurf</option><option>vorschau</option><option>live</option></select><input name="formular_email" type="email" placeholder="Formular an (E-Mail)"><button class="btn">Website anmelden</button></form>' +
        r[0].map(function (w) {
          var u = letzte[w.id + 'uptime'], l = letzte[w.id + 'lighthouse'];
          return '<article class="in-card"><div class="in-row in-between"><h3><a href="https://' + x(w.domain) + '" target="_blank" rel="noopener">' + x(w.domain) + '</a> <span class="in-muted">' + x(w.status) + (w.kunden ? ' · ' + x(w.kunden.firma) : '') + '</span></h3>' +
            '<b>' + (u ? (u.ok ? '● erreichbar' : '● gestört') : '–') + '</b></div><p class="in-muted">' + (u ? 'zuletzt ' + new Date(u.zeit).toLocaleString('de-DE') + ' · ' + u.wert + ' ms' : 'noch nicht geprüft') +
            (l ? ' · PageSpeed ' + l.wert + '/100' : '') + ' · Formular an: ' + x(w.formular_email || 'nicht gesetzt') + '</p>' +
            '<details><summary>Formular einbinden</summary><pre class="in-pre">' + x('<form data-lotwerk-formular="' + w.formular_schluessel + '">…</form>\nPOST ' + SB + '/functions/v1/formular  {"schluessel":"' + w.formular_schluessel + '", "name", "kontakt", "nachricht"}') + '</pre></details></article>';
        }).join('');
    },

    zeiten: async function () {
      var r = await Promise.all([api('zeiten?select=id,start,kunde_id,taetigkeit,kunden(firma)&ende=is.null&order=start.desc&limit=1'),
        api('zeiten?select=minuten,taetigkeit,kunden(firma)&start=gte.' + monatsanfang() + '&ende=not.is.null'), api('kunden?select=id,firma&order=firma')]);
      var lauf = r[0][0], sum = {};
      r[1].forEach(function (z) { var k = (z.kunden ? z.kunden.firma : 'intern') + ' · ' + z.taetigkeit; sum[k] = (sum[k] || 0) + (z.minuten || 0); });
      return (lauf ? '<div class="in-card in-run"><h3>Läuft seit ' + new Date(lauf.start).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }) + '</h3><p>' + x(lauf.kunden ? lauf.kunden.firma : 'intern') + ' · ' + x(lauf.taetigkeit) + '</p><button class="btn" data-a="stopp" data-id="' + lauf.id + '">Stopp</button></div>'
        : '<form class="in-form in-inline" data-form="zeit"><select name="kunde_id"><option value="">intern / Vertrieb</option>' + r[2].map(function (k) { return '<option value="' + k.id + '">' + x(k.firma) + '</option>'; }).join('') +
          '</select><select name="taetigkeit">' + TAET.map(function (t) { return '<option>' + t + '</option>'; }).join('') + '</select><input name="notiz" placeholder="Notiz (optional)"><button class="btn">Start</button></form>') +
        '<h2>Diesen Monat</h2><ul class="in-list">' + Object.keys(sum).sort(function (a, b) { return sum[b] - sum[a]; }).map(function (k) { return '<li>' + x(k) + ': <b>' + (sum[k] / 60).toFixed(1) + ' h</b></li>'; }).join('') + '</ul>';
    },

    anfragen: async function () {
      var a = await api('agentur_anfragen?select=created_at,name,betrieb,email,telefon,thema,nachricht,quelle,kampagne,status&order=created_at.desc&limit=40');
      return a.length ? a.map(function (q) {
        return '<article class="in-card"><p class="in-muted">' + new Date(q.created_at).toLocaleString('de-DE') + ' · ' + x(q.thema || '') + ' · ' + x(q.quelle || '') + (q.kampagne ? ' · über ' + x(q.kampagne) : '') + '</p><h3>' + x(q.name) + (q.betrieb ? ' · ' + x(q.betrieb) : '') + '</h3>' +
          '<p>' + (q.email ? '<a href="mailto:' + x(q.email) + '">' + x(q.email) + '</a> ' : '') + (q.telefon ? '<a href="tel:' + x(q.telefon) + '">' + x(q.telefon) + '</a>' : '') + '</p><p>' + x(q.nachricht || '') + '</p></article>';
      }).join('') : '<p class="in-muted">Noch keine Anfragen.</p>';
    },

    berichte: async function () {
      var b = await api('berichte?select=art,von,bis,text&order=von.desc&limit=16');
      return b.length ? b.map(function (r) { return '<article class="in-card"><p class="in-muted">' + (r.art === 'monat' ? 'Monat' : 'Woche') + ' ' + datum(r.von) + ' – ' + datum(r.bis) + '</p><pre class="in-pre">' + x(r.text) + '</pre></article>'; }).join('')
        : '<p class="in-muted">Der erste Wochenbericht erscheint am Montag.</p>';
    }
  };

  // ------------------------------------------------------------ Aktionen
  function felder(form) { var d = {}; new FormData(form).forEach(function (v, k) { if (v !== '') d[k] = v; }); return d; }
  function meldung(t) { var m = document.createElement('div'); m.className = 'in-toast'; m.textContent = t; document.body.appendChild(m); setTimeout(function () { m.remove(); }, 2600); }

  app.addEventListener('click', async function (ev) {
    var b = ev.target.closest('[data-tab],[data-a]'); if (!b || b.tagName === 'SELECT' || b.tagName === 'INPUT') return;
    if (b.dataset.tab) return zeige(b.dataset.tab);
    var a = b.dataset.a, id = b.dataset.id;
    if (b.closest('#in-login') && /login|signup/.test(a)) ev.preventDefault();
    try {
      if (a === 'login' || a === 'signup' || a === 'reset') {
        var f = document.getElementById('in-login'), em = f.email.value.trim(), pw = f.pw.value;
        if (a === 'reset') { await auth('recover?redirect_to=' + encodeURIComponent(ZURUECK), { email: em }); return anmeldung('Falls das Konto existiert, kommt eine E-Mail zum Zurücksetzen.'); }
        if (!f.reportValidity()) return;
        if (a === 'signup') { await auth('signup?redirect_to=' + encodeURIComponent(ZURUECK), { email: em, password: pw }); return anmeldung('Bestätigungs-E-Mail verschickt. Nach dem Klick auf den Link hier anmelden.'); }
        setze(await auth('token?grant_type=password', { email: em, password: pw }));
        var ok = await api('rpc/ist_admin', { method: 'POST', body: {} });
        if (!ok) { S = {}; sichere(); return anmeldung('Angemeldet, aber kein Admin-Zugang. Nur die hinterlegte Inhaber-Adresse wird freigeschaltet.'); }
        return zeige((location.hash || '').slice(1) && ANSICHT[location.hash.slice(1)] ? location.hash.slice(1) : 'cockpit');
      }
      if (a === 'vertragsdoc') {
        var box = document.getElementById('vd-' + b.dataset.kunde); if (!box) return;
        if (!box.hidden) { box.hidden = true; return; }
        var kd = (CACHE.kunden || []).find(function (q) { return q.id === b.dataset.kunde; }) || {};
        var vorhanden = (kd.vertraege || []).filter(function (v) { return !v.ende; }).map(function (v) { return v.produkt; });
        box.innerHTML = '<p><b>Leistungen für den Vertrag</b></p><div class="in-vd-l">' + Object.keys(PRODUKTE).map(function (key) {
          return '<label class="check"><input type="checkbox" value="' + key + '"' + (vorhanden.indexOf(key) >= 0 ? ' checked' : '') + '> <span>' + x(PRODUKTE[key][0]) + ' · ' + (PRODUKTE[key][1] ? eur(PRODUKTE[key][1]) + ' einmalig' : '') + (PRODUKTE[key][1] && PRODUKTE[key][2] ? ' + ' : '') + (PRODUKTE[key][2] ? eur(PRODUKTE[key][2]) + '/Monat' : '') + '</span></label>'; }).join('') +
          '</div><label>Leistungsbeginn <input type="date" name="vd-start" value="' + heute() + '"></label><label>Besondere Vereinbarungen (optional)<textarea name="vd-extra" rows="3"></textarea></label>' +
          '<div class="in-row"><button class="btn" data-a="vertragoeffnen" data-kunde="' + b.dataset.kunde + '">Vertrag öffnen (Drucken / PDF)</button></div>';
        box.hidden = false; return;
      }
      if (a === 'vertragoeffnen') {
        var bx = document.getElementById('vd-' + b.dataset.kunde), kk = (CACHE.kunden || []).find(function (q) { return q.id === b.dataset.kunde; }) || {};
        var keys = [].slice.call(bx.querySelectorAll('input[type=checkbox]:checked')).map(function (i) { return i.value; });
        if (!keys.length) return meldung('Bitte mindestens eine Leistung wählen.');
        var w = window.open('', '_blank'); if (!w) return meldung('Bitte Pop-ups für diese Seite erlauben.');
        w.document.open(); w.document.write(vertragHtml(kk, keys, bx.querySelector('[name=vd-start]').value, bx.querySelector('[name=vd-extra]').value)); w.document.close();
        setTimeout(function () { w.focus(); w.print(); }, 300); return;
      }
      if (a === 'logout') { S = {}; sichere(); return anmeldung(); }
      if (a === 'erledigt') { await aendere('aufgaben', id, { erledigt_am: new Date().toISOString() }); meldung('Erledigt'); return zeige(); }
      if (a === 'freigeben') {
        var dat = { status: 'freigegeben', text: document.getElementById('t-' + id).value };
        if (b.dataset.t === 'entwuerfe') dat.entschieden_am = new Date().toISOString();
        await aendere(b.dataset.t, id, dat); meldung('Freigegeben'); return zeige();
      }
      if (a === 'verwerfen') { await aendere('entwuerfe', id, { status: 'verworfen', entschieden_am: new Date().toISOString() }); return zeige(); }
      if (a === 'kopieren') { var t = document.getElementById('t-' + id); await navigator.clipboard.writeText(t.value); meldung('Kopiert'); return; }
      if (a === 'filter') { CACHE.filter = b.dataset.f; return zeige(); }
      if (a === 'link-weg') { await aendere('links', id, { archiviert: true }); meldung('Archiviert'); return zeige(); }
      if (a === 'stopp') { await aendere('zeiten', id, { ende: new Date().toISOString() }); meldung('Gestoppt'); return zeige(); }
      if (a === 'inhalte') {
        var r = await neu('inhalte_formulare', { kunde_id: b.dataset.kunde, titel: b.dataset.firma });
        var link = location.origin + '/inhalte/?t=' + r[0].token;
        try { await navigator.clipboard.writeText(link); } catch (e) {}
        meldung('Link kopiert – an den Kunden schicken'); return zeige();
      }
    } catch (e) { meldung('Fehler: ' + e.message); if (/abgemeldet/.test(e.message)) anmeldung(); }
  });

  app.addEventListener('change', async function (ev) {
    var el = ev.target, id = el.dataset.id;
    try {
      if (el.dataset.a === 'status') { var d = { status: el.value }; if (el.value === 'kontaktiert') d.kontaktiert_am = heute(); await aendere('interessenten', id, d); meldung('Status: ' + el.value); }
      if (el.dataset.a === 'schritt') { await aendere('interessenten', id, { naechster_schritt: el.value || null }); meldung('Gespeichert'); }
    } catch (e) { meldung('Fehler: ' + e.message); }
  });

  app.addEventListener('submit', async function (ev) {
    var f = ev.target, art = f.dataset.form; if (!art) return; ev.preventDefault();
    var d = felder(f);
    try {
      if (art === 'aufgabe') { d.prioritaet = Number(d.prioritaet); d.quelle = 'manuell'; await neu('aufgaben', d); }
      if (art === 'interessent') { d.quelle = 'manuell'; await neu('interessenten', d); }
      if (art === 'kunde') await neu('kunden', d);
      if (art === 'website') await neu('websites', d);
      if (art === 'zeit') await neu('zeiten', d);
      if (art === 'link') await neu('links', d);
      if (art === 'vertrag') {
        var p = PRODUKTE[d.produkt];
        await neu('vertraege', { kunde_id: f.dataset.kunde, produkt: p[6] || d.produkt, start: d.start, einmalig: p[1], monatlich: p[2], mindestlaufzeit_monate: p[3], verlaengerung_monate: p[4], kuendigungsfrist_monate: p[5] });
      }
      meldung('Gespeichert'); zeige();
    } catch (e) { meldung('Fehler: ' + e.message); }
  });

  async function neuesPasswort(ev) {
    ev.preventDefault();
    var pw = ev.target.pw.value;
    var r = await fetch(SB + '/auth/v1/user', { method: 'PUT', headers: { apikey: KEY, Authorization: 'Bearer ' + await token(), 'Content-Type': 'application/json' }, body: JSON.stringify({ password: pw }) });
    if (!r.ok) return meldung('Passwort konnte nicht gespeichert werden.');
    meldung('Neues Passwort gespeichert'); zeige('cockpit');
  }

  lade();
  var rueck = new URLSearchParams((location.hash || '').slice(1));
  if (rueck.get('access_token')) {                       // Link aus einer Supabase-Mail: Sitzung übernehmen
    setze({ access_token: rueck.get('access_token'), refresh_token: rueck.get('refresh_token'), expires_in: Number(rueck.get('expires_in') || 3600) });
    history.replaceState(null, '', location.pathname);
    if (rueck.get('type') === 'recovery') {
      app.innerHTML = '<div class="in-login"><h1>Neues Passwort</h1><form id="in-neu"><label>Neues Passwort<input name="pw" type="password" autocomplete="new-password" minlength="10" required></label><button class="btn">Speichern</button></form></div>';
      document.getElementById('in-neu').addEventListener('submit', neuesPasswort);
      return;
    }
  } else if (rueck.get('error')) {
    history.replaceState(null, '', location.pathname);
    anmeldung(rueck.get('error_code') === 'otp_expired' ? 'Der Link war schon benutzt oder ist abgelaufen. Ist die E-Mail bestätigt, kannst du dich einfach anmelden.' : 'Der Link aus der E-Mail hat nicht funktioniert. Bitte erneut versuchen.');
    return;
  }
  if (S.refresh) zeige((location.hash || '').slice(1) && ANSICHT[location.hash.slice(1)] ? location.hash.slice(1) : 'cockpit'); else anmeldung();
})();
