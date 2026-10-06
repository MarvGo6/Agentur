// Gemeinsame Helfer: Datenbankzugriff über die REST-Schnittstelle mit dem Service-Schlüssel (nur serverseitig),
// Schutz der Funktion über ein geheimes Kennwort aus der Tabelle "einstellungen" und Push-Nachrichten über ntfy.
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

let _einst: Record<string, string> | null = null;
export async function einstellung(k: string) {
  if (!_einst) _einst = Object.fromEntries((await db("einstellungen?select=schluessel,wert")).map((x: any) => [x.schluessel, x.wert]));
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
export const json = (d: unknown, status = 200) => new Response(JSON.stringify(d, null, 1), { status, headers: { "Content-Type": "application/json; charset=utf-8" } });
