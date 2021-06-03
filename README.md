[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-no-red.svg)](https://bitbucket.org/lbesson/ansi-colors)
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

<b>Also...</b>

# rF2_serversWithHumans
Similar but scans a set of rFactor 2 servers and lists the servers with probable human drivers, defined as drivers who are not in 
the AI list "drivers.txt".

# rF2_joinServer
Join a race on an rFactor 2 server directly, bypassing the lobby, automatically enters the password.  

The command required is

"C:/Program Files (x86)/Steam/steam.exe" -applaunch 365960 +autojoin="SERVER_NAME" +connect=:PASSWORD@IP_ADDRESS:PORT +multiplayer +path=".."

(Note the use of / instead of \ as \ is the escape character for Python strings.  Windows doesn't care.)

SERVER_NAME and PASSWORD are provided in a data file (defaults to rF2_joinServer.json but you can specify it when calling the program), the program reads the server's IP_ADDRESS and PORT to assemble the complete command and execute it.

Example rF2_joinServer.json 
<br>
{<br>
  <b>"Server"</b> : "FTR Nissan Cup",<br>
  <b>"SteamExe"</b> : "C:/Program Files (x86)/Steam/steam.exe" ,<br>
  <b>"Password"</b> : ""<br>
}<br>

(A password is not required for this server.)
