"""Deriva un dataset verificable sin modificar los archivos entregados por Claude."""
import json,csv,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent.parent
original=json.loads((R/'public/data/historico.json').read_text())
fred={d:float(v) for d,v in list(csv.reader((R/'data/fuentes/fred.csv').open()))[1:] if v not in ('','.')} 
euro={d:float(v) for d,v in list(csv.reader((R/'data/fuentes/fred_eur.csv').open()))[1:] if v not in ('','.')} 
rows=[]
for date,usd,eur,usdt,src in original['filas']:
    if src[0]=='f':
        usd=fred[date]*(1000 if date<'2008-01-01' else 1)
        if date=='2021-10-01':usd/=1e6
    if src[1]=='c':eur=usd*euro[date]
    rows.append([date,round(usd,6) if usd else None,round(eur,6) if eur else None,None,src[:2]+'-',usdt])
result={'generated':original['generado'],'columns':['date','usd','eur','usdt','sources','market'],'eras':original['eras'],'annual':original['anual'],'rows':rows,'sources':{'b':'BCV · archivo oficial','d':'BCV · vía DolarApi','f':'Reserva Federal · tasa de compra','c':'Euro estimado · cruce FRED','x':'Binance P2P · mediana de ofertas','y':'Yadio · referencia de mercado'}}
(R/'public/data/history.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
(R/'public/data/usdt.json').write_text('[]\n') if not (R/'public/data/usdt.json').exists() else None
hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'public/data/historico.json',R/'scripts/construir_historico.py',*sorted((R/'data/fuentes').glob('*.*'))]}
(R/'evidence/original-hashes.json').write_text(json.dumps(hashes,indent=2))
print(f'{len(rows)} registros diarios; {len(result["annual"])} promedios anuales. Fuentes originales conservadas.')
