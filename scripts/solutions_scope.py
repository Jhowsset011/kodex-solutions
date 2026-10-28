"""Business catalog scope and verified public Omega inventory (no account data)."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, urlencode
from omega_public import BASE_URL, _Document, _RateLimiter, _default_context, read_public_url
from sync_nexcom import normalized
from catalog_markup import description_text

ROOT=Path(__file__).resolve().parents[1]
# Public leaf categories from Omega's navigation. Gaming and domestic goods are excluded.
OMEGA_CATEGORIES=(217,142,141,175,12,35,57,62,117,167,218,173,209,208,214,61,174,169,115,114,168,212,206,131,100,200,202,207,130,129,101,43,118,98,201,82,36,170,160,162,161,68,48,220,24,139,180,179)

def business_category(source):
    name=normalized(description_text(source.get('name','')))
    if re.search(r'\b(gamer|gaming|rgb|geforce|radeon|playstation|xbox|joystick|refurbished|refurbish|reacondicionado|reacondicionada)\b',name):return None
    cats=' '.join(normalized(c.get('name',''))+' '+urlsplit(c.get('link','')).path for c in source.get('categories',[]))
    if 'cricut' in name or '/cricut/' in cats:return ('Cricut','Máquinas y herramientas' if re.search(r'maquina|prensa|maker|joy|explore|easypress',name) else 'Materiales y accesorios')
    rules=[
      (r'impres|toner|cartucho|tinta|scanner|scaner|escaner|designjet|etiqueta|\bplotter\b','Impresión'),
      (r'\bups\b|bateria|baterias|regulador|regleta|respaldo-de-energia|generador-electrico','Energía'),
      (r'seguridad|camaras|\bcamara\b|dvr|nvr|alarma|control-de-acceso|videoportero|video-vigilancia','Seguridad'),
      (r'/redes/|\bredes\b|router|switch|access.point|acces.point|repetidor|cableado|rj45|patch|\bpoe\b|telefono.ip|telefonos.ip|adaptador.de.red','Redes'),
      (r'pos.all.in.one|puntos.de.venta|caja.de.dinero|codigo|billetes|contadora.de.dinero|registradora','Punto de venta'),
      (r'laptop|notebook|desktop|desktops|computadora|mini.pc|servidor|todo.en.uno|monitor','Computación'),
      (r'teclado|\bmouse\b|memorias.usb|discos|ssd|almacenamiento|camara.web|cámara.web|software|licencia|sistema.operativo|bultos|bolsos|mochila|soportes.para.(?:monitor|laptop)','Accesorios de oficina'),
      (r'oficina|triturador|calculadora|muebles|escritorio|sillas','Oficina')]
    # A webcam is an office peripheral, not a surveillance camera.
    if re.search(r'camara web',name):return ('Accesorios de oficina','Videoconferencia')
    def leaf_for(category):
      rules_by_category={
       'Impresión':[(r'toner','Tóner'),(r'cartucho','Cartuchos'),(r'tinta','Tintas'),(r'scanner|scaner|escaner','Escáneres'),(r'papel','Papel'),(r'impresora|plotter|designjet','Impresoras')],
       'Energía':[(r'ups','UPS'),(r'bateria','Baterías'),(r'regulador','Reguladores'),(r'regleta','Regletas')],
       'Seguridad':[(r'camara','Cámaras'),(r'dvr|nvr','Grabadores'),(r'alarma','Alarmas'),(r'videoportero','Videoporteros')],
       'Computación':[(r'laptop|notebook','Laptops'),(r'monitor','Monitores'),(r'servidor','Servidores'),(r'computadora|desktop|mini pc|todo en uno','Computadoras')],
       'Accesorios de oficina':[(r'teclado','Teclados y combos'),(r'mouse.?pad','Mouse pads'),(r'mouse','Mouse'),(r'camara web','Videoconferencia'),(r'ssd|disco|memoria usb','Almacenamiento'),(r'licencia|software|sistema operativo','Software'),(r'bolso|bulto|mochila','Bolsos y mochilas')],
       'Redes':[(r'access.point|acces.point','Access points'),(r'router','Routers'),(r'switch','Switches'),(r'telefono','Telefonía IP'),(r'repetidor','Repetidores')],
       'Oficina':[(r'silla','Sillas'),(r'escritorio','Escritorios'),(r'triturador','Trituradoras')]
      }
      for pattern,label in rules_by_category.get(category,[]):
        if re.search(pattern,name):return label
      return 'Accesorios y suministros'
    # Supplier categories occasionally put a keyboard under alarms; product
    # type in the title takes precedence, with source taxonomy as fallback.
    for text in (name,cats):
      for pattern,category in rules:
        if re.search(pattern,text):return category,leaf_for(category)
    return None

def parse_listing(body,page):
    tree=_Document(body.decode('utf-8-sig')).root
    lists=tree.all(lambda n:n.attrs.get('id')=='product-list')
    if len(lists)!=1:raise ValueError('Omega no confirma listado completo')
    listing=lists[0]
    match=re.search(r'mostrando\s+(\d+)\s+a\s+(\d+)\s+de\s+(\d+)\s*\((\d+)\s+paginas?\)',normalized(listing.text()))
    if not match:raise ValueError('Omega no confirma paginación')
    first,last,total,pages=map(int,match.groups())
    cards=listing.all(lambda n:n.tag=='li' and n.has_class('product'))
    if (first,last,total,pages,page)==(1,0,1,1,1) and not cards:return {},1,1,0
    if not (1<=page<=pages<=100 and first==(page-1)*100+1 and last-first+1==len(cards) and 0<len(cards)<=100 and (page==pages or len(cards)==100)):
      raise ValueError('Página Omega incompleta')
    products={}
    for card in cards:
      links=card.all(lambda n:n.tag=='a')
      refs={m[1] for n in links if (m:=re.fullmatch(r'/es/product/consul/([1-9]\d{0,11})/?',n.attrs.get('href','')))}
      if len(refs)!=1:raise ValueError('Referencia Omega ambigua')
      titles=card.all(lambda n:n.tag in ('h2','h3','h4'))
      title=next((n.text().strip() for n in titles if n.text().strip()),'')
      if not title:
        title=next((n.attrs.get('title','').strip() for n in links if n.attrs.get('title')),'')
      if not title:raise ValueError('Producto Omega sin título')
      ref=refs.pop()
      # Omega emits duplicate rows from its public catalog joins. Count every row
      # for pagination; deduplicate only identical reference/title pairs.
      if ref in products and products[ref]!=title:raise ValueError('Referencia Omega con títulos contradictorios')
      products[ref]=title
    return products,pages,total,last

def omega_inventory(snapshot_dir=None):
    context=_default_context()  # Verified HTTPS; works with system and proxy roots.
    limiter=_RateLimiter(0.5)
    if snapshot_dir:Path(snapshot_dir).mkdir(parents=True,exist_ok=True)
    def category(code):
      result={};page=1;pages=None;expected=None
      while pages is None or page<=pages:
        url=BASE_URL+f'/es/category/list/{code}?'+urlencode({'page':page,'type':'grid','sort':'NAS','show':100})
        body=read_public_url(url,context=context,limiter=limiter)
        if snapshot_dir:(Path(snapshot_dir)/f'{code}-{page}.html').write_bytes(body)
        rows,count,total,last=parse_listing(body,page)
        if pages is not None and (pages,expected)!=(count,total):raise ValueError('Inventario Omega cambió durante lectura')
        pages,expected=count,total;result.update(rows);page+=1
      print(f'Omega categoría {code}: {len(result)} referencias',flush=True)
      return result
    inventory={}
    with ThreadPoolExecutor(max_workers=2) as pool:
      for rows in pool.map(category,OMEGA_CATEGORIES):inventory.update(rows)
    if len(inventory)<100:raise ValueError('Inventario empresarial Omega incompleto')
    return inventory

def shared_scope(items,inventory):
    return {str(p.get('sku')):business_category(p) for p in items
            if business_category(p) and str(p.get('sku')) in inventory
            and re.fullmatch(r'[1-9]\d{0,11}',str(p.get('sku')))}

def classify_business(product,source):
    scope=business_category(source)
    if scope is None:raise ValueError('Producto ajeno al alcance empresarial')
    product['category'],product['subcategory']=scope
    brands=source.get('brands') or []
    if brands:product['brand']=description_text(brands[0]['name'])
    if product['brand'] in ('Genérico','Otros'):
        for brand in ('Acer','Ezviz','Xiaomi','Mercusys','Zebra','Honeywell','Epson','Canon','Brother','Cricut'):
            if re.search(r'(?<!\w)'+re.escape(brand)+r'(?!\w)',product['name'],re.I):product['brand']=brand;break
    if scope[0]=='Cricut':product['brand']='Cricut'
    product.pop('collections',None)
    return product
