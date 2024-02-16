""" ENTRY POINT """

from whisper_wrapper import master_call_single, master_call_loop
from user_variables import model_key, word_interval

# Calls all the functions which only need to run once, to do the pre-processing tasks for the entire batch of audio files
audio_filenames, model, word_interval = master_call_single(word_interval, model_key)

# Calls the functions which need to run for each audio file in the batch
master_call_loop(audio_filenames, word_interval, model_key, model)
