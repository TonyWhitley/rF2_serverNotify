# rF2_serverNotify
Scan a set of rFactor 2 servers and send a notification if someone joins a server that had no drivers.

The progam is configured by the file <i>rF2_serverNotify.json</i> which has two types of dictionary entry:<br>
  a) Server<i>X</i> : '<i>name of server to be scanned</i>'<br>
      There can be any number of Server entries.<br>
      Text beyond <i>Server</i> is ignored.<br>
  b) Interval : 30<br>
      seconds between checking the servers<br>

A data file <i>servers.file.json</i> is created automatically the first time the program is run.<br>
It contains all the servers and their addresses.<br>

<i>(Also included are the Behave BDD files used to write the code.)</i>
