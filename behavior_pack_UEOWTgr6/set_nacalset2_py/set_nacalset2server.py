# -*- coding: utf-8 -*-
import modConfig
import random
import copy
import mod.server.extraServerApi as serverApi
from mod_log import logger as logger

ServerSystem = serverApi.GetServerSystemCls()


class set_nacalset2se(ServerSystem):

    def __init__(self, namespace, systemName):
        super(set_nacalset2se, self).__init__(namespace, systemName)
        self.ListenEvent()
        self.levelid = serverApi.GetLevelId()

    def ListenEvent(self):
        print("ListenEvent")
        #self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "", self, self.)
        self.ListenForEvent(serverApi.GetEngineNamespace(),
                            serverApi.GetEngineSystemName(), "ServerChatEvent",
                            self, self.ServerChatEvent)
        #self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "LoadServerAddonScriptsAfter", self, self.LoadServerAddonScriptsAfter)
        self.ListenForEvent(serverApi.GetEngineNamespace(),
                            serverApi.GetEngineSystemName(),
                            "ClientLoadAddonsFinishServerEvent", self,
                            self.ClientLoadAddonsFinishServerEvent)
        self.ListenForEvent(modConfig.ModName, modConfig.ModName + "temc",
                            "save_data", self, self.save_data)

    def ClientLoadAddonsFinishServerEvent(self, args):
        '''a = {
			"mod_id": "ws_test",
			"mod_name": "测试模组",
			"set_class_order":['xlk_test','xlk_test2'],
			"set_class": {
				"xlk_test": {
					"class_name": "下拉框测试",
					"class_text": "下拉框选项",
					"class_image": "textures/blocks/dirt",
					"set_list_order":['xlk','xlk2','hdt1','hdt2'],
					"set_list": {
						"xlk": {
							"ui_type": 'Button',
							"data_type":None,
							"need_op_level": 2,
							"text": "测试用按钮",
							'button_type': "reset_class_data"
						},
						"xlk2": {
							"data_type": 'single_choice',
							"ui_type": 'ComboBoxUIControl',
							"save_place": "client_player",
							"need_op_level": 2,
							"default_data": 'xx8',
							"text": "选择erfrfrre",
							"data_order":['xx1','xx2','xx3','xx4','xx5','xx6','xx7','xx8'],
							"data": {
								'xx1': "啊",
								'xx2': "额",
								'xx3': "人",
								'xx4': "去",
								'xx5': "啊44",
								'xx6': "额5",
								'xx7': "人66",
								'xx8': "去875"
							}
						},
						"hdt1": {
							"data_type": 'range_number',
							"ui_type": 'Slider',
							"save_place": "client_player",
							"need_op_level": 2,
							"default_data": 5,
							"step":1,
							"min":0,
							"max":10,
							"handle":"become_int",
							"text": "0到10",
							"data": {
								0:'最低',
								10:'最大'
							}
						},
						"hdt2": {
							"data_type": 'single_choice',
							"ui_type": 'Slider',
							"save_place": "client_player",
							"need_op_level": 2,
							"default_data": 'a',
							"text": "abc",
							"data_order":["a",'b','c'],
							"data": {
								'a':'aaa',
								'b':'bbb',
								'c':'ccc'
							}
						}
					}
				},
				"xlk_test2": {
					"class_name": "下拉框测试2",
					"class_text": "下拉框选项2",
					"class_image": "textures/blocks/bedrock",
					"set_list_order":['xlk3','srk','srk2','wb'],
					"set_list": {
						"xlk3": {
							"data_type": 'bool',
							"ui_type": 'SwitchToggle',
							"save_place": "client_player",
							"need_op_level": 2,
							"default_data": True,
							"text": "测试2"
						},
						"srk": {
							"data_type": 'range_number',
							"handle":"become_int",
							"ui_type": 'TextEditBox',
							"save_place": "client_player",
							"need_op_level": 2,
							"default_data": 10,
							"text": "qwertyui",
							"min":0,
							"max":20,
							"max_length":2
						},
						"srk2": {
							"data_type": 'character_string',
							"handle":"none",
							"ui_type": 'TextEditBox',
							"save_place": "client_player",
							"need_op_level": 2,
							"default_data": 10,
							"text": "qqqq",
							"min":0,
							"max":20,
							"max_length":10
						},
						"wb": {
							"data_type": 'none',
							"ui_type": 'Label',
							"text": "这是一段文本\n第二行\n第三行"
						}
					}
				}
			}
		}
		self.player = serverApi.GetPlayerList()
		self.reload_set_data({'data':a,'pid':args['playerId']})'''

        comp3 = serverApi.GetEngineCompFactory().CreateGame(self.levelid)
        comp3.AddRepeatedTimer(0.5, self.state_to_client)

    def state_to_client(self):
        dic = {}
        self.player = serverApi.GetPlayerList()
        for pid in self.player:
            comp = serverApi.GetEngineCompFactory().CreatePlayer(pid)
            dic['op'] = comp.GetPlayerOperation()
            self.NotifyToClient(pid, "get_server_state", dic)

    def ServerChatEvent(self, args):
        if args['message'] == '模组配置':
            self.NotifyToClient(args['playerId'], "dk", None)

    def save_data(self, args):
        comp = serverApi.GetEngineCompFactory().CreateExtraData(args[2])
        comp.SetExtraData('mod_' + args[0] + '_set', args[1])

    def reload_set_data(self, args):
        self.player = serverApi.GetPlayerList()
        comp = serverApi.GetEngineCompFactory().CreateExtraData(self.levelid)
        if comp.GetExtraData('mod_' + args['data']['mod_id'] + '_set') == None:
            comp.SetExtraData('mod_' + args['data']['mod_id'] + '_set', {})
        args['l_data'] = comp.GetExtraData('mod_' + args['data']['mod_id'] +
                                           '_set')
        comp = serverApi.GetEngineCompFactory().CreateExtraData(
            args['player_id'])
        if comp.GetExtraData('mod_' + args['data']['mod_id'] + '_set') == None:
            comp.SetExtraData('mod_' + args['data']['mod_id'] + '_set', {})
        args['p_data'] = comp.GetExtraData('mod_' + args['data']['mod_id'] +
                                           '_set')
        self.NotifyToClient(args['player_id'], 'reload_set_data', args)

    def GetServerWorldData(self, mod_id):
        comp = serverApi.GetEngineCompFactory().CreateExtraData(self.levelid)
        data = comp.GetExtraData('mod_' + mod_id + '_set')
        return data

    def GetServerPlayerData(self, mod_id, player_id):
        comp = serverApi.GetEngineCompFactory().CreateExtraData(player_id)
        data = comp.GetExtraData('mod_' + mod_id + '_set')
        return data
