// Wochenbericht (Zeitplan: montags) – sammelt die Zahlen der letzten 7 Tage, speichert sie in "berichte"
// und schickt eine Kurzfassung aufs Handy. ?art=monat wertet den Vormonat aus.
import { db, erlaubt, push, json } from "./db.ts";

const zaehle = (liste: any[], feld: string) => Object.entries(liste.reduce((m: any, x: any) => { const k = x[feld] ?? "–"; m[k] = (m[k] || 0) + 1; return m; }, {}))
  .sort((a: any, b: any) => b[1] - a[1]).slice(0, 10).map(([k, v]) => ({ wert: k, anzahl: v }));
const tag = (d: Date) => d.toISOString().slice(0, 10);

Deno.serve(async (req) => {
  if (!(await erlaubt(req))) return json({ fehler: "nicht erlaubt" }, 401);
  const art = new URL(req.url).searchParams.get("art") === "monat" ? "monat" : "woche";
  const jetzt = new Date();
  let von: Date, bis: Date;
  if (art === "monat") { bis = new Date(Date.UTC(jetzt.getUTCFullYear(), jetzt.getUTCMonth(), 1)); von = new Date(Date.UTC(bis.getUTCFullYear(), bis.getUTCMonth() - 1, 1)); }
  else { bis = new Date(Date.UTC(jetzt.getUTCFullYear(), jetzt.getUTCMonth(), jetzt.getUTCDate())); von = new Date(bis.getTime() - 7 * 864e5); }
  const zr = (spalte: string) => `${spalte}=gte.${von.toISOString()}&${spalte}=lt.${bis.toISOString()}`;

  const [anfragen, aufrufe, interessenten, neueInt, checks, aufgaben, mrr] = await Promise.all([
    db(`agentur_anfragen?select=thema,quelle,created_at&${zr("created_at")}`),
    db(`seitenaufrufe?select=pfad,herkunft,geraet,ereignis&${zr("zeit")}&limit=50000`),
    db("interessenten?select=status,potenzial"),
    db(`interessenten?select=id&${zr("angelegt")}`),
    db(`checks?select=ok,art,wert,website_id&${zr("zeit")}`),
    db("aufgaben?select=id&erledigt_am=is.null"),
    db("mrr_aktuell?select=mrr,kunden"),
  ]);
  const seiten = aufrufe.filter((x: any) => x.ereignis === "aufruf");
  const cta = aufrufe.filter((x: any) => x.ereignis === "cta").length;
  const formular = aufrufe.filter((x: any) => x.ereignis === "formular").length;
  const quellen = anfragen.map((a: any) => ({ seite: (String(a.quelle || "").split("→").pop() || "").trim() || "–" }));
  const lh = checks.filter((c: any) => c.art === "lighthouse");
  const daten = {
    zeitraum: { von: tag(von), bis: tag(new Date(bis.getTime() - 864e5)) },
    website: { aufrufe: seiten.length, top_seiten: zaehle(seiten, "pfad"), herkunft: zaehle(seiten.filter((x: any) => x.herkunft), "herkunft"),
      geraete: zaehle(seiten, "geraet"), cta_klicks: cta, formular_gesendet: formular,
      quote_anfrage: seiten.length ? +(100 * anfragen.length / seiten.length).toFixed(2) : null },
    anfragen: { anzahl: anfragen.length, themen: zaehle(anfragen, "thema"), von_seite: zaehle(quellen, "seite") },
    vertrieb: { interessenten_gesamt: interessenten.length, neu: neueInt.length, nach_status: zaehle(interessenten, "status"),
      hohes_potenzial: interessenten.filter((i: any) => (i.potenzial ?? 0) >= 60 && i.status === "neu").length },
    technik: { pruefungen: checks.length, fehler: checks.filter((c: any) => !c.ok).length,
      pagespeed_mittel: lh.length ? Math.round(lh.reduce((s: number, c: any) => s + Number(c.wert), 0) / lh.length) : null },
    offene_aufgaben: aufgaben.length, mrr: mrr[0]?.mrr ?? 0, kunden: mrr[0]?.kunden ?? 0,
  };
  const text = [`${art === "monat" ? "Monat" : "Woche"} ${daten.zeitraum.von} – ${daten.zeitraum.bis}`,
    `Anfragen: ${daten.anfragen.anzahl} · Seitenaufrufe: ${daten.website.aufrufe} · Klicks auf Ersteinschätzung: ${cta}`,
    `Interessenten: ${daten.vertrieb.interessenten_gesamt} (neu ${daten.vertrieb.neu}, ${daten.vertrieb.hohes_potenzial} mit hohem Potenzial offen)`,
    `MRR: ${daten.mrr} € · Kunden: ${daten.kunden} · offene Aufgaben: ${daten.offene_aufgaben}`,
    daten.technik.fehler ? `Technik: ${daten.technik.fehler} fehlgeschlagene Prüfungen` : "Technik: alles in Ordnung"].join("\n");
  await db("berichte?on_conflict=art,von", { method: "POST", body: JSON.stringify({ art, von: tag(von), bis: daten.zeitraum.bis, daten, text }),
    headers: { Prefer: "resolution=merge-duplicates,return=minimal" } });
  if (art === "monat") {  // Löschfrist laut Datenschutzerklärung: anonyme Zählungen nach 25 Monaten entfernen
    const grenze = new Date(Date.UTC(jetzt.getUTCFullYear(), jetzt.getUTCMonth() - 25, 1)).toISOString();
    await db(`seitenaufrufe?zeit=lt.${grenze}`, { method: "DELETE", headers: { Prefer: "return=minimal" } }).catch(() => {});
  }
  await push(art === "monat" ? "Monatsbericht Lotwerk" : "Wochenbericht Lotwerk", text);
  return json({ art, daten, text });
});
