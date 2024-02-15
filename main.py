""" Entry point for whisper_wrapper.py """

from whisper_wrapper import master_call_single, master_call_loop
from user_variables import model_key, word_interval

audio_filenames, model, word_interval = master_call_single(word_interval, model_key)

master_call_loop(audio_filenames, word_interval, model_key, model)
