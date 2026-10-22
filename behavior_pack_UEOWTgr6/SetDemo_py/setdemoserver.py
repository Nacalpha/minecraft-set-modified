# -*- coding: utf-8 -*-
# 演示模组的服务端系统：客户端加载完成后，把设置表交给设置模块
import mod.server.extraServerApi as serverApi
import demo_config
import demo_setdic

ServerSystem = serverApi.GetServerSystemCls()


class SetDemoServer(ServerSystem):

    def __init__(self, namespace, systemName):
        super(SetDemoServer, self).__init__(namespace, systemName)
        self.ListenEvent()

    def ListenEvent(self):
        self.ListenForEvent(serverApi.GetEngineNamespace(),
                            serverApi.GetEngineSystemName(),
                            "ClientLoadAddonsFinishServerEvent", self,
                            self.ClientLoadAddonsFinishServerEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(),
                            serverApi.GetEngineSystemName(), "ServerChatEvent",
                            self, self.ServerChatEvent)

    def ClientLoadAddonsFinishServerEvent(self, args):
        # 不把设置表交给设置模块的话，设置界面打开是空的
        sys = serverApi.GetSystem(demo_config.SetModName,
                                  demo_config.SetServerSystem)
        if sys is None:
            print("[演示] 没找到设置模块的服务端系统")
            return
        sys.reload_set_data({
            'data': demo_setdic.setdic,
            'player_id': args['playerId']
        })

    def ServerChatEvent(self, args):
        if args['message'] == '测试设置':
            args['cancel'] = True
            self.NotifyToClient(args['playerId'], 'open_set_ui', {})
        elif args['message'] == '测试改设置':
            args['cancel'] = True
            self.NotifyToClient(args['playerId'], 'demo_write_setting', {})
