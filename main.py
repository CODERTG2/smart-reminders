import datetime
import json
import threading
import time
from deepseek_client import DeepseekClient
import speech_recognition as sr
import pyttsx3
import sys
sys.stdout.reconfigure(encoding="utf-8")

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
        print(" Listening...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        print(f" You said: {text}")
        return text
    except Exception as e:
        print(" Error:", e)
        return "Sorry, I didn’t catch that."

# -------------------------
# Talk to DeepSeek
# -------------------------
def ask_deepseek(prompt):
    client = DeepseekClient()
    response = client.chat(
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response["message"]["content"]

# -------------------------
# Reminder System
# -------------------------
def get_motivational_message(task, reminder_type):
    """Generate a motivational message based on the task and reminder type."""
    prompt = f"""
    Create a short, encouraging motivational message (1-2 sentences) for someone about to work on: {task}
    
    This is a {reminder_type} reminder. Make it:
    - Positive and energizing
    - Brief (under 20 words)
    - Appropriate for the timing ({reminder_type})
    
    Just return the motivational message, nothing else.
    """
    return ask_deepseek(prompt)

from plyer import notification

def reminder_notification(task, reminder_type):
    """Show popup and speak motivational reminder."""
    try:
        # Generate motivational message
        motivation = get_motivational_message(task, reminder_type)

        # Create message based on type
        if reminder_type == "halfway":
            time_msg = "You're halfway to your task time!"
        elif reminder_type == "three_quarter":
            time_msg = "Almost time — 75% there!"
        else:
            time_msg = "Final reminder — it’s almost time!"

        full_message = f"{time_msg} {motivation}"

        # 🗣 Speak message
        print(f"\n🔔 REMINDER: {full_message}")
        speak(full_message)

        # 💬 Popup notification
        notification.notify(
            title=f"Reminder: {task}",
            message=full_message,
            timeout=10  # seconds
        )

    except Exception as e:
        print(f"❌ Error in reminder: {e}")
        fallback_msg = f"Reminder: Time to work on {task}!"
        print(f"\n🔔 REMINDER: {fallback_msg}")
        speak(fallback_msg)
        notification.notify(
            title=f"Reminder: {task}",
            message=fallback_msg,
            timeout=10
        )


def schedule_reminder(reminder_time, task, reminder_type):
    """Schedule a reminder to trigger at the specified time."""
    def wait_and_remind():
        # Calculate how long to wait
        current_time = datetime.datetime.now()
        wait_seconds = (reminder_time - current_time).total_seconds()
        
        if wait_seconds > 0:
            print(f"⏱ {reminder_type.replace('_', ' ').title()} reminder scheduled for {reminder_time.strftime('%H:%M')}")
            time.sleep(wait_seconds)
            reminder_notification(task, reminder_type)
        else:
            print(f" Reminder time for {reminder_type} has already passed")
    
    # Start the reminder in a separate thread
    reminder_thread = threading.Thread(target=wait_and_remind, daemon=True)
    reminder_thread.start()

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
    journal_entry = ask_deepseek(ai_prompt)

    # Save entry
    with open("journal.txt", "a", encoding="utf-8") as f:
        f.write("\n" + journal_entry.strip() + "\n")

    print("\n Journal Entry:\n", journal_entry.strip())
    speak("Your journal entry has been saved.")

    prompt = f"""
Parse through the following journal entry and extract the time and task in a JSON format.
Time should be in HH:MM 24-hour format.
Example output:
{{
  "time": "22:00",
  "task": "math homework"
}}

Journal Entry: {journal_entry.strip()}
"""
    # Ask DeepSeek to extract structured info
    json_response_text = ask_deepseek(prompt)

    print("\n🔍 Extracted Info:")
    print(json_response_text)

    try:
        # Clean up Markdown code block formatting
        clean_json = json_response_text.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json.replace("```json", "").replace("```", "").strip()
        elif clean_json.startswith("```"):
            clean_json = clean_json.replace("```", "").strip()

        # Parse JSON
        parsed_data = json.loads(clean_json)

        # Handle list or dict format
        if isinstance(parsed_data, list):
            first_task = parsed_data[0]
        else:
            first_task = parsed_data

        task_time = first_task.get("time", "Unknown")
        task_description = first_task.get("task", "Unknown")

        print(f"⏰ Time: {task_time}")
        print(f"📝 Task: {task_description}")

    except Exception as e:
        print(f"❌ Could not parse JSON response: {e}")
        print(f"Raw response: {repr(json_response_text)}")
        task_time = "Unknown"
        task_description = "Unknown"

    # --- Schedule Reminders ---
    if task_time != "Unknown":
        try:
            time_parts = task_time.split(":")
            task_hour = int(time_parts[0])
            task_minute = int(time_parts[1])

            today = datetime.date.today()
            task_datetime = datetime.datetime.combine(today, datetime.time(task_hour, task_minute))
            current_time = datetime.datetime.now()

            # If time is past, set for tomorrow
            if task_datetime <= current_time:
                task_datetime += datetime.timedelta(days=1)

            print(f" Task scheduled for: {task_datetime.strftime('%Y-%m-%d %H:%M')}")

            # Calculate reminder times
            time_diff = task_datetime - current_time
            halfway_time = current_time + (time_diff * 0.5)
            three_quarter_time = current_time + (time_diff * 0.75)
            nine_tenth_time = current_time + (time_diff * 0.9)

            # Schedule reminders
            schedule_reminder(halfway_time, task_description, "halfway")
            schedule_reminder(three_quarter_time, task_description, "three_quarter")
            schedule_reminder(nine_tenth_time, task_description, "final")

            speak("Your reminders have been scheduled!")

            print("\n Program will keep running to deliver reminders...")
            print("Press Ctrl+C to exit")
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                print("\n Goodbye! Reminders cancelled.")

        except Exception as e:
            print(f" Error parsing task time: {e}")
            speak("I couldn't understand the task time.")
    else:
        speak("No valid task time was found.")


if __name__ == "__main__":
    main()
