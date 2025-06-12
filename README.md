## Requirements:
python
none
an ansi-capable terminal for colored text is recommended 

## just want to test it?
if you run `py reader.py` even before building the indexed folder, it will open `test.json`, which is included as an example. 


# Instructions:

clone this repo

create two folders, `claude_convos/source` and `claude_convos/convos`

place your Anthropic data export conversations.json as-is into the /source folder (which can be requested here: https://claude.ai/settings/data-privacy-controls)
    - You can move the other two files or delete them, they are not used or needed, and contain PII

run `py splitter.py`

it will split your conversations.json into each conversation, and then index them. 
it will also create an index file, which is used for the reader's menus. 
this only has to be done once (or anytime you process a new conversations.json).

run `py reader.py`

and it will explain itself

enjoy



## features

truncating messages: if your messages are sometimes really long, you can choose to unfurl them or not, which may save time in finding the right passages 
customizable user/ai names: change the header names, basically
[f]ind function: a fuzzy text search, you can type in a word and it will try to find entries as close to it as possible. NOT an interpretive search, it's just looking for close diff matches
lightweight: very lightweight and simple to use, I made this because the website kept crashing on long conversations I wanted to go back and read especially when there are a lot of attachments

## issues

no attachments are shown, since they're not in the conversations.json
some formatting may be off