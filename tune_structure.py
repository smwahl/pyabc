#! /Users/swahl/anaconda/bin/python
# coding: utf-8

#import pyabc
import pyabc
import json
import numpy as np

# Functions for searching Json fields
def matchJsonField(js,field,string):
    result = []
    for t in js:
        if t[field] == string:
            result.append(t)
    return  result

def inJsonField(js,field,string):
    result = []
    for t in js:
        if string in t[field]:
            result.append(t)
    return result

def fieldList(js,field):
    result = []
    for t in js:
        result.append(t[field])
    return result

note_symbols = ['C','D','E','F','G','A','B','c','d','e','f','g','a','b','z']
esc_chars = ['\r','\n']
#['^','=']
oct_chars = [",","'"]


# Basic .abc helper functions
def notesInStr(mystr):
    for x in note_symbols:
        if x in mystr:
            return True
    return False

def removeESC(mystr):
    cstr = mystr
    for c in esc_chars:
        cstr = cstr.replace(c,'')
    return cstr


# Functions for making making a more uniform structure
def tripletToSemiQuavers(mystr):
    '''
    To facilitate comparisons of duration, we are going to treat '3(ABc' as 'A\B\c'.
    '''
    tars = []
    reps = []
    for i,c in enumerate(mystr):

        #try:
            if mystr[i]=='(' and mystr[i+1]=='3':
                #print i
                tar = u'(3'
                rep = ''

                ii = i+2
                notes = 0
                while notes<2:
                    if mystr[ii] in note_symbols:
                        #print ii, mystr[ii]
                        tar = tar + mystr[ii]
                        rep = rep + mystr[ii]
                        if mystr[ii+1] in oct_chars:
                            tar = tar + mystr[ii+1]
                            rep = rep + mystr[ii+1]
                            ii = ii+1
                        ii = ii+1
                        rep = rep +"/"

                        notes = notes+1
                    else:
                        #print ii, mystr[ii]
                        tar = tar + mystr[ii]
                        rep = rep + mystr[ii]
                        ii = ii+1


                tars.append(tar)
                reps.append(rep)

    #print tars
    #print reps

    cstr = mystr
    for t,r in zip(tars,reps):
        try:
            cstr = cstr.replace(t,r)
        except:
            pass

    return cstr


def expandRepeats(abc,maxPartLen=16):
    '''
    Reads in a .abc string and parses it into a list of parts, where
    each part is a list of measures with the repeat p
    returns the list of parts, a list with the part lengths, and
    a string describing the patern i.e. 'AABBCC'. Note: this method
    does not explicitly look for '||' between parts, but instead
    '''
    abc2 = removeESC(abc)
    smeas = abc2.split('|')
    smeas2 = [ x for x in smeas if notesInStr(x)]

    part_labels = {0:'A',1:'B',2:'C',3:'D',4:'E',5:'G'}

    i0=0
    i=0
    expmeas = []
    parts = []
    ipart = 0

    repeat = 0
    measinpart = 0

    repeatedpart = []
    ending1 = []
    ending2 = []
    part = []
    parts = []

    pattern = ''
    part_lengths = []

    while i < len(smeas2):
        meas = smeas2[i]

        #if repeat == 0:
        if (i-i0)==maxPartLen:
            print 'Non-repeating part ended by reaching maxParLen.'
            part = repeatedpart
            parts.append(part)

            length = len(repeatedpart)
            part_lengths.append(length)

            label = part_labels[ipart]
            pattern = pattern + label

            i0 = i
            repeatedpart = []; ending1 = []; ending2 = []
            ipart = ipart + 1

            meas = meas[1:]
            i = i+1
            repeatedpart.append(meas)

        elif i>i0 and meas[0]==':':
            print 'Non-repeating part ended by new start of repeat.'
            part = repeatedpart
            parts.append(part)

            length = len(repeatedpart)
            part_lengths.append(length)

            label = part_labels[ipart]
            pattern = pattern + label

            i0 = i
            repeatedpart = []; ending1 = []; ending2 = []
            ipart = ipart + 1

            meas = meas[1:]
            i = i+1
            repeatedpart.append(meas)

        elif meas[0] == '1':
            print 'Repeating part ended by a repeat with different endings.'
            meas = meas[1:]
            while meas[0] !='2':
                if meas[-1] == ':':
                    meas = meas[:-1]
                ending1.append(meas)
                i = i+1
                meas = smeas2[i]
            #print 'ending1',ending1
            meas = meas[1:]
            for j in range(len(ending1)):
                if meas[-1] == ':':
                    meas = meas[:-1]
                ending2.append(meas)
                i = i+1
                if i < len(smeas2):
                    meas = smeas2[i]
            #print 'ending2',ending2

            part = repeatedpart + ending1 + repeatedpart + ending2
            parts.append(part)

            length = len(repeatedpart + ending1) * 2
            part_lengths.append(length)

            label = part_labels[ipart]
            pattern = pattern + label + label

            i0 = i
            ipart = ipart+1
            repeatedpart = []; ending1 = []; ending2 = []

        elif meas[-1] == ':':
            print 'Repeating part ended by a repeat with same ending.'
            meas = meas[:-1]
            repeatedpart.append(meas)

            part = repeatedpart + repeatedpart
            parts.append(part)

            length = len(repeatedpart) * 2
            part_lengths.append(length)

            label = part_labels[ipart]
            pattern = pattern + label + label

            i = i+1
            i0 = i
            ipart = ipart+1
            repeatedpart = []; ending1 = []; ending2 = []

        elif i == len(smeas2)-1:
            print 'Repeating part ended by reaching end of tune.'
            repeatedpart.append(meas)
            part = repeatedpart
            parts.append(part)

            length = len(repeatedpart)
            part_lengths.append(length)

            label = part_labels[ipart]
            pattern = pattern + label

            i = i+1
            i0 = i
            ipart = ipart+1
            repeatedpart = []; ending1 = []; ending2 = []


        else:
            i = i+1
            if meas[0] == ':':
                meas = meas[1:]
            repeatedpart.append(meas)

    #print pattern
    #print part_lengths
    #print parts

    return parts,part_lengths,pattern


def partsToABC(parts,pattern):
    part_labels = {0:'A',1:'B',2:'C',3:'D',4:'E',5:'G'}
    abc = ''
    for i,part in enumerate(parts):
        label = part_labels[i]
        if (label+label) in pattern:
            line1 = '|'.join(part[:(len(part)/2)]) + '|\r\n'
            line2 = '|'.join(part[(len(part)/2):]) + '||\r\n'
            abc = abc + line1 + line2
        else:
            line = '|'.join(part) + '||\r\n'
            abc = abc+line
    #print abc
    return abc



def parseStructure(t):
    '''
    Takes a Json entry for a section and return a json entry with extra entries
    for the sturcture of the tune.

    Replaced fields:
    'abc' -- .abc string replaced with all of the repeated sections expanded out.

    New fields:
    'parts' -- A nested list of measures, divided by part.
    'length' -- A list with the number of measures in each part.
    'pattern' -- Repeat pattern i.e. 'AABBC'.

    '''

    tresult = t.copy()

    abc = t['abc']
    abc2 = removeESC(abc)
    abc3 = tripletToSemiQuavers(abc2)

    parts,lengths,pattern = expandRepeats(abc3)

    abc4 = partsToABC(parts,pattern)

    tresult.update({'abc':abc4})

    tresult.update({'parts':parts})
    tresult.update({'length':lengths})
    tresult.update({'pattern':pattern})

    return tresult

if __name__ == "__main__":
    ts_tunes = json.loads(open('thesession_2017_07_12.json', 'rb').read().decode('utf8'))

    json_test_entries = []

    t = matchJsonField(ts_tunes,'name','Banish Misfortune')[0]
    json_test_entries.append(t)

    t = matchJsonField(ts_tunes,'name','Banshee, The')[1] # The first and second ending breaks the pyabc Tune()?
    json_test_entries.append(t)

    t = matchJsonField(ts_tunes,'name','Kesh, The')[-1]
    json_test_entries.append(t)

    t = matchJsonField(ts_tunes,'name','Green Fields Of Glentown, The')[0]
    json_test_entries.append(t)

    t = inJsonField(ts_tunes,'name','Cloch Na')[3]
    json_test_entries.append(t)

    t = matchJsonField(ts_tunes,'name','Sligo Maid, The')[0]
    json_test_entries.append(t)

    t = matchJsonField(ts_tunes,'name',"Morrison's")[0]
    json_test_entries.append(t)

    t = matchJsonField(ts_tunes,'name',"Sailor's Bonnet, The")[1]
    json_test_entries.append(t)

    for t0 in json_test_entries:
        t = parseStructure(t0)

        print ''
        print 'Name',t['name']
        print ''
        print 'Original .abc:'
        print t0['abc']
        print ''
        print 'Pattern:', t['pattern']
        print 'Length:', t['length'], 'Total:', sum(t['length'])
        print 'Expanded .abc:'
        print t['abc']

