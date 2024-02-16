""" REMOVE LINE NUMBERS FROM TRANSCRIPTS """

import re
import os

# NB: relies upon the line numbers appearing at the start of a line in this format: "12: " (i.e. a number followed by a colon and a space)

# specify the directory path containing transcripts to be stripped
folder = "output/" 
format = ".txt" 
# NB: ALL the files in this folder with this file extension will be enumerated and processed!

# Creates a list of all the filenames in the folder
transcripts = [f for f in os.listdir(folder) if f.endswith(format)]
# print(transcripts)

for transcript in transcripts:
    path_to_transcript = os.path.join(folder, transcript)
    with open(path_to_transcript, "r") as file:
        transcript = file.read()

    # Split the transcript into lines
    lines = transcript.split('\n')

    # Use a regular expression to remove the line numbers
    lines_without_numbers = [re.sub(r'^\d+:\s*', '', line) for line in lines]

    # Join the lines back together into a single string
    transcript_without_numbers = '\n'.join(lines_without_numbers)

    # Write the stripped transcript back to file, replacing the original line-numbered transcript
    with open(path_to_transcript, "w") as file:
        file.write(transcript_without_numbers)
