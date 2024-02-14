#%%
import os
import time
from datetime import datetime as dt
import whisper
import sys

# get_ipython().run_line_magic('load_ext', 'autoreload')
# get_ipython().run_line_magic('autoreload', '2')


from user_variables import log_file_compulsory, path_to_audio, path_for_transcripts, word_interval, audio_format, model_options, audio_info_batch, delimiter

from utils_helper import sanitize_filename, extract_series_episode,log_file_write

""" gorbash1370 Intro 
This script automates the process of transcribing audio files using a local Whisper model from OpenAI. It includes functionality for handling multiple files, adding custom headers to the transcripts, and logging the transcription process.

Notes:
* filenames should contain title of podcast or audio track
* Script attempts to process ALL files with the specified extension in the input path directory: it does NOT enumerate or process files in subfolders

Last code update 24 01 26
"""

logfilename = "" # Instanciates global variable
audio_filenames = []

#%%
########################## PRE-PROCESSING #########################
def log_file_setup():
    """Instanciates a datestamped .txt log file so activity in a single day is aggregated."""
    global logfilename 
    run_date = dt.now().strftime("%Y-%m-%d")
    logfilename = f"log_whisper_transcripts_{run_date}.txt"
    
    try:
        if not os.path.exists(logfilename):
            msg_success = ("Log File Setup - Successful.\n")
            print(msg_success)
            log_file_write(msg_success, logfilename)
            return True
        if os.path.exists(logfilename):
            return True
        
    except (OSError, UnicodeEncodeError) as e:
            formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
            msg_error = f"{formatted_timestamp} - Error, unable to instantiate log file with name {logfilename}. The following error occurred: {e}\n"
            print(msg_error)
            return False 

#%%
def pre_processing(
        path_to_audio, path_for_transcripts, audio_format, word_interval, model_options, model_chosen):
    """Checks if the input directory exists, if the output directory exists, if the audio format is present, and if the word interval is a positive integer. If all checks pass, returns a list of filenames and the model chosen. If any check fails, returns False."""

    formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Check if the user supplied directory path exists
    if not os.path.exists(path_to_audio):
        error_msg = "Error, specified directory does not exist. Please supply a valid directory name or path containing audio files to process.\n"
        
        with open(logfilename, "a") as log_file:
            log_file.write(f"{formatted_timestamp} - {error_msg}")
            print(error_msg)
            return False 
    else: 
        success_msg = f"Pre Processing Checks - Input directory check successful.\n\n"
        with open(logfilename, "a") as log_file:
            log_file.write(f"{formatted_timestamp} - {success_msg}")
        print(success_msg)
    
    # Create the output directory for transcripts if doesn't exist
    try: 
        if not os.path.exists(path_for_transcripts):
            os.makedirs(path_for_transcripts)
            success_msg = f"Pre Processing Checks - Output directory creation successful.\n"
            with open(logfilename, "a") as log_file:
                log_file.write(f"{formatted_timestamp} - {success_msg}")
            print(success_msg)
    except (PermissionError, FileNotFoundError, OSError) as e:
        error_msg = f"Error, unable to create output directory. The following error occurred: {e}\n"
        with open(logfilename, "a") as log_file:
            log_file.write(f"{formatted_timestamp} - {error_msg}")
        return False
    
    try:
        # Obtain list of filenames, filtered by specified filetype(s), and being file vs directory
        audio_file_names = [f for f in os.listdir(path_to_audio) if f.endswith(audio_format) and os.path.isfile(os.path.join(path_to_audio, f))]
        file_count = len(audio_file_names)
        
        pretty_audio_filenames = '\n'.join(audio_file_names)
        summary_files = f"Directory contains {file_count} {audio_format} files:\n{pretty_audio_filenames}\n"
        print(summary_files)
            
        with open(logfilename, "a") as log_file:
            log_file.write(summary_files) # NB: concats list of strings with \n. The +\n ensures full write ends with a newline

        # Use list of filenames to check if directory contains at least one file of type specified
        if not audio_file_names: # NB: an empty list is falsey
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

    # Check if word interval entered is a positive integer or 0
    try:
        word_interval = abs(int(word_interval))
    except ValueError:
        error_msg = "Error, word interval must be a positive integer or 0. Substituting 10 as newline word interval instead.\n"
        print(error_msg)
        with open(logfilename, "a") as log_file:
            log_file.write(f"{formatted_timestamp} - {error_msg}")
        word_interval = 10 # the program will continue using subsituted value, even if invalid word interval (i.e. -4 or "four" entered)

    # Check if model chosen is a valid selection
    model_names = [model["name"] for model in model_options.values()]
    if model_chosen not in model_names:
        error_msg = "Error, invalid model chosen. Please reselect.\n"
        print(error_msg)
        with open(logfilename, "a") as log_file:
            log_file.write(f"{formatted_timestamp} - {error_msg}")
        return False # want the script to exit here, a valid model must be chosen 

    # Need to check that this will ONLY run if all the prior conditions are successful - do i need to set a flag that exits the program if any false is returned?
    with open(logfilename, "a") as log_file:
            summary = f"{formatted_timestamp} - Summary of transcription parameters \n- Input Path: {path_to_audio} \n- Output Path: {path_for_transcripts} \n- Audio format: {audio_format} \n- Number of {audio_format} files: {file_count} \n- Transcription Model: {model_chosen} \n- Newline interval: {word_interval} words.\n\n"
            log_file.write(summary)

    print(f"Please make sure you are happy with this summary of processing:\n{summary}\n Abort if any parameters are incorrect. A large batch of files and-or a using the largest models will take significant time and compute.")
    time.sleep(5)
    return audio_file_names, model_chosen

#%%
########################## LOAD MODEL ###########################
            
def load_model(model_chosen): 
    """Load model"""
    try:
        model = whisper.load_model(model_chosen)
        # transcribe(model)
        return model

    except Exception as e: # REFINE ME
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        error_msg_load_model = (f"{formatted_timestamp} - Model load unsuccessful - {e}")
        print(error_msg_load_model)
        with open(logfilename, "a") as log_file:
            log_file.write(f"{error_msg_load_model}\n")                


#%%
########################## HEADER ################################
def create_header(audio_info_batch, index, audio_file, delimiter):
    """COMPLETE ME"""
    try:
        audio_file = sanitize_filename(audio_file)
        series, episode = extract_series_episode(audio_file)
        # construct individualised header for each file
        header_parts = [
        delimiter, # delimiter for AI processing
        f"Filename: {audio_file}",
        f"Content creation date: Unknown",
        f"Series: {audio_info_batch[1]['audio_content'][2]['series']}",
        f"Series#: {series} ",
        f"Episode#: {episode} ",
        f"Format: {audio_info_batch[1]['audio_content'][3]['format']}", 
        f"Topic: {audio_info_batch[1]['audio_content'][1]['topic']}",
        f"Type: {audio_info_batch[1]['audio_content'][0]['type']}",
        f"Participants: {audio_info_batch[0]['participants']}",
        f"Transcription Producer: {audio_info_batch[2]['transcript_type'][0]['producer']}",
        f"Transcription Model: {audio_info_batch[2]['transcript_type'][1]['model']}",
        f"Series Batch process order: {index}"
        ]
        header = "\n".join(header_parts) + "\n\n"
        
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_header_success = (f"{formatted_timestamp} - Header construction successful.")
        print(msg_header_success)
        print(header)
        with open(logfilename, "a") as log_file:
            log_file.write(f"{msg_header_success}\n")
        
        return header, audio_file

    except (TypeError, KeyError, IndexError, ValueError, Exception) as e:
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_header_error = (f"{formatted_timestamp} - Header construction error - {e}")
        print(msg_header_error)
        with open(logfilename, "a") as log_file:
            log_file.write(f"{msg_header_error}\n")


#%%
########################## TRANSCRIPTION ################################

def transcribe(model, audio_file):
    """
    Transcribes the audio file using the specified whisper model.

    Args:
        model (Model): The model used for transcription.
        audio_file (str): The path to the audio file.

    Returns:
        str: The raw transcript of the audio file.

    Raises:
        FileNotFoundError: If the audio file is not found.
        RuntimeError: If there is an error during transcription.
        Exception: If any other exception occurs.
    """
    try:
        path = os.path.join(path_to_audio, audio_file)
        result = model.transcribe(path)
        raw_transcript = result["text"]

        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        success_msg_transcription = (f"{formatted_timestamp} - Whisper transcription of {audio_file} successful.")
        print(success_msg_transcription)
        with open(logfilename, "a") as log_file:
            log_file.write(f"{success_msg_transcription}\n")
       
        return raw_transcript

    except (FileNotFoundError, RuntimeError, Exception) as e: # CalledProcessError?
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        error_msg_transcription = (f"{formatted_timestamp} - Whisper transcription error - {e}")
        with open(logfilename, "a") as log_file:
            log_file.write({error_msg_transcription})


#%%
######################### FORMATTING & OUTPUT #################################

# helper function to move            
def insert_newlines(text, word_interval):
    """Whisper transcripts are one long line of text. This function will insert a newline character at the end of every {interval} i.e. 10 words. If 0 was chosen, no newlines will be inserted """
    if word_interval == 0:
        return text # Returns original text without any newlines
    
    words = text.split() # NB: list of individual words
    for i in range(word_interval -1, len(words), word_interval): 
        words[i] = words[i] + '\n'
    return ' '.join(words)


def format_transcript(raw_transcript, header, delimiter):
    """ Writes the combined header + transcript + line numbers to file.
    NEED a try except block with error log"""
        
    # Insert newlines every word_interval
    linebreak_transcript = insert_newlines(raw_transcript, word_interval)

    # Combine header and transcript
    formatted_transcript = header+linebreak_transcript
    
    end_delimiter = f"\n{delimiter}\n"
    word_count = f"\nWord count: {len(formatted_transcript.split())}"
    print(word_count) # NB: just a check, can be removed
    formatted_transcript += word_count+end_delimiter

    # Insert line numbers
    lines = formatted_transcript.splitlines()
    formatted_transcript = "\n".join(f"{i+1}: {line}" for i, line in enumerate(lines))
    
    formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
    success_msg_formatting = (f"{formatted_timestamp} - Raw transcript formatted successfully.")
    print(success_msg_formatting)
    with open(logfilename, "a") as log_file:
        log_file.write(f"{success_msg_formatting}\n")

    return formatted_transcript

def save_transcript(formatted_transcript, audio_file):
    """ Save the formatted transcript to txt file and complete log file."""
    try:
        output_filename = f"{os.path.splitext(audio_file)[0]}_transcript.txt"
        # NB: splitext required so that ".mp3" isn't put in filename
   
        # Ensure the output directory exists
        os.makedirs(path_for_transcripts, exist_ok=True)
   
        full_path = os.path.join(path_for_transcripts, output_filename)

        # Now open the file for writing
        with open(full_path, "w") as output_file:
            output_file.write(formatted_transcript)
        
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        success_msg_processed = f"{formatted_timestamp} - {audio_file} processed successfully."
        print(success_msg_processed)
        with open(logfilename, "a") as log_file:
            log_file.write(f"{success_msg_processed}\n\n")

    except (FileNotFoundError, PermissionError, OSError, Exception) as e:
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_output_file_write_error = (f"{formatted_timestamp} - Whisper transcription error - {e}")
        with open(logfilename, "a") as log_file:
            log_file.write({formatted_timestamp}+" - "+{msg_output_file_write_error})
 
# msg = f"Whisper transcription error - {e}"




#%% 
######################## CALL SEQUENCE ########################

def master_call_single(model_chosen): 
    """Calls the functions which only need to be run once (pre-processing and model load) in order to prepare for the batch transcription of files.  in sequence. If any function returns False, the program will exit with an error message. If all functions return True, the program will return the list of audio filenames and the model."""
    if not log_file_setup():
        print("Error in setting up log file. Exiting program.")
        sys.exit(1) # currently makes logfile compulsory

    audio_file_names, model_chosen = pre_processing(path_to_audio, 
    path_for_transcripts, audio_format, word_interval, model_options, model_chosen) # returns: audio_file_names & model_chosen
    if audio_file_names is None or model_chosen is None:
        print("Error in model selection or audio filename processing. Please check error log. Exiting program.")
        sys.exit(1)
    
    model = load_model(model_chosen) # returns: model, takes: model_chosen
    if model is None:
        print("Error in loading model. Please check error log. Exiting program.")
        sys.exit(1)

    return audio_file_names, model
     
def master_call_loop(audio_filenames, model):
    for index, audio_file in enumerate(audio_filenames, start=1):
        header, audio_file = create_header(audio_info_batch, index, audio_file, delimiter) # returns: header
        raw_transcript = transcribe(model, audio_file) # returns: raw_transcript
        # insert_newlines(text, word_interval)
        formatted_transcript = format_transcript(raw_transcript, header, delimiter) # returns: formatted_transcript, takes raw_transcript, header
        save_transcript(formatted_transcript, audio_file) # takes: formatted_transcript

# %%

# def master_call_single(model_chosen): 
#     if not setup_log_file():
#         print("Error in setup_log_file")
#         return False

#     audio_file_names, model_chosen = pre_processing(path_to_audio, path_for_transcripts, audio_format, word_interval, model_options, model_chosen)
#     if audio_file_names is None or model_chosen is None:
#         print("Error in pre_processing")
#         return False

#     model = load_model(model_chosen)
#     if model is None:
#         print("Error in load_model")
#         return False