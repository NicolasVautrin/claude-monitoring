# Instructions pour Claude Code

## Règles de développement

### Python
- ❌ **Ne pas utiliser de caractères Unicode/émojis** dans les scripts Python (print, logs, etc.)
- ✅ Utiliser uniquement des caractères ASCII pour éviter les problèmes d'encodage Windows (cp1252)
- Exemple à éviter : `print("📊 Found...")`
- Exemple correct : `print("Found...")`

## Contexte
Ce projet est développé sur Windows où l'encodage par défaut de la console est cp1252, qui ne supporte pas les caractères Unicode/émojis.
