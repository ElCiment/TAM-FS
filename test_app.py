#!/usr/bin/env python3
import sys
import platform

print("=" * 70)
print(" Tamio FS - Application POS de configuration serveur/station")
print("=" * 70)
print()

print(f"Python version: {sys.version}")
print(f"Système d'exploitation: {platform.system()} {platform.release()}")
print()

print("📦 Vérification des modules...")
print()

modules_status = {
    "customtkinter": False,
    "pyserial": False,
    "xml.etree.ElementTree": False,
    "logging": False,
    "socket": False
}

for module_name in modules_status.keys():
    try:
        __import__(module_name)
        modules_status[module_name] = True
        print(f"  ✅ {module_name}")
    except ImportError as e:
        print(f"  ❌ {module_name} - {e}")

print()

print("📁 Vérification des fichiers du projet...")
print()

import os

project_files = {
    "src/app.py": "Lanceur principal (menu)",
    "src/main.py": "Interface principale (serveur)",
    "src/station.py": "Interface station",
    "src/config_manager.py": "Gestionnaire de configuration XML",
    "src/validators.py": "Validateurs de données",
    "src/utils.py": "Utilitaires et logging",
    "src/ui_components.py": "Composants d'interface",
    "README.md": "Documentation",
    "docs/BUILD_GUIDE.md": "Guide de compilation"
}

for filename, description in project_files.items():
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        display_name = filename.replace("src/", "").replace("docs/", "")
        print(f"  ✅ {display_name:25s} ({size:6d} bytes) - {description}")
    else:
        display_name = filename.replace("src/", "").replace("docs/", "")
        print(f"  ❌ {display_name:25s} - {description}")

print()
print("=" * 70)
print()

if platform.system() == "Windows":
    print("✅ SYSTÈME COMPATIBLE")
    print()
    print("Ce système Windows peut exécuter toutes les fonctionnalités de Tamio FS.")
    print()
    print("Pour démarrer l'application:")
    print("  - Avec menu:      python src/app.py")
    print("  - Mode serveur:   python src/main.py")
    print("  - Mode station:   python src/station.py")
else:
    print("⚠️  SYSTÈME NON-WINDOWS DÉTECTÉ")
    print()
    print(f"Vous utilisez {platform.system()}. Certaines fonctionnalités ne sont")
    print("disponibles que sur Windows:")
    print("  - Changement de nom d'ordinateur (nécessite pywin32)")
    print("  - Partages réseau Windows (\\\\serveur\\partage)")
    print()
    print("L'interface graphique peut être testée, mais les opérations système")
    print("Windows ne fonctionneront pas.")

print()
print("=" * 70)
print()
print("📊 STATUT GLOBAL")
print()

all_modules_ok = all(modules_status.values())
all_files_ok = all(os.path.exists(f) for f in project_files.keys())

if all_modules_ok and all_files_ok:
    print("✅ Tous les modules et fichiers sont présents!")
    print("   L'application est prête à être utilisée.")
else:
    print("⚠️  Certains éléments sont manquants:")
    if not all_modules_ok:
        print("   - Installer les modules manquants avec: pip install -r requirements.txt")
    if not all_files_ok:
        print("   - Certains fichiers du projet sont manquants")

print()
print("=" * 70)
