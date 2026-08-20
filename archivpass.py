import os
import shutil
import sys
import threading
import time
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import ctypes
import customtkinter as ctk
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURACIÓN DE APARIENCIA CUSTOMTKINTER ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('miempresa.backupapp.elite.1.0')
except Exception:
    pass

def obtener_ruta_recurso(nombre_archivo):
    """ Obtiene la ruta absoluta, funciona en desarrollo y con PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, nombre_archivo)
    
    directorio_base = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.path.abspath(".")
    return os.path.join(directorio_base, nombre_archivo)

class AppBackupCorporativoElite(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURACIÓN DE TAMAÑO Y PANTALLA ---
        self.title("Backup Corporativo")
        
        ancho_ventana = 460
        alto_ventana = 640

        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()

        pos_x = int((ancho_pantalla / 2) - (ancho_ventana / 2))
        pos_y = int((alto_pantalla / 2) - (alto_ventana / 2)) - 35

        self.geometry(f"{ancho_ventana}x{alto_ventana}+{pos_x}+{pos_y}")
        self.minsize(450, 600)

        # --- PALETA DE COLORES "CYBER-CORPORATE ELEGANCE" ---
        self.COLOR_BG = "#080C0A"
        self.COLOR_CARD = "#0F1813"
        self.COLOR_CARD_BORDER = "#1A2C22"
        self.COLOR_GOLD = "#E5A800"
        self.COLOR_GOLD_BRIGHT = "#FFC000"
        self.COLOR_TEXT = "#E0E6E2"
        self.COLOR_TEXT_MUTED = "#7A8C82"
        self.COLOR_PANTONE_349C = "#1E4D33"
        self.COLOR_PANTONE_HOVER = "#276342"
        self.COLOR_RED = "#D32F2F"

        self.configure(fg_color=self.COLOR_BG)

        # --- CARGAR ÍCONO ---
# --- CARGAR ÍCONO (CORREGIDO PARA CUSTOMTKINTER) ---
        def aplicar_icono():
            try:
                ruta_ico = obtener_ruta_recurso("icono.ico")
                ruta_png = obtener_ruta_recurso("icono.png")

                if os.path.exists(ruta_ico):
                    self.iconbitmap(ruta_ico)
                    self.wm_iconbitmap(ruta_ico)
                elif os.path.exists(ruta_png):
                    try:
                        from PIL import Image, ImageTk
                        img = Image.open(ruta_png)
                        self.img_icono = ImageTk.PhotoImage(img)
                    except ImportError:
                        self.img_icono = tk.PhotoImage(file=ruta_png)
                    
                    self.iconphoto(True, self.img_icono)
            except Exception as e:
                print(f"No se pudo cargar el ícono: {e}")

        # Se ejecuta 200ms después para evitar que CustomTkinter borre el ícono al renderizar
        self.after(200, aplicar_icono)

        # OPTIMIZACIÓN: Exclusiones como Conjuntos (Set) O(1)
        self.CARPETAS_IGNORADAS = {
            'temp', 'tmp', 'cache', 'caches', 'gpucache', 'code cache', 
            'crashdumps', 'inetcache', 'webcache', '$recycle.bin', 
            'system volume information', 'node_modules', '__pycache__'
        }

        self.ARCHIVOS_IGNORADOS = {
            'desktop.ini', 'thumbs.db', 'ntuser.dat', 'usrclass.dat', 
            'parent.lock', 'swapfile.sys', 'hiberfil.sys', 'pagefile.sys'
        }

        self.EXTENSIONES_IGNORADAS = {'.tmp', '.dmp', '.bak', '.crdownload', '.partial', '.lock'}

        # Variables de control y multithreading
        self.lista_rutas_origen = []
        self.ruta_destino = tk.StringVar()
        self.modo_existente = tk.StringVar(value="omitir")
        self.organizar_por_tipo = tk.BooleanVar(value=True)
        self.cancelar_proceso = False
        self.lock = threading.Lock()
        self.ultima_actualizacion_ui = 0
        
        # OPTIMIZACIÓN: Mapeo de Categorías en Conjuntos (Set) O(1)
        self.EXTENSIONES_OFFICE_WORD = {'.doc', '.docx', '.odt'}
        self.EXTENSIONES_OFFICE_EXCEL = {'.xls', '.xlsx', '.csv', '.ods'}
        self.EXTENSIONES_OFFICE_PPT = {'.ppt', '.pptx', '.odp'}

        self.EXTENSIONES_PDF = {'.pdf', '.epub'}
        self.EXTENSIONES_TXT = {'.txt', '.rtf', '.log'}

        self.EXTENSIONES_ADOBE_PHOTOSHOP = {'.psd', '.psb'}
        self.EXTENSIONES_ADOBE_ILLUSTRATOR = {'.ai', '.ait', '.eps'}
        self.EXTENSIONES_ADOBE_INDESIGN = {'.indd', '.indt', '.idml'}
        self.EXTENSIONES_ADOBE_ACROBAT = {'.pdf'}
        self.EXTENSIONES_ADOBE_PREMIERE = {'.prproj'}
        self.EXTENSIONES_ADOBE_AFTER_EFFECTS = {'.aep', '.aet'}
        self.EXTENSIONES_ADOBE_AUDITION = {'.sesx'}
        self.EXTENSIONES_ADOBE_LIGHTROOM = {'.lrcat', '.dng'}
        self.EXTENSIONES_ADOBE_XD = {'.xd'}
        self.EXTENSIONES_ADOBE_ANIMATE = {'.fla', '.xfl'}

        self.EXTENSIONES_AUTODESK_AUTOCAD = {'.dwg', '.dxf', '.dwt', '.dwf'}

        self.EXTENSIONES_EJECUTABLES = {'.exe', '.msi', '.bat', '.cmd', '.iso', '.ps1'}
        self.EXTENSIONES_ACCESOS = {'.lnk', '.url'}
        self.EXTENSIONES_CORREO = {'.pst', '.ost', '.eml', '.msg', '.oft', '.mbox'}
        self.EXTENSIONES_COMPRIMIDOS = {'.zip', '.rar', '.7z', '.tar', '.gz'}

        # Métricas
        self.exitos = []
        self.errores = []
        self.omitidos = []
        self.ya_existian = 0
        self.bytes_transferidos = 0

        self.crear_interfaz()

    def es_archivo_ignorado(self, nombre_archivo):
        nombre_lower = nombre_archivo.lower()
        _, ext = os.path.splitext(nombre_lower)
        
        if nombre_lower in self.ARCHIVOS_IGNORADOS or nombre_lower.startswith('ntuser.dat'):
            return True
        if ext in self.EXTENSIONES_IGNORADAS:
            return True
        return False

    def crear_tarjeta(self, parent):
        return ctk.CTkFrame(
            parent,
            fg_color=self.COLOR_CARD,
            border_color=self.COLOR_CARD_BORDER,
            border_width=1,
            corner_radius=10
        )

    def crear_interfaz(self):
        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(side="bottom", fill="x", pady=15, padx=20)

        self.btn_iniciar = ctk.CTkButton(
            self.frame_acciones, 
            text="▶   INICIAR BACKUP", 
            fg_color=self.COLOR_GOLD, 
            hover_color=self.COLOR_GOLD_BRIGHT, 
            text_color="#000000",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=42,
            corner_radius=10,
            command=self.comenzar_hilo
        )
        self.btn_iniciar.pack(fill="x")

        self.btn_cancelar = ctk.CTkButton(
            self.frame_acciones, 
            text="✖   CANCELAR BACKUP", 
            fg_color=self.COLOR_RED, 
            hover_color="#B71C1C", 
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            corner_radius=10,
            command=self.solicitar_cancelacion
        )

        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=self.COLOR_BG,
            scrollbar_button_color="#1A2C22",
            scrollbar_button_hover_color=self.COLOR_PANTONE_349C
        )
        self.scroll_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        # --- SECCIÓN 1: ORIGEN ---
        card_origen = self.crear_tarjeta(self.scroll_frame)
        card_origen.pack(pady=6, padx=15, fill="x")

        lbl_sec_origen = ctk.CTkLabel(
            card_origen, 
            text="📁   Carpetas / Discos de Origen", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
            text_color=self.COLOR_GOLD
        )
        lbl_sec_origen.pack(anchor="w", padx=14, pady=(10, 6))

        frame_listbox = ctk.CTkFrame(card_origen, fg_color="transparent")
        frame_listbox.pack(fill="x", padx=14, pady=(0, 6))

        self.lb_origenes = tk.Listbox(
            frame_listbox, height=3, font=("Consolas", 9),
            bg="#060B08", fg=self.COLOR_TEXT, bd=0, 
            highlightthickness=1, highlightbackground=self.COLOR_CARD_BORDER, 
            selectbackground=self.COLOR_PANTONE_349C, selectforeground="#FFFFFF"
        )
        self.lb_origenes.pack(fill="both", expand=True)

        frame_btns_origen = ctk.CTkFrame(card_origen, fg_color="transparent")
        frame_btns_origen.pack(fill="x", padx=14, pady=(0, 10))

        btn_add = ctk.CTkButton(frame_btns_origen, text="+ Añadir", fg_color=self.COLOR_PANTONE_349C, hover_color=self.COLOR_PANTONE_HOVER, width=80, height=28, corner_radius=6, command=self.agregar_origen)
        btn_add.pack(side="left", padx=(0, 6))

        btn_del = ctk.CTkButton(frame_btns_origen, text="- Quitar", fg_color="#18261E", hover_color="#22382C", width=80, height=28, corner_radius=6, command=self.quitar_origen_seleccionado)
        btn_del.pack(side="left", padx=6)

        btn_clr = ctk.CTkButton(frame_btns_origen, text="Limpiar Todo", fg_color="#18261E", hover_color="#22382C", width=95, height=28, corner_radius=6, command=self.limpiar_origenes)
        btn_clr.pack(side="left", padx=6)

        # --- SECCIÓN 2: DESTINO ---
        card_destino = self.crear_tarjeta(self.scroll_frame)
        card_destino.pack(pady=6, padx=15, fill="x")

        lbl_sec_destino = ctk.CTkLabel(
            card_destino, 
            text="📁   Ruta de Destino", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
            text_color=self.COLOR_GOLD
        )
        lbl_sec_destino.pack(anchor="w", padx=14, pady=(10, 6))

        frame_dest_input = ctk.CTkFrame(card_destino, fg_color="transparent")
        frame_dest_input.pack(fill="x", padx=14, pady=(0, 12))

        txt_destino = ctk.CTkEntry(
            frame_dest_input, 
            textvariable=self.ruta_destino, 
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#060B08", 
            border_color=self.COLOR_CARD_BORDER,
            text_color=self.COLOR_TEXT,
            height=32
        )
        txt_destino.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_exam = ctk.CTkButton(
            frame_dest_input, 
            text="Examinar...", 
            fg_color=self.COLOR_PANTONE_349C, 
            hover_color=self.COLOR_PANTONE_HOVER,
            text_color=self.COLOR_TEXT,
            width=90, 
            height=32, 
            corner_radius=6,
            command=self.seleccionar_destino
        )
        btn_exam.pack(side="right")

        # --- SECCIÓN 3: OPCIONES ---
        card_config = self.crear_tarjeta(self.scroll_frame)
        card_config.pack(pady=6, padx=15, fill="x")

        chk_organizar = ctk.CTkCheckBox(
            card_config, 
            text="Clasificar por Categorías, Programas y Años", 
            variable=self.organizar_por_tipo, 
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
            text_color=self.COLOR_GOLD,
            fg_color=self.COLOR_PANTONE_349C,
            hover_color=self.COLOR_PANTONE_HOVER,
            checkmark_color="#FFFFFF",
            corner_radius=4
        )
        chk_organizar.pack(anchor="w", padx=14, pady=(12, 2))

        lbl_info_duplicados = ctk.CTkLabel(
            card_config, 
            text="Protección activa: Duplicados se renombran automáticamente", 
            font=ctk.CTkFont(family="Segoe UI", size=10, slant="italic"), 
            text_color=self.COLOR_TEXT_MUTED
        )
        lbl_info_duplicados.pack(anchor="w", padx=42, pady=(0, 12))

        # --- SECCIÓN 4: ESTADO Y PROGRESO ---
        frame_progreso = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_progreso.pack(pady=8, padx=15, fill="x")

        self.lbl_estado = ctk.CTkLabel(
            frame_progreso, 
            text="Estado: En espera de configuración...", 
            text_color="#25D366", 
            font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic")
        )
        self.lbl_estado.pack(anchor="w", pady=(0, 4))

        self.barra_progreso = ctk.CTkProgressBar(
            frame_progreso, 
            orientation="horizontal", 
            progress_color=self.COLOR_GOLD,
            fg_color="#141F18",
            height=8,
            corner_radius=4
        )
        self.barra_progreso.pack(fill="x")
        self.barra_progreso.set(0)

        # --- SECCIÓN 5: MÉTRICAS ---
        card_metricas = self.crear_tarjeta(self.scroll_frame)
        card_metricas.pack(pady=6, padx=15, fill="x")

        lbl_sec_metricas = ctk.CTkLabel(
            card_metricas, 
            text="📊   Métricas de la Sesión", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
            text_color=self.COLOR_GOLD
        )
        lbl_sec_metricas.pack(anchor="w", padx=14, pady=(10, 8))

        frame_grid_m = ctk.CTkFrame(card_metricas, fg_color="transparent")
        frame_grid_m.pack(fill="x", padx=14, pady=(0, 12))
        frame_grid_m.grid_columnconfigure((0, 1), weight=1)

        f_exito = ctk.CTkFrame(frame_grid_m, fg_color="#0E2A1B", border_color="#1B5433", border_width=1, corner_radius=6)
        f_exito.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)
        self.lbl_m_exito = ctk.CTkLabel(f_exito, text="Copiados: 0", font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color="#22C55E")
        self.lbl_m_exito.pack(pady=6)

        f_renombrados = ctk.CTkFrame(frame_grid_m, fg_color="#0B2136", border_color="#15426B", border_width=1, corner_radius=6)
        f_renombrados.grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=4)
        self.lbl_m_renombrados = ctk.CTkLabel(f_renombrados, text="Renombrados: 0", font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color="#3B82F6")
        self.lbl_m_renombrados.pack(pady=6)

        f_errores = ctk.CTkFrame(frame_grid_m, fg_color="#2A0E11", border_color="#541B21", border_width=1, corner_radius=6)
        f_errores.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=4)
        self.lbl_m_errores = ctk.CTkLabel(f_errores, text="Errores: 0", font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color="#EF4444")
        self.lbl_m_errores.pack(pady=6)

        f_peso = ctk.CTkFrame(frame_grid_m, fg_color="#141F18", border_color="#23382B", border_width=1, corner_radius=6)
        f_peso.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=4)
        self.lbl_m_peso = ctk.CTkLabel(f_peso, text="Volumen: 0 Bytes", font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color=self.COLOR_TEXT)
        self.lbl_m_peso.pack(pady=6)

        # --- SECCIÓN 6: LOG EN TIEMPO REAL ---
        card_log = self.crear_tarjeta(self.scroll_frame)
        card_log.pack(pady=6, padx=15, fill="x")

        lbl_sec_log = ctk.CTkLabel(
            card_log, 
            text="📜   Registro de Actividad en Tiempo Real", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
            text_color=self.COLOR_GOLD
        )
        lbl_sec_log.pack(anchor="w", padx=14, pady=(10, 6))

        self.txt_log = ctk.CTkTextbox(
            card_log, 
            height=120, 
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color="#060B08", 
            text_color=self.COLOR_TEXT,
            border_color=self.COLOR_CARD_BORDER,
            border_width=1,
            corner_radius=6,
            wrap="word"
        )
        self.txt_log.pack(fill="x", expand=True, padx=14, pady=(0, 12))

        self.txt_log._textbox.tag_config("INFO", foreground=self.COLOR_TEXT_MUTED)
        self.txt_log._textbox.tag_config("EXITO", foreground="#22C55E")
        self.txt_log._textbox.tag_config("OMITIDO", foreground=self.COLOR_GOLD_BRIGHT)
        self.txt_log._textbox.tag_config("RENOMBRADO", foreground="#3B82F6")
        self.txt_log._textbox.tag_config("ERROR", foreground="#EF4444")

    def log_mensaje(self, texto, categoria="INFO"):
        """ Agrega log de forma segura """
        self.txt_log.configure(state="normal")
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        self.txt_log.insert(tk.END, f"[{hora}] {texto}\n", categoria)
        self.txt_log.see(tk.END)
        self.txt_log.configure(state="disabled")

    def limpiar_log(self):
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.configure(state="disabled")

    def determinar_ruta_clasificada(self, ruta_origen_archivo, nombre_archivo):
        _, ext = os.path.splitext(nombre_archivo)
        ext = ext.lower()

        try:
            timestamp = os.path.getmtime(ruta_origen_archivo)
            anio = str(datetime.datetime.fromtimestamp(timestamp).year)
        except Exception:
            anio = "Sin_Anio"

        if ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico'}:
            return os.path.join("Multimedia", "Imagenes", anio)
        elif ext in {'.mp4', '.avi', '.mkv', '.mov', '.mp3', '.wav', '.aac', '.flac'}:
            return os.path.join("Multimedia", "Videos y Audio", anio)

        elif ext in self.EXTENSIONES_OFFICE_WORD:
            return os.path.join("Archivos Office", "Word", anio)
        elif ext in self.EXTENSIONES_OFFICE_EXCEL:
            return os.path.join("Archivos Office", "Excel", anio)
        elif ext in self.EXTENSIONES_OFFICE_PPT:
            return os.path.join("Archivos Office", "PowerPoint", anio)
        
        elif ext in self.EXTENSIONES_PDF:
            return os.path.join("PDF y texto","PDF y Lectura", anio)
        elif ext in self.EXTENSIONES_TXT:
            return os.path.join("PDF y texto", "Texto Plano", anio)

        elif ext in self.EXTENSIONES_ADOBE_ACROBAT:
            return os.path.join("Archivos Adobe", "Acrobat", anio)
        elif ext in self.EXTENSIONES_ADOBE_PHOTOSHOP:
            return os.path.join("Archivos Adobe", "Photoshop", anio)
        elif ext in self.EXTENSIONES_ADOBE_ILLUSTRATOR:
            return os.path.join("Archivos Adobe", "Illustrator", anio)
        elif ext in self.EXTENSIONES_ADOBE_INDESIGN:
            return os.path.join("Archivos Adobe", "InDesign", anio)
        elif ext in self.EXTENSIONES_ADOBE_PREMIERE:
            return os.path.join("Archivos Adobe", "Premiere Pro", anio)
        elif ext in self.EXTENSIONES_ADOBE_AFTER_EFFECTS:
            return os.path.join("Archivos Adobe", "After Effects", anio)
        elif ext in self.EXTENSIONES_ADOBE_AUDITION:
            return os.path.join("Archivos Adobe", "Audition", anio)
        elif ext in self.EXTENSIONES_ADOBE_LIGHTROOM:
            return os.path.join("Archivos Adobe", "Lightroom", anio)
        elif ext in self.EXTENSIONES_ADOBE_XD:
            return os.path.join("Archivos Adobe", "Adobe XD", anio)
        elif ext in self.EXTENSIONES_ADOBE_ANIMATE:
            return os.path.join("Archivos Adobe", "Animate", anio)

        elif ext in self.EXTENSIONES_AUTODESK_AUTOCAD:
            return os.path.join("Archivos Autodesk", "AutoCAD", anio)

        elif ext in self.EXTENSIONES_EJECUTABLES:
            return os.path.join("Ejecutables e Instaladores", anio)
        elif ext in self.EXTENSIONES_ACCESOS:
            return os.path.join("Aplicaciones e Accesos", anio)
        elif ext in self.EXTENSIONES_CORREO:
            return os.path.join("Correos y Datos Outlook", anio)
        elif ext in self.EXTENSIONES_COMPRIMIDOS:
            return os.path.join("Archivos Comprimidos", anio)
        else:
            return os.path.join("Otros Archivos", anio)

    def agregar_origen(self):
        ruta = filedialog.askdirectory(title="Seleccionar Carpeta/Unidad de Origen")
        if ruta and ruta not in self.lista_rutas_origen:
            self.lista_rutas_origen.append(ruta)
            self.lb_origenes.insert(tk.END, ruta)

    def quitar_origen_seleccionado(self):
        seleccion = self.lb_origenes.curselection()
        if seleccion:
            index = seleccion[0]
            self.lb_origenes.delete(index)
            self.lista_rutas_origen.pop(index)

    def limpiar_origenes(self):
        self.lb_origenes.delete(0, tk.END)
        self.lista_rutas_origen.clear()

    def seleccionar_destino(self):
        ruta = filedialog.askdirectory(title="Seleccionar Destino")
        if ruta: self.ruta_destino.set(ruta)

    def solicitar_cancelacion(self):
        self.cancelar_proceso = True
        self.lbl_estado.configure(text="Cancelando... Generando reporte parcial.", text_color=self.COLOR_RED)
        self.log_mensaje("⚠️ Solicitud de cancelación detectada por el usuario...", "ERROR")
        self.btn_cancelar.configure(state="disabled", fg_color="#1c382b")

    def comenzar_hilo(self):
        self.cancelar_proceso = False
        hilo = threading.Thread(target=self.proceso_copiado, daemon=True)
        hilo.start()

    def formatear_peso(self, bytes_size):
        for unidad in ['Bytes', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0: return f"{bytes_size:.2f} {unidad}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"

    def normalizar_ruta_larga(self, ruta):
        ruta_abs = os.path.abspath(ruta)
        if not ruta_abs.startswith("\\\\?\\"):
            if ruta_abs.startswith("\\\\"): return "\\\\?\\UNC\\" + ruta_abs[2:]
            return "\\\\?\\" + ruta_abs
        return ruta_abs

    def resetear_interfaz(self):
        self.limpiar_origenes()
        self.ruta_destino.set("")
        self.barra_progreso.set(0)
        self.lbl_estado.configure(text="Estado: En espera de configuración...", text_color=self.COLOR_TEXT_MUTED)
        
        self.lbl_m_exito.configure(text="Copiados: 0")
        self.lbl_m_renombrados.configure(text="Renombrados: 0")
        self.lbl_m_errores.configure(text="Errores: 0")
        self.lbl_m_peso.configure(text="Volumen: 0 Bytes")

        self.btn_cancelar.pack_forget()
        self.btn_cancelar.configure(state="normal", fg_color=self.COLOR_RED)
        self.btn_iniciar.pack(fill="x")

    def actualizar_ui_progreso(self, procesados, total, nombre_archivo):
        """ OPTIMIZACIÓN: Refresco controlado de la interfaz gráfica """
        progreso = procesados / total
        self.barra_progreso.set(progreso)
        nombre_visible = nombre_archivo if len(nombre_archivo) <= 35 else nombre_archivo[:32] + "..."
        self.lbl_estado.configure(text=f"⚡ Copiando: {nombre_visible}", text_color=self.COLOR_GOLD_BRIGHT)
        self.lbl_m_exito.configure(text=f"Copiados: {len(self.exitos)}")
        self.lbl_m_renombrados.configure(text=f"Renombrados: {self.ya_existian}")
        self.lbl_m_errores.configure(text=f"Errores: {len(self.errores)}")
        self.lbl_m_peso.configure(text=f"Volumen: {self.formatear_peso(self.bytes_transferidos)}")

    def proceso_copiado(self):
        destino_raw = self.ruta_destino.get()
        debe_organizar = self.organizar_por_tipo.get()

        if not self.lista_rutas_origen:
            self.lbl_estado.configure(text="⚠️ Error: Añade al menos una carpeta de origen.", text_color=self.COLOR_RED)
            return

        if not destino_raw:
            self.lbl_estado.configure(text="⚠️ Error: Selecciona la ruta de destino.", text_color=self.COLOR_RED)
            return

        self.limpiar_log()
        self.log_mensaje("=== INICIANDO SESIÓN DE RESPALDO CORPORATIVO ===", "INFO")
        self.exitos.clear()
        self.errores.clear()
        self.omitidos.clear()
        self.ya_existian = 0
        self.bytes_transferidos = 0

        self.btn_iniciar.pack_forget()
        self.btn_cancelar.pack(fill="x")
        self.lbl_estado.configure(text="🔍 Escaneando origen y planificando tareas...", text_color=self.COLOR_GOLD)

        try:
            destino = self.normalizar_ruta_larga(destino_raw)

            # --- OPTIMIZACIÓN 1: UN SOLO PASO DE ESCANEO Y CONTRUCCIÓN DE TAREAS ---
            tareas = []
            for origen_item in self.lista_rutas_origen:
                origen_norm = self.normalizar_ruta_larga(origen_item)
                for raiz, dirs, archivos in os.walk(origen_norm):
                    dirs[:] = [d for d in dirs if d.lower() not in self.CARPETAS_IGNORADAS]
                    ruta_relativa = os.path.relpath(raiz, origen_norm)

                    for archivo in archivos:
                        if self.es_archivo_ignorado(archivo):
                            continue

                        ruta_archivo_origen = os.path.join(raiz, archivo)

                        if debe_organizar:
                            subestructura = self.determinar_ruta_clasificada(ruta_archivo_origen, archivo)
                            carpeta_destino_actual = os.path.join(destino, subestructura)
                        else:
                            if ruta_relativa == ".":
                                carpeta_destino_actual = destino
                            else:
                                carpeta_destino_actual = os.path.join(destino, ruta_relativa)

                        tareas.append((ruta_archivo_origen, carpeta_destino_actual, archivo))

            total_archivos = len(tareas)

            if total_archivos == 0:
                self.lbl_estado.configure(text="⚠️ Los orígenes seleccionados no contienen archivos válidos.", text_color=self.COLOR_RED)
                self.log_mensaje("⚠️ No se encontraron archivos válidos para respaldar.", "ERROR")
                self.resetear_interfaz()
                return

            self.log_mensaje(f"Análisis completado: {total_archivos} archivo(s) detectado(s). Iniciando transferencia...", "INFO")
            
            archivos_procesados = 0
            destinos_ocupados = set()

            # --- TRABAJADOR MULTIHILO PARA COPIADO PARALELO ---
            def copiar_tarea(tarea):
                nonlocal archivos_procesados
                if self.cancelar_proceso:
                    return

                ruta_origen, carpeta_destino, archivo = tarea

                if not os.path.exists(carpeta_destino):
                    try: os.makedirs(carpeta_destino, exist_ok=True)
                    except Exception: pass

                # Control de nombres duplicados de forma segura ante hilos concurrentes
                with self.lock:
                    base_nombre, ext = os.path.splitext(archivo)
                    contador = 0
                    fue_renombrado = False
                    ruta_archivo_destino = os.path.join(carpeta_destino, archivo)

                    while os.path.exists(ruta_archivo_destino) or ruta_archivo_destino in destinos_ocupados:
                        contador += 1
                        nuevo_nombre = f"{base_nombre}({contador}){ext}"
                        ruta_archivo_destino = os.path.join(carpeta_destino, nuevo_nombre)
                        fue_renombrado = True

                    destinos_ocupados.add(ruta_archivo_destino)

                try:
                    peso_bytes = os.path.getsize(ruta_origen)
                    peso_legible = self.formatear_peso(peso_bytes)
                except Exception:
                    peso_bytes = 0
                    peso_legible = "Desconocido"

                nombre_archivo_final = os.path.basename(ruta_archivo_destino)

                try:
                    # Copiado rápido en hilo
                    shutil.copy2(ruta_origen, ruta_archivo_destino)

                    with self.lock:
                        self.exitos.append((nombre_archivo_final, peso_legible))
                        self.bytes_transferidos += peso_bytes
                        if fue_renombrado:
                            self.ya_existian += 1

                        archivos_procesados += 1
                        ahora = time.time()

                        # OPTIMIZACIÓN 2: THROTTLING (Solo refresca UI máximo cada 80ms o al terminar)
                        if ahora - self.ultima_actualizacion_ui > 0.08 or archivos_procesados == total_archivos:
                            self.ultima_actualizacion_ui = ahora
                            self.actualizar_ui_progreso(archivos_procesados, total_archivos, nombre_archivo_final)

                        if fue_renombrado:
                            self.log_mensaje(f"[RENOMBRADO] {archivo} ➔ {nombre_archivo_final} ({peso_legible})", "RENOMBRADO")
                        else:
                            self.log_mensaje(f"[COPIADO] {nombre_archivo_final} ({peso_legible})", "EXITO")

                except Exception as e:
                    motivo = str(e).split("]")[-1].strip()
                    with self.lock:
                        self.errores.append((nombre_archivo_final, peso_legible, motivo))
                        archivos_procesados += 1
                        self.log_mensaje(f"[ERROR] {nombre_archivo_final}: {motivo}", "ERROR")

            # --- OPTIMIZACIÓN 3: EJECUCIÓN CON POOL DE HILOS (PARALELISMO MULTIHILO) ---
            max_hilos = min(16, (os.cpu_count() or 4) * 2)
            with ThreadPoolExecutor(max_workers=max_hilos) as executor:
                executor.map(copiar_tarea, tareas)

            if self.cancelar_proceso:
                self.log_mensaje("=== PROCESO CANCELADO POR EL USUARIO ===", "ERROR")
            else:
                self.lbl_estado.configure(text="Estado: Backup completado con éxito.", text_color="#25D366")
                self.log_mensaje("=== RESPALDO COMPLETADO EXITOSAMENTE ===", "INFO")

            # Generar reporte de texto
            ruta_txt_reporte = os.path.join(destino_raw, "reporte_transferencia.txt")
            try:
                with open(ruta_txt_reporte, "w", encoding="utf-8") as f:
                    f.write("==================================================\n")
                    f.write("     REPORTE DETALLADO DE AUDITORÍA Y BACKUP      \n")
                    f.write("==================================================\n\n")
                    f.write(f"Fecha de Ejecución: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("Orígenes Respaldados:\n")
                    for org in self.lista_rutas_origen: f.write(f" - {org}\n")
                    f.write(f"\nRuta Destino: {destino_raw}\n")
                    f.write(f"Estado Final: {'CANCELADO POR USUARIO' if self.cancelar_proceso else 'COMPLETADO'}\n\n")
                    f.write("RESUMEN DE MÉTRICAS:\n")
                    f.write(f"• Archivos respaldados con éxito: {len(self.exitos)}\n")
                    f.write(f"• Archivos renombrados:           {self.ya_existian}\n")
                    f.write(f"• Archivos con error:            {len(self.errores)}\n")
                    f.write(f"• Volumen total copiado:         {self.formatear_peso(self.bytes_transferidos)}\n\n")
            except Exception as e:
                print(f"Error informe: {e}")

            self.mostrar_ventana_finalizacion()

        except Exception as ex:
            self.lbl_estado.configure(text=f"❌ Error grave: {ex}", text_color=self.COLOR_RED)
            self.log_mensaje(f"❌ Error crítico en la ejecución: {ex}", "ERROR")
            self.resetear_interfaz()

    def mostrar_ventana_finalizacion(self):
        if self.cancelar_proceso:
            messagebox.showwarning("Proceso Detenido", "El respaldo se canceló por intervención del usuario.")
        else:
            peso_total = self.formatear_peso(self.bytes_transferidos)
            resumen_msg = (
                "🎉 ¡BACKUP COMPLETO Y CLASIFICADO CON ÉXITO!\n\n"
                f"• Archivos procesados: {len(self.exitos)}\n"
                f"• Archivos renombrados: {self.ya_existian}\n"
                f"• Volumen copiado: {peso_total}\n\n"
                "La interfaz se limpiará automáticamente al dar Aceptar."
            )
            messagebox.showinfo("Proceso Finalizado", resumen_msg)
            
        self.resetear_interfaz()

if __name__ == "__main__":
    app = AppBackupCorporativoElite()
    app.mainloop()