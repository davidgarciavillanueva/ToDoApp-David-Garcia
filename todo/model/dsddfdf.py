


#data beaseeee

import sqlite3
import datetime

class DatabaseManager:
    def __init__(self, db_path="qr_historial.db"):
        self.db_path = db_path
        self._crear_tabla()

    def _crear_tabla(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historial (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contenido TEXT,
                    tipo TEXT,
                    fecha TEXT
                )
            """)
            conn.commit()

    def guardar_historial(self, contenido: str, tipo: str):
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO historial (contenido, tipo, fecha) VALUES (?, ?, ?)",
                           (contenido, tipo, fecha))
            conn.commit()

    def consultar_historial(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM historial")
            return cursor.fetchall()

    def eliminar_registro(self, registro_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM historial WHERE id = ?", (registro_id,))
            conn.commit()



#historialllll
class QRHistory:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def buscar_qr(self, texto: str):
        todos = self.db.consultar_historial()
        return [registro for registro in todos if texto.lower() in registro[1].lower()]

    def filtrar_qr_por_tipo(self, tipo: str):
        todos = self.db.consultar_historial()
        return [registro for registro in todos if tipo.lower() == registro[2].lower()]

    def limpiar_historial(self):
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM historial")
            conn.commit()


#exportador
import pyperclip

class QRExporter:
    def __init__(self, imagen_qr):
        self.imagen = imagen_qr

    def guardar_como_png(self, ruta: str):
        self.imagen.save(ruta, format='PNG')

    def guardar_como_jpg(self, ruta: str):
        self.imagen.convert("RGB").save(ruta, format='JPEG')

    def copiar_al_portapapeles(self):
        # Nota: copiar una imagen al portapapeles no es trivial en Python puro
        # Esto es una solución simulada solo para copiar el contenido QR


#validador

class QRValidator:
    def __init__(self):
        self.longitud_maxima = 1000

    def validar_tipo_dato(self, dato: str):
        if dato.startswith("http"):
            return "URL"
        elif "WIFI:" in dato:
            return "WiFi"
        elif "BEGIN:VCARD" in dato:
            return "Contacto"
        else:
            return "Texto"

    def verificar_longitud(self, dato: str):
        return len(dato) <= self.longitud_maxima


#interfa grafica
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import ImageTk, Image

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Códigos QR")
        self.root.geometry("600x500")

        self._crear_widgets()

    def _crear_widgets(self):
        # Tabs (Pestañas)
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(expand=1, fill='both')

        # Pestaña Generador
        self.tab_generador = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_generador, text="Generar QR")
        self._crear_tab_generador()

        # Pestaña Lector
        self.tab_lector = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_lector, text="Leer QR")
        self._crear_tab_lector()

        # Pestaña Historial
        self.tab_historial = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_historial, text="Historial")
        self._crear_tab_historial()

    def _crear_tab_generador(self):
        tk.Label(self.tab_generador, text="Contenido:").pack(pady=5)
        self.contenido_entry = tk.Entry(self.tab_generador, width=50)
        self.contenido_entry.pack(pady=5)

        tk.Button(self.tab_generador, text="Generar QR", command=self._generar_qr).pack(pady=10)

        self.qr_label = tk.Label(self.tab_generador)
        self.qr_label.pack(pady=10)

    def _crear_tab_lector(self):
        tk.Button(self.tab_lector, text="Seleccionar Imagen", command=self._leer_desde_imagen).pack(pady=10)
        self.resultado_lector = tk.Label(self.tab_lector, text="Resultado:", wraplength=500)
        self.resultado_lector.pack(pady=10)

    def _crear_tab_historial(self):
        self.lista_historial = tk.Listbox(self.tab_historial, width=80, height=15)
        self.lista_historial.pack(pady=10)
        tk.Button(self.tab_historial, text="Actualizar", command=self._actualizar_historial).pack()

    def _generar_qr(self):
        from QRGenerator import QRGenerator  # o usa directamente si ya está definido en el mismo archivo
        from DatabaseManager import DatabaseManager
        from QRValidator import QRValidator

        contenido = self.contenido_entry.get()
        validador = QRValidator()

        if not contenido:
            messagebox.showerror("Error", "El contenido no puede estar vacío.")
            return

        if not validador.verificar_longitud(contenido):
            messagebox.showerror("Error", "El contenido excede la longitud permitida.")
            return

        tipo = validador.validar_tipo_dato(contenido)

        generador = QRGenerator(contenido)
        img = generador.generar_qr()
        generador.guardar_qr()

        db = DatabaseManager()
        db.guardar_historial(contenido, tipo)

        img_tk = ImageTk.PhotoImage(img)
        self.qr_label.configure(image=img_tk)
        self.qr_label.image = img_tk

    def _leer_desde_imagen(self):
        from QRReader import QRReader
        from DatabaseManager import DatabaseManager
        from QRValidator import QRValidator

        ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
        if ruta:
            lector = QRReader(ruta)
            resultado = lector.leer_qr_desde_imagen(ruta)

            if not resultado.startswith("Error") and "No se pudo" not in resultado:
                validador = QRValidator()
                tipo = validador.validar_tipo_dato(resultado)
                db = DatabaseManager()
                db.guardar_historial(resultado, tipo)

            self.resultado_lector.config(text=f"Resultado: {resultado}")

    def _actualizar_historial(self):
        from DatabaseManager import DatabaseManager

        self.lista_historial.delete(0, tk.END)
        db = DatabaseManager()
        datos = db.consultar_historial()

        for registro in datos:
            self.lista_historial.insert(tk.END, f"{registro[3]} | {registro[2]} | {registro[1]}")
