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

    The code reads in an a json file for a tune, which has been standardized
    using the parseStructure() method. The tune is saved as a list of parts,
    which contains a list of measure arrays.
    '''
    def __init__(self,json=None,tune=None,incnote=16):
        if json is not None:
            self.json = json
            self.pyabcTune = pyabc.Tune(json=self.json)
        elif tune is not None:
            self.pyabcTune = tune

        self.tokens = self.pyabcTune.tokens

        self.measures = self.findMeasures(self.tokens)

        self.bars = np.array(json['length'])
        self.num_parts = len(json['length'])
        self.total_bars = np.sum(self.bars)

        parts = self.findParts(self.measures,self.bars)

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
        self.flat_tune = self.flattenTune(self.tune)
        self.steps = self.findSteps(self.tune)

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
            if isinstance(x,pyabc.Note):
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
                #meas.append(t) # include the Beam?
                result.append(meas)
                meas = []
            else:
                meas.append(t)
        return result

    def findParts(self,measures,plens):

        parts = []
        i0 = 0
        i1 = 0

        for l in plens:
            part = []
            i0 = i1
            i1 = i1 + l

            part = measures[i0:i1]
            parts.append(part)

        return parts

    def flattenTune(self,tune):
        '''
        Combine all parts into a single list of measure arrays, facilitates some operations.
        '''
        ftune = []
        for part in tune:
            for meas in part:
                ftune.append(meas)
        return ftune

    def transposeByInterval(self,interval):
        '''
        Return the digitized tune transposed by a given interval.
        '''
        ttune = []
        for part in self.tune:
            tpart = []
            for meas in part:
                tpart.append(meas + interval)
            ttune.append(tpart)
        return ttune

    def interval_root(self):
        '''
        Return the interval by which the tune would be shifted for the root to be "C".
        '''
        val = self.key.root.value
        return  -1 * val

    def interval_relative_ionion(self):
        '''
        Return the interval by which the tune would be shifted the relative ionian scale
        to be "C ionian".
        '''
        val = dtune.key.relative_ionian.root.value
        return -1 * val

    def diffMeasure(self,meas0,meas1):
        '''
        Returns an Interval object representing the difference between two different measures
        '''
        assert len(meas0) == len(meas1), 'Measure arrays must be the same length for comparison.'
        dist = meas1 - meas0
        return Interval(dist)

    def diffPart(self,part0,part1):
        '''
        Returns list of Interval object representing the difference between two different measures
        '''
        assert len(part0) == len(part1), 'Parts must have the same number of measures for comparison.'
        dpart = []
        for meas0,meas1 in zip(part0,part1):
            dpart.append(self.diffMeasure(meas0,meas1))
        return dpart

    def diffTune(self):
        assert False, 'Not implemented yet.'


    def findSteps(self,tune):
        '''
        Returns an Interval object where each point is the how much the pitch changes from the
        previous increment.
        '''

        flat_tune = self.flattenTune(tune)
        sflat = []


        for i in range(len(flat_tune)):
            meas = flat_tune[i]
            smeas0 = np.diff(meas)

            # Find the step from the last inc in the previous
            if i==0:
                s0 = 0.
            else:
                prev_meas = flat_tune[i-1]
                s0 = meas[0] - prev_meas[-1]

            #print s0, smeas0
            smeas = np.hstack([s0,smeas0])
            sflat.append(smeas)

        stune = self.findParts(sflat,self.bars)
        return stune


class Interval(object):
    '''
    Defines an object that looks at the relative interval at every point between two
    measures.

    The 'extend' flag returns matches for intervals in arbitrary octave.
    '''
    def __init__(self,distance):

        # stores the distance in semitones between the two
        self.abs_distance = distance

        # stores the value of absolute interval
        self.values = np.abs(self.abs_distance)

        # interval within same octave
        self.values_octave = np.mod(self.values,12.)

    def unison(self):
        return self.values == 0

    def octave(self,extend=True):
        isUni = self.unison()
        isOct = self.values_octave ==0

        if extend:
            return np.logical_and( np.logical_not(isUni), isOct)
        else:
            return self.values == 12.

    def perfect_fifth(self,extend=True):
        if extend:
            return self.values_octave == 7.
        else:
            return self.values == 7.

    def major_third(self,extend=True):
        if extend:
            return self.values_octave == 4.
        else:
            return self.values == 4.

    def minor_third(self,extend=True):
        if extend:
            return self.values_octave == 3.
        else:
            return self.values == 3.

    def minor_second(self,extend=True):
        if extend:
            return self.values_octave == 1.
        else:
            return self.values == 1.

    def major_second(self,extend=True):
        if extend:
            return self.values_octave == 2.
        else:
            return self.values == 2.

    def perfect_fourth(self,extend=True):
        if extend:
            return self.values_octave == 5.
        else:
            return self.values == 5.

    def diminished_fifth(self,extend=True):
        if extend:
            return self.values_octave == 6.
        else:
            return self.values == 6.

    def minor_sixth(self,extend=True):
        if extend:
            return self.values_octave == 8.
        else:
            return self.values == 8.

    def major_sixth(self,extend=True):
        if extend:
            return self.values_octave == 9.
        else:
            return self.values == 9.

    def minor_seventh(self,extend=True):
        if extend:
            return self.values_octave == 10.
        else:
            return self.values == 10.

    def major_seventh(self,extend=True):
        if extend:
            return self.values_octave == 11.
        else:
            return self.values == 11.

    #def findParts(self,measures):

        #result = []
        #part = []
        #for m in measures:
            #if  ':|' in str(m[-1]):
                #part.append(m)
                #result.append(part)
                #part = []
            #else:
                #part.append(m)
        #return result


if __name__ == "__main__":
    ts_tunes = json.loads(open('thesession_2017_07_12.json', 'rb').read().decode('utf8'))

    t0 = matchJsonField(ts_tunes,'name','Banish Misfortune')[0]

    t = parseStructure(t0)

    dtune = digitizedTune(json=t)

    #print dtune.tune

    # testing interval

    meas0 = np.array([ 0., 0., 0., 0.,
              2., 2., 2., 2.,
              4.,4.,3.,3.,
              8.,8.,8.,8.])

    meas1 = np.array([ 0., 0., 12., 12.,
              9.,9.,9.-12.,9.+12.,
              0.,0.,0.,0.,
              8.,8.,8.-24.,8.-24.])

    int0 = dtune.diffMeasure(meas0,meas1)

    print int0.values




