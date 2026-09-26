const button=document.getElementById('install-app');
const dialog=document.getElementById('install-dialog');
let deferredPrompt=null;
const standalone=()=>window.matchMedia('(display-mode: standalone)').matches||navigator.standalone===true;
function update(){document.documentElement.classList.toggle('standalone',standalone());document.getElementById('app-install-banner').hidden=standalone();}
window.addEventListener('beforeinstallprompt',event=>{event.preventDefault();deferredPrompt=event;});
button.addEventListener('click',async()=>{if(deferredPrompt){await deferredPrompt.prompt();await deferredPrompt.userChoice;deferredPrompt=null;return;}dialog.showModal();});
document.getElementById('close-install').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',event=>{if(event.target===dialog){const box=dialog.getBoundingClientRect();if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom)dialog.close();}});
window.addEventListener('appinstalled',update);window.matchMedia('(display-mode: standalone)').addEventListener('change',update);
update();
if('serviceWorker'in navigator){window.addEventListener('load',()=>{navigator.serviceWorker.register('/sw.js',{scope:'/'}).then(registration=>registration.update()).catch(()=>{});});}
