import re

transcript = """
1: ---
2: Filename: 24 01 26 Daniel Miessler Interview snippet p2.WAV
3: Content creation date: Unknown
4: Series: 
5: Series#: S0 
6: Episode#: E00 
7: Transcription Producer: whisper
8: Transcription Model: tiny.en
9: Series Batch process order: 3
10: 
11: You put it online and now it is from the
12:  moment it goes live, it just starts degrading and breaking
13:  until the point where you actually notice that, oh hey,
14:  this is unusable. And I like to think about even
15:  a small corporate network that works that way, that it's
16:  a machine that's been put in place, it's running, but
17:  it's going to start breaking the moment it comes online.
18:  So you're just doing constant preventative maintenance and it can
19:  usually correct the maintenance to keep that thing and it's
20:  optimum operating state. Yeah, that makes sense. Yeah, I really
21:  do see it as a combination of asset management and
22:  state management and the combination of those two actually include
23:  patch management to your point. It's really interesting that you
24:  started out as patching and now you're more broad but
25:  inclusive still with patching because state management is patching as
26:  well. Yeah, absolutely. And that's it.
27: Word count: 186
28: ---
"""

# Split the transcript into lines
lines = transcript.split('\n')

# Use a regular expression to remove the line numbers
lines_without_numbers = [re.sub(r'^\d+:\s*', '', line) for line in lines]

# Join the lines back together and print the result
print('\n'.join(lines_without_numbers))