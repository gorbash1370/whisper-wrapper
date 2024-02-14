
#%%
from datetime import datetime as dt
import re
from user_variables import log_file_compulsory


def log_file_write(msg, logfilename):
    """Writes a message to the log file with a timestamp."""
    print(msg)
    if log_file_compulsory == False:
        return
    else:
        formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        msg_timestamped = f"{formatted_timestamp} - " + msg
        with open(logfilename, "a") as log_file:
            log_file.write(msg_timestamped)
    


# Called by create_header
def sanitize_filename(filename):
    """Function removes characters from audio file name which may interfere with filename parsing"""
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

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