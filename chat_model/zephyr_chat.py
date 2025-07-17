from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class ZephyrChat:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("HuggingFaceH4/zephyr-7b-beta")
        self.model = AutoModelForCausalLM.from_pretrained(
            "HuggingFaceH4/zephyr-7b-beta",
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.chat_history = []
        self.done = False

    def reset(self):
        self.chat_history = []
        self.done = False

    def ask(self, user_input):
        if self.done:
            return "Dream capturing session is already completed. Please start a new one."

        self.chat_history.append({"role": "user", "content": user_input})

        messages = [
            {"role": "system", "content": (
                "You are a Dream Elicitation Assistant. The user is describing a dream."
                " After each message, ask one relevant, contextual follow-up question to help them recall more."
                " Do not ask generic or repeated questions. Make your questions conversational and concise."
                " Avoid phrases like 'in this dream scenario' or 'did you feel...'."
            )}
        ] + self.chat_history

        input_tokens = self.tokenizer.apply_chat_template(messages, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            output = self.model.generate(input_tokens, max_new_tokens=250, do_sample=True, temperature=0.7)
        response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        model_reply = response.split("<|assistant|>")[-1].strip()

        self.chat_history.append({"role": "assistant", "content": model_reply})
        return model_reply

    def end_session_and_paraphrase(self):
        self.done = True
        user_inputs = [msg["content"] for msg in self.chat_history if msg["role"] == "user"]
        if not user_inputs:
            return "No dream input was recorded."

        full_dream = " ".join(user_inputs)

        messages = [
            {"role": "system", "content": (
                "You are a summarizer. Paraphrase the user's dream in a well-structured and vivid way using only the user's inputs."
                " Do not invent or guess anything. Be concise but descriptive."
            )},
            {"role": "user", "content": full_dream}
        ]

        input_tokens = self.tokenizer.apply_chat_template(messages, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            output = self.model.generate(input_tokens, max_new_tokens=100, do_sample=False)
        paraphrased = self.tokenizer.decode(output[0], skip_special_tokens=True)
        final_dream = paraphrased.split("<|assistant|>")[-1].strip()

        return final_dream
