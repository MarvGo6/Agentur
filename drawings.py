"""Strichzeichnungen als Inline-SVG. Farben über currentColor, Akzente über class="c"."""

def _svg(body, vb="0 0 400 320", label=""):
    return (f'<svg class="drawing" viewBox="{vb}" role="img" aria-label="{label}" fill="none" '
            f'stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')

HERO = _svg('''
<path d="M40 280h320"/>
<path d="M70 280V150h170v130"/><path d="M60 150l20-40h150l20 40z"/>
<path d="M80 110v-6M230 110v-6"/>
<path d="M95 280v-80h45v80"/><rect x="160" y="190" width="60" height="45" rx="3"/>
<path d="M60 150q15 18 30 0q15 18 30 0q15 18 30 0q15 18 30 0q15 18 30 0q15 18 30 0"/>
<g class="c" stroke="currentColor"><circle cx="300" cy="120" r="34"/><path d="M324 144l30 30"/>
<path d="M300 104c-9 0-16 7-16 16c0 12 16 26 16 26s16-14 16-26c0-9-7-16-16-16z"/><circle cx="300" cy="120" r="5"/></g>
<path d="M270 280v-40M300 280v-62M330 280v-84" stroke-width="10" opacity=".25"/>
<path d="M262 236l38-24l30-22l22-14"/><path d="M340 172l12 4l-4 12"/>
''', label="Ladenlokal mit Lupe und Standortmarkierung")

LEISTUNG = {
 "ads": _svg('<rect x="70" y="60" width="260" height="190" rx="12"/><path d="M70 100h260"/><circle cx="92" cy="80" r="5"/><circle cx="110" cy="80" r="5"/><path d="M100 140h120M100 170h180M100 200h90"/><g class="c" stroke="currentColor"><rect x="240" y="130" width="60" height="26" rx="6"/><path d="M252 143h36"/><path d="M300 220l40 40M296 216l-8 30l12-8l10 16"/></g>', label="Anzeige im Suchergebnis"),
 "seo": _svg('<path d="M60 270h290"/><path d="M90 270v-60h40v60M150 270v-100h40v100M210 270v-140h40v140"/><g class="c" stroke="currentColor"><circle cx="300" cy="110" r="40"/><path d="M328 138l34 34"/><path d="M282 112l12 12l24-26"/></g>', label="Steigende Balken mit Lupe"),
 "web": _svg('<rect x="50" y="50" width="300" height="200" rx="12"/><path d="M50 88h300"/><circle cx="72" cy="69" r="5"/><circle cx="90" cy="69" r="5"/><rect x="80" y="112" width="130" height="80" rx="6"/><path d="M230 120h90M230 145h70M230 170h80"/><g class="c" stroke="currentColor"><path d="M150 230l-30 22l30 22M250 230l30 22l-30 22M215 222l-30 60"/></g>', label="Browserfenster mit Code-Klammern"),
 "wachstum": _svg('<path d="M60 270h290M60 270V60"/><path d="M80 240c60-10 100-40 140-90s70-70 120-80" class="c" stroke="currentColor"/><path d="M320 62l22 8l-8 22" class="c" stroke="currentColor"/><circle cx="140" cy="215" r="6"/><circle cx="220" cy="150" r="6"/><circle cx="300" cy="90" r="6"/><path d="M200 270v-30M240 270v-50M280 270v-70" opacity=".35" stroke-width="12"/>', label="Wachstumskurve"),
}

BRANCHE = {
 "friseur": _svg('<g class="c" stroke="currentColor"><circle cx="130" cy="220" r="34"/><circle cx="230" cy="220" r="34"/></g><path d="M150 194l120-140M210 194L90 54"/><circle cx="180" cy="160" r="5"/><path d="M290 80c20 10 30 30 30 60M310 60c30 16 46 46 46 90" opacity=".5"/>', label="Schere"),
 "dach": _svg('<path d="M40 280h320"/><path d="M70 280V170l110-90l110 90v110"/><path d="M50 186l130-106l130 106"/><rect x="155" y="210" width="50" height="70"/><g class="c" stroke="currentColor"><path d="M110 150l50-40l50 40l-50 40z" /><path d="M135 130l50 40M160 110v80M185 130l-50 40"/><circle cx="320" cy="70" r="24"/><path d="M320 30v-12M320 122v-12M280 70h-12M372 70h-12M292 42l-8-8M348 98l8 8M348 42l8-8M292 98l-8 8"/></g>', label="Dach mit Solarmodul und Sonne"),
 "steuer": _svg('<path d="M60 270h280M80 270v-20h240v20"/><path d="M90 250V130M150 250V130M210 250V130M270 250V130M310 250V130"/><path d="M70 130h260l-130-70z"/><g class="c" stroke="currentColor"><rect x="250" y="160" width="100" height="120" rx="8" fill="var(--card)"/><path d="M268 190h64M268 214h64M268 238h40"/><path d="M318 238l8 8l16-16"/></g>', label="Säulen und Dokument"),
 "pflege": _svg('<path d="M60 230c40-10 70-10 110 0l60 14c14 4 14 24-2 24h-58"/><path d="M60 270c60 0 120 10 170 0l90-40c14-6 8-28-8-24l-60 16"/><g class="c" stroke="currentColor"><path d="M200 170c-40-30-60-50-60-76c0-18 14-32 32-32c12 0 22 6 28 16c6-10 16-16 28-16c18 0 32 14 32 32c0 26-20 46-60 76z"/></g>', label="Hand und Herz"),
 "bestatter": _svg('<path d="M110 280h180"/><path d="M200 280V150"/><g class="c" stroke="currentColor"><path d="M200 150c-30-10-50-40-40-80c30 10 40 40 40 80zM200 150c30-10 50-40 40-80c-30 10-40 40-40 80z"/></g><path d="M200 200c-24-4-44-20-50-40M200 220c24-4 44-20 50-40"/><path d="M300 280v-70M300 210c-8-10-8-20 0-30c8 10 8 20 0 30z" class="c" stroke="currentColor"/><path d="M286 280h28"/>', label="Lilie und Kerze"),
 "tierarzt": _svg('<g class="c" stroke="currentColor"><ellipse cx="200" cy="200" rx="56" ry="46"/><ellipse cx="130" cy="130" rx="22" ry="28"/><ellipse cx="180" cy="96" rx="22" ry="28"/><ellipse cx="236" cy="100" rx="22" ry="28"/><ellipse cx="282" cy="140" rx="22" ry="28"/></g><path d="M300 230h40M320 210v40"/><path d="M60 270h280" opacity=".5"/>', label="Pfotenabdruck mit Kreuz"),
}

ICON = {
 "ads": '<svg class="ico" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="9" width="36" height="26" rx="4"/><path d="M14 20h14M14 27h20"/><path d="M34 33l7 7"/></svg>',
 "seo": '<svg class="ico" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="21" cy="21" r="12"/><path d="M30 30l11 11"/><path d="M15 23l4 4l8-9"/></svg>',
 "web": '<svg class="ico" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="8" width="38" height="30" rx="4"/><path d="M5 16h38M19 25l-5 4l5 4M29 25l5 4l-5 4"/></svg>',
 "wachstum": '<svg class="ico" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6 40h36M8 34l10-10l7 6l15-16"/><path d="M33 14h7v7"/></svg>',
}

LOGO = '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M16 3v17" /><path d="M16 20l-6 9h12z" fill="currentColor" stroke="none" class="c"/><circle cx="16" cy="4" r="2"/></svg>'

FAVICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#0f5c4a"/><path d="M16 5v14" stroke="#f6f2ea" stroke-width="2.6" stroke-linecap="round"/><path d="M16 19l-6 8h12z" fill="#e0965e"/></svg>'
