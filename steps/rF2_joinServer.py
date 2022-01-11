"""
A simple Python program join a race on an rFactor 2 server.  The command is

"C:\Program Files (x86)\Steam\steam.exe" -applaunch 365960 +autojoin="SERVER_NAME" +connect=:PASSWORD@IP_ADDRESS:PORT +multiplayer +path=".."

SERVER_NAME and PASSWORD are provided in a data file, this program reads
the server's IP_ADDRESS and PORT to assemble the complete command and execute it.

A data file servers.file.json is created automatically the first time
 the program is run.
It contains all the servers and their addresses.
"""
from __future__ import print_function  # Python 2 compatibility

import json
import subprocess
import sys
from   msvcrt import getch

import rF2_serverNotify

BUILD_REVISION = 38 # The git commit count
versionStr = 'rF2_joinServer V0.3.%d' % BUILD_REVISION
versionDate = '2020-04-25'

class JSONconfigFile:
  """
  Three dictionary entries in the JSON file
  a) SteamExe : "C:/Program Files (x86)/Steam/steam.exe"
  b) Server :   'name of server to join'
  c) Password : letmein

  """
  def __init__(self, _fname):
    #try:
    self.SteamExe = None
    self.server   = None
    self.password = None

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
      if key == 'SteamExe':
        self.SteamExe = value
      elif key == 'Server':
        self.server = value
      elif key == 'Password':
        self.password = value
      else:
        print('Bad key "%s" in %s' % (key, _fname))

def runRf2Online(SteamExe, serverName, password):
  _ip_address,_port = rF2_serverNotify.readSpecificServer(serverName)
  _port = str(int(_port)-2)  # No idea why -2 is necessary but it works.

  if _ip_address != 'ServerNotFound':
    _cmd =  '"%s" -applaunch 365960 +autojoin="%s" +connect=:%s@%s:%s +multiplayer +path=".."' % (SteamExe, serverName, password, _ip_address, _port)
    print(_cmd)
    subprocess.Popen(_cmd)  # Popen doesn't wait for completion (Steam closed)
    _status = 'OK'
  else:
    _status = ('Server "%s" not found' % serverName)
  return _status 

if __name__ == '__main__':

  print(versionStr)
  print('=' * len(versionStr))

  if len(sys.argv) > 1:
    fname = sys.argv[1]
  else:
    fname = 'rF2_joinServer.json'

  print('Using config file %s\n' % fname)

  #try:
  configFileO = JSONconfigFile(fname)

  status = runRf2Online(configFileO.SteamExe, configFileO.server, configFileO.password)
  print(status)
  
  print('\n\nAll done. Press a key...')
  getch()

