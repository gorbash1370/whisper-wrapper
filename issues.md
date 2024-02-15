# Issues
Jobs to do, Improvements, Bugs, Test Idaes


# Top Jobs

## Small
- [ ]  return statements have been included in most functions as a default. Go through and mremove any that aren't necessary.
- [ ]  Amend series count to include XX of XX  
- [ ]  Dependencies listed in requirements.txt (TAKE OUT JUPYTER)
- [ ]  make a list of accepted formats by whisper ffmpeg, in order to check that the audio_format chosen is compatible. This may tie in with being able to accomodate multiple audio file formats in one batch.
- [ ]  End: remove Jupyter code sections

## Large
- [x] Split up pre_processing() into sub-functions
- [ ] Time estimator function. Would have to be able to read audio file length
  - [ ]  create a read of each file length using pydub, and use that to give an estimated processing time relative to the model chosen.
  - [ ]  Count the files in the batch, print to screen. Incorporate with Time Estimator Function.
  - [ ]  if manage to batch files, can then use the processing time to give batch cumulative processing time
- [ ] Accomodate all matching audio files within directory rather than having to specify
- [ ] Make a test file
- [ ] Sanitise inputs for path_to_audio and path_for_transcripts, i.e. catch invalid names
- [ ] Function to move processed files to a 'processed' directory
- [ ] Complete all docstrings, including parameters
- [ ] Start Readme file
- [ ] Refine Exceptions, splitting out error messages
- [ ] Ensure that if a single missing or dodgy file doesn't interrupt the whole stream, and that the process will 'skip' to the next file, via good Exception handling flow for FileNotFound or a model error during the transcription.



## Errors to fix
- [x] Creation of a log file is essential for the program to run. This isn't necessarily the correct priority - the program should probably run even without a log file. Especially given that error messages are printed to screen as well as being written to log text. Would involve putting an exception around every interaction with log file though! Optionality implemented.
- [ ] 


## Tests
- [ ]  What happens if a file which is due to be processed is deleted during procssing of other files - does it crash the program or is it just skipped?
- [ ]  What happens if the date changes during transcription, so it goes from before midnight to afterwards. Does this cause an error regarding the logfilename being datestamped? This might be particularly important if batched processing is implemented.. or will it just create a new logfilename and carry on?
- [ ]  test if input and output folder are set to the same
- [ ]  Test with different file formats. Successful file types: mp3, .wav
- [x]  Blank delimiter 
- [x]  Blank Series & Episode information
- [x]  blank string word interval. Correctly subsitutes 0.
- [x]  0 word interval
- [x]  invalid word interval i.e. four. Tested, substitutes 0 correctly.
- [x]  invalid path_to_audio. Correct error message displays and exits
- [ ]  no path_to_audio
- [x]  invalid path_for_transcripts. Correct error message displays and exits
- [ ]  no path_for_transcripts
- [ ]  invalid audio_format
- [ ]  invalid model

## Later / Maybe One Day
- [ ]  Allow batching of files. So enumerate the whole batch, specify a sub-batch size  / parameters, and have the loop function run across these in batches.
- [ ] Branch the code so that it can read the audio file / header details from another sources (either manual input in User Choices, or a text file maybe in a certain format). OR, maybe a better way would be to have a function which renames the files (backup first, move to backup folder) in the standardised format the program currently uses, based upon a text file or manual entry. It would be nice to remove the manual-per-file dictionary data entry from the user_variables file.
---

# Completed

## Small
- [x]  Separate out the helper functions into utils_helper.py now that the code is running.
- [ ]  
- [x]  put a word count into a footnote at the end of the transcript, before the delimiter. This will be crucial for AI processing.
- [x]  allow the user to set their delimiter in user_variables
- [x]  Tested WAV format
- [x]  Do something with the True Falses? like track the flag? Used to trigger sys.exit (for the one-time functions only)
- [x]  main.py, whisper_transcription.py, config.py in same directory
- [x]  Decide if the word interval 10 should be enforced, or if 0 should be used instead to just give the raw transcript... probably the latter. Changed to 0/raw transcipt.
- [x]  Test with blank delimiter and blank Series & Episode information
- [x]  Implement log_file_compulsory = True
- [x]  Amend log file so that entries for the same file don't include 2 x newlines
- [x] Change model_options from a list to a dictionary, and include the time parameter so that it can be used in the time estimation function
- [x]  change the mp3 variable to format agnostic name
- [x]  untrack scraps.py and mask individualised filenames used for testing
- [ ]  ~~estimated processing time into the header? probably not needed~~
- [ ]  
- [x] If path_to_audio is left blank i..e path_to_audio = "". Perhaps need to set a default value, i.e. batch/. No, this will be unique to the file system. It is reasonable to expect the user to input the path to the audio files, and exit if not.
- [x]  Refactor print statements and log interactions into single helper function
- [x]  Test new refactored log function, testing for consistency in output
- [x]  Check if "Directory contains...." log file entry contains timestamps for each filename or just one at the beginning of the log entry. Ideally should be the latter.

## Large
- [x]  Test with audio file from dictaphone (i.e. not podcast quality). WAV ok.
- [x] Catch errors in path_to_audio and path_for_transcripts (i.e. reject and exit)

## Errors to fix


## Tests


## Larger tasks