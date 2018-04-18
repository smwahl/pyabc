from __future__ import absolute_import, division, print_function

# URL = Uniform Resource Locator
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

from bs4 import BeautifulSoup
import re
from geopy.geocoders import Nominatim
import numpy as np


# This returns the part of the
class userProfile(object):
    '''
    Scrapes user profile page on the session and saves the username, location
    and description. Uses BeautifulSoup to parse html.

    Location is specified by latitude and longitude, and geopy is used to
    identify this location in terms of
    '''
    def __init__(self,uid):
        self.user_id = int(uid)
        self.profile_url= 'https://thesession.org/members/' + str(uid)

        self.__soup = None
        self.name = None
        self.location = None
        self.description = None

        self.getProfileHTML()

        self.getUserName()
        self.getLocation()
        self.getDescription()

        self.locationInfo = self.identifyLocation(self.location)


    def getProfileHTML(self):
        try:
            url = self.profile_url
            response = urlopen(url)
            html = response.read()
            response.close()
            self.__soup = BeautifulSoup(html,"html.parser")
            print(url)
            #print(self.__soup)
        except ValueError:
            print('Failed to parse response from ',self.profile_url)

    def getLocation(self):
        if self.__soup is None:
            self.getProfileHTML()

        mapping_elements = []
        locations = []

        try:
            for child in self.__soup.body.descendants:
              if 'Mapping'in child:
                  mapping_elements.append(child)
                  #print(child)

            #print(len(mapping_elements))
            #m = mapping_elements[0]
            for m in mapping_elements:
                for s in m.split('\n'):
                    if 'Mapping.setLocation' in s:
                        #print(s)
                        fs = [float(f) for f in re.findall(r'-?\d+\.?\d*',s)]
                        #print(fs)
                        if len(fs) == 2:
                            locations.append(fs)

            self.location = locations[0]
            #print(self.location)
        except:
            print('Location not found in profile.')

    def getDescription(self):
        if self.__soup is None:
            self.getProfileHTML()

        try:
            description = ''
            mydivs = self.__soup.findAll("div", {"class": "prose"})
            for m in mydivs:
                description = description + m.text
            #print(description)
            self.description = description
        except:
            print('Description not found on profile.')


    def getUserName(self):
        if self.__soup is None:
            self.getProfileHTML()

        try:
            mydivs = self.__soup.findAll("h1")
            name = mydivs[0].text
            self.userName = name

            #print(self.userName)

        except:
            print('User name not found on profile.')

    def identifyLocation(self,latlon):
        '''
        Takes a tuple with the latitude and longitude and returns a json with categorical
        information (i.e. country, county, city)
        '''
        geolocator = Nominatim()
        location = geolocator.reverse(latlon)

        address = location.raw['address']
        return address


# This returns the part of the
class userTunes(object):
    '''
    Scrapes all of the tunes connected to a user (Tunebook + settings) and store in lists
    of tune ids.
    '''
    def __init__(self,uid):
        self.user_id = int(uid)
        self.tunebook_url = 'https://thesession.org/members/' + str(uid) + '/tunebook'
        self.tunesettings_url = 'https://thesession.org/members/' + str(uid) + '/tunes'

        self.__soup = None
        self.tunebook = []
        self.tunesettings = []
        self.settings = []
        self.tunes = []

        #self.getProfileHTML()

        self.getTuneBook()
        self.getTuneSettings()
        self.combineTuneList()

    def getHTML(self,url):
        try:
            response = urlopen(url)
            html = response.read()
            response.close()
            self.__soup = BeautifulSoup(html,"html.parser")
            #print(self.__soup)
        except ValueError:
            print('Failed to parse response from ',self.profile_url)

    def getTuneBook(self):
        cont = True
        i = 1
        while cont:
            url = self.tunebook_url + '?page=' + str(i)
            print(url)
            self.getHTML(url)

            mapping_elements = []
            locations = []

            description = ''
            hrefs = self.__soup.find_all('a', href=True)


            #print(hrefs)
            for x in hrefs:
                if '/tunes/' in str(x):
                    try:
                        tid = int(re.search(r'\d+', str(x)).group())
                        self.tunebook.append(tid)
                    except:
                        pass

            # see if there are additional pages.
            cont = False
            for x in hrefs:
                if 'next' in str(x):
                    #print('found next')
                    cont = True
                    i = i+1
                    break

            #print(self.tune_list)

    def getTuneSettings(self):
        cont = True
        i = 1
        while cont:
            url = self.tunesettings_url + '?page=' + str(i)
            print(url)
            self.getHTML(url)

            mapping_elements = []
            locations = []

            description = ''
            hrefs = self.__soup.find_all('a', href=True)


            #print(hrefs)
            for x in hrefs:
                if '/tunes/' in str(x):
                    #print(x)
                    try:
                        tid = map(int, re.findall(r'\d+', str(x)))
                        self.tunesettings.append(tid[0])
                        self.settings.append(tid[1])
                    except:
                        pass

            # see if there are additional pages.
            cont = False
            for x in hrefs:
                if 'next' in str(x):
                    #print('found next')
                    cont = True
                    i = i+1
                    break

    def combineTuneList(self):
        tlist = self.tunebook + self.tunesettings
        self.tunes = np.unique(tlist)


if __name__ == "__main__":

    print('Testing userProfile:')
    up = userProfile(97793)

    print('\nUser:',up.userName,up.user_id)

    print('\nDescription:\n',up.description)

    print('\nLocation:\n',up.location)
    print(up.locationInfo['city'])
    print(up.locationInfo['county'])
    print(up.locationInfo['city'])
    print(up.locationInfo['state'])

    print('\nTesting userProfile:')
    utb = userTunes(97793)

    print('\nUser\'s settings:')
    print(utb.settings)

    print('\nUser\'s tunes:')
    print(utb.tunes)


