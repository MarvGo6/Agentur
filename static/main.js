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
    e.preventDefault();var d=new FormData(f),lines=[];
    d.forEach(function(v,k){if(k!=='einwilligung'&&v)lines.push(k.charAt(0).toUpperCase()+k.slice(1)+': '+v)});
    location.href='mailto:'+f.dataset.to+'?subject='+encodeURIComponent('Anfrage über die Website – '+(d.get('betrieb')||d.get('name')||''))+'&body='+encodeURIComponent(lines.join('\n'));
    setTimeout(function(){location.href='/danke/'},800);
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
