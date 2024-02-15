"""USER CHOICES"""

############# MANUAL SECTION 1 : Variables ####################

"""Choose if the program should run with (True) or without (False) a log file.
Set to False to run this script without a log file.
True will require logfile instanciation for the program to proceed (if an error prevents log file instanciation it will exit)."""
log_file_compulsory = True # True or False only

""" Specify directory path containing audio files to be transcribed. 
Path can be relative (i.e. "folder_name/") to reference root directory, or absolute if script isn't being run in same directory as the audio files.
Files in subfolders will NOT be enumerated or processed.
If the directory does not exist, program will exit with an error message."""
path_to_audio = "batch/" 


"""Specify transcript output folder (relative) or full path (absolute). Will be created if doesn't exist."""
path_for_output = "output/"

"""Specify target audio file format
Requirement: all files in processing batch must have same file extension."""
audio_format = ".WAV" # Note: include the . and make sure the case matches the actual file extension: ".wav" will not match if the files are ".WAV" 


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

# Supply the longform name of which model should be used for the transcription
# NB: supply the dictionary key ("Tiny_English"), NOT the model name ("tiny.en")
model_key = "Tiny_English" 


""" Choose word interval for line wrapping and to insert line-numbers into the final transcript.
Whisper returns transcripts which are one long string of text with no linebreaks or speaker labels. Therefore:
* Specify the interval of words at which to insert a newline into transcript, or
* Enter 0 to return the raw transcript with no line wrapping and no line numbers
* If an invalid interval is entered, 0 will be substituted.
! Important note: choosing in interval will not just wrap the lines, but will insert a line number at the start of each line in the format XX: (i.e. 12:). If you don't want line numbers, set the word interval to 0.
"""
word_interval = 10  # approx 9 - 12 is English average


"""Choose a delimiter for transcript. 
Supplying an empty string "" will not insert a delimiter."""
delimiter = "---"

""" Note about filenames
An ideal filename will be in this format, as the script will allow :
[S]eries[#][E]pisode[#] - Title.audio_format
S6E11 - Health and Safety (with Gus Baker).mp3
"""

############# MANUAL SECTION 2 : POPULATE TRANSCRIPT HEADER ####################

"""Fill in any string fields which are the same for all audio files in the batch, which should be included in each transcript's header."""

# If any fields are not required, do NOT remove them here: go to whisper_wrapper.py, create_header() and remove them by commenting out the line.

audio_info_batch = [
    {
        "participants" : [
        {"name": "", "role": ""},
        {"name": "Unknown", "role": "Interviewer"},
        ]
    },
    {
        "audio_content" : [
        {"type" : ""}, # "talk", "interview", "QandA"
        {"topic" : ""}, # e.g. "Health and Safety", "Business", "Economics"
        {"series" : ""}, # e.g. "BBC The Bottom Line"
        {"format" : ""} # e.g. "Podcast", "YouTube"
        ] 
    },
    {
        "transcript_type" : [
        {"producer" : "whisper"},
        {"model" : model_options[model_key]["name"]}
        ]
    },
]

# Populate information which varies per audio file
audio_file_info = [
    # Individualised nfo for file 1
    {
    "index" : 1, # ref = {audio_file_info[index-1]['index']}
    "date" : "2024-02-15", # ref = {audio_file_info[index-1]['date']}
    
    # NB: only need series_num and episode_num if the audio file name does not contain this information: S06 E07 can be extracted by extract_series_episode()
    "series_num" : "S6", # {audio_file_info[index-1]['series_num']}
    "episode_num" : "E7", # ref = {audio_file_info[index-1]['episode_num']}
    
    "speakers" : [
        {"name": "Evan Davies", "role": "Host"}, # Host, Speaker, Interviewer
        {"name": "Mr A", "role": "Interviewee"},
        {"name": "Mrs B", "role": "Interviewee"},
       ]
    },
    # Individualised info for file 2
    {
    "index" : 2, # ref = {audio_file_info[index-1]['index']}
    "date" : "2024-02-15", # ref = {audio_file_info[index-1]['date']}
    
    # NB: only need series_num and episode_num if the audio file name does not contain this information: S06 E07 can be extracted by extract_series_episode()
    "series_num" : "S6", # {audio_file_info[index-1]['series_num']}
    "episode_num" : "E7", # ref = {audio_file_info[index-1]['episode_num']}
    
    "speakers" : [
        {"name": "Dr Bob", "role": "Host"}, # Host, Speaker, Interviewer
        {"name": "Spongebob", "role": "Interviewee"},
        {"name": "Catty McCat", "role": "Guest"},
       ]
    }
]