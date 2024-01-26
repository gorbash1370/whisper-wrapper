""" Entry point for whisper_transcription.py """

#%% 
from whisper_transcription import master_call_single, master_call_loop
from user_variables import model_chosen

#%%
mp3_filenames, model = master_call_single(model_chosen)

#%%
master_call_loop(mp3_filenames, model)

# %%
