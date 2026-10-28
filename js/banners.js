// Build banners from products actually present in the validated catalog.
(() => {
 const hero=document.querySelector('.solutions-hero'); if(!hero)return;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let slides=[],index=0,timer,paused=reduced.matches;
 const el=id=>document.getElementById(id);
 const definitions=[
  ['Impresión','Tu negocio avanza.','Nosotros te equipamos.','Impresión práctica y consumibles para acompañar cada jornada.','Explorar impresión','PARA TU DÍA A DÍA'],
  ['Energía','Que nada detenga','tu próximo paso.','UPS y protección eléctrica para mantener tu negocio en marcha.','Ver UPS y energía','CONTINUIDAD PARA TU EMPRESA'],
  ['Seguridad','Tu tranquilidad,','bien conectada.','Cámaras y soluciones de seguridad para cuidar lo que construyes.','Explorar seguridad','PROTEGE TU NEGOCIO'],
  ['Cricut','De una buena idea','a tu próximo negocio.','Máquinas, herramientas y materiales para crear y personalizar.','Descubrir Cricut','CREA NUEVAS POSIBILIDADES']
 ];
 function render(){
  const [category,title,accent,description,cta,kicker,p]=slides[index];
  el('page-title').replaceChildren(document.createTextNode(title),document.createElement('br'));
  const em=document.createElement('em');em.textContent=accent;el('page-title').append(em);
  el('hero-description').textContent=description;el('hero-link').textContent=cta+' ↗';
  el('hero-link').href='/categoria/'+category.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()+'/';
  el('hero-kicker').textContent=kicker;el('hero-product').textContent=p.name;
  el('hero-image').src=p.image;el('hero-image').alt=p.name;el('hero-image').hidden=false;
  [...el('hero-dots').children].forEach((button,i)=>button.setAttribute('aria-current',String(i===index)));
 }
 function schedule(){clearInterval(timer);if(!paused&&slides.length>1&&!document.hidden)timer=setInterval(()=>{index=(index+1)%slides.length;render()},6500)}
 function pauseUI(){el('hero-pause').textContent=paused?'▶':'Ⅱ';el('hero-pause').setAttribute('aria-label',paused?'Reanudar banners':'Pausar banners')}
 el('hero-pause').addEventListener('click',()=>{paused=!paused;pauseUI();schedule()});
 hero.addEventListener('mouseenter',()=>clearInterval(timer));hero.addEventListener('mouseleave',schedule);
 hero.addEventListener('focusin',()=>clearInterval(timer));hero.addEventListener('focusout',schedule);
 document.addEventListener('visibilitychange',schedule);
 reduced.addEventListener('change',()=>{paused=reduced.matches;pauseUI();schedule()});pauseUI();
 fetch('/js/productos-v2.json').then(r=>{if(!r.ok)throw Error();return r.json()}).then(data=>{
  slides=definitions.flatMap(d=>{const list=data.products.filter(p=>p.category===d[0]&&!p.image.endsWith('.svg'));const p=list.find(p=>p.stock)||list[0];return p?[[...d,p]]:[]});
  if(!slides.length){el('hero-pause').hidden=true;return}
  slides.forEach((s,i)=>{const b=document.createElement('button');b.type='button';b.setAttribute('aria-label','Ver banner de '+s[0]);b.addEventListener('click',()=>{index=i;render();schedule()});el('hero-dots').append(b)});render();schedule();
 }).catch(()=>{el('hero-pause').hidden=true});
})();
