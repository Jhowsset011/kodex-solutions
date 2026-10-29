"""Brand-wide coverage must include supplies outside the printing menu."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from solutions_scope import business_category,printing_brand,shared_scope,omega_brand_inventory

class PrintingBrandTests(unittest.TestCase):
 def test_all_three_brands_include_unclassified_accessories_only_when_shared(self):
  products=[{'sku':str(i+1),'name':brand+' C12C937901','categories':[]} for i,brand in enumerate(('Epson','Brother','Canon'))]
  self.assertEqual(set(shared_scope(products,{'1':'Epson accessory','3':'Canon accessory'})),{'1','3'})
  self.assertIsNone(business_category({'name':'Unknown C12C937901'}))
 def test_explicit_other_manufacturer_does_not_become_epson(self):
  self.assertIsNone(printing_brand({'name':'Tinta compatible Epson','brands':[{'name':'Otro fabricante'}]}))
 def test_photo_printers_and_photo_paper_stay_in_printing(self):
  self.assertEqual(business_category({'name':'Impresora Epson EcoTank L8180 Fotográfica'}),('Impresión','Impresoras'))
  self.assertEqual(business_category({'name':'Papel fotográfico Canon Ivy Zink'}),('Impresión','Papel'))
 def test_maintenance_and_creative_equipment_have_correct_categories(self):
  self.assertEqual(business_category({'name':'Caja de mantenimiento Epson para impresora F170'}),('Impresión','Mantenimiento'))
  self.assertEqual(business_category({'name':'Máquina de coser Brother JX3135F'}),('Creación y personalización','Costura y bordado'))
  self.assertEqual(business_category({'name':'Proyector Epson PowerLite'}),('Oficina','Proyectores'))
 def test_brand_search_uses_filter_and_every_page(self):
  responses=[b'filter',b'page1',b'page2']
  with patch('solutions_scope.FULL_PRINTING_BRANDS',('Epson',)),patch('collect_omega_brands.resolve_brand_filter',return_value=['62']),patch('solutions_scope.read_public_url',side_effect=responses) as read,patch('solutions_scope.parse_listing',side_effect=[({'1':'Printer'},2,101,100),({'2':'Supply'},2,101,101)]):
   self.assertEqual(omega_brand_inventory(object(),object()),{'1':'Printer','2':'Supply'})
   self.assertIn('brands=62',read.call_args_list[1].args[0]);self.assertIn('page=2',read.call_args_list[2].args[0])
 def test_changed_search_totals_abort_instead_of_publishing_partial_brand(self):
  with patch('solutions_scope.FULL_PRINTING_BRANDS',('Epson',)),patch('collect_omega_brands.resolve_brand_filter',return_value=['62']),patch('solutions_scope.read_public_url',return_value=b'page'),patch('solutions_scope.parse_listing',side_effect=[({'1':'Printer'},2,101,100),({'2':'Supply'},2,102,102)]):
   with self.assertRaisesRegex(ValueError,'cambió'):omega_brand_inventory(object(),object())
