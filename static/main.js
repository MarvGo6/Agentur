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
      quelle:((document.referrer?document.referrer.slice(0,140)+' → ':'')+location.pathname).slice(0,200),einwilligung:!!d.get('einwilligung')};
    function mail(){var z=[];Object.keys(daten).forEach(function(k){if(daten[k]&&k!=='einwilligung'&&k!=='quelle')z.push(k.charAt(0).toUpperCase()+k.slice(1)+': '+daten[k])});
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
    if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){load(x.target);io.unobserve(x.target)}})},{rootMargin:'300px'});frames.forEach(function(f){io.observe(f)})}
    else frames.forEach(load)}
  ['scroll','pointermove','touchstart','keydown'].forEach(function(t){addEventListener(t,start,{passive:true})});
})();
(function(){
  // Anonyme Zählung: Seite, Herkunfts-Domain, Gerätetyp, Ereignis. Keine Cookies, keine Kennung, keine IP-Speicherung.
  var f=document.getElementById('anfrage'),sb=document.documentElement.getAttribute('data-sb'),key=document.documentElement.getAttribute('data-key');
  if(!sb||!key||navigator.doNotTrack==='1'||location.hostname==='localhost'||/embed=1/.test(location.search))return;
  var w=innerWidth,geraet=w<700?'handy':w<1100?'tablet':'computer',her=null;
  try{var r=document.referrer&&new URL(document.referrer);if(r&&r.hostname!==location.hostname)her=r.hostname.slice(0,100)}catch(e){}
  function z(ereignis){try{fetch(sb+'/rest/v1/seitenaufrufe',{method:'POST',keepalive:true,headers:{'apikey':key,'Content-Type':'application/json','Prefer':'return=minimal'},
    body:JSON.stringify({pfad:location.pathname.slice(0,200),herkunft:her,geraet:geraet,ereignis:ereignis})}).catch(function(){})}catch(e){}}
  z('aufruf');
  document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a');if(!a)return;var h=a.getAttribute('href')||'';
    if(h.indexOf('/kontakt/')===0)z('cta');else if(h.indexOf('tel:')===0)z('telefon');else if(h.indexOf('mailto:')===0)z('mail');else if(h.indexOf('/vorschau/')===0)z('vorschau')});
  if(f)f.addEventListener('submit',function(){if(f.checkValidity())z('formular')});
})();
