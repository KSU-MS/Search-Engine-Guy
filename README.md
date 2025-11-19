<h2>Search Engine Guy Readme:</h2>

<h3>General Stuff:</h3>

Ok, so here's some vocab for this code so I don't have to make comments for every variable:

 *   chunks are what are thrown into "documents.json". each document is split into chunks
    for faster searching.

*   overlap is the amount of words at the end of one chunk that appear at the beginning of
    another, this is an attempt to capture more context in oone chunk so that if an AI summarizes
    it, there's (hopefully) more info for it to go off of.

Now some notes:

*   yes i'm aware that json files arent the best option for storing an entire database of stuff,
    but i didnt want to learn mongo or some other bullshit so if you're mad about it, take
    the L.

*   the team's formality and everyone's writing style varies so much that any AI that will
    summarize any of this is going to make mistakes. a lot of them
---

<h3>Usage:</h3>

1. Run the "autoinstall.sh" file. If we're installing this on a non debian distro/windows then just copy the pip command and install the other dependencies as needed. 

2. Edit "ingest.py" to include the directory of files to be ingested. Currently anything other than a .pdf is ignored. PLEASE seperate your data into the desired folders, thats part of how the search algorith works.

3. Run "ingest.py" (this will take a while)

4. Run "search.py" once ingest is finished.

---

insert witty/snarky comment here, creatively tell user to go fuck themselves

---
   
Also most of this code was written at ungodly times, so if I accidentally import the json module
twice or something, give me a break

-Nick