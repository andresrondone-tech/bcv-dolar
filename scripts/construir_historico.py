#!/usr/bin/env python3
"""Construye public/data/historico.json a partir de las fuentes crudas de data/fuentes/.

Se corre UNA vez (o cuando se quiera reconstruir desde cero). La actualización diaria
la hace scripts/actualizar.mjs, que solo agrega los días nuevos.

Prioridad por fecha valor (tasa de VENTA, la que publica el BCV como "tasa oficial"):
  USD: BCV (XLS oficiales 2020→) > DolarApi (espejo del BCV, 2023→) > FRED DEXVZUS (2000→, compra ÷ 0,9975)
  EUR: BCV > DolarApi > calculado = USD × EUR/USD de la Reserva Federal (FRED DEXUSEU)
  USDT: Yadio (tasa de mercado P2P, último año)
Antes de 2000 solo hay promedios anuales del Banco Mundial (PA.NUS.FCRF).

Los valores se guardan NOMINALES, en el bolívar de cada época:
  Bs (VEB) < 2008-01-01 ≤ Bs.F (VEF) < 2018-08-20 ≤ Bs.S (VES) < 2021-10-01 ≤ Bs.D (actual)
"""
import csv, json, re, sys
from pathlib import Path
from datetime import date, datetime, timezone

RAIZ = Path(__file__).resolve().parent.parent
F = RAIZ / "data" / "fuentes"
SALIDA = RAIZ / "public" / "data" / "historico.json"
SPREAD = 0.9975  # compra = venta × 0,9975 (diferencial oficial del BCV, verificado en 1.446 días)


def era_factor_desde_bsf(d: str) -> float:
    """FRED y el Banco Mundial expresan todo lo anterior a 2008 en Bs.F; lo llevamos a Bs de la época."""
    return 1000.0 if d < "2008-01-01" else 1.0


def redondear(v):
    if v is None:
        return None
    return float(f"{v:.10g}") if v < 1 else round(v, 4)


def main():
    usd, eur, fuente_usd, fuente_eur, usdt = {}, {}, {}, {}, {}

    # 1) FRED DEXVZUS (compra, Bs.F antes de 2018-08-20) → venta nominal de la época
    for d, v in list(csv.reader(open(F / "fred.csv")))[1:]:
        if v in ("", "."):
            continue
        valor = float(v) / SPREAD * era_factor_desde_bsf(d)
        # La Fed cambió de unidad el 2021-10-04, pero el Bs.D rige desde el 2021-10-01.
        if d >= "2021-10-01" and valor > 1e5:
            valor /= 1e6
        usd[d] = valor
        fuente_usd[d] = "f"

    # 2) DolarApi (espejo del BCV, ya en venta y en Bs.D)
    for x in json.load(open(F / "da_historicos_dolares_oficial.json")):
        usd[x["fecha"]] = x["promedio"]; fuente_usd[x["fecha"]] = "d"
    for x in json.load(open(F / "da_historicos_euros_oficial.json")):
        eur[x["fecha"]] = x["promedio"]; fuente_eur[x["fecha"]] = "d"

    # 3) BCV oficial (XLS trimestrales, columna Bs./M.E. venta), máxima prioridad
    for d, r in json.load(open(F / "bcv_parsed.json")).items():
        if r.get("usd"):
            usd[d] = r["usd"]; fuente_usd[d] = "b"
        if r.get("eur"):
            eur[d] = r["eur"]; fuente_eur[d] = "b"

    # 4) EUR calculado donde el BCV no publicó euro: USD × (USD por EUR de la Fed)
    usd_por_eur = {d: float(v) for d, v in list(csv.reader(open(F / "fred_eur.csv")))[1:] if v not in ("", ".")}
    for d, v in usd.items():
        if d not in eur and d in usd_por_eur:
            eur[d] = v * usd_por_eur[d]; fuente_eur[d] = "c"

    # 5) USDT (Yadio, fechas MM/DD/YYYY, tasa del mercado P2P)
    for x in json.load(open(F / "yadio_365.json")):
        m, dd, y = x["date"].split("/")
        usdt[f"{y}-{m}-{dd}"] = x["rate"]

    fechas = sorted(set(usd) | set(eur) | set(usdt))
    filas = []
    for d in fechas:
        fu = fuente_usd.get(d, "-")
        fe = fuente_eur.get(d, "-")
        fx = "y" if d in usdt else "-"
        filas.append([d, redondear(usd.get(d)), redondear(eur.get(d)), redondear(usdt.get(d)), fu + fe + fx])

    anual = []
    wb = json.load(open(F / "wb.json"))[1]
    for x in sorted(wb, key=lambda r: r["date"]):
        if x["value"] and int(x["date"]) < 2000:
            anual.append([int(x["date"]), redondear(x["value"] * 1000.0)])  # a Bs (VEB) de la época

    # Control de saltos: dentro de una misma era un salto > ×3 en un día es sospechoso
    # (salvo devaluaciones oficiales conocidas: DICOM feb-2018 y reconversión ago-2018).
    avisos = []
    prev = None
    for d, u, *_ in filas:
        if u is None:
            continue
        if prev and (u / prev[1] > 3 or u / prev[1] < 1 / 3):
            avisos.append(f"{prev[0]} {prev[1]} → {d} {u}")
        prev = (d, u)

    datos = {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "columnas": ["fecha", "usd", "eur", "usdt", "fuentes"],
        "leyenda_fuentes": {
            "b": "BCV (archivo oficial)", "d": "BCV vía DolarApi", "f": "Reserva Federal H.10 (compra BCV ÷ 0,9975)",
            "c": "Calculado: USD BCV × EUR/USD Reserva Federal", "y": "Yadio (mercado P2P)", "x": "Binance P2P (registro propio)",
        },
        "eras": [
            {"desde": "1900-01-01", "simbolo": "Bs", "nombre": "Bolívar", "a_actual": 1e-14},
            {"desde": "2008-01-01", "simbolo": "Bs.F", "nombre": "Bolívar Fuerte", "a_actual": 1e-11},
            {"desde": "2018-08-20", "simbolo": "Bs.S", "nombre": "Bolívar Soberano", "a_actual": 1e-6},
            {"desde": "2021-10-01", "simbolo": "Bs", "nombre": "Bolívar Digital", "a_actual": 1},
        ],
        "anual": anual,
        "filas": filas,
    }
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")))
    print(f"{len(filas)} filas {fechas[0]} → {fechas[-1]} · anual {len(anual)} · {SALIDA.stat().st_size/1024:.0f} KB")
    for a in avisos:
        print("  salto:", a)


if __name__ == "__main__":
    sys.exit(main())
