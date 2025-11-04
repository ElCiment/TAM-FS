# Tamio FS - Assistant de Configuration POS

**Version optimisée** - Système de configuration pour Point de Vente (POS) avec architecture serveur/station.

## 📋 Description

Tamio FS est une application desktop Windows qui facilite la configuration d'un système POS (Point of Sale) avec:
- **Serveur**: Configuration centrale pour gérer les paramètres du système
- **Station**: Configuration des postes clients qui se connectent au serveur

## 🎯 Fonctionnalités principales

### Mode Serveur
- ⚙️ Configuration des paramètres généraux (déconnexion automatique, impression, etc.)
- 🎨 Personnalisation de l'interface (mode sombre, taille de police, hauteur des lignes)
- 🔗 Configuration du serveur et de la base de données
- 🛒 Gestion des modes de commande (plan de table, retail, comptoir, pickup, livraison)
- 📝 Configuration MEV Web (informations fiscales québécoises)
- 🖨️ Configuration des imprimantes (IP ou COM)

### Mode Station
- 💻 Configuration du nom d'ordinateur
- 🌐 Connexion au serveur avec test de connectivité
- 📥 Copie automatique des fichiers de configuration depuis le serveur
- ✅ Validation des adresses IP et des connexions réseau

## 🚀 Améliorations de cette version optimisée

### Architecture modulaire
- **config_manager.py**: Gestion centralisée des opérations XML
- **validators.py**: Validation robuste des données (IP, codes postaux, numéros de taxe)
- **utils.py**: Utilitaires et système de logging
- **main.py**: Interface serveur optimisée
- **station.py**: Interface station optimisée


## 📦 Prérequis

### Système d'exploitation
- **Windows** (requis pour certaines fonctionnalités comme le changement de nom d'ordinateur)

### Python
- Python 3.10 ou supérieur

### Dépendances Python
```bash
pip install customtkinter pyserial pywin32
```

## 🔧 Installation

1. **Cloner ou télécharger** le projet
2. **Installer les dépendances**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Créer les dossiers nécessaires** (optionnel, créés automatiquement):
   ```bash
   mkdir -p C:\pos\xml
   mkdir -p logs
   ```

## 📦 Compilation en .exe (Windows)

Pour créer des fichiers .exe distribuables:

### Méthode automatique (RECOMMANDÉ)
```bash
build.bat
```

Cela créera un fichier dans le dossier `dist/`:
- `Tamio_FS.exe` - Application unifiée (choix serveur/station au démarrage)

### Méthode manuelle

1. **Installer PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Compiler l'application**:
   ```bash
   pyinstaller --onefile --windowed --collect-all customtkinter --name "Tamio_FS" src/app.py
   ```

Les fichiers .exe seront dans le dossier `dist/`

**📚 Guide complet**: Consultez `BUILD_GUIDE.md` pour plus de détails

## 🎮 Utilisation

### Lancer l'application (menu de sélection)
```bash
python src/app.py
```

Ou directement en mode serveur/station :
```bash
python src/main.py      # Mode serveur
python src/station.py   # Mode station
```

### Test diagnostic
```bash
python test_app.py
```

## 📁 Structure du projet

```
tamio-fs/
├── src/                    # Code source
│   ├── app.py             # Lanceur principal (menu serveur/station)
│   ├── main.py            # Application serveur
│   ├── station.py         # Application station
│   ├── config_manager.py  # Gestionnaire de configuration XML
│   ├── validators.py      # Validateurs de données
│   ├── ui_components.py   # Composants d'interface réutilisables
│   └── utils.py           # Utilitaires et logging
├── docs/                   # Documentation
│   └── BUILD_GUIDE.md     # Guide de compilation détaillé
├── attached_assets/        # Fichiers originaux (archives)
├── build.bat              # Script de compilation automatique
├── build_debug.bat        # Script de compilation DEBUG
├── test_app.py            # Script de diagnostic
├── README.md              # Ce fichier
├── requirements.txt       # Dépendances Python
└── logs/                  # Fichiers de logs (créé automatiquement)
    └── tamio_fs_YYYYMMDD.log
```

## 🔒 Configuration MEV (Modules d'enregistrement des ventes)

L'application supporte la configuration des informations MEV requises au Québec:
- **Nom commercial**
- **Numéros de taxes** (TPS/TVQ - 9 chiffres)
- **Code d'autorisation**
- **Numéro d'établissement** (6 chiffres)
- **Adresse complète** (numéro, rue, ville)
- **Code postal** (format canadien: A1A 1A1)
- **Secteur** (RES/BAR/CDR)

## 🌐 Configuration réseau

### Serveur
- Doit être accessible via le réseau local
- Partage réseau requis: `\\[IP_SERVEUR]\xml\`

### Station
1. Saisir l'adresse IP du serveur
2. Tester la connexion
3. Copier les fichiers de configuration

### Fichiers synchronisés
- `config.xml` - Configuration générale
- `menu.xml` - Configuration du menu
- `Floor.xml` - Plan de salle
- `layout.xml` - Disposition de l'interface

## 📝 Logs et débogage

Les logs sont automatiquement enregistrés dans le dossier `logs/`:
- Format: `tamio_fs_YYYYMMDD.log`
- Niveau de détail: INFO (erreurs, warnings, opérations importantes)
- Console + fichier simultanément

Pour activer le mode debug:
```python
# Dans utils.py, modifier:
logger = setup_logging(log_level=logging.DEBUG)
```

## ⚠️ Notes importantes

### Compatibilité
- ✅ **Fonctionnalités complètes**: Windows uniquement
- ⚠️ **Fonctionnalités limitées**: Linux/Mac (pas de changement de nom d'ordinateur, pas de support pywin32)

### Sécurité
- Les fichiers XML contiennent des informations sensibles
- Assurez-vous que les permissions réseau sont configurées correctement
- Les logs peuvent contenir des informations de débogage

### Performance
- Validation des données en temps réel
- Test de connectivité avec timeout de 3 secondes
- Copie de fichiers avec gestion des erreurs individuelles

## 🐛 Résolution de problèmes

### Erreur: "Impossible de copier les fichiers"
- Vérifier que le serveur est accessible
- Vérifier que le partage `\\[IP]\xml\` existe
- Vérifier les permissions réseau

### Erreur: "Impossible de changer le nom de l'ordinateur"
- Nécessite les droits administrateur Windows
- Redémarrage requis après le changement

### Erreur: "Module pywin32 introuvable"
- Installer avec: `pip install pywin32`
- Sur Linux/Mac: Fonctionnalité non disponible


---

**Version optimisée** - Améliorations apportées:
- Architecture modulaire
- Validation des données
- Gestion d'erreurs robuste
- Logging complet
- Interface utilisateur améliorée
- Test de connectivité réseau
