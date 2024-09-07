import os
import time
import threading
from gtts import gTTS
from pydub import AudioSegment
from tqdm import tqdm
from moviepy.editor import VideoFileClip
import wx

class MP3SplitApp(wx.Frame):
    def __init__(self, parent, title):
        super(MP3SplitApp, self).__init__(parent, title=title, size=(600, 400))

        self.panel = wx.Panel(self)
        self.input_folder = "./input"
        self.output_folder = "./output"
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(10000)  # Refresh every 10 seconds

        self.init_ui()
        self.Centre()
        self.Show()

    def init_ui(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.mp3_listbox = wx.ListBox(self.panel, style=wx.LB_MULTIPLE)
        vbox.Add(wx.StaticText(self.panel, label="Available MP3 files:"), flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(self.mp3_listbox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        self.mp4_listbox = wx.ListBox(self.panel, style=wx.LB_MULTIPLE)
        vbox.Add(wx.StaticText(self.panel, label="Available MP4 files:"), flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(self.mp4_listbox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        self.convert_button = wx.Button(self.panel, label="Convert MP4 to MP3")
        self.convert_button.Bind(wx.EVT_BUTTON, self.on_convert)
        vbox.Add(self.convert_button, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.split_button = wx.Button(self.panel, label="Split Selected MP3")
        self.split_button.Bind(wx.EVT_BUTTON, self.on_split)
        vbox.Add(self.split_button, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.StaticText(self.panel, label="Start Split Number:"), flag=wx.RIGHT, border=8)
        self.start_number_ctrl = wx.SpinCtrl(self.panel, value="1", min=1)
        hbox.Add(self.start_number_ctrl, flag=wx.EXPAND)
        vbox.Add(hbox, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.progress_bar = wx.Gauge(self.panel, range=100, size=(250, 25))
        vbox.Add(self.progress_bar, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.panel.SetSizer(vbox)
        self.refresh_file_lists()

    def on_timer(self, event):
        self.refresh_file_lists()

    def refresh_file_lists(self):
        selected_mp3 = self.mp3_listbox.GetSelections()
        selected_mp4 = self.mp4_listbox.GetSelections()

        self.mp3_files = [f for f in os.listdir(self.output_folder) if f.endswith('.mp3')]
        self.mp4_files = [f for f in os.listdir(self.input_folder) if f.endswith('.mp4')]

        self.mp3_listbox.Set(self.mp3_files)
        self.mp4_listbox.Set(self.mp4_files)

        for index in selected_mp3:
            if index < len(self.mp3_files):
                self.mp3_listbox.SetSelection(index)
        for index in selected_mp4:
            if index < len(self.mp4_files):
                self.mp4_listbox.SetSelection(index)

    def on_convert(self, event):
        self.refresh_file_lists()
        self.convert_button.Disable()
        threading.Thread(target=self.convert_mp4_to_mp3).start()

    def convert_mp4_to_mp3(self):
        selected_files = [self.mp4_listbox.GetString(i) for i in self.mp4_listbox.GetSelections()]
        if not selected_files:
            wx.CallAfter(wx.MessageBox, "No MP4 file selected.", "Error", wx.OK | wx.ICON_ERROR)
            wx.CallAfter(self.convert_button.Enable)
            return

        for selected_file in selected_files:
            input_path = os.path.join(self.input_folder, selected_file)
            output_path = os.path.join(self.output_folder, os.path.splitext(selected_file)[0] + ".mp3")

            video = VideoFileClip(input_path)
            audio = video.audio

            audio.write_audiofile(output_path, codec='mp3')

        wx.CallAfter(self.refresh_file_lists)
        wx.CallAfter(self.on_task_complete, self.convert_button, "Conversion complete.")

    def on_split(self, event):
        self.refresh_file_lists()
        self.split_button.Disable()
        threading.Thread(target=self.split_mp3).start()

    def split_mp3(self):
        selected_files = [self.mp3_listbox.GetString(i) for i in self.mp3_listbox.GetSelections()]
        if not selected_files:
            wx.CallAfter(wx.MessageBox, "No MP3 file selected.", "Error", wx.OK | wx.ICON_ERROR)
            wx.CallAfter(self.split_button.Enable)
            return

        start_number = self.start_number_ctrl.GetValue()
        current_number = start_number

        for selected_file in selected_files:
            input_path = os.path.join(self.output_folder, selected_file)
            audio = AudioSegment.from_mp3(input_path)

            # Set chunk length to 30 minutes (30 * 60 * 1000 ms)
            chunk_length_ms = 30 * 60 * 1000
            total_duration_ms = len(audio)

            if total_duration_ms <= chunk_length_ms:
                wx.CallAfter(wx.MessageBox, f"The file {selected_file} is shorter than 30 minutes. No splitting necessary.", "Info", wx.OK | wx.ICON_INFORMATION)
                continue

            chunks = [audio[i:i + chunk_length_ms] for i in range(0, total_duration_ms, chunk_length_ms)]
            total_chunks = len(chunks)
            step = 100 / total_chunks

            for i, chunk in enumerate(chunks):
                chunk_name = f"{current_number}_{os.path.splitext(selected_file)[0]}_part{i + 1}.mp3"

                # Add spoken numbers to the beginning of each chunk
                number_audio = gTTS(text=str(current_number), lang='en')
                temp_number_path = os.path.join(self.output_folder, "temp_number.mp3")
                number_audio.save(temp_number_path)
                number_audio_segment = AudioSegment.from_mp3(temp_number_path)
                final_chunk = number_audio_segment + chunk
                final_chunk.export(os.path.join(self.output_folder, chunk_name), format="mp3")

                wx.CallAfter(self.update_progress, int(step * (i + 1)))
                current_number += 1

            os.remove(temp_number_path)  # Clean up the temporary file

        wx.CallAfter(self.refresh_file_lists)
        wx.CallAfter(self.on_task_complete, self.split_button, "Splitting complete.")

    def update_progress(self, value):
        self.progress_bar.SetValue(int(value))

    def on_task_complete(self, button, message):
        button.Enable()
        self.progress_bar.SetValue(0)
        wx.MessageBox(message, "Info", wx.OK | wx.ICON_INFORMATION)

if __name__ == '__main__':
    app = wx.App(False)
    frame = MP3SplitApp(None, "MP3 Splitter")
    app.MainLoop()