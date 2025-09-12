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
def ask_ollama(prompt, model="llama3.2:latest"):
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
    ai_prompt = f"Turn this into a neat journal entry for {today}: {response}"
    journal_entry = ask_ollama(ai_prompt)

    # Save entry
    with open("journal.txt", "a", encoding="utf-8") as f:
        f.write("\n" + journal_entry + "\n")

    print("\n✅ Journal Entry:\n", journal_entry)
    speak("Your journal entry has been saved.")

if __name__ == "__main__":
    main()