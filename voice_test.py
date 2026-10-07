import speech_recognition as sr
import sounddevice as sd

SAMPLE_RATE = 16000
RECORD_SECONDS = 5

# Philips microphone
MICROPHONE = 1

print("================================")
print("   AI ROBOT COMMANDER - VOICE")
print("================================")
print()
print("🎤 Philips microphone selected.")
print("🎤 Speak your command now...")

audio_data = sd.rec(
    int(RECORD_SECONDS * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
    device=MICROPHONE
)

sd.wait()

print("🧠 Understanding your command...")

audio = sr.AudioData(
    audio_data.tobytes(),
    SAMPLE_RATE,
    2
)

recognizer = sr.Recognizer()

try:
    command = recognizer.recognize_google(audio)

    print()
    print("✅ YOU SAID:")
    print(command)
    print()

except sr.UnknownValueError:
    print("❌ I couldn't understand the command.")

except sr.RequestError as e:
    print("❌ Internet/speech service error:", e)