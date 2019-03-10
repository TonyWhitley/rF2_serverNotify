"""
A simple Python program to scan a set of rFactor 2 servers and pop up a
notification if someone joins a server that had no drivers.

The program is configured by the file rF2_serverNotify.json which should
be edited with the server(s) of interest.
It has two types of dictionary entry:
a) ServerX : 'name of server to be scanned'
    There can be any number of Server entries.
    Text beyond Server is ignored, it's just needed to make each entry different.
b) Interval : 30
    seconds between checking the servers

A data file servers.file.json is created automatically the first time
 the program is run.
It contains all the servers and their addresses.
"""
from __future__ import print_function  # Python 2 compatibility

import os
import sys
import datetime
import json
import time
from   msvcrt import kbhit, getch
if __name__ == '__main__':
  import pymsgbox
from multiprocessing.dummy import Pool as ThreadPool 

import valve.source.a2s
import valve.source.master_server

#appID = '244210'  # Assetto Corsa NO
#appID = '805550'  # Assetto Corsa Competitizione NO
appID = '378860'  # Project Cars 2
#appID = '310560'  # DiRT Rally NO
appID = '737800'  # F1 2018 NO
appID = '431600'  # Automobilista
appID = '211500'  # RaceRoom_Racing_Experience NO
appID = '339790'  # rFactor
appID = '365960'  # rFactor 2

class JSONconfigFile:
  """
  Two types of dictionary entries in the JSON file
  a) ServerX : 'name of server to be scanned'
      There can be any number of Server entries.
      Text beyond 'Server' is ignored.
  b) Interval : 30
      seconds between checking the servers
  """
  def __init__(self, _fname):
    #try:
    with open(_fname, 'r') as file:
      self.serversDict = json.load(file)
    """
    except:
      _errStr = 'Could not open "%s" to read' % os.path.join(os.getcwd(), fname)
      print(_errStr)
      self.records = [_errStr]
      #sys.exit(99)
    """
    self.dict = {}
    self.interval = None
    for key, value in self.serversDict.items():   # iter on both keys and values
      #print(key, value)
      if key.startswith('Server'):
        self.dict[value] = 'Idle'
      if key == 'Interval':
        self.interval = value
    if len(self.dict) == 0:
      print('%s must have entries like "Server1" : "S397 GT3 Nola" ,' % _fname)
      sys.exit(98)
    if self.interval == None:
      print('%s must have an entry like "Interval" : 15  where 15 is the interval between checking servers' % _fname)
      sys.exit(99)

  def read(self):
    return self.serversDict['Server1']
  def getServers(self):
    return self.dict
  def setStatus(self, _server, _status):
    try:
      self.dict[_server] = _status
    except KeyError:
      pass
  def getStatus(self, _server):
    try:
      ret = self.dict[_server]
    except KeyError:
      ret = 'Idle'
    return ret
  def getInterval(self):
    try:
      return self.interval
    except AttributeError:
      raise NameError

class Servers:
  """
  Gets the list of all servers and their addresses.
  Writes/reads the info to a data file (as it takes a couple of minutes
  to read them from Steam).
  Gets the status of a particular server.
  """
  def __init__(self):
    self.serversDict = {}
    self.players = []
    self.driverFilter = DriversFilter('drivers.txt')
  def readServerName(self, address):
    for retry in range(3):
      try:
        _server = valve.source.a2s.ServerQuerier(address)
        info = _server.info()
        _server.close()
        serverName = info['server_name']
        return address, serverName
        #self.serversDict[serverName] = address
      except valve.source.a2s.NoResponseError:
        _server.close()
        pass
    print(' (%s:%d timed out)' % address)
    return address, 'Timed out'
  def readServers(self, notEmpty=False):
    msq = valve.source.master_server.MasterServerQuerier()
    self.addresses = []
    """
      Filter code 	            What the filter returns
      0x00 (NULL, empty string) All servers
      \nor\[x] 	                A special filter, specifies that servers matching any of the following [x] conditions should not be returned
      \nand\[x] 	              A special filter, specifies that servers matching all of the following [x] conditions should not be returned
    ? \dedicated\1 	            Servers running dedicated
      \secure\1 	              Servers using anti-cheat technology (VAC, but potentially others as well)
      \gamedir\[mod] 	          Servers running the specified modification (ex. cstrike)
    ? \map\[map] 	              Servers running the specified map (ex. cs_italy)
      \linux\1 	                Servers running on a Linux platform
      \password\0 	            Servers that are not password protected
    * \empty\1 	                Servers that are not empty
    ? \full\1 	                Servers that are not full
      \proxy\1 	                Servers that are spectator proxies
    * \appid\[appid] 	          Servers that are running game [appid]
      \napp\[appid] 	          Servers that are NOT running game [appid] (This was introduced to block Left 4 Dead games from the Steam Server Browser)
      \noplayers\1 	            Servers that are empty
      \white\1 	                Servers that are whitelisted
      \gametype\[tag,...] 	    Servers with all of the given tag(s) in sv_tags
      \gamedata\[tag,...] 	    Servers with all of the given tag(s) in their 'hidden' tags (L4D2)
      \gamedataor\[tag,...] 	  Servers with any of the given tag(s) in their 'hidden' tags (L4D2)
    * \name_match\[hostname] 	  Servers with their hostname matching [hostname] (can use * as a wildcard)
    ? \version_match\[version]  Servers running version [version] (can use * as a wildcard)
      \collapse_addr_hash\1 	  Return only one server for each unique IP address matched
      \gameaddr\[ip] 	          Return only servers on the specified IP address (port supported and optional)     
    """
    # notEmpty: only find servers with players (real or AI)
    if notEmpty:
      # find all non-empty servers:
      all_addresses = msq.find(appid=appID, empty=1)
    else:
      all_addresses = msq.find(appid=appID)
    #msq.close()
    for address in all_addresses:
      self.addresses.append(address)
    pass

  def readServerNames(self):
    # Multi-thread querying all servers to speed things up
    # (perhaps at the cost of missing some servers).
    # make the Pool of workers
    pool = ThreadPool(len(self.addresses)//10) 

    # read the servers in their own threads
    # and return the results
    results = pool.map(self.readServerName, self.addresses)

    # close the pool and wait for the work to finish 
    pool.close() 
    pool.join() 

    for r in results:
      if r[1] != 'Timed out':
        self.serversDict[r[1]] = r[0]
    pass

  def readSpecificServer(self, serverName):
    msq = valve.source.master_server.MasterServerQuerier()
    addresses = []
    all_addresses = msq.find(name_match=serverName)
    
    #msq.close()
    for address in all_addresses:
      addresses.append(address)
    if len(addresses):
      return addresses[0]
    else:
      return 'ServerNotFound', 0

  def writeServersFile(self, filename):
    with open(filename, 'w') as file:
      file.write(json.dumps(self.serversDict, sort_keys=True, indent=2))

  def readServersFile(self, filename):
    with open(filename, 'r') as file:
      self.serversDict = json.load(file)

  def fakeServers(self):
    self.serversDict = {
        'F1_1979_Official_Server_1' : ['46.9.118.148', 62299],
        'F1_1979_Official_Server_2' : ['46.9.118.149', 64399],
        'RSVRsig-racing.boards.net' : ['86.163.28.215', 64299]
        }

  def getServerAddress(self, serverName):
    try:
      _addr = self.serversDict[serverName][0]
    except KeyError:
      _addr = 'ServerNotFound'
    return _addr

  def getServerPort(self, serverName):
    try:
      _port = self.serversDict[serverName][1]
    except KeyError:
      _port = 0
    return _port

  def getServerStatus(self, serverName):
    """
    Read the server status, return
    Idle (No players on the server)
    Active (and load self.players with the names)
    ServerNotInList
    NoResponse
    """
    status, humans, AI, probables, info = self.getPlayerCounts(serverName)
    if not status == 'OK':
      return 'Idle', status
    track = info['map']

    if humans + AI + probables == 0:
      _status = 'Idle'
    if humans == 0:
      _status = 'Active but only AI drivers'
    else:
      _status = 'Active'
    return _status, track

  """
  What is needed (certainly for debugging) is a generator that returns servers one by one.
  For debugging the real data should be read and then pickled so that the real data
  can be unpickled much more quickly.  That's _server.info() and _server.players()
  """

  def getPlayerCounts(self, serverName):
    """
    Read the server status, return
      number of apparent human players
      number of AI players (names in drivers.txt)
      number of probable AI players (on the server for exactly the same time)
      Track name
      Maximum number of players
    """
    humans = 0
    AI = 0 
    probables = 0

    if serverName in self.serversDict:
      for retry in range(3):
        try:

          _server = valve.source.a2s.ServerQuerier(self.serversDict[serverName])
          try:
            info = _server.info()
            if info['player_count'] != 0:
              self.players = []
              players = _server.players()
              _server.close()

            
              AI = info['player_count'] # initialise to "all players"
              if info['player_count'] > 1:
                # Check for players who've been playing for exactly the same time - they're AI
                _durations = []
                for p in range(players.values['player_count']):
                  _durations.append(players.values['players'][p].values['duration'])
                _durations.sort(reverse=True)
                for p in range(players.values['player_count']):
                  ################################################# disable test
                  if 0 and _durations[0] == _durations[1] and \
                    players.values['players'][p].values['duration'] == _durations[0]:
                      probables += 1
                      AI -= 1
                      # Write this AI player's name
                      ### self.driverFilter.addAI(players.values['players'][p].values['name'])
                      #debug print(players.values['players'][p].values['name'], end=" ")
                      #debug print(_durations[0])
                  else:
                    _player = players.values['players'][p].values['name']
                    if self.driverFilter.match(_player) == 'Human':
                      humans += 1
                      AI -= 1
                      self.players.append(_player)
            if retry:
              print('---> Server %s retry succeeded #%d' % (serverName, retry))
            return 'OK', humans, AI, probables, info
          except valve.source.a2s.NoResponseError:
            _server.close()
            pass

        except valve.source.a2s.NoResponseError:
          _server.close()
          pass
          print('---> Server %s timed out' % (serverName))
    else: # serverName not in self.serversDict
      return 'ServerNotInList', 0,0,0, 'ServerNotInList'
    return 'NoResponse', 0,0,0, 'NoResponse'

  def getServerNames(self):
    return self.serversDict

  def getServerAddresses(self):
    return self.addresses

class DriversFilter:
  """
  Use a file of names of AI drivers to check whether a driver is human.
  """
  def __init__(self, _driversFileName):
    self._driversFileName = _driversFileName
    try:
      with open(_driversFileName, 'r') as file:
        self.drivers = file.read().splitlines()
    except FileNotFoundError:
      print('Could not open "%s"' % _driversFileName)
      self.drivers = []
  def match(self, _driversName):
    if _driversName in self.drivers:
      return 'AI'
    return 'Human'
  def addAI(self, _AIname):
    if not _AIname in self.drivers:
      self.drivers.append(_AIname)
      try:
        with open(self._driversFileName, 'w') as file:
          _drivers = '\n'.join(self.drivers)
          file.write(_drivers)
      except:
        print('Could not write to "%s"' % self._driversFileName)

def readServersFile():
  serversFilename = 'servers.file.json'
  try:
    serverObj = Servers()
    if not os.path.isfile(serversFilename):
      print('Stored file of available servers %s does not exist, creating it. This will take a couple of minutes...' % serversFilename)
      serverObj.readServers()
      serverObj.readServerNames()
      serverObj.writeServersFile(serversFilename)
    serverObj.readServersFile(serversFilename)
    return serverObj
  except:
    print('Failed to read %s. Exiting.' % serversFilename)
    sys.exit(99)

def readSpecificServer(serverName):
  serverObj = Servers()
  return serverObj.readSpecificServer(serverName)

def readNonEmptyServers():
  serverObj = Servers()
  serverObj.readServers(notEmpty=True)
  return serverObj

def alert(_server, _driver):
  pymsgbox.alert('%s' % _driver, '%s is active' % _server)

if __name__ == '__main__':
  if len(sys.argv) > 1:
    fname = sys.argv[1]
  else:
    fname = 'rF2_serverNotify.json'

  print('rF2_serverNotify V0.6')
  print('=====================')
  print('Using config file %s\n' % fname)

  serverObj = readServersFile()

  try:
    configFileO = JSONconfigFile(fname)
  except:
    print('Usage: %s <rF2_serverNotify config file>' % os.path.basename(sys.argv[0]))
    print('The config file must be a JSON file.')
    raise
  serversDict = configFileO.getServers()
  interval = configFileO.getInterval()

  print('Press Esc to quit (only checked every %dS)' % interval)

  # formatting
  _longestServerName = 0
  serversFilename = 'servers.file.json'   # this is a hack to overcome a change I made.
  for server, status in serversDict.items():
    if len(server) > _longestServerName:
      _longestServerName = len(server)

  while True:
    _time = datetime.datetime.now().strftime('%I:%M %p')
    print('\nAt %s these servers were idle (checking at %dS intervals):' % (_time, interval))
    for server, status in serversDict.items():
      status, track = serverObj.getServerStatus(server) 
      if status == 'Active':
        alert(server, serverObj.players)
        sys.exit(0)
      elif status  == 'Idle':
        print('%-*s  Idle' % (_longestServerName, server))
      elif status  == 'Active but only AI drivers':
        print('%-*s  Active but only AI drivers' % (_longestServerName, server))
      elif status == 'ServerNotInList':
        print('%-*s  not in server list %s' % (_longestServerName, server, serversFilename))
      else:
        print('%-*s  did not respond' % (_longestServerName, server))

    if kbhit() and getch() == b'\x1B':
      print('\nEsc pressed')  # Quit
      sys.exit(1)
    time.sleep(interval)
