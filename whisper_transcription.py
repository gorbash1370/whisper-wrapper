#%%
import os
import re
import time
from datetime import datetime as dt
import whisper

from main import path_to_audio, path_for_transcripts, audio_format, word_interval, model_chosen, model_options 

""" gorbash1370 Intro 
This script automates the process of transcribing audio files using a local Whisper model from OpenAI. It includes functionality for handling multiple files, adding custom headers to the transcripts, and logging the transcription process.

It requires:
filenames should contain title of podcast or audio track
all files with the specified extension in the input_path directory will be attempted to be procesed.

!! TO DO: Extract series and episode number from filename
It can be further automated if the filename contains information (series and episode number) in a standardised way.

Last code update 24 01 24
"""
#%%
def load_model(): # is there a time delay here? to warn about?
    model = whisper.load_model(model_chosen) 

rundate = ""

#%%
########################## Pre-Processing #########################
def setup_log_file():
    """Instanciates a datestamped .txt log file so activity in a single day is aggregated."""
    run_date = dt.now().strftime("%Y-%m-%d")
    logfilename = f"log_whisper_transcripts_{run_date}.txt"
    if not os.path.exists(logfilename):
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        try:
            with open(logfilename, "a") as log_file:
                log_file.write(f"{formatted_timestamp} - Log File Setup - Successful.\n")
                # pre_processing(logfilename) # return True?
        except (FileExistsError, OSError, UnicodeEncodeError) as e:
            error = f"Error, unable to instantiate log file with name {logfilename}. The following error occurred: {e}\n"
            print(error)
            return False # return error?
    else:
        return logfilename

def pre_processing(
        path_to_audio, path_for_transcripts, logfilename, audio_format, word_interval, model_options, model_chosen):
    
    formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Check if the user supplied directory path exists
    if not os.path.exists(path_to_audio):
        error_msg = "Error, specified directory does not exist.\n"
        with open(logfilename, "a") as log_file:
            log_file.write(f"{formatted_timestamp} - {error_msg}")
            print(error_msg)
            return False # return error?
    else: 
        success_msg = f"Pre Processing Checks - Input directory check successful.\n"
        with open(logfilename, "a") as log_file:
            log_file.write(f"{formatted_timestamp} - {success_msg}")
        print(success_msg)
    
    # Create the output directory path for transcripts if doesn't exist
    if not os.path.exists(path_for_transcripts):
        os.makedirs(path_for_transcripts)
        success_msg = f"Pre Processing Checks - Output directory creation successful.\n"
        with open(logfilename, "a") as log_file:
            log_file.write(f"{formatted_timestamp} - {success_msg}")
        print(success_msg)

    try:
        # Obtain list of filenames, filtered by mp3, and being file vs directory
        mp3_filenames = [f for f in os.listdir(path_to_audio) if f.endswith(audio_format) and os.path.isfile(os.path.join(path_to_audio, f))]
        file_count = len(mp3_filenames)
        
        summary_files = f"Directory contains {file_count} {audio_format} files: '\n'.join(mp3_filenames) + '\n'."
        print(summary_files)

        with open(logfilename, "a") as log_file:
            log_file.write(summary_files) # NB: concats list of strings with \n. The +\n ensures full write ends with a newline

        # Use list of filenames to check if directory contains at least one file of type specified
        if not mp3_filenames: # NB: an empty list is falsey
            error_msg = f"Error, no files of type {audio_format} found in {path_to_audio}.\n"
            with open(logfilename, "a") as log_file:
                log_file.write(f"{formatted_timestamp} - {error_msg}")
                return False # return error?     
        else:
            success_msg = "Pre Processing Checks - File type check successful.\n"
            with open(logfilename, "a") as log_file:
                log_file.write(f"{formatted_timestamp} - {success_msg}")
            
    except (FileNotFoundError, PermissionError, OSError) as e: # need to specify errors
        error_msg = f"Error, pre-processing audio filenames. The following error occurred: {e}\n "
        return False

    # Check if word interval entered is a positive integer
    try:
        word_interval = abs(int(word_interval))
    except ValueError:
        error_msg = "Error, word interval must be a positive integer. Substituting 10 as word interval instead.\n"
        print(error_msg)
        word_interval = 10
       
    if model_chosen not in model_options:
        error_msg += "Error, invalid model chosen. Please reselect.\n"
        print(error_msg)
        with open(logfilename, "a") as log_file:
            log_file.write(f"{formatted_timestamp} - {error_msg}")
        return False # want the script to exit here, correct model must be actively chosen 

    # Need to check that this will ONLY run if all the prior conditions are successful - do i need to set a flag that exits the program if any false is returned?
    with open(logfilename, "a") as log_file:
            summary = f"{formatted_timestamp} - Summary of transcription parameters - Input Path: {path_to_audio} - Output Path: {path_for_transcripts} - Audio format: {audio_format} - Number of {audio_format} files: {file_count} - Transcription Model: {model_chosen} - Newline interval: {word_interval} words.\n"
            log_file.write(summary)

    print(f"Please make sure you are happy with this summary of processing:\n{summary}\n Abort if any parameters are incorrect. A large batch of files and-or a using the largest models will take significant time and compute.")
    time.sleep(5)


# Whisper transcripts are one long line of text. This function will insert a newline character at the end of every {interval} i.e. 10 words. If 0 was chosen, no newlines will be inserted 
def insert_newlines(text, word_interval):
    if word_interval == 0:
        return text # Returns original text without any newlines
    
    words = text.split() # NB: list of individual words
    for i in range(word_interval -1, len(words), word_interval): 
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
    # "speakers" : [
    #     {"name": "Daniel Barnett", "role": "Host"} # Host, Speaker, Interviewer
        # {"name": "Unknown", "role": "Interviewer"},
    #    ]
    },
    {
    # "audio_file_num" : index, 
    # "audio_title": filename,
    "date" : "Unknown",
    "series_num" : "S6",
    "episode_num" : "E10",
    # "speakers" : [
    #     {"name": "Daniel Barnett", "role": "Host"} # Host, Speaker, Interviewer
    #     # {"name": "Unknown", "role": "Interviewer"},
    #    ]
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
        path = os.path.join(path_to_audio, audio_file)
        result = model.transcribe(path)
        raw_transcript = result["text"]

        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_transcription_success = (f"{formatted_timestamp} - Whisper transcription successful.")
        print(msg_transcription_success)

    except (FileNotFoundError, RuntimeError, Exception) as e: # CalledProcessError
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_transciption_error = (f"{formatted_timestamp} - Whisper transcription error - {e}")
        with open(logfilename, "a") as log_file:
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
        os.makedirs(path_for_transcripts, exist_ok=True)
   
        full_path = os.path.join(opath_for_transcripts, output_filename)

        # Now open the file for writing
        with open(full_path, "w") as output_file:
            output_file.write(formatted_transcript)
        
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_transcript_write_success = f"{formatted_timestamp} - Successfully transcribed {audio_file}"
        print(msg_transcript_write_success)
        
    except (FileNotFoundError, PermissionError, OSError, Exception) as e:
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_output_file_write_error = (f"{formatted_timestamp} - Whisper transcription error - {e}")
        with open(logfilename, "a") as log_file:
            log_file.write({formatted_timestamp}+" - "+{msg_output_file_write_error})

    with open(logfilename, "a") as log_file:
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
# Suggested rework of pre_processing()

def pre_processing(path_to_audio, path_for_transcripts, logfilename, audio_format, word_interval, model_chosen, model_options):
    formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
    error_msg = ""

    # Check if the user supplied directory path exists
    if not os.path.exists(path_to_audio):
        error_msg = f"{formatted_timestamp} - Error, specified directory does not exist.\n"
    else:
        # Create the output directory path for transcripts if doesn't exist
        if not os.path.exists(path_for_transcripts):
            os.makedirs(path_for_transcripts)

        # Check for the presence of audio files
        try:
            mp3_filenames = [f for f in os.listdir(path_to_audio) if f.endswith(audio_format) and os.path.isfile(os.path.join(path_to_audio, f))]
            if not mp3_filenames:
                error_msg = f"{formatted_timestamp} - Error, no files of type {audio_format} found in {path_to_audio}.\n"
        except FileNotFoundError:
            error_msg = f"{formatted_timestamp} - Error, directory not found: {path_to_audio}\n"
        except PermissionError:
            error_msg = f"{formatted_timestamp} - Error, permission denied for directory: {path_to_audio}\n"
        except OSError as e:  # General catch-all for other OS-related errors
            error_msg = f"{formatted_timestamp} - OS error occurred: {e}\n"

    # Check if word interval entered is a positive integer
    try:
        word_interval = abs(int(word_interval))
    except ValueError:
        word_interval = 10  # Default value

    # Check if the chosen model is valid
    if model_chosen not in model_options:
        error_msg += f"{formatted_timestamp} - Error, invalid model chosen. Please reselect.\n"

    if error_msg:
        with open(logfilename, "a") as log_file:
            log_file.write(error_msg)
        print(error_msg)
        return False

    # If everything is fine, proceed
    with open(logfilename, "a") as log_file:
        summary = f"{formatted_timestamp} - Summary of transcription parameters - Input Path: {path_to_audio} - Output Path: {path_for_transcripts} - Audio format: {audio_format} - Newline interval: {word_interval} words - Transcription Model: {model_chosen}\n"
        log_file.write(summary)

    print(f"Please make sure you are happy with this summary of processing:\n{summary}\nAbort if any parameters are incorrect. A large batch of files and/or using the largest models will take significant time and compute.")
    time.sleep(5)
    return True

# Example usage
# pre_processing(path_to_audio, path_for_transcripts, logfilename, audio_format, word_interval, model_chosen, model_options)

# Alternative filename processing errror
try:
    mp3_filenames = [f for f in os.listdir(path_to_audio) if f.endswith(audio_format) and os.path.isfile(os.path.join(path_to_audio, f))]
    if not mp3_filenames:
        error_msg = f"{formatted_timestamp} - Error, no files of type {audio_format} found in {path_to_audio}.\n"
except FileNotFoundError:
    error_msg = f"{formatted_timestamp} - Error, directory not found: {path_to_audio}\n"
except PermissionError:
    error_msg = f"{formatted_timestamp} - Error, permission denied for directory: {path_to_audio}\n"
except OSError as e:  # General catch-all for other OS-related errors
    error_msg = f"{formatted_timestamp} - OS error occurred: {e}\n"
