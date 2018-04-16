import pyabc
import numpy as np
import json

from tune_structure import matchJsonField, inJsonField, fieldList, parseStructure



def transposeKey(key0,step):
    '''
    Transpose one pyabc.Key() by a number of half-steps.
    '''
    from numpy import mod, floor_divide
    inv_pitch_values={ pitch_values[n]:n for n in chromatic_notes }


    mode = key0.mode
    rootval0 = pitch_values[key0.root.name] + step
    rootval = mod(rootval0,12)
    root = inv_pitch_values[rootval]

    return pyabc.Key(root=root,mode=mode)


class digitizedTune(object):
    '''
    Defines an object that extends the pyabc tune functionality by finding
    and storing a digitized version that records the note durations and
    relative durations in a discritized format that allows for direct
    comparison of the tune shapes.
    '''
    def __init__(self,json=None,tune=None,incnote=32):
        if json is not None:
            self.json = json
            self.pyabcTune = pyabc.Tune(json=self.json)
        elif tune is not None:
            self.pyabcTune = tune

        self.tokens = self.pyabcTune.tokens

        measures = self.findMeasures(self.tokens)
        parts = self.findParts(measures)
        self.measures = measures
        self.num_parts =  len(parts)
        la = []
        for p in parts:
            la.append( 2.*len(p)) # Note simplified version assumes repeating parts.

        self.bars = np.array(la) # array of number of bars for part
        self.total_bars = np.sum(self.bars)

        self.key = pyabc.Key(self.pyabcTune.header['key'])
        self.meter = self.pyabcTune.header['meter']
        self.beat_mult = float(self.meter.split('/')[0])
        self.beat_value = float(self.meter.split('/')[1])
        self.incnote = incnote
        self.incdur = 1. * self.beat_value / self.incnote

        dtune = []
        for p in parts:
            dpart = []
            for m in p:
                dmeas = self.digitizeMeasure(m)
                dpart.append(dmeas)

            dtune.append(dpart)

        self.tune = dtune

    def part(self,n):
        assert n < self.num_parts
        return self.tune[n]

    def measure(self,np,nm):
        assert np < self.numparts
        assert nm < len(self.tune[np])
        return self.tune[np][nm]

        #incnote = 32
    def digitizeMeasure(self,measure):

        lm = []
        for x in measure:
            if isinstance(x,Note):
                #print x.pitch.value, x.duration, int(np.round(x.duration / incdur))
                ndigits = int(np.round(x.duration / self.incdur))
                lm += [x.pitch.value + 12.*x.pitch.octave for i in range(ndigits)]

        marr = np.array(lm)
        #marr_rel_root  = marr_abs - key.root.value
        #marr_rel_ionian = marr_abs - key.relative_ionian.root.value
        return marr

    def isNote(self,x):
        return isinstance(x,pyabc.Note)

    def isBeam(self,x):
        return isinstance(x,pyabc.Beam)

    def simplifyTokens(self,tokens):
        '''
        Removes any elements that aren't notes or bars.
        '''
        results = []
        for t in tokens:
            if self.isNote(t) or self.isBeam(t):
                results.append(t)
            else:
                pass
        return results

    def findMeasures(self,tokens1):
        '''
        For now this requires that parts be repeating
        '''
        tokens = self.simplifyTokens(tokens1)
        result = []
        meas = []
        for t in tokens:
            if self.isBeam(t):
                meas.append(t)
                result.append(meas)
                meas = []
            else:
                meas.append(t)
        return result


    def findParts(self,measures):

        result = []
        part = []
        for m in measures:
            if  ':|' in str(m[-1]):
                part.append(m)
                result.append(part)
                part = []
            else:
                part.append(m)
        return result


if __name__ == "__main__":
    ts_tunes = json.loads(open('thesession_2017_07_12.json', 'rb').read().decode('utf8'))

    t0 = matchJsonField(ts_tunes,'name','Banish Misfortune')[0]

    t = parseStructure(t0)

    dtune = digitizedTune(json=t)

    print dtune.tune

