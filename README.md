# pyTrad -- Tools for a trad musician 

This Project is using data from a community driven website for traditional Irish music.

https://thesession.org/

in which users can submit their transcriptions of tunes in '.abc' format.

My goal is to make use of the rich source of information to augment a user's ability to find tunes they would like to play, and also as an academic study of the present-day distribution of tunes.

In the future work could be extended to other databases with focuses different than
Irish music.

The tasks for this code base are roughly divided by the type of information being used.

1. Information extracted directly from the '.abc' sheetmusic notation for the tunes in the DB.

2. Metadata associated with those tunes, or extracted from discussion text associated with the tunes. 

In this notbook I am focusing on (1), for details on (2) see 'web_scraper.ipynb'.

### Digitizing the tune from .abc

The sheet-music based tasks I am addressing with this codebase are achieved using a digitized version of the tune which stores the pitch information in arrays with integer values corresponding to the given semitone. The notes are discretized, so that each 

The intent is to be able to search for and compare tunes in cases where only portions of the tunes might be known, and the musical key for which the tune is stored in the database is not known.

This will be an approvement over previous reverse tune finders I have used as you will be able to specifically include measure structure avoiding false positives in cases that include a similar series of notes, but with a different measure structure.

The code for translating from the plain text '.abc' format to array based digitized form is in 'digitizedTune.py'

In addition to a 'digitizedTune' class, I also define and 'Interval' class, that behaves similarly, but looks at either differences between two different tune portions, or the location of the jumps and skips in a single piece of music.

For some basic '.abc' parsing tasks I make use of the pyabc library https://github.com/campagnola/pyabc, with minor modifications. 

### Creating a uniform tune structure

Musical notation can include many diverse features. Luckily, most trad tunes follow a fairly simple structures. Nonetheless some simplification must be taken to make different tunes directly comparable. I apply these simplifications on the '.abc' 

'tune_structure.py' collects code that is designed to take the original '.abc' sheet music and edit it to fit a standard format prior to digitizing it.

The main function for doing this is 'parseStructure'

Repeat patterns are a common divergence point for similar and related tunes. As such parsStructure calls functions which detect and store the repeat patter, and then return an abc with all of the repeats completely expanded. This means that each measure that is played is written out, even when it is an exact repeat.

I also standardize triplets in a way that allows their duration to be digitized into an even duration. This facilitates comparison even thought it isn't 100% correct from a music theory standpoint.

### Web-scraping User Profile Information

This Project is using data from a community driven website for traditional Irish music

https://thesession.org/

in which users can submit tunes in '.abc' format.

The websights designer kindly provides portions of the website database in a json format

https://github.com/adactio/TheSession-data

which includes:

- Tune settings (submitted by users)
- Recordings of tunes (which are cross-referenced against tune settings)
- Aliases of tunes (traditional tunes are referred to by different names)
- Sessions and Events (posted by users)

This forms the initial basis of the of the SQL-based database defined in thesessionDB.py 

However the site has additional information that I am interested in using.

Namely the users have the option of providing a location

https://thesession.org/members/97793

which we can then link to their saved tunes

https://thesession.org/members/97793/tunebook

And tunes for which they have submitted settings

https://thesession.org/members/97793/tunes

Scapeing code is located scraper.py

I plan to aggregate this information and link it with the existing the existing thesessionDB.

### SQL-based database

Defines an sqlite database, built from the json-based data dumps provided at 'https://github.com/adactio/TheSession-data'.

Tables are included for:

- Users
- Tunes
- Settings
- Aliases
- Recordings
- Recorded Tunes
- Events
- Sessions

Fields are added to the database from additional scraped directly from thesession.org, using the sites api, and from information consolidated by this codebase.

I plan to extend the database class with a variety of pythonic seach functions wrapping SQL queries for specific needs from other parts of the code.

# Planned functionality

### Tune recommender

One future goal of this work is to create a tune recommend to do one of a possible different things.

- Recommend tunes that a musician might light based on a set of tunes they know/like.

- Recommend tunes that might fall into a style based on a set of recorded tunes.

- Suggest tunes that might be historically related.

- Suggest tunes that might fit together in a set.

To achieve this in ML framework we want a variety of features, both from the raw sheetmusic and from metadata for the tune. Below I look at some possible features for quantifying the shape of an individual tune.

### Proposed goals for location information
Here are a number of possibilities to use this kind of information.

- Distribution of particular tunes

- Variation in popularity of tune types

- Quantifying how 'traditional' a region's repetoires is (i.e. compare to O'neills or likewise).

- Looking for similarities / influences between locations repertoires.

- Generating a list of tunes to try if you are attening a session in a new location (cross-referenced with a user's tunebook).

- Regional connectedness could be included as a feature for a ML-based

### Tune comment information 

The site has another source of information of tunes which is not included in the database provided by Jeremy. Namely the user comments on tune pages include a wealth of more specific information. There would be a variety of interesting task to approach with natural language processing including.

- Origin of tunes (this could be more specific than the previous suggestion using User locations.)
- Connnection to musicians (particularly those pre-dating modern recordings)
- Identifying traditional versus modern tunes
- Instrument-specific repertoires (i.e. piping tunes)
- More abstract traits of the tune itself? (i.e. tempo, feel)
- Related tunes via references to other tune pages (need to be cautious as people suggest tunes in this way)
