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

Les variables d'environnement peuvent être définies de deux façons :

#### Option A : Configuration permanente (recommandée)

**Windows - Méthode 1 : Variables système (setx)**
```powershell
# Définir les variables de manière permanente (niveau utilisateur)
setx CLAUDE_CODE_ENABLE_TELEMETRY "1"
setx OTEL_METRICS_EXPORTER "otlp"
setx OTEL_EXPORTER_OTLP_ENDPOINT "http://localhost:4317"
setx OTEL_EXPORTER_OTLP_PROTOCOL "grpc"

# ⚠️ IMPORTANT : Fermer et rouvrir tous les terminaux et Claude Code
# Les variables ne seront disponibles que dans les nouvelles sessions
```

**Windows - Méthode 2 : Profil PowerShell**
```powershell
# Éditer votre profil PowerShell
notepad $PROFILE

# Ajouter ces lignes au fichier :
$env:CLAUDE_CODE_ENABLE_TELEMETRY="1"
$env:OTEL_METRICS_EXPORTER="otlp"
$env:OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
$env:OTEL_EXPORTER_OTLP_PROTOCOL="grpc"

# Sauvegarder et recharger le profil
. $PROFILE
```

**Linux/Mac (Bash)**
```bash
# Ajouter à votre ~/.bashrc (ou ~/.zshrc si vous utilisez Zsh)
echo 'export CLAUDE_CODE_ENABLE_TELEMETRY=1' >> ~/.bashrc
echo 'export OTEL_METRICS_EXPORTER=otlp' >> ~/.bashrc
echo 'export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317' >> ~/.bashrc
echo 'export OTEL_EXPORTER_OTLP_PROTOCOL=grpc' >> ~/.bashrc

# Recharger la configuration
source ~/.bashrc
```

#### Option B : Session temporaire (pour tester)

**Windows (PowerShell)**
```powershell
# Ces variables seront perdues à la fermeture du terminal
$env:CLAUDE_CODE_ENABLE_TELEMETRY="1"
$env:OTEL_METRICS_EXPORTER="otlp"
$env:OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
$env:OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
```

**Linux/Mac**
```bash
# Ces variables seront perdues à la fermeture du terminal
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
```

#### Variables optionnelles

**Logger les prompts utilisateur** (⚠️ données sensibles) :
```bash
# Windows
$env:OTEL_LOG_USER_PROMPTS="1"

# Linux/Mac
export OTEL_LOG_USER_PROMPTS=1
```

#### Vérifier la configuration

```bash
# Windows
echo $env:CLAUDE_CODE_ENABLE_TELEMETRY
echo $env:OTEL_EXPORTER_OTLP_ENDPOINT

# Linux/Mac
echo $CLAUDE_CODE_ENABLE_TELEMETRY
echo $OTEL_EXPORTER_OTLP_ENDPOINT
```

### 3. Redémarrer Claude Code

**IMPORTANT** : Les variables d'environnement ne sont chargées qu'au démarrage d'un processus.

- **Si vous utilisez Claude Code en ligne de commande** : Fermez et rouvrez votre terminal, puis relancez Claude Code
- **Si vous utilisez Claude Code dans un IDE** (IntelliJ, VS Code, etc.) : Redémarrez complètement l'IDE
- **Si vous avez utilisé `setx` sur Windows** : Fermez tous les terminaux et applications, puis relancez-les

Pour vérifier que les variables sont bien chargées avant de lancer Claude Code :
```bash
# Windows
echo $env:CLAUDE_CODE_ENABLE_TELEMETRY

# Linux/Mac
echo $CLAUDE_CODE_ENABLE_TELEMETRY
```

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
sum(increase(claude_code_cost_usage_USD_total[24h]))
```

**Tokens par type** :
```promql
sum by (type) (claude_code_token_usage_tokens_total)
```

**Lignes de code modifiées (1h)** :
```promql
sum(increase(claude_code_lines_of_code_count_total[1h]))
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

5. **Vérifier que les métriques sont bien dans Prometheus** :
   ```bash
   curl 'http://localhost:9090/api/v1/query?query=claude_code_cost_usage_USD_total'
   ```
   Si cette commande retourne des données mais Grafana affiche "No Data", le problème vient du dashboard Grafana.

### Grafana affiche "No Data"

Si Prometheus a bien des données mais Grafana affiche "No Data" :

1. **Vérifier le datasource Prometheus** :
   - Aller dans Configuration > Data sources dans Grafana
   - Vérifier que le datasource "Prometheus" existe et est accessible
   - URL doit être : `http://prometheus:9090`

2. **Tester une requête manuelle** :
   - Aller dans Explore dans Grafana
   - Sélectionner le datasource Prometheus
   - Tester la requête : `claude_code_cost_usage_USD_total`
   - Si ça fonctionne ici mais pas dans le dashboard, le dashboard a peut-être un problème

3. **Réinitialiser Grafana** :
   ```bash
   docker-compose down
   docker volume rm claude-monitoring_grafana-data
   docker-compose up -d
   ```
   Cela rechargera le dashboard avec la configuration correcte.

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

**Note :** Certaines métriques ne s'afficheront que lorsque l'action correspondante est effectuée :
- `commit_count_total` : Seulement quand vous créez des commits
- `lines_of_code_count_total` : Seulement quand du code est modifié

### claude_code_cost_usage_USD_total
Coût en USD par modèle

**Labels** : `model`, `session_id`, `user_account_uuid`, `terminal_type`, etc.

### claude_code_token_usage_tokens_total
Tokens consommés

**Labels** : `type` (input/output/cacheCreation/cacheRead), `model`

### claude_code_active_time_seconds_total
Temps actif de la session en secondes

**Labels** : `type` (user/cli), `session_id`, etc.

### claude_code_lines_of_code_count_total
Lignes de code modifiées

**Labels** : `operation`, `session_id`, etc.

### claude_code_commit_count_total
Nombre de commits Git créés

**Labels** : `session_id`, etc.

### claude_code_code_edit_tool_decision_total
Décisions sur les permissions d'édition de code

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
