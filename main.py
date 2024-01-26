""" Entry point for whisper_transcription.py
Requirements: 
* dependencies listed in requirements.txt (TAKE OUT JUPYTER)
* main.py, whisper_trasncription.py, config.py in same directory
"""


############# MANUAL SECTION 1 ####################
""" Specify directory path containing audio files to be transcribed. 
Can be relative (i.e. "folder_name/") to reference root directory, or absolute if script isn't being run in same directory as audio files.
If the specified directory doesn't exist, it will be created."""
path_to_audio = "batch/" 
# TEST what happens if do = ""

"""Specify transcript output folder / path. It will be created if doesn't exis."""
path_for_transcripts = "transcripts/"

"""Specify target audio file format
Requirement: all files in processing batch must have same file extension / file type."""
audio_format = ".mp3" # include the .
# TEST what happens with different format: look at whisper docuemtnation, does it specify just mp3

"""Choose transcription model"""
# Whisper Model Summary:
# - tiny.en: Requires ~1 GB VRAM, Speed ~32x.
# - base.en: Requires ~1 GB VRAM, Speed ~16x.
# - small.en: Requires ~2 GB VRAM, Speed ~6x.
# - medium.en: Requires ~5 GB VRAM, Speed ~2x.
# - large (Multilingual): Requires ~10 GB VRAM, Speed 1x.

model_options = ["tiny.en", "base.en", "small.en", "medium.en", "large", "tiny", "base", "small", "medium"] # non .en are multilingual. en's best for English

model_chosen = model_options[2]

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