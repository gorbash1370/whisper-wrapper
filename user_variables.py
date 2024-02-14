#%%
"""USER CHOICES"""

"""Run this script without a log file, or log inspite of log file not being able to be instantiated"""
log_file_compulsory = True

""" Specify directory path containing audio files to be transcribed. 
Path can be relative (i.e. "folder_name/") to reference root directory, or absolute if script isn't being run in same directory as the audio files.
Files in subfolders will NOT be enumerated or processed.
If the directory does not exist, program will exit with an error message."""
path_to_audio = "batch/" 


"""Specify transcript output folder (relative) or full path (absolute). Will be created if doesn't exist."""
path_for_transcripts = "transcripts/"

"""Specify target audio file format
Requirement: all files in processing batch must have same file extension."""
audio_format = ".WAV" # include the .


"""Choose transcription model"""
# Whisper Model Options (tiny & base 1GB VRAM, small 2GB, medium 5GB, large 10GB). Non .en are multilingual. en's are best for English.

model_options = {
    "Tiny_English": {"name": "tiny.en", "speed_x": 32},
    "Base_English": {"name": "base.en", "speed_x": 16},
    "Small_English": {"name": "small.en", "speed_x": 6},
    "Medium_English": {"name": "medium.en", "speed_x": 2},
    "Tiny_Multilingual": {"name": "tiny", "speed_x": 32},
    "Base_Multilingual": {"name": "base", "speed_x": 16},
    "Small_Multilingual": {"name": "small", "speed_x": 6},
    "Medium_Multilingual": {"name": "medium", "speed_x": 2},
    "Large_Multilingual": {"name": "large", "speed_x": 1}
    }

# Choose the model from the list above. Requires vale in "name" key.
model_chosen = model_options["Tiny_English"]["name"]

"""Whisper returns transcripts which are one long string of text with no linebreaks or speaker labels, therefore:
Specify the interval of words at which to insert a newline in transcript, or
Enter 0 to return the raw transcript with no line wrapping:"""
word_interval = 10  # approx 9 - 12 is English average
# TEST - what happens if this is blank?
# TEST - need to accomodate if user doesn't want line wrapping and just leave

"""Choose a delimiter for transcript. Empty string "" will not insert a delimiter."""
delimiter = "---"

""" Note about filenames
An ideal filename will be in this format:
[S]eries[#][E]pisode[#] - Title.audio_format
S6E11 - Health and Safety (with Gus Baker).mp3
"""

############# MANUAL SECTION 2 : POPULATE TRANSCRIPT HEADER ####################

# Populate 'group' string fields for the transcript file 'header' (so these are the same for all the videos)
audio_info_batch = [
    {
        "participants" : [
        {"name": "", "role": ""},
        # {""name": "Unknown", "role": "Interviewer"},
        ]
    },
    {
        "audio_content" : [
        {"type" : ""}, # talk, interview, QandA
        {"topic" : ""},
        {"series" : ""},
        {"format" : ""}
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
# audio_file_info = [
#     {
#     "audio_file_num" : index, # don't need this, from index
#     "audio_title": filename,
#     "date" : "Unknown", # ref = {audio_file_info[index-1]['date']}
#     "series_num" : "S6", # {audio_file_info[index-1]['series_num']}
#     "episode_num" : "E7", # ref = {audio_file_info[index-1]['episode_num']}
    
#     "speakers" : [
#         {"name": "Daniel Barnett", "role": "Host"} # Host, Speaker, Interviewer
#         {"name": "Unknown", "role": "Interviewer"},
#        ]
#     }
# ]
# %%
