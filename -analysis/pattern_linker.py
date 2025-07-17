# emotion_analysis/pattern_linker.py

import sqlite3
import json
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import seaborn as sns
import pandas as pd

DB_PATH = "dream_logs/dreams.db"

def fetch_dream_analysis():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT date, analysis FROM dream_logs ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()

    data = []
    for row in rows:
        try:
            parsed = json.loads(row[1])
            parsed['date'] = row[0]
            data.append(parsed)
        except:
            continue
    return data

def plot_emotion_over_time(dream_data):
    df = []
    for entry in dream_data:
        date = entry["date"]
        for emotion, score in entry.get("emotions", {}).items():
            df.append({"date": date, "emotion": emotion, "score": score})

    df = pd.DataFrame(df)
    if df.empty:
        return None

    plt.figure(figsize=(8, 4))
    sns.lineplot(data=df, x="date", y="score", hue="emotion", marker="o")
    plt.xticks(rotation=30)
    plt.title("Emotion Trends Over Time")
    plt.tight_layout()

    return fig_to_base64()

def plot_symbol_frequency(dream_data):
    symbol_freq = {}
    for entry in dream_data:
        for symbol in entry.get("symbols", []):
            symbol_freq[symbol] = symbol_freq.get(symbol, 0) + 1

    if not symbol_freq:
        return None

    plt.figure(figsize=(6, 4))
    sns.barplot(x=list(symbol_freq.keys()), y=list(symbol_freq.values()), palette="muted")
    plt.xticks(rotation=30)
    plt.title("Symbol Frequency")
    plt.tight_layout()

    return fig_to_base64()

def plot_intent_frequency(dream_data):
    intent_freq = {}
    for entry in dream_data:
        intent = entry.get("intent", "unknown")
        intent_freq[intent] = intent_freq.get(intent, 0) + 1

    if not intent_freq:
        return None

    plt.figure(figsize=(6, 4))
    sns.barplot(x=list(intent_freq.keys()), y=list(intent_freq.values()), palette="pastel")
    plt.xticks(rotation=30)
    plt.title("Intent Frequency")
    plt.tight_layout()

    return fig_to_base64()

def fig_to_base64():
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    return encoded
