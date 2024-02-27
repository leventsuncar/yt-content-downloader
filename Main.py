import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import pytube

videos = {}
progress_bar = None
downloaded_message = None


def get_video_info():
    is_sound = mp3_var.get()
    video_url = videoUrl.get()
    yt = pytube.YouTube(video_url)
    yt.register_on_progress_callback(on_progress)
    yt.register_on_complete_callback(on_complete)
    streams = yt.streams.filter(only_audio=is_sound, progressive=not is_sound)

    # Listbox'ı temizle
    stream_listbox.delete(0, tk.END)

    # Stream bilgilerini Listbox'a ekle
    for i, stream in enumerate(streams):
        if not stream.mime_type.endswith("webm"):
            if stream.type.startswith('audio'):
                stream_info = f"{i + 1}. {stream.abr if stream.abr is not None else ''} {stream.mime_type if stream.mime_type is not None else ''}."
            else:
                stream_info = f"{i + 1}. {stream.resolution + ' ' if stream.resolution is not None else ''}{stream.mime_type if stream.mime_type is not None else ''}."
            stream_listbox.insert(tk.END, stream_info)
            videos[i] = stream


def download_selected_content(event):
    selected_index = stream_listbox.curselection()

    if not selected_index:
        return

    selected_index = selected_index[0]

    # Seçilen öğenin değerini al
    selected_value = stream_listbox.get(selected_index)

    # Eğer selected_index videos sözlüğünde yoksa, fonksiyondan çık
    if selected_index not in videos:
        return

    # Videos sözlüğünden stream objesini al
    stream: pytube.Stream = videos.get(selected_index)

    # Eğer stream objesi None değilse, download() metodunu çağır
    if stream:
        # Kullanıcıdan indirme konumu seçmesini iste
        output_path = filedialog.askdirectory()

        # Eğer bir konum seçilmediyse, fonksiyondan çık
        if not output_path:
            return
        try:
            # TODO Aynı isimde dosya var ise üstüne yazıyor
            file_name = stream.default_filename
            file_name = find_file_name(file_name, output_path)
            stream.download(output_path, file_name)
            print("Video başarıyla indirildi.")
            show_toast("Video downloaded!")
        except Exception as e:
            print(f"Hata oluştu: {e}")


def find_file_name(file_name, output_path):
    full_path = os.path.join(output_path, file_name)  # doğru seperator'ü kullansın diye
    if os.path.exists(full_path):  # Öncesinde new diye işaretlediğim dosya var mı?
        fresh_name = ""
        if file_name.__contains__("_new"):
            parts = file_name.split("_new")  # Bu new diye işaretlediğim kaçıncı dosya?
            old_index = parts[1][0]  # FIXME iki haneli veya daha uzun ise yani 9 kereden fazla inidirildiyse bug
            new_index = int(old_index) + 1
            fresh_name = parts[0] + "_new" + parts[1].replace(old_index.__str__(), new_index.__str__())
        else:  # inşaalah başka "." yoktur
            parts = file_name.split(".")
            just_file_name = parts[0] + "_new1"
            new_file_name = just_file_name + "." + parts[1]
            fresh_name = new_file_name
        return find_file_name(fresh_name, output_path)
    else:
        return file_name


def show_toast(message):
    toast = tk.Toplevel()
    toast.geometry("200x100+400+300")
    toast.wm_attributes("-topmost", 1)  # Diğer pencerelerin üzerinde göster
    toast.title("Toast")
    label = ttk.Label(toast, text=message, padding=20)
    label.pack()
    toast.after(3000, toast.destroy)


def on_progress(stream, chunk, remaining):
    global progress_bar
    if progress_bar is None:
        progress_bar = ttk.Progressbar(center_frame, orient="horizontal", length=200, mode="determinate")
        progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
    progress = ((stream.filesize - remaining) * 100) / stream.filesize
    progress_bar["value"] = progress
    windowManager.update()


def on_complete(stream, file_path):
    global progress_bar
    global downloaded_message
    if progress_bar is not None:
        progress_bar.destroy()
        progress_bar = None
    if downloaded_message is None:
        downloaded_message = ttk.Label(center_frame, text="Video Downloaded")
        downloaded_message.grid(row=5, column=0, columnspan=3)
    windowManager.update()


def clear_interface():
    global downloaded_message
    if downloaded_message is not None:
        downloaded_message.destroy()  # Yeni video indirmeden önce indirildi yazmasın
        downloaded_message = None
    videoUrl.delete(0, tk.END)  # Input text'i temizle
    stream_listbox.delete(0, tk.END)  # Seçenekleri temizle


def download_another_video():
    clear_interface()


windowManager = tk.Tk()
windowManager.geometry("640x480")
windowManager.title("Video Downloader")

style = ttk.Style()
style.configure("TEntry", padding=5, relief="raised", background="#black")
style.configure("TButton", padding=5, relief="raised", background="#4caf50", foreground="black")
style.configure("CustomCheckbutton.TCheckbutton", padding=10, relief="raised")

center_frame = ttk.Frame(windowManager)
center_frame.place(relx=0.5, rely=0.5, anchor="center")

ttk.Label(center_frame, text='VideoURL').grid(row=0, column=0, padx=10, pady=10)
videoUrl = ttk.Entry(center_frame, style="TEntry")
videoUrl.grid(row=0, column=1, padx=10, pady=10)

mp3_var = tk.BooleanVar()
checkButton = ttk.Checkbutton(center_frame, text="MP3", style="CustomCheckbutton.TCheckbutton", variable=mp3_var)
checkButton.grid(row=0, column=2, padx=10, pady=10)

get_info_button = ttk.Button(center_frame, text="Get Video Info", style="TButton", command=get_video_info)
get_info_button.grid(row=2, column=0, columnspan=3, pady=10)

close_button = ttk.Button(center_frame, text="Close", command=windowManager.destroy, style="TButton")
close_button.grid(row=3, column=0, columnspan=3, pady=10)

download_another_button = ttk.Button(center_frame, text="Download another video", command=download_another_video,
                                     style="TButton")
download_another_button.grid(row=6, column=0, columnspan=3, pady=10)

# Stream listbox'ını oluştur ve bağla
stream_listbox = tk.Listbox(center_frame, selectmode=tk.SINGLE)
stream_listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
stream_listbox.bind("<<ListboxSelect>>", download_selected_content)

windowManager.mainloop()
