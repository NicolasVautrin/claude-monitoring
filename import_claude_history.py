#!/usr/bin/env python3
"""
Import Claude Code conversation history into VictoriaMetrics.
Reads JSONL files from ~/.claude/projects/ and imports tokens/costs with original timestamps.
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from collections import defaultdict

VICTORIA_URL = "http://localhost:9090"
CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"

MODEL_PRICING = {
    "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30},
    "claude-haiku-4-5-20251001": {"input": 1.00, "output": 5.00, "cache_write": 1.25, "cache_read": 0.10},
    "claude-opus-4-20250514": {"input": 15.00, "output": 75.00, "cache_write": 18.75, "cache_read": 1.50},
    "claude-sonnet-3-5-20241022": {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30},
    "claude-sonnet-3-5-20240620": {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30},
}

def calculate_cost(model, tokens):
    """Calculate cost in USD for given model and token counts."""
    if model not in MODEL_PRICING:
        return 0.0

    pricing = MODEL_PRICING[model]
    cost = (
        (tokens.get('input', 0) / 1_000_000 * pricing['input']) +
        (tokens.get('output', 0) / 1_000_000 * pricing['output']) +
        (tokens.get('cache_creation', 0) / 1_000_000 * pricing['cache_write']) +
        (tokens.get('cache_read', 0) / 1_000_000 * pricing['cache_read'])
    )
    return cost

def parse_conversation_file(file_path):
    """Parse a single conversation JSONL file."""
    messages = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        msg = json.loads(line)
                        messages.append(msg)
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        print(f"[!] Error reading {file_path}: {e}")
        return []

    return messages

def extract_metrics(messages):
    """Extract metrics from parsed messages."""
    metrics = []

    for msg in messages:
        if msg.get('type') != 'api_response':
            continue

        usage = msg.get('usage', {})
        model = msg.get('model', 'unknown')
        timestamp_str = msg.get('timestamp')

        if not timestamp_str:
            continue

        # Parse timestamp (ISO format)
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            timestamp_ms = int(dt.timestamp() * 1000)
        except:
            continue

        # Token metrics
        tokens = {
            'input': usage.get('input_tokens', 0),
            'output': usage.get('output_tokens', 0),
            'cache_creation': usage.get('cache_creation_input_tokens', 0),
            'cache_read': usage.get('cache_read_input_tokens', 0),
        }

        # Cost metric
        cost = calculate_cost(model, tokens)

        metrics.append({
            'timestamp': timestamp_ms,
            'model': model,
            'tokens': tokens,
            'cost': cost,
        })

    return metrics

def generate_prometheus_format(all_metrics):
    """Generate Prometheus text format from metrics."""
    lines = []

    # Group by timestamp to create consistent metric exports
    for metric in all_metrics:
        timestamp = metric['timestamp']
        model = metric['model']

        # Token metrics
        for token_type, count in metric['tokens'].items():
            if count > 0:
                lines.append(
                    f'claude_code_token_usage_tokens_total{{model="{model}",type="{token_type}"}} {count} {timestamp}'
                )

        # Cost metric
        if metric['cost'] > 0:
            lines.append(
                f'claude_code_cost_usage_USD_total{{model="{model}"}} {metric["cost"]:.6f} {timestamp}'
            )

    return '\n'.join(lines) + '\n'

def import_to_victoria(prometheus_data):
    """Import Prometheus-format data into VictoriaMetrics."""
    response = requests.post(
        f"{VICTORIA_URL}/api/v1/import/prometheus",
        data=prometheus_data.encode('utf-8'),
        headers={'Content-Type': 'text/plain'}
    )

    if response.status_code == 204:
        return True
    else:
        print(f"[!] Import failed: HTTP {response.status_code}")
        print(f"    Response: {response.text}")
        return False

def main():
    print("[*] Claude Code History Import")
    print(f"[*] Reading from: {CLAUDE_PROJECTS_DIR}")
    print(f"[*] Target: {VICTORIA_URL}")
    print()

    if not CLAUDE_PROJECTS_DIR.exists():
        print(f"[!] Projects directory not found: {CLAUDE_PROJECTS_DIR}")
        return

    # Find all conversation files
    jsonl_files = list(CLAUDE_PROJECTS_DIR.glob("*/conversation.jsonl"))
    print(f"[*] Found {len(jsonl_files)} conversation files")

    # Parse all conversations
    all_metrics = []
    total_messages = 0
    total_tokens = defaultdict(int)
    total_cost = 0.0

    for file_path in jsonl_files:
        messages = parse_conversation_file(file_path)
        metrics = extract_metrics(messages)
        all_metrics.extend(metrics)
        total_messages += len(messages)

        for m in metrics:
            for token_type, count in m['tokens'].items():
                total_tokens[token_type] += count
            total_cost += m['cost']

    print(f"[*] Parsed {total_messages} messages")
    print(f"[*] Total tokens:")
    for token_type, count in sorted(total_tokens.items()):
        print(f"    - {token_type}: {count:,}")
    print(f"[*] Total cost: ${total_cost:,.2f}")
    print()

    # Generate Prometheus format
    print("[*] Generating Prometheus format...")
    prometheus_data = generate_prometheus_format(all_metrics)
    sample_count = len([l for l in prometheus_data.split('\n') if l.strip() and not l.startswith('#')])
    print(f"[*] Generated {sample_count:,} metric samples")
    print()

    # Import to VictoriaMetrics
    print("[*] Importing to VictoriaMetrics...")
    if import_to_victoria(prometheus_data):
        print("[+] Import successful!")
        print()
        print("[+] Check Grafana to see your historical data:")
        print("    http://localhost:3000")
    else:
        print("[!] Import failed")

if __name__ == "__main__":
    main()
