# Issues
Jobs to do, Improvements, Bugs, Test Idaes


# Top Jobs

## Small
- [ ]  Amend series count to include XX of XX 
- [ ]  Amend log file so that entries for the same file don't include 2 x newlines
- [ ] Change model_options from a list to a dictionary, and include the time parameter so that it can be used in the time estimation function
- [ ]  change the mp3 variable to format agnostic name
- [ ]  Separate out the helper functions into utils_helper.py now that the code is running
- [x]  untrack scraps.py and mask individualised filenames used for testing
- [ ]  estimated processing time into the header? probably not needed
- [ ]  put a word (and token?) count into a footnote at the end of the transcript, before the delimiter. This will be crucial for AI processing.
- [ ]  allow the user to set their delimiter in user_variables
- [ ]  Count the files in the batch, print to screen. Incorporate with Time Estimator Function.

## Large
- [ ] Split up pre_processing() into sub-functions
- [ ] Make a test file
- [ ] Sanitise inputs for path_to_audio and path_for_transcripts, i.e. catch invalid names
- [ ] Function to move processed files to a 'processed' directory
- [ ] Complete all docstrings, including parameters
- [ ] Start Readme file
- [ ] Refine Exceptions, splitting out error messages
- [ ] Ensure that if a single missing or dodgy file doesn't interrupt the whole stream, and that the process will 'skip' to the next file, via good Exception handling flow for FileNotFound or a model error during the transcription.
- [ ] Time estimator function. Would have to be able to read audio file length
- [ ] Branch the code so that it can read the audio file / header details from another sources (either manual input in User Choices, or a text file maybe in a certain format). OR, maybe a better way would be to have a function which renames the files (backup first, move to backup folder) in the standardised format the program currently uses, based upon a text file or manual entry. It would be nice to remove the manual-per-file dictionary data entry from the user_variables file.

# Errors to fix
- [ ] None yet 

# Minor tweaks
- [ ]  Do something with the True Falses? like track the flag?
- [ ]  Dependencies listed in requirements.txt (TAKE OUT JUPYTER)
- [x]  main.py, whisper_transcription.py, config.py in same directory
- [ ]  make a list of accepted formats by whisper ffmpeg, in order to check that the audio_format chosen is compatible.


# Tests
- [ ]  if path_to_audio is left blank i..e path_to_audio = "". Perhaps need to set a default value, i.e. batch/
- [ ]  What happens if a file which is due to be processed is deleted during procssing of other files - does it crash the program or is it just skipped?
- [ ]  What happens if the date changes during transcription, so it goes from before midnight to afterwards. Does this cause an error regarding the logfilename being datestamped? This might be particularly important if batched processing is implemented.. or will it just create a new logfilename and carry on?


# Larger tasks
- [ ]  Allow batching of files. So enumerate the whole batch, specify a sub-batch size  / parameters, and have the loop function run across these in batches.
- [ ]  Test with audio file from dictaphone (i.e. not podcast quality)