import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from solutions_scope import business_category,shared_scope,parse_listing
from sync_nexcom_catalog import plan_catalog
from test_nexcom_catalog import source,catalog,old
class SolutionsTests(unittest.TestCase):
 def test_only_verified_shared_office_items_are_selected(self):
  printer=dict(source(),name='Impresora Epson EcoTank',sku='100001')
  gamer=dict(source('100002'),name='Monitor Gamer MSI')
  other=dict(source('100003'),name='UPS APC 1000VA')
  self.assertEqual(set(shared_scope([printer,gamer,other],{'100001':'EPSON','100002':'MSI'})),{'100001'})
 def test_scope_restricts_existing_manual_and_new_products(self):
  items=[source('100001'),source('100002')]
  result,_,_=plan_catalog(catalog(),items,set(),{'100002'},eligibility={'100001':('Computación','Monitores')})
  self.assertEqual([p['reference'] for p in result['products']],['100001'])
  self.assertEqual(result['products'][0]['category'],'Computación')
 def test_large_disappearance_blocks_publication(self):
  with self.assertRaisesRegex(ValueError,'Cambio masivo'):
   plan_catalog(catalog([old(str(100001+i)) for i in range(5)]),[],set(),set(),eligibility={})
 def test_cricut_and_webcam_are_correctly_classified(self):
  self.assertEqual(business_category({'name':'Máquina Cricut Maker 4'})[0],'Cricut')
  self.assertEqual(business_category({'name':'Cámara web Logitech'})[0],'Accesorios de oficina')
 def test_title_type_overrides_wrong_supplier_category(self):
  keyboard={'name':'Combo Teclado y Mouse MSI','categories':[{'name':'Alarmas','link':'https://nexcomtienda.com.do/categoria-producto/seguridad/alarmas/'}]}
  self.assertEqual(business_category(keyboard),('Accesorios de oficina','Teclados y combos'))
  self.assertIsNone(business_category({'name':'Monitor Acer reacondicionado'}))
 def test_partial_omega_page_is_rejected(self):
  with self.assertRaises(ValueError):parse_listing(b'<div id="product-list">Mostrando 1 a 100 de 150 (2 paginas)</div>',1)
