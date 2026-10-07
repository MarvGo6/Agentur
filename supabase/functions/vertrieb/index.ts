// V4 Vertrieb, täglich: (1) KI-Entwurf einer persönlichen Erstnachricht für die besten neuen Interessenten (Befund + Vorschau),
// (2) Erinnerung per Push, wenn kontaktierte Betriebe nach 3 bzw. 7 Tagen nachgefasst werden sollten oder ein vereinbarter
// nächster Schritt fällig ist. Entwürfe landen in "interessenten.nachricht_entwurf" und "entwuerfe" – verschickt wird nichts automatisch.
import { db, aendern, einfuegen, push, ki, json, erlaubt, tag } from "./db.ts";

const SYSTEM = `Du schreibst für eine kleine Webagentur kurze, persönliche Erstnachrichten an lokale Betriebe in Deutschland (Sie-Form).
Regeln: höchstens 90 Wörter, kein Marketing-Sprech, keine Superlative, nichts erfinden. Nenne genau zwei konkrete Punkte aus dem Befund,
sachlich und ohne Vorwurf. Wenn ein Vorschau-Link vorhanden ist, biete ihn an. Schließe mit einer einfachen Frage nach einem 15-Minuten-Gespräch.
Gib nur den Nachrichtentext aus, ohne Betreff, ohne Platzhalter in eckigen Klammern außer [IHR NAME].`;

Deno.serve(async (req) => {
  if (!(await erlaubt(req))) return json({ fehler: "nicht erlaubt" }, 401);
  const heute = tag(), ergebnis: any = { entwuerfe: 0, erinnerungen: [] as string[] };

  const kandidaten = await db("interessenten?select=id,name,branche,ort,website_alt,vorschau_url,befund,potenzial&status=eq.neu&nachricht_entwurf=is.null&potenzial=gte.50&order=potenzial.desc&limit=5");
  for (const i of kandidaten) {
    const punkte = (i.befund?.befund ?? []).slice(0, 5).join("\n- ");
    const text = await ki(SYSTEM, `Betrieb: ${i.name} (${i.branche ?? "–"}, ${i.ort ?? "–"})\nWebsite: ${i.website_alt ?? "keine"}\nVorschau-Link: ${i.vorschau_url ?? "keiner"}\nBefund:\n- ${punkte || "keine Website"}`,
      { art: "analyse", effort: "low", max: 1200, bezug: { interessent_id: i.id } });
    if (!text) break;                                                     // kein Schlüssel oder Fehler → später erneut
    await aendern("interessenten", `id=eq.${i.id}`, { nachricht_entwurf: text });
    await einfuegen("entwuerfe", { art: "nachricht", interessent_id: i.id, titel: `Erstnachricht ${i.name}`, text });
    ergebnis.entwuerfe++;
  }

  const kontaktiert = await db("interessenten?select=id,name,kontaktiert_am,naechster_schritt,erinnert_am&status=in.(kontaktiert,vorschau,angebot)");
  for (const i of kontaktiert) {
    const seit = i.kontaktiert_am ? Math.floor((Date.parse(heute) - Date.parse(i.kontaktiert_am)) / 864e5) : null;
    const faellig = (i.naechster_schritt && i.naechster_schritt <= heute) || seit === 3 || seit === 7;
    if (faellig && i.erinnert_am !== heute) {
      ergebnis.erinnerungen.push(`${i.name}${i.naechster_schritt && i.naechster_schritt <= heute ? " (vereinbarter Schritt fällig)" : ` (kontaktiert vor ${seit} Tagen)`}`);
      await aendern("interessenten", `id=eq.${i.id}`, { erinnert_am: heute });
    }
  }
  if (ergebnis.erinnerungen.length) await push("Heute nachfassen", ergebnis.erinnerungen.join("\n"));
  if (ergebnis.entwuerfe) await push("Neue Nachrichten-Entwürfe", `${ergebnis.entwuerfe} Erstnachrichten warten auf deine Freigabe.`);
  return json(ergebnis);
});
