""" Entry point for whisper_transcription.py """

#%%
from whisper_transcription import master_call_single, master_call_loop
from user_variables import model_chosen, word_interval

#%%
audio_filenames, model, word_interval = master_call_single(word_interval, model_chosen)

#%%
master_call_loop(audio_filenames, model, word_interval)

# %%
