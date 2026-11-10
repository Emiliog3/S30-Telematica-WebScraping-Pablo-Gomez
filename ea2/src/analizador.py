"""EA2. Extrae el registro de respaldo, lo valida y genera un sitio estático.

El programa NO visita Mercado Libre de forma automática. Se utiliza un HTML
académico congelado en la EA1, porque las pruebas del repositorio deben ser
reproducibles incluso cuando una plataforma cambia o bloquea sus páginas.
"""

# Se importa argparse para recibir opciones desde la terminal de VS Code.
import argparse
# Se importa csv para guardar una tabla que puede abrirse en Excel.
import csv
# Se importa json para recuperar datos estructurados y guardar resultados.
import json
# Se importa re para identificar cantidades dentro de textos comerciales.
import re
# Se importa datetime para registrar cuándo se genera el reporte.
from datetime import datetime, timezone
# Se importa escape para mostrar textos en HTML sin interpretarlos como etiquetas.
from html import escape
# Se importa Path para manejar las rutas de Windows y otros sistemas.
from pathlib import Path
# Se importa BeautifulSoup para interpretar el HTML sin ejecutar un navegador.
from bs4 import BeautifulSoup

# Se definen los nombres de los ocho campos obligatorios de la evidencia.
CAMPOS = ("titulo", "marca", "modelo", "precio_cop", "moneda", "calificacion", "opiniones", "ventas_minimas")
# Se conserva la fecha que identifica la observación comercial de la EA1.
FECHA_CORTE = "2026-10-25"
# Se conserva el vínculo de origen para que la información sea rastreable.
URL_PRODUCTO = "https://www.mercadolibre.com.co/tp-link-router-wifi-dual-band-gigabit-ac1200-archer-c64/p/MCO19592151"


def obtener_numero(valor):
    """Convierte formatos como '1.282 opiniones' y '+1000 vendidos' a enteros."""
    # Si no hay dato, se devuelve cero para advertir que no se obtuvo un número.
    if valor is None:
        return 0
    # Se conserva únicamente la secuencia numérica y sus separadores.
    texto = re.search(r"[\d.,]+", str(valor))
    # Se comprueba que la expresión regular realmente haya encontrado dígitos.
    if not texto:
        return 0
    # Se eliminan los separadores de miles usados en los conteos del sitio.
    return int(re.sub(r"[.,]", "", texto.group()))


def leer_datos_productos(html):
    """Recupera la ficha Product desde JSON-LD y completa la señal de ventas."""
    # BeautifulSoup convierte el texto HTML en un objeto que puede consultarse.
    pagina = BeautifulSoup(html, "html.parser")
    # Se revisan todos los scripts JSON-LD de la página, no solo el primero.
    for etiqueta in pagina.select('script[type="application/ld+json"]'):
        # Un script vacío no contiene datos útiles para este ejercicio.
        if not etiqueta.string:
            continue
        # Un JSON incorrecto no debe derrumbar todo el procesamiento.
        try:
            datos = json.loads(etiqueta.string)
        except json.JSONDecodeError:
            continue
        # Algunos sitios publican una lista de entidades en un mismo script.
        candidatos = datos if isinstance(datos, list) else [datos]
        # Se identifica una entidad de tipo Product dentro de la lista.
        for producto in candidatos:
            if not isinstance(producto, dict):
                continue
            # Una entidad puede declarar su tipo con una cadena o una lista.
            tipos = producto.get("@type", "")
            if "Product" not in (tipos if isinstance(tipos, list) else [tipos]):
                continue
            # Se toman los grupos de precios, marca y reputación del producto.
            oferta = producto.get("offers", {})
            marca = producto.get("brand", {})
            reputacion = producto.get("aggregateRating", {})
            # En casos sencillos, 'offers' puede contener una lista de ofertas.
            oferta = oferta[0] if isinstance(oferta, list) and oferta else oferta
            # Si la marca es un diccionario, interesa su nombre comercial.
            marca = marca.get("name", "") if isinstance(marca, dict) else marca
            # Si una sección falta, se utiliza un diccionario vacío.
            oferta = oferta if isinstance(oferta, dict) else {}
            reputacion = reputacion if isinstance(reputacion, dict) else {}
            # La cifra de ventas se reconoce por el texto visible, si está presente.
            ventas = pagina.select_one(".ui-pdp-subtitle")
            texto_ventas = ventas.get_text(" ", strip=True) if ventas else ""
            # Se busca expresamente una cifra seguida de la palabra 'vendidos'.
            coincidencia = re.search(r"([\d.,]+)\s*vendidos", texto_ventas, re.I)
            # La salida mantiene los mismos campos que se compararon en la EA1.
            return {
                "titulo": str(producto.get("name", "")).strip(),
                "marca": str(marca).strip(),
                "modelo": str(producto.get("model", "")).strip(),
                "precio_cop": obtener_numero(oferta.get("price")),
                "moneda": str(oferta.get("priceCurrency", "")).strip(),
                "calificacion": float(reputacion.get("ratingValue", 0)),
                "opiniones": obtener_numero(reputacion.get("reviewCount")),
                "ventas_minimas": obtener_numero(coincidencia.group(1)) if coincidencia else 0,
            }
    # Si no existe un Product, la entrada no corresponde al escenario previsto.
    raise ValueError("No se encontró una ficha Product válida dentro del HTML.")


def validar_registro(registro):
    """Comprueba que el dato procesado tenga una estructura coherente."""
    # Se detectan variables ausentes, no conocidas por el modelo de salida.
    faltantes = [campo for campo in CAMPOS if not registro.get(campo)]
    # El proyecto requiere los ocho campos definidos para ser consistente.
    if faltantes:
        raise ValueError("Faltan datos obligatorios: " + ", ".join(faltantes))
    # El caso se refiere a pesos colombianos, no a otra moneda.
    if registro["moneda"] != "COP":
        raise ValueError("Se esperaba un precio expresado en COP.")
    # Una calificación de producto no puede superar el máximo de cinco puntos.
    if not (0 <= registro["calificacion"] <= 5):
        raise ValueError("La calificación está fuera del rango de 0 a 5.")
    # Los valores de conteo y precio no deben ser negativos o iguales a cero.
    if any(registro[campo] <= 0 for campo in ("precio_cop", "opiniones", "ventas_minimas")):
        raise ValueError("Precio, opiniones y ventas deben ser positivos.")
    # Una validación satisfactoria se informa como verdadero.
    return True


def crear_html(registro, fecha_proceso):
    """Prepara el contenido web que posteriormente publicará GitHub Pages."""
    # Los atributos de texto se escapan para evitar etiquetas HTML no deseadas.
    titulo = escape(registro["titulo"])
    # Se usa un formato claro para cantidades en pesos colombianos.
    precio = f"{registro['precio_cop']:,.0f}".replace(",", ".")
    # Se convierte la cifra de opiniones a una representación legible.
    opiniones = f"{registro['opiniones']:,}".replace(",", ".")
    # Se elabora una página independiente que no necesita servidor ni JavaScript.
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Analítica Archer C64 · Evidencia 2</title>
<style>
:root{{--azul:#12324f;--amarillo:#f6bf36;--claro:#edf4f9;--texto:#21334a}}
*{{box-sizing:border-box}}body{{font-family:system-ui,Arial,sans-serif;margin:0;background:#f4f7fb;color:var(--texto)}}
header{{padding:48px max(20px,calc((100vw - 1050px)/2));background:var(--azul);color:white}}
header p{{max-width:720px;line-height:1.6}}.etiqueta{{color:var(--amarillo);letter-spacing:.15em;font-size:.8rem;font-weight:bold}}
main{{max-width:1050px;margin:30px auto;padding:0 20px 30px}}.tarjetas{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:16px}}
article{{background:white;padding:24px;border-radius:14px;border:1px solid #dce8f0;box-shadow:0 3px 8px #132d4010}}
article b{{font-size:1.5rem;color:var(--azul)}}article small{{display:block;color:#5b7185;margin-bottom:12px}}
.aviso{{margin-top:26px;padding:20px;background:#fff9e6;border-left:5px solid var(--amarillo);line-height:1.6}}
footer{{max-width:1050px;margin:10px auto 30px;padding:0 20px;font-size:.86rem;color:#4d6175}}
a{{color:#0d5c91}}
</style></head><body>
<header><div class="etiqueta">IU DIGITAL · INGENIERÍA DE SOFTWARE Y DATOS</div>
<h1>Extracción y análisis reproducible</h1><p>{titulo}</p></header>
<main><h2>Registro del estudio de caso</h2><section class="tarjetas">
<article><small>Precio de referencia</small><b>COP {precio}</b></article>
<article><small>Calificación</small><b>{registro['calificacion']:.1f} / 5</b></article>
<article><small>Opiniones</small><b>{opiniones}</b></article>
<article><small>Ventas registradas, al menos</small><b>{registro['ventas_minimas']:,}</b></article>
</section><div class="aviso"><strong>Alcance de los resultados.</strong> Se trata de un HTML de respaldo académico fechado el {FECHA_CORTE}; no es una extracción en vivo ni un precio vigente. La ejecución generó este reporte el {fecha_proceso} UTC. La automatización valida datos y crea una página que puede desplegarse mediante GitHub Actions.</div>
<p><strong>Marca y modelo:</strong> {escape(registro['marca'])} · {escape(registro['modelo'])}</p>
<p><a href="{URL_PRODUCTO}" rel="noopener noreferrer">Consultar la publicación de referencia</a></p>
</main><footer>Estudiante: Pablo Emilio Gómez Gómez · Asignatura: Programación para Análisis de Datos · Docente: Andrés Felipe Palacio</footer>
</body></html>"""


def guardar_resultados(registro, destino):
    """Escribe archivos JSON, CSV y HTML en un mismo directorio."""
    # Se crea la carpeta de salida si todavía no existe en el equipo.
    destino.mkdir(parents=True, exist_ok=True)
    # Se fija la zona horaria en UTC para no depender del equipo de ejecución.
    fecha = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    # Se adjuntan metadatos que distinguen fuente histórica y ejecución reciente.
    salida = {**registro, "fuente": "snapshot_academico_EA1", "corte": FECHA_CORTE, "url": URL_PRODUCTO, "generado_utc": fecha}
    # Se guarda un archivo JSON legible para otros programas.
    (destino / "resultado.json").write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    # Se abre un CSV compatible con los lectores habituales de tablas.
    with (destino / "resultado.csv").open("w", encoding="utf-8-sig", newline="") as archivo:
        # Se conserva un orden fijo de columnas para que los cambios sean rastreables.
        escritor = csv.DictWriter(archivo, fieldnames=salida.keys())
        # Se escribe la primera fila con los nombres de los campos.
        escritor.writeheader()
        # Se escribe el registro normalizado debajo de los encabezados.
        escritor.writerow(salida)
    # Se guarda el tablero para verlo desde VS Code o GitHub Pages.
    (destino / "index.html").write_text(crear_html(registro, fecha), encoding="utf-8")
    # Se informa dónde quedaron los archivos creados.
    return destino


def main():
    """Coordina la lectura, el control de calidad y la generación de resultados."""
    # Se crea el intérprete de argumentos para utilizar el programa en terminal.
    parser = argparse.ArgumentParser(description="Analiza el HTML académico del Archer C64.")
    # Esta opción permite escoger el archivo de entrada sin cambiar el código.
    parser.add_argument("--html", type=Path, default=Path("datos/snapshot_ea1.html"))
    # Esta opción permite seleccionar la carpeta de los resultados.
    parser.add_argument("--salida", type=Path, default=Path("sitio"))
    # Se leen las opciones escritas por el usuario o por GitHub Actions.
    args = parser.parse_args()
    # Se lee el HTML de referencia con codificación UTF-8.
    contenido = args.html.read_text(encoding="utf-8")
    # Se obtiene un diccionario con los atributos del producto.
    registro = leer_datos_productos(contenido)
    # Se comprueba la completitud y la plausibilidad del registro.
    validar_registro(registro)
    # Se preparan todos los archivos reproducibles de salida.
    guardar_resultados(registro, args.salida)
    # Se muestra un resumen corto para la terminal de VS Code.
    print(f"Análisis correcto: {len(CAMPOS)}/{len(CAMPOS)} campos. Archivos en: {args.salida}")


# Esta condición evita ejecutar el programa al importarlo desde las pruebas.
if __name__ == "__main__":
    # Se inicia el proceso únicamente cuando el archivo se llama como programa.
    main()
