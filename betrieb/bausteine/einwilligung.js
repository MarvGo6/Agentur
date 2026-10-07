/* Lotwerk-Einwilligung – schlanker Einwilligungs-Baustein für Kunden-Websites (DSGVO / § 25 TDDDG).
   Nutzung (nur wenn eine Website zustimmungspflichtige Dienste hat):
     <script>window.LW_DIENSTE=[{id:"ads",name:"Google Ads Conversion-Messung",zweck:"Misst, welche Anzeigen zu Anfragen führen.",anbieter:"Google Ireland Ltd.",gcm:["ad_storage","ad_user_data","ad_personalization"],laden:function(){ ... }},
                                {id:"maps",name:"Google Maps",zweck:"Zeigt die Karte zur Anfahrt.",anbieter:"Google Ireland Ltd."}];</script>
     <script src="/einwilligung.js" defer></script>
   Externe Inhalte zwei-klick-sicher einbetten:
     <div class="lw-extern" data-dienst="maps" data-src="https://www.google.com/maps/embed?pb=..." data-titel="Anfahrt"></div>
   Widerruf: beliebiger Link mit data-einwilligung öffnet die Einstellungen (z. B. im Fußbereich).
   Regeln: kein Dienst lädt vor der Einwilligung; alle Knöpfe sind gleich gestaltet (kein Hervorheben von „Alle akzeptieren“); Entscheidung wird nur lokal gespeichert
   (unbedingt erforderlich) und nach 12 Monaten oder bei geänderter Dienstliste erneut abgefragt; Google Consent Mode v2 startet mit „denied“. */
(function () {
  var D = window.LW_DIENSTE || [], KEY = "lw-einwilligung", VERSION = D.map(function (d) { return d.id; }).join(",");
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  gtag("consent", "default", { ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied", analytics_storage: "denied", wait_for_update: 500 });
  if (!D.length) return;                                     // keine zustimmungspflichtigen Dienste → kein Banner

  function lesen() { try { var e = JSON.parse(localStorage.getItem(KEY) || "null");
    if (e && e.v === VERSION && Date.now() - e.t < 365 * 864e5) return e; } catch (x) {} return null; }
  function speichern(erlaubt) { var e = { v: VERSION, t: Date.now(), erlaubt: erlaubt };
    try { localStorage.setItem(KEY, JSON.stringify(e)); } catch (x) {} anwenden(e); }
  var geladen = {};
  function anwenden(e) {
    var gcm = {};
    D.forEach(function (d) {
      var ja = e.erlaubt.indexOf(d.id) > -1;
      (d.gcm || []).forEach(function (k) { gcm[k] = ja ? "granted" : "denied"; });
      if (ja && d.laden && !geladen[d.id]) { geladen[d.id] = 1; try { d.laden(); } catch (x) {} }
    });
    if (Object.keys(gcm).length) gtag("consent", "update", gcm);
    externe(e);
    var b = document.getElementById("lw-ew"); if (b) b.remove();
  }
  function externe(e) {
    [].forEach.call(document.querySelectorAll(".lw-extern"), function (el) {
      var id = el.getAttribute("data-dienst"), d = D.filter(function (x) { return x.id === id; })[0];
      if (e && e.erlaubt.indexOf(id) > -1) {
        if (el.getAttribute("data-geladen")) return;
        el.setAttribute("data-geladen", "1"); el.innerHTML = "";
        var f = document.createElement("iframe"); f.src = el.getAttribute("data-src"); f.title = el.getAttribute("data-titel") || (d && d.name) || "Externer Inhalt";
        f.loading = "lazy"; f.setAttribute("referrerpolicy", "strict-origin-when-cross-origin"); f.style.cssText = "border:0;width:100%;height:100%;min-height:320px"; el.appendChild(f);
      } else if (!el.getAttribute("data-platzhalter")) {
        el.setAttribute("data-platzhalter", "1");
        el.innerHTML = '<div class="lw-ph"><p><b>' + esc((d && d.name) || "Externer Inhalt") + "</b><br>Beim Laden werden Daten an " + esc((d && d.anbieter) || "einen Drittanbieter") +
          " übertragen.</p><button type=\"button\">Inhalt laden</button></div>";
        el.querySelector("button").addEventListener("click", function () {
          var a = (lesen() || { erlaubt: [] }).erlaubt.slice(); if (a.indexOf(id) < 0) a.push(id); speichern(a); });
      }
    });
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function zeigen(einstellungen) {
    if (document.getElementById("lw-ew")) return;
    var akt = (lesen() || { erlaubt: [] }).erlaubt, w = document.createElement("div");
    w.id = "lw-ew"; w.setAttribute("role", "dialog"); w.setAttribute("aria-label", "Datenschutz-Einstellungen"); w.setAttribute("aria-modal", "false");
    w.innerHTML = '<div class="lw-box"><p class="lw-t">Ihre Datenschutz-Einstellungen</p><p>Wir möchten folgende Dienste nutzen. Sie entscheiden selbst – die Website funktioniert auch ohne. Ihre Wahl können Sie jederzeit über „Datenschutz-Einstellungen“ ändern. Details in der <a href="/datenschutz/">Datenschutzerklärung</a>.</p>' +
      (einstellungen ? '<ul class="lw-l">' + D.map(function (d) { return '<li><label><input type="checkbox" value="' + esc(d.id) + '"' + (akt.indexOf(d.id) > -1 ? " checked" : "") + "> <b>" + esc(d.name) + "</b> – " + esc(d.zweck) + " <small>(" + esc(d.anbieter || "") + ")</small></label></li>"; }).join("") + "</ul>" : "") +
      '<div class="lw-b"><button type="button" data-a="nein">Nur notwendige</button>' + (einstellungen ? '<button type="button" data-a="auswahl">Auswahl speichern</button>' : '<button type="button" data-a="einst">Einstellungen</button>') + '<button type="button" data-a="ja">Alle akzeptieren</button></div></div>';
    document.body.appendChild(w);
    w.addEventListener("click", function (ev) {
      var a = ev.target.getAttribute && ev.target.getAttribute("data-a"); if (!a) return;
      if (a === "ja") speichern(D.map(function (d) { return d.id; }));
      else if (a === "nein") speichern([]);
      else if (a === "einst") { w.remove(); zeigen(true); }
      else speichern([].map.call(w.querySelectorAll("input:checked"), function (i) { return i.value; }));
    });
    var erster = w.querySelector("button"); if (erster) erster.focus({ preventScroll: true });
  }
  var css = "#lw-ew{position:fixed;left:16px;right:16px;bottom:16px;z-index:9999;display:flex;justify-content:center;font:15px/1.5 system-ui,sans-serif}" +
    ".lw-box{max-width:640px;background:#fff;color:#111;border:1px solid #ccc;border-radius:10px;padding:20px 22px;box-shadow:0 20px 60px rgba(0,0,0,.25)}" +
    ".lw-t{font-weight:700;font-size:17px;margin:0 0 6px}.lw-box p{margin:0 0 10px}.lw-box a{color:inherit}.lw-l{list-style:none;padding:0;margin:0 0 12px}.lw-l li{margin:6px 0}" +
    ".lw-b{display:flex;flex-wrap:wrap;gap:8px}.lw-b button,.lw-ph button{flex:1 1 150px;font:inherit;font-weight:600;padding:11px 14px;border-radius:8px;border:1px solid #111;background:#fff;color:#111;cursor:pointer}" +
    ".lw-ph{font:15px/1.5 system-ui,sans-serif;display:grid;place-items:center;min-height:240px;background:#f2f2f0;border:1px dashed #bbb;border-radius:8px;padding:20px;text-align:center}";
  var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  function start() {
    var e = lesen(); if (e) anwenden(e); else { externe(null); zeigen(false); }
    document.addEventListener("click", function (ev) { var l = ev.target.closest && ev.target.closest("[data-einwilligung]"); if (l) { ev.preventDefault(); zeigen(true); } });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
