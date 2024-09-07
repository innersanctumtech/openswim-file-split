# MP3 Splitter and Converter

This project contains two scripts for splitting and converting audio files:
1. mp3-split.py (Command-line version)
2. GUI-mp3-split.py (Graphical User Interface version)

## Requirements

To run these scripts, you need:

- Python 3.x
- Libraries: 
  - soundfile
  - gtts
  - pydub
  - tqdm
  - moviepy
  - wxPython (for GUI version only)

Install the required libraries using:

```
pip install soundfile gtts pydub tqdm moviepy wxPython
```

## What it does

These scripts allow you to:
- Convert MP4 files to MP3
- Split large MP3 files into smaller chunks (30 min chunks)
- Add spoken numbers at the beginning of each audio chunk

## Types of conversions

- MP4 to MP3 conversion
- Large MP3 files to multiple smaller MP3 files

## How to run

1. Place your input files in the './input' folder.
2. Run the script:
   - For command-line version: `python mp3-split.py`
   - For GUI version: `python GUI-mp3-split.py`

## How to operate

### Command-line version (mp3-split.py):
1. Follow the prompts to select files and options.
2. The script will process the files and save the output in the './output' folder.

### GUI version (GUI-mp3-split.py):
1. Launch the application.
2. Select MP4 files to convert or MP3 files to split.
3. Set the starting number for split files if needed.*
4. Click "Convert MP4 to MP3" or "Split Selected MP3" as required.
5. The processed files will be saved in the './output' folder.

Both versions will automatically add spoken numbers to the beginning of each split audio file.


* example, see screenshot3.jpg
Lets say you have performed the split for video1.mp3 file but did not do for video2. However, you want to use both file, video1 and video2 in the same folder after split. You also want to keep them in order. Since video1 has produced 3 files. You will need to select on the 'Start Split Number:', the number 4. So the files can be properly named from #4 on... as well as added the correct initial spoken number to the split file.


Note: the main reason I created this for my openswim headphone, is due to the fact that it reads files in shuffle mode (not sure if it is supposed to be that way). I tried renaming the files simply but it did not work for me. So while I am swimming, I at least know which file it just jumped to if I am listening to a podcast or a book. I also sometimes swim 15 mins, 30 mins or 45 mins. Which I will add to the script an ability to be able to change that later.