import soundfile as sf
import os
from gtts import gTTS
from pydub import AudioSegment
from tqdm import tqdm
from moviepy.editor import VideoFileClip

# List all .mp3 and .mp4 files in the ./input directory
input_folder = "./input"
mp3_files = [f for f in os.listdir(input_folder) if f.endswith('.mp3')]
mp4_files = [f for f in os.listdir(input_folder) if f.endswith('.mp4')]

# Display the list of MP3 files to the user
print("Available MP3 files:")
for idx, file in enumerate(mp3_files, start=1):
    print(f"{idx}. {file}")

# Check if there are any MP4 files in the input folder
if mp4_files:
    print("Available MP4 files:")
    for idx, file in enumerate(mp4_files, start=1):
        print(f"{idx}. {file}")

    # Ask the user if they want to convert any MP4 files
    convert_mp4 = input("Would you like to convert any MP4 files to MP3? (y/n): ").strip().lower()

    if convert_mp4 == 'y':
        mp4_choice = int(input("Enter the number of the MP4 file you want to convert: ")) - 1

        # Check if the chosen file index is valid
        if mp4_choice < 0 or mp4_choice >= len(mp4_files):
            print("Invalid file choice.")
            exit(1)

        chosen_mp4 = mp4_files[mp4_choice]
        mp4_path = os.path.join(input_folder, chosen_mp4)
        mp3_output_path = os.path.join(input_folder, os.path.splitext(chosen_mp4)[0] + '.mp3')

        # Convert MP4 to MP3
        print(f"Converting {chosen_mp4} to MP3...")
        video = VideoFileClip(mp4_path)
        video.audio.write_audiofile(mp3_output_path)
        print(f"Conversion completed. {mp3_output_path} saved.")

        # Add the newly converted MP3 file to the list
        mp3_files.append(os.path.basename(mp3_output_path))

# Check if there are any MP3 files in the input folder
if not mp3_files:
    print("No MP3 files found in the input folder.")
    exit(1)

# Display the list of MP3 files to the user again if any new files were added
print("Available MP3 files:")
for idx, file in enumerate(mp3_files, start=1):
    print(f"{idx}. {file}")

# Ask the user to choose a file
file_choice = int(input("Enter the number of the file you want to use: ")) - 1

# Check if the chosen file index is valid
if file_choice < 0 or file_choice >= len(mp3_files):
    print("Invalid file choice.")
    exit(1)

chosen_file = mp3_files[file_choice]

# Load the chosen MP3 file
audio, sr = sf.read(os.path.join(input_folder, chosen_file))

# Define the length of each split in samples for 30 minutes at 44.1kHz sample rate
split_length = 44100 * 1800

# Split the file into chunks of `split_length` samples
chunks = [audio[i:i+split_length] for i in range(0, len(audio), split_length)]

# Ensure the first chunk is larger than the second, second is larger than third, and so on
for i in range(len(chunks) - 1):
    if len(chunks[i]) <= len(chunks[i + 1]):
        # Reduce the length of the next chunk to ensure ordering
        chunks[i + 1] = chunks[i + 1][:len(chunks[i]) - 1]

# Save each chunk as a separate MP3 file in the ./output folder
output_folder = "./output"
os.makedirs(output_folder, exist_ok=True)
print("Saving chunks with progress bar:")
for i, chunk in enumerate(tqdm(chunks, desc="Splitting"), start=1):
    filename = os.path.join(output_folder, f"{i:02d}_{chosen_file}")
    sf.write(filename, chunk, sr, format="mp3")

print(f"Splitting completed. Chunks saved in {output_folder}")

# Define the input folder and get a list of MP3 files in it
file_names = sorted([f for f in os.listdir(output_folder) if f.endswith('.mp3')])

# Ask the user if they want to start from 1
while True:
    start_from_one = input("Would you like to start from 1? (y/n): ").strip().lower()
    if start_from_one in ['y', 'n']:
        break
    else:
        print("Invalid input. Please enter 'y' or 'n'.")

if start_from_one == 'y':
    start_number = 1
else:
    start_number = int(input("Enter the number to start from: ").strip())

# Debug print to check the start number
print(f"Starting from number: {start_number}")

# Define an empty list to store the audio chunks
chunks = []

# Load each file and append its audio data to the chunks list
for file_name in file_names:
    file_path = os.path.join(output_folder, file_name)
    chunk = AudioSegment.from_file(file_path, format='mp3')
    chunks.append(chunk)

# Concatenate the chunks with spoken numbers
print("Concatenating chunks with progress bar:")
for i, chunk in enumerate(tqdm(chunks, desc="Concatenating"), start=start_number):
    # Generate spoken number audio
    spoken_number = gTTS(str(i), lang='en')
    spoken_number.save('spoken_number.mp3')

    # Load spoken number and original chunk audio
    spoken_number_audio = AudioSegment.from_mp3('spoken_number.mp3')
    chunk_audio = chunk

    # Concatenate audio files
    final_audio = spoken_number_audio + chunk_audio

    # Handle existing files by renaming if necessary
    output_file = os.path.join(output_folder, f"{i:02d}_{chosen_file}")
    base, ext = os.path.splitext(output_file)
    counter = 1
    while os.path.exists(output_file):
        output_file = f"{base}_{counter}{ext}"
        counter += 1

    # Save concatenated audio to file with chosen file name
    final_audio.export(output_file, format='mp3')

print(f"Concatenation completed. Files saved in {output_folder}")

# Clean up temporary files
for file_name in file_names:
    os.remove(os.path.join(output_folder, file_name))
os.remove('spoken_number.mp3')

print(f"Temporary files removed from {output_folder}")