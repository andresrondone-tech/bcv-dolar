import {cp,mkdir,rm} from 'node:fs/promises';
await rm('dist',{recursive:true,force:true});await mkdir('dist',{recursive:true});await cp('public','dist',{recursive:true,filter:source=>!source.endsWith('/historico.json')});console.log('Sitio estático preparado en dist.');
