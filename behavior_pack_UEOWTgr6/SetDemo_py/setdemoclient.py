# -*- coding: utf-8 -*-
# 演示模组的客户端系统：调用设置模块的接口，并轮询设置变化
import mod.client.extraClientApi as clientApi
import demo_config
import demo_setdic

ClientSystem = clientApi.GetClientSystemCls()


class SetDemoClient(ClientSystem):

    def __init__(self, namespace, systemName):
        super(SetDemoClient, self).__init__(namespace, systemName)
        self.tick = 0
        # 上一次轮询到的设置快照。None 表示还没开始采
        self.last_settings = None
        # 正在套用预设时置 True，防止把脚本自己写进去的值当成玩家改动
        self.applying_preset = False
        self.ListenForEvent(demo_config.ModName, demo_config.ModName + "Server",
                            "open_set_ui", self, self.OnOpenSetUI)
        self.ListenForEvent(demo_config.ModName, demo_config.ModName + "Server",
                            "demo_write_setting", self, self.OnDemoWrite)
        self.ListenForEvent(clientApi.GetEngineNamespace(),
                            clientApi.GetEngineSystemName(),
                            "OnScriptTickClient", self, self.OnScriptTickClient)

    def GetSetSystem(self):
        return clientApi.GetSystem(demo_config.SetModName,
                                   demo_config.SetClientSystem)

    def OnOpenSetUI(self, args):
        sys = self.GetSetSystem()
        if sys is not None:
            sys.dk(None)

    # ---------- 轮询设置变化 ----------
    # 设置模块不会主动通知外部“哪一项改了”（除非你注册回调），最省事的办法
    # 就是界面开着的时候定时读一遍，和自己存的快照比。

    def OnScriptTickClient(self, args=None):
        self.tick += 1
        if self.tick % 5 != 0:
            return
        sys = self.GetSetSystem()
        # 设置界面还没注册成功时不要调 GetUI：那会让引擎每 5 tick 刷一次
        # get_screen_def error（界面定义还没加载完），等注册好了再看
        if sys is None or not sys.IsUIRegistered():
            self.last_settings = None
            return
        # GetUI 拿得到节点说明设置界面正开着，拿不到就别轮询了
        uiNode = clientApi.GetUI(demo_config.SetModName,
                                 demo_config.SetTemplateUIName)
        if uiNode is None:
            # 顺手把快照清掉，下次打开界面重新采一次基准
            self.last_settings = None
            return
        current = sys.GetSettings(demo_config.DemoModId)
        if self.last_settings is None:
            self.last_settings = current
            print("[演示] 设置界面已打开，开始轮询：%r" % (current, ))
            return

        changed = []
        for set_id in current:
            if self.last_settings.get(set_id) != current[set_id]:
                changed.append(set_id)
        if changed:
            for set_id in changed:
                print("[演示] 设置变化 %s：%r -> %r" % (
                    set_id, self.last_settings.get(set_id), current[set_id]))
            # 下拉框被改动：套一整套设置，模拟“预设组合”
            if 'demo_combo' in changed and not self.applying_preset:
                self.ApplyPresetByCombo(current.get('demo_combo'))
        self.last_settings = current

    def ApplyPresetByCombo(self, combo_value):
        """按下拉框当前选项套用一整套设置"""
        preset = demo_setdic.preset_dic.get(combo_value)
        if not preset:
            return False
        sys = self.GetSetSystem()
        if sys is None:
            return False
        print("[演示] 下拉框改成 %r，套用预设：%r" % (combo_value, preset))
        self.applying_preset = True
        try:
            ok = sys.ApplySettingsDict(demo_config.DemoModId, preset,
                                       source='preset')
        finally:
            self.applying_preset = False
        return ok

    # ---------- 脚本主动改设置 ----------

    def OnDemoWrite(self, args):
        sys = self.GetSetSystem()
        if sys is None:
            print("[演示] 没找到设置模块的客户端系统")
            return

        # 改单项：整数滑条从 3 改成 8
        sys.SetSetting(demo_config.DemoModId, "demo_slider", 8)

        # 改一串，界面上会一起变（预设就是这种用法）
        # 注意这里不动 demo_combo，否则上面轮询里的“下拉框改动触发预设”会自己转起来
        sys.ApplySettingsDict(demo_config.DemoModId, {
            "demo_switch": False,
            "demo_float": 0.2,
            "demo_choice": "c",  # 也可以直接传 key
            "demo_text": "脚本改过"
        })

        print("[演示] 当前设置：%r" % (sys.GetSettings(demo_config.DemoModId), ))
