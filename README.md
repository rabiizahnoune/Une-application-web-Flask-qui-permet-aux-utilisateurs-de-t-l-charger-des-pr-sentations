# Slide Downloader

Une application web Flask qui permet aux utilisateurs de télécharger des présentations SlideShare en PDF en entrant le nom d'une technologie (par exemple, "kafka"). L'application effectue une recherche Google via l'API Custom Search, scrape les slides avec Selenium, et fusionne les images en un PDF.

## Fonctionnalités
- Interface web simple pour entrer une technologie.
- Recherche automatique des présentations SlideShare via Google Custom Search API.
- Téléchargement des slides en haute résolution (2048w).
- Conversion des images en un fichier PDF téléchargeable.

## Prérequis
- **Python 3.12+** installé (vérifiez avec `py --version`).
- **Google Chrome** et **ChromeDriver** compatibles avec votre version de Chrome.
- Une **clé API Google** pour Custom Search API.
- Un **ID de moteur de recherche personnalisé (CX)** configuré pour SlideShare.

