#!/usr/bin/env python3
"""Read-only audit of business brands and shared public supplier references."""
import argparse
from collections import Counter
from datetime import datetime,timezone
import json
from pathlib import Path
from nexcom_feed import fetch_catalog
from solutions_scope import omega_inventory,shared_scope,classify_business
from sync_nexcom import brand_of

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',type=Path,required=True)
 parser.add_argument('--request-file',type=Path,required=True)
 args=parser.parse_args()
 request=json.loads(args.request_file.read_text())
 if set(request)!={'brands'} or not isinstance(request['brands'],list) or not request['brands'] or any(not isinstance(b,str) or not b.strip() for b in request['brands']):raise ValueError('Solicitud de marcas inválida')
 brands={b.upper() for b in request['brands']}
 items=fetch_catalog();inventory=omega_inventory();eligible=shared_scope(items,inventory)
 rows=[]
 for source in items:
  ref=str(source.get('sku'))
  if ref not in eligible:continue
  p=classify_business({'name':source['name'],'brand':brand_of(source['name'])},source)
  if p['brand'].upper() in brands:rows.append({'reference':ref,'brand':p['brand'],'category':p['category'],'nexcomTitle':source['name'],'omegaTitle':inventory[ref]})
 report={'verifiedAt':datetime.now(timezone.utc).isoformat(),'requestedBrands':sorted(brands),'sharedBusinessProducts':len(eligible),'brandCounts':dict(Counter(p['brand'] for p in rows)),'products':rows}
 args.output.mkdir(parents=True,exist_ok=True)
 (args.output/'brands.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='products'},ensure_ascii=False))
if __name__=='__main__':main()
