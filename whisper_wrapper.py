"""MAIN UTILITIES"""
from datetime import datetime as dt
import os
import shutil
import sys
import time
import whisper

from user_variables import use_log_file, path_to_logs, path_to_audio, path_for_output, move_processed, path_for_processed, audio_format, model_options, audio_info_batch, audio_file_info, delimiter

from utils_helper import log_file_write, audio_file_durations, process_time_estimator, extract_series_episode, insert_newlines

# Instanciate global variables
log_path = "" 
audio_filenames = []

#########################  PRE-PROCESSING ######################### 
def log_file_setup(use_log_file, path_to_logs):
    """
    Instanciates a datestamped .txt log file so activity in a single day is aggregated. Creates the specified directory for the log file if it doesn't already exist.

    Args:
        use_log_file (bool): Flag. If True, a log file will be created. If False, no log file will be created. User-set in user_variables.py.
        path_to_logs (str): Path to the directory where the log file will be created. User-specified in user_variables.py.
    
    Raises:
        TypeError: If value of use_log_file is not a boolean or if log_path is not a string.
        OSError: If there is a system-related error, such as a file not found.
        UnicodeEncodeError: If there are issues with the encoding of the file.

    Returns:
        bool: True if log file is set up successfully, False if log file is not set up.

    Exits:
        sys.exit(): Program will exit if the value of use_log_file was not a boolean value, or if the log file was set to compulsory but could not be instantiated.
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
        path_to_audio (str): Path to directory containing the audio files. Imported from user_variables.py
    
    Exits:
        sys.exit(): Program will exit if specified target directory does not exist.
    """
    
    if not os.path.exists(path_to_audio):
        msg_error = "Error, specified directory does not exist. Valid directory name or path for audio files to process is required. Exiting program.\n"
        log_file_write(msg_error, log_path)
        sys.exit(1)
    else: 
        msg_success = f"Pre Processing Checks - Input directory check successful.\n"
        log_file_write(msg_success, log_path)
        

def check_output_directory(path_for_output):   
    """
    Checks if the user specified output directory (to receive finished transcripts) already exists: if it doesn't, it attempts to create it. If this process fails, the program will exit with an error message and log entry.

    Args:
        path_for_output (str) - Path to the directory where transcripts will be saved. Imported from user_variables.py
    
    Exits:
        sys.exit(): Program will exit if the directory cannot be created.
    """
    
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
    """
    Checks if the user specified output directory (to receive processed audio files) already exists: if it doesn't, it attempts to create it. If this process fails, the program will exit with an error message and log entry.
    
    Args:
        move_processed (bool) - Flag. If True, processed audio files will be moved to the specified 'processed' directory. If False, no files will be moved. Imported from user_variables.py
        path_for_processed (str) - Path of directory to which processed audio files will be moved. Imported from user_variables.py

    Returns:
        bool: False if move_processed is not a boolean or if move_processed is False. Does not return a value if the directory is successfully created.
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
    """
    Obtains a list of audio file filenames in the target directory, incorporating a check to ensure that at least one file of the specified type is present. If no files are found, the program will exit with an error message and log entry.

    Args:
        path_to_audio (str): Path to directory containing the audio files. Imported from user_variables.py
        audio_format (str): The file extension of the audio files. Imported from user_variables.py

    Returns:
        tuple: A tuple containing the number of files (file_count) and a list of the audio_filenames.

    Exits:
        sys.exit(): Program will exit if there are no files of the target type in the specified directory.
    """   
    
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
    """
    Checks if word_interval entered is a positive integer or 0. If value is invalid, 0 is substituted and a raw transcript with no newlines or line numbers will be outputted.
    
    Args:
        word_interval (int) - Word interval at which to insert newlines into the transcript. Imported from user_variables.py

    Raises:
        ValueError: If the value of word_interval cannot be converted to an integer.
        
    Returns:
        word_interval (int) - The word interval at which to insert newlines into the transcript, which may have been changed to 0 if the user-input was invalid. If it was originally valid, the value will be the same as that passed in.
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
    """Checks if selected model is a valid choice from model_options dictionary.
    
    Args:
        model_key (str): The key for the chosen model in the model_options dictionary. Imported from user_variables.py

    Raises:
        KeyError: If the model_key is not found in the model_options dictionary.
    
    Exits:
        sys.exit(): Program will exit if the chosen model is not valid or is None.

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
        path_to_audio (str): Path to directory containing the audio files. Imported from user_variables.py 
        path_for_output (str) - Path to the directory where transcripts will be saved. Imported from user_variables.py
        audio_format (str): File extension / format of the audio files. Imported from user_variables.py
        file_count (int): Number of audio files in the batch to be processed.
        model_key (str): The key for the chosen model in the model_options dictionary. Imported from user_variables.py
        word_interval (int) - The word interval at which to insert newlines into the transcript, which may have been changed to 0 by  check_word_interval() since it's original pass to master_call_single(), if the user-input was invalid.
        audio_filenames (list): List of audio file names in the batch, generated by obtain_audio_filenames()

    Interactions:
        Calls two helper functions: audio_file_durations() and process_time_estimator() to extract the audio file duration and then calculate the estimated time required to process the batch. If there are errors in either of these functions, the program will simply continue without the time estimation.

    Returns:
        None. Does output to screen and log file a summary of the processing parameters, and where possible, an estimate of the time required to process the batch. Processing time for individual files is only printed to screen - a batch processing time estimate is printed and written to the log file.
    
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
    
######################### LOAD MODEL #########################
            
def load_model(model_key): 
    """Loads selected model into whisper transcribe function. If model is not found, the program will exit with an error message and log entry.
    
    Args:
        model_key (str): Key representing the chosen model from model_options dictionary.

    Interactions:
        check_model() has already been called to ensure that the model_key is a valid choice from the model_options dictionary, so any errors here are likely to be system-related.

    Exits:
        sys.exit(): Program will exit if the returned model None.
                
    Returns:
        model (str): The Whisper ASR model instance to be used for transcription.

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


######################### HEADER #########################
def create_header(index, audio_file, delimiter):
    """Constructs a header for the transcript file.
    
    Args:
        index (int): The batch process order of the series.
        audio_file (str): Filename of the currently processing audio file.
        delimiter (str): Delimiter inserted at start and end of transcript.
    
    Manual Customisation:
        The header fields are populated from the audio_info_batch and audio_file_info dictionaries in user_variables.py. If any fields are not required, simply comment out the line beginning `f"{field_name}` which you want to omit. Depending upon the method you are using, you will need to change the interpolated references to point towards whichever dictionary you are using. The default is to use audio_info_batch, as it is far less labour intensive (but, obviously, it cannot accomodate information which should vary per file. See README for full explanation). 

    Interactions:
        Calls extract_series_episode() in utils_helper.py to extract series and episode numbers from the filename where possible.    

    Returns:
        tuple: A tuple containing the constructed header (str) and the audio_file name (str)."""    

    try:
        # Extract series and episode numbers from filename where possible     
        series, episode = extract_series_episode(audio_file, log_path)
        
        # Create speaker strings (from individual audio_file_info)
        try:
            if index-1 < len(audio_file_info):
                speaker_strings = [f"Speaker: {speaker['name']} - {speaker['role']}" for speaker in audio_file_info[index-1]['speakers']]
            else:
                speaker_strings = ["Error"]
                
        except IndexError as e:
            msg_error = (f"Error in constructing information from audio_file_info dictionary. It is likely that the number of dictionaries and the number of files are not matched - {e}.\n")
            log_file_write(msg_error, log_path)
            speaker_strings = ["Error"]
            
        # Create participant strings (from audio_batch_info)
        participant_strings = [f"Participant: {participant['name']} - {participant['role']}" for participant in audio_info_batch[0]['participants']]

        header_parts = [
        delimiter, # delimiter useful for AI processing
        f"Filename: {audio_file}",
        f"Content date: {audio_info_batch[1]['audio_content'][4]['date']}",
        f"Series: {audio_info_batch[1]['audio_content'][2]['series']}",
        f"Series#: {series}",
        f"Episode#: E0{index}", # should be {episode}
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
        # Return a default value when an exception is caught
        return "Error constructing header", audio_file


######################### TRANSCRIPTION ######################### 

def transcribe(model, audio_file):
    """
    Transcribes the audio file using the specified whisper model.

    Args:
        model (str): The Whisper ASR model instance to be used for transcription, instanciated by load_model().
        audio_file (str): Filename of the currently processing audio file.

    Returns:
        raw transcript (str): unformatted text string the audio file produced by Whisper.

    Raises:
        FileNotFoundError: If the input audio file is not found.
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


######################### FORMATTING & OUTPUT #########################

def format_transcript(raw_transcript, word_interval, header, delimiter):
    """ Manifests the header + transcript + line numbers and newlines + word count and writes the combination to a text file.
            
    Args:
        raw transcript (str): unformatted text string the audio file produced by Whisper.
        word_interval (int) - User defined word interval at which to insert newlines into the transcript, which may have been changed to 0 by check_word_interval() if the user-input was invalid. 
        header (str): The header fields constructed by create_header().
        delimiter (str): User-defined delimiter to be inserted at start and end of transcript. If an empty string was supplied, no delimiter will be inserted.

    Interactions:
        Calls insert_newlines() to insert newlines into the raw transcript at the specified word_interval.    

    Contingency:
        If the function encounters an error, it will return the raw transcript as it was passed in, without formatting.        

    Returns:
        - formatted_transcript (str): If the function is successful and no error is thrown, it will return the formatted transcript with header, newlines, line numbers, word count and delimiters.
        - raw_transcript (str): If the function encounters an error, it will return the raw transcript without formatting.
        
    """
    try:       
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
    
    except Exception as e:
        msg_error = (f"Error in formatting transcript - {e}.\nThe raw transcript will be returned without formatting.\n")
        log_file_write(msg_error, log_path)
        return raw_transcript


def save_transcript(formatted_transcript, audio_file, model_key):
    """Save the formatted transcript to .txt file.
        
    Args:
        * formatted_transcript (str): If format_transcript() was successful, it provided the formatted transcript with header, newlines, line numbers, word count and delimiters.
        * formatted_transcript (str): If format_transcript() encountered an error, the variable instead contains the raw transcript as it was transcribed without formatting.
        audio_file (str): Filename of the currently processing audio file.
        model_key (str): Key representing the chosen model from model_options dictionary.

    Interactions:
        check_output_directory() has already been called to ensure that the output directory exists, so any errors here are likely to be system-related.    

    Contingency:
        If the function encounters an error in the attempt to save the text file     

    Returns:
        bool: True if the transcript was saved successfully, False if the transcript was not saved successfully.
    """
    try:
        alt_name = model_options[model_key]["alt_name"]
        output_filename = f"{os.path.splitext(audio_file)[0]}_{alt_name}.txt"
        # NB: splitext required so that the file extension isn't put in filename
   
        full_path = os.path.join(path_for_output, output_filename)

        with open(full_path, "w") as output_file:
            output_file.write(formatted_transcript)
        
        msg_success = f"{audio_file} processed successfully and transcript saved to .txt file.\n"
        log_file_write(msg_success, log_path)
        return True

    except (FileNotFoundError, PermissionError, OSError, Exception) as e:
        msg_error = (f"Error attempting to save transcript to txt file - {e}.\nWill attempt to print transcript string to terminal incase it can be manually saved...\n")
        print(formatted_transcript)
        log_file_write(msg_error, log_path)
        return False

######################### TIDY UP #########################

def move_processed_file(move_processed, audio_file, path_to_audio, path_for_processed, log_path):
    """
    Moves the audio file to the 'processed' directory after transcription. Note, it is perfectly valid for the 'processed' directory to be the same as the 'output' directory. 
    
    Args:
        move_processed (bool): Flag. If True, the file will be moved to the processed directory. If false, the operation will be skipped.
        audio_file (str): Filename of the currently processing audio file.
        path_to_audio (str): Path to directory containing the audio files. 
        path_for_processed (str): Path to directory where processed files are to be moved.
        log_path (str): Full path of log file to which status messages are written.

    Dependencies:
        Function relies upon check_processed_directory() to have already  checked for a legitimate filepath and created the directory if required."""
    if move_processed == False:
        return False

    # Move the file to the 'processed' directory
    try:
        current_file_path = os.path.join(path_to_audio, audio_file)
        new_file_path = os.path.join(path_for_processed, audio_file)

        # Move the file
        shutil.move(current_file_path, new_file_path)
        msg_success = f"File moved from '{current_file_path}' to '{new_file_path}'\n"
        log_file_write(msg_success, log_path)
        return True
    
    except (FileNotFoundError, PermissionError, RuntimeError, OSError, Exception) as e:
        msg_error = (f"Error occurred whilst attempting to move {audio_file}\nfrom {current_file_path}\nto {new_file_path}\n: {e}")
        log_file_write(msg_error, log_path)
        return False

######################## CALL SEQUENCE ########################

def master_call_single(word_interval, model_key): 
    """Sequentially calls the functions which only need to be run once in order to prepare for the batch transcription of files. Successful processing of: 
    check_input_directory, check_output_directory, obtain_audio_filenames, check_model and load_model are all essential, so the program will exit upon failure of any of these functions.
        
    Args:
        word_interval (int): The user-specified word interval at which to insert newlines into the transcript. Note, that check_word_interval may alter this value (substituting 0 if an invalid interval was entered), so a potentially altered value may be what is passed to master_call_loop().
        model_key (str): Key representing the chosen model from model_options dictionary.

    Returns:
        audio_filenames (list): List of audio file names in the batch, generated by obtain_audio_filenames()
        model (str): The Whisper ASR model instance to be used for transcription.
    
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
    """
    Sequentially calls the functions which need to run for each audio file in the batch. 
    
    Args:
        audio_filenames (list): List of audio file names in the batch, generated by obtain_audio_filenames()
        word_interval (int): The user-specified word interval at which to insert newlines into the transcript. Note, that check_word_interval may alter this value (substituting 0 if an invalid interval was entered), so a potentially altered value may be what is passed to master_call_loop().
        model_key (str): Key representing the chosen model from model_options dictionary.
        model (str): The Whisper ASR model instance to be used for transcription.

    Contingency:
        format_transcript() and save_transcript() have contingencies for failure which attempt to preserve and output the original transcript produced by the Whisper model.

    Returns:
        None. Upon completion of the batch processing, a message is printed to the terminal and written to the log file to indicate that the batch processing has finished.
    """

    for index, audio_file in enumerate(audio_filenames, start=1):
        header, audio_file = create_header(index, audio_file, delimiter) 
        raw_transcript = transcribe(model, audio_file)
        formatted_transcript = format_transcript(raw_transcript, word_interval, header, delimiter)
        save_transcript(formatted_transcript, audio_file, model_key)
        move_processed_file(move_processed, audio_file, path_to_audio, path_for_processed, log_path)
    msg_finished = f"Transcription of {audio_filenames} finished. This is not confirmation that all files were transcribed without issue: check log file and print statements to see if any individual files encountered errors.\n\n"
    log_file_write(msg_finished, log_path)

