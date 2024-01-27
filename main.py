""" Entry point for whisper_transcription.py """

#%% 
from whisper_transcription import master_call_single, master_call_loop
from user_variables import model_chosen

#%%
audio_filenames, model = master_call_single(model_chosen)

#%%
master_call_loop(audio_filenames, model)

# %%
