import logging
import os
import sys
import platform
import tempfile
from datetime import datetime
from typing import List
import serial.tools.list_ports


def setup_logging(log_dir: str = None, log_level: int = logging.DEBUG):
    # Utiliser %TEMP% si aucun dossier n'est donné
    if log_dir is None:
        temp_dir = tempfile.gettempdir()  # Ex: C:\Users\xxx\AppData\Local\Temp
        log_dir = os.path.join(temp_dir, "tamio_logs")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    log_filename = os.path.join(
        log_dir, 
        f"tamio_fs_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    absolute_log_path = os.path.abspath(log_filename)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("Tamio FS - Démarrage de l'application")
    logger.info(f"Fichier log: {absolute_log_path}")
    logger.info(f"Version Python: {sys.version}")
    logger.info(f"Système d'exploitation: {platform.system()} {platform.release()}")
    logger.info("=" * 50)
    
    return logger


def get_com_ports() -> List[str]:
    ports = [p.device for p in serial.tools.list_ports.comports()]
    return ports if ports else ["Aucun port COM disponible"]


def is_windows() -> bool:
    return platform.system() == "Windows"


def can_rename_computer() -> bool:
    return is_windows()


def rename_computer_windows(new_name: str) -> tuple[bool, str]:
    import subprocess
    import socket
    
    if not is_windows():
        return False, "Cette fonctionnalité n'est disponible que sur Windows"
    
    try:
        
        current_hostname = socket.gethostname()
        
        subprocess.run(
            ["wmic", "computersystem", "where", f"name='{current_hostname}'", "rename", new_name],
            check=True,
            capture_output=True,
            text=True
        )
        
        return True, f"Nom de l'ordinateur changé en '{new_name}'. Redémarrage nécessaire."
    except ImportError:
        return False, "Modules Windows requis non disponibles"
    except subprocess.CalledProcessError as e:
        return False, f"Erreur lors du changement de nom : {e.stderr}"
    except Exception as e:
        return False, f"Erreur inattendue : {str(e)}"


def format_file_size(size_bytes: float) -> str:
    for unit in ['o', 'Ko', 'Mo', 'Go']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} To"


class ProgressTracker:
    def __init__(self, total_steps: int):
        self.total_steps = total_steps
        self.current_step = 0
        self.logger = logging.getLogger(__name__)
    
    def step(self, description: str):
        self.current_step += 1
        progress = (self.current_step / self.total_steps) * 100
        self.logger.info(f"[{self.current_step}/{self.total_steps}] ({progress:.1f}%) - {description}")
    
    def complete(self):
        self.logger.info(f"Progression terminée : {self.total_steps}/{self.total_steps} étapes")
