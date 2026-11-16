import os
import importlib.util
import sys
import traceback
import builtins
import hashlib

BANNED_MODULES = {
    "os",
    "subprocess",
    "socket",
    "shutil",
    "ctypes",
    "requests",
    "urllib",
    "http",
    "ftplib",
    "telnetlib",
    "webbrowser",
    "winreg",
    "pathlib",
    "builtins",
    "sys"
}


def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_plugins(confirm=None, trusted=None, on_error=None):
    """Carga los plugins de ./plugins.

    AVISO: el bloqueo de imports NO es una sandbox real; un plugin tiene acceso total.
    Por eso, si se pasa `confirm(name, path)`, cada plugin nuevo o modificado (por hash
    SHA-256) requiere confirmacion del usuario. Los aceptados se guardan en `trusted`.
    Sin `confirm` se mantiene el comportamiento anterior.
    """
    plugins = []

    base_path = get_base_path()

    plugin_folder = os.path.join(
        base_path,
        "plugins"
    )

    if not os.path.exists(plugin_folder):
        return plugins

    REAL_IMPORT = builtins.__import__

    def safe_import(
        name,
        globals=None,
        locals=None,
        fromlist=(),
        level=0
    ):
        root = name.split(".")[0]

        if root in BANNED_MODULES:
            raise ImportError(
                f"Blocked dangerous module: {root}"
            )

        return REAL_IMPORT(
            name,
            globals,
            locals,
            fromlist,
            level
        )

    for file in os.listdir(plugin_folder):

        if not file.endswith((".py", ".pyc")):
            continue

        file_path = os.path.join(
            plugin_folder,
            file
        )

        if confirm is not None and trusted is not None:
            digest = _sha256(file_path)
            if trusted.get(file) != digest:
                if not confirm(file, file_path):
                    print(f"[PLUGIN] Skipped untrusted plugin: {file}")
                    continue
                trusted[file] = digest

        module_name = (
            f"plugin_{os.path.splitext(file)[0]}"
        )

        try:

            if module_name in sys.modules:
                del sys.modules[module_name]

            spec = importlib.util.spec_from_file_location(
                module_name,
                file_path
            )

            if not spec or not spec.loader:
                continue

            module = importlib.util.module_from_spec(spec)

            sys.modules[module_name] = module

            old_import = builtins.__import__
            builtins.__import__ = safe_import

            try:
                spec.loader.exec_module(module)

            finally:
                builtins.__import__ = old_import

            if (
                hasattr(module, "run")
                or hasattr(module, "init_ui")
            ):

                plugins.append({
                    "name": getattr(
                        module,
                        "PLUGIN_NAME",
                        file[:-3]
                    ),

                    "run": getattr(
                        module,
                        "run",
                        None
                    ),

                    "init_ui": getattr(
                        module,
                        "init_ui",
                        None
                    ),

                    "refresh": getattr(
                        module,
                        "refresh",
                        None
                    ),

                    "module": module
                })

        except Exception as e:

            print(
                f"[PLUGIN ERROR] {file}"
            )

            print(str(e))

            traceback.print_exc()
            if on_error is not None:
                on_error(file, str(e))

    return plugins