#%%
"""USER CHOICES"""

""" Specify directory path containing audio files to be transcribed. 
Path can be relative (i.e. "folder_name/") to reference root directory, or absolute if script isn't being run in same directory as the audio files.
If the specified directory doesn't exist, it will be created.
The script will NOT enumerate or process files in subfolders"""
path_to_audio = "batch/" 


"""Specify transcript output folder / path. It will be created if doesn't exis."""
path_for_transcripts = "transcripts/"

"""Specify target audio file format
Requirement: all files in processing batch must have same file extension / file type."""
audio_format = ".mp3" # include the .


"""Choose transcription model"""
# Whisper Model Summary:
# - tiny.en: Requires ~1 GB VRAM, Speed ~32x.
# - base.en: Requires ~1 GB VRAM, Speed ~16x.
# - small.en: Requires ~2 GB VRAM, Speed ~6x.
# - medium.en: Requires ~5 GB VRAM, Speed ~2x.
# - large (Multilingual): Requires ~10 GB VRAM, Speed 1x.

model_options = ["tiny.en", "base.en", "small.en", "medium.en", "large", "tiny", "base", "small", "medium"] # non .en are multilingual. en's best for English

model_chosen = model_options[1]

"""Whisper returns transcripts which are one long string of text with no linebreaks or speaker labels, therefore:
Specify the interval of words at which to insert a newline in transcript, or
Enter 0 to return the raw transcript with no line wrapping:"""
word_interval = 10  # approx 9 - 12 is English average
# TEST - what happens if this is blank?
# TEST - need to accomodate if user doesn't want line wrapping and just leave


"""A note about filenames
An ideal filename will be in this format:
[S]eries[#][E]pisode[#] - Title.audio_format
S6E11 - Health and Safety (with Gus Baker).mp3
"""

############# MANUAL SECTION 2 : POPULATE TRANSCRIPT HEADER ####################

# Populate 'group' string fields for the transcript file 'header' (so these are the same for all the videos)
audio_info_batch = [
    {
        "participants" : [
        {"name": "Daniel Barnett", "role": "Host & Speaker"},
        # {""name": "Unknown", "role": "Interviewer"},
        ]
    },
    {
        "video_content" : [
        {"type" : "QandA"}, # talk, interview, QandA
        {"topic" : "UK Employment Law"},
        {"series" : "Employment Law Matters"},
        {"format" : "Podcast"}
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
