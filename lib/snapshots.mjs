import {readFile} from 'node:fs/promises';
import {getJSON} from './providers.mjs';
const ROOT='https://raw.githubusercontent.com/andresrondone-tech/bcv-dolar/main/public/data/';
export async function loadSnapshot(name){try{return await getJSON(ROOT+name);}catch{return JSON.parse(await readFile(new URL('../public/data/'+name,import.meta.url),'utf8'));}}
