import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import random
import os
import sys
import stat
import tempfile
import math

GLOSARIO_N2 = {
    "Rafaga": (
        "RAFAGA (Burst Time)",
        "Es el tiempo total que un programa necesita usar la CPU para terminar su trabajo.\n\n"
        "En palabras simples: es lo que tarda el cocinero en preparar un pedido completo. "
        "Un pedido grande tiene una rafaga larga; uno pequeño, una rafaga corta."
    ),
    "Quantum": (
        "QUANTUM (turno)",
        "Es el tiempo maximo que la CPU le presta a un programa antes de pasar al siguiente, "
        "haya terminado o no.\n\n"
        "En palabras simples: es el cronometro del cocinero. Si el quantum es de 2 segundos, "
        "cocina 2 segundos un pedido y luego cambia, aunque no lo haya terminado."
    ),
    "Cola de listos": (
        "COLA DE LISTOS (Ready Queue)",
        "Es la fila donde esperan los programas que ya estan preparados para usar la CPU pero "
        "todavia no les toca su turno.\n\n"
        "En palabras simples: es la fila de pedidos pegados en la ventanilla de la cocina."
    ),
    "Cambio de contexto": (
        "CAMBIO DE CONTEXTO (Context Switch)",
        "Es el momento en que el nucleo guarda el estado del programa que sale de la CPU y carga "
        "el estado del programa que entra, para que pueda continuar exactamente donde se quedo.\n\n"
        "En palabras simples: es poner una nota en el pedido que se deja a medias para saber "
        "por donde seguir despues. Hacerlo cuesta un poquito de tiempo."
    ),
    "Apropiacion": (
        "APROPIACION (Preemption)",
        "Es cuando la CPU le quita su turno a un programa que aun no termino, porque su quantum "
        "se acabo, y lo manda al final de la cola.\n\n"
        "En palabras simples: el cocinero deja el pedido a medias y lo pone al final de la fila "
        "para darle oportunidad a los demas."
    ),
    "Terminacion": (
        "TERMINACION DE PROCESO",
        "Es cuando un programa completa toda su rafaga. El kernel lo saca de la cola para siempre "
        "y libera la CPU para otro.\n\n"
        "En palabras simples: el pedido quedo listo y sale de la cocina."
    ),
    "Round Robin": (
        "ROUND ROBIN",
        "Es un algoritmo de planificacion: cada programa recibe un turno igual (quantum) y se van "
        "rotando en orden circular hasta que todos terminan.\n\n"
        "En palabras simples: nadie se queda esperando eternamente, porque todos avanzan un poquito "
        "cada vez. Es un reparto justo."
    ),
}

CONTENIDO_ARCHIVOS_N5 = {
    "informe_confidencial.txt": (
        "INFORME CONFIDENCIAL - InsideOS\n"
        "================================\n"
        "Este es un archivo REAL guardado en tu disco duro.\n"
        "El Sistema Operativo decide si puedes leerlo, modificarlo o ejecutarlo.\n"
        "Codigo secreto de la mision: OS-2026-ALFA\n"
    ),
    "programa_saludo.py": (
        "import os\n"
        "import time\n"
        "print('Hola! Soy un programa REAL ejecutado por el Sistema Operativo.')\n"
        "print('Mi identificador de proceso (PID) es:', os.getpid())\n"
        "print('Hora de ejecucion:', time.strftime('%H:%M:%S'))\n"
    ),
}


class InsideOSVentanasReales:
    def __init__(self, root):
        self.root = root
        self.root.title("InsideOS - Version Ventanas Reales")
        self.root.geometry("1250x900")
        self.root.configure(bg="#1e1e2e")
        self.root.protocol("WM_DELETE_WINDOW", self.al_cerrar)

        self.historial_programas_abiertos = []

        self.pid_real = None
        self.nombre_proceso_win = ""
        self.corriendo_real = False
        self.ram_blocks_real = [None] * 12
        self.pipeline_cajas_n1 = []
        self.pipeline_token_n1 = None
        self.canvas_pipeline_n1 = None

        self.apps_dict = {
            "Google Chrome": {"cmd": "chrome", "exe": "chrome.exe"},
            "Microsoft Word": {"cmd": "winword", "exe": "WINWORD.EXE"},
            "Microsoft Excel": {"cmd": "excel", "exe": "EXCEL.EXE"},
            "Visual Studio Code": {"cmd": "code", "exe": "Code.exe"},
            "Bloc de Notas": {"cmd": "notepad", "exe": "notepad.exe"},
            "Calculadora": {"cmd": "calc", "exe": "CalculatorApp.exe"},
            "Paint (Dibujo)": {"cmd": "mspaint", "exe": "mspaint.exe"}
        }

        self.ram_blocks_sim = [None] * 12
        self.virtual_memory = []
        self.permisos = {"Ver": False, "Modificar": False, "Ejecutar": False, "Admin": False}

        self.carpeta_swap = os.path.join(tempfile.gettempdir(), "InsideOS_Swap")
        if not os.path.exists(self.carpeta_swap):
            os.makedirs(self.carpeta_swap)
        self.archivos_swap_creados = []

        self.monitor_n4_activo = False
        self.cola_monitor_n4 = []
        self.limite_ventanas_n4 = 3
        self.ventanas_ignoradas_n4 = set()
        self.advertencia_en_curso_n4 = False

        self.hora_inicio_sesion = time.time()
        self.contador_procesos_creados_n1 = 0
        self.contador_cierres_manuales_n1 = 0
        self.contador_expulsiones_n4 = 0
        self.contador_advertencias_rechazadas_n4 = 0

        self.nivel1_usado = False
        self.nivel2_usado = False
        self.nivel3_usado = False
        self.nivel4_usado = False
        self.nivel5_usado = False

        self.nombres_tabs = [
            "Nivel 1: Abrir e Iniciar Procesos",
            "Nivel 2: Algoritmos CPU con tus Apps",
            "Nivel 3: RAM + Disco Duro (Swap)",
            "Nivel 4: Control Real de Ventanas",
            "Nivel 5: Candados de Archivos",
            "Nivel Final: Diagnostico General",
        ]
        self.niveles_notificados = set()

        self.simulando_n2 = False
        self.pausa_n2 = False
        self.modo_paso_n2 = False
        self.velocidad_n2 = 1.0
        self.quantum_n2 = 2
        self.evento_paso_n2 = threading.Event()
        self.colores_n2 = ["#89b4fa", "#a6e3a1", "#f9e2af", "#f5c2e7"]
        self.celda_gantt_n2 = 40

        self.carpeta_archivos_n5 = os.path.join(tempfile.gettempdir(), "InsideOS_Archivos")
        self.archivos_n5 = {
            "informe_confidencial.txt (documento)": "informe_confidencial.txt",
            "programa_saludo.py (programa)": "programa_saludo.py",
        }
        self.n5_acciones = set()
        self.n5_resultados = set()
        self.animando_n5 = False
        self.crear_archivos_reales_n5()

        self.setup_styles()
        self.create_layout()
        self.actualizar_estado_tabs()

    def al_cerrar(self):
        try:
            for nombre in self.archivos_n5.values():
                ruta = os.path.join(self.carpeta_archivos_n5, nombre)
                if os.path.exists(ruta):
                    os.chmod(ruta, stat.S_IREAD | stat.S_IWRITE)
        except Exception:
            pass
        self.root.destroy()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background="#1e1e2e", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#313244", foreground="#cdd6f4", font=("Arial", 10, "bold"), padding=[10, 4])
        self.style.map("TNotebook.Tab",
                       background=[("disabled", "#181825"), ("selected", "#89b4fa")],
                       foreground=[("disabled", "#6c7086"), ("selected", "#11111b")])
        self.style.configure("Vertical.TScrollbar", background="#313244", troughcolor="#1e1e2e", arrowcolor="#cdd6f4")

    def create_layout(self):
        lbl_titulo = tk.Label(self.root, text="INSIDE OS: Analisis Real de tus Ventanas Activas",
                              font=("Arial", 22, "bold"), bg="#1e1e2e", fg="#89b4fa", pady=10)
        lbl_titulo.pack(fill=tk.X)

        tk.Label(self.root, text="Completa cada nivel para desbloquear el siguiente. Las pestañas con candado todavia estan bloqueadas.",
                 font=("Arial", 10, "italic"), bg="#1e1e2e", fg="#f9e2af").pack(fill=tk.X)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.tab1 = tk.Frame(self.notebook, bg="#1e1e2e")
        self.tab2 = tk.Frame(self.notebook, bg="#1e1e2e")
        self.tab3 = tk.Frame(self.notebook, bg="#1e1e2e")
        self.tab4 = tk.Frame(self.notebook, bg="#1e1e2e")
        self.tab5 = tk.Frame(self.notebook, bg="#1e1e2e")
        self.tab6 = tk.Frame(self.notebook, bg="#1e1e2e")

        for tab, nombre in zip([self.tab1, self.tab2, self.tab3, self.tab4, self.tab5, self.tab6], self.nombres_tabs):
            self.notebook.add(tab, text=nombre)

        self.construir_nivel_1()
        self.construir_nivel_2()
        self.construir_nivel_3()
        self.construir_nivel_4()
        self.construir_nivel_5()
        self.construir_nivel_6()

    def actualizar_estado_tabs(self):
        banderas = [self.nivel1_usado, self.nivel2_usado, self.nivel3_usado, self.nivel4_usado, self.nivel5_usado]
        for i, nombre in enumerate(self.nombres_tabs):
            abierto = all(banderas[:i])
            self.notebook.tab(i, state="normal" if abierto else "disabled", text=nombre if abierto else f"🔒 {nombre}")

    def completar_nivel(self, n):
        self.actualizar_estado_tabs()
        if n in self.niveles_notificados:
            return
        self.niveles_notificados.add(n)
        self.mostrar_mini_ventana("¡Nivel completado!", f"Completaste el Nivel {n}. Se desbloqueo: {self.nombres_tabs[n]}. Ya puedes abrir esa pestaña.", "exito")

    def crear_area_desplazable(self, tab_padre):
        contenedor = tk.Frame(tab_padre, bg="#1e1e2e")
        contenedor.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(contenedor, bg="#1e1e2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(contenedor, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        frame_interno = tk.Frame(canvas, bg="#1e1e2e")

        ventana_id = canvas.create_window((0, 0), window=frame_interno, anchor="nw")

        def actualizar_scroll(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def ajustar_ancho(event):
            canvas.itemconfig(ventana_id, width=event.width)

        frame_interno.bind("<Configure>", actualizar_scroll)
        canvas.bind("<Configure>", ajustar_ancho)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _rueda(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _activar_rueda(event):
            canvas.bind_all("<MouseWheel>", _rueda)

        def _desactivar_rueda(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _activar_rueda)
        canvas.bind("<Leave>", _desactivar_rueda)

        return frame_interno

    def agregar_introduccion(self, parent, titulo, texto):
        frame_intro = tk.LabelFrame(parent, text=f" {titulo} ", font=("Arial", 12, "bold"), bg="#1e1e2e", fg="#f9e2af", padx=15, pady=10)
        frame_intro.pack(fill=tk.X, padx=15, pady=10)
        tk.Label(frame_intro, text=texto, font=("Arial", 10), bg="#1e1e2e", fg="#cdd6f4", justify=tk.LEFT, wraplength=1100).pack(anchor=tk.W)

    def mostrar_mini_ventana(self, titulo, mensaje, tipo="info"):
        paletas = {
            "exito": ("#a6e3a1", "#11111b"),
            "error": ("#f38ba8", "#11111b"),
            "info": ("#89b4fa", "#11111b")
        }
        bg, fg = paletas.get(tipo, paletas["info"])

        ventana = tk.Toplevel(self.root)
        ventana.title(titulo)
        ventana.configure(bg=bg)
        ventana.resizable(False, False)
        try:
            x = self.root.winfo_x() + 420
            y = self.root.winfo_y() + 260
        except Exception:
            x, y = 400, 300
        ventana.geometry(f"360x190+{x}+{y}")
        ventana.attributes("-topmost", True)

        tk.Label(ventana, text=titulo, font=("Arial", 13, "bold"), bg=bg, fg=fg).pack(pady=(15, 5))
        tk.Label(ventana, text=mensaje, font=("Arial", 10), bg=bg, fg=fg, wraplength=320, justify=tk.CENTER).pack(pady=5, padx=10)
        tk.Button(ventana, text="Cerrar", font=("Arial", 9, "bold"), bg="#11111b", fg=bg, command=ventana.destroy).pack(pady=10)

        ventana.after(5000, lambda: ventana.destroy() if ventana.winfo_exists() else None)

    def mostrar_ventana_explicativa(self, titulo, mensaje):
        ventana = tk.Toplevel(self.root)
        ventana.title(titulo)
        ventana.configure(bg="#181825")
        ventana.resizable(False, False)
        try:
            x = self.root.winfo_x() + 350
            y = self.root.winfo_y() + 200
        except Exception:
            x, y = 380, 260
        ventana.geometry(f"500x340+{x}+{y}")
        ventana.attributes("-topmost", True)

        tk.Label(ventana, text=titulo, font=("Arial", 14, "bold"), bg="#181825", fg="#f9e2af").pack(pady=(18, 8))
        tk.Label(ventana, text=mensaje, font=("Arial", 10), bg="#181825", fg="#cdd6f4", wraplength=450, justify=tk.LEFT).pack(pady=5, padx=20)
        tk.Button(ventana, text="Entendido", font=("Arial", 10, "bold"), bg="#89b4fa", fg="#11111b", command=ventana.destroy).pack(pady=15)

    def obtener_procesos_ventanas_reales(self, limite=3, orden="mem"):
        try:
            if orden == "tiempo":
                ps_cmd = 'Get-Process | Where-Object {$_.MainWindowTitle -ne ""} | Sort-Object StartTime | Select-Object Name, Id, WorkingSet64 | ConvertTo-Csv -NoTypeInformation'
            else:
                ps_cmd = 'Get-Process | Where-Object {$_.MainWindowTitle -ne ""} | Select-Object Name, Id, WorkingSet64 | ConvertTo-Csv -NoTypeInformation'

            proc = subprocess.Popen(['powershell', '-Command', ps_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            salida, _ = proc.communicate()

            lineas = salida.strip().split('\n')
            lista_procesos = []

            for l in lineas:
                if ',' in l:
                    partes = l.split(',')
                    nombre = partes[0].replace('"', '') + ".exe"
                    pid = partes[1].replace('"', '')
                    try:
                        mem_kb = int(partes[2].replace('"', '')) // 1024
                        if mem_kb > 1000 and "powershell" not in nombre.lower():
                            lista_procesos.append({"name": nombre, "pid": pid, "mem": mem_kb})
                    except ValueError:
                        continue

            if orden != "tiempo":
                lista_procesos.sort(key=lambda x: x["mem"], reverse=True)

            if not lista_procesos:
                return [{"name": "chrome.exe", "pid": "1024", "mem": 60000}, {"name": "explorer.exe", "pid": "2048", "mem": 40000}]

            return lista_procesos[:limite]
        except Exception:
            return [{"name": "chrome.exe", "pid": "1024", "mem": 60000}]

    def obtener_ram_fisica_real(self):
        try:
            ps_cmd = 'Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Csv -NoTypeInformation'
            proc = subprocess.Popen(['powershell', '-Command', ps_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            salida, _ = proc.communicate()
            lineas = salida.strip().split('\n')
            if len(lineas) >= 2:
                partes = lineas[1].split(',')
                total_kb = int(partes[0].replace('"', ''))
                libre_kb = int(partes[1].replace('"', ''))
                return total_kb, libre_kb
        except Exception:
            pass
        return None, None

    def construir_nivel_1(self):
        contenedor = self.crear_area_desplazable(self.tab1)

        self.agregar_introduccion(contenedor, "Que hace este nivel",
            "Abrimos un programa real de tu computador y vemos, como si fuera un video reproducido paso a paso, "
            "todo lo que hace el Sistema Operativo desde que pides abrirlo hasta que la ventana aparece en tu "
            "escritorio y ocupa bloques de tu memoria RAM. Elige un programa, presiona 'Abrir Programa Real' y "
            "observa la secuencia iluminarse en orden. Cuando termines, usa el boton de cierre para liberar la "
            "aplicacion y poder abrir otra distinta.\n\n"
            "PARA DESBLOQUEAR EL NIVEL 2: abre un programa real con exito y observa la secuencia completa.")

        frame_opciones = tk.Frame(contenedor, bg="#1e1e2e")
        frame_opciones.pack(pady=5)

        self.cmb_real = ttk.Combobox(frame_opciones, font=("Arial", 11), width=22)
        self.cmb_real['values'] = list(self.apps_dict.keys())
        self.cmb_real.current(0)
        self.cmb_real.pack(side=tk.LEFT, padx=5)

        btn_lanzar = tk.Button(frame_opciones, text="¡Abrir Programa Real!", font=("Arial", 11, "bold"), bg="#a6e3a1", fg="#11111b", command=self.lanzar_programa_computador)
        btn_lanzar.pack(side=tk.LEFT, padx=10)

        frame_pipeline = tk.LabelFrame(contenedor, text=" Diagrama en Vivo: Como Viaja tu Solicitud por el Sistema Operativo ", font=("Arial", 11, "bold"), bg="#1e1e2e", fg="#f9e2af")
        frame_pipeline.pack(fill=tk.X, padx=15, pady=(5, 10))

        self.canvas_pipeline_n1 = tk.Canvas(frame_pipeline, width=1180, height=180, bg="#313244", highlightthickness=0)
        self.canvas_pipeline_n1.pack(padx=10, pady=10, fill=tk.X)
        self.construir_pipeline_n1()

        frame_visual = tk.Frame(contenedor, bg="#1e1e2e")
        frame_visual.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        frame_explicacion = tk.LabelFrame(frame_visual, text=" Explicacion Detallada del Paso Actual ", font=("Arial", 11, "bold"), bg="#1e1e2e", fg="#89b4fa")
        frame_explicacion.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.lbl_pasos_real = tk.Label(frame_explicacion, text="Estado: Esperando que abras un programa...", font=("Arial", 11, "bold"), bg="#1e1e2e", fg="#f9e2af", anchor=tk.W, justify=tk.LEFT, wraplength=430)
        self.lbl_pasos_real.pack(fill=tk.X, padx=10, pady=10)

        self.lbl_telemetria = tk.Label(frame_explicacion, text="ID Unico (PID): Ninguno\nRAM Usada: 0 KB", font=("Arial", 11), bg="#181825", fg="#94e2d5", bd=4, relief=tk.SUNKEN, justify=tk.LEFT, padx=10, pady=10)
        self.lbl_telemetria.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame_explicacion, text="Bitacora tecnica (lo que hace el Sistema Operativo por dentro):", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(anchor=tk.W, padx=10)
        self.txt_logs_real = tk.Text(frame_explicacion, bg="#11111b", fg="#a6e3a1", font=("Courier New", 9), height=10, state=tk.DISABLED)
        self.txt_logs_real.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        frame_hardware = tk.LabelFrame(frame_visual, text=" Mapa de Celdas de tu RAM Fisica ", font=("Arial", 11, "bold"), bg="#1e1e2e", fg="#cba6f7")
        frame_hardware.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.canvas_real = tk.Canvas(frame_hardware, bg="#313244", highlightthickness=0, height=320)
        self.canvas_real.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas_real.bind("<Configure>", lambda e: self.dibujar_ram_real())

        frame_cierre = tk.LabelFrame(contenedor, text=" Cerrar la Aplicacion Abierta ", font=("Arial", 11, "bold"), bg="#1e1e2e", fg="#f38ba8")
        frame_cierre.pack(fill=tk.X, padx=15, pady=15)
        tk.Label(frame_cierre, text="Cuando termines de observar el proceso puedes cerrarlo de verdad, liberar la RAM y elegir otro programa para abrir.", bg="#1e1e2e", fg="#cdd6f4", font=("Arial", 9), wraplength=1100, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=(8, 0))
        tk.Button(frame_cierre, text="Cerrar Aplicacion Actual", font=("Arial", 11, "bold"), bg="#f38ba8", fg="#11111b", command=self.cerrar_programa_actual).pack(padx=10, pady=10)

    def dibujar_icono_persona(self, canvas, cx, cy):
        canvas.create_oval(cx-8, cy-20, cx+8, cy-4, fill="#f9e2af", outline="")
        canvas.create_arc(cx-15, cy-6, cx+15, cy+24, start=0, extent=180, fill="#f9e2af", outline="")

    def dibujar_icono_engranaje(self, canvas, cx, cy, color):
        canvas.create_oval(cx-13, cy-13, cx+13, cy+13, fill=color, outline="")
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            x1 = cx + 13 * math.cos(rad)
            y1 = cy + 13 * math.sin(rad)
            x2 = cx + 19 * math.cos(rad)
            y2 = cy + 19 * math.sin(rad)
            canvas.create_line(x1, y1, x2, y2, fill=color, width=5)
        canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="#11111b", outline="")

    def dibujar_icono_disco(self, canvas, cx, cy):
        canvas.create_rectangle(cx-18, cy-10, cx+18, cy+12, fill="#a6e3a1", outline="#11111b")
        canvas.create_oval(cx-18, cy-16, cx+18, cy-4, fill="#a6e3a1", outline="#11111b")
        canvas.create_oval(cx-18, cy+6, cx+18, cy+18, fill="#a6e3a1", outline="#11111b")
        canvas.create_oval(cx-4, cy-13, cx+4, cy-7, fill="#11111b", outline="")

    def dibujar_icono_tarjeta(self, canvas, cx, cy):
        canvas.create_rectangle(cx-20, cy-13, cx+20, cy+13, fill="#cba6f7", outline="#11111b")
        canvas.create_oval(cx-15, cy-6, cx-5, cy+4, fill="#11111b", outline="")
        canvas.create_line(cx+1, cy-6, cx+16, cy-6, fill="#11111b", width=2)
        canvas.create_line(cx+1, cy, cx+16, cy, fill="#11111b", width=2)
        canvas.create_line(cx+1, cy+6, cx+10, cy+6, fill="#11111b", width=2)

    def dibujar_icono_chip(self, canvas, cx, cy):
        canvas.create_rectangle(cx-18, cy-12, cx+18, cy+12, fill="#94e2d5", outline="#11111b")
        for i in range(4):
            px = cx - 15 + i * 10
            canvas.create_line(px, cy-12, px, cy-19, fill="#11111b")
            canvas.create_line(px, cy+12, px, cy+19, fill="#11111b")

    def construir_pipeline_n1(self):
        canvas = self.canvas_pipeline_n1
        canvas.delete("all")

        etapas = [
            {"label": "TU\n(Usuario)", "tipo": "persona"},
            {"label": "Sistema\nOperativo", "tipo": "engranaje_azul"},
            {"label": "Disco Duro\n(buscando .exe)", "tipo": "disco"},
            {"label": "Kernel\n(fork / exec)", "tipo": "engranaje_rojo"},
            {"label": "Tabla de\nProcesos (PID)", "tipo": "tarjeta"},
            {"label": "Memoria\nRAM", "tipo": "chip"},
        ]

        ancho_caja = 175
        alto_caja = 120
        espacio = 20
        x = 15
        y = 25

        self.pipeline_cajas_n1 = []

        for etapa in etapas:
            rect = canvas.create_rectangle(x, y, x+ancho_caja, y+alto_caja, fill="#1e1e2e", outline="#6c7086", width=3)
            cx = x + ancho_caja/2
            cy = y + 45

            if etapa["tipo"] == "persona":
                self.dibujar_icono_persona(canvas, cx, cy)
            elif etapa["tipo"] == "engranaje_azul":
                self.dibujar_icono_engranaje(canvas, cx, cy, "#89b4fa")
            elif etapa["tipo"] == "disco":
                self.dibujar_icono_disco(canvas, cx, cy)
            elif etapa["tipo"] == "engranaje_rojo":
                self.dibujar_icono_engranaje(canvas, cx, cy, "#f38ba8")
            elif etapa["tipo"] == "tarjeta":
                self.dibujar_icono_tarjeta(canvas, cx, cy)
            elif etapa["tipo"] == "chip":
                self.dibujar_icono_chip(canvas, cx, cy)

            canvas.create_text(cx, y+alto_caja-18, text=etapa["label"], font=("Arial", 9, "bold"), fill="#cdd6f4", justify=tk.CENTER)

            self.pipeline_cajas_n1.append({"rect": rect, "cx": cx, "cy_token": y+alto_caja+18})

            if len(self.pipeline_cajas_n1) < len(etapas):
                canvas.create_line(x+ancho_caja, y+alto_caja/2, x+ancho_caja+espacio, y+alto_caja/2, fill="#585b70", width=3, arrow=tk.LAST)

            x += ancho_caja + espacio

        primera = self.pipeline_cajas_n1[0]
        self.pipeline_token_n1 = canvas.create_oval(primera["cx"]-9, primera["cy_token"]-9, primera["cx"]+9, primera["cy_token"]+9, fill="#f9e2af", outline="#11111b", width=2)

    def resetear_pipeline_n1(self):
        canvas = self.canvas_pipeline_n1
        for caja in self.pipeline_cajas_n1:
            canvas.itemconfig(caja["rect"], outline="#6c7086", width=3, fill="#1e1e2e")
        primera = self.pipeline_cajas_n1[0]
        coords = canvas.coords(self.pipeline_token_n1)
        cx_actual = (coords[0] + coords[2]) / 2
        canvas.move(self.pipeline_token_n1, primera["cx"] - cx_actual, 0)

    def avanzar_pipeline_n1(self, indice, explicacion):
        canvas = self.canvas_pipeline_n1

        for i, caja in enumerate(self.pipeline_cajas_n1):
            if i < indice:
                canvas.itemconfig(caja["rect"], outline="#a6e3a1", width=3, fill="#1e1e2e")
            elif i == indice:
                canvas.itemconfig(caja["rect"], outline="#f9e2af", width=6, fill="#45475a")
            else:
                canvas.itemconfig(caja["rect"], outline="#6c7086", width=3, fill="#1e1e2e")

        destino = self.pipeline_cajas_n1[indice]
        coords = canvas.coords(self.pipeline_token_n1)
        cx_actual = (coords[0] + coords[2]) / 2
        distancia = destino["cx"] - cx_actual
        pasos_animacion = 24
        for _ in range(pasos_animacion):
            canvas.move(self.pipeline_token_n1, distancia/pasos_animacion, 0)
            canvas.update()
            time.sleep(0.02)

        self.lbl_pasos_real.config(text=explicacion)

    def log_nivel1(self, texto):
        self.txt_logs_real.config(state=tk.NORMAL)
        self.txt_logs_real.insert(tk.END, f"> {texto}\n")
        self.txt_logs_real.see(tk.END)
        self.txt_logs_real.config(state=tk.DISABLED)

    def marcar_bloque_ram_real(self, indice, color):
        col = indice % 4
        row = indice // 4
        x1, y1 = 20 + col * 85, 40 + row * 65
        x2, y2 = x1 + 75, y1 + 55
        self.canvas_real.delete("check_mark_real")
        self.canvas_real.create_rectangle(x1, y1, x2, y2, outline=color, width=5, tags="check_mark_real")
        self.canvas_real.update()

    def animar_asignacion_ram_inicial(self, bloques):
        self.ram_blocks_real = [None] * 12
        self.dibujar_ram_real()
        for i in range(bloques):
            self.log_nivel1(f"   -> Verificando Bloque {i}... LIBRE. El administrador de memoria lo reserva.")
            self.marcar_bloque_ram_real(i, "#f9e2af")
            time.sleep(0.35)
            self.ram_blocks_real[i] = "#89b4fa"
            self.dibujar_ram_real()
            time.sleep(0.25)
        self.canvas_real.delete("check_mark_real")

    def lanzar_programa_computador(self):
        if self.corriendo_real:
            messagebox.showwarning("Atencion", "Ya tienes un proceso activo. Cierralo con el boton de abajo antes de abrir otro.")
            return
        threading.Thread(target=self._lanzar_programa_hilo, daemon=True).start()

    def _lanzar_programa_hilo(self):
        seleccion = self.cmb_real.get().strip()

        if seleccion in self.apps_dict:
            comando = self.apps_dict[seleccion]["cmd"]
            self.nombre_proceso_win = self.apps_dict[seleccion]["exe"]
        else:
            comando = seleccion
            self.nombre_proceso_win = seleccion if ".exe" in seleccion else f"{seleccion}.exe"

        self.resetear_pipeline_n1()

        self.avanzar_pipeline_n1(0, f"PASO 1: Pediste abrir '{seleccion}'.\nEl Sistema Operativo recibe tu solicitud desde el escritorio o la terminal y la coloca en su cola de peticiones.")
        self.log_nivel1(f"PASO 1: Pediste abrir '{seleccion}'. El Sistema Operativo recibe la orden.")
        time.sleep(1.4)

        try:
            self.avanzar_pipeline_n1(1, f"PASO 2: El Sistema Operativo interpreta la orden y consulta las variables de entorno (PATH) y el Registro de Windows para saber donde vive el programa '{seleccion}'.")
            self.log_nivel1("PASO 2: El OS busca el ejecutable en las carpetas del sistema (PATH / Registro).")
            time.sleep(1.2)

            self.avanzar_pipeline_n1(2, f"PASO 3: El disco duro localiza el archivo '{self.nombre_proceso_win}', lo lee en bloques y lo entrega al cargador del Sistema Operativo para prepararlo en memoria.")
            self.log_nivel1(f"PASO 3: El disco duro localiza y lee el archivo '{self.nombre_proceso_win}'.")
            subprocess.Popen(f"start {comando}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(1.6)

            self.avanzar_pipeline_n1(3, "PASO 4: El Kernel ejecuta la llamada de sistema (fork/exec o CreateProcess). Crea un Bloque de Control de Proceso (PCB) con el estado, los registros y los permisos del nuevo programa.")
            self.log_nivel1("PASO 4: El kernel crea el proceso y arma su Bloque de Control de Proceso (PCB).")
            time.sleep(1.8)

            self.log_nivel1("PASO 5: El OS escanea las ventanas activas para confirmar que la app abrio de verdad.")
            ventanas = self.obtener_procesos_ventanas_reales(limite=10)
            proceso_encontrado = None
            for v in ventanas:
                if v["name"].lower() == self.nombre_proceso_win.lower():
                    proceso_encontrado = v
                    break

            if proceso_encontrado:
                self.pid_real = proceso_encontrado["pid"]
                self.corriendo_real = True
                self.contador_procesos_creados_n1 += 1

                if seleccion not in self.historial_programas_abiertos:
                    self.historial_programas_abiertos.append(seleccion)

                self.avanzar_pipeline_n1(4, f"PASO 6: La Tabla de Procesos del Sistema Operativo asigna un identificador unico (PID = {self.pid_real}) y marca el proceso como READY / RUNNING.")
                self.log_nivel1(f"PASO 6: Windows asigna un identificador unico (PID) al proceso: {self.pid_real}.")
                time.sleep(1.2)

                self.avanzar_pipeline_n1(5, "PASO 7: El Administrador de Memoria revisa bloque por bloque tu memoria RAM, buscando espacio libre, y va reservando celdas fisicas una por una para el nuevo proceso.")
                self.log_nivel1("PASO 7: El OS reserva bloques de memoria RAM, verificando celda por celda.")

                mem_inicial = proceso_encontrado.get("mem", 15000)
                bloques_iniciales = min(12, max(1, mem_inicial // 15000))
                self.animar_asignacion_ram_inicial(bloques_iniciales)

                self.lbl_pasos_real.config(text=f"¡Proceso en ejecucion!\n{seleccion} quedo instalado en {bloques_iniciales} bloque(s) de RAM y sigue vivo (running) mientras la ventana este abierta.")
                self.log_nivel1("PASO FINAL: La ventana aparece en tu escritorio y el proceso queda 'vivo' (running).")

                self.nivel1_usado = True
                self.root.after(0, lambda: self.completar_nivel(1))

                threading.Thread(target=self.monitorear_hardware_computador, daemon=True).start()
            else:
                self.log_nivel1(f"RESULTADO: No se detecto ventana activa para '{seleccion}'.")
                self.lbl_pasos_real.config(text="Estado: Busqueda fallida.")
                messagebox.showerror("Programa No Encontrado", f"El programa '{seleccion}' no esta instalado en este computador o no se abrio una ventana principal.")
        except Exception:
            messagebox.showerror("Error", "Error al intentar rastrear el programa.")

    def cerrar_programa_actual(self):
        if not self.corriendo_real or not self.pid_real:
            messagebox.showinfo("Sin Proceso", "No hay ninguna aplicacion abierta por este simulador en este momento.")
            return
        try:
            resultado = subprocess.run(["taskkill", "/F", "/PID", str(self.pid_real)], capture_output=True, text=True)
            if resultado.returncode == 0:
                self.log_nivel1(f"CIERRE MANUAL: Se envio la señal de terminacion (TerminateProcess) al PID {self.pid_real}.")
                self.log_nivel1("CIERRE MANUAL: La RAM que usaba ese proceso quedo libre. Ya puedes abrir otro programa.")
                self.contador_cierres_manuales_n1 += 1
            else:
                self.log_nivel1(f"CIERRE MANUAL: Windows no pudo cerrar el PID {self.pid_real} (quizas ya se habia cerrado).")
        except Exception as e:
            self.log_nivel1(f"ERROR al cerrar la aplicacion: {e}")

        self.corriendo_real = False
        self.pid_real = None
        self.ram_blocks_real = [None] * 12
        self.dibujar_ram_real()
        self.lbl_telemetria.config(text="ID Unico (PID): Ninguno\nRAM Usada: 0 KB")
        self.lbl_pasos_real.config(text="Estado: Aplicacion cerrada. Puedes abrir otra ventana cuando quieras.")
        self.resetear_pipeline_n1()

    def monitorear_hardware_computador(self):
        primera_lectura = True
        while self.corriendo_real:
            try:
                ventanas = self.obtener_procesos_ventanas_reales(limite=15)
                proceso_activo = [v for v in ventanas if str(v["pid"]) == str(self.pid_real)]

                if not proceso_activo:
                    self.log_nivel1("PASO FINAL: La ventana se cerro. El kernel destruye el proceso y libera toda su RAM.")
                    self.lbl_pasos_real.config(text="Estado: Programa cerrado.")
                    self.lbl_telemetria.config(text="ID Unico (PID): Ninguno\nRAM Usada: 0 KB")
                    self.corriendo_real = False
                    self.pid_real = None
                    self.ram_blocks_real = [None] * 12
                    self.root.after(0, self.dibujar_ram_real)
                    self.root.after(0, self.resetear_pipeline_n1)
                    break

                mem_kb = proceso_activo[0]["mem"]
                self.lbl_telemetria.config(text=f"ID Unico (PID): {self.pid_real}\nRAM Usada: {mem_kb:,} KB")

                bloques = min(12, max(1, mem_kb // 15000))
                if primera_lectura:
                    self.log_nivel1(f"MONITOREO: El proceso esta consumiendo {mem_kb:,} KB -> ocupa {bloques} bloques de RAM.")
                    primera_lectura = False
                self.ram_blocks_real = [None] * 12
                for i in range(bloques):
                    self.ram_blocks_real[i] = "#89b4fa"

                self.root.after(0, self.dibujar_ram_real)
            except Exception:
                pass
            time.sleep(1.5)

    def dibujar_ram_real(self):
        self.canvas_real.delete("all")
        for i in range(12):
            col = i % 4
            row = i // 4
            x1, y1 = 20 + col * 85, 40 + row * 65
            x2, y2 = x1 + 75, y1 + 55
            color = self.ram_blocks_real[i] if self.ram_blocks_real[i] else "#1e1e2e"
            texto = f"Bloque {i}\nLleno" if self.ram_blocks_real[i] else f"Bloque {i}\nLibre"
            self.canvas_real.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cdd6f4")
            self.canvas_real.create_text((x1+x2)/2, (y1+y2)/2, text=texto, font=("Arial", 9, "bold"), fill="#11111b" if self.ram_blocks_real[i] else "#6c7086")

    def construir_nivel_2(self):
        contenedor = self.crear_area_desplazable(self.tab2)

        self.agregar_introduccion(contenedor, "Que hace este nivel (explicado facil)",
            "Imagina una cocina con UN SOLO cocinero (la CPU) y varios pedidos esperando (tus programas abiertos). "
            "El cocinero no puede preparar todo a la vez, asi que trabaja por turnos: cocina unos pocos segundos un "
            "pedido, lo deja en pausa, pasa al siguiente, y asi hasta terminar todos. Ese reparto justo de turnos "
            "se llama Round Robin.\n\n"
            "Aqui tus ventanas reales hacen de pedidos. Veras como esperan en fila, como entran a la CPU, como se les "
            "acaba el turno y como terminan. Puedes cambiar el tamaño del turno, la velocidad, pausar, o avanzar "
            "paso a paso a tu propio ritmo. Abajo hay un glosario: toca cualquier palabra para entenderla.\n\n"
            "PARA DESBLOQUEAR EL NIVEL 3: deja que la simulacion llegue hasta el final.")

        frame_controles = tk.LabelFrame(contenedor, text=" Controles de la simulacion ", font=("Arial", 11, "bold"), bg="#1e1e2e", fg="#cba6f7", padx=10, pady=8)
        frame_controles.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(frame_controles, text="Tamaño del turno (quantum):", font=("Arial", 10, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(side=tk.LEFT, padx=(5, 5))
        self.cmb_quantum_n2 = ttk.Combobox(frame_controles, values=["1 segundo", "2 segundos", "3 segundos"], state="readonly", width=12, font=("Arial", 10))
        self.cmb_quantum_n2.current(1)
        self.cmb_quantum_n2.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(frame_controles, text="Velocidad:", font=("Arial", 10, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(side=tk.LEFT, padx=(5, 5))
        self.escala_velocidad_n2 = tk.Scale(frame_controles, from_=0.5, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, length=140, bg="#1e1e2e", fg="#cdd6f4", highlightthickness=0, troughcolor="#313244", command=self.cambiar_velocidad_n2)
        self.escala_velocidad_n2.set(1.0)
        self.escala_velocidad_n2.pack(side=tk.LEFT, padx=(0, 15))

        self.var_paso_n2 = tk.BooleanVar(value=False)
        tk.Checkbutton(frame_controles, text="Modo paso a paso (yo controlo)", variable=self.var_paso_n2, font=("Arial", 10), bg="#1e1e2e", fg="#f9e2af", selectcolor="#313244", activebackground="#1e1e2e", activeforeground="#f9e2af", command=self.cambiar_modo_paso_n2).pack(side=tk.LEFT, padx=10)

        frame_botones = tk.Frame(contenedor, bg="#1e1e2e")
        frame_botones.pack(pady=5)

        self.btn_sim_n2 = tk.Button(frame_botones, text="Escanear ventanas y comenzar", font=("Arial", 11, "bold"), bg="#cba6f7", fg="#11111b", command=self.iniciar_simulacion_n2)
        self.btn_sim_n2.pack(side=tk.LEFT, padx=8)

        self.btn_pausa_n2 = tk.Button(frame_botones, text="Pausar", font=("Arial", 11, "bold"), bg="#f9e2af", fg="#11111b", width=10, command=self.alternar_pausa_n2)
        self.btn_pausa_n2.pack(side=tk.LEFT, padx=8)

        self.btn_siguiente_n2 = tk.Button(frame_botones, text="Siguiente paso ▶", font=("Arial", 11, "bold"), bg="#94e2d5", fg="#11111b", state=tk.DISABLED, command=self.siguiente_paso_n2)
        self.btn_siguiente_n2.pack(side=tk.LEFT, padx=8)

        self.lbl_status_cpu = tk.Label(contenedor, text="Presiona 'Escanear ventanas y comenzar' para ver como la CPU reparte su tiempo.", font=("Arial", 12, "bold"), bg="#1e1e2e", fg="#cdd6f4", wraplength=1100)
        self.lbl_status_cpu.pack(pady=(8, 4))

        self.canvas_cpu = tk.Canvas(contenedor, width=1180, height=270, bg="#313244", highlightthickness=0)
        self.canvas_cpu.pack(padx=15, pady=5, fill=tk.X)

        self.canvas_gantt = tk.Canvas(contenedor, width=1180, height=130, bg="#313244", highlightthickness=0)
        self.canvas_gantt.pack(padx=15, pady=5, fill=tk.X)

        frame_concepto = tk.LabelFrame(contenedor, text=" Que esta pasando ahora mismo ", font=("Arial", 11, "bold"), bg="#181825", fg="#f9e2af", padx=12, pady=8)
        frame_concepto.pack(fill=tk.X, padx=15, pady=8)

        self.lbl_concepto_titulo_n2 = tk.Label(frame_concepto, text="Todavia no empieza la simulacion", font=("Arial", 13, "bold"), bg="#181825", fg="#f9e2af", anchor=tk.W, justify=tk.LEFT, wraplength=1100)
        self.lbl_concepto_titulo_n2.pack(fill=tk.X)
        self.lbl_concepto_cpu = tk.Label(frame_concepto, text="Aqui se explicara, en el momento exacto en que ocurre, que concepto de Sistemas Operativos esta pasando.", font=("Arial", 10), bg="#181825", fg="#cdd6f4", anchor=tk.W, justify=tk.LEFT, wraplength=1100)
        self.lbl_concepto_cpu.pack(fill=tk.X, pady=(4, 2))
        self.lbl_simple_n2 = tk.Label(frame_concepto, text="", font=("Arial", 10, "italic"), bg="#181825", fg="#94e2d5", anchor=tk.W, justify=tk.LEFT, wraplength=1100)
        self.lbl_simple_n2.pack(fill=tk.X)

        frame_glosario = tk.LabelFrame(contenedor, text=" Glosario: toca una palabra para entenderla ", font=("Arial", 11, "bold"), bg="#1e1e2e", fg="#89b4fa", padx=10, pady=8)
        frame_glosario.pack(fill=tk.X, padx=15, pady=5)
        for clave in GLOSARIO_N2:
            tk.Button(frame_glosario, text=clave, font=("Arial", 9, "bold"), bg="#313244", fg="#cdd6f4", activebackground="#45475a", activeforeground="#f9e2af", command=lambda k=clave: self.mostrar_ventana_explicativa(*GLOSARIO_N2[k])).pack(side=tk.LEFT, padx=4, pady=2)

        frame_resumen = tk.LabelFrame(contenedor, text=" Resultados: cuanto espero cada programa ", font=("Arial", 11, "bold"), bg="#1e1e2e", fg="#a6e3a1", padx=10, pady=8)
        frame_resumen.pack(fill=tk.X, padx=15, pady=8)
        self.lbl_resumen_n2 = tk.Label(frame_resumen, text="Los resultados apareceran aqui cuando termine la simulacion.", font=("Courier New", 10), bg="#181825", fg="#cdd6f4", anchor=tk.W, justify=tk.LEFT, wraplength=1100, padx=10, pady=8)
        self.lbl_resumen_n2.pack(fill=tk.X)

        tk.Label(contenedor, text="Bitacora del algoritmo Round Robin (paso a paso):", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(anchor=tk.W, padx=15)
        self.txt_logs_cpu = tk.Text(contenedor, bg="#11111b", fg="#94e2d5", font=("Courier New", 9), height=8, state=tk.DISABLED)
        self.txt_logs_cpu.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        self.dibujar_escenario_base_n2()
        self.dibujar_gantt_inicial_n2()

    def log_nivel2(self, texto):
        self.txt_logs_cpu.config(state=tk.NORMAL)
        self.txt_logs_cpu.insert(tk.END, f"> {texto}\n")
        self.txt_logs_cpu.see(tk.END)
        self.txt_logs_cpu.config(state=tk.DISABLED)

    def limpiar_log_n2(self):
        self.txt_logs_cpu.config(state=tk.NORMAL)
        self.txt_logs_cpu.delete("1.0", tk.END)
        self.txt_logs_cpu.config(state=tk.DISABLED)

    def cambiar_velocidad_n2(self, valor):
        try:
            self.velocidad_n2 = float(valor)
        except ValueError:
            self.velocidad_n2 = 1.0

    def cambiar_modo_paso_n2(self):
        self.modo_paso_n2 = self.var_paso_n2.get()
        if self.modo_paso_n2:
            self.btn_siguiente_n2.config(state=tk.NORMAL)
        else:
            self.btn_siguiente_n2.config(state=tk.DISABLED)
            self.evento_paso_n2.set()

    def siguiente_paso_n2(self):
        self.evento_paso_n2.set()

    def alternar_pausa_n2(self):
        self.pausa_n2 = not self.pausa_n2
        self.btn_pausa_n2.config(text="Continuar" if self.pausa_n2 else "Pausar", bg="#a6e3a1" if self.pausa_n2 else "#f9e2af")

    def dormir_n2(self, segundos):
        restante = segundos / max(0.1, self.velocidad_n2)
        while restante > 0:
            while self.pausa_n2:
                time.sleep(0.1)
            paso = min(0.05, restante)
            time.sleep(paso)
            restante -= paso

    def esperar_paso_n2(self):
        if self.modo_paso_n2:
            self.evento_paso_n2.clear()
            while self.modo_paso_n2 and not self.evento_paso_n2.wait(0.1):
                pass
        while self.pausa_n2:
            time.sleep(0.1)

    def set_concepto_n2(self, titulo, tecnico, simple):
        self.lbl_concepto_titulo_n2.config(text=titulo)
        self.lbl_concepto_cpu.config(text=tecnico)
        self.lbl_simple_n2.config(text=f"En palabras simples: {simple}")

    def dibujar_escenario_base_n2(self):
        c = self.canvas_cpu
        c.delete("all")

        c.create_text(20, 16, text="COLA DE LISTOS (programas esperando su turno)", font=("Arial", 10, "bold"), fill="#f9e2af", anchor=tk.W)
        c.create_rectangle(20, 35, 640, 215, fill="#181825", outline="#585b70", dash=(4, 4))
        etiquetas = ["Siguiente", "2do", "3ro", "4to"]
        for i in range(4):
            sx = 30 + i * 148
            c.create_rectangle(sx, 75, sx + 130, 175, fill="", outline="#45475a", dash=(2, 4))
            c.create_text(sx + 65, 192, text=etiquetas[i], font=("Arial", 9, "bold"), fill="#6c7086")
        c.create_text(330, 55, text="Aqui apareceran tus programas abiertos", font=("Arial", 10, "italic"), fill="#6c7086", tags="ayuda_cola")

        c.create_line(645, 125, 715, 125, fill="#f9e2af", width=4, arrow=tk.LAST)
        c.create_text(680, 108, text="entra", font=("Arial", 9, "bold"), fill="#f9e2af")

        c.create_rectangle(720, 35, 940, 255, fill="#2a2a3c", outline="#f38ba8", width=3)
        c.create_text(830, 50, text="CPU (el cocinero)", font=("Arial", 11, "bold"), fill="#f38ba8")
        c.create_text(830, 125, text="CPU libre\nsin trabajo", font=("Arial", 11, "bold"), fill="#6c7086", justify=tk.CENTER, tags="cpulibre")
        self.texto_quantum_n2 = c.create_text(830, 205, text="Turno restante: -", font=("Arial", 9, "bold"), fill="#cdd6f4")
        c.create_rectangle(740, 215, 920, 230, fill="#45475a", outline="#cdd6f4")
        self.barra_quantum_n2 = c.create_rectangle(740, 215, 740, 230, fill="#a6e3a1", outline="")
        self.texto_reloj_n2 = c.create_text(830, 243, text="Reloj: 0 s", font=("Arial", 9, "bold"), fill="#f9e2af")

        c.create_text(1060, 16, text="TERMINADOS", font=("Arial", 10, "bold"), fill="#a6e3a1")
        c.create_rectangle(960, 35, 1160, 255, fill="#181825", outline="#585b70", dash=(4, 4))

    def dibujar_gantt_inicial_n2(self):
        g = self.canvas_gantt
        g.delete("all")
        g.create_text(590, 65, text="La linea de tiempo de la CPU (diagrama de Gantt) se ira dibujando aqui durante la simulacion.", font=("Arial", 11, "italic"), fill="#6c7086")

    def dibujar_tarjeta_n2(self, p, activa=False):
        c = self.canvas_cpu
        c.delete(p["tag"])
        x, y = p["x"], p["y"]
        borde = "#ffffff" if activa else "#11111b"
        grosor = 4 if activa else 2
        c.create_rectangle(x, y, x + 130, y + 100, fill=p["color"], outline=borde, width=grosor, tags=p["tag"])
        c.create_text(x + 65, y + 16, text=f"{p['label']}: {p['name'][:13]}", font=("Arial", 9, "bold"), fill="#11111b", tags=p["tag"])
        c.create_text(x + 65, y + 36, text=f"Rafaga total: {p['burst']}s", font=("Arial", 8), fill="#11111b", tags=p["tag"])
        c.create_rectangle(x + 10, y + 50, x + 120, y + 64, fill="#181825", outline="#11111b", tags=p["tag"])
        hecho = p["burst"] - p["rest"]
        if hecho > 0:
            c.create_rectangle(x + 10, y + 50, x + 10 + 110 * hecho / p["burst"], y + 64, fill="#cdd6f4", outline="", tags=p["tag"])
        c.create_text(x + 65, y + 82, text=f"Falta: {p['rest']}s", font=("Arial", 9, "bold"), fill="#11111b", tags=p["tag"])

    def mover_tarjetas_n2(self, movimientos, pasos=12):
        deltas = [(p, nx - p["x"], ny - p["y"]) for p, nx, ny in movimientos]
        for _ in range(pasos):
            for p, dx, dy in deltas:
                if dx or dy:
                    self.canvas_cpu.move(p["tag"], dx / pasos, dy / pasos)
            self.dormir_n2(0.03)
        for p, nx, ny in movimientos:
            p["x"], p["y"] = nx, ny

    def actualizar_barra_quantum_n2(self, restante, total):
        fraccion = max(0, restante) / total if total else 0
        color = "#a6e3a1" if fraccion > 0.5 else ("#f9e2af" if fraccion > 0 else "#f38ba8")
        self.canvas_cpu.coords(self.barra_quantum_n2, 740, 215, 740 + 180 * fraccion, 230)
        self.canvas_cpu.itemconfig(self.barra_quantum_n2, fill=color)
        self.canvas_cpu.itemconfig(self.texto_quantum_n2, text=f"Turno restante: {max(0, restante)}s de {total}s")

    def preparar_gantt_n2(self, procesos):
        g = self.canvas_gantt
        g.delete("all")
        total = sum(p["burst"] for p in procesos)
        self.celda_gantt_n2 = min(44, 1080 / total)
        g.create_text(20, 14, text="LINEA DE TIEMPO DE LA CPU: cada cuadro = 1 segundo de trabajo. Asi se ve quien uso la CPU y cuando.", font=("Arial", 10, "bold"), fill="#f9e2af", anchor=tk.W)
        for i, p in enumerate(procesos):
            x = 20 + i * 285
            g.create_rectangle(x, 30, x + 14, 44, fill=p["color"], outline="")
            g.create_text(x + 20, 37, text=f"{p['label']} = {p['name'][:18]}", font=("Arial", 9), fill="#cdd6f4", anchor=tk.W)
        g.create_text(1160, 37, text="Linea roja CS = cambio de contexto", font=("Arial", 9, "bold"), fill="#f38ba8", anchor=tk.E)
        g.create_text(28, 78, text="CPU", font=("Arial", 10, "bold"), fill="#cdd6f4")
        g.create_text(50, 112, text="0", font=("Arial", 8), fill="#cdd6f4")

    def agregar_bloque_gantt_n2(self, p, t, cambio):
        g = self.canvas_gantt
        cel = self.celda_gantt_n2
        x1 = 50 + t * cel
        x2 = x1 + cel
        g.create_rectangle(x1, 58, x2, 98, fill=p["color"], outline="#11111b", width=2)
        g.create_text((x1 + x2) / 2, 78, text=p["label"], font=("Arial", 9, "bold"), fill="#11111b")
        g.create_text(x2, 112, text=str(t + 1), font=("Arial", 8), fill="#cdd6f4")
        if cambio:
            g.create_line(x1, 52, x1, 104, fill="#f38ba8", width=3)
            g.create_text(x1, 47, text="CS", font=("Arial", 8, "bold"), fill="#f38ba8")

    def iniciar_simulacion_n2(self):
        if self.simulando_n2:
            return
        self.simulando_n2 = True
        self.quantum_n2 = int(self.cmb_quantum_n2.get().split()[0])
        self.modo_paso_n2 = self.var_paso_n2.get()
        self.pausa_n2 = False
        self.btn_pausa_n2.config(text="Pausar", bg="#f9e2af")
        self.btn_sim_n2.config(state=tk.DISABLED)
        self.cmb_quantum_n2.config(state=tk.DISABLED)
        threading.Thread(target=self._simulacion_n2, daemon=True).start()

    def _simulacion_n2(self):
        try:
            self.limpiar_log_n2()
            self.dibujar_escenario_base_n2()
            self.dibujar_gantt_inicial_n2()
            self.lbl_resumen_n2.config(text="Los resultados apareceran aqui cuando termine la simulacion.")
            q = self.quantum_n2

            self.lbl_status_cpu.config(text="PASO 1: Buscando los programas que tienes abiertos...")
            self.set_concepto_n2(
                "PASO 1: Buscamos tus programas abiertos",
                "El Sistema Operativo escanea las ventanas activas de tu escritorio. Cada una es un PROCESO que quiere usar la CPU.",
                "son los 'pedidos' que le llegaron al cocinero. Vamos a ver cuales tienes abiertos ahora mismo.")
            self.log_nivel2("PASO 1: Escaneando el escritorio para encontrar ventanas activas reales...")
            self.esperar_paso_n2()

            reales = self.obtener_procesos_ventanas_reales(limite=4)
            procesos = []
            for r in reales:
                rafaga = max(3, min(7, r["mem"] // 40000 + 2))
                procesos.append({"name": r["name"], "mem": r["mem"], "burst": rafaga})

            extras = ["explorer.exe", "notepad.exe", "spotify.exe"]
            agregados = 0
            while len(procesos) < 3 and agregados < len(extras):
                procesos.append({"name": extras[agregados], "mem": 0, "burst": random.randint(3, 6)})
                agregados += 1
            if agregados:
                self.log_nivel2("AVISO: Tenias pocas ventanas abiertas, se agregaron programas de ejemplo para que la demostracion sea clara.")

            for i, p in enumerate(procesos):
                p["id"] = i
                p["label"] = f"P{i + 1}"
                p["color"] = self.colores_n2[i % len(self.colores_n2)]
                p["rest"] = p["burst"]
                p["tag"] = f"proc_{i}"
                p["x"] = 30 + i * 148
                p["y"] = 75

            self.lbl_status_cpu.config(text="PASO 2: Calculamos cuanto trabajo necesita cada programa (su rafaga).")
            self.set_concepto_n2(
                "PASO 2: Cada programa tiene una RAFAGA",
                "La rafaga (burst time) es el tiempo total que un proceso necesita de CPU para terminar. Aqui la calculamos segun cuanta RAM consume cada ventana real: a mas RAM, mas trabajo.",
                "cada pedido tiene un tamaño. Un pedido grande tarda mas en cocinarse que uno pequeño.")
            self.canvas_cpu.delete("ayuda_cola")
            self.preparar_gantt_n2(procesos)
            for p in procesos:
                self.dibujar_tarjeta_n2(p)
                origen = f"{p['mem']:,} KB en RAM" if p["mem"] else "programa de ejemplo"
                self.log_nivel2(f"   -> {p['label']} = {p['name']} ({origen}) -> rafaga de {p['burst']}s")
                self.dormir_n2(0.35)
            self.esperar_paso_n2()

            self.lbl_status_cpu.config(text="PASO 3: Los programas forman la COLA DE LISTOS, esperando su turno.")
            self.set_concepto_n2(
                "PASO 3: Se forma la COLA DE LISTOS (Ready Queue)",
                "Todos los procesos que estan preparados pero aun no tienen la CPU esperan en esta fila, en el orden en que fueron detectados.",
                "es la fila de pedidos pegados en la ventanilla. El primero de la izquierda sera el primero en cocinarse.")
            self.log_nivel2("PASO 3: Se arma la Cola de Listos (Ready Queue) en el orden en que se detectaron.")
            self.esperar_paso_n2()

            self.lbl_status_cpu.config(text=f"PASO 4: Empieza Round Robin. Cada turno (quantum) dura {q} segundo(s).")
            self.set_concepto_n2(
                f"PASO 4: Round Robin con QUANTUM de {q}s",
                f"Cada proceso recibe como maximo {q} segundo(s) de CPU. Si no termina en ese tiempo, la CPU se lo quita y pasa al siguiente.",
                f"el cocinero pone un cronometro de {q} segundo(s) por pedido. Cuando suena, cambia de pedido aunque no haya terminado.")
            self.log_nivel2(f"PASO 4: Empieza el algoritmo Round Robin: cada app recibe un quantum de {q}s de CPU.")
            self.esperar_paso_n2()

            cola = list(procesos)
            reloj = 0
            cambios = 0
            ultimo = None
            fin = {}
            terminados = 0

            while cola:
                p = cola.pop(0)
                self.lbl_status_cpu.config(text=f"La CPU atiende a {p['label']} ({p['name']}).")
                self.set_concepto_n2(
                    f"CAMBIO DE CONTEXTO: entra {p['label']} ({p['name']})",
                    f"El nucleo guarda el estado del proceso anterior y carga los registros de '{p['name']}' para que continue exactamente donde se quedo.",
                    "el cocinero lee la nota del pedido que le toca y retoma su trabajo justo donde lo dejo.")
                self.log_nivel2(f"CAMBIO DE CONTEXTO: el nucleo carga el estado de {p['label']} ({p['name']}) y le da la CPU.")
                self.esperar_paso_n2()

                self.canvas_cpu.delete("cpulibre")
                movimientos = [(p, 765, 70)]
                for i, otro in enumerate(cola):
                    movimientos.append((otro, 30 + i * 148, 75))
                self.mover_tarjetas_n2(movimientos)

                cambio_flag = ultimo is not None and ultimo is not p
                if cambio_flag:
                    cambios += 1

                self.dibujar_tarjeta_n2(p, activa=True)
                self.actualizar_barra_quantum_n2(q, q)
                uso = min(q, p["rest"])

                for t in range(uso):
                    self.dormir_n2(0.7)
                    p["rest"] -= 1
                    reloj += 1
                    self.agregar_bloque_gantt_n2(p, reloj - 1, cambio_flag and t == 0)
                    self.actualizar_barra_quantum_n2(q - (t + 1), q)
                    self.dibujar_tarjeta_n2(p, activa=True)
                    self.canvas_cpu.itemconfig(self.texto_reloj_n2, text=f"Reloj: {reloj} s")
                    self.log_nivel2(f"   -> {p['label']} uso 1s de CPU (segundo {reloj}). Le faltan {p['rest']}s.")

                if p["rest"] > 0:
                    self.lbl_status_cpu.config(text=f"Se acabo el turno de {p['label']}. Vuelve al final de la fila.")
                    self.set_concepto_n2(
                        f"APROPIACION (Preemption): {p['label']} pierde su turno",
                        f"Como '{p['name']}' no termino dentro de su quantum, la CPU se lo quita y lo manda al final de la Cola de Listos. Aun le faltan {p['rest']}s de trabajo.",
                        "suena el cronometro: el cocinero deja el pedido a medias y lo pone al final de la fila para atender a los demas.")
                    self.log_nivel2(f"APROPIACION: se acabo el quantum y a {p['label']} aun le falta trabajo -> regresa al final de la cola.")
                    self.esperar_paso_n2()
                    self.dibujar_tarjeta_n2(p, activa=False)
                    cola.append(p)
                    movimientos = [(o, 30 + i * 148, 75) for i, o in enumerate(cola)]
                    self.mover_tarjetas_n2(movimientos)
                else:
                    anticipada = uso < q
                    extra_t = f" Termino antes de gastar todo su turno ({uso}s de {q}s), asi que cede la CPU voluntariamente." if anticipada else ""
                    self.lbl_status_cpu.config(text=f"¡{p['label']} ({p['name']}) completo todo su trabajo!")
                    self.set_concepto_n2(
                        f"TERMINACION: {p['label']} termino",
                        f"'{p['name']}' ya cumplio toda su rafaga, asi que el kernel lo saca de la cola para siempre y libera la CPU.{extra_t}",
                        "el pedido quedo listo y sale de la cocina. El cocinero queda libre para el siguiente.")
                    self.log_nivel2(f"TERMINACION: {p['label']} termino su rafaga en el segundo {reloj} -> el nucleo lo saca de la cola.")
                    self.esperar_paso_n2()
                    self.dibujar_tarjeta_n2(p, activa=False)
                    self.mover_tarjetas_n2([(p, 985, 70)])
                    self.canvas_cpu.delete(p["tag"])
                    yc = 70 + terminados * 42
                    self.canvas_cpu.create_rectangle(970, yc, 1150, yc + 34, fill=p["color"], outline="#11111b", width=2)
                    self.canvas_cpu.create_text(1060, yc + 17, text=f"✓ {p['label']} {p['name'][:11]} ({reloj}s)", font=("Arial", 8, "bold"), fill="#11111b")
                    terminados += 1
                    fin[p["id"]] = reloj

                self.actualizar_barra_quantum_n2(0, q)
                self.canvas_cpu.create_text(830, 125, text="CPU libre\nsin trabajo", font=("Arial", 11, "bold"), fill="#6c7086", justify=tk.CENTER, tags="cpulibre")
                ultimo = p

            lineas = [f"{'Programa':<26}{'Rafaga':>8}{'Termino en':>12}{'Espero':>9}", "-" * 55]
            espera_total = 0
            for p in procesos:
                retorno = fin[p["id"]]
                espera = retorno - p["burst"]
                espera_total += espera
                nombre = f"{p['label']} {p['name'][:20]}"
                lineas.append(f"{nombre:<26}{str(p['burst']) + 's':>8}{str(retorno) + 's':>12}{str(espera) + 's':>9}")
            promedio = espera_total / len(procesos)
            lineas.append("")
            lineas.append(f"Espera promedio: {promedio:.1f}s | Cambios de contexto: {cambios} | Tiempo total: {reloj}s | Quantum: {q}s")
            lineas.append("'Espero' = tiempo que el programa estuvo en la fila SIN usar la CPU (termino en - su rafaga).")
            lineas.append("Prueba otro quantum y compara: turnos chicos = mas cambios de contexto; turnos grandes = se parece a 'el primero que llega se atiende completo'.")
            self.lbl_resumen_n2.config(text="\n".join(lineas))

            self.lbl_status_cpu.config(text="Fila vacia. La CPU repartio de forma justa el tiempo entre tus ventanas.")
            self.set_concepto_n2(
                "FIN: Round Robin repartio la CPU de forma justa",
                "Cada proceso recibio turnos iguales de CPU hasta completar toda su rafaga. Ninguno se quedo esperando para siempre.",
                "todos los pedidos salieron de la cocina y ninguno quedo olvidado. Revisa la linea de tiempo y la tabla de resultados.")
            self.log_nivel2("PASO FINAL: Cola vacia. Todas las apps recibieron CPU de forma equitativa (Round Robin).")

            self.nivel2_usado = True
            self.root.after(0, lambda: self.completar_nivel(2))
        finally:
            self.simulando_n2 = False
            self.pausa_n2 = False
            self.root.after(0, lambda: self.btn_sim_n2.config(state=tk.NORMAL, text="Repetir simulacion"))
            self.root.after(0, lambda: self.cmb_quantum_n2.config(state="readonly"))
            self.root.after(0, lambda: self.btn_pausa_n2.config(text="Pausar", bg="#f9e2af"))

    def construir_nivel_3(self):
        contenedor = self.crear_area_desplazable(self.tab3)

        self.agregar_introduccion(contenedor, "Que hace este nivel",
            "La RAM de tu computador solo tiene 12 bloques disponibles en esta simulacion. Cuando tus ventanas "
            "reales ocupan mas espacio del que existe, el Sistema Operativo usa tu disco duro como una memoria "
            "de respaldo llamada 'memoria virtual' o 'swap'. Presiona el boton y observa, bloque por bloque, "
            "como el Administrador de Memoria revisa cada celda de la RAM, la reserva si esta libre, y cuando "
            "ya no queda espacio, veras una animacion real de la pagina viajando hacia el disco duro mientras "
            "se escribe un archivo de verdad en tu sistema.\n\n"
            "PARA DESBLOQUEAR EL NIVEL 4: deja que el mapeo de memoria termine por completo.")

        tk.Button(contenedor, text="Mapear consumo actual de mis Ventanas", font=("Arial", 10, "bold"), bg="#a6e3a1", fg="#11111b", command=self.cargar_ram_con_datos_reales).pack(pady=5)

        self.canvas_ram3 = tk.Canvas(contenedor, width=950, height=280, bg="#313244", highlightthickness=0)
        self.canvas_ram3.pack(pady=10)
        self.lbl_status_ram3 = tk.Label(contenedor, text="Presiona el boton para leer tus ventanas abiertas y rellenar los bloques.", font=("Arial", 11, "italic"), bg="#1e1e2e", fg="#cdd6f4")
        self.lbl_status_ram3.pack(pady=5)

        tk.Label(contenedor, text="Bitacora de Memoria Virtual / Paginacion (aqui SI se usa tu disco duro real):", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#fab387").pack(anchor=tk.W, padx=15)
        self.txt_logs_ram3 = tk.Text(contenedor, bg="#11111b", fg="#fab387", font=("Courier New", 9), height=7, state=tk.DISABLED)
        self.txt_logs_ram3.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        self.redibujar_panel_ram_mapeado()

    def log_nivel3(self, texto):
        self.txt_logs_ram3.config(state=tk.NORMAL)
        self.txt_logs_ram3.insert(tk.END, f"> {texto}\n")
        self.txt_logs_ram3.see(tk.END)
        self.txt_logs_ram3.config(state=tk.DISABLED)

    def redibujar_panel_ram_mapeado(self):
        self.canvas_ram3.delete("ram_m")
        self.canvas_ram3.delete("check_mark_n3")
        self.canvas_ram3.delete("token_transfer_n3")
        for i in range(12):
            col = i % 4
            row = i // 4
            x1, y1 = 30 + col * 115, 60 + row * 65
            x2, y2 = x1 + 100, y1 + 55
            info_bloque = self.ram_blocks_sim[i]

            color = info_bloque["color"] if info_bloque else "#1e1e2e"
            texto = info_bloque["text"] if info_bloque else "[Disponible]"

            self.canvas_ram3.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cdd6f4", tags="ram_m")
            self.canvas_ram3.create_text((x1+x2)/2, (y1+y2)/2, text=texto, fill="#11111b" if info_bloque else "#6c7086", font=("Arial", 8, "bold"), tags="ram_m")

        self.canvas_ram3.create_rectangle(520, 40, 920, 240, fill="#181825", outline="#fab387", dash=(4, 4), tags="ram_m")
        self.canvas_ram3.create_text(720, 60, text="DISCO DURO AUXILIAR (Memoria Virtual / Swap Real)", font=("Arial", 11, "bold"), fill="#fab387", tags="ram_m")

        for idx, block in enumerate(self.virtual_memory):
            vy1 = 95 + idx * 32
            self.canvas_ram3.create_rectangle(540, vy1, 900, vy1+24, fill="#fab387", tags="ram_m")
            self.canvas_ram3.create_text(720, vy1+12, text=f"Volcado: {block}", font=("Arial", 9, "bold"), fill="#11111b", tags="ram_m")

    def marcar_bloque_verificando_n3(self, indice, color):
        col = indice % 4
        row = indice // 4
        x1, y1 = 30 + col * 115, 60 + row * 65
        x2, y2 = x1 + 100, y1 + 55
        self.canvas_ram3.delete("check_mark_n3")
        self.canvas_ram3.create_rectangle(x1, y1, x2, y2, outline=color, width=5, tags="check_mark_n3")
        self.canvas_ram3.update()

    def animar_transferencia_disco_n3(self, nombre_proceso):
        self.canvas_ram3.delete("token_transfer_n3")
        token = self.canvas_ram3.create_oval(465, 130, 495, 160, fill="#f38ba8", outline="#11111b", width=2, tags="token_transfer_n3")
        etiqueta = self.canvas_ram3.create_text(480, 175, text=f"Enviando\n{nombre_proceso[:10]}", font=("Arial", 8, "bold"), fill="#f38ba8", tags="token_transfer_n3")
        pasos_animacion = 14
        for _ in range(pasos_animacion):
            self.canvas_ram3.move(token, 4, 0)
            self.canvas_ram3.move(etiqueta, 4, 0)
            self.canvas_ram3.update()
            time.sleep(0.05)
        time.sleep(0.3)
        self.canvas_ram3.delete("token_transfer_n3")

    def cargar_ram_con_datos_reales(self):
        threading.Thread(target=self._cargar_ram_hilo_n3, daemon=True).start()

    def _cargar_ram_hilo_n3(self):
        self.txt_logs_ram3.config(state=tk.NORMAL)
        self.txt_logs_ram3.delete("1.0", tk.END)
        self.txt_logs_ram3.config(state=tk.DISABLED)

        self.lbl_status_ram3.config(text="Escaneando tus ventanas activas...")
        self.log_nivel3("PASO 1: Escaneando tus ventanas activas y su consumo de RAM real...")
        time.sleep(0.6)
        procesos = self.obtener_procesos_ventanas_reales(limite=4)
        self.ram_blocks_sim = [None] * 12
        self.redibujar_panel_ram_mapeado()

        for archivo in self.archivos_swap_creados:
            try:
                if os.path.exists(archivo):
                    os.remove(archivo)
            except Exception:
                pass
        self.archivos_swap_creados = []
        self.virtual_memory = []

        colores = ["#89b4fa", "#cba6f7", "#f9e2af", "#94e2d5"]
        casillero_actual = 0

        self.log_nivel3("PASO 2: El Administrador de Memoria revisara la RAM bloque por bloque (solo hay 12 bloques).")
        time.sleep(0.6)

        for idx, p in enumerate(procesos):
            bloques_a_ocupar = max(1, min(4, p["mem"] // 25000))
            self.lbl_status_ram3.config(text=f"Acomodando la ventana '{p['name']}' ({p['mem']:,} KB) en la memoria...")
            self.log_nivel3(f"Procesando ventana '{p['name']}': necesita {bloques_a_ocupar} bloque(s) de RAM.")
            time.sleep(0.4)

            for _ in range(bloques_a_ocupar):
                if casillero_actual < 12:
                    self.log_nivel3(f"   -> Verificando Bloque {casillero_actual}... LIBRE. Asignando a '{p['name']}'.")
                    self.marcar_bloque_verificando_n3(casillero_actual, "#f9e2af")
                    time.sleep(0.5)
                    self.ram_blocks_sim[casillero_actual] = {"color": colores[idx % len(colores)], "text": p["name"][:12]}
                    self.redibujar_panel_ram_mapeado()
                    casillero_actual += 1
                    time.sleep(0.4)
                else:
                    self.log_nivel3("   -> Verificando bloques libres... TODOS OCUPADOS. La RAM esta llena.")
                    time.sleep(0.5)
                    if p["name"] not in self.virtual_memory:
                        self.lbl_status_ram3.config(text=f"¡RAM llena! Transfiriendo '{p['name']}' al disco duro (swap)...")
                        self.log_nivel3(f"PASO 3: ¡RAM LLENA! El OS activa la MEMORIA VIRTUAL para '{p['name']}'.")
                        self.animar_transferencia_disco_n3(p["name"])

                        tamano_pagina_kb = max(4, p["mem"] // 200)
                        ruta_archivo = os.path.join(self.carpeta_swap, f"pagina_{p['name']}_{idx}.swap")
                        try:
                            with open(ruta_archivo, "wb") as f:
                                f.write(os.urandom(tamano_pagina_kb * 1024))
                            tamano_real = os.path.getsize(ruta_archivo)
                            self.archivos_swap_creados.append(ruta_archivo)
                            self.log_nivel3(f"PASO 4: Se escribio de verdad en tu disco duro: {ruta_archivo}")
                            self.log_nivel3(f"        Tamano real en disco: {tamano_real:,} bytes ({tamano_real/1024:.1f} KB).")
                            self.virtual_memory.append(p["name"][:12])
                            self.redibujar_panel_ram_mapeado()
                            time.sleep(0.5)
                        except Exception as e:
                            self.log_nivel3(f"ERROR al escribir la pagina en disco: {e}")

        if not self.virtual_memory:
            self.log_nivel3("RESULTADO: Todas tus ventanas cupieron en RAM, no fue necesario usar el disco duro.")
        else:
            self.log_nivel3("PASO 5: El OS guarda un 'mapa de paginas' para saber en que archivo quedo cada proceso.")
            self.log_nivel3("PASO FINAL: Cuando esa ventana vuelva a necesitarse, el OS leera el archivo del disco")
            self.log_nivel3("            y lo traera de nuevo a la RAM (esto se llama 'swap in', y es mas lento que la RAM).")

        self.lbl_status_ram3.config(text="¡Mapeo Real de Ventanas Completado! Revisa la bitacora para ver el uso real del disco.")
        self.redibujar_panel_ram_mapeado()

        self.nivel3_usado = True
        self.root.after(0, lambda: self.completar_nivel(3))

    def construir_nivel_4(self):
        contenedor = self.crear_area_desplazable(self.tab4)

        self.agregar_introduccion(contenedor, "Que hace este nivel",
            "Cuando la memoria esta llena y llega un proceso nuevo, el Sistema Operativo debe decidir a cual "
            "ventana sacrificar. El algoritmo FIFO (First In, First Out) siempre elige a la ventana que lleva "
            "MAS TIEMPO abierta, sin importar cuanta RAM use. Este nivel aplica esa regla de verdad sobre tu "
            "computador: al activar el Modo de Control Real, este stand solo permitira un maximo de 3 ventanas "
            "abiertas al mismo tiempo. Si abres una cuarta, el sistema la detectara casi al instante y te "
            "avisara UNA sola vez para cerrar de verdad la ventana mas antigua; si dices que no, no volvera a "
            "insistir con la misma ventana, solo avisara de nuevo cuando aparezca otra ventana distinta.\n\n"
            "PARA DESBLOQUEAR EL NIVEL 5: activa el modo y responde (Si o No) a una advertencia de limite. "
            "Si no quieres abrir ventanas reales, usa el boton de demostracion: simula la advertencia sin cerrar nada.")

        tk.Label(contenedor, text="Al activar este modo, el stand vigilara tu computador en segundo plano cada 1.5 segundos. Si detecta una cuarta ventana abierta, te preguntara UNA sola vez si quieres cerrar de verdad la mas antigua para dejarle espacio a la nueva. Las ventanas que ya estaban abiertas ANTES de activar el modo no generaran avisos: solo se avisa cuando aparece algo realmente nuevo despues de activar.", font=("Arial", 9), bg="#1e1e2e", fg="#cdd6f4", wraplength=1100, justify=tk.LEFT).pack(anchor=tk.W, padx=20, pady=(0, 10))

        frame_botones = tk.Frame(contenedor, bg="#1e1e2e")
        frame_botones.pack(pady=5)

        self.btn_monitor_n4 = tk.Button(frame_botones, text="Activar Modo de Control Real", font=("Arial", 11, "bold"), bg="#94e2d5", fg="#11111b", command=self.alternar_monitor_n4)
        self.btn_monitor_n4.pack(side=tk.LEFT, padx=8)

        tk.Button(frame_botones, text="Simular ventana nueva (demostracion segura)", font=("Arial", 11, "bold"), bg="#f9e2af", fg="#11111b", command=self.simular_ventana_n4).pack(side=tk.LEFT, padx=8)

        self.canvas_monitor_n4 = tk.Canvas(contenedor, width=950, height=160, bg="#313244", highlightthickness=0)
        self.canvas_monitor_n4.pack(pady=10)

        self.lbl_status_monitor_n4 = tk.Label(contenedor, text="Modo de Control Real desactivado.", font=("Arial", 11, "italic"), bg="#1e1e2e", fg="#cdd6f4")
        self.lbl_status_monitor_n4.pack(pady=5)

        tk.Label(contenedor, text="Bitacora del Modo de Control Real:", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(anchor=tk.W, padx=15)
        self.txt_logs_monitor_n4 = tk.Text(contenedor, bg="#11111b", fg="#f9e2af", font=("Courier New", 9), height=10, state=tk.DISABLED)
        self.txt_logs_monitor_n4.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        self.renderizar_cola_monitor_n4()

    def log_nivel4_monitor(self, texto):
        self.txt_logs_monitor_n4.config(state=tk.NORMAL)
        self.txt_logs_monitor_n4.insert(tk.END, f"> {texto}\n")
        self.txt_logs_monitor_n4.see(tk.END)
        self.txt_logs_monitor_n4.config(state=tk.DISABLED)

    def renderizar_cola_monitor_n4(self):
        self.canvas_monitor_n4.delete("all")
        for i in range(self.limite_ventanas_n4):
            x1 = 60 + i * 280
            self.canvas_monitor_n4.create_rectangle(x1, 20, x1+240, 120, fill="#181825", outline="#585b70", width=2, dash=(4, 4))
            if i < len(self.cola_monitor_n4):
                elem = self.cola_monitor_n4[i]
                color = "#f38ba8" if i == 0 else "#94e2d5"
                self.canvas_monitor_n4.create_rectangle(x1, 20, x1+240, 120, fill=color, outline="#11111b", width=2)
                self.canvas_monitor_n4.create_text(x1+120, 60, text=f"{elem['name']}\nPID {elem['pid']}", font=("Arial", 10, "bold"), fill="#11111b")
                if i == 0:
                    self.canvas_monitor_n4.create_text(x1+120, 135, text="Mas antigua", font=("Arial", 9, "bold"), fill="#f38ba8")
            else:
                self.canvas_monitor_n4.create_text(x1+120, 70, text="Slot libre", font=("Arial", 10, "bold"), fill="#6c7086")

    def alternar_monitor_n4(self):
        if not self.monitor_n4_activo:
            self.monitor_n4_activo = True
            self.btn_monitor_n4.config(text="Desactivar Modo de Control Real", bg="#f38ba8")
            self.lbl_status_monitor_n4.config(text="Modo de Control Real ACTIVADO. Vigilando tus ventanas...")
            threading.Thread(target=self._bucle_monitor_n4, daemon=True).start()
        else:
            self.monitor_n4_activo = False
            self.btn_monitor_n4.config(text="Activar Modo de Control Real", bg="#94e2d5")
            self.lbl_status_monitor_n4.config(text="Modo de Control Real desactivado.")
            self.log_nivel4_monitor("Modo de Control Real desactivado por el usuario.")

    def simular_ventana_n4(self):
        if not self.monitor_n4_activo:
            messagebox.showinfo("Modo desactivado", "Primero activa el Modo de Control Real y luego usa la demostracion.")
            return
        if self.advertencia_en_curso_n4:
            return
        if self.cola_monitor_n4:
            antigua = dict(self.cola_monitor_n4[0])
        else:
            antigua = {"name": "ventana_antigua.exe", "pid": "0000"}
        nueva = {"name": "ventana_nueva.exe", "pid": "9999"}
        self.advertencia_en_curso_n4 = True
        self.log_nivel4_monitor("DEMOSTRACION: se simula la aparicion de una ventana nueva con el limite ya alcanzado. No se cerrara nada real.")
        self.advertir_limite_n4(nueva, antigua, demo=True)

    def _bucle_monitor_n4(self):
        ventanas_iniciales = self.obtener_procesos_ventanas_reales(limite=20, orden="tiempo")
        self.cola_monitor_n4 = [{"name": v["name"], "pid": v["pid"]} for v in ventanas_iniciales[:self.limite_ventanas_n4]]

        self.ventanas_ignoradas_n4 = {v["pid"] for v in ventanas_iniciales[self.limite_ventanas_n4:]}

        self.log_nivel4_monitor(f"Base inicial cargada con {len(self.cola_monitor_n4)} ventana(s) reales, ordenadas por antiguedad.")
        if self.ventanas_ignoradas_n4:
            self.log_nivel4_monitor(f"Se detectaron {len(self.ventanas_ignoradas_n4)} ventana(s) que ya estaban abiertas antes de activar el modo. No generaran avisos; solo se avisara cuando abras algo nuevo.")
        self.root.after(0, self.renderizar_cola_monitor_n4)

        while self.monitor_n4_activo:
            time.sleep(1.5)
            ventanas_actuales = self.obtener_procesos_ventanas_reales(limite=20, orden="tiempo")
            pids_actuales = [v["pid"] for v in ventanas_actuales]

            antes = len(self.cola_monitor_n4)
            self.cola_monitor_n4 = [e for e in self.cola_monitor_n4 if e["pid"] in pids_actuales]
            if len(self.cola_monitor_n4) != antes:
                self.log_nivel4_monitor("Una ventana vigilada se cerro por su cuenta. Espacio liberado en la cola.")

            self.ventanas_ignoradas_n4 = {p for p in self.ventanas_ignoradas_n4 if p in pids_actuales}

            if self.advertencia_en_curso_n4:
                continue

            pids_en_cola = [e["pid"] for e in self.cola_monitor_n4]
            nuevas = [v for v in ventanas_actuales if v["pid"] not in pids_en_cola and v["pid"] not in self.ventanas_ignoradas_n4]

            if nuevas:
                nueva = nuevas[0]
                if len(self.cola_monitor_n4) < self.limite_ventanas_n4:
                    self.cola_monitor_n4.append({"name": nueva["name"], "pid": nueva["pid"]})
                    self.log_nivel4_monitor(f"Nueva ventana detectada: {nueva['name']} (PID {nueva['pid']}). Habia espacio libre, se admite directamente.")
                else:
                    mas_antigua = dict(self.cola_monitor_n4[0])
                    self.advertencia_en_curso_n4 = True
                    self.ventanas_ignoradas_n4.add(nueva["pid"])
                    self.log_nivel4_monitor(f"LIMITE ALCANZADO: se detecto '{nueva['name']}' pero ya hay {self.limite_ventanas_n4} ventanas bajo control. Se muestra una unica advertencia.")
                    self.root.after(0, lambda n=dict(nueva), a=mas_antigua: self.advertir_limite_n4(n, a))

            self.root.after(0, self.renderizar_cola_monitor_n4)

    def advertir_limite_n4(self, nueva, antigua, demo=False):
        try:
            if not self.monitor_n4_activo:
                return
            encabezado = "Limite de Ventanas Alcanzado" + (" (DEMOSTRACION)" if demo else "")
            nota = "\n\n(Es una demostracion: no se cerrara ninguna ventana real.)" if demo else ""
            confirmar = messagebox.askyesno(
                encabezado,
                f"Ya tienes {self.limite_ventanas_n4} ventanas bajo control (el maximo permitido en este modo).\n\n"
                f"La mas antigua es '{antigua['name']}' (PID {antigua['pid']}).\n\n"
                f"Se detecto una ventana nueva: '{nueva['name']}' (PID {nueva['pid']}).\n\n"
                f"¿Deseas cerrar realmente la ventana mas antigua para dejarle espacio a la nueva?{nota}"
            )
            if confirmar:
                if demo:
                    self.log_nivel4_monitor(f"DEMOSTRACION: con FIFO se habria cerrado '{antigua['name']}' por ser la mas antigua. No se cerro nada real.")
                else:
                    try:
                        resultado = subprocess.run(["taskkill", "/F", "/PID", str(antigua["pid"])], capture_output=True, text=True)
                        if resultado.returncode == 0:
                            self.log_nivel4_monitor(f"Se cerro realmente '{antigua['name']}' (PID {antigua['pid']}) por ser la mas antigua bajo el limite de {self.limite_ventanas_n4}.")
                            self.contador_expulsiones_n4 += 1
                            self.cola_monitor_n4 = [e for e in self.cola_monitor_n4 if e["pid"] != antigua["pid"]]
                            self.cola_monitor_n4.append({"name": nueva["name"], "pid": nueva["pid"]})
                            self.ventanas_ignoradas_n4.discard(nueva["pid"])
                        else:
                            self.log_nivel4_monitor(f"Windows no pudo cerrar '{antigua['name']}' (quizas requiere permisos de administrador).")
                    except Exception as e:
                        self.log_nivel4_monitor(f"Error al cerrar el proceso: {e}")
            else:
                if not demo:
                    self.contador_advertencias_rechazadas_n4 += 1
                self.log_nivel4_monitor(f"El usuario decidio NO cerrar '{antigua['name']}'. No se volvera a preguntar por '{nueva['name']}' mientras siga abierta; solo se avisara si aparece otra ventana distinta.")
            self.nivel4_usado = True
            self.completar_nivel(4)
            self.renderizar_cola_monitor_n4()
        finally:
            self.advertencia_en_curso_n4 = False

    def crear_archivos_reales_n5(self):
        os.makedirs(self.carpeta_archivos_n5, exist_ok=True)
        for nombre, texto in CONTENIDO_ARCHIVOS_N5.items():
            ruta = os.path.join(self.carpeta_archivos_n5, nombre)
            try:
                if os.path.exists(ruta):
                    os.chmod(ruta, stat.S_IREAD | stat.S_IWRITE)
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(texto)
            except Exception:
                pass

    def aplicar_atributos_reales_n5(self):
        escritura = self.permisos["Modificar"] or self.permisos["Admin"]
        modo = (stat.S_IREAD | stat.S_IWRITE) if escritura else stat.S_IREAD
        for nombre in self.archivos_n5.values():
            ruta = os.path.join(self.carpeta_archivos_n5, nombre)
            try:
                os.chmod(ruta, modo)
            except Exception:
                pass

    def ruta_archivo_n5(self):
        clave = self.cmb_archivo_n5.get()
        return os.path.join(self.carpeta_archivos_n5, self.archivos_n5[clave])

    def actualizar_info_archivo_n5(self):
        ruta = self.ruta_archivo_n5()
        try:
            tam = os.path.getsize(ruta)
            hora = time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(ruta)))
            escribible = os.access(ruta, os.W_OK)
            atributo = "Lectura y escritura" if escribible else "SOLO LECTURA (bloqueado por el sistema)"
            texto = f"Ruta real: {ruta}\nTamaño actual: {tam:,} bytes | Ultima modificacion: {hora} | Atributo real del archivo: {atributo}"
        except Exception as e:
            texto = f"No se pudo leer la informacion del archivo: {e}"
        self.lbl_info_archivo_n5.config(text=texto)

    def mostrar_en_visor_n5(self, texto, color="#cdd6f4"):
        self.txt_visor_n5.config(state=tk.NORMAL, fg=color)
        self.txt_visor_n5.delete("1.0", tk.END)
        self.txt_visor_n5.insert(tk.END, texto)
        self.txt_visor_n5.config(state=tk.DISABLED)

    def al_cambiar_archivo_n5(self, event=None):
        nombre = os.path.basename(self.ruta_archivo_n5())
        self.canvas_flujo_n5.itemconfig(self.texto_archivo_flujo_n5, text=f"Archivo REAL\n{nombre}")
        self.mostrar_en_visor_n5("Elige una accion (VER, GUARDAR o EJECUTAR) para ver aqui el resultado real.", "#6c7086")
        self.actualizar_info_archivo_n5()

    def abrir_carpeta_n5(self):
        try:
            if hasattr(os, "startfile"):
                os.startfile(self.carpeta_archivos_n5)
            else:
                messagebox.showinfo("Carpeta de archivos", f"Los archivos estan en:\n{self.carpeta_archivos_n5}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta: {e}")

    def restaurar_archivos_n5(self):
        self.crear_archivos_reales_n5()
        self.aplicar_atributos_reales_n5()
        self.mostrar_en_visor_n5("Los archivos fueron restaurados a su contenido original.", "#a6e3a1")
        self.actualizar_info_archivo_n5()
        self.log_nivel5("Se restauraron los archivos reales a su contenido original.")

    def construir_nivel_5(self):
        contenedor = self.crear_area_desplazable(self.tab5)

        self.agregar_introduccion(contenedor, "Que hace este nivel (explicado facil)",
            "Imagina un archivo como una caja con 3 candados distintos: uno para VER su contenido, otro para "
            "CAMBIARLO y otro para EJECUTARLO como programa. El Sistema Operativo revisa esos candados cada vez "
            "que alguien intenta usar el archivo.\n\n"
            "Ahora el archivo es REAL: el simulador crea de verdad dos archivos en tu disco duro (un documento de "
            "texto y un pequeño programa). Abre o cierra candados y prueba VER, GUARDAR o EJECUTAR: si el candado "
            "esta abierto, el sistema lee, escribe o ejecuta el archivo de verdad; si esta cerrado, lo bloquea "
            "(incluso el candado de escritura activa el atributo real de 'solo lectura' del archivo).")

        self.lbl_mision_n5 = tk.Label(contenedor, text="", font=("Courier New", 10, "bold"), bg="#181825", fg="#f9e2af", anchor=tk.W, justify=tk.LEFT, padx=15, pady=10)
        self.lbl_mision_n5.pack(fill=tk.X, padx=15, pady=5)

        frame_casos = tk.LabelFrame(contenedor, text=" Casos de Prueba Rapidos ", bg="#313244", fg="#cdd6f4", font=("Arial", 11, "bold"), padx=15, pady=10)
        frame_casos.pack(pady=10, fill=tk.X, padx=20)

        self.casos_permiso = {
            "Usuario normal - Solo lectura": {"Ver": True, "Modificar": False, "Ejecutar": False, "Admin": False},
            "Usuario normal - Sin ningun permiso": {"Ver": False, "Modificar": False, "Ejecutar": False, "Admin": False},
            "Usuario con permiso total": {"Ver": True, "Modificar": True, "Ejecutar": True, "Admin": False},
            "Administrador del sistema": {"Ver": True, "Modificar": True, "Ejecutar": True, "Admin": True},
            "Archivo de sistema protegido (bloqueado)": {"Ver": True, "Modificar": False, "Ejecutar": False, "Admin": False},
        }

        self.cmb_caso = ttk.Combobox(frame_casos, font=("Arial", 10), width=38, state="readonly")
        self.cmb_caso['values'] = list(self.casos_permiso.keys())
        self.cmb_caso.current(0)
        self.cmb_caso.pack(side=tk.LEFT, padx=5)

        tk.Button(frame_casos, text="Aplicar Caso de Prueba", font=("Arial", 10, "bold"), bg="#cba6f7", fg="#11111b", command=self.aplicar_caso_permiso).pack(side=tk.LEFT, padx=10)

        frame_candados = tk.LabelFrame(contenedor, text=" Interruptores de Permisos ", bg="#313244", fg="#cdd6f4", font=("Arial", 11, "bold"), padx=20, pady=10)
        frame_candados.pack(pady=10, fill=tk.X, padx=20)

        self.chk_ver = tk.BooleanVar()
        self.chk_cambiar = tk.BooleanVar()
        self.chk_ejecutar = tk.BooleanVar()
        self.chk_admin = tk.BooleanVar()

        tk.Checkbutton(frame_candados, text="Candado de LECTURA: permite mirar el contenido", variable=self.chk_ver, font=("Arial", 11), bg="#313244", fg="#a6e3a1", selectcolor="#1e1e2e", command=self.actualizar_permisos).pack(anchor=tk.W, pady=3)
        tk.Checkbutton(frame_candados, text="Candado de ESCRITURA: permite cambiar el contenido", variable=self.chk_cambiar, font=("Arial", 11), bg="#313244", fg="#f9e2af", selectcolor="#1e1e2e", command=self.actualizar_permisos).pack(anchor=tk.W, pady=3)
        tk.Checkbutton(frame_candados, text="Candado de EJECUCION: permite correrlo como programa", variable=self.chk_ejecutar, font=("Arial", 11), bg="#313244", fg="#94e2d5", selectcolor="#1e1e2e", command=self.actualizar_permisos).pack(anchor=tk.W, pady=3)
        tk.Checkbutton(frame_candados, text="Privilegios de Administrador (abre los 3 candados de golpe)", variable=self.chk_admin, font=("Arial", 11), bg="#313244", fg="#f38ba8", selectcolor="#1e1e2e", command=self.actualizar_permisos).pack(anchor=tk.W, pady=3)

        self.canvas_candados_n5 = tk.Canvas(contenedor, width=1100, height=170, bg="#313244", highlightthickness=0)
        self.canvas_candados_n5.pack(pady=10)

        frame_archivo = tk.LabelFrame(contenedor, text=" Archivo REAL de prueba (guardado en tu disco duro) ", bg="#1e1e2e", fg="#a6e3a1", font=("Arial", 11, "bold"), padx=15, pady=10)
        frame_archivo.pack(fill=tk.X, padx=20, pady=10)

        fila_archivo = tk.Frame(frame_archivo, bg="#1e1e2e")
        fila_archivo.pack(fill=tk.X)
        tk.Label(fila_archivo, text="Archivo a probar:", font=("Arial", 10, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(side=tk.LEFT, padx=(0, 8))
        self.cmb_archivo_n5 = ttk.Combobox(fila_archivo, font=("Arial", 10), width=38, state="readonly", values=list(self.archivos_n5.keys()))
        self.cmb_archivo_n5.current(0)
        self.cmb_archivo_n5.pack(side=tk.LEFT, padx=5)
        self.cmb_archivo_n5.bind("<<ComboboxSelected>>", self.al_cambiar_archivo_n5)
        tk.Button(fila_archivo, text="Abrir carpeta del archivo", font=("Arial", 9, "bold"), bg="#89b4fa", fg="#11111b", command=self.abrir_carpeta_n5).pack(side=tk.LEFT, padx=8)
        tk.Button(fila_archivo, text="Restaurar archivos originales", font=("Arial", 9, "bold"), bg="#fab387", fg="#11111b", command=self.restaurar_archivos_n5).pack(side=tk.LEFT, padx=8)

        self.lbl_info_archivo_n5 = tk.Label(frame_archivo, text="", font=("Courier New", 9), bg="#181825", fg="#94e2d5", anchor=tk.W, justify=tk.LEFT, wraplength=1050, padx=10, pady=8)
        self.lbl_info_archivo_n5.pack(fill=tk.X, pady=(8, 0))

        frame_flujo = tk.LabelFrame(contenedor, text=" Diagrama en Vivo: Como el Sistema Operativo Decide ", bg="#1e1e2e", fg="#f9e2af", font=("Arial", 11, "bold"))
        frame_flujo.pack(fill=tk.X, padx=20, pady=10)

        self.canvas_flujo_n5 = tk.Canvas(frame_flujo, width=1100, height=170, bg="#313244", highlightthickness=0)
        self.canvas_flujo_n5.pack(padx=10, pady=10)
        self.construir_flujo_n5()

        frame_texto = tk.Frame(contenedor, bg="#1e1e2e")
        frame_texto.pack(pady=(5, 0))
        tk.Label(frame_texto, text="Texto que se agregara al archivo al GUARDAR:", font=("Arial", 10, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(side=tk.LEFT, padx=5)
        self.ent_texto_n5 = tk.Entry(frame_texto, font=("Arial", 10), width=45, bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4")
        self.ent_texto_n5.insert(0, "Cambio de prueba hecho desde InsideOS")
        self.ent_texto_n5.pack(side=tk.LEFT, padx=5)

        frame_acciones = tk.Frame(contenedor, bg="#1e1e2e")
        frame_acciones.pack(pady=10)

        tk.Button(frame_acciones, text="Intentar VER Archivo", font=("Arial", 11, "bold"), bg="#89b4fa", fg="#11111b", command=self.click_ver).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_acciones, text="Intentar GUARDAR Cambios", font=("Arial", 11, "bold"), bg="#f9e2af", fg="#11111b", command=self.click_guardar).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_acciones, text="Intentar EJECUTAR Archivo", font=("Arial", 11, "bold"), bg="#94e2d5", fg="#11111b", command=self.click_ejecutar).pack(side=tk.LEFT, padx=10)

        self.lbl_resultado_n5 = tk.Label(contenedor, text="Esperando un intento de acceso...", font=("Arial", 12, "bold"), bg="#181825", fg="#cdd6f4", wraplength=1050, justify=tk.LEFT, padx=15, pady=15)
        self.lbl_resultado_n5.pack(fill=tk.X, padx=20, pady=10)

        frame_visor = tk.LabelFrame(contenedor, text=" Visor del archivo real (aqui ves lo que el sistema realmente leyo, escribio o ejecuto) ", bg="#1e1e2e", fg="#cba6f7", font=("Arial", 11, "bold"), padx=10, pady=8)
        frame_visor.pack(fill=tk.X, padx=20, pady=5)
        self.txt_visor_n5 = tk.Text(frame_visor, bg="#11111b", fg="#6c7086", font=("Courier New", 10), height=9, state=tk.DISABLED, wrap=tk.WORD)
        self.txt_visor_n5.pack(fill=tk.X)

        tk.Label(contenedor, text="Bitacora de seguridad (lo que revisa el OS en cada intento):", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(anchor=tk.W, padx=15, pady=(10, 0))
        self.txt_logs_permisos = tk.Text(contenedor, bg="#11111b", fg="#cba6f7", font=("Courier New", 9), height=7, state=tk.DISABLED)
        self.txt_logs_permisos.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        self.al_cambiar_archivo_n5()
        self.actualizar_permisos()
        self.verificar_mision_n5()

    def log_nivel5(self, texto):
        self.txt_logs_permisos.config(state=tk.NORMAL)
        self.txt_logs_permisos.insert(tk.END, f"> {texto}\n")
        self.txt_logs_permisos.see(tk.END)
        self.txt_logs_permisos.config(state=tk.DISABLED)

    def verificar_mision_n5(self):
        def marca(cond):
            return "[X]" if cond else "[ ]"
        texto = (
            "MISION PARA DESBLOQUEAR EL DIAGNOSTICO FINAL:\n"
            f" {marca('VER' in self.n5_acciones)} Probar la accion VER\n"
            f" {marca('GUARDAR' in self.n5_acciones)} Probar la accion GUARDAR\n"
            f" {marca('EJECUTAR' in self.n5_acciones)} Probar la accion EJECUTAR\n"
            f" {marca('concedido' in self.n5_resultados)} Lograr al menos un acceso CONCEDIDO\n"
            f" {marca('denegado' in self.n5_resultados)} Lograr al menos un acceso DENEGADO"
        )
        self.lbl_mision_n5.config(text=texto)
        completa = len(self.n5_acciones) == 3 and len(self.n5_resultados) == 2
        if completa and not self.nivel5_usado:
            self.nivel5_usado = True
            self.completar_nivel(5)

    def dibujar_candado_individual(self, canvas, cx, cy, abierto, etiqueta):
        color = "#a6e3a1" if abierto else "#f38ba8"
        canvas.create_arc(cx-18, cy-35, cx+18, cy, start=0, extent=180, outline=color, width=6, style=tk.ARC)
        canvas.create_rectangle(cx-22, cy-8, cx+22, cy+30, fill=color, outline="#11111b", width=2)
        if abierto:
            canvas.create_text(cx, cy+14, text="OK", font=("Arial", 9, "bold"), fill="#11111b")
        else:
            canvas.create_oval(cx-6, cy+2, cx+6, cy+14, fill="#11111b", outline="")
        canvas.create_text(cx, cy+48, text=etiqueta, font=("Arial", 10, "bold"), fill="#cdd6f4")
        estado = "ABIERTO" if abierto else "CERRADO"
        canvas.create_text(cx, cy+64, text=estado, font=("Arial", 9, "bold"), fill=color)

    def dibujar_candados_n5(self):
        canvas = self.canvas_candados_n5
        canvas.delete("all")
        admin = self.chk_admin.get()
        lectura = self.chk_ver.get() or admin
        escritura = self.chk_cambiar.get() or admin
        ejecucion = self.chk_ejecutar.get() or admin
        self.dibujar_candado_individual(canvas, 220, 60, lectura, "Lectura (r)")
        self.dibujar_candado_individual(canvas, 550, 60, escritura, "Escritura (w)")
        self.dibujar_candado_individual(canvas, 880, 60, ejecucion, "Ejecucion (x)")

    def construir_flujo_n5(self):
        canvas = self.canvas_flujo_n5
        canvas.delete("all")
        etapas = ["TU\n(Usuario)", "Sistema Operativo\n(revisa candados)", "Archivo REAL"]
        self.cajas_flujo_n5 = []
        ancho = 300
        alto = 110
        x = 40
        y = 30
        for i, etiqueta in enumerate(etapas):
            rect = canvas.create_rectangle(x, y, x+ancho, y+alto, fill="#1e1e2e", outline="#6c7086", width=3)
            texto_id = canvas.create_text(x+ancho/2, y+alto/2, text=etiqueta, font=("Arial", 11, "bold"), fill="#cdd6f4", justify=tk.CENTER)
            if i == 2:
                self.texto_archivo_flujo_n5 = texto_id
            self.cajas_flujo_n5.append({"rect": rect, "cx": x+ancho/2, "cy": y+alto+25})
            if len(self.cajas_flujo_n5) < len(etapas):
                canvas.create_line(x+ancho, y+alto/2, x+ancho+60, y+alto/2, fill="#585b70", width=3, arrow=tk.LAST)
            x += ancho + 60
        primera = self.cajas_flujo_n5[0]
        self.token_flujo_n5 = canvas.create_oval(primera["cx"]-9, primera["cy"]-9, primera["cx"]+9, primera["cy"]+9, fill="#f9e2af", outline="#11111b", width=2)

    def animar_flujo_permiso_n5(self, concedido):
        canvas = self.canvas_flujo_n5
        for caja in self.cajas_flujo_n5:
            canvas.itemconfig(caja["rect"], outline="#6c7086", width=3, fill="#1e1e2e")
        canvas.itemconfig(self.token_flujo_n5, fill="#f9e2af")

        primera = self.cajas_flujo_n5[0]
        coords = canvas.coords(self.token_flujo_n5)
        cx_actual = (coords[0]+coords[2])/2
        canvas.move(self.token_flujo_n5, primera["cx"]-cx_actual, 0)

        canvas.itemconfig(self.cajas_flujo_n5[0]["rect"], outline="#f9e2af", width=6)
        canvas.update()
        time.sleep(0.4)

        destino = self.cajas_flujo_n5[1]
        coords = canvas.coords(self.token_flujo_n5)
        cx_actual = (coords[0]+coords[2])/2
        dist = destino["cx"] - cx_actual
        for _ in range(20):
            canvas.move(self.token_flujo_n5, dist/20, 0)
            canvas.update()
            time.sleep(0.02)
        canvas.itemconfig(self.cajas_flujo_n5[0]["rect"], outline="#6c7086", width=3)
        canvas.itemconfig(self.cajas_flujo_n5[1]["rect"], outline="#f9e2af", width=6)
        canvas.update()
        time.sleep(0.6)

        color_final = "#a6e3a1" if concedido else "#f38ba8"
        destino2 = self.cajas_flujo_n5[2]
        coords = canvas.coords(self.token_flujo_n5)
        cx_actual = (coords[0]+coords[2])/2
        dist = destino2["cx"] - cx_actual
        for _ in range(20):
            canvas.move(self.token_flujo_n5, dist/20, 0)
            canvas.update()
            time.sleep(0.02)
        canvas.itemconfig(self.cajas_flujo_n5[1]["rect"], outline="#6c7086", width=3)
        canvas.itemconfig(self.cajas_flujo_n5[2]["rect"], outline=color_final, width=6, fill="#1e1e2e")
        canvas.itemconfig(self.token_flujo_n5, fill=color_final)
        canvas.update()

    def aplicar_caso_permiso(self):
        caso = self.cmb_caso.get()
        datos = self.casos_permiso.get(caso)
        if not datos:
            return
        self.chk_ver.set(datos["Ver"])
        self.chk_cambiar.set(datos["Modificar"])
        self.chk_ejecutar.set(datos["Ejecutar"])
        self.chk_admin.set(datos["Admin"])
        self.actualizar_permisos()
        self.log_nivel5(f"CASO CARGADO: '{caso}'.")
        self.log_nivel5(f"   -> Lectura: {'SI' if datos['Ver'] else 'NO'} | Escritura: {'SI' if datos['Modificar'] else 'NO'} "
                         f"| Ejecucion: {'SI' if datos['Ejecutar'] else 'NO'} | Administrador: {'SI' if datos['Admin'] else 'NO'}")

    def actualizar_permisos(self):
        self.permisos["Ver"] = self.chk_ver.get()
        self.permisos["Modificar"] = self.chk_cambiar.get()
        self.permisos["Ejecutar"] = self.chk_ejecutar.get()
        self.permisos["Admin"] = self.chk_admin.get()
        self.dibujar_candados_n5()
        self.aplicar_atributos_reales_n5()
        self.actualizar_info_archivo_n5()

    def click_ver(self):
        if self.animando_n5:
            return
        self.animando_n5 = True
        self.log_nivel5("PASO 1: Solicitud de LECTURA recibida. El OS consulta el candado de lectura.")
        concedido = self.permisos["Ver"] or self.permisos["Admin"]
        threading.Thread(target=self._procesar_intento_n5, args=("VER", concedido, "lectura", ""), daemon=True).start()

    def click_guardar(self):
        if self.animando_n5:
            return
        self.animando_n5 = True
        self.log_nivel5("PASO 1: Solicitud de ESCRITURA recibida. El OS consulta el candado de escritura.")
        concedido = self.permisos["Modificar"] or self.permisos["Admin"]
        texto = self.ent_texto_n5.get().strip() or "Cambio de prueba"
        threading.Thread(target=self._procesar_intento_n5, args=("GUARDAR", concedido, "escritura", texto), daemon=True).start()

    def click_ejecutar(self):
        if self.animando_n5:
            return
        self.animando_n5 = True
        self.log_nivel5("PASO 1: Solicitud de EJECUCION recibida. El OS consulta el candado de ejecucion.")
        concedido = self.permisos["Ejecutar"] or self.permisos["Admin"]
        threading.Thread(target=self._procesar_intento_n5, args=("EJECUTAR", concedido, "ejecucion", ""), daemon=True).start()

    def ejecutar_operacion_real_n5(self, accion, ruta, texto_extra):
        nombre = os.path.basename(ruta)
        try:
            if accion == "VER":
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = f.read()
                self.mostrar_en_visor_n5(contenido, "#a6e3a1")
                self.log_nivel5(f"PASO 3: El OS abrio '{nombre}' y leyo {len(contenido.encode('utf-8')):,} bytes REALES del disco. Mira el visor.")
            elif accion == "GUARDAR":
                prefijo = "# " if nombre.endswith(".py") else ""
                linea = f"{prefijo}[{time.strftime('%H:%M:%S')}] {texto_extra}\n"
                with open(ruta, "a", encoding="utf-8") as f:
                    f.write(linea)
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = f.read()
                self.mostrar_en_visor_n5(contenido, "#f9e2af")
                self.log_nivel5(f"PASO 3: El OS escribio de verdad una linea nueva al final de '{nombre}'. Mira el visor y el tamaño del archivo.")
            else:
                if nombre.endswith(".py"):
                    resultado = subprocess.run([sys.executable, ruta], capture_output=True, text=True, timeout=15, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                    salida = resultado.stdout.strip() or resultado.stderr.strip() or "(sin salida)"
                    self.mostrar_en_visor_n5(f">>> Salida del programa ejecutado de verdad por el Sistema Operativo:\n\n{salida}", "#94e2d5")
                    self.log_nivel5(f"PASO 3: El OS creo un proceso nuevo y ejecuto '{nombre}' de verdad. Mira su salida en el visor.")
                else:
                    self.mostrar_en_visor_n5(f"El candado de ejecucion estaba abierto, pero '{nombre}' es un documento de texto, no un programa. El OS lo trata como datos y no sabe ejecutarlo. Prueba con 'programa_saludo.py'.", "#fab387")
                    self.log_nivel5(f"PASO 3: Permiso concedido, pero '{nombre}' no es un programa ejecutable.")
        except Exception as e:
            self.mostrar_en_visor_n5(f"Error real del sistema: {e}", "#f38ba8")
            self.log_nivel5(f"ERROR REAL: {e}")

    def intentar_operacion_bloqueada_n5(self, accion, ruta):
        nombre = os.path.basename(ruta)
        if accion == "GUARDAR":
            try:
                with open(ruta, "a", encoding="utf-8"):
                    pass
                self.log_nivel5(f"PASO 3: El OS reviso '{nombre}' y no se modifico nada.")
            except PermissionError as e:
                self.log_nivel5(f"PASO 3: El sistema operativo REAL tambien rechazo la escritura: {e}")
            except Exception as e:
                self.log_nivel5(f"PASO 3: Error real al intentar escribir: {e}")
            self.mostrar_en_visor_n5("ACCESO BLOQUEADO: el candado de escritura esta cerrado. El archivo no fue modificado.", "#f38ba8")
        elif accion == "VER":
            self.mostrar_en_visor_n5("ACCESO BLOQUEADO: el candado de lectura esta cerrado. El contenido del archivo es secreto para ti.", "#f38ba8")
            self.log_nivel5(f"PASO 3: El OS no abrio '{nombre}'. Tu no puedes ver su contenido.")
        else:
            self.mostrar_en_visor_n5("ACCESO BLOQUEADO: el candado de ejecucion esta cerrado. El programa no fue ejecutado.", "#f38ba8")
            self.log_nivel5(f"PASO 3: El OS no creo ningun proceso para '{nombre}'.")

    def _procesar_intento_n5(self, accion, concedido, candado, texto_extra):
        try:
            self.animar_flujo_permiso_n5(concedido)
            ruta = self.ruta_archivo_n5()
            nombre = os.path.basename(ruta)
            if concedido:
                mensaje = f"Acceso CONCEDIDO para {accion} sobre '{nombre}'. El candado de {candado} estaba abierto (o tienes privilegios de administrador)."
                self.lbl_resultado_n5.config(text=mensaje, fg="#a6e3a1")
                self.log_nivel5(f"PASO 2: Candado de {candado} = ABIERTO. Acceso CONCEDIDO.")
                self.ejecutar_operacion_real_n5(accion, ruta, texto_extra)
                self.n5_resultados.add("concedido")
                self.mostrar_mini_ventana("Acceso Concedido", mensaje, "exito")
            else:
                mensaje = f"Acceso DENEGADO para {accion} sobre '{nombre}'. El candado de {candado} esta cerrado."
                self.lbl_resultado_n5.config(text=mensaje, fg="#f38ba8")
                self.log_nivel5(f"PASO 2: Candado de {candado} = CERRADO y no eres Administrador. Acceso DENEGADO.")
                self.intentar_operacion_bloqueada_n5(accion, ruta)
                self.n5_resultados.add("denegado")
                self.mostrar_mini_ventana("Acceso Denegado", mensaje, "error")
            self.n5_acciones.add(accion)
            self.root.after(0, self.actualizar_info_archivo_n5)
            self.root.after(0, self.verificar_mision_n5)
        finally:
            self.animando_n5 = False

    def construir_nivel_6(self):
        contenedor = self.crear_area_desplazable(self.tab6)

        self.agregar_introduccion(contenedor, "Que hace este nivel",
            "Este nivel genera un balance completo de todo el recorrido y lo muestra como un tablero "
            "interactivo: un semaforo con los 5 niveles, dos barras que comparan la RAM simulada del "
            "stand contra la RAM fisica real de tu computador, y una fila de contadores de la sesion. "
            "TODO es clickeable: toca cualquier circulo o barra y se abrira una ventana explicando, en "
            "palabras simples, que significa ese numero y con que nivel se relaciona. Debajo veras ademas "
            "el reporte de texto completo, por si quieres el detalle linea por linea.")

        btn_diagnostico = tk.Button(contenedor, text="¡Escanear y Generar Auditoria del Sistema!", font=("Arial", 11, "bold"), bg="#89b4fa", fg="#11111b", command=self.ejecutar_diagnostico_final)
        btn_diagnostico.pack(pady=10)

        frame_tablero = tk.LabelFrame(contenedor, text=" Tablero Interactivo (haz clic para aprender) ", bg="#1e1e2e", fg="#f9e2af", font=("Arial", 12, "bold"))
        frame_tablero.pack(fill=tk.X, padx=15, pady=10)

        self.lbl_hint_tablero = tk.Label(frame_tablero, text="Toca cualquier circulo o barra de abajo para que te explique que significa.", font=("Arial", 9, "italic"), bg="#1e1e2e", fg="#94e2d5")
        self.lbl_hint_tablero.pack(anchor=tk.W, padx=10, pady=(5, 0))

        self.canvas_semaforo_n6 = tk.Canvas(frame_tablero, width=1180, height=140, bg="#313244", highlightthickness=0, cursor="hand2")
        self.canvas_semaforo_n6.pack(padx=10, pady=10, fill=tk.X)

        self.canvas_ram_n6 = tk.Canvas(frame_tablero, width=1180, height=150, bg="#313244", highlightthickness=0, cursor="hand2")
        self.canvas_ram_n6.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.canvas_contadores_n6 = tk.Canvas(frame_tablero, width=1180, height=200, bg="#313244", highlightthickness=0, cursor="hand2")
        self.canvas_contadores_n6.pack(padx=10, pady=(0, 10), fill=tk.X)

        self._datos_dashboard_n6 = {
            "suma_ram": 0, "capacidad_maxima_kb": 12 * 15000,
            "total_kb_real": None, "libre_kb_real": None,
        }

        self.dibujar_semaforo_niveles_n6()
        self.dibujar_barras_ram_n6()
        self.dibujar_contadores_n6()

        tk.Label(contenedor, text="Reporte de texto completo (detalle linea por linea):", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(anchor=tk.W, padx=15, pady=(5, 0))
        self.txt_auditoria = tk.Text(contenedor, width=90, height=22, font=("Courier New", 10), bg="#181825", fg="#94e2d5", bd=2, padx=12, pady=12)
        self.txt_auditoria.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        self.txt_auditoria.insert(tk.END, "Esperando orden para auditar la computadora...")

    def dibujar_semaforo_niveles_n6(self):
        canvas = self.canvas_semaforo_n6
        canvas.delete("all")

        self.info_niveles_n6 = [
            {
                "titulo": "Nivel 1 - Procesos",
                "usado": self.nivel1_usado,
                "explicacion": ("Aqui abriste un programa REAL de tu computador y viste, paso a paso, como el "
                                "Sistema Operativo lo busca en el disco, crea un proceso con un PID unico y le "
                                "reserva bloques de RAM. Cerrarlo libera esa RAM para el siguiente programa.")
            },
            {
                "titulo": "Nivel 2 - CPU (Round Robin)",
                "usado": self.nivel2_usado,
                "explicacion": ("Aqui viste como el CPU reparte su tiempo entre varias ventanas usando turnos "
                                "llamados 'quantum'. Si una ventana no termina su trabajo en su turno, la CPU se "
                                "lo quita (apropiacion) y la manda al final de la fila para que todas sean atendidas "
                                "de forma justa.")
            },
            {
                "titulo": "Nivel 3 - RAM y Swap",
                "usado": self.nivel3_usado,
                "explicacion": ("Aqui la RAM simulada (solo 12 bloques) se lleno con tus ventanas reales, y cuando "
                                "ya no quedo espacio, el Sistema Operativo escribio de verdad una pagina en tu disco "
                                "duro (memoria virtual o 'swap') para poder seguir funcionando sin quedarse sin memoria.")
            },
            {
                "titulo": "Nivel 4 - Control de Ventanas (FIFO)",
                "usado": self.nivel4_usado,
                "explicacion": ("Aqui el stand vigilo tus ventanas reales y aplico la regla FIFO: si se supera el "
                                "limite permitido, se avisa UNA sola vez para cerrar la ventana mas antigua y dejarle "
                                "sitio a la nueva. Las ventanas que ya existian antes de activar el modo no generan "
                                "avisos, solo las que aparecen despues.")
            },
            {
                "titulo": "Nivel 5 - Candados de Archivos",
                "usado": self.nivel5_usado,
                "explicacion": ("Aqui viste como el Sistema Operativo revisa 3 candados antes de dejarte usar un "
                                "archivo REAL: Lectura, Escritura y Ejecucion. Si el candado esta cerrado (y no eres "
                                "administrador), el acceso se DENIEGA, sin importar lo que quieras hacer con el archivo.")
            },
        ]

        canvas.create_text(20, 15, text="Semaforo de Niveles Completados", font=("Arial", 11, "bold"), fill="#cdd6f4", anchor=tk.W)

        espacio = 1180 / len(self.info_niveles_n6)
        for i, nivel in enumerate(self.info_niveles_n6):
            cx = espacio * i + espacio / 2
            cy = 80
            color = "#a6e3a1" if nivel["usado"] else "#45475a"
            borde = "#a6e3a1" if nivel["usado"] else "#6c7086"
            oid = canvas.create_oval(cx-32, cy-32, cx+32, cy+32, fill=color, outline=borde, width=3)
            tid = canvas.create_text(cx, cy, text=("✓" if nivel["usado"] else str(i+1)), font=("Arial", 18, "bold"), fill="#11111b" if nivel["usado"] else "#cdd6f4")
            lid = canvas.create_text(cx, cy+48, text=nivel["titulo"], font=("Arial", 8, "bold"), fill="#cdd6f4", justify=tk.CENTER, width=espacio-10)

            tag = f"nivel_n6_{i}"
            for item_id in (oid, tid, lid):
                canvas.itemconfig(item_id, tags=tag)
            canvas.tag_bind(tag, "<Button-1>", lambda e, idx=i: self.explicar_nivel_n6(idx))

    def explicar_nivel_n6(self, idx):
        nivel = self.info_niveles_n6[idx]
        estado = "Ya completaste este nivel en esta sesion." if nivel["usado"] else "Todavia NO has completado este nivel en esta sesion; ¡pruebalo en su pestaña!"
        self.mostrar_ventana_explicativa(nivel["titulo"], f"{nivel['explicacion']}\n\nEstado actual: {estado}")

    def dibujar_barras_ram_n6(self):
        canvas = self.canvas_ram_n6
        canvas.delete("all")
        datos = self._datos_dashboard_n6

        canvas.create_text(20, 15, text="RAM: Simulada del Stand vs Fisica Real de tu Computador", font=("Arial", 11, "bold"), fill="#cdd6f4", anchor=tk.W)

        suma_ram = datos["suma_ram"]
        capacidad_maxima_kb = datos["capacidad_maxima_kb"]
        porcentaje_sim = min(100, (suma_ram / capacidad_maxima_kb) * 100) if capacidad_maxima_kb else 0

        y1 = 45
        canvas.create_rectangle(20, y1, 1160, y1+28, fill="#181825", outline="#585b70", tags="barra_sim_n6")
        ancho_lleno = 1140 * (porcentaje_sim / 100)
        canvas.create_rectangle(20, y1, 20+ancho_lleno, y1+28, fill="#89b4fa", outline="", tags="barra_sim_n6")
        canvas.create_text(590, y1+14, text=f"RAM SIMULADA (12 bloques): {suma_ram:,} KB usados de {capacidad_maxima_kb:,} KB ({porcentaje_sim:.1f}%)", font=("Arial", 9, "bold"), fill="#11111b" if porcentaje_sim > 45 else "#cdd6f4", tags="barra_sim_n6")

        y2 = 95
        total_kb_real = datos["total_kb_real"]
        libre_kb_real = datos["libre_kb_real"]
        if total_kb_real:
            usado_kb_real = total_kb_real - libre_kb_real
            porcentaje_real = min(100, (usado_kb_real / total_kb_real) * 100) if total_kb_real else 0
            texto_real = f"RAM FISICA REAL: {usado_kb_real:,} KB usados de {total_kb_real:,} KB ({porcentaje_real:.1f}%)"
        else:
            porcentaje_real = 0
            texto_real = "RAM FISICA REAL: no disponible todavia (presiona 'Escanear y Generar Auditoria')"

        canvas.create_rectangle(20, y2, 1160, y2+28, fill="#181825", outline="#585b70", tags="barra_real_n6")
        ancho_lleno_real = 1140 * (porcentaje_real / 100)
        canvas.create_rectangle(20, y2, 20+ancho_lleno_real, y2+28, fill="#fab387", outline="", tags="barra_real_n6")
        canvas.create_text(590, y2+14, text=texto_real, font=("Arial", 9, "bold"), fill="#11111b" if porcentaje_real > 45 else "#cdd6f4", tags="barra_real_n6")

        canvas.tag_bind("barra_sim_n6", "<Button-1>", lambda e: self.explicar_ram_n6("simulada"))
        canvas.tag_bind("barra_real_n6", "<Button-1>", lambda e: self.explicar_ram_n6("real"))

    def explicar_ram_n6(self, cual):
        if cual == "simulada":
            self.mostrar_ventana_explicativa(
                "RAM Simulada del Stand",
                "Este stand simula solo 12 bloques de RAM (como en el Nivel 3) para que sea facil de ver en "
                "pantalla. Cuando la suma de tus ventanas reales supera esos 12 bloques, el simulador activa "
                "la memoria virtual: escribe una pagina de verdad en tu disco duro para poder seguir "
                "funcionando aunque la RAM simulada ya este llena. Es la misma idea que usa Windows, solo que "
                "aqui la vemos en miniatura."
            )
        else:
            self.mostrar_ventana_explicativa(
                "RAM Fisica Real de tu Computador",
                "Esta barra consulta con PowerShell la memoria RAM VERDADERA de tu maquina (no la simulada). "
                "Te muestra cuanta memoria total tienes y cuanta esta en uso ahora mismo por TODOS los "
                "programas de tu computador, no solo por el simulador. Sirve para comparar: la RAM simulada "
                "del stand es solo una pequeña demostracion; tu computador real maneja muchisima mas memoria "
                "al mismo tiempo."
            )

    def dibujar_contadores_n6(self):
        canvas = self.canvas_contadores_n6
        canvas.delete("all")

        canvas.create_text(20, 15, text="Contadores en Vivo de esta Sesion", font=("Arial", 11, "bold"), fill="#cdd6f4", anchor=tk.W)

        self.info_contadores_n6 = [
            {
                "titulo": "Procesos\nCreados (N1)",
                "valor": self.contador_procesos_creados_n1,
                "color": "#a6e3a1",
                "explicacion": ("Cada vez que abriste un programa real en el Nivel 1, el kernel ejecuto una llamada "
                                "de sistema (fork/exec) para crear un proceso nuevo con su propio PID. Este numero "
                                "cuenta cuantas veces ocurrio eso en esta sesion.")
            },
            {
                "titulo": "Cierres\nManuales (N1)",
                "valor": self.contador_cierres_manuales_n1,
                "color": "#89b4fa",
                "explicacion": ("Cada vez que presionaste 'Cerrar Aplicacion Actual' en el Nivel 1, el simulador envio "
                                "una señal real de terminacion (TerminateProcess) al proceso, y el kernel libero toda "
                                "la RAM que ese proceso ocupaba.")
            },
            {
                "titulo": "Paginas\nSwap (N3)",
                "valor": len(self.archivos_swap_creados),
                "color": "#fab387",
                "explicacion": ("Cada vez que la RAM simulada de 12 bloques se lleno, el Sistema Operativo escribio "
                                "de verdad un archivo de pagina en tu disco duro (memoria virtual). Este numero cuenta "
                                "cuantos archivos de pagina reales se crearon durante el Nivel 3.")
            },
            {
                "titulo": "Expulsiones\nFIFO (N4)",
                "valor": self.contador_expulsiones_n4,
                "color": "#f38ba8",
                "explicacion": ("Cada vez que aceptaste cerrar la ventana mas antigua en el Nivel 4, el simulador la "
                                "cerro de verdad con taskkill, aplicando la regla FIFO: la ventana con mas tiempo "
                                "abierta es siempre la primera en salir cuando no hay espacio.")
            },
            {
                "titulo": "Avisos\nRechazados (N4)",
                "valor": self.contador_advertencias_rechazadas_n4,
                "color": "#cba6f7",
                "explicacion": ("Cada vez que dijiste 'No' cuando el Nivel 4 te pregunto si querias cerrar la ventana "
                                "mas antigua, quedo registrado aqui. El sistema entonces NO vuelve a insistir con esa "
                                "misma ventana nueva; solo avisara de nuevo si aparece otra distinta.")
            },
        ]

        n = len(self.info_contadores_n6)
        ancho_col = 1140 / n
        max_valor = max(1, max(c["valor"] for c in self.info_contadores_n6))
        alto_max_barra = 110
        base_y = 175

        for i, c in enumerate(self.info_contadores_n6):
            cx = 20 + ancho_col * i + ancho_col / 2
            alto_barra = max(6, (c["valor"] / max_valor) * alto_max_barra)
            x1 = cx - 35
            x2 = cx + 35
            y1 = base_y - alto_barra
            y2 = base_y

            tag = f"contador_n6_{i}"
            canvas.create_rectangle(x1, base_y - alto_max_barra, x2, base_y, fill="#181825", outline="#585b70", tags=tag)
            canvas.create_rectangle(x1, y1, x2, y2, fill=c["color"], outline="#11111b", width=2, tags=tag)
            canvas.create_text(cx, y1-14, text=str(c["valor"]), font=("Arial", 12, "bold"), fill="#f9e2af", tags=tag)
            canvas.create_text(cx, base_y+22, text=c["titulo"], font=("Arial", 8, "bold"), fill="#cdd6f4", justify=tk.CENTER, tags=tag)

            canvas.tag_bind(tag, "<Button-1>", lambda e, idx=i: self.explicar_contador_n6(idx))

    def explicar_contador_n6(self, idx):
        c = self.info_contadores_n6[idx]
        titulo_plano = c["titulo"].replace("\n", " ")
        self.mostrar_ventana_explicativa(titulo_plano, f"Valor actual: {c['valor']}\n\n{c['explicacion']}")

    def ejecutar_diagnostico_final(self):
        self.txt_auditoria.delete("1.0", tk.END)
        self.txt_auditoria.insert(tk.END, ">>> INICIANDO ESCANEO PROFUNDO DEL KERNEL...\n")

        ventanas_actuales = self.obtener_procesos_ventanas_reales(limite=6)

        time.sleep(0.2)
        self.txt_auditoria.insert(tk.END, ">>> ANALIZANDO MEMORIA DE APLICACIONES ACTIVAS...\n\n")

        self.txt_auditoria.insert(tk.END, "====================================================================\n")
        self.txt_auditoria.insert(tk.END, "               REPORTE REAL DEL ADMINISTRADOR DE TAREAS             \n")
        self.txt_auditoria.insert(tk.END, "====================================================================\n")

        suma_ram = 0
        for v in ventanas_actuales:
            self.txt_auditoria.insert(tk.END, f" Ventana detectada: {v['name']:<20} | PID: {v['pid']:<6} | Consumo: {v['mem']:,} KB\n")
            suma_ram += v['mem']

        self.txt_auditoria.insert(tk.END, f"\n-> Impacto total estimado de ventanas visibles: {suma_ram:,} KB\n\n")

        self.txt_auditoria.insert(tk.END, "====================================================================\n")
        self.txt_auditoria.insert(tk.END, "               CAPACIDAD SIMULADA VS RAM FISICA REAL                \n")
        self.txt_auditoria.insert(tk.END, "====================================================================\n")

        capacidad_por_bloque_kb = 15000
        total_bloques = 12
        capacidad_maxima_kb = capacidad_por_bloque_kb * total_bloques
        porcentaje_sim = min(100, (suma_ram / capacidad_maxima_kb) * 100) if capacidad_maxima_kb else 0
        barras_llenas_sim = int(porcentaje_sim // 5)
        barra_sim = "[" + "#" * barras_llenas_sim + "-" * (20 - barras_llenas_sim) + f"] {porcentaje_sim:.1f}%"

        self.txt_auditoria.insert(tk.END, f" Bloques totales simulados: {total_bloques} bloques de {capacidad_por_bloque_kb:,} KB cada uno.\n")
        self.txt_auditoria.insert(tk.END, f" Capacidad maxima simulada de tu RAM en este stand: {capacidad_maxima_kb:,} KB\n")
        self.txt_auditoria.insert(tk.END, f" Uso simulado frente al maximo: {barra_sim}\n")

        if suma_ram >= capacidad_maxima_kb:
            self.txt_auditoria.insert(tk.END,
                " ¡LIMITE SIMULADO ALCANZADO! Cuando la RAM llega a su tope, el Sistema Operativo ya no\n"
                " puede asignar mas bloques fisicos y activa la MEMORIA VIRTUAL (swap) del Nivel 3, usando\n"
                " tu disco duro como respaldo temporal.\n")
        else:
            self.txt_auditoria.insert(tk.END,
                " Todavia hay espacio libre en la RAM simulada. Si el consumo superara el limite, el\n"
                " Sistema Operativo activaria automaticamente la memoria virtual (swap) del Nivel 3.\n")

        total_kb_real, libre_kb_real = self.obtener_ram_fisica_real()
        if total_kb_real:
            usado_kb_real = total_kb_real - libre_kb_real
            porcentaje_real = min(100, (usado_kb_real / total_kb_real) * 100) if total_kb_real else 0
            barras_llenas_real = int(porcentaje_real // 5)
            barra_real = "[" + "#" * barras_llenas_real + "-" * (20 - barras_llenas_real) + f"] {porcentaje_real:.1f}%"
            self.txt_auditoria.insert(tk.END, f"\n RAM fisica total real de este computador: {total_kb_real:,} KB ({total_kb_real/1024/1024:.1f} GB)\n")
            self.txt_auditoria.insert(tk.END, f" RAM fisica realmente en uso ahora mismo: {usado_kb_real:,} KB\n")
            self.txt_auditoria.insert(tk.END, f" Uso real frente a tu maquina completa: {barra_real}\n")
        else:
            self.txt_auditoria.insert(tk.END, "\n No se pudo consultar la RAM fisica real de la maquina en este momento.\n")

        self.txt_auditoria.insert(tk.END, "\n====================================================================\n")
        self.txt_auditoria.insert(tk.END, "               ESTADISTICAS GLOBALES DE ESTA SESION                 \n")
        self.txt_auditoria.insert(tk.END, "====================================================================\n")

        duracion_segundos = int(time.time() - self.hora_inicio_sesion)
        minutos = duracion_segundos // 60
        segundos = duracion_segundos % 60

        self.txt_auditoria.insert(tk.END, f" Tiempo total de uso del stand: {minutos} min {segundos} s\n")
        self.txt_auditoria.insert(tk.END, f" Procesos reales creados desde el Nivel 1: {self.contador_procesos_creados_n1}\n")
        self.txt_auditoria.insert(tk.END, f" Procesos cerrados manualmente en el Nivel 1: {self.contador_cierres_manuales_n1}\n")
        self.txt_auditoria.insert(tk.END, f" Paginas reales escritas en disco durante el Nivel 3 (swap): {len(self.archivos_swap_creados)}\n")
        self.txt_auditoria.insert(tk.END, f" Ventanas expulsadas de verdad por el Modo de Control Real (Nivel 4): {self.contador_expulsiones_n4}\n")
        self.txt_auditoria.insert(tk.END, f" Advertencias de limite rechazadas por el usuario en el Nivel 4: {self.contador_advertencias_rechazadas_n4}\n")
        self.txt_auditoria.insert(tk.END, f" Ventanas bajo vigilancia ahora mismo en el Modo de Control Real: {len(self.cola_monitor_n4)} / {self.limite_ventanas_n4}\n")

        self.txt_auditoria.insert(tk.END, "\n====================================================================\n")
        self.txt_auditoria.insert(tk.END, "               NIVELES EXPLORADOS EN ESTA SESION                    \n")
        self.txt_auditoria.insert(tk.END, "====================================================================\n")

        niveles_estado = [
            ("Nivel 1 - Creacion real de procesos", self.nivel1_usado),
            ("Nivel 2 - Round Robin y conceptos de CPU", self.nivel2_usado),
            ("Nivel 3 - RAM y memoria virtual (swap)", self.nivel3_usado),
            ("Nivel 4 - Control Real de Ventanas (FIFO)", self.nivel4_usado),
            ("Nivel 5 - Candados de archivos", self.nivel5_usado),
        ]
        completados = 0
        for nombre, usado in niveles_estado:
            marca = "[X]" if usado else "[ ]"
            if usado:
                completados += 1
            self.txt_auditoria.insert(tk.END, f" {marca} {nombre}\n")

        self.txt_auditoria.insert(tk.END, f"\n-> Progreso total de exploracion: {completados}/5 niveles completados en esta sesion.\n")

        self.txt_auditoria.insert(tk.END, "\n====================================================================\n")
        self.txt_auditoria.insert(tk.END, "               HISTORIAL DE INTERACCION EN EL STAND                 \n")
        self.txt_auditoria.insert(tk.END, "====================================================================\n")

        if self.historial_programas_abiertos:
            self.txt_auditoria.insert(tk.END, " Durante esta simulacion, el visitante abrio con exito:\n")
            for prog in self.historial_programas_abiertos:
                self.txt_auditoria.insert(tk.END, f"  * {prog}\n")
        else:
            self.txt_auditoria.insert(tk.END, " El visitante aun no ha provocado el nacimiento de nuevos procesos en el Nivel 1.\n")

        self.txt_auditoria.insert(tk.END, "\n====================================================================\n")
        self.txt_auditoria.insert(tk.END, "                          CONCLUSION FINAL                          \n")
        self.txt_auditoria.insert(tk.END, "====================================================================\n")
        self.txt_auditoria.insert(tk.END,
            " Con este simulador se demostraron, en tu propio computador, los pilares de un\n"
            " Sistema Operativo moderno: creacion y cierre real de procesos (Nivel 1), reparto\n"
            " justo del CPU con Round Robin y sus conceptos clave (Nivel 2), gestion de RAM y uso\n"
            " real del disco duro mediante memoria virtual o 'swap' (Nivel 3), un limite real y\n"
            " controlado de ventanas simultaneas con el algoritmo FIFO (Nivel 4), y control de\n"
            " acceso mediante candados de lectura, escritura y ejecucion sobre archivos reales (Nivel 5).\n"
            " En conjunto, el stand logro traducir conceptos teoricos de Sistemas Operativos en una\n"
            " experiencia visual, interactiva y 100% real para el usuario.\n"
        )

        self.txt_auditoria.insert(tk.END, "\n>>> DIAGNOSTICO: El nucleo esta estable. El stand de Sistemas esta listo para ganar.")

        self._datos_dashboard_n6 = {
            "suma_ram": suma_ram,
            "capacidad_maxima_kb": capacidad_maxima_kb,
            "total_kb_real": total_kb_real,
            "libre_kb_real": libre_kb_real,
        }
        self.dibujar_semaforo_niveles_n6()
        self.dibujar_barras_ram_n6()
        self.dibujar_contadores_n6()

        messagebox.showinfo("Auditoria Exitosa", "Se ha analizado con exito todo lo que abriste y lo que esta corriendo en tu PC. Revisa el tablero interactivo arriba: puedes tocar cualquier circulo o barra para que te explique que significa.")


if __name__ == "__main__":
    root = tk.Tk()
    app = InsideOSVentanasReales(root)
    root.mainloop()