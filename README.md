# Taza · consulta de divisas

Web independiente de Andrés Rondone para consultar USD, EUR, USDT, convertir importes y explorar fechas históricas. Destino: https://taza.andresrondone.com.

## Ejecutar

Node 22, sin dependencias. `npm run dev` abre http://127.0.0.1:3187. `npm test` valida fechas, conversiones, reconversiones, prioridades y el dataset. `npm run build` prepara `dist`.

## Datos

- BCV: archivos oficiales de Claude conservados en `data/fuentes/`. Fecha valor; cotizaciones futuras se anuncian aparte.
- DolarApi: actualización de USD/EUR oficiales, identificada como fuente intermediaria.
- FRED DEXVZUS: tasa de compra original, sin aplicar retroactivamente un diferencial fijo. Antes de 2008 se pasa de Bs.F a Bs de la época. El 1 de octubre de 2021 se corrige la unidad antigua publicada por la Fed. DEXUSEU permite estimar EUR; la interfaz etiqueta el cálculo.
- Banco Mundial PA.NUS.FCRF: 40 promedios anuales 1960–1999 separados de las series diarias.
- Binance P2P: mediana de hasta diez anuncios de comerciantes por lado, sin filtro por método de pago. Sin precio garantizado ni comisiones. Registro propio desde el 25 de septiembre de 2026.
- Yadio: referencia de mercado independiente; no se presenta como USDT.

Gráfico en bolívares actuales; tabla y calculadora en la unidad nominal de cada fecha. Se identifica el último dato publicado, máximo 7 días, sin rellenar huecos en la tabla. USDT requiere muestra de la fecha exacta.

## Actualización

`/api/live` sirve la última instantánea USD/EUR/USDT del registro programado, con caché CDN de 5 minutos y fechas de origen. `/api/history` sirve el histórico consolidado que el registro programado amplía con DolarApi, Yadio y Binance. Consulta el registro guardado al abrir y cada doce horas mientras la página está visible; ante fallos muestra los datos guardados con aviso.

El workflow `Registrar tasas` corre dos veces al día (10:00 y 22:00 UTC; 06:00 y 18:00 en Venezuela) y manualmente. Conserva la última muestra diaria en `public/data/usdt.json`, respalda `latest.json` y amplía `history.json`. Usa el token efímero de Actions, sin claves externas. Los cron de GitHub pueden retrasarse; revisar periódicamente Actions. Si todas las fuentes fallan, conserva los archivos y falla de forma visible. No sustituye USDT por otro activo cuando Binance está inaccesible.

## Despliegue

`vercel deploy --prod`. Estáticos en `dist`, funciones Node en `api/`. CSP y protección de enmarcado en `vercel.json`. No se recopilan datos privados del visitante. Los originales `historico.json` y `construir_historico.py` se conservan como evidencia histórica; el sitio usa `history.json` y `preparar_v2.py`.

Fuentes: https://www.bcv.org.ve/estadisticas/tipo-cambio-de-referencia-smc · https://dolarapi.com/docs/venezuela/ · https://fred.stlouisfed.org/series/DEXVZUS · https://fred.stlouisfed.org/series/DEXUSEU · https://data.worldbank.org/indicator/PA.NUS.FCRF?locations=VE · https://p2p.binance.com · https://www.yadio.io/info.html

## iPhone y pago móvil

Pantalla principal: entrada con selector BCV (predeterminado), euro o USDT y copia de solo el importe en Bs, con coma decimal y sin separadores de miles. La diferencia USDT/BCV usa `(USDT / BCV - 1) × 100`. Las herramientas avanzadas permanecen plegadas. App instalable con manifest standalone, Apple touch icon, áreas seguras y service worker. Después de una visita conectada puede abrirse sin conexión; la UI marca los datos guardados. Apple: https://support.apple.com/es-us/guide/iphone/iphea86e5236/ios
