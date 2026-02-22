"""
generate_retail_data.py
=======================
Genera datasets sintéticos de retail de moda para portafolio DS.

Outputs:
  - data/dim_tiendas.csv
  - data/dim_skus.csv
  - data/dim_calendario.csv
  - data/fact_ventas.csv
  - data/fact_inventario.csv

Uso:
  python generate_retail_data.py

Requiere: pandas, numpy
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

np.random.seed(42)

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
FECHA_INICIO = "2022-01-01"
FECHA_FIN    = "2024-12-31"
N_TIENDAS    = 12
N_SKUS_BASE  = 80   # SKUs base → con talla/color se expanden

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────
# 1. DIM_TIENDAS
# ─────────────────────────────────────────────
ciudades = [
    ("Bogotá",      "Centro Comercial Andino",   "A", "Alto"),
    ("Bogotá",      "Centro Comercial Titán",    "B", "Medio"),
    ("Bogotá",      "Plaza de las Américas",     "B", "Medio"),
    ("Medellín",    "El Tesoro",                 "A", "Alto"),
    ("Medellín",    "Viva Envigado",             "B", "Medio"),
    ("Cali",        "Chipichape",                "A", "Alto"),
    ("Cali",        "Unicentro Cali",            "B", "Medio"),
    ("Barranquilla","Buenavista",                "B", "Medio"),
    ("Cartagena",   "La Serrezuela",             "A", "Alto"),
    ("Pereira",     "Parque Arboleda",           "B", "Medio"),
    ("Bucaramanga", "Cacique",                   "B", "Medio"),
    ("Manizales",   "Cable Plaza",               "C", "Bajo"),
]

dim_tiendas = pd.DataFrame(ciudades, columns=["ciudad","nombre_cc","segmento","nivel_trafico"])
dim_tiendas.insert(0, "tienda_id", [f"T{str(i+1).zfill(2)}" for i in range(len(dim_tiendas))])
dim_tiendas["region"] = dim_tiendas["ciudad"].map({
    "Bogotá":"Centro","Medellín":"Occidente","Cali":"Occidente",
    "Barranquilla":"Costa","Cartagena":"Costa","Pereira":"Eje Cafetero",
    "Bucaramanga":"Oriente","Manizales":"Eje Cafetero"
})
dim_tiendas["metros_cuadrados"] = np.random.randint(120, 400, len(dim_tiendas))
dim_tiendas["año_apertura"] = np.random.randint(2010, 2022, len(dim_tiendas))

dim_tiendas.to_csv(OUTPUT_DIR / "dim_tiendas.csv", index=False)
print(f"✅ dim_tiendas.csv → {len(dim_tiendas)} tiendas")

# ─────────────────────────────────────────────
# 2. DIM_SKUS (con Talla y Color)
# ─────────────────────────────────────────────
categorias = {
    "Camiseta":    {"tallas": ["XS","S","M","L","XL"],    "colores": ["Blanco","Negro","Azul","Rojo"], "precio_base": 45000},
    "Jean":        {"tallas": ["28","30","32","34","36"],  "colores": ["Azul Oscuro","Negro","Gris"],  "precio_base": 95000},
    "Vestido":     {"tallas": ["XS","S","M","L"],          "colores": ["Floral","Negro","Verde"],      "precio_base": 75000},
    "Chaqueta":    {"tallas": ["S","M","L","XL"],          "colores": ["Negro","Café","Azul"],         "precio_base": 120000},
    "Pantalón":    {"tallas": ["28","30","32","34","36"],  "colores": ["Negro","Beige","Gris"],        "precio_base": 80000},
    "Blusa":       {"tallas": ["XS","S","M","L","XL"],    "colores": ["Blanco","Rosa","Verde"],       "precio_base": 55000},
    "Bermuda":     {"tallas": ["S","M","L","XL"],          "colores": ["Azul","Kaki","Negro"],         "precio_base": 60000},
    "Abrigo":      {"tallas": ["S","M","L","XL"],          "colores": ["Gris","Negro","Camel"],        "precio_base": 180000},
}

# Generar modelo base (referencia sin variante)
referencias = []
ref_id = 1
for categoria, config in categorias.items():
    n_refs = max(4, N_SKUS_BASE // len(categorias))
    for i in range(n_refs):
        referencias.append({
            "referencia_id": f"REF{str(ref_id).zfill(4)}",
            "categoria": categoria,
            "precio_base": config["precio_base"],
            "temporada_lanzamiento": np.random.choice(["SS22","FW22","SS23","FW23","SS24"]),
        })
        ref_id += 1

df_refs = pd.DataFrame(referencias)

# Expandir a SKUs (referencia × talla × color)
skus = []
sku_id = 1
for _, ref in df_refs.iterrows():
    config = categorias[ref["categoria"]]
    for talla in config["tallas"]:
        for color in config["colores"]:
            variacion_precio = np.random.uniform(0.9, 1.15)
            skus.append({
                "sku_id":         f"SKU{str(sku_id).zfill(6)}",
                "referencia_id":  ref["referencia_id"],
                "categoria":      ref["categoria"],
                "talla":          talla,
                "color":          color,
                "precio_venta":   round(ref["precio_base"] * variacion_precio / 1000) * 1000,
                "costo":          round(ref["precio_base"] * variacion_precio * 0.45 / 1000) * 1000,
                "temporada":      ref["temporada_lanzamiento"],
                "es_nuevo":       np.random.choice([True, False], p=[0.3, 0.7]),
            })
            sku_id += 1

dim_skus = pd.DataFrame(skus)
dim_skus.to_csv(OUTPUT_DIR / "dim_skus.csv", index=False)
print(f"✅ dim_skus.csv → {len(dim_skus)} SKUs (referencia × talla × color)")

# ─────────────────────────────────────────────
# 3. DIM_CALENDARIO
# ─────────────────────────────────────────────
fechas = pd.date_range(FECHA_INICIO, FECHA_FIN, freq="D")

# Fechas especiales Colombia
fechas_especiales = {
    "Día de la Madre":    ["2022-05-08","2023-05-14","2024-05-12"],
    "Amor y Amistad":     ["2022-09-17","2023-09-16","2024-09-21"],
    "Navidad":            ["2022-12-25","2023-12-25","2024-12-25"],
    "Año Nuevo":          ["2022-01-01","2023-01-01","2024-01-01"],
    "Black Friday":       ["2022-11-25","2023-11-24","2024-11-29"],
    "Cyber Monday":       ["2022-11-28","2023-11-27","2024-12-02"],
    "Día del Padre":      ["2022-06-19","2023-06-18","2024-06-16"],
    "Temporada Escolar":  ["2022-01-15","2023-01-14","2024-01-13"],
}
mapa_fechas = {}
for evento, lista in fechas_especiales.items():
    for f in lista:
        mapa_fechas[f] = evento

dim_cal = pd.DataFrame({"fecha": fechas})
dim_cal["año"]          = dim_cal["fecha"].dt.year
dim_cal["mes"]          = dim_cal["fecha"].dt.month
dim_cal["semana"]       = dim_cal["fecha"].dt.isocalendar().week.astype(int)
dim_cal["dia_semana"]   = dim_cal["fecha"].dt.dayofweek          # 0=Lun
dim_cal["nombre_dia"]   = dim_cal["fecha"].dt.day_name()
dim_cal["nombre_mes"]   = dim_cal["fecha"].dt.month_name()
dim_cal["trimestre"]    = dim_cal["fecha"].dt.quarter
dim_cal["es_fin_semana"]= dim_cal["dia_semana"] >= 5
dim_cal["temporada"]    = dim_cal["mes"].map({
    12:"FW",1:"FW",2:"SS",3:"SS",4:"SS",5:"SS",
    6:"SS",7:"FW",8:"FW",9:"FW",10:"FW",11:"FW"
})
dim_cal["evento_especial"] = dim_cal["fecha"].dt.strftime("%Y-%m-%d").map(mapa_fechas).fillna("Ninguno")
dim_cal["semana_navidad"]  = ((dim_cal["mes"]==12) & (dim_cal["fecha"].dt.day >= 15))
dim_cal["semana_amor"]     = ((dim_cal["mes"]==9) & (dim_cal["dia_semana"].between(0,6)) &
                              (dim_cal["fecha"].dt.day.between(10,21)))

dim_cal.to_csv(OUTPUT_DIR / "dim_calendario.csv", index=False)
print(f"✅ dim_calendario.csv → {len(dim_cal)} días")

# ─────────────────────────────────────────────
# 4. FACT_VENTAS
# ─────────────────────────────────────────────
# Estrategia: muestreo realista (no todas las combinaciones venden cada día)
# Simulamos ~300K registros de transacciones semanales tienda-SKU

print("⏳ Generando fact_ventas (puede tardar ~30 seg)...")

tiendas_ids = dim_tiendas["tienda_id"].tolist()
skus_sample = dim_skus["sku_id"].tolist()

# Semanas en el período
semanas = pd.date_range(FECHA_INICIO, FECHA_FIN, freq="W-MON")

# Factor de estacionalidad por mes (retail moda Colombia)
estacionalidad_mes = {
    1: 0.7,  2: 0.65, 3: 0.8,  4: 0.85,
    5: 1.4,  # Día Madre
    6: 0.9,  7: 0.8,  8: 0.75,
    9: 1.2,  # Amor y Amistad
    10: 0.85, 11: 1.3,  # Black Friday
    12: 1.8   # Navidad
}

# Factor por segmento de tienda
factor_tienda = dim_tiendas.set_index("tienda_id")["segmento"].map({"A":1.4,"B":1.0,"C":0.6}).to_dict()

ventas_rows = []

for semana in semanas:
    mes = semana.month
    factor_est = estacionalidad_mes.get(mes, 1.0)

    # Cada semana: muestra aleatoria de combinaciones tienda-SKU activas
    n_combos = int(len(tiendas_ids) * 25 * factor_est)  # combos activos esa semana
    t_sample  = np.random.choice(tiendas_ids, n_combos, replace=True)
    s_sample  = np.random.choice(skus_sample, n_combos, replace=True)

    for tienda_id, sku_id in zip(t_sample, s_sample):
        precio = dim_skus.loc[dim_skus["sku_id"]==sku_id, "precio_venta"].values[0]
        ft     = factor_tienda.get(tienda_id, 1.0)
        unidades = max(1, int(np.random.lognormal(mean=1.2, sigma=0.8) * ft * factor_est))
        descuento_pct = np.random.choice([0,0,0,0.1,0.2,0.3,0.5],
                                          p=[0.5,0.15,0.1,0.1,0.08,0.04,0.03])
        precio_final = round(precio * (1 - descuento_pct))
        ventas_rows.append({
            "fecha":        semana,
            "tienda_id":    tienda_id,
            "sku_id":       sku_id,
            "unidades":     unidades,
            "precio_unitario": precio,
            "descuento_pct":   descuento_pct,
            "precio_final":    precio_final,
            "ingresos":        unidades * precio_final,
            "costo_total":     unidades * dim_skus.loc[dim_skus["sku_id"]==sku_id,"costo"].values[0],
        })

fact_ventas = pd.DataFrame(ventas_rows)
fact_ventas["margen_bruto"] = fact_ventas["ingresos"] - fact_ventas["costo_total"]
fact_ventas["margen_pct"]   = (fact_ventas["margen_bruto"] / fact_ventas["ingresos"]).round(4)

fact_ventas.to_csv(OUTPUT_DIR / "fact_ventas.csv", index=False)
print(f"✅ fact_ventas.csv → {len(fact_ventas):,} registros | Ingresos totales: ${fact_ventas['ingresos'].sum()/1e9:.1f}B COP")

# ─────────────────────────────────────────────
# 5. FACT_INVENTARIO (snapshot semanal)
# ─────────────────────────────────────────────
print("⏳ Generando fact_inventario...")

inv_rows = []
# Estado inicial de inventario por tienda-SKU
stock_actual = {}

for semana in semanas:
    mes = semana.month
    ventas_semana = fact_ventas[fact_ventas["fecha"] == semana]

    for tienda_id in tiendas_ids:
        # Muestra de SKUs asignados a esta tienda (no todos)
        skus_tienda = np.random.choice(skus_sample, size=min(50, len(skus_sample)), replace=False)

        for sku_id in skus_tienda:
            key = (tienda_id, sku_id)

            # Inicializar stock si es la primera vez
            if key not in stock_actual:
                stock_actual[key] = np.random.randint(5, 40)

            # Restar ventas de la semana
            venta = ventas_semana[
                (ventas_semana["tienda_id"] == tienda_id) &
                (ventas_semana["sku_id"] == sku_id)
            ]["unidades"].sum()
            stock_actual[key] = max(0, stock_actual[key] - venta)

            # Reabastecimiento aleatorio (lead time simulado)
            if stock_actual[key] < 5 and np.random.random() < 0.6:
                reabastecimiento = np.random.randint(10, 35)
                stock_actual[key] += reabastecimiento
            else:
                reabastecimiento = 0

            precio_sku = dim_skus.loc[dim_skus["sku_id"]==sku_id, "precio_venta"].values[0]
            stock = stock_actual[key]

            inv_rows.append({
                "fecha":              semana,
                "tienda_id":          tienda_id,
                "sku_id":             sku_id,
                "stock_disponible":   stock,
                "unidades_vendidas":  int(venta),
                "reabastecimiento":   reabastecimiento,
                "valor_inventario":   stock * precio_sku,
                "quiebre_stock":      stock == 0,
                "stock_bajo":         0 < stock < 5,
            })

fact_inventario = pd.DataFrame(inv_rows)
fact_inventario.to_csv(OUTPUT_DIR / "fact_inventario.csv", index=False)
quiebres = fact_inventario["quiebre_stock"].mean() * 100
print(f"✅ fact_inventario.csv → {len(fact_inventario):,} registros | Tasa quiebre promedio: {quiebres:.1f}%")

# ─────────────────────────────────────────────
# RESUMEN FINAL
# ─────────────────────────────────────────────
print("\n" + "="*55)
print("📦 DATASETS GENERADOS EN /data")
print("="*55)
for f in sorted(OUTPUT_DIR.glob("*.csv")):
    size_mb = f.stat().st_size / 1024 / 1024
    df_tmp  = pd.read_csv(f, nrows=1)
    print(f"  {f.name:<30} {size_mb:.1f} MB  |  {len(df_tmp.columns)} columnas")
print("\n✅ Listo para P01 - EDA de Ventas Retail")
print("   Siguiente paso: abrir 01_EDA_ventas.ipynb")
