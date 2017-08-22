# pylint: skip-file
import rF2_serverNotify

#######################################################
# Notification file tests
@given(u'I have the file name "{string}"')
def step_impl(context, string):
  context.fileName = string

@when(u'the text file is read')
def step_impl(context):
  context.configFile = rF2_serverNotify.configFile(context.fileName)
  context.serverNames = context.configFile.read()

@then(u'I see the result "{string}"')
def step_impl(context, string):
  assert context.serverNames == string, \
    "Got %s" % context.serverNames

@when(u'the server "{server}" is "{status}"')
def step_impl(context, server, status):
    context.configFile.setStatus(server, status)

@then(u'I see the status "{server}" is "{status}"')
def step_impl(context, server, status):
  _readStatus = context.configFile.getStatus(server)
  assert _readStatus == status, \
    "Got %s" % _readStatus


#######################################################
# JSON config file tests
@when(u'the JSON file is read')
def step_impl(context):
  context.configFile = rF2_serverNotify.JSONconfigFile(context.fileName)
  context.serverNames = context.configFile.read()

@then(u'I see the interval 30')
def step_impl(context):
    assert context.configFile.getInterval() == 30


#######################################################
# Live server tests
@when(u'the server "{server}" is read')
def step_impl(context, server):
  _readStatus = context.serverObj.getServerStatus(server)
  context.configFile.setStatus(server, _readStatus)

# Servers and servers file tests
@when(u'the servers are read')
def step_impl(context):
  # read the real list of servers - takes a few minutes
  context.serverObj = rF2_serverNotify.Servers()
  context.serverObj.readServers()

@when(u'the servers file is set up')
def step_impl(context):
  context.serverObj = rF2_serverNotify.Servers()

@when(u'the servers are faked')
def step_impl(context):
  context.serverObj = rF2_serverNotify.Servers()
  context.serverObj.fakeServers()

@when(u'the servers file is written')
def step_impl(context):
    context.serverObj.writeServersFile('servers.file.json')

@when(u'the servers file is read')
def step_impl(context):
    context.serverObj.readServersFile('servers.file.json')

@when(u'the fake servers file is written')
def step_impl(context):
    context.serverObj.writeServersFile('fake.servers.file.json')

@when(u'the fake servers file is read')
def step_impl(context):
    context.serverObj.readServersFile('fake.servers.file.json')

@then(u'the servers match the fake servers')
def step_impl(context):
  _readServers = context.serverObj.serversDict
  context.serverObj.fakeServers()
  _fakeServers = context.serverObj.serversDict
  print(_readServers)
  print(_fakeServers)
  assert _readServers == _fakeServers
  #assert __equal(_readServers, _fakeServers)



@then(u'I see the address for "{server}" is "{address}"')
def step_impl(context, server, address):
  _readAddress = context.serverObj.getServerAddress(server)
  assert _readAddress == address, \
    "Got %s" % _readAddress

@then(u'I see the port for "{server}" is {port}')
def step_impl(context, server, port):
  _readPort = context.serverObj.getServerPort(server)
  assert _readPort == int(port), \
    "Got %s" % _readPort

#######################################################
# AI driver filter
@given(u'I have the drivers file name "{driversTxtFile}"')
def step_impl(context, driversTxtFile):
  context.driversTxtFile = driversTxtFile

@when(u'the drivers file is read')
def step_impl(context):
  context.DFo = rF2_serverNotify.DriversFilter(context.driversTxtFile)
  assert context.DFo.match('A J Foyt') == "AI"

@when(u'the filter is "{driver}"')
def step_impl(context, driver):
  context.driver = driver

@then(u'I see the driver status "{status}"')
def step_impl(context, status):
  assert context.DFo.match(context.driver) == status
