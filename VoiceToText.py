import pyaudio
import wave

def Record_Speach_from_mic():
    CHUNK              = 1024                     
    FORMAT             = pyaudio.paInt16            
    CHANNELS           = 1                          
    RATE               = 44100                      
    RECORD_SECONDS     = 5                     
    WAVE_OUTPUT_FILENAME = "output.wav" 

    pyaudio_obj = pyaudio.PyAudio()

    stream = pyaudio_obj.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,                 
        frames_per_buffer=CHUNK     
    )

    print("Recording started for 5 seconds…")

    frames = []
    for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording stopped.")

    stream.stop_stream()
    stream.close()
    pyaudio_obj.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pyaudio_obj.get_sample_size(FORMAT))
    wf.setframerate(RATE)              
    wf.writeframes(b"".join(frames))
    wf.close()

    print(f"WAV file saved: {WAVE_OUTPUT_FILENAME}")
