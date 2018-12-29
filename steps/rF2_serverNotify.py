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
import pymsgbox
from multiprocessing.dummy import Pool as ThreadPool 

import valve.source.a2s
import valve.source.master_server

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
    for key, value in self.serversDict.items():   # iter on both keys and values
      #print(key, value)
      if key.startswith('Server'):
        self.dict[value] = 'Idle'
      if key == 'Interval':
        self.interval = value

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
    return self.interval

class Servers:
  """
  Gets the list of all servers and their addresses.
  Writes/reads the info to a data file (as it takes a couple of minutes
  to read them from Steam).
  Gets the status of a particular server.
  """
  def __init__(self):
    self.serversDict = {}
    self.players = ''
    self.driverFilter = DriversFilter('drivers.txt')
  def readServer(self, address):
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
    print('%s:%d timed out' % address)
    return address, 'Timed out'
  def readServers(self):
    msq = valve.source.master_server.MasterServerQuerier()
    addresses = []
    all_addresses = msq.find(appid='365960')
    for address in all_addresses:
      addresses.append(address)

    # Multi-thread querying all servers to speed things up
    # (perhaps at the cost of missing some servers).
    # make the Pool of workers
    pool = ThreadPool(len(addresses)//10) 

    # read the servers in their own threads
    # and return the results
    results = pool.map(self.readServer, addresses)

    # close the pool and wait for the work to finish 
    pool.close() 
    pool.join() 

    for r in results:
      if r[1] != 'Timed out':
        self.serversDict[r[1]] = r[0]
    pass

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
    if serverName in self.serversDict:
      try:

        _server = valve.source.a2s.ServerQuerier(self.serversDict[serverName])
        try:
          info = _server.info()
          _track = info['map']
          _status = 'Idle'
          if info['player_count'] != 0:
            _status = 'Active but only AI drivers'
            self.players = 'On the server:'
            players = _server.players()
            
            # Check for players who've been playing for exactly the same time - they're AI
            _duration = players.values['players'][0].values['duration']
            for p in range(1, players.values['player_count']):
              if players.values['players'][p].values['duration'] == _duration:
                # Write player[0]'s name
                self.driverFilter.addAI(players.values['players'][0].values['name'])
                # Write this AI player's name
                self.driverFilter.addAI(players.values['players'][p].values['name'])

            for p in range(players.values['player_count']):
              _player = players.values['players'][p].values['name']
              if self.driverFilter.match(_player) == 'Human':
                self.players += '\n' + _player
                _status = 'Active'
          return _status, _track
        except valve.source.a2s.NoResponseError:
          pass

      except valve.source.a2s.NoResponseError:
        pass
        #print('%s:%d timed out' % SERVER_ADDRESS)
    else: # serverName not in self.serversDict
      return 'ServerNotInList', 'ServerNotInList'
    return 'NoResponse', 'NoResponse'

  def getServerNames(self):
    return self.serversDict

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
      serverObj.writeServersFile(serversFilename)
    serverObj.readServersFile(serversFilename)
    return serverObj
  except:
    print('Failed to read %s. Exiting.' % serversFilename)
    sys.exit(99)

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

  try:
    configFileO = JSONconfigFile(fname)
    serverObj = rF2_serverNotify.readServersFile()

    serversDict = configFileO.getServers()
    interval = configFileO.getInterval()

  except:
    print('Usage: %s <rF2_serverNotify config file>' % os.path.basename(sys.argv[0]))
    print('The config file must be a JSON file.')
    raise

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
      if serverObj.getServerStatus(server) == 'Active':
        alert(server, serverObj.players)
        sys.exit(0)
      elif serverObj.getServerStatus(server) == 'Idle':
        print('%-*s  Idle' % (_longestServerName, server))
      elif serverObj.getServerStatus(server) == 'Active but only AI drivers':
        print('%-*s  Active but only AI drivers' % (_longestServerName, server))
      elif serverObj.getServerStatus(server) == 'ServerNotInList':
        print('%-*s  not in server list %s' % (_longestServerName, server, serversFilename))
      else:
        print('%-*s  did not respond' % (_longestServerName, server))

    if kbhit() and getch() == b'\x1B':
      print('\nEsc pressed')  # Quit
      sys.exit(1)
    time.sleep(interval)
