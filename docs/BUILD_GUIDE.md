# Guide de compilation - Tamio FS en .exe

## Prérequis

Avant de compiler, assurez-vous d'avoir :
- Python 3.10+ installé sur Windows
- Toutes les dépendances installées : `pip install -r requirements.txt`
- PyInstaller installé : `pip install pyinstaller`

## Méthode 1 : Script automatique (RECOMMANDÉ)

Utilisez le script batch fourni :

```bash
build.bat
```

Ce script va créer **un seul .exe** avec menu de sélection :
- **Tamio_FS.exe** - Application unifiée (choix serveur/station au démarrage)

Le fichier .exe sera dans le dossier `dist/`

## Méthode 2 : Commande manuelle

```bash
pyinstaller --onefile --windowed --collect-all customtkinter --name "Tamio_FS" src/app.py
```

**Note**: Pour ajouter une icône personnalisée, ajoutez `--icon=chemin/vers/votre_icone.ico` à la commande

## Options de compilation

### Options de base
- `--onefile` : Crée un seul fichier .exe (plus lent au démarrage)
- `--onedir` : Crée un dossier avec l'exe et les dépendances (plus rapide)
- `--windowed` ou `-w` : Masque la console Windows
- `--console` ou `-c` : Affiche la console (utile pour déboguer)

### Options CustomTkinter
- `--collect-all customtkinter` : **OBLIGATOIRE** - Inclut tous les fichiers de CustomTkinter (thèmes, polices)

### Options avancées
- `--name "NomApp"` : Nom du fichier .exe
- `--icon=chemin/vers/icone.ico` : Icône de l'application (optionnel, fichier .ico requis)
- `--add-data "source;destination"` : Ajouter des fichiers supplémentaires (utiliser `;` sur Windows, `:` sur Linux/Mac)

## Structure après compilation

```
dist/
└── Tamio_FS.exe            (Application unifiée - Serveur et Station)

build/                      (Fichiers temporaires - peut être supprimé)
```

## Tester l'exécutable

1. **Test sur votre machine** :
   ```bash
   cd dist
   Tamio_FS.exe
   ```
   
   Au démarrage, un menu s'affiche pour choisir entre :
   - 🖥️ Mode Serveur
   - 💻 Mode Station

2. **Test sur une machine sans Python** :
   - Copiez le fichier .exe sur une machine Windows propre
   - Vérifiez que l'application démarre correctement
   - Testez toutes les fonctionnalités

## Résolution de problèmes courants

### Erreur : "Module customtkinter not found"
**Solution** : Ajoutez `--collect-all customtkinter` à la commande

### Erreur : "Failed to execute script - missing .json files"
**Solution** : Utilisez `--collect-all customtkinter` (déjà inclus dans build.bat)

### L'exe démarre lentement
**Comportement normal** avec `--onefile`. Pour accélérer :
- Utilisez `--onedir` au lieu de `--onefile`
- Ou acceptez le délai (extraction temporaire au démarrage)

### La console s'affiche
**Solution** : Ajoutez `--windowed` à la commande

### Erreur : "pywin32 not found" au démarrage
**Normal** : pywin32 fonctionne uniquement sur Windows. L'exe compilé sur Windows l'inclura automatiquement.

## Distribution

Pour distribuer votre application :

1. **Version simple** : Distribuez juste le fichier .exe
   - Avantage : Un seul fichier
   - Inconvénient : Démarrage plus lent (3-5 secondes)

2. **Version optimisée** : Utilisez `--onedir` et distribuez le dossier complet
   - Avantage : Démarrage instantané
   - Inconvénient : Plusieurs fichiers à distribuer

3. **Installateur** (optionnel) : 
   - Utilisez Inno Setup ou NSIS pour créer un installateur .exe
   - Inclut désinstallation, raccourcis, etc.

## Conseils de production

1. **Testez sur Windows propre** : Machine sans Python installé
2. **Incluez un README** : Instructions d'utilisation pour l'utilisateur
3. **Vérifiez les chemins** : Les chemins relatifs fonctionnent mieux
4. **Logs** : Les fichiers de log seront créés dans le dossier de l'exe
5. **Configuration XML** : Sera créée automatiquement au premier lancement

## Commandes utiles

```bash
# Nettoyer les fichiers de compilation
rmdir /s /q build dist
del /q *.spec

# Recompiler proprement
build.bat

# Voir les dépendances détectées
pyinstaller --collect-all customtkinter --log-level DEBUG main.py

# Ajouter une icône personnalisée (optionnel)
# 1. Créez/obtenez un fichier .ico (icône Windows)
# 2. Ajoutez --icon=mon_icone.ico à la commande pyinstaller
```

## Taille finale estimée

- **Tamio_FS.exe** : ~50-80 MB

La taille est normale pour une application Python avec GUI, car elle inclut :
- Python runtime
- CustomTkinter + Tkinter
- Toutes les dépendances (lxml, pywin32, etc.)
- Bibliothèques système Windows

## Support et débogage

Si vous rencontrez des problèmes :

1. Compilez d'abord avec `--console` pour voir les erreurs
2. Vérifiez les logs dans le dossier `logs/`
3. Testez chaque module individuellement
4. Consultez la documentation PyInstaller : https://pyinstaller.org/

---

**Bon déploiement ! 🚀**
