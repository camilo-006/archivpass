# Backup Corporativo - ArchivPass

Sistema de respaldo corporativo e inteligente desarrollado en Python. La aplicación permite organizar y clasificar archivos automáticamente por categorías y año de modificación, gestionar duplicados de forma segura y monitorear el estado del proceso en tiempo real mediante una consola de actividad integrada.

---

## Características Principales

* **Organización Automática:** Clasifica archivos por categorías (*Word, Excel, PDF, Multimedia, Ejecutables, Comprimidos, etc.*) y crea automáticamente subcarpetas organizadas por el año de modificación del archivo.
* **Gestión Inteligente de Duplicados:** 
  * Identifica si un archivo idéntico (*mismo tamaño y fecha*) ya existe en el destino para omitirlo o reemplazarlo según la configuración.
  * Si detecta un archivo con el mismo nombre pero diferente contenido o fecha, le asigna un correlativo automático (*ejemplo: documento(1).pdf*) para evitar la pérdida de datos.
* **Registro de Actividad en Tiempo Real:** Consola de texto integrada que muestra el progreso detallado evento por evento (`[COPIADO]`, `[RENOMBRADO]`, `[OMITIDO]`, `[ERROR]`).
* **Panel de Métricas:** Contadores en tiempo real sobre la cantidad de archivos procesados, omitidos, errores y el volumen total de datos transferidos.
* **Informe Físico de Auditoría:** Genera automáticamente un archivo de texto (`reporte_transferencia.txt`) en la carpeta destino al finalizar la ejecución.
* **Procesamiento Multihilo:** Utiliza hilos de ejecución (`threading`) para evitar que la interfaz gráfica se congele durante la copia de grandes volúmenes de datos.
* **Soporte de Rutas Largas:** Compatible con la sintaxis de rutas extensas en entornos Windows (`\\?\`).
* **Interfaz Profesional:** Diseño gráfico optimizado en modo oscuro con contraste alto y tipografía legible.

---

## Tecnologías Utilizadas

* **Lenguaje:** Python 3.10+
* **Interfaz Gráfica:** Tkinter / TTK
* **Módulos del Sistema:** `os`, `shutil`, `threading`, `datetime`, `ctypes`
* **Empaquetado:** PyInstaller
---

## Instalación y Uso

### Requisitos Previos
Tener instalado Python 3.10 o superior en el sistema operativo.

### 1. Clonar el Repositorio

git clone [https://github.com/camilo-006/archivpass.git](https://github.com/camilo-006/archivpass.git)
cd archivpass


### 2. ejecutar la aplicacion

python archivpasss.py

### 3. complilar el ejecutable (.exe)

pip install pyinstaller \
pyinstaller --noconsole --onefile --add-data "icono.png;." archivpasss.py

## estructura del proyecto

archivpass/
│
├── archivpasss.py      # Código fuente principal de la aplicación
├── icono.png           # Recurso gráfico para el ícono de la interfaz
├── .gitignore          # Exclusión de archivos temporales y compilados
└── README.md           # Documentación técnica del repositorio

## Autor

desarrolldo por Camilo Alarcon 