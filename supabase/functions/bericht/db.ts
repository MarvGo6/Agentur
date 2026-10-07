// Gemeinsame Helfer (Quelle: supabase/functions/_shared/db.ts – wird beim Deploy in jede Funktion kopiert):
// Datenbankzugriff über die REST-Schnittstelle mit dem Service-Schlüssel (nur serverseitig), Schutz über ein geheimes
// Kennwort aus der Tabelle "einstellungen", Push über ntfy, Aufgaben ohne Dubletten, E-Mail (Resend) und KI-Entwürfe (Claude).
import Anthropic from "npm:@anthropic-ai/sdk@0.131.0";
const URL_ = Deno.env.get("SUPABASE_URL")!;
const KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const H = { apikey: KEY, Authorization: `Bearer ${KEY}`, "Content-Type": "application/json" };

export async function db(pfad: string, init: RequestInit = {}) {
  const r = await fetch(`${URL_}/rest/v1/${pfad}`, { ...init, headers: { ...H, ...(init.headers || {}) } });
  const t = await r.text();
  if (!r.ok) throw new Error(`DB ${r.status}: ${t.slice(0, 300)}`);
  return t ? JSON.parse(t) : null;
}
export const einfuegen = (tabelle: string, daten: unknown, extra = "") =>
  db(`${tabelle}${extra}`, { method: "POST", body: JSON.stringify(daten), headers: { Prefer: "return=representation" } });
export const aendern = (tabelle: string, filter: string, daten: unknown) =>
  db(`${tabelle}?${filter}`, { method: "PATCH", body: JSON.stringify(daten), headers: { Prefer: "return=minimal" } });

let _einst: Record<string, string> | null = null, _geladen = 0;   // Einstellungen 30 s zwischenspeichern
export async function einstellung(k: string) {
  if (!_einst || Date.now() - _geladen > 30000) _geladen = Date.now(), _einst = Object.fromEntries((await db("einstellungen?select=schluessel,wert")).map((x: any) => [x.schluessel, x.wert]));
  return _einst![k];
}
export async function erlaubt(req: Request) {
  const s = req.headers.get("x-cron-secret") || new URL(req.url).searchParams.get("key");
  return !!s && s === (await einstellung("cron_secret"));
}
export async function push(titel: string, text: string, prio = "default") {
  const thema = await einstellung("ntfy_topic");
  if (!thema) return;
  await fetch(`https://ntfy.sh/${thema}?title=${encodeURIComponent(titel)}&priority=${prio}&tags=bar_chart`, { method: "POST", body: text }).catch(() => {});
}
export async function laden(url: string, ms = 15000) {
  const c = new AbortController(); const t = setTimeout(() => c.abort(), ms); const start = performance.now();
  try {
    const r = await fetch(url, { signal: c.signal, redirect: "follow", headers: { "User-Agent": "Mozilla/5.0 (Lotwerk-Pruefung; +https://lotwork.vercel.app)" } });
    const text = await r.text();
    return { ok: r.ok, status: r.status, ms: Math.round(performance.now() - start), url: r.url, text, headers: r.headers };
  } catch (e) { return { ok: false, status: 0, ms: Math.round(performance.now() - start), url, text: "", headers: new Headers(), fehler: String(e) }; }
  finally { clearTimeout(t); }
}
export async function pagespeed(url: string) {
  const k = Deno.env.get("PSI_KEY") || (await einstellung("psi_key")) || "";
  const q = new URLSearchParams({ url, strategy: "mobile" });
  for (const c of ["performance", "accessibility", "best-practices", "seo"]) q.append("category", c);
  if (k) q.set("key", k);
  const r = await laden(`https://www.googleapis.com/pagespeedonline/v5/runPagespeed?${q}`, 60000);
  if (!r.ok) return null;
  const j = JSON.parse(r.text), lh = j.lighthouseResult;
  const s = (c: string) => Math.round((lh.categories[c]?.score ?? 0) * 100);
  return { leistung: s("performance"), barrierefreiheit: s("accessibility"), praxis: s("best-practices"), seo: s("seo"),
    lcp_s: +(lh.audits["largest-contentful-paint"]?.numericValue / 1000).toFixed(2), cls: +(+lh.audits["cumulative-layout-shift"]?.numericValue).toFixed(3) };
}
export const CORS = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET,POST,OPTIONS", "Access-Control-Allow-Headers": "content-type" };
export const json = (d: unknown, status = 200, extra: Record<string, string> = {}) =>
  new Response(JSON.stringify(d, null, 1), { status, headers: { "Content-Type": "application/json; charset=utf-8", ...extra } });
export const tag = (d = new Date()) => d.toISOString().slice(0, 10);

// Aufgabe anlegen – mit Schlüssel genau einmal (z. B. "frist:<vertrag>:2027-01")
export async function aufgabe(titel: string, schluessel: string, extra: Record<string, unknown> = {}) {
  const r = await db("aufgaben?on_conflict=schluessel", { method: "POST", body: JSON.stringify({ titel, schluessel, quelle: "check", prioritaet: 2, ...extra }),
    headers: { Prefer: "resolution=ignore-duplicates,return=representation" } }).catch(() => []);
  return Array.isArray(r) && r.length > 0;   // true = neu angelegt
}

// E-Mail über Resend (einstellungen: resend_key, mail_absender). Ohne Schlüssel: false (Aufrufer weicht auf Push aus).
export async function mail(an: string, betreff: string, text: string, antwortAn?: string) {
  const key = await einstellung("resend_key"), von = await einstellung("mail_absender");
  if (!key || !von || !an) return false;
  const r = await fetch("https://api.resend.com/emails", { method: "POST", headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from: von, to: [an], subject: betreff, text, ...(antwortAn ? { reply_to: antwortAn } : {}) }) }).catch(() => null);
  return !!r?.ok;
}

// KI-Entwurf mit Claude (einstellungen: anthropic_key oder Secret ANTHROPIC_API_KEY). Ohne Schlüssel: null.
// Jeder Lauf wird mit Kosten in ki_laeufe protokolliert. Ergebnisse sind immer Entwürfe zur Freigabe.
const MODELL = "claude-opus-5-5";
export async function ki(system: string, eingabe: string, o: { art: string; effort?: string; max?: number; bezug?: Record<string, unknown> }) {
  const key = Deno.env.get("ANTHROPIC_API_KEY") || (await einstellung("anthropic_key"));
  if (!key) return null;
  const client = new Anthropic({ apiKey: key });
  try {
    const r: any = await (client.beta.messages.create as any)({
      model: MODELL, max_tokens: o.max ?? 4000, system,
      output_config: { effort: o.effort ?? "medium" },
      betas: ["server-side-fallback-2026-07-01"], fallbacks: "default",   // bei Ablehnung automatisch empfohlenes Ersatzmodell
      messages: [{ role: "user", content: eingabe }],
    });
    const text = r.stop_reason === "refusal" ? "" : r.content.filter((b: any) => b.type === "text").map((b: any) => b.text).join("\n").trim();
    const kosten = ((r.usage?.input_tokens ?? 0) * 4 + (r.usage?.output_tokens ?? 0) * 20) / 1e6 * 0.92;  // $4/$20 je Mio. Token, grob in €
    await einfuegen("ki_laeufe", { art: o.art, modell: r.model ?? MODELL, tokens_ein: r.usage?.input_tokens, tokens_aus: r.usage?.output_tokens,
      kosten_eur: +kosten.toFixed(4), status: text ? "wartet" : "fehler", zusammenfassung: (text || `abgelehnt: ${r.stop_details?.category ?? "–"}`).slice(0, 300), ...(o.bezug ?? {}) }).catch(() => {});
    return text || null;
  } catch (e) {
    await einfuegen("ki_laeufe", { art: o.art, modell: MODELL, status: "fehler", zusammenfassung: String(e).slice(0, 300), ...(o.bezug ?? {}) }).catch(() => {});
    return null;
  }
}
