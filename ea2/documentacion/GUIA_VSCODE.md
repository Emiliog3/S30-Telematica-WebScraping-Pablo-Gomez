# Guía paso a paso para trabajar en Visual Studio Code

## 1. Abrir el proyecto

1. Descomprima el ZIP en la carpeta `G:\Mi unidad\15. ING. DE SOFTWARE Y DATOS\06. PROGRAMACIÓN PARA ANÁLISIS DE DATOS\ACTIVIDADES\ACTIVIDAD 02`.
2. En Visual Studio Code seleccione **Archivo > Abrir carpeta** y abra `EA2_Pablo_Gomez`.
3. Compruebe que aparecen `src`, `tests`, `datos`, `sitio` y `documentacion`.
4. Abra **Terminal > Nuevo terminal**. Si aparece `PS ...`, está usando PowerShell.

## 2. Preparar Python

Escriba las siguientes órdenes, una a una. Cada una tiene una finalidad distinta.

```powershell
py --version
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell restringe la activación, no cambie permisos globales. Use directamente:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## 3. Ejecutar pruebas automatizadas

```powershell
python -m unittest discover -s tests -v
```

Lo esperado es que muestre **Ran 8 tests** y **OK**. Si alguna prueba falla, guarde la captura del error y no entregue el proyecto como validado.

## 4. Generar el tablero de resultados

```powershell
python src/analizador.py --html datos/snapshot_ea1.html --salida sitio
```

Esto crea o actualiza tres archivos: `sitio/index.html`, `sitio/resultado.csv` y `sitio/resultado.json`. Abra el HTML con el navegador para ver las tarjetas del tablero. El contenido representa una **captura histórica**, no una consulta nueva a Mercado Libre.

## 5. Verificar Git y GitHub

Desde Visual Studio Code, abra una terminal dentro del repositorio descargado desde GitHub:

```powershell
git --version
git status
git branch -a
git log --oneline -5
```

`git status` indica cambios pendientes, `git branch -a` enseña las ramas y `git log` presenta los commits. Para conservar el trabajo original, el proyecto de EA2 se añade como la carpeta `ea2` dentro del repositorio de EA1.

## 6. Pruebas de la automatización en GitHub

1. Abra el repositorio `Emiliog3/S30-Telematica-WebScraping-Pablo-Gomez`.
2. Entre a la pestaña **Actions** y busque el flujo **EA2 - pruebas y despliegue**.
3. Abra la ejecución de la rama principal. Compruebe si las pruebas finalizaron correctamente.
4. Si el paso de Pages solicita habilitación, abra **Settings > Pages > Build and deployment**, seleccione **GitHub Actions** y vuelva a ejecutar el flujo. Algunas cuentas o repositorios necesitan habilitar esta opción manualmente.
5. Cuando el despliegue figure como correcto, abra la URL real mostrada por GitHub en el resultado del job y compruebe que el tablero carga. No suponga que está publicado solo porque el archivo YAML existe.

## 7. Capturas recomendadas para la evidencia

Conserve capturas donde se vea: (a) carpeta abierta en VS Code, (b) resultado `OK` de las pruebas, (c) ejecución del script, (d) archivos HTML/CSV/JSON, (e) commits y ramas, (f) pull request y su fusión, (g) el flujo de GitHub Actions y, si se activa Pages, (h) la dirección del tablero en el navegador. Añádalas al informe final si el docente solicita evidencias visuales.

## 8. Entrega en el aula

Adjunte el PDF `Gomez_Pablo_EA2_Programacion_Analisis_Datos.pdf` y, si corresponde, el ZIP del código fuente o la URL del repositorio. El docente permite archivo o dirección web. No entregue una dirección Pages si su despliegue no está efectivamente activo.
