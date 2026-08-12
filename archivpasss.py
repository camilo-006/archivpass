import os
import shutil
import sys
import threading
import datetime
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
import ctypes

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('miempresa.backupapp.elite.1.0')
except Exception:
    pass

def obtener_ruta_recurso(nombre_archivo):
    """ Obtiene la ruta absoluta del recurso, funciona para dev y para PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, nombre_archivo)
    return os.path.join(os.path.abspath("."), nombre_archivo)

class AppBackupCorporativoElite(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Backup Corporativo")
        self.geometry("700x860")
        self.resizable(False, False)

        # --- CARGAR ÍCONO COMPATIBLE CON .EXE Y .PY ---
        try:
            ruta_icono = obtener_ruta_recurso("icono.png")
            self.img_icono = tk.PhotoImage(file=ruta_icono)
            self.iconphoto(True, self.img_icono)
        except Exception as e:
            print(f"No se pudo cargar el ícono: {e}")
        
        # --- PALETA DE COLORES PERSONALIZADA ---
        self.COLOR_BG = "#121714"            # Fondo general ultra oscuro
        self.COLOR_CARD = "#0f281e"          # Tarjetas en verde bosque profundo
        self.COLOR_PANTONE_349C = "#046a38"  # Verde Pantone 349 C oficial
        self.COLOR_PANTONE_HOVER = "#0b8247" # Verde derivado más vivo
        self.COLOR_GOLD = "#d4af37"          # Dorado metálico elegante
        self.COLOR_GOLD_BRIGHT = "#ffd700"   # Dorado brillante (Hover/Destacados)
        self.COLOR_TEXT = "#ffffff"          # Blanco puro para texto
        self.COLOR_TEXT_MUTED = "#a0b2a6"    # Verde grisáceo suave para textos secundarios
        self.COLOR_RED = "#d9534f"           # Rojo suave para cancelar/errores

        self.configure(bg=self.COLOR_BG)

        # Estilo para ProgressBar
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Modern.Horizontal.TProgressbar", 
                        thickness=14, 
                        troughcolor=self.COLOR_CARD, 
                        background=self.COLOR_GOLD, 
                        bordercolor=self.COLOR_CARD, 
                        lightcolor=self.COLOR_GOLD, 
                        darkcolor=self.COLOR_GOLD)

        # Variables de control
        self.lista_rutas_origen = []
        self.ruta_destino = tk.StringVar()
        self.modo_existente = tk.StringVar(value="omitir")
        self.organizar_por_tipo = tk.BooleanVar(value=True)
        self.cancelar_proceso = False
        
        # Mapeo de Categorías
        self.EXTENSIONES_OFFICE_WORD = ['.doc', '.docx', '.odt']
        self.EXTENSIONES_OFFICE_EXCEL = ['.xls', '.xlsx', '.csv', '.ods']
        self.EXTENSIONES_OFFICE_PPT = ['.ppt', '.pptx', '.odp']
        self.EXTENSIONES_OFFICE_PDF = ['.pdf', '.epub']
        self.EXTENSIONES_OFFICE_TXT = ['.txt', '.rtf', '.log']

        self.EXTENSIONES_EJECUTABLES = ['.exe', '.msi', '.bat', '.cmd', '.iso', '.ps1']
        self.EXTENSIONES_ACCESOS = ['.lnk', '.url']
        self.EXTENSIONES_CORREO = ['.pst', '.ost', '.eml', '.msg', '.oft', '.mbox']
        self.EXTENSIONES_COMPRIMIDOS = ['.zip', '.rar', '.7z', '.tar', '.gz']

        # Métricas
        self.exitos = []
        self.errores = []
        self.omitidos = []
        self.ya_existian = 0
        self.bytes_transferidos = 0

        self.crear_interfaz()

    def crear_boton_estilizado(self, parent, text, bg, fg, hover_bg, hover_fg, command, width=12, height=1):
        btn = tk.Button(parent, text=text, bg=bg, fg=fg, font=("Segoe UI Semibold", 10, "bold"),
                        activebackground=hover_bg, activeforeground=hover_fg,
                        bd=0, relief="flat", cursor="hand2", width=width, height=height, command=command)
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg, fg=hover_fg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg, fg=fg))
        return btn

    def crear_interfaz(self):
        # --- HEADER ---
        frame_header = tk.Frame(self, bg=self.COLOR_BG)
        frame_header.pack(pady=(12, 8), fill="x", padx=25)

        lbl_titulo = tk.Label(frame_header, text=" Backup Corporativo", 
                              font=("Segoe UI Semibold", 18, "bold"), bg=self.COLOR_BG, fg=self.COLOR_GOLD)
        lbl_titulo.pack(anchor="w")

        lbl_sub = tk.Label(frame_header, text="Sistema de respaldo inteligente con organización automática", 
                           font=("Segoe UI", 10), bg=self.COLOR_BG, fg=self.COLOR_TEXT_MUTED)
        lbl_sub.pack(anchor="w")

        # --- SECCIÓN ORIGEN ---
        card_origen = tk.Frame(self, bg=self.COLOR_CARD, padx=15, pady=10, highlightthickness=1, highlightbackground=self.COLOR_PANTONE_349C)
        card_origen.pack(pady=4, padx=25, fill="x")

        lbl_sec_origen = tk.Label(card_origen, text="📁 Carpetas / Discos de Origen", 
                                  font=("Segoe UI Semibold", 11, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_GOLD)
        lbl_sec_origen.pack(anchor="w", pady=(0, 6))

        frame_listbox = tk.Frame(card_origen, bg=self.COLOR_CARD)
        frame_listbox.pack(fill="x")

        self.lb_origenes = tk.Listbox(frame_listbox, height=3, font=("Consolas", 9),
                                      bg="#080c09", fg=self.COLOR_TEXT, bd=0, 
                                      highlightthickness=1, highlightbackground=self.COLOR_PANTONE_349C, selectbackground=self.COLOR_PANTONE_349C)
        self.lb_origenes.pack(side="left", fill="both", expand=True, padx=(0, 10))

        scroll_lb = tk.Scrollbar(frame_listbox, command=self.lb_origenes.yview)
        scroll_lb.pack(side="right", fill="y")
        self.lb_origenes.config(yscrollcommand=scroll_lb.set)

        frame_btns_origen = tk.Frame(card_origen, bg=self.COLOR_CARD)
        frame_btns_origen.pack(fill="x", pady=(6, 0))

        self.crear_boton_estilizado(frame_btns_origen, "+ Añadir", self.COLOR_PANTONE_349C, self.COLOR_TEXT, self.COLOR_PANTONE_HOVER, self.COLOR_TEXT, self.agregar_origen, width=10).pack(side="left", padx=(0, 5))
        self.crear_boton_estilizado(frame_btns_origen, "- Quitar", "#1c382b", self.COLOR_TEXT, "#2a4f3d", self.COLOR_TEXT, self.quitar_origen_seleccionado, width=10).pack(side="left", padx=5)
        self.crear_boton_estilizado(frame_btns_origen, "Limpiar Todo", "#1c382b", self.COLOR_TEXT, "#2a4f3d", self.COLOR_TEXT, self.limpiar_origenes, width=12).pack(side="left", padx=5)

        # --- SECCIÓN DESTINO ---
        card_destino = tk.Frame(self, bg=self.COLOR_CARD, padx=15, pady=10, highlightthickness=1, highlightbackground=self.COLOR_PANTONE_349C)
        card_destino.pack(pady=4, padx=25, fill="x")

        lbl_sec_destino = tk.Label(card_destino, text="🎯 Ruta de Destino", 
                                   font=("Segoe UI Semibold", 11, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_GOLD)
        lbl_sec_destino.pack(anchor="w", pady=(0, 6))

        frame_dest_input = tk.Frame(card_destino, bg=self.COLOR_CARD)
        frame_dest_input.pack(fill="x")

        txt_destino = tk.Entry(frame_dest_input, textvariable=self.ruta_destino, font=("Segoe UI", 10),
                               bg="#080c09", fg=self.COLOR_TEXT, bd=0, highlightthickness=1, highlightbackground=self.COLOR_PANTONE_349C, insertbackground="white")
        txt_destino.pack(side="left", fill="x", expand=True, ipady=3, padx=(0, 10))

        self.crear_boton_estilizado(frame_dest_input, "Examinar...", self.COLOR_PANTONE_349C, self.COLOR_TEXT, self.COLOR_PANTONE_HOVER, self.COLOR_TEXT, self.seleccionar_destino, width=12).pack(side="right")

        # --- SECCIÓN OPCIONES ---
        card_config = tk.Frame(self, bg=self.COLOR_CARD, padx=15, pady=8, highlightthickness=1, highlightbackground=self.COLOR_PANTONE_349C)
        card_config.pack(pady=4, padx=25, fill="x")

        chk_organizar = tk.Checkbutton(card_config, text="✨ Clasificar por Categorías, Programas y Años", 
                                        variable=self.organizar_por_tipo, font=("Segoe UI Semibold", 10, "bold"), 
                                        bg=self.COLOR_CARD, fg=self.COLOR_GOLD, selectcolor="#080c09", activebackground=self.COLOR_CARD, activeforeground=self.COLOR_GOLD)
        chk_organizar.pack(anchor="w", pady=(0, 4))

        frame_rb = tk.Frame(card_config, bg=self.COLOR_CARD)
        frame_rb.pack(anchor="w")

        tk.Label(frame_rb, text="Duplicados:", font=("Segoe UI Semibold", 10, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_TEXT_MUTED).pack(side="left", padx=(0, 10))
        tk.Radiobutton(frame_rb, text="Omitir", variable=self.modo_existente, value="omitir", bg=self.COLOR_CARD, fg=self.COLOR_TEXT, selectcolor="#080c09", activebackground=self.COLOR_CARD, activeforeground=self.COLOR_TEXT, font=("Segoe UI", 10)).pack(side="left", padx=5)
        tk.Radiobutton(frame_rb, text="Reemplazar", variable=self.modo_existente, value="reemplazar", bg=self.COLOR_CARD, fg=self.COLOR_TEXT, selectcolor="#080c09", activebackground=self.COLOR_CARD, activeforeground=self.COLOR_TEXT, font=("Segoe UI", 10)).pack(side="left", padx=5)

        # --- PROGRESO Y ESTADO ---
        frame_progreso = tk.Frame(self, bg=self.COLOR_BG)
        frame_progreso.pack(pady=6, padx=25, fill="x")

        self.lbl_estado = tk.Label(frame_progreso, text="Estado: En espera de configuración...", fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_BG, font=("Segoe UI", 10, "italic"))
        self.lbl_estado.pack(anchor="w", pady=(0, 2))

        self.barra_progreso = ttk.Progressbar(frame_progreso, orient="horizontal", style="Modern.Horizontal.TProgressbar", mode="determinate")
        self.barra_progreso.pack(fill="x")

        # --- PANEL DE MÉTRICAS EN TIEMPO REAL ---
        card_metricas = tk.Frame(self, bg=self.COLOR_CARD, padx=15, pady=8, highlightthickness=1, highlightbackground=self.COLOR_PANTONE_349C)
        card_metricas.pack(pady=4, padx=25, fill="x")

        lbl_sec_metricas = tk.Label(card_metricas, text="📊 Métricas de la Sesión", 
                                     font=("Segoe UI Semibold", 11, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_GOLD)
        lbl_sec_metricas.pack(anchor="w", pady=(0, 4))

        frame_grid_m = tk.Frame(card_metricas, bg=self.COLOR_CARD)
        frame_grid_m.pack(fill="x")

        self.lbl_m_exito = tk.Label(frame_grid_m, text="Copiados: 0", font=("Consolas", 10, "bold"), bg=self.COLOR_CARD, fg="#4CAF50")
        self.lbl_m_exito.grid(row=0, column=0, sticky="w", padx=(0, 15))

        self.lbl_m_omitidos = tk.Label(frame_grid_m, text="Omitidos: 0", font=("Consolas", 10, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_GOLD_BRIGHT)
        self.lbl_m_omitidos.grid(row=0, column=1, sticky="w", padx=15)

        self.lbl_m_errores = tk.Label(frame_grid_m, text="Errores: 0", font=("Consolas", 10, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_RED)
        self.lbl_m_errores.grid(row=0, column=2, sticky="w", padx=15)

        self.lbl_m_peso = tk.Label(frame_grid_m, text="Volumen: 0 Bytes", font=("Consolas", 10, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_TEXT)
        self.lbl_m_peso.grid(row=0, column=3, sticky="w", padx=(15, 0))

        # --- CUADRO DE REPORTE EN TIEMPO REAL (LOG) ---
        card_log = tk.Frame(self, bg=self.COLOR_CARD, padx=15, pady=8, highlightthickness=1, highlightbackground=self.COLOR_PANTONE_349C)
        card_log.pack(pady=4, padx=25, fill="x")

        lbl_sec_log = tk.Label(card_log, text="📜 Registro de Actividad en Tiempo Real", 
                               font=("Segoe UI Semibold", 11, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_GOLD)
        lbl_sec_log.pack(anchor="w", pady=(0, 4))

        self.txt_log = scrolledtext.ScrolledText(
            card_log, height=6, font=("Consolas", 8),
            bg="#080c09", fg=self.COLOR_TEXT, bd=0,
            highlightthickness=1, highlightbackground=self.COLOR_PANTONE_349C,
            state="disabled", wrap="word"
        )
        self.txt_log.pack(fill="x", expand=True)

        # Configuración de colores para el log
        self.txt_log.tag_config("INFO", foreground=self.COLOR_TEXT_MUTED)
        self.txt_log.tag_config("EXITO", foreground="#4CAF50")
        self.txt_log.tag_config("OMITIDO", foreground=self.COLOR_GOLD_BRIGHT)
        self.txt_log.tag_config("RENOMBRADO", foreground="#4fc3f7")
        self.txt_log.tag_config("ERROR", foreground=self.COLOR_RED)

        # --- BOTONES DE ACCIÓN ---
        self.frame_acciones = tk.Frame(self, bg=self.COLOR_BG)
        self.frame_acciones.pack(pady=10)

        self.btn_iniciar = self.crear_boton_estilizado(
            self.frame_acciones, "▶ Iniciar Backup", 
            self.COLOR_GOLD, "#080c09", 
            self.COLOR_GOLD_BRIGHT, "#080c09", 
            self.comenzar_hilo, width=18, height=2
        )
        self.btn_iniciar.pack()

        self.btn_cancelar = tk.Button(
            self.frame_acciones, text="✖ Cancelar Backup", 
            bg=self.COLOR_RED, fg=self.COLOR_TEXT, 
            font=("Segoe UI Semibold", 10, "bold"), bd=0, relief="flat", 
            cursor="hand2", width=18, height=2, command=self.solicitar_cancelacion
        )

    def log_mensaje(self, texto, categoria="INFO"):
        """ Agrega un mensaje formateado con color al cuadro de reporte """
        self.txt_log.config(state="normal")
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        self.txt_log.insert(tk.END, f"[{hora}] {texto}\n", categoria)
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")

    def limpiar_log(self):
        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.config(state="disabled")

    def determinar_ruta_clasificada(self, ruta_origen_archivo, nombre_archivo):
        _, ext = os.path.splitext(nombre_archivo)
        ext = ext.lower()

        try:
            timestamp = os.path.getmtime(ruta_origen_archivo)
            anio = str(datetime.datetime.fromtimestamp(timestamp).year)
        except Exception:
            anio = "Sin_Anio"

        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico']:
            return os.path.join("Multimedia", "Imagenes", anio)
        elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.mp3', '.wav', '.aac', '.flac']:
            return os.path.join("Multimedia", "Videos y Audio", anio)

        elif ext in self.EXTENSIONES_OFFICE_WORD:
            return os.path.join("Archivos Office", "Word", anio)
        elif ext in self.EXTENSIONES_OFFICE_EXCEL:
            return os.path.join("Archivos Office", "Excel", anio)
        elif ext in self.EXTENSIONES_OFFICE_PPT:
            return os.path.join("Archivos Office", "PowerPoint", anio)
        elif ext in self.EXTENSIONES_OFFICE_PDF:
            return os.path.join("Archivos Office", "PDF y Lectura", anio)
        elif ext in self.EXTENSIONES_OFFICE_TXT:
            return os.path.join("Archivos Office", "Texto Plano", anio)

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
        self.lbl_estado.config(text="Cancelando... Generando reporte parcial.", fg=self.COLOR_RED)
        self.log_mensaje("⚠️ Solicitud de cancelación detectada por el usuario...", "ERROR")
        self.btn_cancelar.config(state="disabled", bg="#1c382b", fg=self.COLOR_TEXT_MUTED)

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
        self.barra_progreso["value"] = 0
        self.lbl_estado.config(text="Estado: En espera de configuración...", fg=self.COLOR_TEXT_MUTED)
        
        # Reset de métricas visuales
        self.lbl_m_exito.config(text="Copiados: 0")
        self.lbl_m_omitidos.config(text="Omitidos: 0")
        self.lbl_m_errores.config(text="Errores: 0")
        self.lbl_m_peso.config(text="Volumen: 0 Bytes")

        # Restaurar botones (Ocultar Cancelar, Mostrar Iniciar)
        self.btn_cancelar.pack_forget()
        self.btn_cancelar.config(state="normal", bg=self.COLOR_RED, fg=self.COLOR_TEXT)
        self.btn_iniciar.pack()

    def proceso_copiado(self):
        destino_raw = self.ruta_destino.get()
        modo = self.modo_existente.get()
        debe_organizar = self.organizar_por_tipo.get()

        if not self.lista_rutas_origen:
            self.lbl_estado.config(text="⚠️ Error: Añade al menos una carpeta de origen.", fg=self.COLOR_RED)
            return

        if not destino_raw:
            self.lbl_estado.config(text="⚠️ Error: Selecciona la ruta de destino.", fg=self.COLOR_RED)
            return

        self.limpiar_log()
        self.log_mensaje("=== INICIANDO SESIÓN DE RESPALDO CORPORATIVO ===", "INFO")
        self.exitos.clear()
        self.errores.clear()
        self.omitidos.clear()
        self.ya_existian = 0
        self.bytes_transferidos = 0

        # Ocultar Iniciar y Mostrar Cancelar
        self.btn_iniciar.pack_forget()
        self.btn_cancelar.pack()
        self.lbl_estado.config(text="🔍 Analizando y contabilizando archivos...", fg=self.COLOR_GOLD)

        try:
            destino = self.normalizar_ruta_larga(destino_raw)

            total_archivos = 0
            for origen_item in self.lista_rutas_origen:
                origen_norm = self.normalizar_ruta_larga(origen_item)
                for _, _, archivos in os.walk(origen_norm):
                    total_archivos += len(archivos)

            if total_archivos == 0:
                self.lbl_estado.config(text="⚠️ Los orígenes seleccionados están vacíos.", fg=self.COLOR_RED)
                self.log_mensaje("⚠️ No se encontraron archivos en las rutas seleccionadas.", "ERROR")
                self.resetear_interfaz()
                return

            self.log_mensaje(f"Análisis completado: {total_archivos} archivo(s) detectado(s).", "INFO")
            archivos_procesados = 0

            for origen_item in self.lista_rutas_origen:
                if self.cancelar_proceso: break

                origen_norm = self.normalizar_ruta_larga(origen_item)
                
                for raiz, _, archivos in os.walk(origen_norm):
                    if self.cancelar_proceso: break
                    ruta_relativa = os.path.relpath(raiz, origen_norm)

                    for archivo in archivos:
                        if self.cancelar_proceso: break
                        ruta_archivo_origen = os.path.join(raiz, archivo)

                        if debe_organizar:
                            subestructura = self.determinar_ruta_clasificada(ruta_archivo_origen, archivo)
                            carpeta_destino_actual = os.path.join(destino, subestructura)
                        else:
                            if ruta_relativa == ".":
                                carpeta_destino_actual = destino
                            else:
                                carpeta_destino_actual = os.path.join(destino, ruta_relativa)

                        if not os.path.exists(carpeta_destino_actual):
                            try: os.makedirs(carpeta_destino_actual)
                            except Exception: pass

                        ruta_archivo_destino = os.path.join(carpeta_destino_actual, archivo)

                        archivos_procesados += 1
                        self.barra_progreso["value"] = (archivos_procesados / total_archivos) * 100

                        try:
                            peso_bytes = os.path.getsize(ruta_archivo_origen)
                            peso_legible = self.formatear_peso(peso_bytes)
                        except Exception:
                            peso_bytes = 0
                            peso_legible = "Desconocido"

                        # --- ANÁLISIS DE DUPLICADOS Y CONTADOR CORRELATIVO ---
                        base_nombre, ext = os.path.splitext(archivo)
                        contador = 0
                        es_duplicado_real = False
                        fue_renombrado = False

                        while os.path.exists(ruta_archivo_destino):
                            try:
                                size_origen = peso_bytes
                                mtime_origen = os.path.getmtime(ruta_archivo_origen)
                                
                                size_destino = os.path.getsize(ruta_archivo_destino)
                                mtime_destino = os.path.getmtime(ruta_archivo_destino)

                                # Comprobar si tamaño y fecha coinciden (margen < 1 seg)
                                if size_origen == size_destino and abs(mtime_origen - mtime_destino) < 1.0:
                                    es_duplicado_real = True
                                    break
                            except Exception:
                                pass

                            contador += 1
                            nuevo_nombre = f"{base_nombre}({contador}){ext}"
                            ruta_archivo_destino = os.path.join(carpeta_destino_actual, nuevo_nombre)
                            fue_renombrado = True

                        if es_duplicado_real:
                            if modo == "omitir":
                                self.ya_existian += 1
                                self.omitidos.append((archivo, "Ya existe en el destino (Mismo tamaño y fecha)"))
                                self.lbl_m_omitidos.config(text=f"Omitidos: {self.ya_existian}")
                                self.log_mensaje(f"[OMITIDO] {archivo} (Duplicado idéntico)", "OMITIDO")
                                continue 
                            elif modo == "reemplazar":
                                try: os.remove(ruta_archivo_destino)
                                except Exception as e:
                                    motivo = f"Sin permiso reemplazo: {e}"
                                    self.errores.append((archivo, peso_legible, motivo))
                                    self.lbl_m_errores.config(text=f"Errores: {len(self.errores)}")
                                    self.log_mensaje(f"[ERROR REEMPLAZO] {archivo}: {motivo}", "ERROR")
                                    continue

                        nombre_archivo_final = os.path.basename(ruta_archivo_destino)
                        nombre_visible = nombre_archivo_final if len(nombre_archivo_final) <= 35 else nombre_archivo_final[:32] + "..."
                        self.lbl_estado.config(text=f"⚡ Copiando: {nombre_visible}", fg=self.COLOR_GOLD_BRIGHT)
                        
                        try:
                            shutil.copy2(ruta_archivo_origen, ruta_archivo_destino)
                            self.exitos.append((nombre_archivo_final, peso_legible))
                            self.bytes_transferidos += peso_bytes
                            
                            self.lbl_m_exito.config(text=f"Copiados: {len(self.exitos)}")
                            self.lbl_m_peso.config(text=f"Volumen: {self.formatear_peso(self.bytes_transferidos)}")

                            if fue_renombrado:
                                self.log_mensaje(f"[RENOMBRADO] {archivo} ➔ {nombre_archivo_final} ({peso_legible})", "RENOMBRADO")
                            else:
                                self.log_mensaje(f"[COPIADO] {nombre_archivo_final} ({peso_legible})", "EXITO")

                        except Exception as e:
                            motivo = str(e).split("]")[-1].strip()
                            self.errores.append((nombre_archivo_final, peso_legible, motivo))
                            self.lbl_m_errores.config(text=f"Errores: {len(self.errores)}")
                            self.log_mensaje(f"[ERROR] {nombre_archivo_final}: {motivo}", "ERROR")

            # Final de proceso en Log
            if self.cancelar_proceso:
                self.log_mensaje("=== PROCESO CANCELADO POR EL USUARIO ===", "ERROR")
            else:
                self.log_mensaje("=== RESPALDO COMPLETADO EXITOSAMENTE ===", "INFO")

            # Generar Auditoría Física Detallada
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
                    f.write(f"• Archivos omitidos:             {self.ya_existian}\n")
                    f.write(f"• Archivos con error:            {len(self.errores)}\n")
                    f.write(f"• Volumen total copiado:         {self.formatear_peso(self.bytes_transferidos)}\n\n")

                    if self.omitidos:
                        f.write("--------------------------------------------------\n")
                        f.write("DETALLE DE ARCHIVOS OMITIDOS:\n")
                        f.write("--------------------------------------------------\n")
                        for item, razon in self.omitidos:
                            f.write(f"[OMITIDO] {item} -> Causa: {razon}\n")
                        f.write("\n")

                    if self.errores:
                        f.write("--------------------------------------------------\n")
                        f.write("DETALLE DE ERRORES / FALLOS:\n")
                        f.write("--------------------------------------------------\n")
                        for item, peso, motivo in self.errores:
                            f.write(f"[ERROR] {item} ({peso}) -> Causa: {motivo}\n")
                        f.write("\n")

            except Exception as e:
                print(f"Error informe: {e}")

            self.mostrar_ventana_finalizacion()

        except Exception as ex:
            self.lbl_estado.config(text=f"❌ Error grave: {ex}", fg=self.COLOR_RED)
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
                f"• Archivos omitidos (duplicados reales): {self.ya_existian}\n"
                f"• Volumen copiado: {peso_total}\n\n"
                "La interfaz se limpiará automáticamente al dar Aceptar."
            )
            messagebox.showinfo("Proceso Finalizado", resumen_msg)
            
        self.resetear_interfaz()

if __name__ == "__main__":
    app = AppBackupCorporativoElite()
    app.mainloop()