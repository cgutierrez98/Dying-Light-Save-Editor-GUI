# Dying Light Save Editor GUI
This project is a tool designed to be a GUI for the Dying Light CLI save editor by Steffen. Can be found [here](https://steffenl.com/projects/dying-light-save-editor/releases).

It allows users to edit player stats, skills, and other in-game values in a simple interface. (basically its a json editor).

The goal of this project is to provide a reliable and easy-to-use editor for customizing gameplay without manually editing save files.

## Features

* Edit player statistics
* Edit inventory
* Edit skills

## Releases

[Downloads](https://github.com/EllisGamingTv/Dying-Light-Save-Editor-GUI/releases)

## How to Use

editor.exe and your save file save_coop_0.sav must be at C:\Editor

## EXE Requirements

* [CLI by Steffen](https://steffenl.com/projects/dying-light-save-editor/releases).

## PY Requirements

* Python

```
pip install requests packaging
```

* [CLI by Steffen](https://steffenl.com/projects/dying-light-save-editor/releases).

## Compilation

```
pip install pyinstaller
```
* cd to main.py directory then

```
pyinstaller --onefile --noconsole main.py
```

## Plugins

The plugin system lets you easily add new features to the app without touching the main project.

Basically, a plugin can:
* add new tabs or sections to the interface
* create custom tools or mini-features
* refresh or update parts of the UI
* run actions in the background
* extend the app however you want

To use it, you just drop your plugin file into the "plugins" folder and the app will automatically detect and load it when it starts
Each plugin is independent, so itâ€™s super convenient to keep things organized and add/remove features whenever you want without breaking the whole app.

## Note

if you want any feature or weapons/skills added you can ask me to add it, i would be glad.

i am still learning coding, the code source might burn your eyes. thats why all contributors are appreciated.

## Desarrollo

```
pip install -r requirements.txt
python src/main.py
python -m pytest tests
```

La versión se define en `src/logic/version.py`. Build: `pyinstaller src/main.spec`.

## Seguridad y avisos

* **Cierra el juego** antes de guardar y mantén tus backups. Se crea uno automático en `backups/` al guardar (se conservan los 30 últimos; si el backup falla, no se guarda). El guardado es atómico.
* **Plugins** (`plugins/*.py`): se ejecutan sin aislamiento real. Cada plugin nuevo o modificado pide confirmación (hash SHA-256) la primera vez. Instala solo plugins de confianza.
* Valores extremos (p. ej. cantidades máximas) en saves online pueden provocar baneos; úsalo bajo tu responsabilidad.
