import os
import sys
import datetime
import json
import pymsgbox
import time
from msvcrt import kbhit, getch

import valve.source.a2s
import valve.source.master_server
        
class configFile:
  def __init__(self, fname):
    try:
      with open(fname) as f:
          self.records = f.read().splitlines()
    except:
      _errStr = 'Could not open "%s" to read' % os.path.join(os.getcwd(), fname)
      print(_errStr)
      self.records = [_errStr]
      #sys.exit(99)
    self.dict = {key: "Idle" for key in self.records}
  def read(self):
    return self.records[0]
  def setStatus(self, server, status):
    try:
      self.dict[server] = status
    except:
      pass
  def getStatus(self, server):
    try:
      ret = self.dict[server]
    except KeyError:
      ret = "Idle"
    return ret


class JSONconfigFile:
  """
  Two types of dictionary entries in the JSON file
  a) ServerX : 'name of server to be scanned'
      There can be any number of Server entries.
      Text beyond 'Server' is ignored.
  b) Interval : 30   
      seconds between checking the servers
  """
  def __init__(self, fname):
    #try:
    with open(fname, 'r') as file:
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
  def setStatus(self, server, status):
    try:
      self.dict[server] = status
    except:
      pass
  def getStatus(self, server):
    try:
      ret = self.dict[server]
    except KeyError:
      ret = "Idle"
    return ret
  def getInterval(self):
    return self.interval
    
class servers:
  def __init__(self):
    pass
  def readServers(self, masterServer = None):
    msq = valve.source.master_server.MasterServerQuerier()
    self.serversDict = {}
    for address in msq.find(appid = '365960'):
        #region=["eu", "as"], gamedir="rFactor 2"):
        #print ("{0}:{1}".format(*address))
        try:
          server = valve.source.a2s.ServerQuerier(address)
          info = server.get_info()
          serverName = info["server_name"]
          self.serversDict[serverName] = address
        except valve.source.a2s.NoResponseError:
          pass
          #print('%s:%d timed out' % SERVER_ADDRESS)
          
  def writeServersFile(self, filename):
    with open(filename, 'w') as file:
      file.write(json.dumps(self.serversDict, sort_keys=True, indent=2))

  def readServersFile(self, filename):
    with open(filename, 'r') as file:
      self.serversDict = json.load(file)
  
#  def _getServers_TEST(self):
#    return self.serversDict

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
    if serverName in self.serversDict:
      try:
        #print(SERVER_ADDRESS)

        server = valve.source.a2s.ServerQuerier(self.serversDict[serverName])
        try:
          info = server.get_info()
          if info["player_count"] == 0:
            return "Idle"
          ########## UGH!
          players = server.get_players()
          for player in sorted(players["players"],
                   key=lambda p: p["score"], reverse=True):
              self.player = ' '.join(("{score} {name}".format(**player)).split()[1:])
          ########## UGH!
          return "Active"
        except valve.source.a2s.NoResponseError:
          pass

      except valve.source.a2s.NoResponseError:
        pass
        #print('%s:%d timed out' % SERVER_ADDRESS)
    return "Idle"

def alert(server, driver):
  pymsgbox.alert("%s is on the server!" % driver, '%s is active' % server)

if __name__ == '__main__':
  serversFilename = 'servers.file.json'
  if len(sys.argv) > 1:
    fname = sys.argv[1]
  else:
    fname = 'rF2_serverNotify.json'
  
  print('Using config file %s\n' % fname)

  try:
    configFileO = JSONconfigFile(fname)
    serverObj = servers()
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
        alert(server, serverObj.player)
        sys.exit(0)
      print('"%s"'% server)
    if kbhit() and getch() == b'\x1B':
      print('\nEsc pressed')
      sys.exit(1)
    time.sleep(interval)


