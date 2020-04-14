from tkinter import *
import webbrowser
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Progressbar
from tkinter import filedialog
from tkinter import messagebox
import json
import requests
import time
import threading
import os
import datetime

def callback(url):
    webbrowser.open_new(url)

def browse_button():    
    filename = filedialog.askdirectory()
    gui.folder_path = filename
    gui.entry_directory.delete(0,END)
    gui.entry_directory.insert(0,filename)
    
def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

class GUI:
    def __init__(self, master):
        self.master = master
                
        self.folder_path = os.getcwd()

        self.master.title("Streamable Video Downloader")
        self.master.geometry('600x550')
        self.master.minsize(600, 550)
        self.master.maxsize(600, 550)

        self.text_instruction1 = Label(self.master, text="Log in to streamable, open API page and copy paste the content to text field below")
        self.text_instruction1.pack()

        self.link1 = Label(self.master, text="API page", fg="blue", cursor="hand2")
        self.link1.pack()
        self.link1.bind("<Button-1>", lambda e: callback("https://ajax.streamable.com/videos?sort=date_added&sortd=DESC&count=10000&page=1"))

        self.entry_api = ScrolledText(self.master, width=70, height=8)
        self.entry_api.pack()
        
        self.button_load_json = Button(self.master, text="Load videos", command=vid_list.get_list)
        self.button_load_json.place(x = 10,y = 180,width=580,height=30)
        
        self.text_total_videos = Label(self.master, text="All videos")
        self.text_total_videos.place(x = 10,y = 220,width=90,height=30)        
        self.entry_total_videos = Entry(window,width=10, state='disabled')
        self.entry_total_videos.place(x = 110,y = 220,width=90,height=30)        
        
        self.text_total_duration = Label(self.master, text="Total duration")
        self.text_total_duration.place(x = 200,y = 220,width=90,height=30)        
        self.entry_total_duration = Entry(window,width=10, state='disabled')
        self.entry_total_duration.place(x = 290,y = 220,width=90,height=30)
        
        self.text_total_size = Label(self.master, text="Total size")
        self.text_total_size.place(x = 380,y = 220,width=90,height=30)        
        self.entry_total_size = Entry(window,width=10, state='disabled')
        self.entry_total_size.place(x = 470,y = 220,width=90,height=30)        
        
        self.text_total_pending_delete_videos = Label(self.master, text="Pending delete")
        self.text_total_pending_delete_videos.place(x = 10,y = 260,width=90,height=30)        
        self.entry_total_pending_delete_videos = Entry(window,width=10, state='disabled')
        self.entry_total_pending_delete_videos.place(x = 110,y = 260,width=90,height=30)        
        
        self.text_total_pending_delete_duration = Label(self.master, text="Total duration")
        self.text_total_pending_delete_duration.place(x = 200,y = 260,width=90,height=30)        
        self.entry_total_pending_delete_duration = Entry(window,width=10, state='disabled')
        self.entry_total_pending_delete_duration.place(x = 290,y = 260,width=90,height=30)
        
        self.text_total_pending_delete_size = Label(self.master, text="Total size")
        self.text_total_pending_delete_size.place(x = 380,y = 260,width=90,height=30)        
        self.entry_total_pending_delete_size = Entry(window,width=10, state='disabled')
        self.entry_total_pending_delete_size.place(x = 470,y = 260,width=90,height=30)  
        
        self.is_pending_checked = IntVar()
        self.check_download_only_pending = Checkbutton(self.master, text='Download only marked as pending to delete', onvalue=1, offvalue=0, variable=self.is_pending_checked)
        self.check_download_only_pending.place(x = 10,y = 300,width=270,height=30)
                
        var = IntVar()
        var.set("5")
        self.text_threads_count = Label(self.master, text="Threads:")
        self.text_threads_count.place(x = 450,y = 300,width=50,height=30)        
        self.spin_threads_count = Spinbox(self.master, from_=0, to=100, textvariable=var)
        self.spin_threads_count.place(x = 500,y = 300,width=90,height=30)
        

        self.text_save_to = Label(self.master, text="Save to")
        self.text_save_to.place(x = 10,y = 350,width=60,height=30)

        self.entry_directory = Entry(self.master)
        self.entry_directory.place(x = 80,y = 350,width=500,height=30)
        self.entry_directory.insert(0,os.getcwd())

        self.browse_button = Button(text="Browse", command=browse_button)
        self.browse_button.place(x = 540,y = 350,width=50,height=30)
        
        self.button_start_download = Button(self.master, text="Start download", command=download_manager.start_thread)
        self.button_start_download.place(x = 10,y = 400,width=580,height=50)
        
        self.progress_bar = Progressbar(self.master, length=580)
        self.progress_bar.place(x = 10,y = 480,width=580,height=30)        
        self.progress_bar['value'] = 0
        
        self.text_progress_finished = Label(self.master, text="", justify="left")
        self.text_progress_finished.place(x = 10,y = 510,width=60,height=30)
        
        self.text_total_downloaded = Label(self.master, text="")
        self.text_total_downloaded.place(x = 250,y = 510,width=100,height=30)
        
        self.text_current_speed = Label(self.master, text="", justify="right")
        self.text_current_speed.place(x = 450,y = 510,width=150,height=30)
        
    def show(self):
        self.saveText = self.entry_api.get('1.0', END)

class VidList:
    def __init__(self):
        self.is_json_loaded = False
        
    def get_list(self):
        try:
            self.data = json.loads(str(gui.entry_api.get('1.0', END)))
        except:
            messagebox.showinfo('Error','Can not load API page, make sure you copied it correctly')
            return
        gui.entry_api.delete('1.0', END)
        self.total_videos = self.data['total']       
        
        self.pending_delete_count = 0
        self.total_duration = 0
        self.total_size = 0
        self.pending_delete_total_duration = 0
        self.pending_delete_total_size = 0
        
        for video in self.data['videos']:
            if "stale" in video:                
                if(video['stale'] == True):
                    self.pending_delete_count += 1
                    self.pending_delete_total_duration += video['duration']
                    self.pending_delete_total_size += video['size']
            
            self.total_duration += video['duration']
            self.total_size += video['size']        

        gui.entry_total_videos.configure(state='normal')
        gui.entry_total_videos.delete(0,END)
        gui.entry_total_videos.insert(0,self.total_videos)
        gui.entry_total_videos.configure(state='disabled')
        
        gui.entry_total_duration.configure(state='normal')
        gui.entry_total_duration.delete(0,END)
        gui.entry_total_duration.insert(0,str(datetime.timedelta(seconds=round(self.total_duration))))
        gui.entry_total_duration.configure(state='disabled')
        
        gui.entry_total_size.configure(state='normal')
        gui.entry_total_size.delete(0,END)
        gui.entry_total_size.insert(0,sizeof_fmt(self.total_size))
        gui.entry_total_size.configure(state='disabled')
        
        gui.entry_total_pending_delete_videos.configure(state='normal')
        gui.entry_total_pending_delete_videos.delete(0,END)
        gui.entry_total_pending_delete_videos.insert(0,self.pending_delete_count)
        gui.entry_total_pending_delete_videos.configure(state='disabled')
        
        gui.entry_total_pending_delete_duration.configure(state='normal')
        gui.entry_total_pending_delete_duration.delete(0,END)
        gui.entry_total_pending_delete_duration.insert(0,str(datetime.timedelta(seconds=round(self.pending_delete_total_duration))))
        gui.entry_total_pending_delete_duration.configure(state='disabled')
        
        gui.entry_total_pending_delete_size.configure(state='normal')
        gui.entry_total_pending_delete_size.delete(0,END)
        gui.entry_total_pending_delete_size.insert(0,sizeof_fmt(self.pending_delete_total_size))
        gui.entry_total_pending_delete_size.configure(state='disabled')        
                
        self.is_json_loaded = True
        
class DownloadManager:
    def __init__(self):
        self.is_runnning = False
        
    def start_thread(self):
        if(vid_list.is_json_loaded == False):
            messagebox.showinfo('Error','You have to load content from API page first')
            return
    
        self.t = threading.Thread(target=download_manager.start, args=())
        self.t.start()
    
    def start(self):    
        if(self.is_runnning == True):
            self.is_runnning = False
            gui.button_start_download['text'] = 'Start download'
            return
            
        gui.button_start_download['text'] = 'Stop'
    
        self.is_runnning = True
        self.total_downloaded = 0        
        self.finished_downloads = 0
        self.active_downloads_count = 0        
        self.current_speed = 0 
        last_total_downloaded = 0
        downloaded_since_last_measurement = 0        
        self.download_left = vid_list.total_size        
        self.time_left = 0     
        
        if(gui.is_pending_checked.get() == 1):
            total_size = vid_list.pending_delete_total_size
            total_videos = vid_list.pending_delete_count
        else:
            total_size = vid_list.total_size
            total_videos = vid_list.total_videos                  
        
        t0 = time.time()
        i = 0
        self.t = threading.currentThread()
        while(self.is_runnning == True):
            time.sleep(0.1)
            if(self.active_downloads_count < int(gui.spin_threads_count.get())):
                try:
                    if(gui.is_pending_checked.get() == 0 or vid_list.data["videos"][i]["stale"] == True):
                        url = "https:"+vid_list.data["videos"][i]["files"]["mp4"]["url"]
                        name = vid_list.data["videos"][i]["original_name"]
                        self.d = threading.Thread(target=download_manager.get_video, args=(url, name))
                        self.d.start()           
                        i += 1
                    else:
                        i += 1
                except:
                    i += 1
            else:
                pass
            
            time_since_last_speed_measure = time.time() - t0
            if(time_since_last_speed_measure >= 2):
            
                self.download_left = total_size - self.total_downloaded 
                
                downloaded_since_last_measurement = self.total_downloaded - last_total_downloaded
                self.current_speed = downloaded_since_last_measurement/2
                
                if(self.current_speed > 0):
                    self.time_left = self.download_left/self.current_speed
                else:
                    self.time_left = 3600
                
                last_total_downloaded = self.total_downloaded
                t0 = time.time()

            percentage = round(float(self.total_downloaded) / float(total_size) * 100)
            
            gui.text_total_downloaded['text'] = sizeof_fmt(self.total_downloaded)+"/"+sizeof_fmt(total_size)
            gui.text_progress_finished['text'] = str(self.finished_downloads)+"/"+str(total_videos)
            gui.text_current_speed['text'] = sizeof_fmt(self.current_speed)+"/s ("+str(datetime.timedelta(seconds=round(self.time_left)))+")"
            
            gui.progress_bar['value'] = percentage
            
            if(self.finished_downloads >= total_videos):
                messagebox.showinfo('Done','All videos downloaded')
                gui.button_start_download['text'] = 'Start download'                
                return            
        
    def get_video(self, link, file_name):        
        self.active_downloads_count += 1
        self.d = threading.currentThread()
        download_path = os.path.join(gui.folder_path, file_name)
        with open(download_path, "wb") as f:
                response = requests.get(link, stream=True)
                total_length = response.headers.get('content-length')

                if total_length is None: # no content length header
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=4096):
                        if(self.is_runnning == False):
                            return
                    
                        dl += len(data)
                        self.total_downloaded += len(data)
                        f.write(data)                   
        self.finished_downloads += 1
        self.active_downloads_count -= 1
        
download_manager = DownloadManager()
vid_list = VidList()
window = Tk()
gui = GUI(window)
window.mainloop()    