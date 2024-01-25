#%%
import os
import whisper
from datetime import datetime as dt

""" gorbash1370 Intro 
This script is designed to automate the process of transcribing audio files using a local Whisper model from OpenAI. It includes functionality for handling multiple files, adding custom headers to the transcripts, and logging the transcription process.

It requires:
currently assumes mp3
filenames should contain title of podcast or audio track
all files with the specified extension in the input_path directory will be attempted to be procesed.

!! TO DO: Extract series and episode number from filename
It can be further automated if the filename contains information (series and episode number) in a standardised way.

Last code update 24 01 24
"""
#%%
############# MANUAL SECTION 1 ####################

# NB: Specify full absolute input_path if not runnings script in directory containing audio files to transcribe

# Specify directory path containing audio files. Can be absolute if required
input_path = "batch/" 

# Specify transcript output folder / path, will be created if doesn't exist
output_path = "transcripts/"
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Specify target audio file format 
audio_format = ".mp3"

# Choose transcription model (see table at end for time and RAM requirements)
# Whisper Model Summary:
# - tiny.en: Requires ~1 GB VRAM, Speed ~32x.
# - base.en: Requires ~1 GB VRAM, Speed ~16x.
# - small.en: Requires ~2 GB VRAM, Speed ~6x.
# - medium.en: Requires ~5 GB VRAM, Speed ~2x.
# - large (Multilingual): Requires ~10 GB VRAM, Speed 1x.

model_options = ["tiny.en", "base.en", "small.en", "medium.en", "large", "tiny", "base", "small", "medium"] # non .en are multilingual. en's best for English

model_chosen = model_options[2]

model = whisper.load_model(model_chosen) 

# Specify the interval of words at which to insert a newline in transcript
word_interval = 10  # for example, every 10 words

run_date = dt.now().strftime("%Y-%m-%d")


#%%
########################## Pre-Processing #########################

##### Log file set-up
formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
with open(f"log_whisper_transcripts_{run_date}.txt", "a") as log_file:
    log_file.write(f"{formatted_timestamp} - Input Path: {input_path} - Output Path: {output_path} - Audio format: {audio_format} - Transcription Model: {model_chosen} - Newline interval: {word_interval} words.\n")

# Obtain list of filenames, filtered by mp3, and being file vs directory
mp3_filenames = [f for f in os.listdir(input_path) if f.endswith(audio_format) and os.path.isfile(os.path.join(input_path, f))]

print(mp3_filenames)
with open(f"log_whisper_transcripts_{run_date}.txt", "a") as log_file:
    log_file.write("\n".join(mp3_filenames) + "\n") # concats list of strings with a \n, and the +\n ensures full write ends on a newline

# Whisper transcripts are one long line of text. This function will insert a newline character at the end of every {interval} i.e. 10 words 
def insert_newlines(text, word_interval):
    words = text.split() # list of individual words
    for i in range(word_interval, len(words), word_interval): 
        words[i] = words[i] + '\n'
    return ' '.join(words)


#%%
############# MANUAL SECTION 2 : POPULATE TRANSCRIPT HEADER ####################

# Populate 'group' string fields for the transcript file 'header' (so these are the same for all the videos)
audio_info_batch = [
    {
        "participants" : [
        {"name": "Daniel Barnett", "role": "Host & Speaker"},
        # {""name": "Unknown", "role": "Interviewer"},
        ]
    },
    {
        "video_content" : [
        {"type" : "QandA"}, # talk, interview, QandA
        {"topic" : "UK Employment Law"},
        {"series" : "Employment Law Matters"},
        {"format" : "Podcast"}
        ] # Podcast, YouTube
    },
    {
        "transcript_type" : [
        {"producer" : "whisper"},
        {"model" : model_chosen}
        ]
    },
]

# Populate information which varies per audio file
audio_file_info = [
    {
    # "audio_file_num" : index, 
    # "audio_title": filename,
    "date" : "Unknown",
    "series_num" : "S6",
    "episode_num" : "E7",
    "speakers" : [
        {"name": "Daniel Barnett", "role": "Host"} # Host, Speaker, Interviewer
        # {"name": "Unknown", "role": "Interviewer"},
        ]
    },
    {
    # "audio_file_num" : index, 
    # "audio_title": filename,
    "date" : "Unknown",
    "series_num" : "S6",
    "episode_num" : "E10",
    "speakers" : [
        {"name": "Daniel Barnett", "role": "Host"} # Host, Speaker, Interviewer
        # {"name": "Unknown", "role": "Interviewer"},
        ]
    }
]

#%%
########################## TRANSCRIPTION ################################

# Need to put a try except block in with error / success messages to log file

for index, audio_file in enumerate(mp3_filenames, start=1):
    try:
        # construct individualised header for each file
        header_parts = [
        f"Filename: {audio_file}",
        f"Content creation date: {audio_file_info[index-1]['date']}",
        f"Series: {audio_info_batch[1]['video_content'][2]['series']}",
        f"Series num: {audio_file_info[index-1]['series_num']}",
        f"Episode num: {audio_file_info[index-1]['episode_num']}",
        f"Format: {audio_info_batch[1]['video_content'][3]['format']}", 
        f"Topic: {audio_info_batch[1]['video_content'][1]['topic']}",
        f"Type: {audio_info_batch[1]['video_content'][0]['type']}",
        f"Participants: {audio_info_batch[0]['participants']}",
        f"Transcription Producer: {audio_info_batch[2]['transcript_type'][0]['producer']}",
        f"Transcription Model: {audio_info_batch[2]['transcript_type'][1]['model']}",
        f"Series Batch process order: {index}"
        ]
        header = "\n".join(header_parts) + "\n\n"
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_header_success = (f"{formatted_timestamp} - Header construction successful.")
        print(msg_header_success)

    except (TypeError, KeyError, IndexError, ValueError, Exception) as e:
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_header_error = (f"{formatted_timestamp} - Header construction error - {e}")
    
    # whisper.ai transcription
    try:
        path = os.path.join(input_path, audio_file)
        result = model.transcribe(path)
        raw_transcript = result["text"]

        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_transcription_success = (f"{formatted_timestamp} - Whisper transcription successful.")
        print(msg_transcription_success)

    except (FileNotFoundError, RuntimeError, Exception) as e: # CalledProcessError
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_transciption_error = (f"{formatted_timestamp} - Whisper transcription error - {e}")
        with open(f"log_whisper_transcripts_{run_date}.txt", "a") as log_file:
            log_file.write({formatted_timestamp}+" - "+{msg_transciption_error})

    # insert newlines every word_interval
    linebreak_transcript = insert_newlines(raw_transcript, word_interval)

    # combine header and transcript
    formatted_transcript = header + "\n" + linebreak_transcript 

    # insert line numbers
    lines = formatted_transcript.splitlines()
    formatted_transcript = "\n".join(f"{i+1}: {line}" for i, line in enumerate(lines))

    # write the combined header + transcript + line numbers to file
    try:
        output_filename = f"{os.path.splitext(audio_file)[0]}_(transcript).txt"
        # NB: splitext required so that ".mp3" isn't put in filename
   
        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)
   
        full_path = os.path.join(output_path, output_filename)

        # Now open the file for writing
        with open(full_path, "w") as output_file:
            output_file.write(formatted_transcript)
        
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_transcript_write_success = f"{formatted_timestamp} - Successfully transcribed {audio_file}"
        print(msg_transcript_write_success)
        
    except (FileNotFoundError, PermissionError, OSError, Exception) as e:
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_output_file_write_error = (f"{formatted_timestamp} - Whisper transcription error - {e}")
        with open(f"log_whisper_transcripts_{run_date}.txt", "a") as log_file:
            log_file.write({formatted_timestamp}+" - "+{msg_output_file_write_error})

    with open(f"log_whisper_transcripts_{run_date}.txt", "a") as log_file:
        log_file.write(f"{msg_header_success}\n{msg_transcription_success}\n{msg_transcription_success}\n\n")
                       


#%%
#         try:
#     # Your code to write file
# except FileNotFoundError:
#     print("The specified directory does not exist and could not be created.")
# except PermissionError:
#     print("You do not have permission to write to the specified directory.")
# except OSError as e:
#     print(f"OS error occurred: {e}")
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")



#%%
"""# Create a list comprehension to filter and list files
mp3_filenames = [
    f  # Take each file name 'f'
    for f in os.listdir(input_path)  # Iterate over each file and directory name in the specified path
    if f.endswith('.mp3')  # Check if the file name ends with '.mp3' (to filter only MP3 files)
    and os.path.isfile(os.path.join(input_path, f))  # Check if the path represents a file (not a directory)
    # os.path.join(input_path, f) constructs the full path for each file.
    # This is necessary because os.listdir returns only file or directory names, not their full paths.
]# mp3_files now contains a list of all .mp3 files in the specified directory"""



# %%

# |  Size  | Parameters | English-only model | Multilingual model | Required VRAM | Relative speed |
# |:------:|:----------:|:------------------:|:------------------:|:-------------:|:--------------:|
# |  tiny  |    39 M    |     `tiny.en`      |       `tiny`       |     ~1 GB     |      ~32x      |
# |  base  |    74 M    |     `base.en`      |       `base`       |     ~1 GB     |      ~16x      |
# | small  |   244 M    |     `small.en`     |      `small`       |     ~2 GB     |      ~6x       |
# | medium |   769 M    |    `medium.en`     |      `medium`      |     ~5 GB     |      ~2x       |
# | large  |   1550 M   |        N/A         |      `large`       |    ~10 GB     |       1x       |
