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

Last code update 24 01 26 """

logfilename = "" # Instanciates global variable
audio_filenames = []

#%%
########################## PRE-PROCESSING #########################
def log_file_setup(log_file_complsory):
    """Instanciates a datestamped .txt log file so activity in a single day is aggregated."""
    global logfilename 
    run_date = dt.now().strftime("%Y-%m-%d")
    logfilename = f"log_whisper_transcripts_{run_date}.txt"
    if log_file_compulsory == False:
        return True
    try:
        if os.path.exists(logfilename):
            return True
        if not os.path.exists(logfilename):
            msg_success = ("Log File Setup - Successful.\n")
            log_file_write(msg_success, logfilename)
            return True
        
    except (OSError, UnicodeEncodeError) as e:
            formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
            msg_error = f"{formatted_timestamp} - Error, unable to instantiate log file with name {logfilename}. The following error occurred: {e}\n"
            print(msg_error)
            print("Log file is set to compulsory. Exiting program.")
            sys.exit(1)

#%%

    """Checks if the input directory exists, if the output directory exists, if the audio format is present, and if the word interval is a positive integer. If all checks pass, returns a list of filenames and the model chosen. If any check fails, returns False."""

def check_input_directory(path_to_audio):
    # Check if the user supplied directory path exists
    if not os.path.exists(path_to_audio):
        msg_error = "Error, specified directory does not exist. Valid directory name or path for audio files to process is required. Exiting program.\n"
        log_file_write(msg_error, logfilename)
        sys.exit(1)
    else: 
        msg_success = f"Pre Processing Checks - Input directory check successful.\n"
        print(msg_success)
        log_file_write(msg_success, logfilename)
        # ? return True

def check_output_directory(path_for_transcripts):   
    """Function attempts to create specified output directory for finished transcripts, if it doesn't already exist."""
    try: 
        if not os.path.exists(path_for_transcripts):
            os.makedirs(path_for_transcripts)
            msg_success = f"Pre Processing Checks - Output directory creation successful.\n"
            log_file_write(msg_success, logfilename)
    except (PermissionError, FileNotFoundError, OSError) as e:
        msg_error = f"Error, unable to create output directory. The following error occurred: {e}.\n Check directory path and permissions. Exiting program.\n"
        log_file_write(msg_error, logfilename)
        sys.exit(1)

def obtain_audio_filenames(path_to_audio, audio_format):   
    """COMPLETE ME"""   
    try:
        # Obtain list of filenames, filtered by specified filetype(s), and being file vs directory
        audio_file_names = [f for f in os.listdir(path_to_audio) if f.endswith(audio_format) and os.path.isfile(os.path.join(path_to_audio, f))]
        file_count = len(audio_file_names)
        
        pretty_audio_filenames = '\n'.join(audio_file_names)
        summary_files = f"Directory contains {file_count} {audio_format} file(s):\n{pretty_audio_filenames}\n"
        # NB: concats list of strings with \n. The +\n ensures full write ends with a newline
        log_file_write(summary_files, logfilename)    

        # Use list of filenames to check if directory contains at least one file of type specified
        if not audio_file_names: # NB: an empty list is falsey
            msg_error = f"Error, no files of type {audio_format} found in {path_to_audio}.\n Check file extension supplied matches at least one audio file. Exiting program.\n"
            log_file_write(msg_error, logfilename)
            sys.exit(1)
        else:
            msg_success = "File type check successful.\n"
            log_file_write(msg_success, logfilename)
            return file_count, audio_file_names
            
    except (FileNotFoundError, PermissionError, OSError) as e: # need to specify errors
        msg_error = f"Error pre-processing audio filenames. The following error occurred: {e}.\n Check directory path, file types and permissions. Exiting program.\n"
        log_file_write(msg_error, logfilename)
        sys.exit(1)

def check_word_interval(word_interval):
    """Checks if word interval entered is a positive integer or 0. If entry was invalid subsitutes 0 word interval to provide raw transcript with no newlines."""
    try:
        word_interval = abs(int(word_interval))
    except ValueError:
        msg_error = "Error, word interval must be a positive integer or 0. No newlines will be inserted, defaulting to raw transcript.\n"
        log_file_write(msg_error, logfilename)
        word_interval = 0 # the program will continue without inserting linebreaks, even if invalid word interval (i.e. -4 or "four") entered.

def check_model(model_chosen):
    """Checks if user chosen model is a valid selection from model_options."""
    model_names = [model["name"] for model in model_options.values()]
    if model_chosen not in model_names:
        msg_error = "Error, invalid model chosen. Please reselect. Exiting program.\n"
        log_file_write(msg_error, logfilename)
        sys.exit(1)

def provide_pre_processing_summary(path_to_audio, path_for_transcripts, audio_format, file_count, model_chosen, word_interval):
    summary = f"Summary of transcription parameters \n- Input Path: {path_to_audio} \n- Output Path: {path_for_transcripts} \n- Audio format: {audio_format} \n- Number of {audio_format} files: {file_count} \n- Transcription Model: {model_chosen} \n- Newline interval: {word_interval} words.\n"
    log_file_write(summary, logfilename)

    print(f"Please ensure this summary of processing is correct:\n{summary}\n Abort if any parameters are incorrect. A large batch of files and/or a using the largest models may take significant time and compute.")
    time.sleep(5)
    return True # ? Necessary

#%%
########################## LOAD MODEL ###########################
            
def load_model(model_chosen): 
    """Load model selected model."""
    ### Need to do a check here that model chosen matches the list of valid models
    if model_chosen not in [m["name"] for m in model_options.values()]:
        msg_error = f"Error, invalid model name '{model_chosen}' supplied. Please reselect. Exiting program."
        log_file_write(msg_error, logfilename)
        sys.exit(1)
    try:
        model = whisper.load_model(model_chosen)
        return model

    except Exception as e: # REFINE THIS
        msg_error = (f"Model load unsuccessful - {e}.\n")
        log_file_write(msg_error, logfilename)               


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
        
        msg_success = (f"Header construction successful.\n")
        print(header)
        log_file_write(msg_success, logfilename)        
        return header, audio_file

    except (TypeError, KeyError, IndexError, ValueError, Exception) as e:
        msg_error = (f"Header construction error - {e}.\n")
        log_file_write(msg_error, logfilename)


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

        success_msg = (f"Whisper transcription of {audio_file} successful.\n")
        log_file_write(success_msg, logfilename)
        return raw_transcript

    except (FileNotFoundError, RuntimeError, Exception) as e: # CalledProcessError?
        msg_error = (f"Whisper transcription error - {e}.\n")
        log_file_write(msg_error, logfilename)
        return False


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
    """ Writes the combined header + transcript + line numbers to file."""
    ### NEED a try except block with error log
        
    # Insert newlines every word_interval
    linebreak_transcript = insert_newlines(raw_transcript, word_interval)

    # Combine header and transcript
    formatted_transcript = header+linebreak_transcript
    
    end_delimiter = f"\n{delimiter}\n"
    word_count = f"\nWord count: {len(formatted_transcript.split())}"
    formatted_transcript += word_count+end_delimiter

    # Insert line numbers
    lines = formatted_transcript.splitlines()
    formatted_transcript = "\n".join(f"{i+1}: {line}" for i, line in enumerate(lines))

    msg_success = (f"Raw transcript formatted successfully.\n")
    log_file_write(msg_success, logfilename)

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
        
        msg_success = f"{audio_file} processed successfully.\n"
        log_file_write(msg_success, logfilename)
        return True

    except (FileNotFoundError, PermissionError, OSError, Exception) as e:
        msg_error = (f"Whisper transcription error - {e}.\n")
        log_file_write(msg_error, logfilename)
        return False

#%% 
######################## CALL SEQUENCE ########################

def master_call_single(model_chosen): 
    """Calls the functions which only need to be run once (pre-processing and model load) in order to prepare for the batch transcription of files.  in sequence. If any function returns False, the program will exit with an error message. If all functions return True, the program will return the list of audio filenames and the model."""
    log_file_setup(log_file_compulsory)
    audio_file_names, model_chosen = pre_processing(path_to_audio, 
    path_for_transcripts, audio_format, word_interval, model_options, model_chosen) # returns: audio_file_names & model_chosen
    if audio_file_names is None or model_chosen is None:
        print("Error in model selection or audio filename processing. Please check error log. Exiting program.")
        sys.exit(1)
        #### CHANGE THIS ^^ WHEN SPLIT PREPROCESSING FUNCTION
    
    model = load_model(model_chosen) 
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

