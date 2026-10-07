// E1 Inhalte-Formular: der Kunde öffnet /inhalte/?t=<token> auf der Agentur-Website und liefert Texte, Fotos und Zugänge.
// GET  ?t=…                        → Titel, Frist, bisherige Angaben (zum Weiterarbeiten)
// POST ?t=…&aktion=upload {name,typ} → signierter Upload-Link in den privaten Speicher "inhalte"
// POST ?t=…&aktion=speichern {daten, fertig}  → speichert; bei fertig: Push + Aufgabe "Inhalte prüfen"
import { db, aendern, push, aufgabe, json, CORS } from "./db.ts";

const SB = Deno.env.get("SUPABASE_URL")!, KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const TYPEN = ["image/jpeg", "image/png", "image/webp", "image/heic", "image/svg+xml", "application/pdf"];

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: CORS });
  const p = new URL(req.url).searchParams, t = (p.get("t") || "").slice(0, 64);
  const f = t && (await db(`inhalte_formulare?select=id,titel,frist,daten,dateien,eingereicht_am,angelegt,kunde_id,website_id&token=eq.${encodeURIComponent(t)}`))[0];
  if (!f || Date.now() - new Date(f.angelegt).getTime() > 90 * 864e5) return json({ fehler: "Link ungültig oder abgelaufen." }, 404, CORS);
  if (req.method === "GET") return json({ titel: f.titel, frist: f.frist, daten: f.daten, dateien: f.dateien.map((d: any) => d.name), eingereicht: !!f.eingereicht_am }, 200, CORS);

  const b: any = await req.json().catch(() => ({}));
  if (p.get("aktion") === "upload") {
    if ((f.dateien?.length ?? 0) >= 60) return json({ fehler: "Maximal 60 Dateien." }, 400, CORS);
    if (!TYPEN.includes(b.typ)) return json({ fehler: "Nur Fotos (JPG, PNG, WebP, HEIC), SVG oder PDF." }, 400, CORS);
    const sauber = String(b.name || "datei").toLowerCase().replace(/[^a-z0-9._-]+/g, "-").slice(-80);
    const pfad = `${f.id}/${Date.now()}-${sauber}`;
    const r = await fetch(`${SB}/storage/v1/object/upload/sign/inhalte/${pfad}`, { method: "POST", headers: { apikey: KEY, Authorization: `Bearer ${KEY}` } });
    if (!r.ok) return json({ fehler: "Upload derzeit nicht möglich." }, 500, CORS);
    const { url } = await r.json();                                       // relativ: /object/upload/sign/inhalte/…?token=…
    await aendern("inhalte_formulare", `id=eq.${f.id}`, { dateien: [...(f.dateien || []), { name: sauber, pfad, typ: b.typ, zeit: new Date().toISOString() }] });
    return json({ upload: `${SB}/storage/v1${url}` }, 200, CORS);
  }
  if (p.get("aktion") === "speichern") {
    const daten = JSON.parse(JSON.stringify(b.daten ?? {}).slice(0, 100000));
    await aendern("inhalte_formulare", `id=eq.${f.id}`, { daten, ...(b.fertig ? { eingereicht_am: new Date().toISOString() } : {}) });
    if (b.fertig) {
      await push("Inhalte eingegangen", `${f.titel || "Kunde"}: ${f.dateien?.length ?? 0} Dateien, Angaben vollständig abgeschickt.`, "high");
      await aufgabe(`Inhalte prüfen: ${f.titel || "Kunde"}`, `inhalte:${f.id}`, { kunde_id: f.kunde_id, website_id: f.website_id, prioritaet: 1 });
    }
    return json({ ok: true }, 200, CORS);
  }
  return json({ fehler: "unbekannte Aktion" }, 400, CORS);
});
