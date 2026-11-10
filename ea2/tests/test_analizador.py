"""Pruebas unitarias para validar el programa antes de cada integración."""

# Se importa unittest porque es el sistema de pruebas integrado en Python.
import sys
# Se importa Path para ubicar los directorios desde cualquier sistema.
from pathlib import Path
# Se importa tempfile para comprobar archivos sin ensuciar el proyecto.
import tempfile
# Se importa json para verificar la estructura generada.
import json
# Se importa unittest para agrupar y ejecutar los casos de validación.
import unittest

# Se identifica el directorio raíz del trabajo.
RAIZ = Path(__file__).resolve().parents[1]
# Se incorpora la carpeta src para importar el módulo sin instalar un paquete.
sys.path.insert(0, str(RAIZ / "src"))
# Se importan las funciones que se desean verificar.
from analizador import leer_datos_productos, validar_registro, guardar_resultados, obtener_numero, CAMPOS


# Cada método que empieza con test_ representa una prueba automatizada.
class PruebasArcherC64(unittest.TestCase):
    """Verifica datos, validaciones, manejo de errores y archivos finales."""

    # Se conserva la lectura original como punto de partida común.
    @classmethod
    def setUpClass(cls):
        # Se lee la captura académica que acompaña al proyecto.
        cls.html = (RAIZ / "datos" / "snapshot_ea1.html").read_text(encoding="utf-8")
        # Se ejecuta una única extracción para reutilizar el registro.
        cls.registro = leer_datos_productos(cls.html)

    def test_campos_completos(self):
        # Comprueba que ningún campo del modelo de datos quede sin valor.
        self.assertEqual(len(CAMPOS), 8)
        self.assertTrue(all(self.registro[campo] for campo in CAMPOS))

    def test_precio_corte_historico(self):
        # El valor fijo proviene del corte académico, no del mercado actual.
        self.assertEqual(self.registro["precio_cop"], 112285)
        self.assertEqual(self.registro["moneda"], "COP")

    def test_reputacion_y_ventas(self):
        # Se verifican las cifras de opiniones, ventas y calificación.
        self.assertEqual(self.registro["opiniones"], 1282)
        self.assertEqual(self.registro["ventas_minimas"], 1000)
        self.assertAlmostEqual(self.registro["calificacion"], 4.8)

    def test_normalizacion(self):
        # La función elimina puntos usados como separadores de miles.
        self.assertEqual(obtener_numero("1.282 opiniones"), 1282)
        self.assertEqual(obtener_numero("+1000 vendidos"), 1000)

    def test_html_invalido(self):
        # Un documento sin ficha Product debe producir un error explicativo.
        with self.assertRaises(ValueError):
            leer_datos_productos("<html><p>Sin datos de producto</p></html>")

    def test_validacion_moneda_incorrecta(self):
        # Una moneda distinta no puede pasar desapercibida.
        dato = {**self.registro, "moneda": "USD"}
        with self.assertRaises(ValueError):
            validar_registro(dato)

    def test_validacion_correcta(self):
        # Se confirma que los datos históricos aprobados superan la validación.
        self.assertTrue(validar_registro(self.registro))

    def test_generacion_artefactos(self):
        # Se usa una carpeta temporal, que se destruye al finalizar la prueba.
        with tempfile.TemporaryDirectory() as carpeta:
            # Se escriben el CSV, el JSON y el HTML de presentación.
            destino = guardar_resultados(self.registro, Path(carpeta))
            # Se comprueba la existencia de los tres productos esperados.
            for nombre in ("resultado.json", "resultado.csv", "index.html"):
                self.assertTrue((destino / nombre).is_file())
            # Se lee el JSON para comprobar la trazabilidad de la fuente.
            info = json.loads((destino / "resultado.json").read_text(encoding="utf-8"))
            self.assertEqual(info["fuente"], "snapshot_academico_EA1")
            # Se verifica que el HTML indica que los precios no son actuales.
            self.assertIn("no es una extracción en vivo", (destino / "index.html").read_text(encoding="utf-8"))


# Esta condición permite iniciar directamente el archivo de pruebas.
if __name__ == "__main__":
    # Se ejecuta unittest con mensajes detallados para aprendizaje.
    unittest.main(verbosity=2)
