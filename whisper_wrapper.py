"""MAIN UTILITIES"""

import os
import time
from datetime import datetime as dt
import whisper
import sys

from user_variables import use_log_file, path_to_logs, path_to_audio, path_for_output, path_for_processed, audio_format, model_options, audio_info_batch, audio_file_info, delimiter

from utils_helper import log_file_write, audio_file_durations, process_time_estimator, extract_series_episode, move_processed_file

log_path = "" # Instanciates global variable
audio_filenames = []

########################## PRE-PROCESSING #########################
def log_file_setup(use_log_file, path_to_logs):
    """
    Instanciates a datestamped .txt log file so activity in a single day is aggregated.

    Args:
        use_log_file (bool): If True, a log file will be created. If False, no log file will be created. Set in user_variables.py.
    
    Returns:
        bool: True if log file is set up successfully, False if log file is not set up.

        sys.exit(): The program will exit if the value of use_log_file was not a boolean value, or if the log file was set to compulsory but could not be instantiated.
    """

    try:
        if not isinstance(use_log_file, bool):
            raise TypeError

    except TypeError:
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_error = f"{formatted_timestamp} - Error, use_log_file must be a boolean value: True or False. Check that you haven't entered a string. Exiting program.\n"
        print(msg_error)
        sys.exit(1)

    if use_log_file == False:
        return False
    
    global log_path 
    run_date = dt.now().strftime("%Y-%m-%d")
    logfilename = f"log_whisper_transcripts_{run_date}.txt"
    log_path = os.path.join(path_to_logs, logfilename)

    try:
        if not log_path:
            raise TypeError
    except TypeError:
            formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
            msg_error = f"{formatted_timestamp} - Error, log_file_path must be either "" for root directory or 'directory'. Check that you haven't entered None. Exiting program.\n"
            print(msg_error)
            sys.exit(1)
    try:    
        if os.path.exists(log_path):
            return True
        if not os.path.exists(log_path):
            os.makedirs(path_to_logs, exist_ok=True)
            with open(log_path, 'a'):
                pass
            msg_success = ("Log File Setup - Successful.\n")
            log_file_write(msg_success, log_path)
            return True
        
    except (OSError, UnicodeEncodeError) as e:
            formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
            msg_error = f"{formatted_timestamp} - Error, unable to instantiate log file with name {logfilename} in {path_to_logs}. The following error occurred: {e}\n"
            print(msg_error)
            print("Log file is set to compulsory. Exiting program.\n")
            sys.exit(1)


def check_input_directory(path_to_audio):
    """
    Checks if the user supplied directory path exists. If not, the program will exit with an error message and log entry.
    
    Args: 
        path_to_audio (str) - the path to the directory where audio files to process are located. Imported from user_variables.py
    """
    ### First check supplied string against list of invalid characters?
    if not os.path.exists(path_to_audio):
        msg_error = "Error, specified directory does not exist. Valid directory name or path for audio files to process is required. Exiting program.\n"
        log_file_write(msg_error, log_path)
        sys.exit(1)
    else: 
        msg_success = f"Pre Processing Checks - Input directory check successful.\n"
        log_file_write(msg_success, log_path)
        

def check_output_directory(path_for_output):   
    """    Checks if specified output directory (for finished transcripts) already exists: if it doesn't, it attempts to create it. If this process fails, the program will exit with an error message & log entry.

    Args:
        path_for_output (str) - the path to the directory where transcripts will be saved. Imported from user_variables.py
    """
    ### First check supplied string against list of invalid characters?
    try: 
        if not os.path.exists(path_for_output):
            os.makedirs(path_for_output)
            msg_success = f"Pre Processing Checks - Output directory creation successful.\n"
            log_file_write(msg_success, log_path)
           
        
    except (PermissionError, FileNotFoundError, RuntimeError, OSError, Exception) as e:
        msg_error = f"Error, unable to create output directory. The following error occurred: {e}.\n Check directory path and permissions. Exiting program.\n"
        log_file_write(msg_error, log_path)
        sys.exit(1)


def check_processed_directory(move_processed, path_for_processed):
    """Checks if specified output directory (for moved audio files) already exists: if it doesn't, it attempts to create it. If this process fails, the program will exit with an error message & log entry.
    
    Args:
        move_processed (bool) - if True, processed audio files will be moved to a new directory. If False, no files will be moved. Imported from user_variables.py
        path_for_processed (str) - the path to the directory where processed audio files will be moved. Imported from user_variables.py
    """
    try:
        if not isinstance(move_processed, bool):
            raise TypeError

    except TypeError:
        msg_error = f"Error, move_processed must be a boolean value: True or False. Check that you haven't entered a string. Processed files will not be moved.\n"
        log_file_write(msg_error, log_path)
        return False
        
    if move_processed == False:
        return False

    # Check if the directory already exists, if not create it
    if not os.path.exists(path_for_processed):
        os.makedirs(path_for_processed)
        msg_success = f"Created directory to receive processed files: {path_for_processed}\n"
        log_file_write(msg_success, log_path)


def obtain_audio_filenames(path_to_audio, audio_format):   
    """COMPLETE ME"""   
    try:
        # Obtain list of filenames, filtered by specified filetype(s), and being file vs directory
        audio_filenames = [f for f in os.listdir(path_to_audio) if f.endswith(audio_format) and os.path.isfile(os.path.join(path_to_audio, f))]
        # Sort filenames in ascending order (alphabetical and numerical)
        audio_filenames = sorted(audio_filenames) 
        print(audio_filenames)
        file_count = len(audio_filenames)
        
        pretty_audio_filenames = '\n'.join(audio_filenames)
        summary_files = f"Directory contains {file_count} {audio_format} file(s):\n{pretty_audio_filenames}\n"
        log_file_write(summary_files, log_path)    

        # Use list of filenames to check if directory contains at least one file of type specified
        if not audio_filenames: # NB: an empty list is falsey
            msg_error = f"Error, no files of type {audio_format} found in {path_to_audio}.\n Check file extension supplied matches at least one audio file. Exiting program.\n"
            log_file_write(msg_error, log_path)
            sys.exit(1)
        else:
            msg_success = "File type check successful.\n"
            log_file_write(msg_success, log_path)
            return file_count, audio_filenames
            
    except (FileNotFoundError, PermissionError, RuntimeError, OSError, Exception) as e: # need to specify errors
        msg_error = f"Error pre-processing audio filenames. The following error occurred: {e}.\n Check directory path, file types and permissions. Exiting program.\n"
        log_file_write(msg_error, log_path)
        sys.exit(1)


def check_word_interval(word_interval):
    """Checks if word interval entered is a positive integer or 0. If value is invalid 0 is substituted and a raw transcript with no newlines or line numbers will be outputted.
    
    Args:
        word_interval (str) - word interval at which to insert newlines into the transcript. Imported from user_variables.py

    Returns:
        word_interval (int) - the word interval at which to insert newlines into the transcript, which may have been changed to 0 if the input was invalid. If it was originally valid, the value will be the same as passed in.
    """
    try:
        word_interval = abs(int(word_interval))
        return word_interval
    except ValueError:
        msg_error = "Error, word interval must be a positive integer or 0. No newlines will be inserted, defaulting to raw transcript.\n"
        log_file_write(msg_error, log_path)
        word_interval = 0 # the program will continue without inserting linebreaks, even if invalid word interval (i.e. -4 or "four") entered.
        return word_interval


def check_model(model_key):
    """Checks if selected model is a valid choice from model_options.
    
    Args:
        model_key (str) - the user's chosen model as a longform string. References keys in model_options dictionary. Imported from user_variables.py
    
    Returns: None
    """
    model_chosen = model_options[model_key]["name"]
    model_names = [model["name"] for model in model_options.values()]
    if model_chosen not in model_names or model_chosen is None: 
        msg_error = "Error, invalid model chosen. Please reselect. Exiting program.\n"
        log_file_write(msg_error, log_path)
        sys.exit(1)


def provide_pre_processing_summary(path_to_audio, path_for_output, audio_format, file_count, model_key, word_interval, audio_filenames):
    """Provides a summary of the processing parameters to the user, including, where possible, an estimate of the time required to process the batch.
    
    Args:

    
    Returns:
        None
    
    """
    model_chosen = model_options[model_key]["name"]
    summary = f"Summary of transcription parameters \n- Input Path: {path_to_audio} \n- Output Path: {path_for_output} \n- Audio format: {audio_format} \n- Number of {audio_format} files: {file_count} \n- Transcription Model: {model_chosen} \n- Newline interval: {word_interval} words.\n"
    log_file_write(summary, log_path)

    audio_duration_success = True # if audio_file_durations fails, then process_time_estimator should also be skipped
    try:
        audio_time_dict = audio_file_durations(path_to_audio, audio_filenames, log_path) # calls helper fuction to extract audio file durations
    except Exception as e:
        msg_error = f"Error, unable to extract audio file durations. The following error occurred: {e}.\n"
        log_file_write(msg_error, log_path)
        audio_duration_success = False

    if audio_duration_success:
        try:
            batch_summary = process_time_estimator(audio_time_dict, model_key, model_options, log_path) # calls helper function to estimate time required to process batch
            log_file_write(batch_summary, log_path)
            msg_preprocessing_w_time = f"A large batch of files and/or a using the largest models may take significant time and compute.\nPlease ensure this summary of processing is correct:\n{summary}Estimated {batch_summary}\n"
            print(msg_preprocessing_w_time)
            time.sleep(5)
        except Exception as e:
            msg_error = f"Error, unable to estimate time required to process batch. The following error occurred: {e}.\n"
            log_file_write(msg_error, log_path)

    else:
        msg_preprocessing = f"A large batch of files and/or a using the largest models may take significant time and compute.\nPlease ensure this summary of processing is correct:\n{summary}"
        print(msg_preprocessing)
        time.sleep(5)
    
########################## LOAD MODEL ###########################
            
def load_model(model_key): 
    """Loads selected model into whisper transcribe function. If model is not found, the program will exit with an error message and log entry.
    
    Args:

    Returns:

    """
    
    if model_key not in model_options:
        msg_error = f"Error, invalid model name '{model_key}' supplied. Please reselect. Exiting program.\n"
        log_file_write(msg_error, log_path)
        sys.exit(1)
    
    model_chosen = model_options[model_key]["name"]
    try:
        model = whisper.load_model(model_chosen)
        if model is not None:
            msg_success = (f"{model_chosen} Model load successful.\n")
            log_file_write(msg_success, log_path)
            return model
        elif model is None:
            msg_error = "Error in loading model. Please check error log. Exiting program.\n"
            log_file_write(msg_error, log_path)
        sys.exit(1)

    except (FileNotFoundError, RuntimeError, Exception) as e:
        msg_error = (f"Model load unsuccessful - {e}.\n")
        log_file_write(msg_error, log_path)               


########################## HEADER ################################
def create_header(index, audio_file, delimiter):
    """Constructs a header for the transcript file. Simply comment out any header fields that aren't required.
    
    Args:
        audio_info_batch (list): List of audio filename strings in the batch.
        index (int): The batch process order of the series.
        audio_file (str): Filename of audio file.
        delimiter (str): Delimiter inserted at start and end of transcript.
    
    Returns:
        tuple: A tuple containing the constructed header (str) and the audio file name (str)."""    

    try:
        # Extract series and episode numbers from filename where possible     
        series, episode = extract_series_episode(audio_file, log_path)
        
        # Create speaker strings (from individual audio_file_info)
        speaker_strings = [f"Speaker: {speaker['name']} - {speaker['role']}" for speaker in audio_file_info[index-1]['speakers']]
        
        # Create participant strings (from audio_batch_info)
        participant_strings = [f"Participant: {participant['name']} - {participant['role']}" for participant in audio_info_batch[0]['participants']]

        header_parts = [
        delimiter, # delimiter useful for AI processing
        f"Filename: {audio_file}",
        f"Content date: {audio_info_batch[1]['audio_content'][4]['date']}",
        f"Series: {audio_info_batch[1]['audio_content'][2]['series']}",
        f"Series#: {series} ",
        f"Episode#: {episode} ",
        f"Format: {audio_info_batch[1]['audio_content'][3]['format']}", 
        f"Topic: {audio_info_batch[1]['audio_content'][1]['topic']}",
        f"Type: {audio_info_batch[1]['audio_content'][0]['type']}",
        *participant_strings,
        # *speaker_strings,
        f"Transcription Producer: {audio_info_batch[2]['transcript_type'][0]['producer']}",
        f"Transcription Model: {audio_info_batch[2]['transcript_type'][1]['model']}",
        f"Batch process order: {index}"
        ]
        header = "\n".join(header_parts) + "\n\n"
        
        msg_success = (f"Header construction successful.\n")
        print(header)
        log_file_write(msg_success, log_path)        
        return header, audio_file

    except (TypeError, KeyError, IndexError, ValueError, Exception) as e:
        msg_error = (f"Header construction error - {e}.\n")
        log_file_write(msg_error, log_path)


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
        log_file_write(success_msg, log_path)
        return raw_transcript

    except (FileNotFoundError, RuntimeError, Exception) as e: 
        msg_error = (f"Whisper transcription error - {e}.\n")
        log_file_write(msg_error, log_path)
        return False


######################### FORMATTING & OUTPUT #################################

# helper function to move            
def insert_newlines(text, word_interval):
    """Whisper transcripts are one long line of text. This function will insert a newline character at the end of every {interval} i.e. 10 words. If 0 was chosen, no newlines will be inserted.
    
    Args:

    Returns:
    
    """
    if word_interval == 0:
        return text # Returns original text without any newlines
    
    words = text.split() # NB: list of individual words
    for i in range(word_interval -1, len(words), word_interval): 
        words[i] = words[i] + '\n'
    return ' '.join(words)


def format_transcript(raw_transcript, word_interval, header, delimiter):
    """ Writes the combined header + transcript + line numbers to file.
    
        
    Args:

    Returns:
    
    """
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
    log_file_write(msg_success, log_path)

    return formatted_transcript


def save_transcript(formatted_transcript, audio_file, model_key):
    """Save the formatted transcript to .txt file.
        
    Args:

    Returns:
    
    """
    try:
        alt_name = model_options[model_key]["alt_name"]
        output_filename = f"{os.path.splitext(audio_file)[0]}_{alt_name}.txt"
        # NB: splitext required so that the file extension isn't put in filename
   
        # Ensure the output directory exists - is this required given check_output_directory has already run?
        # os.makedirs(path_for_output, exist_ok=True)
   
        full_path = os.path.join(path_for_output, output_filename)

        # Now open the file for writing
        with open(full_path, "w") as output_file:
            output_file.write(formatted_transcript)
        
        msg_success = f"{audio_file} processed successfully.\n"
        log_file_write(msg_success, log_path)
        return True

    except (FileNotFoundError, PermissionError, OSError, Exception) as e:
        msg_error = (f"Whisper transcription error - {e}.\n")
        log_file_write(msg_error, log_path)
        return False

#%% 
######################## CALL SEQUENCE ########################

def master_call_single(word_interval, model_key): 
    """Sequentially calls the functions which only need to be run once in order to prepare for the batch transcription of files. Successful processing of: 
    check_input_directory, check_output_directory, obtain_audio_filenames, check_model and load_model are all essential, so the program will exit upon failure of any of these functions.
        
    Args:

    Returns:
        audio_filenames (list): List of audio filenames in the batch.
        model (str): The model name to be used for transcription.
    
    """
    log_file_setup(use_log_file, path_to_logs)
    check_input_directory(path_to_audio)
    check_output_directory(path_for_output)
    file_count, audio_filenames = obtain_audio_filenames(path_to_audio, audio_format)
    word_interval = check_word_interval(word_interval)
    check_model(model_key)
    provide_pre_processing_summary(path_to_audio, path_for_output, audio_format, file_count, model_key, word_interval, audio_filenames)
    model = load_model(model_key) 
    return audio_filenames, model, word_interval
     
def master_call_loop(audio_filenames, word_interval, model_key, model):
    for index, audio_file in enumerate(audio_filenames, start=1):
        header, audio_file = create_header(index, audio_file, delimiter) 
        raw_transcript = transcribe(model, audio_file)
        formatted_transcript = format_transcript(raw_transcript, word_interval, header, delimiter)
        save_transcript(formatted_transcript, audio_file, model_key)
        move_processed_file(audio_file, path_to_audio, path_for_processed, log_path)
    msg_finished = f"Transcription of {audio_filenames} finished. This is not confirmation that all files were transcribed without issue: check log file and print statements to see if any individual files encountered errors.\n\n"
    log_file_write(msg_finished, log_path)

