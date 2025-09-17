import datetime
import ollama
import speech_recognition as sr
import pyttsx3

# -------------------------
# Text-to-Speech setup
# -------------------------
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# -------------------------
# Speech-to-Text setup
# -------------------------
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        print(f"🗣️ You said: {text}")
        return text
    except Exception as e:
        print("❌ Error:", e)
        return "Sorry, I didn’t catch that."

# -------------------------
# Talk to Ollama
# -------------------------
def ask_ollama(prompt, model="gpt-oss:20b"):
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response["message"]["content"]

# -------------------------
# Main Assistant Flow
# -------------------------
def main():
    speak("What work do you have to get done, and when?")
    response = listen()

    if "Sorry" in response:
        speak("I couldn’t understand. Try again later.")
        return

    speak("Got it. Let me write that down.")

    today = datetime.date.today().strftime("%Y-%m-%d")
    ai_prompt = f"""
    You are my personal assistant. 
    Write a short journal entry for {today} that:
    - Starts by reminding me of the task in a casual, direct way. (e.g., "Hey, you have math homework at 10.")
    - Suggests a very short, simple plan to make it easier to get started or stay focused.
    - Keep it friendly, not too long.
    - Only output the journal entry text, nothing else.

    Task: {response}
    """
    journal_entry = ask_ollama(ai_prompt)

    # Save entry
    with open("journal.txt", "a", encoding="utf-8") as f:
        f.write("\n" + journal_entry.strip() + "\n")

    print("\n✅ Journal Entry:\n", journal_entry.strip())
    speak("Your journal entry h.ps1as been saved.")

if __name__ == "__main__":
    main()