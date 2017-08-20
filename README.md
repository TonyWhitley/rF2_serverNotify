# rF2_serverNotify
A simple program to scan a set of rFactor 2 servers and pop up a notification if someone joins a server that had no drivers.

The program is configured by the file <i>rF2_serverNotify.json</i> which should be edited with the server(s) of interest.<br>
It has two types of dictionary entry:<br>
  <b>a) Server<i>X</i></b> : '<i>name of server to be scanned</i>'<br>
      There can be any number of Server entries.<br>
      Text beyond <i>Server</i> is ignored, it's just needed to make each entry different.<br>
  <b>b) Interval</b> : 30<br>
      seconds between checking the servers<br>

A data file <i>servers.file.json</i> is created automatically the first time the program is run.<br>
It contains all the servers and their addresses.<br>

Click on the Releases tab to find an .exe file created from the Python with pyinstaller and a sample rF2_serverNotify.json.<br><br>
<i>(Also included are in the source the Behave BDD files used to write the code.)</i>
