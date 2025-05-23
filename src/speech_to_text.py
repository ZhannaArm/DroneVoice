import subprocess
import pyaudio
import wave
import asyncio
import re
from good import (
    arm_drone, disarm_drone, takeoff, rotate_drone, move_forward,
    altitude_mode, land_drone, set_altitude, connect_to_drone
)

WAV_AM_TRANSCRIBE_AUDIO_URL = "https://wav.am/transcribe_audio/"
WAV_AM_AUTH_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiI2MzBiNGU5MjM3ZTc0Nzc3ODY2MTA1ZDNhMGZhZDcyMyIsInVzZXJuYW1lIjoiU2hlcmxvY2tZYW4iLCJjb25uZWN0aW9uIjoiYXBpIiwiZXhwIjoxNzU5MTkwNDAwLCJpYXQiOjE3NDczMTgyMDR9.eeqo1ARRSqynKbZxJQ6d79N_PjE_JBR7OcHdB5MdP5c"
WAV_PROJECT_ID = "3228"

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 3
OUTPUT_FILENAME = "output.wav"

master = connect_to_drone()
master.set_mode("GUIDED")

COMMANDS = {
    "սկսել": lambda: arm_drone(master),
    "պրծնել": lambda: disarm_drone(master),
    "վայրէջք": lambda: land_drone(master),
    "վարդան": lambda: altitude_mode(master),
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


async def listen_and_process():
    while True:
        record_audio()
        recognized_text = await transcribe_audio(OUTPUT_FILENAME)
        text_from_audio = recognized_text.stdout.strip().lower()
        text_from_audio_clean = re.sub(r'[^\w\s]', '', text_from_audio)

        for command in COMMANDS:
            if command in text_from_audio_clean:
                COMMANDS[command]()
                break
        else:
            if "թռնել" in text_from_audio_clean:
                match = re.search(r'թռնել\s*(\d+)', text_from_audio_clean)
                if match:
                    alt = float(match.group(1))
                    takeoff(master, alt)
            elif "շրջադարձ" in text_from_audio_clean:
                match = re.search(r'շրջադարձ\s*(\d+)', text_from_audio_clean)
                if match:
                    angle = float(match.group(1))
                    print("շրջադարձ", angle)
                    rotate_drone(master, angle)
            elif "առաջ" in text_from_audio_clean:
                match = re.search(r'առաջ\s*(\d+)', text_from_audio_clean)
                if match:
                    dist = float(match.group(1))
                    move_forward(master, dist)
            elif "վերեւ" in text_from_audio_clean:
                match = re.search(r'վերեւ\s*(\d+)', text_from_audio_clean)
                if match:
                    alt = float(match.group(1))
                    set_altitude(master, alt)
            elif "ռեժիմ" in text_from_audio_clean:
                    if "նստել" in text_from_audio_clean:
                        master.set_mode("LAND")
                    elif "դրսից" in text_from_audio_clean:
                        master.set_mode("GUIDED")
            else:
                print("Անհայտ հրաման:")


if __name__ == "__main__":
    asyncio.run(listen_and_process())
