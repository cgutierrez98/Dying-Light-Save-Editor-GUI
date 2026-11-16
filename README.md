# Dying Light Save Editor GUI

Interfaz gráfica (GUI) para el editor de partidas guardadas por línea de comandos de Dying Light desarrollado por **Steffen** (disponible en [su web oficial](https://steffenl.com/projects/dying-light-save-editor/releases)).

> **Nota:** Este proyecto es un *fork* del trabajo original de [EllisGamingTv](https://github.com/EllisGamingTv/Dying-Light-Save-Editor-GUI), ampliado con mejoras de arquitectura, desacople de lógica, guardado atómico, validación de integridad, gestión robusta de copias de seguridad y verificación de plugins.

Permite modificar estadísticas del jugador, habilidades, inventario, armas y otros valores de la partida a través de una interfaz visual clara e intuitiva.

---

## Características

* **Estadísticas del jugador:** Edición de salud, furia y dinero.
* **Inventario y armas:** Modificación de durabilidad, reparaciones, cantidad, rareza (incluyendo platino), planos de crafteo y engarces/mejoras (sockets).
* **Gestión de munición:** Pestaña dedicada con acceso rápido para maximizar todo tipo de munición.
* **Árbol de habilidades:** Edición de niveles y adición de habilidades de leyenda o especiales.
* **Guardado seguro y atómico:** Reemplazo atómico de archivos que previene la corrupción de partidas en caso de fallo o corte de energía.
* **Copias de seguridad automáticas:** Creación de un backup previo a cada guardado y ventana de restauración integrada.
* **Buscador y filtros:** Búsqueda rápida por nombre y categoría de ítems.
* **Sistema de plugins:** Capacidad para añadir pestañas y herramientas personalizadas.

---

## Descargas y Versiones

Puedes descargar los ejecutables compilados directamente desde la sección de lanzamientos:

👉 [Descargar última versión](https://github.com/cgutierrez98/Dying-Light-Save-Editor-GUI/releases)

---

## Requisitos y Configuración de `editor.exe`

Para descifrar y cifrar los archivos `.sav` de Dying Light, esta herramienta requiere el CLI de Steffen (`editor.exe`).

1. Descarga `editor.exe` desde [Steffen's CLI Releases](https://steffenl.com/projects/dying-light-save-editor/releases).
2. Puedes colocar `editor.exe` en la carpeta `C:\Editor`, en la misma carpeta del ejecutable, o seleccionarlo desde el menú de la aplicación:  
   **Tools > Configure Steffen CLI (editor.exe)...**

---

## Desarrollo local

Si deseas ejecutar o modificar el código fuente:

### 1. Clonar e instalar dependencias

```bash
git clone https://github.com/cgutierrez98/Dying-Light-Save-Editor-GUI.git
cd Dying-Light-Save-Editor-GUI
pip install -r requirements.txt
```

### 2. Ejecutar la aplicación

```bash
python src/main.py
```

### 3. Ejecutar las pruebas

```bash
python -m pytest tests
```

---

## Compilación (Crear `.exe` con PyInstaller)

La configuración del ejecutable está definida en `src/main.spec` (modo `--noconsole` y empaquetado en un solo binario).

Para compilar:

```bash
cd src
pyinstaller main.spec --noconfirm
```

El ejecutable generado se ubicará en la carpeta `src/dist/main.exe`.

La versión de la aplicación se centraliza en `src/logic/version.py`.

---

## Sistema de Plugins

El sistema de plugins permite extender la interfaz y las funciones de la aplicación sin modificar el código base.

* Los plugins se colocan en la carpeta `plugins/` (archivos `.py`).
* La aplicación los detecta y carga al iniciar.
* Pueden añadir nuevas pestañas, herramientas, acciones en segundo plano o modificar datos del inventario.

---

## Seguridad y Copias de Seguridad

* **Cierra el juego antes de guardar:** Evita que el juego sobrescriba o bloquee el archivo mientras realizas modificaciones.
* **Copias de seguridad obligatorias:** Al pulsar *Save Changes*, el editor crea automáticamente una copia en la carpeta `backups/` junto a la partida. Si por algún motivo no se puede crear la copia, el guardado se cancela para proteger tu partida. Se conservan las 30 copias más recientes.
* **Plugins:** Los plugins de Python se ejecutan con acceso a tu entorno. Por seguridad, la aplicación solicita confirmación mediante hash SHA-256 la primera vez que detecta un plugin nuevo o modificado. Carga únicamente plugins de fuentes fiables.
* **Partidas online:** Modificar valores a niveles extremos en partidas multijugador puede acarrear penalizaciones o incompatibilidades. Utiliza estas modificaciones con precaución.

---

## Créditos y Agradecimientos

* **[EllisGamingTv](https://github.com/EllisGamingTv/Dying-Light-Save-Editor-GUI)**: Creador original del proyecto Dying-Light-Save-Editor-GUI.
* **[Steffen](https://steffenl.com/projects/dying-light-save-editor/releases)**: Creador de la herramienta de línea de comandos `editor.exe` que permite descifrar y cifrar las partidas de Dying Light.
