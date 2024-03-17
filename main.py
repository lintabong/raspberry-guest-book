import os
import tkinter
import keyboard
import soundfile
import sounddevice
import threading
import numpy
import logging
import time
import shutil
import keyboard

# from tkinter import osk 
import tkinter.ttk as ttk
from tkinter import messagebox

from scipy.io import wavfile
from datetime import datetime

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def record_audio(samplerate=44100):
    logging.info('Merekam suara... (Tekan tombol space untuk berhenti)')
    audio_data = []
    recording = True

    def callback(indata, frames, time, status):
        nonlocal recording

        if status:
            logging.info(status)
            
        audio_data.append(indata.copy())
        if keyboard.is_pressed('space'):
            recording = False

    with sounddevice.InputStream(samplerate=samplerate, channels=2, dtype=numpy.int16, callback=callback):
        while recording:
            sounddevice.sleep(100)
            if keyboard.is_pressed('space'):  # Hentikan perekaman jika tombol spasi ditekan
                recording = False

    logging.info('Selesai merekam.')
    return numpy.concatenate(audio_data, axis=0)

def save_audio(audio_data, folder, samplerate=44100):
    now = datetime.now()
    folder_name = os.path.join(folder, now.strftime('%Y-%m-%d')) 

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)  

    filename = os.path.join(folder_name, now.strftime('%H%M%S') + '.wav') 
    soundfile.write(filename, audio_data, samplerate)
    # wavfile.write(filename, samplerate, audio_data)
    logging.info(f"Recording saved as {filename}")

def play_audio(audio_path, samplerate=44100):
    audio_file = wavfile.read(audio_path)

    duration_seconds = len(audio_file[1]) / samplerate

    sounddevice.play(audio_file[1], samplerate, device=3)
    sounddevice.wait()

def stop_audio():
    sounddevice.stop()
    logging.info('Audio stopped.')


class GuestbookApp:
    def __init__(self, master):
        self.master = master
        master.title('GUESTBOOK APP')

        self.currently_playing = False
        
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        x_pos = (screen_width - 400) // 2
        y_pos = (screen_height - 300) // 2
        master.geometry(f"400x300+{x_pos}+{y_pos}")

        self.label = tkinter.Label(master, text="Status")
        self.label.place(relx=0.1, rely=0.05, anchor="center")
        # self.label.place(x=10, y=10)

        self.listbox1 = tkinter.Listbox(master, height=5)
        self.listbox1.place(relx=0.1, rely=0.15, relwidth=0.4, relheight=0.7)
        self.listbox1.bind("<<ListboxSelect>>", self.on_select_listbox1)
        self.scrollbar1 = tkinter.Scrollbar(master, orient="vertical", command=self.listbox1.yview)
        self.scrollbar1.place(relx=0.5, rely=0.15, relheight=0.7)
        self.listbox1.config(yscrollcommand=self.scrollbar1.set)

        self.listbox2 = tkinter.Listbox(master, height=5)
        self.listbox2.place(relx=0.55, rely=0.15, relwidth=0.4, relheight=0.5)
        self.scrollbar2 = tkinter.Scrollbar(master, orient="vertical", command=self.listbox2.yview)
        self.scrollbar2.place(relx=0.95, rely=0.15, relheight=0.5)
        self.listbox2.config(yscrollcommand=self.scrollbar2.set)
        self.listbox2.bind("<<ListboxSelect>>", self.on_select_listbox2) 

        self.folder = 'master'
        if os.path.exists(self.folder):
            files = os.listdir(self.folder)
            for file in files:
                self.listbox1.insert(tkinter.END, file)

        self.copy_button = tkinter.Button(master, text='Copy to Flashdisk', command=self.print_all_files)
        self.copy_button.place(relx=0.4, rely=0.9, relwidth=0.3, relheight=0.08)

        self.delete_button = tkinter.Button(master, text='Delete', command=self.confirm_delete_folder)
        self.delete_button.place(relx=0.1, rely=0.9, relwidth=0.3, relheight=0.08)

        self.rename_button = tkinter.Button(master, text='Rename', command=self.open_virtual_keyboard)
        self.rename_button.place(relx=0.7, rely=0.9, relwidth=0.3, relheight=0.08)

        self.playing_audio_duration = 0

        self.progress_bar = ttk.Progressbar(master, orient='horizontal', length=160, mode='determinate')
        self.progress_bar.place(relx=0.55, rely=0.7)

        # progress_bar['value'] = 160

        keyboard.on_press_key('m', self.start_recording)

    def start_recording(self, event):
        self.label.config(text="Merekam suara...")
        audio_data = record_audio()
        save_audio(audio_data, folder)
        self.label.config(text="Rekaman selesai.")

    def on_select_listbox1(self, event):
        selected_index = self.listbox1.curselection()
        if selected_index:
            self.listbox2.delete(0, tkinter.END)
            # Mendapatkan nama folder dari item yang dipilih pada listbox1
            self.selected_folder = self.listbox1.get(selected_index)
            # Mendapatkan isi dari folder master
            folder_path = os.path.join('master', self.selected_folder)
            if os.path.exists(folder_path):
                files = os.listdir(folder_path)
                for file in files:
                    self.listbox2.insert(tkinter.END, file)

    def on_select_listbox2(self, event):  # Menambahkan fungsi untuk event pada listbox2
        # Mendapatkan indeks item yang dipilih pada listbox2
        selected_index2 = self.listbox2.curselection()
        if selected_index2 :
            # Mendapatkan nama file dari item yang dipilih pada listbox2
            selected_file = self.listbox2.get(selected_index2)
            sound = f'{folder}/{self.selected_folder}/{selected_file}'
            # threading.Thread(target=self.play_audio, args=(sound,)).start()

            if not self.currently_playing:
                logging.info(f'Play sound: {sound}')
                threading.Thread(target=self.play_audio, args=(sound,)).start()

    def print_all_files(self):
        logging.info(f"Files in 'master/{self.selected_folder}':")
        folder_path = os.path.join(self.folder, self.selected_folder)
        if os.path.exists(folder_path):
            destination_folder = 'flashdisk'
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)

            files = os.listdir(folder_path)
            for file in files:
                logging.info(f"- {file}")

                source = os.path.join(folder_path, file)
                destination = os.path.join(destination_folder, file)
                shutil.copyfile(source, destination)

    def confirm_delete_folder(self):
        if self.selected_folder:
            folder_path = os.path.join(self.folder, self.selected_folder)
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                confirm = messagebox.askyesno("Delete Folder", f"Are you sure you want to delete '{self.selected_folder}' folder and its contents?")
                if confirm:
                    self.delete_folder()
            else:
                messagebox.showerror("Error", "Selected folder does not exist.")
        else:
            messagebox.showerror("Error", "No folder selected.")

    def delete_folder(self):
        folder_path = os.path.join(self.folder, self.selected_folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            self.listbox1.delete(0, tkinter.END)
            files = os.listdir(self.folder)
            for file in files:
                self.listbox1.insert(tkinter.END, file)
            logging.info(f"Folder '{self.selected_folder}' and its contents deleted.")

    def play_audio(self, audio_path, samplerate=44100):
        audio_file = wavfile.read(audio_path)
        self.playing_audio_duration = len(audio_file[1]) / samplerate

        self.currently_playing = True
        sounddevice.play(audio_file[1], samplerate, device=3)
        self.update_progress_bar()  # Panggil metode update progress bar saat audio dimulai
        sounddevice.wait()
        self.currently_playing = False

    # Metode baru untuk mengupdate nilai progress bar berdasarkan waktu yang telah berlalu
    def update_progress_bar(self):
        elapsed_time = 0
        while elapsed_time < self.playing_audio_duration:
            time.sleep(0.1)  # Tunggu sebentar sebelum mengupdate nilai progress bar
            elapsed_time += 0.1
            progress_percentage = (elapsed_time / self.playing_audio_duration) * 100
            self.progress_bar['value'] = progress_percentage
            self.master.update()

    def open_virtual_keyboard(self):
        keyboard_window = tkinter.Toplevel(self.master)
        keyboard_window.title("Virtual Keyboard")

        # Daftar huruf qwerty
        qwerty_layout = [
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm']
        ]

        # Buat tombol untuk setiap huruf di qwerty_layout
        for row in qwerty_layout:
            frame = tkinter.Frame(keyboard_window)
            frame.pack(pady=5)
            for letter in row:
                btn = tkinter.Button(frame, text=letter, width=3, command=lambda l=letter: self.btn_click(l))
                btn.pack(side=tkinter.LEFT, padx=2)

        # Buat tombol untuk angka 0 hingga 9
        numbers_layout = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['0']
        ]

        for row in numbers_layout:
            frame = tkinter.Frame(keyboard_window)
            frame.pack(pady=5)
            for number in row:
                btn = tkinter.Button(frame, text=number, width=3, command=lambda n=number: self.btn_click(n))
                btn.pack(side=tkinter.LEFT, padx=2)

    def btn_click(self, letter):
        print(f"You clicked {letter}")

if __name__ == '__main__':
    folder = 'master'
    if not os.path.exists(folder):
        os.makedirs(folder)

    root = tkinter.Tk()
    app = GuestbookApp(root)
    root.mainloop()
