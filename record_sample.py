import sounddevice
import soundfile
import numpy

def record_audio(duration, samplerate=44100):
    print("Merekam suara...")

    audio_data = sounddevice.rec(int(samplerate * duration), samplerate=samplerate, channels=2, dtype=numpy.int16)
    sounddevice.wait()

    print("Selesai merekam.")

    return audio_data

def save_audio(audio_data, filename, samplerate=44100):
    soundfile.write(filename, audio_data, samplerate)

if __name__ == "__main__":
    duration = 5
    filename = "recorded_audio2.wav"

    audio_data = record_audio(duration)
    save_audio(audio_data, filename)
