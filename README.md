# whisper_wrapper
This is a simple implementation of the [Whisper transcription model from OpenAI](https://github.com/openai/whisper).

The program automates the supply of single or multiple audio files to a local copy of OpenAI's whisper transcription model. It adds in a header and word-count to the transcript. It optionally adds in line numbers and newline wrapping, and a delimiter. It also estimates the time to process the files and gives a cumulative time for the batch. There's extensive logging capability and error handling.


# Dependencies
See the [Setup section of OpenAI's whisper README](https://github.com/openai/whisper#setup) for the original model and it's dependencies. As their guide describes, you need to install [ffmpeg]((https://ffmpeg.org/)).

# Program structure
`user_variables.py` - user choices and parameters must be specified here
`utils_helper.py` - helper functions
`whisper_wrapper.py` - utility functions. Unwanted header fields can be manually commented out in create_header().
`main.py` -
`issues.md` - project To Do list
`test_whisper_transcribe.py` - test file 


# Notes
* At the time of writing (24 02), whisper is compatible with Python versions 3.8-3.11
* My code has only been tested on .mp3 and .wav files so far.
* My code was developed with Python 3.11.7 and on a Windows (10) machine. It should work on other OSs but I _haven't tested this_. 
* Filenames should contain title of podcast or audio track at a minimum. If the filename format is as follows:  
    `[S]eries[#][E]pisode[#] - Title.audio_format`
    e.g. `S6E11 - Talking Health and Safety (with Mr Safety).mp3`
    Then the program will automatically extract the series and episode number and title from the filename. If the filename does not follow this format, the user can manually enter the series and episode information through the audio_file_info or the audio_info_batch dictionaries in the `user_variables.py` file.
* Script attempts to process ALL files with the specified extension in the input path directory. It does NOT enumerate or process files in subfolders.


**Because this was developed as a practice Python project, much of it's functionality has been set to my taste, namely**:
* the program inserts a header into the transcript
* the header fields were set according to my use-cases. But!, they can all be easily commented out in the whisper_wrapper.py file, create_header() function.
* if the transcript is wrapped, line numbers will also be added into the transcript. This is valuable to me for AI processing and quality control of responses. I appreciate this can be annoying if you are copying and pasting quotes from the text though (line numbers scattered throughout). Currently, if you wrap, you get line numbers. 


# Start 
* requirements.txt
`user_variables.py` - fill in the variable values here following instructions in the comments


# gorbash1370 Disclaimer
This is an amateur project built mainly for coding practice, therefore...
* Commentary may appear excessive (learning 'notes')
* Some code is expanded (rather than shortened & simplified) for learning clarity.
* Please always inspect code before running. Use at your own risk!

# Improvements on the To Do List
- [ ] Add in an option to skip adding the header
- [ ] Add in an option to insert newlines but not line-numbers
- [ ] Add in an option to skip adding the word count  

# Licence
[Licence] COMPLETE ME
[whisperAI Licence](https://github.com/openai/whisper/blob/main/LICENSE)
[ffmpeg Licence](https://www.ffmpeg.org/legal.html)


### Last code update 24 02 14 """