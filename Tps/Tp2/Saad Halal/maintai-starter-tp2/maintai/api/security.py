
"""Authentification par clé API, transmise dans l'en-tête X-API-Key."""

import secrets

from fastapi import Header, HTTPException, status

from maintai.config import get_settings


def require_api_key(
    x_api_key: str | None = Header(default=None)
) -> None:
    """Refuse la requête si la clé est absente ou fausse."""

    # Récupérer la clé API configurée sur le serveur
    api_key = get_settings().api_key

    # Vérifier que le serveur possède une clé API
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée sur le serveur"
        )

    # Vérifier que la clé reçue est présente et correcte
    if x_api_key is None or not secrets.compare_digest(x_api_key, api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide"
        )
