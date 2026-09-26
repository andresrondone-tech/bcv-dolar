import {fetchHistory} from '../lib/providers.mjs';
export default async function handler(req,res){if(req.method!=='GET')return res.status(405).json({error:'Método no permitido'});const data=await fetchHistory();res.setHeader('Cache-Control','public, s-maxage=3600, stale-while-revalidate=300');res.status(data.rows.length?200:503).json(data);}
