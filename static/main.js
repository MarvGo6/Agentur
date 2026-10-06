(function(){
  var r=document.documentElement,t=document.querySelector('.theme'),b=document.querySelector('.burger'),n=document.querySelector('.nav');
  try{var s=localStorage.getItem('theme');if(s)r.setAttribute('data-theme',s)}catch(e){}
  if(t)t.addEventListener('click',function(){
    var dark=r.getAttribute('data-theme')==='dark'||(!r.getAttribute('data-theme')&&matchMedia('(prefers-color-scheme: dark)').matches);
    var v=dark?'light':'dark';r.setAttribute('data-theme',v);try{localStorage.setItem('theme',v)}catch(e){}
  });
  if(b)b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o)});
  var f=document.getElementById('anfrage');
  if(f)f.addEventListener('submit',function(e){
    e.preventDefault();
    var d=new FormData(f),btn=f.querySelector('button[type=submit]'),msg=f.querySelector('.form-msg');
    if(d.get('website'))return;                                   // Spam-Falle
    var daten={name:(d.get('name')||'').trim(),betrieb:(d.get('betrieb')||'').trim()||null,email:(d.get('email')||'').trim(),
      telefon:(d.get('telefon')||'').trim()||null,thema:d.get('thema')||null,nachricht:(d.get('nachricht')||'').trim()||null,
      quelle:((document.referrer?document.referrer.slice(0,140)+' → ':'')+location.pathname).slice(0,200),einwilligung:!!d.get('einwilligung')};
    function mail(){var z=[];Object.keys(daten).forEach(function(k){if(daten[k]&&k!=='einwilligung'&&k!=='quelle')z.push(k.charAt(0).toUpperCase()+k.slice(1)+': '+daten[k])});
      location.href='mailto:'+f.dataset.to+'?subject='+encodeURIComponent('Anfrage über die Website – '+(daten.betrieb||daten.name))+'&body='+encodeURIComponent(z.join('\n'))}
    btn.disabled=true;btn.textContent='Wird gesendet …';
    fetch(f.dataset.sb+'/rest/v1/agentur_anfragen',{method:'POST',headers:{'apikey':f.dataset.key,'Content-Type':'application/json','Prefer':'return=minimal'},body:JSON.stringify(daten)})
      .then(function(r){if(!r.ok)throw new Error(r.status);location.href='/danke/'})
      .catch(function(){btn.disabled=false;btn.textContent='Anfrage senden';msg.textContent='Das hat nicht geklappt – wir öffnen Ihr E-Mail-Programm mit der vorbereiteten Nachricht.';setTimeout(mail,900)});
  });
})();
(function(){
  var frames=[].slice.call(document.querySelectorAll('.lv iframe'));if(!frames.length)return;
  function fit(f){var w=f.parentNode.clientWidth;f.style.transform='scale('+(w/f.width)+')';f.parentNode.style.height=(f.height*w/f.width)+'px'}
  function load(f){if(f.src)return;fit(f);f.addEventListener('load',function(){f.classList.add('ready')});f.src=f.dataset.src}
  addEventListener('resize',function(){frames.forEach(fit)});
  addEventListener('load',function(){
    setTimeout(function(){
      if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){load(x.target);io.unobserve(x.target)}})},{rootMargin:'300px'});frames.forEach(function(f){io.observe(f)})}
      else frames.forEach(load);
    },600);
  });
})();
