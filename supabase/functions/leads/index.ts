// V1 Lead-Liste: Betriebe aus Google Maps (Places API, neue Version) in "interessenten" eintragen.
// POST {branche, ort, anzahl?}  oder ohne Body (Zeitplan): nimmt die nächste Suche aus einstellungen.lead_suchen
// (JSON-Liste [{"branche":"Dachdecker","ort":"Bielefeld"}, …], wird reihum abgearbeitet).
// Betriebe ohne Website bekommen sofort Potenzial 95 – alle anderen analysiert die Funktion "analyse".
import { db, einstellung, push, json, erlaubt } from "./db.ts";

const FELDER = "places.id,places.displayName,places.formattedAddress,places.websiteUri,places.nationalPhoneNumber,places.rating,places.userRatingCount,places.businessStatus";

Deno.serve(async (req) => {
  if (!(await erlaubt(req))) return json({ fehler: "nicht erlaubt" }, 401);
  const key = Deno.env.get("PLACES_KEY") || (await einstellung("places_key"));
  if (!key) return json({ hinweis: "Kein Google-Places-Schlüssel hinterlegt (einstellungen.places_key)." });
  let b: any = await req.json().catch(() => ({}));
  if (!b?.branche) {
    const suchen = JSON.parse((await einstellung("lead_suchen")) || "[]");
    if (!suchen.length) return json({ hinweis: "Keine Suchen hinterlegt (einstellungen.lead_suchen)." });
    const i = Number((await einstellung("lead_index")) || 0) % suchen.length;
    b = suchen[i];
    await db("einstellungen?on_conflict=schluessel", { method: "POST", body: JSON.stringify({ schluessel: "lead_index", wert: String(i + 1) }), headers: { Prefer: "resolution=merge-duplicates,return=minimal" } });
  }
  const r = await fetch("https://places.googleapis.com/v1/places:searchText", {
    method: "POST", headers: { "Content-Type": "application/json", "X-Goog-Api-Key": key, "X-Goog-FieldMask": FELDER },
    body: JSON.stringify({ textQuery: `${b.branche} in ${b.ort}`, languageCode: "de", regionCode: "DE", pageSize: Math.min(20, Number(b.anzahl) || 20) }),
  });
  if (!r.ok) { const t = await r.text(); await push("Lead-Liste: Fehler", t.slice(0, 300)); return json({ fehler: t.slice(0, 300) }, 502); }
  const orte = ((await r.json()).places || []).filter((p: any) => p.businessStatus !== "CLOSED_PERMANENTLY");
  const zeilen = orte.map((p: any) => ({
    name: p.displayName?.text ?? "–", branche: b.branche, ort: b.ort, telefon: p.nationalPhoneNumber ?? null, website_alt: p.websiteUri ?? null,
    google_place_id: p.id, bewertung: p.rating ?? null, bewertungen_anzahl: p.userRatingCount ?? null, quelle: "places",
    ...(p.websiteUri ? {} : { potenzial: 95, analysiert_am: new Date().toISOString(), befund: { befund: ["Keine eigene Website im Google-Profil hinterlegt."] } }),
  }));
  const neu = zeilen.length ? await db("interessenten?on_conflict=google_place_id", { method: "POST", body: JSON.stringify(zeilen),
    headers: { Prefer: "resolution=ignore-duplicates,return=representation" } }) : [];
  if (neu.length) await push("Neue Interessenten", `${neu.length} neue Betriebe: ${b.branche} in ${b.ort} (${neu.filter((x: any) => !x.website_alt).length} ohne Website)`);
  return json({ suche: b, gefunden: zeilen.length, neu: neu.length });
});
