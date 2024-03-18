import os
import time
import numpy
import shutil
import tkinter
import logging
import keyboard
import soundfile
import threading
import sounddevice

import tkinter.ttk as ttk
from tkinter import messagebox

from scipy.io import wavfile
from datetime import datetime

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class GuestbookApp:
    def __init__(self, master):
        self.master = master
        master.title('GUESTBOOK APP')

        self.currently_playing = False
        
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        x_pos = (screen_width - 400) // 2
        y_pos = (screen_height - 300) // 2
        master.geometry(f'400x300+{x_pos}+{y_pos}')

        self.label = tkinter.Label(master, text='Status')
        self.label.place(relx=0.1, rely=0.05, anchor='center')

        self.listbox1 = tkinter.Listbox(master, height=5)
        self.listbox1.bind('<<ListboxSelect>>', self.on_select_listbox1)
        self.listbox1.place(relx=0.1, rely=0.15, relwidth=0.4, relheight=0.7)
        self.scrollbar1 = tkinter.Scrollbar(master, orient='vertical', command=self.listbox1.yview)
        self.scrollbar1.place(relx=0.5, rely=0.15, relheight=0.7)
        self.listbox1.config(yscrollcommand=self.scrollbar1.set)

        self.listbox2 = tkinter.Listbox(master, height=5)
        self.listbox2.bind('<<ListboxSelect>>', self.on_select_listbox2) 
        self.listbox2.place(relx=0.55, rely=0.15, relwidth=0.4, relheight=0.5)
        self.scrollbar2 = tkinter.Scrollbar(master, orient='vertical', command=self.listbox2.yview)
        self.scrollbar2.place(relx=0.95, rely=0.15, relheight=0.5)
        self.listbox2.config(yscrollcommand=self.scrollbar2.set)

        self.folder = 'master'
        if os.path.exists(self.folder):
            files = os.listdir(self.folder)
            for file in files:
                self.listbox1.insert(tkinter.END, file)

        self.copy_button = tkinter.Button(master, text='Copy to Flashdisk', command=self.print_all_files)
        self.copy_button.place(relx=0.4, rely=0.9, relwidth=0.3, relheight=0.08)

        self.delete_button = tkinter.Button(master, text='Delete', command=self.confirm_delete_folder)
        self.delete_button.place(relx=0.1, rely=0.9, relwidth=0.3, relheight=0.08)

        self.rename_button = tkinter.Button(master, text='Rename', command=self.rename_folder)
        self.rename_button.place(relx=0.7, rely=0.9, relwidth=0.3, relheight=0.08)

        self.playing_audio_duration = 0

        self.progress_bar = ttk.Progressbar(master, orient='horizontal', length=160, mode='determinate')
        self.progress_bar.place(relx=0.55, rely=0.7)

        keyboard.on_press_key('m', self.start_recording)

    def record_audio(self, samplerate=44100):
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
                if keyboard.is_pressed('space'):
                    recording = False

        logging.info('Selesai merekam.')
        return numpy.concatenate(audio_data, axis=0)

    def save_audio(self, audio_data, folder, samplerate=44100):
        now = datetime.now()
        folder_name = os.path.join(folder, now.strftime('%Y-%m-%d')) 

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)  

        filename = os.path.join(folder_name, now.strftime('%H%M%S') + '.wav') 
        soundfile.write(filename, audio_data, samplerate)
        logging.info(f'Recording saved as {filename}')

    def start_recording(self, event):
        self.label.config(text='Merekam suara...')
        audio_data = self.record_audio()
        self.save_audio(audio_data, folder)
        self.label.config(text='Rekaman selesai.')

    def on_select_listbox1(self, event):
        selected_index = self.listbox1.curselection()
        if selected_index:
            self.listbox2.delete(0, tkinter.END)
            self.selected_folder = self.listbox1.get(selected_index)
            folder_path = os.path.join('master', self.selected_folder)
            if os.path.exists(folder_path):
                files = os.listdir(folder_path)
                for file in files:
                    self.listbox2.insert(tkinter.END, file)

    def on_select_listbox2(self, event):
        selected_index2 = self.listbox2.curselection()
        if selected_index2 :
            selected_file = self.listbox2.get(selected_index2)
            sound = f'{folder}/{self.selected_folder}/{selected_file}'

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
                confirm = messagebox.askyesno('Delete Folder', f'Are you sure you want to delete `{self.selected_folder}` folder and its contents?')
                if confirm:
                    self.delete_folder()
            else:
                messagebox.showerror('Error', 'Selected folder does not exist.')
        else:
            messagebox.showerror('Error', 'No folder selected.')

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
        self.update_progress_bar()
        sounddevice.wait()
        self.currently_playing = False

    def update_progress_bar(self):
        elapsed_time = 0
        while elapsed_time < self.playing_audio_duration:
            time.sleep(0.1) 
            elapsed_time += 0.1
            progress_percentage = (elapsed_time / self.playing_audio_duration) * 100
            self.progress_bar['value'] = progress_percentage
            self.master.update()

    def rename_folder(self):
        selected_index = self.listbox1.curselection()
        if selected_index:
            selected_folder = self.listbox1.get(selected_index)

            rename_window = tkinter.Toplevel(self.master)
            rename_window.title("Rename Folder")
            rename_window.overrideredirect(True)

            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()

            keyboard_padding = 20
            keyboard_width = 350 + 2 * keyboard_padding
            keyboard_height = 250 + 2 * keyboard_padding

            x_pos = (screen_width - keyboard_width) // 2
            y_pos = (screen_height - keyboard_height) // 2

            rename_window.geometry(f"{keyboard_width}x{keyboard_height}+{x_pos}+{y_pos}")

            def add_char(character):
                current_name = entry.get()
                entry.insert(tkinter.END, character)

            def clear_entry():
                entry.delete(0, tkinter.END)

            def delete_char():
                current_name = entry.get()
                entry.delete(len(current_name) - 1, tkinter.END)

            entry_text = self.listbox1.get(selected_index)
            entry = tkinter.Entry(rename_window)
            entry.insert(tkinter.END, entry_text)
            entry.pack(pady=keyboard_padding)

            button_frame = tkinter.Frame(rename_window)
            button_frame.pack()

            qwerty_layout = [
                ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
                ['z', 'x', 'c', 'v', 'b', 'n', 'm'],
                ['-','_','+','=','^','*','/'],
                ['Clear', 'Delete', 'Cancel', 'Enter']
            ]

            for row in qwerty_layout:
                frame = tkinter.Frame(rename_window)
                frame.pack(pady=5)
                for letter in row:
                    if letter == 'Clear':
                        btn = tkinter.Button(frame, text=letter, width=5, command=clear_entry)
                    elif letter == 'Delete':
                        btn = tkinter.Button(frame, text=letter, width=5, command=delete_char)
                    elif letter == 'Cancel':
                        btn = tkinter.Button(frame, text=letter, width=5, command=rename_window.destroy)
                    elif letter == 'Enter':
                        btn = tkinter.Button(frame, text=letter, width=5, command=lambda: self.complete_rename(entry.get(), selected_index, rename_window))
                    else:
                        btn = tkinter.Button(frame, text=letter, width=3, command=lambda c=letter: add_char(c))
                    btn.pack(side=tkinter.LEFT, padx=2)

    def complete_rename(self, new_name, selected_index, rename_window):
        if new_name:
            old_folder_name = self.listbox1.get(selected_index)
            old_path = os.path.join(self.folder, old_folder_name)
            new_path = os.path.join(self.folder, new_name)
            os.rename(old_path, new_path)

            self.listbox1.delete(selected_index)
            self.listbox1.insert(selected_index, new_name)

            rename_window.destroy()

if __name__ == '__main__':
    folder = 'master'
    if not os.path.exists(folder):
        os.makedirs(folder)

    root = tkinter.Tk()
    app = GuestbookApp(root)
    root.mainloop()
