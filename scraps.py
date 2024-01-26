# %%
# Suggested rework of pre_processing()

def pre_processing(path_to_audio, path_for_transcripts, logfilename, audio_format, word_interval, model_chosen, model_options):
    formatted_timestamp = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
    error_msg = ""

    # Check if the user supplied directory path exists
    if not os.path.exists(path_to_audio):
        error_msg = f"{formatted_timestamp} - Error, specified directory does not exist.\n"
    else:
        # Create the output directory path for transcripts if doesn't exist
        if not os.path.exists(path_for_transcripts):
            os.makedirs(path_for_transcripts)

        # Check for the presence of audio files
        try:
            mp3_filenames = [f for f in os.listdir(path_to_audio) if f.endswith(audio_format) and os.path.isfile(os.path.join(path_to_audio, f))]
            if not mp3_filenames:
                error_msg = f"{formatted_timestamp} - Error, no files of type {audio_format} found in {path_to_audio}.\n"
        except FileNotFoundError:
            error_msg = f"{formatted_timestamp} - Error, directory not found: {path_to_audio}\n"
        except PermissionError:
            error_msg = f"{formatted_timestamp} - Error, permission denied for directory: {path_to_audio}\n"
        except OSError as e:  # General catch-all for other OS-related errors
            error_msg = f"{formatted_timestamp} - OS error occurred: {e}\n"

    # Check if word interval entered is a positive integer
    try:
        word_interval = abs(int(word_interval))
    except ValueError:
        word_interval = 10  # Default value

    # Check if the chosen model is valid
    if model_chosen not in model_options:
        error_msg += f"{formatted_timestamp} - Error, invalid model chosen. Please reselect.\n"

    if error_msg:
        with open(logfilename, "a") as log_file:
            log_file.write(error_msg)
        print(error_msg)
        return False

    # If everything is fine, proceed
    with open(logfilename, "a") as log_file:
        summary = f"{formatted_timestamp} - Summary of transcription parameters - Input Path: {path_to_audio} - Output Path: {path_for_transcripts} - Audio format: {audio_format} - Newline interval: {word_interval} words - Transcription Model: {model_chosen}\n"
        log_file.write(summary)

    print(f"Please make sure you are happy with this summary of processing:\n{summary}\nAbort if any parameters are incorrect. A large batch of files and/or using the largest models will take significant time and compute.")
    time.sleep(5)
    return True

# Example usage
# pre_processing(path_to_audio, path_for_transcripts, logfilename, audio_format, word_interval, model_chosen, model_options)


#%% 
# Alternative filename processing errror
try:
    mp3_filenames = [f for f in os.listdir(path_to_audio) if f.endswith(audio_format) and os.path.isfile(os.path.join(path_to_audio, f))]
    if not mp3_filenames:
        error_msg = f"{formatted_timestamp} - Error, no files of type {audio_format} found in {path_to_audio}.\n"
except FileNotFoundError:
    error_msg = f"{formatted_timestamp} - Error, directory not found: {path_to_audio}\n"
except PermissionError:
    error_msg = f"{formatted_timestamp} - Error, permission denied for directory: {path_to_audio}\n"
except OSError as e:  # General catch-all for other OS-related errors
    error_msg = f"{formatted_timestamp} - OS error occurred: {e}\n"


#%%
#         try:
#     # Your code to write file
# except FileNotFoundError:
#     print("The specified directory does not exist and could not be created.")
# except PermissionError:
#     print("You do not have permission to write to the specified directory.")
# except OSError as e:
#     print(f"OS error occurred: {e}")
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")



#%%
        # except Exception as e:
#     error_msg = ""
#     with open(log_file)
#     return False

#%%
"""# Create a list comprehension to filter and list files
mp3_filenames = [
    f  # Take each file name 'f'
    for f in os.listdir(input_path)  # Iterate over each file and directory name in the specified path
    if f.endswith('.mp3')  # Check if the file name ends with '.mp3' (to filter only MP3 files)
    and os.path.isfile(os.path.join(input_path, f))  # Check if the path represents a file (not a directory)
    # os.path.join(input_path, f) constructs the full path for each file.
    # This is necessary because os.listdir returns only file or directory names, not their full paths.
]# mp3_files now contains a list of all .mp3 files in the specified directory"""

