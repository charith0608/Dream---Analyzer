# emotion_analysis/emotion_utils.py

import matplotlib.pyplot as plt
from io import BytesIO
import base64

def plot_emotion_trends(emotion_dicts):
    emotion_totals = {}
    for emo in emotion_dicts:
        for k, v in emo.items():
            emotion_totals[k] = emotion_totals.get(k, 0) + v

    emotions = list(emotion_totals.keys())
    scores = [emotion_totals[k] for k in emotions]

    plt.figure(figsize=(6, 4))
    plt.bar(emotions, scores, color="skyblue")
    plt.title("Overall Emotion Trends in Logged Dreams")
    plt.xticks(rotation=30)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_bytes = buf.getvalue()
    buf.close()

    return base64.b64encode(img_bytes).decode("utf-8")
