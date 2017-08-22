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
        self.dict[value] = "Idle"
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
      ret = "Idle"
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
  def readServers(self):
    msq = valve.source.master_server.MasterServerQuerier()
    for address in msq.find(appid='365960'):
      #region=["eu", "as"], gamedir="rFactor 2"):    Didn't work
      #print ("{0}:{1}".format(*address))
      try:
        _server = valve.source.a2s.ServerQuerier(address)
        info = _server.get_info()
        serverName = info["server_name"]
        self.serversDict[serverName] = address
      except valve.source.a2s.NoResponseError:
        pass
        #  Debug print('%s:%d timed out' % SERVER_ADDRESS)

  def writeServersFile(self, filename):
    with open(filename, 'w') as file:
      file.write(json.dumps(self.serversDict, sort_keys=True, indent=2))

  def readServersFile(self, filename):
    with open(filename, 'r') as file:
      self.serversDict = json.load(file)

  def fakeServers(self):
    self.serversDict = {
        "F1_1979_Official_Server_1" : ['46.9.118.148', 62299],
        "F1_1979_Official_Server_2" : ['46.9.118.149', 64399],
        "RSVRsig-racing.boards.net" : ['86.163.28.215', 64299]
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
    NoResponse
    """
    if serverName in self.serversDict:
      try:

        _server = valve.source.a2s.ServerQuerier(self.serversDict[serverName])
        try:
          info = _server.get_info()
          _status = 'Idle'
          if info["player_count"] != 0:
            _status = 'Active but only AI drivers'
            self.players = 'On the server:'
            players = _server.get_players()
            for p in range(players.values['player_count']):
              _player = players.values['players'][p].values['name']
              if self.driverFilter.match(_player) == 'Human':
                self.players += '\n' + _player
                _status = "Active"
          return _status
        except valve.source.a2s.NoResponseError:
          pass

      except valve.source.a2s.NoResponseError:
        pass
        #print('%s:%d timed out' % SERVER_ADDRESS)
    return "NoResponse"

class DriversFilter:
  """
  Use a file of names of AI drivers to check whether a driver is human.
  """
  def __init__(self, _driversFileName):
    try:
      with open(_driversFileName, 'r') as file:
        self.drivers = file.read().splitlines()
    except FileNotFoundError:
      print('Could not open "%s"' % _driversFileName)
      self.drivers = []
  def match(self, _driversName):
    if _driversName in self.drivers:
      return "AI"
    return "Human"


def alert(_server, _driver):
  pymsgbox.alert("%s" % _driver, '%s is active' % _server)

if __name__ == '__main__':
  serversFilename = 'servers.file.json'
  if len(sys.argv) > 1:
    fname = sys.argv[1]
  else:
    fname = 'rF2_serverNotify.json'

  print('Using config file %s\n' % fname)

  try:
    configFileO = JSONconfigFile(fname)
    serverObj = Servers()
    if not os.path.isfile(serversFilename):
      print('Finding available servers.  This may take a couple of minutes..')
      serverObj.readServers()
      serverObj.writeServersFile(serversFilename)
    serverObj.readServersFile(serversFilename)

    serversDict = configFileO.getServers()
    interval = configFileO.getInterval()

  except:
    print('Usage: %s <rF2_serverNotify config file>' % os.path.basename(sys.argv[0]))
    print('The config file must be a JSON file.')
    raise

  print('Press Esc to quit (only checked every %dS)\n' % interval)

  while True:
    _time = datetime.datetime.now().strftime('%I:%M %p')
    print('At %s these servers were idle (checking at %dS intervals):' % (_time, interval))
    for server, status in serversDict.items():
      if serverObj.getServerStatus(server) == "Active":
        alert(server, serverObj.players)
        sys.exit(0)
      elif serverObj.getServerStatus(server) == "Idle":
        print('"%s" Idle'% server)
      elif serverObj.getServerStatus(server) == "Active but only AI drivers":
        print('"%s" Active but only AI drivers'% server)
      else:
        print('"%s" did not respond'% server)

    if kbhit() and getch() == b'\x1B':
      print('\nEsc pressed')  # Quit
      sys.exit(1)
    time.sleep(interval)
