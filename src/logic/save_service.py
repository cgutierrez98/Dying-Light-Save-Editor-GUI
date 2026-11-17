"""Logica de carga/guardado de saves, independiente de la UI (sin Tk).

Usa el CLI de Steffen (editor.exe) para descifrar/cifrar. Todos los fallos se
elevan como `SaveError` con un mensaje apto para mostrar al usuario.
"""
import json
import os
import shutil
import subprocess
import sys
import uuid

from logic.config import create_save_backup, prune_backups, atomic_replace
from logic.validation import validate_save_data, SaveValidationError


class SaveError(Exception):
    """Error de carga/guardado con mensaje legible."""


class EditorNotFoundError(SaveError):
    """No se encontro editor.exe."""


class SaveService:
    def __init__(self, editor_path=None, temp_dir=None, candidates=(), runner=subprocess.run):
        self.editor_path = editor_path
        self.candidates = list(candidates)
        self._runner = runner
        if temp_dir is None:
            import tempfile
            temp_dir = os.path.join(tempfile.gettempdir(), "dying_light_save_editor")
        os.makedirs(temp_dir, exist_ok=True)
        token = f"{os.getpid()}_{uuid.uuid4().hex[:8]}"
        self.temp_json = os.path.join(temp_dir, f"._tmp_{token}.json")
        self.temp_save = os.path.join(temp_dir, f"._tmp_{token}.sav")

    # ---------- editor.exe ----------
    def find_editor(self):
        """Devuelve la ruta de editor.exe (o None) y la recuerda en `editor_path`."""
        if self.editor_path and os.path.exists(self.editor_path):
            return self.editor_path
        for c in self.candidates:
            if os.path.exists(c):
                self.editor_path = c
                return c
        found = shutil.which("editor.exe") or shutil.which("editor")
        if found:
            self.editor_path = found
            return found
        return None

    def set_editor(self, path):
        if not path or not os.path.exists(path):
            raise EditorNotFoundError(f"editor.exe no existe: {path}")
        self.editor_path = path

    def run_editor(self, args):
        exe = self.find_editor()
        if not exe:
            raise EditorNotFoundError("editor.exe (Steffen's CLI) was not found.")
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        try:
            ret = self._runner(
                [exe, *args],
                cwd=os.path.dirname(exe) or None,
                capture_output=True,
                creationflags=flags,
            )
        except OSError as e:
            raise SaveError(f"Could not run editor.exe: {e}") from e
        if ret.returncode != 0:
            detail = (getattr(ret, "stderr", b"") or b"").decode("utf-8", "replace").strip()
            msg = f"editor.exe exited with code {ret.returncode}."
            if detail:
                msg += f"\n{detail[-500:]}"
            raise SaveError(msg)
        return ret

    # ---------- carga / guardado ----------
    def load(self, save_path):
        """Descifra el .sav y devuelve el JSON como dict."""
        self._remove(self.temp_json)
        self.run_editor(["sample", save_path, f"--patch={self.temp_json}"])
        if not os.path.exists(self.temp_json):
            raise SaveError("Could not decrypt the selected .sav file.\nTemporary JSON file was not generated.")
        try:
            with open(self.temp_json, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError) as e:
            raise SaveError(f"Error reading save data:\n{e}") from e
        finally:
            self._remove(self.temp_json)

    def save(self, save_path, data):
        """Valida, hace backup obligatorio, cifra y reemplaza el .sav de forma atomica.

        Devuelve la ruta del backup creado.
        """
        try:
            validate_save_data(data)
        except SaveValidationError as e:
            raise SaveError(f"Invalid save data, nothing was written:\n{e}") from e

        backup = create_save_backup(save_path)
        if not backup:
            raise SaveError("Could not create a backup; save cancelled to protect your file.")
        prune_backups(save_path)

        try:
            self._remove(self.temp_save)
            with open(self.temp_json, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            self.run_editor(["update", save_path, f"--patch={self.temp_json}", f"--output={self.temp_save}"])
            if not os.path.exists(self.temp_save):
                raise SaveError("Could not update the .sav file: editor.exe produced no output.")

            atomic_replace(self.temp_save, save_path)
        except SaveError:
            raise
        except OSError as e:
            raise SaveError(f"Failed to save changes:\n{e}") from e
        finally:
            self._remove(self.temp_json)
            self._remove(self.temp_save)
        return backup

    def cleanup(self):
        for p in (self.temp_json, self.temp_save):
            self._remove(p)

    @staticmethod
    def _remove(path):
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass
