# S30 - Web Scraping en Mercado Libre Colombia

## Evidencia de aprendizaje 1 - Telemática

**Estudiante:** Pablo Emilio Gómez Gómez  
**Programa:** Ingeniería de Software y Datos  
**Institución:** Institución Universitaria Digital de Antioquia  
**Asignatura:** Telemática  
**Código:** PREICA2602B020056  
**Actividad:** S30 - Análisis y herramientas de extracción de datos

## Descripción

Este repositorio contiene la evidencia técnica desarrollada para comparar tres herramientas de web scraping en Python:

- BeautifulSoup
- Selenium
- Scrapy

El caso de estudio corresponde a la publicación del router TP-Link Archer C64 AC1200 en Mercado Libre Colombia.

## Publicación analizada

https://www.mercadolibre.com.co/tp-link-router-wifi-dual-band-gigabit-ac1200-archer-c64/p/MCO19592151

## Objetivo

Evaluar el desempeño de BeautifulSoup, Selenium y Scrapy en la extracción de información pública del router TP-Link Archer C64 AC1200 publicado en Mercado Libre Colombia, mediante métricas de completitud, consistencia, tiempo de ejecución y trazabilidad.

## Archivos principales

- Gomez_Pablo_Analizando_EA1.ipynb: notebook principal ejecutado y guardado con sus salidas.
- Gomez_Pablo_Analizando_EA1.py: versión complementaria del código fuente.
- requirements.txt: librerías necesarias.
- data/snapshot_academico.html: captura HTML utilizada para la prueba reproducible.
- data/resultados_ejecucion.csv: resultados obtenidos durante la ejecución.
- data/metricas_ejecucion.csv: métricas de la comparación.
- docs/Gomez_Pablo_Analizando_EA1.pdf: informe académico final.

## Metodología

Cada herramienta intenta trabajar sobre la publicación viva.

Cuando la respuesta obtenida no contiene información suficiente para comparar los ocho campos definidos, el ejercicio utiliza un snapshot académico local. La fuente queda registrada explícitamente y no se presenta el respaldo como si hubiera sido extraído de la publicación viva.

## Resultados observados

En la consulta viva se observaron diferencias entre herramientas.

BeautifulSoup y Selenium recuperaron información limitada, mientras Scrapy obtuvo siete de los ocho campos definidos.

En la prueba reproducible con el snapshot académico se obtuvo:

- BeautifulSoup: 100 % de completitud.
- Selenium: 100 % de completitud.
- Scrapy: 87,5 % de completitud.
- Consistencia entre valores comparables: 100 %.

Los tiempos de ejecución dependen del equipo y del entorno utilizado, por lo que no deben generalizarse como características permanentes de las bibliotecas.

## Reproducibilidad

Las dependencias pueden instalarse mediante:

    pip install -r requirements.txt

Posteriormente puede abrirse el archivo:

    Gomez_Pablo_Analizando_EA1.ipynb

en Jupyter Notebook o Visual Studio Code y ejecutar sus celdas en orden.

## Acceso responsable

La práctica tiene alcance exclusivamente académico.

El código no intenta:

- evadir CAPTCHA;
- superar autenticaciones;
- rotar identidades;
- evitar bloqueos;
- realizar rastreo masivo;
- alterar la plataforma consultada.

La prueba se limita al estudio de una publicación de comercio electrónico y utiliza una fuente local de respaldo para conservar reproducibilidad.

## Fecha de ejecución

26 de octubre de 2026.

## Autor

Pablo Emilio Gómez Gómez  
Ingeniería de Software y Datos  
Institución Universitaria Digital de Antioquia
