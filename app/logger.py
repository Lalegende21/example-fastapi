import logging

# Configuration de base du logger
logging.basicConfig(
    level=logging.INFO,  # Niveau minimal de logs
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# Création d'un logger spécifique à l'app
logger = logging.getLogger("fastapi_app")