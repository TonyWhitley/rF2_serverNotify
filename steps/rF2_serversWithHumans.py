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
from   msvcrt import kbhit, getch

import rF2_serverNotify

if __name__ == '__main__':

  print('rF2_serversWithHumans V0.3')
  print('==========================')
  serverObj = rF2_serverNotify.readServersFile()

  print('\nPress Esc to quit')

  for server in serverObj.getServerNames():
    _status,_track = serverObj.getServerStatus(server) 
    if _status == 'Active':
      print('\nServer: %s (%s)\nhas these drivers who are not in the AI list "drivers.txt"' % (server, _track))
      print(serverObj.players)

    if kbhit() and getch() == b'\x1B':
      print('\nEsc pressed')  # Quit
      sys.exit(1)
  print('\n\nAll done. Press a key...')
  getch()
