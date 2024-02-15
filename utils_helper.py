#%%
from datetime import datetime as dt
import os
import re
import subprocess
from user_variables import log_file_compulsory

def log_file_write(msg, logfilename):
    """Writes supplied message to the log file, prepended with a timestamp."""
    print(msg)
    if log_file_compulsory == False:
        return
    else:
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_timestamped = f"{formatted_timestamp} - " + msg
        with open(logfilename, "a") as log_file:
            log_file.write(msg_timestamped)
    

def sanitize_filename(filename):
    """Function removes characters from audio file name which may interfere with filename parsing

    Called by: create_header

    """
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename


def audio_file_durations(path_to_audio, audio_filenames, logfilename):
    """Extracts the duration of each audio file in the batch and returns a dictionary with the filename as the key and the duration in seconds as the value. This data is then used in the time estimator to calculate the time required to process the batch, relative to the model's processing speed.

    Dependencies: ffprobe is tool (for extracting info about media files) included with ffmpeg. ffmpeg should already be installed as OpenAi's whisper model requires it."""
    print(f"raw filenames are: {audio_filenames}") # remove after testing
    audio_time_dict = dict.fromkeys(audio_filenames, 0)
    print(f"Dictionary looks like: {audio_time_dict}") # remove after testing

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
            log_file_write(msg_error, logfilename)
            raise
        except subprocess.CalledProcessError:
            msg_error = f"Error: ffprobe command failed. Check that ffprobe is installed and that the file '{full_path}' is a valid audio file."
            log_file_write(msg_error, logfilename)
            raise    

        try:           
            duration = round(float(output), 2)  # duration in seconds
        except ValueError:
            msg_error = f"Error, Could not convert output to float. Check that the file '{full_path}' is a valid audio file."
            log_file_write(msg_error, logfilename)
            raise

        audio_time_dict[filename] = duration
    print(audio_time_dict) # remove after testing   

    return audio_time_dict


def process_time_estimator(audio_time_dict, model_key, model_options, logfilename):
    """Estimates the time required to process the audio files based on the model chosen."""
    try:
        speed_ratio = abs(model_options[model_key]["speed_x"])
        if speed_ratio == 0:
            raise ValueError("Speed ratio cannot be zero.")
    except KeyError as e:
        msg_error = (f"Model key '{model_key}' not found in model options.\n   Error: {e.args[0]}")
        log_file_write(msg_error, logfilename)
        raise
    except ValueError as e:
        msg_error = f"Error: {e.args[0]}"
        log_file_write(msg_error, logfilename)
        raise
    
    batch_est_seconds = 0
    for file in audio_time_dict:
        file_duration = audio_time_dict[file]
        file_mins = int((file_duration) / 60)
        file_secs = round(int(file_duration % 60), 2) #) / 100) * 60)
        est_file_process_secs = file_duration / speed_ratio
        est_mins = int(est_file_process_secs / 60) 
        est_seconds = round(int(est_file_process_secs % 60), 2) #) / 100) * 60)
        file_summary = (
        f"At a duration of {file_mins}m{file_secs}, processing '{file}'\n"
        f"with {model_options[model_key]['name']} at {speed_ratio}x is estimated to take {est_mins} minutes, {est_seconds} seconds.\n")
        log_file_write(file_summary, logfilename)
        batch_est_seconds += est_file_process_secs
        print(f"Running total batch processing seconds: {batch_est_seconds}\n")
    formatted_batch_est_mins = int(batch_est_seconds/ 60)
    formatted_batch_est_seconds = round(int(batch_est_seconds % 60), 2)
    batch_summary = f"Total processing time for batch is approx {formatted_batch_est_mins}min {formatted_batch_est_seconds}sec."
    print(batch_summary)
    return batch_summary


# Called by create_header
def extract_series_episode(
        audio_file, default_series="S0", default_episode="E00"):
    """
    Extracts series and episode information from the given audio file's name when in format (i.e.) "S01E03" (series 1 episode 3). Regex accommodates any number series after "S" or "E" i.e. S00001 or E01235.

    Rationale: it will be easier to search for S0 or E00 to identify transcripts with missing information, rather than just leaving the field blank.
    
    Args:
        audio_file (str): Name of audio file.
        default_series (str, optional): Series value inserted if no series number is found in the audio file name. Supply blank string "" to completely omit. Defaults to "S0".
        default_episode (str, optional): Episode value inserted if no episode number is found in the audio file name. Supply blank string "" to completely omit. Defaults to "E00".

    Returns:
        tuple: A tuple containing the extracted series and episode information.
    """
    series_regex = r"S\d+"
    episode_regex = r"E\d+"

    series_match = re.search(series_regex, audio_file)
    episode_match = re.search(episode_regex, audio_file)

    series = series_match.group(0) if series_match else default_series
    episode = episode_match.group(0) if episode_match else default_episode

    return series, episode

