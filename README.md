# dl-lifecubby
A small python script to pull down pictures and videos from lifecubby.

Setup:
    cp credentials-example.json credentials.json
    vi credentials.json
    ./dl-lifecubby.py

Images and videos will be downloaded into the current directory, and
renamed based on the date and entry title.  Entries with more than one
attachment will be numbered sequentially.
