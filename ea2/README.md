# Evidencia de aprendizaje 2 · Programación para Análisis de Datos

**Institución Universitaria Digital de Antioquia (IU Digital)**  
**Estudiante:** Pablo Emilio Gómez Gómez  
**Docente:** Andrés Felipe Palacio  
**Curso:** PREICA2602B020048  
**Caso:** TP-Link Archer C64 de la evidencia 1

Este proyecto continúa el análisis del router que fue presentado en la EA1. En lugar de afirmar que existe extracción en vivo cuando una página comercial cambia, utiliza una **muestra HTML reconstruida a partir de los valores académicos documentados el 25 de octubre de 2026**. De esta manera se pueden automatizar las pruebas, comparar resultados y demostrar control de versiones de forma transparente.

## Contenido

- `src/analizador.py`: lectura HTML con BeautifulSoup, validación y exportación.
- `tests/test_analizador.py`: ocho pruebas unitarias con `unittest`.
- `datos/snapshot_ea1.html`: muestra local, reproducible y sin red.
- `sitio/`: tablero HTML, JSON y CSV generados.
- `documentacion/GUIA_VSCODE.md`: instrucciones sencillas para ejecutar el proyecto.
- `.github/workflows/ea2-ci-cd.yml`: pruebas automáticas y despliegue a GitHub Pages.

## Ejecutar desde la carpeta del proyecto

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py src/analizador.py --html datos/snapshot_ea1.html --salida sitio
```

Se puede abrir `sitio/index.html` haciendo doble clic, o desde VS Code usando Live Server. El CSV permite revisar los resultados en Excel.

## Decisiones técnicas

Se trabajó con un solo producto para conservar el objetivo de la EA1. El análisis se centra en un proceso **CI/CD verificable**: cada commit o pull request ejecuta pruebas y construye el tablero. En la rama `main`, GitHub Actions intenta publicar el directorio `ea2/sitio/` en GitHub Pages, siempre que Pages esté activado en el repositorio. El script no evade CAPTCHA, autenticación ni límites de la plataforma.

**Importante:** si el proyecto se encuentra dentro del repositorio original, el comando debe ejecutarse primero con `cd ea2`. No se deben interpretar los resultados congelados como precios actuales.

## Referencias breves

GitHub. (s. f.). *Understanding GitHub Actions*. https://docs.github.com/en/actions  
GitHub. (s. f.). *About pull requests*. https://docs.github.com/en/pull-requests  
Python Software Foundation. (s. f.). *unittest — Unit testing framework*. https://docs.python.org/3/library/unittest.html  
Richardson, L. (s. f.). *Beautiful Soup documentation*. https://www.crummy.com/software/BeautifulSoup/bs4/doc/
