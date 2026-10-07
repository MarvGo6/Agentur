// Ü2 Zentrale Formular-Funktion für alle Kunden-Websites.
// POST {schluessel, name, kontakt, nachricht, thema?, seite?, felder?, cf_token?, firma2 (Honigtopf, muss leer sein)}
// → speichert in "anfragen" (Löschung nach 90 Tagen, siehe monitor), leitet per E-Mail an den Betrieb weiter,
// bei fehlendem Mailversand: Push an dich + Aufgabe. Antwort immer JSON mit CORS.
import { db, einfuegen, aendern, einstellung, push, aufgabe, mail, json, CORS } from "./db.ts";

const kurz = (v: unknown, n: number) => String(v ?? "").trim().slice(0, n);

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: CORS });
  if (req.method !== "POST") return json({ fehler: "nur POST" }, 405, CORS);
  const b: any = await req.json().catch(() => null);
  if (!b) return json({ fehler: "ungültige Daten" }, 400, CORS);
  if (b.firma2) return json({ ok: true }, 200, CORS);                    // Spam-Bot: still verwerfen
  const name = kurz(b.name, 120), kontakt = kurz(b.kontakt, 160), nachricht = kurz(b.nachricht, 4000);
  if (!kontakt || (!nachricht && !b.felder)) return json({ fehler: "Bitte Kontakt und Nachricht angeben." }, 400, CORS);

  const w = (await db(`websites?select=id,domain,formular_email,kunde_id&formular_schluessel=eq.${encodeURIComponent(kurz(b.schluessel, 64))}`))[0];
  if (!w) return json({ fehler: "unbekanntes Formular" }, 404, CORS);

  const secret = await einstellung("turnstile_secret");                  // Spamschutz (Cloudflare Turnstile), sobald eingerichtet
  if (secret) {
    const f = new FormData(); f.append("secret", secret); f.append("response", kurz(b.cf_token, 2048));
    const v = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body: f }).then(r => r.json()).catch(() => ({ success: false }));
    if (!v.success) return json({ fehler: "Spamschutz fehlgeschlagen – bitte Seite neu laden." }, 400, CORS);
  }
  const letzte = await db(`anfragen?select=id&website_id=eq.${w.id}&eingang=gte.${new Date(Date.now() - 6e4).toISOString()}`);
  if (letzte.length >= 5) return json({ fehler: "Zu viele Anfragen – bitte in einer Minute erneut versuchen." }, 429, CORS);

  const felder = b.felder && typeof b.felder === "object" ? Object.fromEntries(Object.entries(b.felder).slice(0, 20).map(([k, v]) => [kurz(k, 40), kurz(v, 500)])) : null;
  const [a] = await einfuegen("anfragen", { website_id: w.id, thema: kurz(b.thema, 80) || null, name, kontakt, nachricht, seite: kurz(b.seite, 200) || null, daten: felder });

  const text = [`Neue Anfrage über ${w.domain}`, "", `Name: ${name || "–"}`, `Kontakt: ${kontakt}`, b.thema ? `Thema: ${kurz(b.thema, 80)}` : "",
    ...(felder ? Object.entries(felder).map(([k, v]) => `${k}: ${v}`) : []), "", nachricht, "", `Seite: ${kurz(b.seite, 200) || "–"}`].filter(x => x !== "").join("\n");
  const antwortAn = /@/.test(kontakt) ? kontakt : undefined;
  const gesendet = w.formular_email ? await mail(w.formular_email, `Neue Anfrage: ${b.thema ? kurz(b.thema, 60) : name || "Website"}`, text, antwortAn) : false;
  if (gesendet) await aendern("anfragen", `id=eq.${a.id}`, { weitergeleitet: true });
  else {
    await push(`Anfrage ${w.domain}`, text, "high");
    await aufgabe(`Anfrage für ${w.domain} an den Betrieb weiterleiten (Mailversand nicht eingerichtet)`, `anfrage:${a.id}`, { website_id: w.id, kunde_id: w.kunde_id, prioritaet: 1 });
  }
  return json({ ok: true }, 200, CORS);
});
