import {readFile,writeFile} from 'node:fs/promises';
import {fetchLive,fetchHistory} from '../lib/providers.mjs';
import {mergeRows} from '../public/core.js';
const live=await fetchLive();if(!live.usd&&!live.eur&&!live.usdt)throw new Error('Todas las fuentes fallaron; se conserva el último archivo.');
await writeFile(new URL('../public/data/latest.json',import.meta.url),JSON.stringify(live,null,2)+'\n');
if(live.usdt){const path=new URL('../public/data/usdt.json',import.meta.url);const history=JSON.parse(await readFile(path,'utf8'));const record={date:live.usdt.date,buy:live.usdt.buy,sell:live.usdt.sell,observedAt:live.usdt.updatedAt,count:live.usdt.count,source:'Binance P2P · mediana de hasta 10 anuncios de comerciantes por lado'};const idx=history.findIndex(x=>x.date===record.date);if(idx<0)history.push(record);else history[idx]=record;await writeFile(path,JSON.stringify(history.sort((a,b)=>a.date.localeCompare(b.date)),null,2)+'\n');}
console.log(JSON.stringify({updatedAt:live.fetchedAt,usd:!!live.usd,eur:!!live.eur,usdt:!!live.usdt,errors:live.errors}));
const remote=await fetchHistory();
const file=new URL('../public/data/history.json',import.meta.url);
const dataset=JSON.parse(await readFile(file,'utf8'));
dataset.rows=mergeRows(dataset.rows,remote.rows);
if(live.usdt)dataset.rows=mergeRows(dataset.rows,[[live.usdt.date,null,null,live.usdt.buy,'--x',null]]);
dataset.generated=new Date().toISOString();
await writeFile(file,JSON.stringify(dataset)+'\n');
