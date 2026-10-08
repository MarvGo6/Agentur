// Herkunft aus der aufgerufenen Adresse (utm_source/utm_campaign, Klick-Parameter) – nur als Wort, ohne Kennung, ohne Speicherung im Gerät
function lwQuelle(){try{var q=new URLSearchParams(location.search),s=(q.get('gclid')||q.get('gbraid')||q.get('wbraid'))?'google-ads':q.get('fbclid')?'meta':(q.get('utm_source')||'');
  s=s.toLowerCase().replace(/[^a-z0-9_.-]/g,'').slice(0,40);var c=(q.get('utm_campaign')||'').replace(/[^\w .-]/g,'').slice(0,80);return s?(c?s+' / '+c:s).slice(0,100):null}catch(e){return null}}
// Google-Klick-Kennung nur, wenn der Google-Ads-Messung zugestimmt wurde (für spätere Offline-Conversions)
function lwGclid(){try{var e=JSON.parse(localStorage.getItem('lw-einwilligung')||'null');if(!e||!e.erlaubt||e.erlaubt.indexOf('anzeigen')<0)return null;
  var g=new URLSearchParams(location.search).get('gclid');if(!g){var m=document.cookie.match(/(?:^|; )_gcl_aw=([^;]*)/);if(m)g=m[1].split('.').slice(2).join('.')}return g?g.slice(0,200):null}catch(x){return null}}
(function(){
  var r=document.documentElement,t=document.querySelector('.theme'),b=document.querySelector('.burger'),n=document.querySelector('.nav');
  try{var s=localStorage.getItem('theme');if(s)r.setAttribute('data-theme',s)}catch(e){}
  if(t)t.addEventListener('click',function(){
    var dark=r.getAttribute('data-theme')==='dark'||(!r.getAttribute('data-theme')&&matchMedia('(prefers-color-scheme: dark)').matches);
    var v=dark?'light':'dark';r.setAttribute('data-theme',v);try{localStorage.setItem('theme',v)}catch(e){}
  });
  if(b)b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o)});
  var f=document.getElementById('anfrage');
  try{var k=new URLSearchParams(location.search).get('thema'),o=k&&f&&f.querySelector('option[data-k="'+k.replace(/[^a-z]/g,'')+'"]');if(o)o.selected=true}catch(e){}
  if(f)f.addEventListener('submit',function(e){
    e.preventDefault();
    var d=new FormData(f),btn=f.querySelector('button[type=submit]'),msg=f.querySelector('.form-msg');
    if(d.get('website'))return;                                   // Spam-Falle
    var daten={name:(d.get('name')||'').trim(),betrieb:(d.get('betrieb')||'').trim()||null,email:(d.get('email')||'').trim(),
      telefon:(d.get('telefon')||'').trim()||null,thema:d.get('thema')||null,nachricht:(d.get('nachricht')||'').trim()||null,
      quelle:location.pathname.slice(0,200),einwilligung:!!d.get('einwilligung'),kampagne:lwQuelle(),gclid:lwGclid()};
    function mail(){var z=[];Object.keys(daten).forEach(function(k){if(daten[k]&&k!=='einwilligung'&&k!=='quelle'&&k!=='gclid')z.push(k.charAt(0).toUpperCase()+k.slice(1)+': '+daten[k])});
      location.href='mailto:'+f.dataset.to+'?subject='+encodeURIComponent('Anfrage über die Website – '+(daten.betrieb||daten.name))+'&body='+encodeURIComponent(z.join('\n'))}
    if(!f.dataset.sb){mail();setTimeout(function(){location.href='/danke/'},800);return}
    btn.disabled=true;btn.textContent='Wird gesendet …';
    fetch(f.dataset.sb+'/rest/v1/agentur_anfragen',{method:'POST',headers:{'apikey':f.dataset.key,'Content-Type':'application/json','Prefer':'return=minimal'},body:JSON.stringify(daten)})
      .then(function(r){if(!r.ok)throw new Error(r.status);location.href='/danke/'})
      .catch(function(){btn.disabled=false;btn.textContent='Ersteinschätzung anfordern';msg.textContent='Das hat nicht geklappt – wir öffnen Ihr E-Mail-Programm mit der vorbereiteten Nachricht.';setTimeout(mail,900)});
  });
})();
(function(){
  var frames=[].slice.call(document.querySelectorAll('.lv iframe'));if(!frames.length)return;
  function fit(f){var w=f.parentNode.clientWidth;f.style.transform='scale('+(w/f.width)+')';f.parentNode.style.height=(f.height*w/f.width)+'px'}
  function load(f){if(f.src)return;fit(f);f.addEventListener('load',function(){f.classList.add('ready')});f.src=f.dataset.src}
  addEventListener('resize',function(){frames.forEach(fit)});
  // Live-Ansichten erst nach der ersten Interaktion laden – bis dahin zeigt der Rahmen das Vorschaubild
  var los=false;function start(){if(los)return;los=true;['scroll','pointermove','touchstart','keydown'].forEach(function(t){removeEventListener(t,start)});
    if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){load(x.target);io.unobserve(x.target)}})},{threshold:0.3});frames.forEach(function(f){io.observe(f)})}
    else frames.forEach(load)}
  ['scroll','pointermove','touchstart','keydown'].forEach(function(t){addEventListener(t,start,{passive:true})});
})();
(function(){
  // Anonyme Zählung ohne Zugriff auf Informationen im Endgerät (§ 25 TDDDG): nur die aufgerufene Seite und das Ereignis.
  // Keine Cookies, kein localStorage, keine Bildschirmgröße, kein Referrer, keine Kennung.
  var f=document.getElementById('anfrage'),sb=document.documentElement.getAttribute('data-sb'),key=document.documentElement.getAttribute('data-key');
  if(!sb||!key||location.hostname==='localhost'||/embed=1/.test(location.search)||/^\/(intern|inhalte)\//.test(location.pathname))return;
  var her=lwQuelle();
  function z(ereignis){if(ereignis!=='aufruf'&&ereignis!=='formular'&&window.lwKonversion)try{window.lwKonversion(ereignis)}catch(e){}   // nur aktiv nach Einwilligung (dienste.js)
    try{var b={pfad:location.pathname.slice(0,200),ereignis:ereignis};if(her)b.herkunft=her;
    fetch(sb+'/rest/v1/seitenaufrufe',{method:'POST',keepalive:true,headers:{'apikey':key,'Content-Type':'application/json','Prefer':'return=minimal'},
    body:JSON.stringify(b)}).catch(function(){})}catch(e){}}
  z('aufruf');
  document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a');if(!a)return;var h=a.getAttribute('href')||'';
    if(h.indexOf('/kontakt/')===0)z('cta');else if(h.indexOf('tel:')===0)z('telefon');else if(h.indexOf('mailto:')===0)z('mail');else if(h.indexOf('/vorschau/')===0)z('vorschau')});
  if(f)f.addEventListener('submit',function(){if(f.checkValidity())z('formular')});
})();

// Kundenweg (Handy): Tippen auf ein Symbol zeigt die passende Karte, Wischen markiert das passende Symbol
(function(){var w=document.querySelector('.cj-weg'),l=document.querySelector('.cj-line');if(!w||!l)return;
  var b=w.querySelectorAll('button'),k=l.children;
  function mark(i){for(var j=0;j<b.length;j++){b[j].classList.toggle('akt',j===i);b[j].setAttribute('aria-pressed',j===i)}}
  for(var j=0;j<b.length;j++)b[j].addEventListener('click',function(){var i=+this.getAttribute('data-cj'),c=k[i];if(!c)return;
    l.scrollTo({left:c.offsetLeft-16,behavior:'smooth'});mark(i);k[i].classList.add('blink');setTimeout(function(){c.classList.remove('blink')},700)});
  var t;l.addEventListener('scroll',function(){clearTimeout(t);t=setTimeout(function(){var x=l.scrollLeft,best=0,d=1e9;
    for(var j=0;j<k.length;j++){var e=Math.abs(k[j].offsetLeft-16-x);if(e<d){d=e;best=j}}mark(best)},80)},{passive:true});
  for (var j=0;j<k.length;j++)(function(j){k[j].addEventListener('mouseenter',function(){if(innerWidth>900)mark(j)})})(j);
  mark(0);
})();
