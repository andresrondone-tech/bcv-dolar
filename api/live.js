import {fetchLive} from '../lib/providers.mjs';
export default async function handler(req,res){if(req.method!=='GET')return res.status(405).json({error:'Método no permitido'});const data=await fetchLive();res.setHeader('Cache-Control','public, s-maxage=300, stale-while-revalidate=60');res.setHeader('X-Content-Type-Options','nosniff');res.status(data.usd||data.eur||data.usdt?200:503).json(data);}
