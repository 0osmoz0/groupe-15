# Smashtopia

Jeu de combat type plateforme (inspiration Smash Bros) à deux joueurs, thème Zootopie. Versus local clavier et/ou manettes, sélection de personnage (Judy Hopps, Nick Wilde), sélection de carte, combat avec pourcentages et stocks.

---

## Stack technique

- **Langage** : Python 3
- **Moteur / rendu** : Pygame (écran, sprites, entrées clavier/manette, son)
- **Assets** : images (PNG), GIFs (écrans victoire), vidéos d’intro (MP4 via OpenCV en option), sons (WAV/MP3)
- **Dépendances** : voir `requirements.txt`. Pygame est requis ; Pillow et opencv-python sont optionnels (GIF animés et vidéos d’intro).

---

## Prérequis

- **Python** : version recommandée **3.8 à 3.11**. Pygame et les autres dépendances posent souvent des problèmes de compatibilité avec les versions plus récentes (par ex. 3.14) ; rester sur 3.8–3.11 évite ces erreurs.
- Dépendances listées dans `requirements.txt`

---

## Installation et lancement

```bash
# Cloner le dépôt (ou extraire l’archive)
cd groupe-15

# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate   # Linux / macOS
# ou : venv\Scripts\activate   # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer le jeu (depuis la racine du projet)
python src/main.py
```

Le point d’entrée est `src/main.py`. Le jeu s’ouvre en plein écran par défaut. Sans Pillow, les GIF de victoire s’affichent en image statique ; sans opencv-python, les vidéos d’intro sont ignorées.

**En cas d’erreur d’import** (pygame, Pillow ou autre) après `pip install -r requirements.txt`, il est recommandé de passer par l’environnement virtuel : créer le venv, l’activer, puis réinstaller les dépendances et lancer le jeu dans la même session. Cela évite les conflits avec d’autres installations Python ou un mauvais `pip` utilisé.

---

## Structure du projet (résumé)

- `src/main.py` : point d’entrée, init Pygame, contexte, boucle principale
- `src/game/` : config, contexte, assets, HUD, gestion des entrées, écrans (menu carte, perso, combat, victoire, etc.)
- `src/menu/` : menu principal, paramètres, contrôles
- `src/player/` : joueur (sprite, déplacement, attaques, stats)
- `src/combat/` : hitbox, knockback, hitstun, attaques, projectiles
- `src/smash_platform/` : plateformes
- `src/assets/` : ressources (images, sons, polices, cartes, etc.)

---

## Contrôles

- **Joueur 1** : A/D (déplacement), Espace (saut), S (bas), F (attaque), E (special), G (grab), H (contre). Menus : A/D ou flèches, Entrée/Espace pour valider.
- **Joueur 2** : Flèches (déplacement), Haut (saut), M/I/O/J (attaque, special, grab, contre). Menus : flèches, Entrée/Espace ou Haut pour valider.
- Les touches sont modifiables dans Paramètres > Contrôles. Support manette (jusqu’à 2) en plus du clavier.

---

## Évolution prévue

Ce projet est un prototype réalisé en Python/Pygame. Une migration vers **Unity** est envisagée pour la suite du développement (portabilité, outils, pipeline graphique et sonore).
