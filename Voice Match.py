import tkinter as tk
from tkinter import filedialog, messagebox
import wave
import math
import struct
import ctypes
import os

RECORD_FILE = "recorded_sample.wav"

def extract_features(wav_path):
    with wave.open(wav_path, 'rb') as wf:
        frames = wf.readframes(wf.getnframes())
        samples = struct.unpack("<" + "h" * (len(frames) // 2), frames)

    energy = sum(abs(s) for s in samples) / len(samples)
    zero_crossings = sum(
        1 for i in range(1, len(samples))
        if samples[i - 1] * samples[i] < 0
    )

    return energy, zero_crossings

def browse_file():
    path = filedialog.askopenfilename(
        filetypes=[("WAV Audio Files", "*.wav")]
    )
    if path:
        uploaded_file.set(path)

def start_recording():
    status_label.config(
        text="Recording started... Speak now",
        fg="red"
    )
    root.update()

    ctypes.windll.winmm.mciSendStringW(
        "open new Type waveaudio Alias recsound", None, 0, None
    )
    ctypes.windll.winmm.mciSendStringW(
        "record recsound", None, 0, None
    )

def stop_recording():
    ctypes.windll.winmm.mciSendStringW(
        f"save recsound {RECORD_FILE}", None, 0, None
    )
    ctypes.windll.winmm.mciSendStringW(
        "close recsound", None, 0, None
    )

    status_label.config(
        text="Recording stopped and saved",
        fg="green"
    )

def match_voices():
    if not uploaded_file.get():
        messagebox.showerror("Error", "Please upload a WAV file")
        return

    if not os.path.exists(RECORD_FILE):
        messagebox.showerror("Error", "Please record your voice first")
        return

    f1 = extract_features(uploaded_file.get())
    f2 = extract_features(RECORD_FILE)

    distance = math.sqrt(
        (f1[0] - f2[0]) ** 2 +
        (f1[1] - f2[1]) ** 2
    )

    similarity = max(0, 100 - distance / 1000)

    result_label.config(
        text=f"Voice Match Similarity: {similarity:.2f} %"
    )

root = tk.Tk()
root.title("Voice Matching Tool")
root.geometry("520x380")

uploaded_file = tk.StringVar()

tk.Label(root, text="Upload Reference Voice Sample (WAV only)").pack(pady=5)
tk.Entry(root, textvariable=uploaded_file, width=60).pack()
tk.Button(root, text="Browse WAV File", command=browse_file).pack(pady=5)

tk.Label(root, text="Record Your Voice").pack(pady=10)
tk.Button(root, text="Start Recording", command=start_recording).pack()
tk.Button(root, text="Stop Recording", command=stop_recording).pack(pady=5)

status_label = tk.Label(root, text="", font=("Arial", 10))
status_label.pack(pady=5)

tk.Button(root, text="Match Voices", command=match_voices).pack(pady=15)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack()

root.mainloop()
