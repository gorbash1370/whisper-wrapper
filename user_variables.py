"""USER CHOICES"""

############# MANUAL SECTION 1 : Variables ####################

"""Choose if the program should run with (True) or without (False) a log file.
Set to False to run this script without a log file.
True will require logfile instanciation for the program to proceed (if an error prevents this, the program will exit)."""
use_log_file = True # True or False only

""" Use a separate folder for collecting log files? Specify the directory path if so, or leave as "" to use the same directory as the script."""
path_to_logs = "/" # supply "/" for root or a directory path. Do not use None.


""" Specify directory path containing audio files to be transcribed. 
Path can be relative (i.e. "folder_name/") to reference root directory, or absolute if script isn't being run in same directory as the audio files.
Files in subfolders will NOT be enumerated or processed.
If the directory does not exist, program will exit with an error message."""
path_to_audio = "batch/" 


"""Specify output folder (relative) or full path (absolute) for transcripts. Will be created if doesn't exist."""
path_for_output = "output/"

"""Choose if processed audio files should be moved to a new folder after transcription?"""
move_processed = True # True or False only
path_for_processed = "output/" # this can be the same as path_for_output, or a different folder. Provide a relative or absolute path. If the folder does not exist, it will be created.


"""Specify target audio file format
Requirement: all files in processing batch must have same file extension."""
audio_format = ".mp3" # Note: include the . and make sure the case matches the actual file extension: ".wav" will not match if the files are ".WAV" 


"""Choose transcription model"""
# Whisper Model Options (tiny & base 1GB VRAM, small 2GB, medium 5GB, large 10GB). Non .en are multilingual. en's are best for English.

model_options = {
    "Tiny_English": {"name": "tiny.en", "speed_x": 32, "alt_name": "tiny_en"},
    "Base_English": {"name": "base.en", "speed_x": 16, "alt_name": "base_en"},
    "Small_English": {"name": "small.en", "speed_x": 6, "alt_name": "small_en"},
    "Medium_English": {"name": "medium.en", "speed_x": 2, "alt_name": "medium_en"},
    "Tiny_Multilingual": {"name": "tiny", "speed_x": 32, "alt_name": "tiny_multi"},
    "Base_Multilingual": {"name": "base", "speed_x": 16, "alt_name": "base_multi"},
    "Small_Multilingual": {"name": "small", "speed_x": 6, "alt_name": "small_multi"},
    "Medium_Multilingual": {"name": "medium", "speed_x": 2, "alt_name": "medium_multi"},
    "Large_Multilingual": {"name": "large", "speed_x": 1, "alt_name": "large_multi"}
    }

"""Supply the longform name (dictionary key) of which model should be used for the transcription.
Supply the dictionary key ("Tiny_English"), NOT the model name ("tiny.en")
See print statements (each file) / log entry (file batch) produced by process_time_estimator() for processing time estimations."""
model_key = "Base_English" # spelling must match exactly. 


""" Choose word interval for line wrapping and to insert line-numbers into the final transcript."""
# Whisper returns transcripts which are one long string of text with no linebreaks or speaker labels. Therefore:
# Specify the interval of words at which to insert a newline into transcript, or
# Enter 0 to return the raw transcript with no line wrapping and no line numbers
# If an invalid interval is entered, 0 will be substituted.
# ! Important note: choosing in interval will not just wrap the lines, but will insert a line number at the start of each line in the format XX: (i.e. 12:). If you don't want line numbers, set the word interval to 0.
word_interval = 0  # approx 9 - 12 is English average


"""Choose a delimiter for transcript. 
Supplying an empty string "" will not insert a delimiter."""
delimiter = "---"

""" Note about filenames
An ideal filename will be in this format, as the script will allow :
[S]eries[#][E]pisode[#] - Title.audio_format
S6E11 - Health and Safety (with Gus Baker).mp3
"""

############# MANUAL SECTION 2 : POPULATE TRANSCRIPT HEADER ####################

"""OPTION 1: Populate header fields as a group.

Fill in any string fields which are the same for all audio files in the batch."""

# If any fields are not required, do NOT remove them here: go to create_header() in whisper_wrapper.py,commenting out the line beginning `f"{field_name}` which you want to omit.

audio_info_batch = [
    {
        "participants" : [
        {"name": "Evan Davis", "role": "Host"},
        {"name": "Spongebob Squarepants", "role": "Employment Expert"},
        ]
    },
    {
        "audio_content" : [
        {"type" : "Talk Show"}, # "talk", "interview", "QandA"
        {"topic" : "Employment & Business"}, # e.g. "Health and Safety", "Business", "Economics"
        {"series" : "BBC Radio 4 The Bottom Line"}, # e.g. "BBC The Bottom Line"
        {"format" : "Podcast audio"} # e.g. "Podcast", "YouTube"
        ] 
    },
    {
        "transcript_type" : [
        {"producer" : "whisper"},
        {"model" : model_options[model_key]["name"]}
        ]
    },
]

"""OPTION 2: Populate header fields which vary per audio file.

This option is laborious and NOT recommended: see the notes in README.md. By default, the create_header() function points towards the `audio_info_batch` dictionary above, so you will have to change the function to point towards the relevant key in the `audio_file_info` dictionary below. The commented code provides the alternative reference code.
"""

audio_file_info = [
    # Individualised nfo for file 1
    {
    "index" : 1, # {audio_file_info[index-1]['index']}
    "date" : "2024-02-08", # {audio_file_info[index-1]['date']}
    
    # NB: only need series_num and episode_num if the audio file name does not contain this information: S06 E07 can be extracted by extract_series_episode()
    "series_num" : "S6", # {audio_file_info[index-1]['series_num']}
    "episode_num" : "E7", # {audio_file_info[index-1]['episode_num']}
    
    "speakers" : [
        {"name": "Evan Davies", "role": "Host"}, # Host, Speaker, Interviewer
        {"name": "Mr A", "role": "Interviewee"},
        {"name": "Mrs B", "role": "Interviewee"},
       ]
    },
    # Individualised info for file 2
    {
    "index" : 2, # {audio_file_info[index-1]['index']}
    "date" : "2024-02-15", # {audio_file_info[index-1]['date']}
    
    # NB: only need series_num and episode_num if the file name does not contain this information: S06 E07 can be extracted by extract_series_episode()
    "series_num" : "S6", # {audio_file_info[index-1]['series_num']}
    "episode_num" : "E7", # {audio_file_info[index-1]['episode_num']}
    
    "speakers" : [
        {"name": "Dr Bob", "role": "Host"}, # Host, Speaker, Interviewer
        {"name": "Spongebob", "role": "Interviewee"},
        {"name": "Catty McCat", "role": "Guest"},
       ]
    }
]