# -*- coding: utf-8 -*-

from common.mod import Mod
import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi
import modConfig


@Mod.Binding(name=modConfig.ModName, version="0.0.1")
class abcdemodset(object):

    def __init__(self):
        pass

    @Mod.InitServer()
    def MuSeZhenbanServerInit(self):
        print("===== init nacalgungun server =====")
        # 函数可以将System注册到服务端引擎中，实例的创建和销毁交给引擎处理。第一个参数是MOD名称，第二个是System名称，第三个是自定义MOD System类的路径
        # 取名名称尽量个性化，不能与其他人的MOD冲突，可以使用英文、拼音、下划线这三。
        sys = serverApi.GetSystem(modConfig.ModName, modConfig.ModName + "tem")

        if sys != None:
            print("注册信息： %s系统已经存在" % (modConfig.ModName + "tem"))

        else:
            print("注册信息： %s系统目前不存在，现在注册" % (modConfig.ModName + "tem"))
            serverApi.RegisterSystem(
                modConfig.ModName, modConfig.ModName + "tem",
                modConfig.ModName + "_py." + modConfig.ModName + "server." +
                modConfig.ModName + "se")

    @Mod.DestroyServer()
    def MuSeZhenbanServerDestroy(self):
        print("===== destroy nacalgungun server =====")

    # InitClient绑定的函数作为客户端脚本初始化的入口函数，通常用来注册客户端系统system和组件component
    @Mod.InitClient()
    def MuSeZhenbanClientInit(self):
        print("===== init nacalgungun client =====")
        # 函数可以将System注册到客户端引擎中，实例的创建和销毁交给引擎处理。第一个参数是MOD名称，第二个是System名称，第三个是自定义MOD System类的路径
        # 取名名称尽量个性化，不能与其他人的MOD冲突，可以使用英文、拼音、下划线三种。
        sys = clientApi.GetSystem(modConfig.ModName,
                                  modConfig.ModName + "temc")

        if sys != None:
            print("注册信息： %s系统已经存在" % (modConfig.ModName + "temc"))

        else:
            print("注册信息： %s系统目前不存在，现在注册" % (modConfig.ModName + "temc"))
            clientApi.RegisterSystem(
                modConfig.ModName, modConfig.ModName + "temc",
                modConfig.ModName + "_py." + modConfig.ModName + "client." +
                modConfig.ModName + "cl")

    # DestroyClient绑定的函数作为客户端脚本退出的时候执行的析构函数，通常用来反注册一些内容,可为空
    @Mod.DestroyClient()
    def MuSeZhenbanClientDestroy(self):
        print("===== destroy nacalgungun client =====")
