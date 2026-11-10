# Lectura pedagógica del programa

**¿Qué hace el proyecto?** Lee un archivo HTML que conserva el caso investigado en la EA1, recupera ocho variables, verifica su coherencia y construye tres resultados que sirven para analizar y presentar la información. No descarga páginas comerciales nuevas.

## Bloque 1. Bibliotecas y constantes

Cada instrucción `import` pone a disposición una herramienta de Python. `argparse` permite escribir opciones en la terminal, `csv` guarda tablas, `json` organiza registros, `re` reconoce números dentro de texto, `datetime` registra el momento de ejecución, `escape` protege los textos mostrados en HTML, `Path` administra rutas y `BeautifulSoup` interpreta las etiquetas HTML. `CAMPOS` define los ocho datos que deben encontrarse; `FECHA_CORTE` y `URL_PRODUCTO` conservan la procedencia.

## Bloque 2. `obtener_numero`

`def obtener_numero(valor):` declara una función que recibe un contenido cualquiera. `if valor is None` reconoce valores faltantes. `re.search(...)` identifica una cifra, `if not texto` evita continuar cuando no se halló número y `re.sub(...)` elimina los puntos o las comas que separan miles. Finalmente, `int(...)` devuelve la cantidad como entero. Así, el texto `1.282 opiniones` se convierte en `1282`.

## Bloque 3. `leer_datos_productos`

`BeautifulSoup(html, "html.parser")` crea una estructura del documento. `select(...)` busca guiones JSON-LD con datos estructurados del producto; `for` recorre candidatos, `try/except` evita fallas por JSON incorrecto y `isinstance` comprueba los tipos de datos. Las instrucciones `get(...)` recuperan marca, precio y opiniones sin asumir que todas las secciones existen. `re.search` localiza el número de ventas. `return { ... }` devuelve un diccionario con los ocho campos comunes de la EA1. Si el documento no contiene un producto, `raise ValueError(...)` informa por qué no puede analizarse.

## Bloque 4. `validar_registro`

La expresión por comprensión `[campo for campo in CAMPOS if not registro.get(campo)]` elabora una lista de vacíos; `if faltantes` detecta datos incompletos, luego las condiciones sobre `moneda`, `calificacion` y cantidades evitan inconsistencias. `return True` significa que el registro superó las verificaciones planteadas.

## Bloque 5. `crear_html`

`escape` evita que el título o la marca alteren el diseño del reporte; las cadenas `f"..."` insertan datos reales en el texto y los formatos numéricos hacen más fácil la lectura de valores. El resultado es una página HTML autónoma que distingue una referencia histórica de una observación actual. El CSS usa una cuadrícula adaptable y tarjetas para visualizar las métricas.

## Bloque 6. `guardar_resultados`

`mkdir` crea el directorio, `datetime.now(timezone.utc)` registra la fecha actual de procesamiento, `json.dumps` guarda un registro estructurado, `csv.DictWriter` produce la tabla, `writeheader` agrega títulos de columna y `writerow` incorpora la observación. Finalmente se guarda `index.html` y se devuelve la ruta de salida. Esta separación facilita que el programa pueda probarse.

## Bloque 7. `main` y ejecución

`ArgumentParser` recibe `--html` y `--salida`; `parse_args` interpreta los parámetros escritos en la terminal; `read_text` abre el archivo, las funciones de lectura y validación preparan los datos y `guardar_resultados` elabora las evidencias. La condición `if __name__ == "__main__"` impide que el código se ejecute automáticamente cuando las pruebas lo importan.

## Bloque 8. Pruebas y DevOps

Cada función `test_...` representa un comportamiento que debe seguir cumpliéndose. `assertEqual`, `assertTrue` y `assertRaises` revisan cifras, condiciones y errores esperados. El flujo CI/CD instala Python y dependencias, ejecuta `unittest` y construye el sitio. Solo después de superar esa fase se intenta el despliegue en GitHub Pages. Los comentarios en los archivos `.py` explican las instrucciones de manera aún más cercana a cada línea.
