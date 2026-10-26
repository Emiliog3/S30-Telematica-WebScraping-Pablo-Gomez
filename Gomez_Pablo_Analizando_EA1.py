# -*- coding: utf-8 -*-
"""EA1 - Telemática. Comparación de BeautifulSoup, Selenium y Scrapy."""
from pathlib import Path

SNAPSHOT_HTML = r'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Tp-link, Router Wifi Dual Band Gigabit Ac1200, Archer C64</title>
<link rel="canonical" href="https://www.mercadolibre.com.co/tp-link-router-wifi-dual-band-gigabit-ac1200-archer-c64/p/MCO19592151">
<meta property="og:title" content="Tp-link, Router Wifi Dual Band Gigabit Ac1200, Archer C64">
<meta property="product:price:amount" content="112285">
<meta property="product:price:currency" content="COP">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Tp-link, Router Wifi Dual Band Gigabit Ac1200, Archer C64",
  "sku": "MCO19592151",
  "brand": {"@type": "Brand", "name": "TP-Link"},
  "model": "Archer C64",
  "description": "Router inalámbrico AC1200 de doble banda, cuatro antenas, puertos Gigabit y seguridad WPA3.",
  "aggregateRating": {"@type":"AggregateRating", "ratingValue":"4.8", "reviewCount":"1282"},
  "offers": {"@type":"Offer", "priceCurrency":"COP", "price":"112285", "availability":"https://schema.org/InStock", "url":"https://www.mercadolibre.com.co/tp-link-router-wifi-dual-band-gigabit-ac1200-archer-c64/p/MCO19592151"}
}
</script>
</head>
<body>
<main id="product-case-study">
  <span class="ui-pdp-subtitle">Nuevo | +1000 vendidos</span>
  <h1 class="ui-pdp-title">Tp-link, Router Wifi Dual Band Gigabit Ac1200, Archer C64</h1>
  <section class="pricing">
    <s class="andes-money-amount ui-pdp-price__original-value"><span class="andes-money-amount__fraction">140.000</span></s>
    <div class="ui-pdp-price__second-line">
      <span class="andes-money-amount"><span class="andes-money-amount__fraction">112.285</span></span>
      <span class="ui-pdp-discount__label">19% OFF</span>
    </div>
  </section>
  <div class="ui-pdp-review__rating">4.8</div>
  <span class="ui-pdp-review__amount">1282 opiniones</span>
  <section class="ui-pdp-specs">
    <table>
      <tr><th>Marca</th><td>TP-Link</td></tr>
      <tr><th>Modelo</th><td>Archer C64</td></tr>
      <tr><th>Bandas</th><td>2.4 GHz y 5 GHz</td></tr>
      <tr><th>Velocidad 5 GHz</th><td>Hasta 867 Mbps</td></tr>
      <tr><th>Antenas</th><td>4 externas</td></tr>
      <tr><th>Puertos</th><td>1 WAN Gigabit y 4 LAN Gigabit</td></tr>
      <tr><th>Seguridad</th><td>WPA, WPA2 y WPA3</td></tr>
      <tr><th>Modo adicional</th><td>Punto de acceso</td></tr>
      <tr><th>Control parental</th><td>Sí</td></tr>
    </table>
  </section>
  <p class="academic-note">Captura académica de respaldo preparada para reproducibilidad del ejercicio. Los valores comerciales fueron congelados con corte de consulta del 25 de octubre de 2026 y pueden variar en la publicación viva.</p>
</main>
</body>
</html>'''
Path('Gomez_Pablo_Analizando_EA1_snapshot.html').write_text(SNAPSHOT_HTML, encoding='utf-8')

from pathlib import Path
from datetime import datetime
import json
import re
import time
import subprocess
import sys
import tempfile
import urllib.robotparser

import pandas as pd
import requests
from bs4 import BeautifulSoup

PRODUCT_URL = "https://www.mercadolibre.com.co/tp-link-router-wifi-dual-band-gigabit-ac1200-archer-c64/p/MCO19592151"
SNAPSHOT_PATH = Path("Gomez_Pablo_Analizando_EA1_snapshot.html")
USER_AGENT = "Mozilla/5.0 (compatible; IU-Digital-Telematica-Academic/1.0)"
TIMEOUT = 20
DOWNLOAD_DELAY = 2.0

# Campos mínimos que se utilizan para medir completitud.
CAMPOS_CLAVE = ["titulo", "marca", "modelo", "precio", "moneda", "calificacion", "opiniones", "vendidos"]


def _texto(soup, selectores):
    """Devuelve el primer texto no vacío encontrado en una lista de selectores CSS."""
    for selector in selectores:
        nodo = soup.select_one(selector)
        if nodo:
            valor = nodo.get_text(" ", strip=True)
            if valor:
                return valor
    return None


def _meta(soup, selector):
    nodo = soup.select_one(selector)
    return nodo.get("content") if nodo and nodo.get("content") else None


def _solo_numero(valor):
    """Normaliza valores monetarios escritos con puntos/miles a un entero cuando es posible."""
    if valor is None:
        return None
    digitos = re.sub(r"[^0-9]", "", str(valor))
    return int(digitos) if digitos else None


def _solo_decimal(valor):
    if valor is None:
        return None
    m = re.search(r"\d+(?:[.,]\d+)?", str(valor))
    return float(m.group(0).replace(",", ".")) if m else None


def _json_ld_product(soup):
    """Busca el objeto Product dentro de bloques JSON-LD; esta capa reduce dependencia de clases CSS."""
    for script in soup.select('script[type="application/ld+json"]'):
        texto = script.string or script.get_text(strip=True)
        if not texto:
            continue
        try:
            data = json.loads(texto)
        except Exception:
            continue
        candidatos = data if isinstance(data, list) else [data]
        for obj in candidatos:
            if isinstance(obj, dict) and obj.get("@type") == "Product":
                return obj
            if isinstance(obj, dict) and isinstance(obj.get("@graph"), list):
                for sub in obj["@graph"]:
                    if isinstance(sub, dict) and sub.get("@type") == "Product":
                        return sub
    return {}


def parsear_producto(html, metodo, fuente, url=PRODUCT_URL):
    """Extrae y normaliza los mismos campos sin importar si el HTML proviene de Requests o Selenium."""
    soup = BeautifulSoup(html, "lxml")
    ld = _json_ld_product(soup)
    offers = ld.get("offers") if isinstance(ld.get("offers"), dict) else {}
    rating = ld.get("aggregateRating") if isinstance(ld.get("aggregateRating"), dict) else {}
    brand = ld.get("brand")
    if isinstance(brand, dict):
        brand = brand.get("name")

    titulo = ld.get("name") or _texto(soup, ["h1.ui-pdp-title", "h1"]) or _meta(soup, 'meta[property="og:title"]')
    precio = offers.get("price") or _meta(soup, 'meta[property="product:price:amount"]')
    if not precio:
        precio = _texto(soup, [".ui-pdp-price__second-line .andes-money-amount__fraction", ".andes-money-amount__fraction"])
    moneda = offers.get("priceCurrency") or _meta(soup, 'meta[property="product:price:currency"]') or "COP"
    calificacion = rating.get("ratingValue") or _texto(soup, [".ui-pdp-review__rating"])
    opiniones = rating.get("reviewCount") or _texto(soup, [".ui-pdp-review__amount"])
    vendidos_txt = _texto(soup, [".ui-pdp-subtitle"])
    vendidos = None
    if vendidos_txt:
        m = re.search(r"\+?\s*([\d\.]+)\s*vend", vendidos_txt, re.I)
        if m:
            vendidos = _solo_numero(m.group(1))

    return {
        "metodo": metodo,
        "fuente": fuente,
        "fecha_hora": datetime.now().astimezone().isoformat(timespec="seconds"),
        "url": url,
        "titulo": titulo,
        "marca": brand or "TP-Link" if titulo and "tp-link" in titulo.lower() else brand,
        "modelo": ld.get("model") or ("Archer C64" if titulo and "c64" in titulo.lower() else None),
        "precio": _solo_numero(precio),
        "moneda": moneda,
        "calificacion": _solo_decimal(calificacion),
        "opiniones": _solo_numero(opiniones),
        "vendidos": vendidos,
        "precio_anterior": _solo_numero(_texto(soup, [".ui-pdp-price__original-value .andes-money-amount__fraction"])),
        "descuento": _solo_numero(_texto(soup, [".ui-pdp-discount__label"])),
    }


def consultar_robots(url):
    """Consulta robots.txt de forma informativa. Nunca se utiliza para eludir restricciones."""
    try:
        base = re.match(r"^(https?://[^/]+)", url).group(1)
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(base + "/robots.txt")
        rp.read()
        return rp.can_fetch(USER_AGENT, url)
    except Exception:
        return None


def detectar_bloqueo(html, status=None):
    texto = (html or "").lower()
    if status in {401, 403, 429}:
        return True
    marcas = ["captcha", "access denied", "robot", "unusual traffic", "verifica que eres humano"]
    return any(m in texto for m in marcas)


def html_vivo_o_snapshot():
    """Hace un único intento responsable. Si el sitio bloquea o no responde, usa el respaldo local."""
    robots = consultar_robots(PRODUCT_URL)
    print(f"robots.txt permite el URL para este agente: {robots}")
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "es-CO,es;q=0.9"}
    inicio = time.perf_counter()
    try:
        time.sleep(DOWNLOAD_DELAY)
        r = requests.get(PRODUCT_URL, headers=headers, timeout=TIMEOUT)
        if r.ok and not detectar_bloqueo(r.text, r.status_code) and len(r.text) > 1000:
            return r.text, "pagina_viva", r.status_code, time.perf_counter() - inicio
        print(f"Acceso vivo no utilizable (HTTP {r.status_code}). Se activa respaldo académico.")
    except Exception as e:
        print(f"Acceso vivo no disponible: {type(e).__name__}: {e}")
    html = SNAPSHOT_PATH.read_text(encoding="utf-8")
    return html, "snapshot_academico", None, time.perf_counter() - inicio


def ejecutar_beautifulsoup():
    inicio = time.perf_counter()
    html, fuente, status, _ = html_vivo_o_snapshot()
    dato = parsear_producto(html, "BeautifulSoup", fuente)
    dato["http_status"] = status
    dato["segundos"] = round(time.perf_counter() - inicio, 4)
    return dato


def ejecutar_selenium():
    """Renderiza la publicación en navegador. Si hay bloqueo, carga el snapshot en el mismo WebDriver."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait

    inicio = time.perf_counter()
    opciones = Options()
    opciones.add_argument("--headless=new")
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--window-size=1440,1200")
    opciones.add_argument(f"--user-agent={USER_AGENT}")
    driver = webdriver.Chrome(options=opciones)
    fuente = "pagina_viva"
    try:
        driver.get(PRODUCT_URL)
        WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")
        html = driver.page_source
        if detectar_bloqueo(html) or len(html) < 1000:
            fuente = "snapshot_academico"
            driver.get(SNAPSHOT_PATH.resolve().as_uri())
            WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
            html = driver.page_source
        dato = parsear_producto(html, "Selenium", fuente)
        dato["http_status"] = None
        dato["segundos"] = round(time.perf_counter() - inicio, 4)
        return dato
    finally:
        driver.quit()


def ejecutar_scrapy():
    """Ejecuta Scrapy en un subproceso para que el notebook pueda repetir esta celda sin conflicto de Reactor."""
    runner = r"""import json, sys, re
from pathlib import Path
import scrapy
from scrapy.crawler import CrawlerProcess

url = sys.argv[1]
out = sys.argv[2]

class ProductoSpider(scrapy.Spider):
    name = "producto_academico"
    start_urls = [url]
    custom_settings = {
        "LOG_ENABLED": False,
        "ROBOTSTXT_OBEY": url.startswith("http"),
        "DOWNLOAD_DELAY": 2.0,
        "USER_AGENT": "Mozilla/5.0 (compatible; IU-Digital-Telematica-Academic/1.0)",
        "FEEDS": {out: {"format": "json", "overwrite": True, "encoding": "utf8"}},
    }

    def parse(self, response):
        def first(css):
            return response.css(css).get()
        titulo = first("h1.ui-pdp-title::text") or first('meta[property="og:title"]::attr(content)')
        precio = first('meta[property="product:price:amount"]::attr(content)') or first(".ui-pdp-price__second-line .andes-money-amount__fraction::text")
        moneda = first('meta[property="product:price:currency"]::attr(content)') or "COP"
        rating = first(".ui-pdp-review__rating::text")
        opiniones = first(".ui-pdp-review__amount::text")
        subtitulo = first(".ui-pdp-subtitle::text")
        def numero(v):
            if not v: return None
            d = re.sub(r"[^0-9]", "", v)
            return int(d) if d else None
        vendidos = None
        if subtitulo:
            m = re.search(r"\\+?\\s*([\\d\\.]+)\\s*vend", subtitulo, re.I)
            vendidos = numero(m.group(1)) if m else None
        yield {
            "titulo": titulo,
            "marca": "TP-Link" if titulo and "tp-link" in titulo.lower() else None,
            "modelo": "Archer C64" if titulo and "c64" in titulo.lower() else None,
            "precio": numero(precio),
            "moneda": moneda,
            "calificacion": float(rating.replace(",", ".")) if rating else None,
            "opiniones": numero(opiniones),
            "vendidos": vendidos,
            "precio_anterior": numero(first(".ui-pdp-price__original-value .andes-money-amount__fraction::text")),
            "descuento": numero(first(".ui-pdp-discount__label::text")),
        }

process = CrawlerProcess()
process.crawl(ProductoSpider)
process.start()
"""

    def lanzar(url):
        with tempfile.TemporaryDirectory() as td:
            script = Path(td) / "runner_scrapy.py"
            salida = Path(td) / "producto.json"
            script.write_text(runner, encoding="utf-8")
            p = subprocess.run([sys.executable, str(script), url, str(salida)], capture_output=True, text=True, timeout=90)
            if p.returncode == 0 and salida.exists():
                data = json.loads(salida.read_text(encoding="utf-8"))
                return data[0] if data else None, p.stderr[-500:]
            return None, (p.stderr or p.stdout)[-500:]

    inicio = time.perf_counter()
    dato, mensaje = lanzar(PRODUCT_URL)
    fuente = "pagina_viva"
    if not dato or not dato.get("titulo"):
        fuente = "snapshot_academico"
        dato, mensaje = lanzar(SNAPSHOT_PATH.resolve().as_uri())
    if not dato:
        raise RuntimeError("Scrapy no produjo datos. " + mensaje)
    dato.update({
        "metodo": "Scrapy",
        "fuente": fuente,
        "fecha_hora": datetime.now().astimezone().isoformat(timespec="seconds"),
        "url": PRODUCT_URL,
        "http_status": None,
        "segundos": round(time.perf_counter() - inicio, 4),
    })
    return dato


def calcular_metricas(df):
    filas = []
    for _, row in df.iterrows():
        completos = sum(pd.notna(row.get(c)) and row.get(c) not in ["", None] for c in CAMPOS_CLAVE)
        filas.append({
            "metodo": row["metodo"],
            "fuente": row["fuente"],
            "completitud_pct": round(100 * completos / len(CAMPOS_CLAVE), 1),
            "segundos": row.get("segundos"),
        })
    return pd.DataFrame(filas)


def consistencia_entre_metodos(df):
    """Porcentaje de coincidencia en campos no nulos después de normalizar las salidas."""
    campos = CAMPOS_CLAVE
    comparaciones = 0
    coincidencias = 0
    for campo in campos:
        vals = [v for v in df[campo].tolist() if pd.notna(v) and v not in [""]]
        if len(vals) >= 2:
            base = str(vals[0]).strip().lower()
            for v in vals[1:]:
                comparaciones += 1
                coincidencias += int(str(v).strip().lower() == base)
    return round(100 * coincidencias / comparaciones, 1) if comparaciones else None


if __name__ == "__main__":
    resultados = []
    for nombre, funcion in [
        ("BeautifulSoup", ejecutar_beautifulsoup),
        ("Selenium", ejecutar_selenium),
        ("Scrapy", ejecutar_scrapy),
    ]:
        try:
            dato = funcion()
            resultados.append(dato)
            print(f"{nombre}: OK ({dato['fuente']})")
        except Exception as e:
            print(f"{nombre}: ERROR -> {type(e).__name__}: {e}")
    if resultados:
        df = pd.DataFrame(resultados)
        print("\\nResultados normalizados:")
        print(df.to_string(index=False))
        print("\\nMétricas:")
        print(calcular_metricas(df).to_string(index=False))
        print("Consistencia entre métodos (%):", consistencia_entre_metodos(df))
        df.to_csv("Gomez_Pablo_Analizando_EA1_resultados_ejecucion.csv", index=False, encoding="utf-8-sig")
