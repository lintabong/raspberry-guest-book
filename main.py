import tkinter as tk

def on_button_click():
    label.config(text="Hello, " + entry.get())

# Membuat jendela utama
root = tk.Tk()
root.title("Aplikasi Tkinter Sederhana")

# Membuat label
label = tk.Label(root, text="Masukkan nama:")
label.pack(pady=10)

# Membuat entry (input teks)
entry = tk.Entry(root)
entry.pack(pady=10)

# Membuat tombol
button = tk.Button(root, text="Click Me", command=on_button_click)
button.pack(pady=10)

# Menjalankan loop utama Tkinter
root.mainloop()
