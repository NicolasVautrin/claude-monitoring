# Claude Code Monitoring

Stack OpenTelemetry locale pour monitorer votre usage et consommation Claude Code.

## 📊 Qu'est-ce que c'est ?

Une stack de monitoring complète pour suivre :
- **Tokens consommés** (input, output, cache) par modèle
- **Coûts API** en USD
- **Sessions** et temps actif
- **Code modifié** (lignes ajoutées/supprimées)
- **Git activity** (commits, PRs)
- **Tool usage** (accepté/rejeté)

## ✨ Fonctionnalités

- ✅ **100% local** : Aucune donnée envoyée sur internet
- ✅ **Prêt à l'emploi** : Dashboard Grafana pré-configuré
- ✅ **Léger** : ~100 MB RAM, ~50 MB disque (hors données)
- ✅ **Historique** : 30 jours de métriques conservées
- ✅ **Open Source** : Stack complète gratuite

## 🚀 Quick Start

### Prérequis

- Docker Desktop installé et démarré
- Claude Code installé

### 1. Démarrer la stack

```bash
# Cloner ou naviguer dans le repo
cd claude-monitoring

# Démarrer tous les services
docker-compose up -d

# Vérifier que tout tourne
docker-compose ps
```

### 2. Configurer Claude Code

#### Windows (PowerShell)
```powershell
# Ajouter à votre profil PowerShell ou définir à chaque session
$env:CLAUDE_CODE_ENABLE_TELEMETRY="1"
$env:OTEL_METRICS_EXPORTER="otlp"
$env:OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
```

#### Linux/Mac (Bash/Zsh)
```bash
# Ajouter à votre ~/.bashrc ou ~/.zshrc
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

**Optionnel** : Logger les prompts
```bash
export OTEL_LOG_USER_PROMPTS=1
```

### 3. Redémarrer Claude Code

Fermez et relancez Claude Code pour que les variables d'environnement soient prises en compte.

### 4. Accéder aux interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |

## 📈 Utilisation

### Grafana

1. Ouvrir http://localhost:3000
2. Login : `admin` / `admin`
3. Le dashboard "Claude Code Usage" devrait apparaître automatiquement
4. Sélectionner votre période de temps en haut à droite

### Prometheus (requêtes brutes)

Exemples de requêtes PromQL :

**Coût total cumulé (24h)** :
```promql
sum(increase(claude_code_cost_usage_total[24h]))
```

**Tokens par type** :
```promql
sum by (token_type) (claude_code_token_usage_total)
```

**Sessions actives** :
```promql
claude_code_session_count
```

**Lignes de code modifiées (1h)** :
```promql
sum(increase(claude_code_lines_modified_total[1h]))
```

## 📁 Structure du projet

```
claude-monitoring/
├── docker-compose.yml                    # Stack Docker complète
├── otel-collector-config.yaml           # Config OpenTelemetry
├── prometheus.yml                        # Config Prometheus
├── grafana-provisioning/                # Auto-config Grafana
│   ├── datasources/
│   │   └── prometheus.yaml              # Datasource Prometheus
│   └── dashboards/
│       ├── dashboards.yaml              # Provider dashboards
│       └── claude-usage.json            # Dashboard pré-configuré
├── .gitignore                           # Ignore volumes Docker
├── README.md                            # Ce fichier
├── start.sh                             # Script démarrage (Linux/Mac)
└── start.bat                            # Script démarrage (Windows)
```

## 🔧 Configuration avancée

### Changer la rétention des données

Dans `docker-compose.yml`, modifier :
```yaml
command:
  - '--storage.tsdb.retention.time=30d'  # 30 jours par défaut
```

### Réduire la cardinalité (économiser l'espace)

Variables d'environnement Claude Code :
```bash
export OTEL_METRICS_INCLUDE_SESSION_ID=false     # Défaut: true
export OTEL_METRICS_INCLUDE_ACCOUNT_UUID=false   # Défaut: true
```

### Exporter vers d'autres plateformes

Le collecteur OTLP peut aussi exporter vers :
- Datadog
- New Relic
- Honeycomb
- Jaeger

Modifier `otel-collector-config.yaml` section `exporters`.

## 🐛 Troubleshooting

### Les métriques n'arrivent pas

1. **Vérifier que les conteneurs tournent** :
   ```bash
   docker-compose ps
   ```

2. **Vérifier les logs du collecteur** :
   ```bash
   docker-compose logs -f otel-collector
   ```

3. **Vérifier la connexion Claude Code** :
   ```bash
   # Windows
   echo $env:OTEL_EXPORTER_OTLP_ENDPOINT

   # Linux/Mac
   echo $OTEL_EXPORTER_OTLP_ENDPOINT
   ```
   Doit afficher : `http://localhost:4317`

4. **Relancer Claude Code** après avoir défini les variables

### Port déjà utilisé

Si le port 3000, 4317, ou 9090 est déjà utilisé, modifier dans `docker-compose.yml` :
```yaml
ports:
  - "3001:3000"  # Utiliser 3001 au lieu de 3000
```

### Grafana ne démarre pas

```bash
# Vérifier les logs
docker-compose logs grafana

# Réinitialiser les volumes si nécessaire
docker-compose down -v
docker-compose up -d
```

### Reset complet

```bash
# Arrêter et supprimer tous les volumes
docker-compose down -v

# Redémarrer proprement
docker-compose up -d
```

## 📊 Métriques disponibles

### claude_code_cost_usage_total
Coût en USD par modèle

**Labels** : `model`, `session_id`, `user.account_uuid`

### claude_code_token_usage_total
Tokens consommés

**Labels** : `token_type` (input/output/cache), `model`

### claude_code_session_count
Nombre de sessions actives

### claude_code_lines_modified_total
Lignes de code ajoutées/supprimées

**Labels** : `operation` (added/removed)

### claude_code_git_commits_total
Commits Git créés par Claude

### claude_code_tool_decisions_total
Décisions sur les permissions d'outils

**Labels** : `decision` (accepted/rejected)

## ⚠️ Notes importantes

- **Approximations** : Les coûts sont des estimations. Pour la facturation officielle, consultez votre fournisseur d'API.
- **Local uniquement** : Cette stack est conçue pour un usage local individuel.
- **Données sensibles** : Les prompts peuvent contenir des données sensibles. Les volumes Docker restent sur votre machine.

## 🤝 Contribution

N'hésitez pas à :
- Améliorer les dashboards Grafana
- Ajouter des alertes
- Optimiser les configs
- Partager vos requêtes PromQL utiles

## 📝 License

MIT

## 🔗 Ressources

- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code/monitoring-usage)
- [OpenTelemetry](https://opentelemetry.io/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
