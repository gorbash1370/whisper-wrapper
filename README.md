# whisper_wrapper
This is a simple implementation of the wonderful [Whisper transcription model from OpenAI](https://github.com/openai/whisper). It is just a wrapper around Whisper and the magic of [ffmpeg](https://ffmpeg.org/); simply a good starting point for anyone who wants to automate the batch transcription of audio files. The code is extremely simple (novice coder) and should be easy for anyone to understand and modify. 

The program automates the supply of single or multiple audio files to OpenAI's whisper transcription model. It calculates the estimated processing time for each file and the batch as a whole, based upon `model_chosen`. It adds in a header and word-count to the transcript. There's an option to add in line numbers + line wrapping (as a pair), and to add a delimiter. (I've supplied a script in [`remove_line_nos.py`](www.github.com/gorbash1370/whisper_wrapper/misc) to quickly remove line-numbers if desired). The program also estimates the time to transcribe the files and gives a cumulative time for the batch. There's extensive logging capability and error handling.

_Because this was developed as a practice Python project, much of it's functionality has been set to my taste, so please read the [Notes Usage](https://github.com/gorbash1370/whisper_wrapper#Notes_Usage) section carefully._

# Dependencies
See the [Setup section of OpenAI's whisper README](https://github.com/openai/whisper#setup) for the original model and it's dependencies.
As their guide describes, you need to install [ffmpeg](https://ffmpeg.org/).
I've tried to use as few external libraries as possible.

# Program structure
`user_variables.py` - user choices and parameters must be specified here
`utils_helper.py` - helper functions
`whisper_wrapper.py` - utility functions. Unwanted header fields can be manually commented out in the create_header() function.
`main.py` - executions the program

# Other files
`README.md` - voila!
`LICENCE.md` - licence information
`requirements.txt` - list of dependencies for pip install

## in /misc
`issues.md` - casual project To Do list
`remove_linenos.py` - script to remove line numbers from the transcript, if you want to keep the newlines but remove the line numbers
~~`test_whisper_transcribe.py` - test file~~ (not yet created)


# Notes: Installation and Testing
* At the time of writing (24 02), OpenAi's Whisper is compatible with Python versions 3.8-3.11
* My code has only been tested on .mp3, .WAV and .mp4 files so far.
* My code was developed with Python 3.11.7 and on a Windows (10) machine. It should work on other OSs but I _have not tested this_.

# Notes: Usage
![www.github.com/gorbash1370/whisper_wrapper/misc/screenshot_sample_transcript_header_linenos.PNG]
## File processing order
The program reads the names of all the files which have an extension matching the `audio_format` variable in `user_variables.py`, in the `path_to_audio` directory. The way/order in which Python adds the filenames to the resulting list this could potentially vary between operating systems, and your File Explorer may be set to display files in a non-standard sort order. Therefore, the program is set to sort the extracted filenames in the `audio_filenames` list alphabetically. This is the order in which they will be transcribed. If you want to change the transcription order of the files, you will need to rename them so that they appear alphabetically sorted in the order you want. This is only relevant if you are manually completing `audio_file_info` dictionaries in `user_variables.py` to populate individual transcript headers with unique header values file by file. See [`.4`](####Considerations) in `The Header` section below.

* Control sections Referenced:
  * `audio_file_info` and `audio_info_batch` are dictionaries in `user_variables.py`.
  * `header_parts` is a code section in `create_header()` function in `whisper_wrapper.py`

## The Header
At present, **the program inserts a header at the top of the transcript**. The header and it's fields can be omitted or populated in the following ways:
  1. Completely omit the header by commenting out all lines within the `header_parts`.  
  [Screenshot](www.github.com/gorbash1370/whisper_wrapper/misc/screenshot_commented_out_header.PNG.png)
  In this case, the only output will be the [transcript with a wordcount](www.github.com/gorbash/whisper_wrapper/misc/screenshot_no_header.png)
  2. Omit some fields by commenting out the relevant lines in `header_parts`.
  3. Complete the `audio_info_batch` dictionary in `user_variables.py`. Information here will be inserted into the header for _all_ the files processed. Useful for a batch of files all sharing the same info (i.e. all the same Series or Hosted by the same person). Combine with commenting out in `header_parts` any fields you don't want to appear. [Screenshot](www.github.com/gorbash/whisper_wrapper/misc/screenshot_audio_info_batch_dict.PNG)
  4. Not recommended: manually complete individual dictionaries within `audio_file_info` dictionary in the `user_variables.py` file for unique file by file info. [Screenshot](www.github.com/gorbash/whisper_wrapper/misc/screenshot_audio_file_info_dict.PNG)
    #### Considerations re `audio_file_info` dictionary use: 
      * This method is laborious.
      * Ensure the number of dictionaries matches the number of files in the input directory, else the program will throw an error.
      * Start the `index` field from 1 for the first dictionary, 2 for the second, etc.
      * Ensure the order of the dictionaries matches the order of the files in `audio_filenames` list, which is sorted alphabetically by their original filenames. The is the order Python will process the files in.
      * Requires manually changing the code in `header_parts` in `create_header()` to point towards the `audio_file_info` dictionary instead of the `audio_info_batch` dictionary (left as default). The code to use is in the comments beside the fields in `audio_file_info`.

## Filenames & the Header
* Filenames should contain title of the audio track at a minimum. This will auto-populate the `Title:` field in the header.
* Ideal filename: The program includes a script to extract the series and episode number from the filename (to auto-populate the header `Series:` and `Episode:` fields), if present in this format `S<any digits> E<any digits>`. For example, if filename format is as follows:  
    `[S]eries[#][E]pisode[#] - Title.audio_format`
    i.e. `S6E11 - Talking Health and Safety (with Mr Safety).mp3`
    or `S6 E11 - Talking Health and Safety (with Mr Safety).mp3`
    `S6` and `E11` will be extracted and inserted into `Series:` and `Episode:` respectively.
    If the filename does not follow this format, the user can manually enter the series and episode information through `audio_file_info` dictionaries, set a default value in `extract_series_episode()` in `utils_helper.py` or set a consistent series number in the `audio_info_batch` dictionary.
    * If no Series or Episode number is detected, the program will insert "S0" and "E00" into the header. To turn this off, manually comment out these two lines in the `header_parts` section:
    ```# f"Series#: {series} ",
       # f"Episode#: {episode} ",```

## Line Numbers and Line Wrapping
* Control variable: `word_interval` in `user_variables.py`
* Line wrapping and line numbers are implemented as a package: if the transcript is wrapped, line numbers will also be added into the transcript.
    *_This is valuable to me for AI processing (saving context, compute, enhancing quality control of AI responses and making AI output verification a million times more reliable). However, line numbers will be an annoyance if you are copying and pasting quotes from the transcript text (line numbers will be scattered throughout)._
* Line numbers can be easily omitted by setting `word_interval = 0`. Note: this will also prevent line-wrapping.
* If you want line-wrapping at the word_interval, but want to remove the line numbers, use word_interval as usual. Then, run the `remove_line_nos.py` script in `/misc` on your transcripts (in bulk). This will remove all the prependeing `##: ` from all the transcipts but preserve the newline breaks.

## Scope
* Program only processes files of one type per pass, currently. So, if your input directory contains both .mp3 and .wav files, you will need to run the script twice (updating `audio_format` as necessary), once for each file type.
* Program attempts to process _ALL_ files with the specified extension in the input path directory. It does NOT enumerate or process files in subfolders

## Output Customisation
* `use_log_file` - use this variable to turn on/off the logging of the program's output to a file.
* `path_to_logs` - specify the path where the log file should be saved.
* `path_to_output` - specify the path where the transcripts should be saved.
* `move_processed` and `path_for_processed` - specify if / where you want the audio files to be moved to a different directory after processing.
* `model_options` - specify which OpenAI Whisper model you want to use for the transcription.
* `delimiter` - customise the delimiter or omit by supplying an empty string `""`
* and `word interval` - customise the word interval for line wrapping and line numbers. See [##Line Numbers and Line Wrapping] above.
* `header_parts` in `create_header`- customise the header fields: see [##The Header section] above.

# Start 
* Install dependencies as mentioned above
* `pip install -r requirements.txt` - install the required packages
* Please read the #Notes: Usage section above carefully so you understand some of the quirks of the program
* `user_variables.py` - complete all the variable values following comment instructions
* Comment out any unwanted header fields in `whisper_wrapper.py` - `create_header()` function
* Run the code in `main.py`


# gorbash1370 Disclaimer
This is an amateur project built mainly for coding practice, therefore...
* Commentary may appear excessive (learning 'notes')
* Some code is expanded (rather than shortened & simplified) for learning clarity.
* Please always inspect code before running. Use at your own risk!


# Improvements on the To Do List
- [ ] Add in an option to skip adding the header
- [ ] Add in an option to insert newlines but not line-numbers
- [ ] Add in an option to skip adding the word count 
- [ ] Accommodate processing of all audio files in the directory, rather than having to specify a single type/file extension.
- [ ] Create an input 'terminal' prompt for the user to enter the program user choices. This would be a more user-friendly way to input the variable values.

# Licence
[Licence] COMPLETE ME
[whisperAI Licence](https://github.com/openai/whisper/blob/main/LICENSE)
[ffmpeg Licence](https://www.ffmpeg.org/legal.html)

# If you enjoy this project...
- Please consider sending me some feedback or a suggestion for improvement!
- [BuyMeACoffee](https://www.buymeacoffee.com/gorbash1370)

_Last code update 2024-02-16_