document.querySelectorAll('.demo-form').forEach(function(f){f.addEventListener('submit',function(e){e.preventDefault();var b=f.querySelector('button');if(b){b.textContent='✓ Vorschau – nichts gesendet';b.disabled=true}})});
document.querySelectorAll('.slots i').forEach(function(s){s.addEventListener('click',function(){s.parentNode.querySelectorAll('i').forEach(function(x){x.classList.remove('on')});s.classList.add('on')})});
if(/[?&]embed=1/.test(location.search)){document.documentElement.classList.add('embed');var b=document.querySelector('.demo-bar');if(b)b.remove();var m=document.querySelector('.mbar');if(m)m.remove();document.body.style.paddingBottom='0';
  // In der Live-Ansicht (Rahmen auf der Agentur-Seite) sichtbare Bilder sofort laden, sonst bleibt die Vorschau leer
  document.querySelectorAll('img[loading=lazy]').forEach(function(i){if(i.getBoundingClientRect().top<innerHeight*1.2)i.loading='eager'})}
(function(){
  function off(i){i.classList.add('off');var g=i.closest('.pgrid,.strip-f');if(g&&g.querySelectorAll('img:not(.off)').length===0){var s=g.closest('section');if(s&&!s.classList.contains('sec'))s.style.display='none';else{g.style.display='none';var fb=g.nextElementSibling;if(fb&&fb.classList.contains('fb'))fb.style.display='block'}}}
  document.querySelectorAll('img.foto').forEach(function(i){if(i.complete&&i.naturalWidth===0)off(i);else i.addEventListener('error',function(){off(i)})});
})();
