# whisper_wrapper
## Intro
This program is a simple implementation of the wonderful ✨[Whisper transcription model from OpenAI](https://github.com/openai/whisper), designed to automate the batch transcription of audio files whilst throwing in some extra formatting features along the way, before saving output as a .txt file. 

The program is a 'wrapper' around the core Whisper transcription functionality. The code is extremely simple (novice coder) and should be easy for coders of all proficiencies to understand and modify. Simply set a few variables to customise how the finished transcript will be formatted, point the script at a directory containing your audio files, and off it goes. 🐱‍🏍

[![Screenshot Sample Transcript annot](https://github.com/gorbash1370/whisper_wrapper/blob/main/misc/ss_trans_header_linenos_ann_small.png)](https://github.com/gorbash1370/whisper_wrapper/blob/main/misc/ss_trans_header_linenos_ann.png)

My fellow AI/LLM geeks 🤓 will spot the purpose of the formatting features offered. The program:
* adds in a header containing information about the file / content
* adds in word-count
* optionally adds in line numbers + line wrapping (as a pair)
* optionally adds a delimiter

Additionally:
* It calculates the estimated processing time for each file and the batch as a whole, based upon `model_chosen`.
* There's extensive logging capability (optional) and error handling.
* I've supplied a script [`remove_line_nos.py`](https://github.com/gorbash1370/whisper_wrapper/blob/main/misc/remove_line_nos.py) to quickly remove line-numbers from a batch of .txt files, if desired. 

_This was a practice Python project created for my practical use, so much of its functionality has been set to my taste. Therefore, please read the [Notes Usage](#notes-usage) section carefully for how to set its parameters to match your workflow. I built in as much variability as time would allow, before I had to re-emerge from The Code Cave this project led me into._

# Dependencies
* See the [Setup section of OpenAI's whisper README](https://github.com/openai/whisper#setup) for the original model and it's dependencies. Mostly, it involves running `pip install -U openai-whisper`, but please do read their instructions.
* As their guide describes, Whisper utilises the 'powerhouse' of [ffmpeg](https://ffmpeg.org/)❤️ so that needs to be installed.
* There is no requirements.txt because my code only uses the libraries which are required/installed as part of the Whisper installation or the standard Python libraries.


# Program structure
[`user_variables.py`](https://github.com/gorbash1370/whisper_wrapper/blob/main/user_variables.py) - user choices and parameters must be specified here  
[`utils_helper.py`](https://github.com/gorbash1370/whisper_wrapper/blob/main/utils_helper.py) - helper functions  
[`whisper_wrapper.py`](https://github.com/gorbash1370/whisper_wrapper/blob/main/whisper_wrapper.py) - utility functions. Unwanted header fields can be manually commented out in the create_header() function (explained below).  
[`main.py`](https://github.com/gorbash1370/whisper_wrapper/blob/main/main.py) - executions the program

# Other files
[`README.md`](https://github.com/gorbash1370/whisper_wrapper/blob/main/README.md) - voila!  
[`LICENCE.md`](https://github.com/gorbash1370/whisper_wrapper/blob/main/LICENCE.md) - lgpl-3.0 licence  

`issues.md` - casual project To Do list (in [`misc/`](https://github.com/gorbash1370/whisper_wrapper/tree/main/misc) folder)  
[`remove_line_nos.py`](https://github.com/gorbash1370/whisper_wrapper/blob/main/misc/remove_line_nos.py) - script to remove line numbers from the transcript, if you want to keep the newlines but remove the line numbers (in [`misc/`](https://github.com/gorbash1370/whisper_wrapper/tree/main/misc) folder)  

# Notes: Installation and Testing
* At the time of writing (24 02), OpenAi's Whisper is compatible with Python versions 3.8-3.11. 
    * If, like me, you're already on Python 3.12, you'll need to install Python 3.11 and then run  
`/full/path/to/your/python311.exe -m venv /path/to/new/virtual/environment` to create your virtual environment.
* My code has only been tested on .mp3, .wav and .mp4 files so far.
* My code was developed with Python 3.11.7 and on a Windows (10) machine. It should work on other OSs but _I have not tested this_.
* I built the code as robustly as I could, but **I have not had chance to do extensive testing**. Please do let me know what errors you find and I'll do my best to fix them.


# Start 
* Install [dependencies](#dependencies) as mentioned above
* Read the [#Notes: Usage](#notes-usage) section carefully so you understand the program quirks
* `user_variables.py` - complete all the variable values following the instructions in the comments
* Comment out any unwanted header fields in `whisper_wrapper.py`, `create_header()` function
* Run the code in `main.py`


# Notes: Usage

## Codesections Referenced:
  * `audio_file_info` and `audio_info_batch` are dictionaries in `user_variables.py`.
  * `header_parts` is a code section in `create_header()` function in `whisper_wrapper.py`
  * User choices / variables are all set in `user_variables.py`

## The Header
The program inserts a header at the top of the transcript. The header and its fields can be omitted or populated in the following ways:
  1. Completely omit the header by commenting out all lines within `header_parts`:  [![Screenshot No Header](https://github.com/gorbash1370/whisper_wrapper/blob/main/misc/ss_code_commented_out_header_thumb.png)](https://github.com/gorbash1370/whisper_wrapper/blob/main/misc/ss_code_commented_out_header.png)  
  
  In this case, the only output will be the only the unformatted transcript with a wordcount, like this:
  [![Screenshot Unformatted Transcript](https://github.com/gorbash1370/whisper_wrapper/blob/main/misc/ss_trans_no_header_small.png)](https://github.com/gorbash1370/whisper_wrapper/blob/main/misc/ss_trans_no_header_annot.png) 
  2. Omit _some_ fields by commenting out just the relevant lines in `header_parts`.
  3. To 'group-set' header fields which are the same for all the files (i.e. all the same Series or Hosted by the same person) complete the `audio_info_batch` dictionary.  
  [![Screenshot Batch Dictionaries](https://github.com/gorbash1370/whisper_wrapper/blob/main/misc/ss_code_audio_info_batch_dict_thumb.png)](https://github.com/gorbash1370/whisper_wrapper/blob/main/misc/ss_code_audio_info_batch_dict.png)  
  Values here will be inserted into the headers for _all_ the files processed. Combine with commenting out in `header_parts` any fields you don't want to appear. 
  4. **Not recommended**: manually complete individual dictionaries within `audio_file_info` to set unique file-by-file info. [![Screenshot Individual Dictionaries](https://github.com/gorbash1370/whisper_wrapper/blob/main/misc/ss_code_audio_file_info_dict_thumb.png)](https://github.com/gorbash1370/whisper_wrapper/blob/main/misc/ss_code_audio_file_info_dict.png)

    
      #### Considerations regarding `audio_file_info` dictionary use: 
      * This method is laborious.
      * Ensure the number of dictionaries matches the number of files in the input directory, else the program will throw an error.
      * Start the `index` field from 1 for the first dictionary, 2 for the second, etc.
      * Ensure the order of the dictionaries matches the order of the files in `audio_filenames` list, which is sorted alphabetically by their original filenames. This is the order in which Python will process the files.
      * Using this dictionary will require manually changing the code in `header_parts` in `create_header()` to point towards the `audio_file_info` dictionary instead of the `audio_info_batch` dictionary (latter used as default). The code to substitute to switch references is in the comments beside the `audio_file_info` dictionary entries.
      * I suppose you could paste the format of the `audio_file_info` dictionary into an LLM alongside natural language instructions for how to complete them; it might save time!

## Filenames & the Header
* Filenames should contain title of the audio track at a minimum. This will auto-populate the `Title:` field in the header.
* Ideal filename: The program includes a script to extract the series and episode number from the filename (to auto-populate the header `Series:` and `Episode:` fields), if present in this format `S<any digits> E<any digits>`. For example, if filename format is as follows:  
  
    `[S]eries[#][E]pisode[#] - Title.audio_format`  
    i.e. `S6E11 - Talking Health and Safety (with Mr Safety).mp3`  
    or `S6 E11 - Talking Health and Safety (with Mr Safety).mp3`  

    `S6` and `E11` will be extracted and inserted into `Series:` and `Episode:` respectively.
    If the filename does not follow this format or if no Series or Episode number is detected, the user can:  
    - allow the program to insert "S0" and "E00" into the header, which is the current default
    - manually enter the series and episode information through `audio_file_info` dictionaries
    - set a default value in `extract_series_episode()` in `utils_helper.py`
    - set a consistent series number in the `audio_info_batch` dictionary
    - or, you can of course also just comment out these two lines in the `header_parts` section to omit them completely (as with any other unwanted field):  
    `# f"Series#: {series} ",`  
    `# f"Episode#: {episode} ",`

## Line Numbers and Line Wrapping
* Control variable: `word_interval` in `user_variables.py`. `word_interval = 10` will insert a newline every 10 words.
* Line wrapping and line numbers are implemented as a package: if the transcript is wrapped, line numbers will also be added into the transcript.  

    _This is valuable for AI processing (saving context, compute, enhancing quality control of AI responses and making AI output verification a million times more reliable). However, line numbers will be an annoyance if you are copying and pasting quotes from the transcript text (line numbers will be scattered throughout)._  

* Line numbers can be easily omitted by setting `word_interval = 0`. Note: this will also prevent line-wrapping.
[![Screenshot Word Interval 0](https://github.com/gorbash1370/whisper_wrapper/blob/main/misc/ss_trans_no_linenos_annot_small.png)](https://github.com/gorbash1370/whisper_wrapper/blob/main/misc/ss_trans_no_linenos_annot.png)


* If you want line-wrapping at the word_interval, but want to remove the line numbers, use `word_interval` as usual. Then, run the `remove_line_nos.py` script on your .txt transcripts (in bulk). This will remove all the prependeing `##: ` from all the transcipts but preserve the newline breaks.

## File processing order
The program reads the names of all files in the `path_to_audio` directory which have an extension matching the `audio_format`. The way/order in which Python adds the filenames to the resulting list could potentially vary between OSs, and your File Explorer may be set to display files in a non-standard sort order. Therefore, the program is set to sort the extracted filenames in the `audio_filenames` list alphabetically. This is the order in which they will sent to Whisper for transcription.  

To change the transcription order of the files, you will need to rename them so that they appear alphabetically sorted in the order you want. _This is only relevant_ if you are manually completing `audio_file_info` dictionaries to populate individual transcript headers with unique values for each file. See [`.4`](#considerations-regarding-audio_file_info-dictionary-use) in #The Header section.

## Scope
* Program only processes files of one type per pass, currently. So, if your input directory contains both .mp3 and .wav files, you will need to run the script twice (updating `audio_format` as necessary), once for each file type.
* Program attempts to process _ALL_ files with the specified extension in the input path directory. It does *not* enumerate or process files in subfolders.

## Output Customisation
* `use_log_file` - use this variable to turn on/off the logging of the program's output to a file.
* `path_to_logs` - specify the path where the log file should be saved, if logging is enabled.
* `path_to_output` - specify the path where the transcripts should be saved.
* `move_processed` and `path_for_processed` - specify if you want the audio files to be moved to a different directory after processing.
* `model_options` - specify which OpenAI Whisper model you want to use for the transcription.
* `delimiter` - customise the delimiter or omit by supplying an empty string `""`
* `word interval` - customise the word interval for line wrapping and line numbers. Set to `0` to skip line-wrapping and line-numbers. See [#Line Numbers and Line Wrapping section](#line-numbers-and-line-wrapping) above.
* `header_parts` in `create_header` - customise the header fields: see [#The Header section](#the-header) above.

_Writing all the customisation steps out makes it sound like a lot, but it's actually very simple: once you have the parameters set up to your preferences it's set and forget. All you will need to change is the `audio_format` when you want to process a different file type._

# gorbash1370 Disclaimer
This is an amateur project built mainly for coding practice, therefore...
* Commentary may appear excessive (learning 'notes')
* Some code is expanded (rather than shortened & simplified) for learning clarity.
* I'm not a professional or trained Dev, so please always inspect code before running. Use at your own risk!

# Improvements (Bigger Ones) on the To Do List
- [ ] Accommodate processing of all audio files in the directory, rather than having to specify a single type/file extension.
- [ ] Create an input 'terminal program' for a more user-friendly way to enter set-up choices.
- [ ] Add a function which extracts a date from the filename (if present) and inserts it into the header "date" field.
- [ ] Create `test_whisper_transcribe.py` test file

# Licences
[Licence](https://github.com/gorbash1370/whisper_wrapper/blob/main/LICENCE.md)  
[whisperAI Licence](https://github.com/openai/whisper/blob/main/LICENSE)  
[ffmpeg Licence](https://www.ffmpeg.org/legal.html)  

# If you enjoy this project...
- If you find any bugs or errors, please do let me know.
- Please consider sending me some project feedback or any suggestions for improvement!
- [BuyMeACawfee](https://www.buymeacoffee.com/gorbash1370)

_Last code update 2024-02-16_