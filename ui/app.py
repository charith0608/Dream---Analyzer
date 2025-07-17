# main_app.py
import gradio as gr
from chat_model.zephyr_chat import ZephyrChat
from emotion_analysis.emotion_classifier import EmotionClassifier
from emotion_analysis.emotion_utils import plot_emotion_trends
from emotion_analysis.pattern_linker import (
    plot_emotion_over_time,
    plot_symbol_frequency,
    plot_intent_frequency
)
from utils.dream_storage import store_dream, get_dreams

chatbot = ZephyrChat()
emotion_model = EmotionClassifier()

dream_logs = []  # Global log

def continue_chat(text, history):
    reply = chatbot.ask(text)
    history = history + [(text, reply)]
    return history, ""

def end_dream():
    dream = chatbot.end_session_and_paraphrase()
    emotions = emotion_model.predict(dream)
    store_dream(dream, emotions)
    return dream, str(emotions)

def reset_session():
    chatbot.reset()
    return [], "", "", ""

def show_logs():
    global dream_logs
    dreams = get_dreams()
    dream_logs = dreams
    choices = [f"{d['timestamp']} - {d['text'][:30]}..." for d in dreams]
    return gr.update(choices=choices)

def get_selected_dream(choice_label):
    for d in dream_logs:
        if d['timestamp'] in choice_label:
            return d['text']
    return ""

def show_emotion_trend():
    dreams = get_dreams()
    if not dreams:
        return None
    trend_img = plot_emotion_trends([d["emotions"] for d in dreams])
    return gr.update(value=f"data:image/png;base64,{trend_img}")

def analyze_symbols_and_intent(dream_text):
    symbols = ["water", "snake"] if "water" in dream_text or "snake" in dream_text else []
    intent = "growth"
    return symbols, intent

def analyze_emotion_symbol_intent(text):
    emotions = emotion_model.predict(text)
    symbols, intent = analyze_symbols_and_intent(text)
    result = {
        "emotions": emotions,
        "symbols": symbols,
        "intent": intent
    }
    return str(result)

def generate_dynamic_feedback(dream_text, emotion_json):
    import json
    try:
        parsed = json.loads(emotion_json)
        emotions = parsed.get("emotions", [])
        symbols = parsed.get("symbols", [])
        intent = parsed.get("intent", "")
    except:
        emotions, symbols, intent = [], [], ""

    reflection = "### 🪞 Personalized Reflection Based on Your Dream\n"
    for emotion in emotions:
        if emotion == "anger":
            reflection += "\n🔥 **Anger** - Unresolved frustration?"
        elif emotion == "fear":
            reflection += "\n👻 **Fear** - Facing unknown fears?"
        elif emotion == "sadness":
            reflection += "\n😢 **Sadness** - Emotional loss or burnout?"
        elif emotion == "joy":
            reflection += "\n😊 **Joy** - Feeling content?"
        elif emotion == "surprise":
            reflection += "\n😲 **Surprise** - Unexpected events?"

    for symbol in symbols:
        if symbol == "water":
            reflection += "\n🌊 **Water** - Emotional flow or turmoil?"
        elif symbol == "snake":
            reflection += "\n🐍 **Snake** - Fear or transformation?"
        elif symbol == "chase":
            reflection += "\n🏃‍♂️ **Chase** - Avoiding something?"
        elif symbol == "flight":
            reflection += "\n✈️ **Flying** - Seeking freedom?"
        elif symbol == "death":
            reflection += "\n💀 **Death** - End or transformation?"

    if intent == "growth":
        reflection += "\n🌱 **Growth** - Are you evolving?"
    elif intent == "conflict_resolution":
        reflection += "\n⚖️ **Conflict** - Seeking peace?"
    elif intent == "exploration":
        reflection += "\n🗽️ **Exploration** - Want to discover something?"

    reflection += "\n\n**Try journaling and connecting this dream to real life.**"
    return reflection

def pattern_linking_analysis(choice_label):
    for d in dream_logs:
        if d['timestamp'] in choice_label:
            emotion_plot = plot_emotion_over_time([d])
            symbol_plot = plot_symbol_frequency([d])
            intent_plot = plot_intent_frequency([d])
            return (
              f"<img src='data:image/png;base64,{emotion_plot}' width='100%'>",
              f"<img src='data:image/png;base64,{symbol_plot}' width='100%'>",
              f"<img src='data:image/png;base64,{intent_plot}' width='100%'>"
            )
    return None, None, None

with gr.Blocks(title="Dream Analyzer") as app:
    with gr.Tabs():
        with gr.Tab("🨠 Log Dream"):
            chatbot_box = gr.Chatbot(label="Dream Conversation", type="messages")
            user_input = gr.Textbox(label="Your Dream Input")
            dream_output = gr.Textbox(label="Paraphrased Dream", lines=4)
            emotion_json = gr.Textbox(label="Extracted Emotions (JSON)", visible=False)

            with gr.Row():
                submit_btn = gr.Button("Continue Dream")
                done_btn = gr.Button("Done Dream")
                reset_btn = gr.Button("Start New Dream Session")

            submit_btn.click(fn=continue_chat, inputs=[user_input, chatbot_box], outputs=[chatbot_box, user_input])
            done_btn.click(fn=end_dream, outputs=[dream_output, emotion_json])
            reset_btn.click(fn=reset_session, outputs=[chatbot_box, user_input, dream_output, emotion_json])

        with gr.Tab("📚 View Logged Dreams"):
            dream_list = gr.Dropdown(label="Select a Logged Dream", choices=[])
            dream_view = gr.Textbox(label="Dream Text", lines=6)
            refresh_logs = gr.Button("Refresh Dream List")
            refresh_logs.click(fn=show_logs, outputs=dream_list)
            dream_list.change(fn=get_selected_dream, inputs=dream_list, outputs=dream_view)

        with gr.Tab("🎭 Emotion, Symbol & Intent"):
            input_text = gr.Textbox(label="Paste Paraphrased Dream")
            analyze_btn = gr.Button("Analyze")
            analysis_output = gr.Textbox(label="Detected Emotions & Patterns", lines=4)
            analyze_btn.click(fn=analyze_emotion_symbol_intent, inputs=input_text, outputs=analysis_output)

        with gr.Tab("🔍 Pattern Linking"):
            linked_dream = gr.Dropdown(label="Select Dream for Pattern Analysis", choices=[])
            analyze_pattern = gr.Button("Analyze Pattern")
            emotion_plot = gr.HTML(label="Emotion Over Time")
            symbol_plot = gr.HTML(label="Symbol Frequency")
            intent_plot = gr.HTML(label="Intent Frequency")
            analyze_pattern.click(fn=pattern_linking_analysis, inputs=linked_dream, outputs=[emotion_plot, symbol_plot, intent_plot])
            linked_dream.change(fn=show_logs, outputs=linked_dream)

        with gr.Tab("🪞 Self-Guidance"):
            reflect_input = gr.Textbox(label="Enter a Dream Description")
            reflect_button = gr.Button("Generate Reflection")
            reflection_output = gr.Markdown()
            reflect_button.click(fn=generate_dynamic_feedback, inputs=[reflect_input, emotion_json], outputs=reflection_output)

def launch_app():
    app.launch(share=True)
