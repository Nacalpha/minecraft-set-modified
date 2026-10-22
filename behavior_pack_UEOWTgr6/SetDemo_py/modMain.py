# -*- coding: utf-8 -*-
# 演示模组：只负责给设置模块喂一份设置表，并演示怎么用脚本改设置值。
# 不需要演示的话整个 SetDemo_py 目录都可以删掉。

from common.mod import Mod
import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi
import demo_config


@Mod.Binding(name=demo_config.ModName, version="0.0.1")
class SetDemoMod(object):

    @Mod.InitServer()
    def SetDemoServerInit(self):
        if serverApi.GetSystem(demo_config.ModName,
                               demo_config.ModName + "Server") is None:
            serverApi.RegisterSystem(
                demo_config.ModName, demo_config.ModName + "Server",
                "SetDemo_py.setdemoserver.SetDemoServer")

    @Mod.InitClient()
    def SetDemoClientInit(self):
        if clientApi.GetSystem(demo_config.ModName,
                               demo_config.ModName + "Client") is None:
            clientApi.RegisterSystem(
                demo_config.ModName, demo_config.ModName + "Client",
                "SetDemo_py.setdemoclient.SetDemoClient")
