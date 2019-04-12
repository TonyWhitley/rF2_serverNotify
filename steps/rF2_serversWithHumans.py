"""
A simple Python program to scan a set of rFactor 2 servers and list the
servers with probable human drivers, defined as drivers who are not in 
the AI list "drivers.txt".

A data file servers.file.json is created automatically the first time
 the program is run.
It contains all the servers and their addresses.
"""
from __future__ import print_function  # Python 2 compatibility

import sys
from msvcrt import kbhit, getch
from multiprocessing.dummy import Pool as ThreadPool 

import rF2_serverNotify

BUILD_REVISION = 34 # The git commit count
versionStr = 'rF2_serversWithHumans V0.4.%d' % BUILD_REVISION
versionDate = '2019-04-11'

class ServerQuery:
  def __init__(self):
    print('Finding non-empty servers...')
    self.serverObj = rF2_serverNotify.readNonEmptyServers()
    print('Reading server names... (though we don\'t really need to)')
    self.serverObj.readServerNames()
    self.newNames = []

    print('\nPress Esc to quit')

    servers = self.serverObj.getServerNames()
  
    if 0:
      # Multi-thread querying all servers to speed things up
      # (perhaps at the cost of missing some servers).
      # make the Pool of workers
      pool = ThreadPool(len(servers)//10) 

      # read the servers in their own threads
      # and return the results
      results = pool.map(self.serverIsActive, servers)

      # close the pool and wait for the work to finish 
      pool.close() 
      pool.join() 
    else:
      for server in servers:
        #print('Checking server "%s"' % server)
        self.serverIsActive(server)
    
  def serverIsActive(self, server):
    _status,_track = self.serverObj.getServerStatus(server) 
    if _status == 'Active':
      print('\nServer: %s (%s)\nhas these drivers who are not in the AI list "drivers.txt"' % (server, _track))
      #print(self.serverObj.players)
      for player in self.serverObj.players:
        if 0: # player in self.newNames:
          # Player name found on two servers simultaneously - must be AI
          # Add this AI player's name to drivers.txt
          self.serverObj.driverFilter.addAI(player)
          print('"%s" added to drivers.txt' % player)
        else:
          self.newNames.append(player)
          print(player)


    if kbhit() and getch() == b'\x1B':
      print('\nEsc pressed')  # Quit
      sys.exit(1)



if __name__ == '__main__':

  print(versionStr)
  print('=' * len(versionStr))

  ServerQuery()

  print('\n\nAll done. Press a key...')
  getch()
