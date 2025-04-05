import subprocess
import pyaudio
import wave
import asyncio
import re

WAV_AM_TRANSCRIBE_AUDIO_URL = "https://wav.am/transcribe_audio/"
WAV_AM_AUTH_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiI0ZGM5NDNjY2IzZWI0YTJiOTQ5OGQ1MWU4NGIyMTJlMSIsInVzZXJuYW1lIjoiU2hlcmxvY2tZYW4iLCJjb25uZWN0aW9uIjoiYXBpIiwiZXhwIjoxNzQ1OTcxMjAwLCJpYXQiOjE3NDExODk0MDl9.HYQKkvO8wRSwpoNMuz4ebYUGxgEZIUbpaVIsRmyUk64"
WAV_PROJECT_ID = "1311"

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 3
OUTPUT_FILENAME = "output.wav"

COMMANDS = {
    "վերեւ": lambda: print("Հրաման: Վերև"),
    "ներքեւ": lambda: print("Հրաման: Ներքև"),
    "աոաջ": lambda: print("Հրաման: Աոաջ"),
    "հետ": lambda: print("Հրաման: Դրոնը հետ է թռնում"),
    "ձախ": lambda: print("Հրաման: Դրոնը ձախ է թռնում"),
    "աջ": lambda: print("Հրաման: Դրոնը աջ է թռնում"),
}

async def transcribe_audio(audio_path):
    transcribe_command = [
        "curl",
        "-X", "POST", WAV_AM_TRANSCRIBE_AUDIO_URL,
        "-H", f"Authorization: {WAV_AM_AUTH_KEY}",
        "-F", f"project_id={WAV_PROJECT_ID}",
        "-F", f"audio_file=@{audio_path}"
    ]
    return subprocess.run(transcribe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


async def process_audio_transcription(audio_path):
    transcription_result = await transcribe_audio(audio_path)
    if transcription_result.returncode != 0:
        print(f"Error during transcription: {transcription_result.stderr}")

    transcription_data = transcription_result.stdout
    print(f"Transcription data: {transcription_data}")


def record_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved as {OUTPUT_FILENAME}")

async def listen_and_process():
    while True:
        record_audio()
        recognized_text = await transcribe_audio(OUTPUT_FILENAME)
        text_from_audio = recognized_text.stdout.strip().lower()
        text_from_audio_clean = re.sub(r'[^\w\s]', '', text_from_audio)

        words = [word.strip() for word in text_from_audio_clean.split() if word.strip()]

        detected_command = None
        for word in words:
            for command in COMMANDS:
                if word == command:
                    detected_command = command
                    break
            if detected_command:
                break

        if detected_command:
            print(f"Recognized: {detected_command}")
            COMMANDS[detected_command]()
        else:
            print("Unknown command. Ignoring.")

if __name__ == "__main__":
    asyncio.run(listen_and_process())
