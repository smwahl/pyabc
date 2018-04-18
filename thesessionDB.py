#! /Users/swahl/anaconda/bin/python
# coding: utf-8

#import pyabc
# from pyabc import *
import json
# import numpy as np

import os
import sqlite3  # this is the module that binds to SQLite
# import pandas as pd  # you'll see why we can use this later

# from progress import progress
from click import progressbar

# https://thesession.org/api
#
# Formats
# JSON	?format=json
# XML	?format=xml
# RSS	?format=rss
# Endpoints
# The following lists are available in multiple formats e.g. /tunes/new?format=json or /recordings/search?q=altan&format=rss
#
# By default, 10 items will be returned in a list. You can request up to 50 items by appending &perpage= e.g. /tunes/new?format=json&perpage=35
#
# If you request an individual item, e.g. /tunes/27?format=xml, you will get back the details for that item and any comments that have been posted to it.

class thesessionDB(object):
    '''
    Defines an sqlite database, built from the json-based data dumps provided
    at 'https://github.com/adactio/TheSession-data'.

    Tables are included for:

    Users
    Tunes
    Settings
    Aliases
    Recordings
    Recorded Tunes
    Events
    Sessions

    Fields are added to the database from additional scraped directly from
    thesession.org, using the sites api, and from information consolidated by
    this codebase.

    Search functions are defined to translate more pthonic searches to SQL
    language.
    '''

    def __init__(self, delete=False,download=False):

        # setup database
        self.DBFILE = 'thesession.db'  # this will be our database
        self.BASEDIR = os.getcwd() + '/sqlite3'  # os.path.abspath(os.path.dirname(__file__))
        self.DBPATH = os.path.join(self.BASEDIR, self.DBFILE)

        # we may need to delete the existing file first
        if delete:
            if os.path.exists(self.DBPATH):
                os.remove(self.DBPATH)

        # open a connection to the database for this tutorial
        self.conn = sqlite3.connect(self.DBPATH)

        # get a cursor to the database
        self.cur = self.conn.cursor()

        if not os.path.isfile("json/tunes.json"):
            self.get_thesession_jsons()
        elif download:
            self.get_thesession_jsons()

    def clearDB(self):
        if os.path.exists(self.DBPATH):
            os.remove(self.BPATH)

        # open a connection to the database for this tutorial
        self.conn = sqlite3.connect(self.DBPATH)

        # get a cursor to the database
        self.cur = self.conn.cursor()

    def get_thesession_jsons(self,
            src='https://raw.githubusercontent.com/adactio/TheSession-data/master/json'):
        import urllib
        for f in ['tunes','recordings','aliases','events','sessions']:
            url = src+'/'+f+'.json'
            print("Downloading "+f+" database from %s..." % url)
            try:
                urllib.urlretrieve(url, 'json/'+f+'.json')
            except AttributeError:
                import urllib.request
                urllib.request.urlretrieve(url, 'json/'+f+'.json')

    def defineTables(self):

        # Create users table
        try:
            self.cur.execute('DROP TABLE users')
        except:
            pass

        self.cur.execute('''CREATE TABLE users (
            user TEXT PRIMARY KEY
        )''')
        #self.conn.commit()

        # Create tunes table
        try:
            self.cur.execute('DROP TABLE tunes')
        except:
            pass

        self.cur.execute('''CREATE TABLE tunes (
            tune_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            rhythm TEXT NOT NULL,
            meter TEXT NOT NULL,
            mode TEXT NOT NULL
        )''')
        #self.conn.commit()

        # Create settings table
        try:
            self.cur.execute('DROP TABLE settings')
        except:
            pass

        self.cur.execute('''CREATE TABLE settings (
            setting_id TEXT PRIMARY KEY,
            tune_id TEXT NOT NULL REFERENCES tunes ON UPDATE CASCADE ON DELETE CASCADE,
            abc  TEXT,
            date TEXT NOT NULL,
            user TEXT NOT NULL REFERENCES users on UPDATE CASCADE ON DELETE CASCADE,
            name TEXT NOT NULL,
            rhythm TEXT NOT NULL,
            meter TEXT NOT NULL,
            mode TEXT NOT NULL,
            bars INTEGER,
            structure TEXT
        )''')
        #self.conn.commit()

        # Create aliases table
        try:
            self.cur.execute('DROP TABLE aliases')
        except:
            pass

        self.cur.execute('''CREATE TABLE aliases (
            alias_id INTEGER PRIMARY KEY,
            alias TEXT NOT NULL,
            name TEXT,
            tune_id NOT NULL REFERENCES tunes ON UPDATE CASCADE ON DELETE CASCADE
        )''')
        #self.conn.commit()

        # from recordings.json

        # Create artists table
        try:
            self.cur.execute('DROP TABLE artists')
        except:
            pass

        self.cur.execute('''CREATE TABLE artists (
            artist TEXT PRIMARY KEY
        )''')
        #self.conn.commit()

        # Create recordings table (albums)
        try:
            self.cur.execute('DROP TABLE recordings')
        except:
            pass

        self.cur.execute('''CREATE TABLE recordings (
            recording_id TEXT PRIMARY KEY,
            recording_name TEXT NOT NULL,
            artist TEXT REFERENCES artists ON UPDATE CASCADE ON DELETE CASCADE
        )''')
        #self.conn.commit()

        # recorded tunes
        try:
            self.cur.execute('DROP TABLE recorded_tunes')
        except:
            pass

        self.cur.execute('''CREATE TABLE recorded_tunes (
            id TEXT PRIMARY KEY,
            recording_id TEXT REFERENCES recordings ON UPDATE CASCADE ON DELETE CASCADE,
            recording_name TEXT NOT NULL,
            artist TEXT REFERENCES artists ON UPDATE CASCADE ON DELETE CASCADE,
            track INTEGER ,
            number INTEGER ,
            tune_name TEXT,
            tune_id REFERENCES tunes ON UPDATE CASCADE ON DELETE CASCADE

        )''')
        #self.conn.commit()

        # Create events table from events.json
        try:
            self.cur.execute('DROP TABLE events')
        except:
            pass

        self.cur.execute('''CREATE TABLE events (
            event_id TEXT PRIMARY KEY,
            address TEXT,
            area TEXT,
            country TEXT,
            dtend TEXT,
            dtstart TEXT,
            event_name TEXT,
            latitude TEXT,
            logitude TEXT,
            town TEXT,
            venue TEXT
        )''')
        #self.conn.commit()

        # Create sessions tablei from sessions.json
        try:
            self.cur.execute('DROP TABLE sessions')
            #conn.commit()
        except:
            pass

        self.cur.execute('''CREATE TABLE sessions (
            session_id TEXT PRIMARY KEY,
            address TEXT,
            area TEXT,
            country TEXT,
            date TEXT,
            latitude TEXT,
            logitude TEXT,
            name TEXT,
            town TEXT
        )''')
        self.conn.commit()


    def load_jsons(self):
        self.json_tunes = json.loads(open('json/tunes.json', 'rb').read().decode('utf8'))
        self.json_recordings = json.loads(open('json/recordings.json', 'rb').read().decode('utf8'))
        self.json_aliases = json.loads(open('json/aliases.json', 'rb').read().decode('utf8'))
        self.json_events = json.loads(open('json/events.json', 'rb').read().decode('utf8'))
        self.json_sessions = json.loads(open('json/sessions.json', 'rb').read().decode('utf8'))

    def populateTablesFromJSON(self,Ntest=None):

        self.load_jsons()

        if Ntest is None:
            N = len(self.json_tunes)
        else:
            N = Ntest

        self.insertTuneSettings(self.json_tunes[:N])

        if Ntest is None:
            N = len(self.json_aliases)
        else:
            N = Ntest

        self.insertTuneAliases(self.json_aliases[:N])

        if Ntest is None:
            N = len(self.json_recordings)
        else:
            N = Ntest

        self.insertTuneRecordings(self.json_recordings[:N])

        if Ntest is None:
            N = len(self.json_events)
        else:
            N = Ntest

        self.insertEvents(self.json_events[:N])

        if Ntest is None:
            N = len(self.json_sessions)
        else:
            N = Ntest

        self.insertSessions(self.json_sessions[:N])

    def insertTuneSettings(self,json_tunes):
        # Insert entries from tunes.json
        N = len(json_tunes)
        with progressbar(range(N),label='Transferring tune settings from JSON to SQL') as bar:
            for i,jj in zip(bar,json_tunes):
            #for i,jj in enumerate(json_tunes):
#                 jj = json_tunes[i]

                # Fill missing with None
                keys = ['setting','tune','abc','date','username','name','type','meter','mode']
                j = {}
                for x in keys:
                    try:
                        j.update({x:jj[x]})
                    except:
                        j.update({x:None})

                # Check if user is new, if so add to table
                self.cur.execute('SELECT * FROM users WHERE (user=?)', [j['username']])
                entry = self.cur.fetchone()
                if entry is None:
                    self.cur.execute('INSERT INTO users VALUES (?)', [j['username']])

                # Check if tune is new, if so add to table
                self.cur.execute('SELECT * FROM tunes WHERE (tune_id=?)', [j['tune']])
                entry = self.cur.fetchone()
                if entry is None:
                    row = [j['tune'],j['name'],j['type'],j['meter'],j['mode']]
                    self.cur.execute('INSERT INTO tunes VALUES (?,?,?,?,?)', row)

                row = [j['setting'],j['tune'],j['abc'],j['date'],j['username'],j['name'],j['type'],j['meter'],j['mode']]
                self.cur.execute('INSERT INTO settings VALUES (?,?,?,?,?,?,?,?,?,NULL,NULL)',row)
#                 progress(i+1,N,'Transfering tune settings from JSON to SQL.')

        self.conn.commit()  # you must commit for it to become permanent

    def insertTuneAliases(self,json_aliases):
        # Insert entries from tunes.json
        self.cur.execute('SELECT MAX(alias_id) from aliases')
        try:
            startid = int(cur.fetchone()[0])+1
        except:
            startid = 0

        N = len(json_aliases)
        with progressbar(range(N),label='Transferring tune aliases from JSON to SQL') as bar:
            for i,j in zip(bar,json_aliases):
#             for i,j in enumerate(json_aliases):
                keys = ['alias','name','tune_id']
                jj = {}
                for x in keys:
                    try:
                        jj.update({x:j[x]})
                    except:
                        jj.update({x:None})

                row = [startid+i,jj['alias'],jj['name'],jj['tune_id']]
                self.cur.execute('INSERT INTO aliases VALUES (?,?,?,?)',row)
#                 progress(i+1,N,'Transferrring aliases from JSON to SQL.')
        self.conn.commit()



    def insertTuneRecordings(self,json_recordings):

        N = len(json_recordings)

        with progressbar(range(N),label='Transferring recordings from JSON to SQL') as bar:
            for i,j in zip(bar,json_recordings):
#             for i,j in enumerate(json_recordings):

                keys = ['id','recording','artist','track','number','tune','tune_id']
                jj = {}
                for x in keys:
                    try:
                        jj.update({x:j[x]})
                    except:
                        jj.update({x:None})

                # Check if user is new, if so add to table
                self.cur.execute('SELECT * FROM artists WHERE (artist=?)', [jj['artist']])
                entry = self.cur.fetchone()
                if entry is None:
                    self.cur.execute('INSERT INTO artists VALUES (?)', [jj['artist']])

                # Check if tune is new, if so add to table
                self.cur.execute('SELECT * FROM recordings WHERE (recording_id=?)', [jj['id']])
                entry = self.cur.fetchone()
                if entry is None:
                    row = [j['id'],j['recording'],j['artist']]
                    self.cur.execute('INSERT INTO recordings VALUES (?,?,?)', row)

                try:
                    itrack = int(jj['track'])
                except:
                    itrack = None

                try:
                    inum = int(jj['number'])
                except:
                    inum = None

                row = [i,jj['id'],jj['recording'],jj['artist'],itrack,inum,jj['tune'],jj['tune_id']]
                self.cur.execute('INSERT INTO recorded_tunes VALUES (?,?,?,?,?,?,?,?)',row)
#                 progress(i+1,N,'Transferring recordings from JSON to SQL.')

        self.conn.commit()  # you must commit for it to become permanent

    def insertEvents(self,json_events):
        N = len(json_events)
        with progressbar(range(N),label='Transferring events from JSON to SQL') as bar:
            for i,j in zip(bar,json_events):
#             for i,j in enumerate(json_events):

                keys = ['id','address','area','country','dtend','dtstart','event','latitude','longitude','town','venue']
                row = [ None for x in range(len(keys))]

                for x in  range(len(keys)):
                    try:
                        row[x] = j[keys[x]]
                    except:
                        pass
                #row = [j['id'],j['address'],j['area'],j['country'],j['dtend'],j['dtstart'],j['event'],
                #      j['latitude'],j['longitude'],j['town'],j['venue']]
                self.cur.execute('INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?,?)',row)
#                 progress(i+1,N,'Transfering events from JSON to SQL.')

        self.conn.commit()  # you must commit for it to become permanent


    def insertSessions(self,json_sessions):

        N = len(json_sessions)
        with progressbar(range(N),label='Transferring sessions from JSON to SQL') as bar:
            for i,j in zip(bar,json_sessions):
#             for i,j in enumerate(json_sessions):

                keys = ['id','address','area','country','date','latitude','longitude','name','town']
                row = [ None for x in range(len(keys))]

                for x in  range(len(keys)):
                    try:
                        row[x] = j[keys[x]]
                    except:
                        pass

                #row = [j['id'],j['address'],j['area'],j['country'],j['date'],
                #      j['latitude'],j['longitude'],j['name'],j['town']]

                self.cur.execute('INSERT INTO sessions VALUES (?,?,?,?,?,?,?,?,?)',row)
#                 progress(i+1,N,'Transfering sessions from JSON to SQL.')

        self.conn.commit()  # you must commit for it to become permanent

if __name__ == "__main__":

    db = thesessionDB(delete=True,download=True)

    db.defineTables()
#     db.populateTablesFromJSON(Ntest=1000)
    db.populateTablesFromJSON()

    db.cur.execute('SELECT * FROM users LIMIT 5')
    q = db.cur.fetchall()  # fetch all the results of the query

    print ''
    print 'Users:'
    for x in q:
        print x

    db.cur.execute('SELECT * FROM tunes LIMIT 5')
    q = db.cur.fetchall()  # fetch all the results of the query

    print ''
    print 'Tunes:'
    for x in q:
        print x

    db.cur.execute('SELECT setting_id, tune_id, date, user FROM settings LIMIT 5')
    q = db.cur.fetchall()  # fetch all the results of the query

    print ''
    print 'Settings:'
    for x in q:
        print x

    db.cur.execute('SELECT * FROM aliases LIMIT 5')
    q = db.cur.fetchall()  # fetch all the results of the query

    print ''
    print 'Aliases:'
    for x in q:
        print x

    db.cur.execute('SELECT * FROM artists LIMIT 5')
    q = db.cur.fetchall()  # fetch all the results of the query

    print ''
    print 'Artists:'
    for x in q:
        print x

    db.cur.execute('SELECT * FROM recordings LIMIT 5')
    q = db.cur.fetchall()  # fetch all the results of the query

    print ''
    print 'Recordings:'
    for x in q:
        print x

    db.cur.execute('SELECT * FROM recorded_tunes LIMIT 5')
    q = db.cur.fetchall()  # fetch all the results of the query

    print ''
    print 'Recorded tunes:'
    for x in q:
        print x
