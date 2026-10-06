// Überwachung aller Websites (Tabelle websites, Status live/vorschau):
// täglich Erreichbarkeit + Antwortzeit, montags zusätzlich Google PageSpeed (Handy). Fehler → Aufgabe + Push.
import { db, einfuegen, erlaubt, push, laden, pagespeed, json } from "./db.ts";

Deno.serve(async (req) => {
  if (!(await erlaubt(req))) return json({ fehler: "nicht erlaubt" }, 401);
  const p = new URL(req.url).searchParams;
  const mitPsi = p.get("psi") === "1" || new Date().getUTCDay() === 1;
  const seiten = await db("websites?select=id,domain,status&status=in.(live,vorschau)&domain=not.is.null");
  const heute = new Date().toISOString().slice(0, 10), ergebnis: any[] = [], probleme: string[] = [];
  for (const w of seiten) {
    const url = `https://${w.domain}/`;
    const r = await laden(url);
    await einfuegen("checks", { website_id: w.id, art: "uptime", ok: r.ok, wert: r.ms, details: { status: r.status, fehler: (r as any).fehler ?? null } });
    if (!r.ok) probleme.push(`${w.domain} nicht erreichbar (Status ${r.status || "–"})`);
    let psi = null;
    if (mitPsi && r.ok) {
      psi = await pagespeed(url);
      if (psi) {
        await einfuegen("checks", { website_id: w.id, art: "lighthouse", ok: psi.leistung >= 90 && psi.barrierefreiheit >= 90, wert: psi.leistung, details: psi });
        const mw = Object.entries({ psi_leistung: psi.leistung, psi_barrierefreiheit: psi.barrierefreiheit, psi_seo: psi.seo, lcp_s: psi.lcp_s })
          .map(([kennzahl, wert]) => ({ website_id: w.id, datum: heute, kennzahl, wert }));
        await db("messwerte?on_conflict=website_id,datum,kennzahl", { method: "POST", body: JSON.stringify(mw), headers: { Prefer: "resolution=merge-duplicates,return=minimal" } }).catch(() => {});
        if (psi.leistung < 80) probleme.push(`${w.domain}: PageSpeed Handy nur ${psi.leistung}/100`);
      }
    }
    ergebnis.push({ domain: w.domain, erreichbar: r.ok, ms: r.ms, psi });
  }
  for (const t of probleme) {
    const offen = await db(`aufgaben?select=id&erledigt_am=is.null&titel=eq.${encodeURIComponent(t)}`);
    if (!offen.length) await einfuegen("aufgaben", { titel: t, quelle: "check", prioritaet: 1 });
  }
  if (probleme.length) await push("Website-Problem", probleme.join("\n"), "high");
  return json({ geprueft: ergebnis.length, probleme, ergebnis });
});
