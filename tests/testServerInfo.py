import sys
import unittest

rF2_serverNotify_path = r'..\rF2_serverNotify\steps'
sys.path.append(rF2_serverNotify_path)
from rF2_serverNotify import Servers

class Test_testServerInfo(unittest.TestCase):
  def test_readServer(self):
      serverName = 'S397 Open - Formula E'
      serverName = 'GTItalia_Srv3'
      serverName = 'Youlbi Challenge Bathurst'
      serverName = "ILS | GoBag GT3 Cup"
      s_o = Servers()
      address = s_o.readSpecificServer(serverName)
      info,players = s_o.readServerInfo(address)
      if info:
        print(info['player_count'])
        print(info['max_players'])
        print(info['password_protected'])
      if players:
        for p in range(players.values['player_count']):
          _player = players.values['players'][p].values['name']
          print(_player)
      pass
      

if __name__ == '__main__':
  unittest.main()

