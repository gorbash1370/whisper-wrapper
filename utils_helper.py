"""HELPER UTILTIES"""

from datetime import datetime as dt
import os
import re

import subprocess
from user_variables import use_log_file

def log_file_write(msg, log_path):
    """
    Supplied message is printed to screen and written to the log file, prepended with a timestamp. If use_log_file is set to False, the message is only printed to screen.

    Args:
        msg (str): Message to be written to log file.
        log_path (str): Full path of log file to which status messages are written.
    
    Note:
        'use_log_file' should be a global boolean variable that controls whether logging to file is enabled.
    
    Returns: None
    """

    print(msg)
    if use_log_file == False:
        return
    else:
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_timestamped = f"{formatted_timestamp} - " + msg
        with open(log_path, "a") as log_file:
            log_file.write(msg_timestamped)
    


def audio_file_durations(path_to_audio, audio_filenames, log_path):
    """
    Extracts the duration of each audio file in the batch.

    Args:
        path_to_audio (str): Path to directory containing the audio files.
        audio_filenames (list): List of audio file names in the batch, generated by obtain_audio_filenames()
        log_path (str): Full path of log file to which status messages are written.

    Dependencies: 
        ffprobe is tool (for extracting info about media files) included with ffmpeg. This method was chosen because ffmpeg should already be installed as OpenAi's Whisper model requires it.
    
    Raises:
        FileNotFoundError: If the audio file is not found at the provided path.
        subprocess.CalledProcessError: If the ffprobe command fails.
        ValueError: If the output of the ffprobe command cannot be converted to a float.
    
    Returns:
        dict: Dictionary containing filename (key) and the duration in seconds(value) of each audio file. This data is then used in process_time_estimator() to calculate the time required to process the batch, relative to the model's processing speed.
    """
    
    audio_time_dict = dict.fromkeys(audio_filenames, 0)
    
    for filename in audio_filenames:
        full_path = os.path.join(path_to_audio, filename)
        cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{full_path}"'
        # NB: creates command-line string to be run, elements:
        # -v error: only error messages should be displayed
        # -show_entries format=duration: extract duration of the file
        # -of default=noprint_wrappers=1:nokey=1: removes key and wrappers from output so that it's easier to parse
        try:    
            output = subprocess.check_output(cmd, shell=True).decode('utf-8')
        except FileNotFoundError:
            msg_error = f"Error, file '{full_path}' not found."
            log_file_write(msg_error, log_path)
            raise
        except subprocess.CalledProcessError:
            msg_error = f"Error: ffprobe command failed. Check that ffprobe is installed and that the file '{full_path}' is a valid audio file."
            log_file_write(msg_error, log_path)
            raise    

        try:           
            duration = round(float(output), 2)  # duration in seconds
        except ValueError:
            msg_error = f"Error, Could not convert output to float. Check that the file '{full_path}' is a valid audio file."
            log_file_write(msg_error, log_path)
            raise

        audio_time_dict[filename] = duration
    print(audio_time_dict) # remove after testing   

    return audio_time_dict


def process_time_estimator(audio_time_dict, model_key, model_options, log_path):
    """
    Estimates the time required to process the audio files based on the chosen model's processing speed. Converts times to mins/secs format. Prints to screen (only) a summary of the time for each individual file. The final batch processing time is written to log file.

    Args:
        audio_time_dict (dict): Dictionary containing filename (key) and the duration (value) of each audio file. Provided by audio_file_durations.
        model_key (str): Key representing the chosen model from model_options dictionary.
        model_options (dict): Dictionary containing the options for different models (see user_variables.py).
        log_path (str): Full path of log file to which status messages are written.

    Interactions:
        Called by provide_pre_processing_summary in whisper_wrapper.py.

    Raises:
        KeyError: If the provided model key is not found in the model options.
        ValueError: If the speed ratio is zero.
    
    Returns:
        str: A summary of the total processing time for the batch.
    """

    try:
        speed_ratio = abs(model_options[model_key]["speed_x"])
        if speed_ratio == 0:
            raise ValueError("Speed ratio cannot be zero.")
    except KeyError as e:
        msg_error = (f"Model key '{model_key}' not found in model options.\n   Error: {e.args[0]}")
        log_file_write(msg_error, log_path)
        raise
    except ValueError as e:
        msg_error = f"Error: {e.args[0]}"
        log_file_write(msg_error, log_path)
        raise
    
    batch_est_seconds = 0
    for file in audio_time_dict:
        file_duration = audio_time_dict[file]
        file_mins = int((file_duration) / 60)
        file_secs = round(int(file_duration % 60), 2) 
        est_file_process_secs = round(file_duration / speed_ratio, 2)
        est_mins = int(est_file_process_secs / 60) 
        est_seconds = round(int(est_file_process_secs % 60), 2) 
        file_summary = (
        f"At a duration of {file_mins}min {file_secs}sec, processing '{file}'\n"
        f"with {model_options[model_key]['name']} at {speed_ratio}x is estimated to take {est_mins}min {est_seconds}sec.\n")
        log_file_write(file_summary, log_path)
        batch_est_seconds += est_file_process_secs
        print(f"Running total batch processing seconds: {batch_est_seconds}\n")
    formatted_batch_est_mins = int(batch_est_seconds/ 60)
    formatted_batch_est_seconds = round(int(batch_est_seconds % 60), 2)
    batch_summary = f"Total processing time for batch is approx {formatted_batch_est_mins}min {formatted_batch_est_seconds}sec\n"
    return batch_summary


def extract_series_episode(
        audio_file, log_path, default_series="S0", default_episode="E00"):
    """
    Extracts series and episode information from the given audio file's name when in format (i.e.) "S01E03" or "S01 E03" (series 1 episode 3). Regex accommodates any number after "S" or "E" i.e. S00001 or E01235.
    
    Args:
        audio_file (str): Name of audio file.
        default_series (str, optional): Series value inserted if no series number is found in the audio file name. Defaults to "S0". Supply blank string ="" to completely omit. 
        default_episode (str, optional): Episode value inserted if no episode number is found in the audio file name. Defaults to "E00". Supply blank string ="" to completely omit. 

    Rationale: It will be easier to search for S0 or E00 to identify transcripts with missing information, vs. just a blank field.

    Interaction: 
        Called by create_header() in whisper_wrapper.py.
        
    Returns:
        tuple: A tuple containing the extracted series and episode information.
    """
    series_regex = r"S\d+"
    episode_regex = r"E\d+"
    try: 
        series_match = re.search(series_regex, audio_file)
        episode_match = re.search(episode_regex, audio_file)

        series = series_match.group(0) if series_match else default_series
        episode = episode_match.group(0) if episode_match else default_episode
    
    except Exception as e:
        msg_error = f"Error occurred whilst extracting series and episode information from {audio_file} or whilst attempting to substitue with default values: {e}"
        log_file_write(msg_error, log_path)
        raise

    return series, episode


def insert_newlines(text, word_interval):
    """Whisper transcripts are one long line of text. This function will insert a newline character at the end of every {interval} i.e. 10 words. If 0 was chosen, no newlines will be inserted.
    
    Args:
        text (str): The raw transcript produced by Whisper (one long string).
        word_interval (int): The user-specified word interval at which to insert newlines into the transcript. Note, that check_word_interval may alter this value (substituting 0 if an invalid interval was entered, so and this potentially altered value is what is passed to master_call_loop().

    Interactions:
        Called by format_transcript().
        
    Returns:
        str: The formatted transcript with newlines inserted at the specified interval.
        """
    try: 
        if word_interval == 0:
            return text # Returns original text without any newlines
        
        words = text.split() # NB: list of individual words
        for i in range(word_interval -1, len(words), word_interval): 
            words[i] = words[i] + '\n'
        return ' '.join(words)

    except TypeError as e:
        print(f"TypeError: {e}")
        raise

    except ValueError as e:
        print(f"ValueError: {e}")
        raise