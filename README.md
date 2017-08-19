# rF2_serverNotify
Scan a set of rFactor 2 servers and send a notification if someone joins a server that had no drivers.

rF2_serverNotify.json has two types of dictionary entry:
  a) ServerX : 'name of server to be scanned'
      There can be any number of Server entries.
      Text beyond 'Server' is ignored.
  b) Interval : 30   
      seconds between checking the servers

servers.file.json contains all the servers and their addresses. 
It is created automatically the first time the program is run.

Also included are the Behave BDD files used to write the code.
