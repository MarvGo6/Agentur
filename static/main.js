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
