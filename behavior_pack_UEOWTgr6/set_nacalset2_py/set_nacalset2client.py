# -*- coding: utf-8 -*-
import modConfig
import random
import copy
import mod.client.extraClientApi as clientApi
import setting_shim

ClientSystem = clientApi.GetClientSystemCls()

# 区分“字典里没有这个键”和“值是 None”这两种情况
_MISSING = object()

# § 的 utf-8 字节。颜色码处理都在这上面做，避免 str/unicode 混用
_COLOR_MARKER = u'\u00a7'.encode('utf-8')

try:
    _STRING_TYPES = (unicode, str)
except NameError:  # 兼容 Python 3，方便离线跑语法检查
    _STRING_TYPES = (str, )


def _ToComparableText(value):
    """str 统一转成 utf-8 字节串，方便和 unicode 比较。
    不是字符串返回 None
    """
    if isinstance(value, unicode):
        return value.encode('utf-8')
    if isinstance(value, str):
        return value
    return None


def _StripColorCode(text):
    """去掉 §x 这类颜色/样式码，text 是 _ToComparableText 出来的 utf-8 字节串。

    设置表里的显示文字经常写成 "§l关闭开火按钮"，玩家看到的是去掉码之后的样子，
    所以按显示文字匹配时要再比一次去码版本。
    """
    if not text or not isinstance(text, (str, bytes)):
        return text
    if isinstance(text, bytes):
        marker = _COLOR_MARKER  # Python 2 的 str 就是字节串
    else:
        marker = u'\u00a7'
    if marker not in text:
        return text
    out = []
    i = 0
    length = len(text)
    while i < length:
        if text[i:i + 2] == marker:
            i += 3  # § 自身两字节，再跳过后面那个格式符
            continue
        out.append(text[i:i + 1])
        i += 1
    return text[0:0].join(out)


def _SameKey(a, b):
    """比较两个可能当字典 key 的值。允许 str 与 unicode 互相比，
    bool 只跟 bool 比（避免 True 和 1 混掉）
    """
    if a is b:
        return True
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    ta = _ToComparableText(a)
    tb = _ToComparableText(b)
    if ta is not None and tb is not None:
        return ta == tb
    return type(a) is type(b) and a == b


class set_nacalset2cl(ClientSystem):

    def __init__(self, namespace, systemName):
        super(set_nacalset2cl, self).__init__(namespace, systemName)
        self.ListenEvent()
        self.levelid = clientApi.GetLevelId()
        self.pid = clientApi.GetLocalPlayerId()
        self.mod = {}
        self.hdt_timer = None
        self.hdt_bg = None
        self.set = {}
        self.start = False
        self.srk_data = {}
        self.hdt_data = {}
        self.uiNode1 = None
        # 当前打开的分类，没打开时为 None。外部改设置时靠它判断要不要重画
        self.mod_id = None
        self.class_id = None
        # 玩家权限等级由服务端每 0.5 秒推一次，没收到之前先按 0 处理
        self.world_state = {'op': 0}
        # 设置项变更回调表：{mod_id: [callback, ...]}，见 AddSettingChangeListener
        self.setting_listeners = {}
        if clientApi.GetPlatform() == 0:
            self.sta = 'stack_'
            self.stb = 'mouse'
        else:
            self.sta = ''
            self.stb = 'touch'
        # 兜底用的路径，正常情况会被 RefreshScrollPath() 向引擎查到的结果覆盖
        self.stc = '/scroll_' + self.stb + '/scroll_view/' + self.sta + 'panel/background_and_viewport/scrolling_view_port/scrolling_content'

    #函数回调
    def ListenEvent(self):
        print("ListenEvent")
        self.ListenForEvent(clientApi.GetEngineNamespace(),
                            clientApi.GetEngineSystemName(),
                            "GetEntityByCoordReleaseClientEvent", self,
                            self.GetEntityByCoordReleaseClientEvent)
        #self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), "LoadClientAddonScriptsAfter", self, self.LoadClientAddonScriptsAfter)
        self.ListenForEvent(clientApi.GetEngineNamespace(),
                            clientApi.GetEngineSystemName(),
                            "OnKeyPressInGame", self, self.OnKeyPressInGame)
        self.ListenForEvent(clientApi.GetEngineNamespace(),
                            clientApi.GetEngineSystemName(), "UiInitFinished",
                            self, self.UiInitFinished)
        self.ListenForEvent(modConfig.ModName, modConfig.ModName + "tem",
                            "reload_set_data", self, self.reload_set_data)
        self.ListenForEvent(modConfig.ModName, modConfig.ModName + "tem", "dk",
                            self, self.dk)
        self.ListenForEvent(modConfig.ModName, modConfig.ModName + "tem",
                            "get_server_state", self, self.get_server_state)

    def get_server_state(self, args):
        self.world_state = args

    def UiInitFinished(self, args):
        clientApi.RegisterUI(modConfig.ModName, modConfig.TemplateUIName,
                             modConfig.TemplateUIPyClsPath,
                             modConfig.TemplateUIScreenDef)
        if self.start == False:
            self.start = True
            comp = clientApi.GetEngineCompFactory().CreateGame(self.levelid)
            comp.AddRepeatedTimer(0.1, self.get_hdt_data)

    def dk(self, args):
        if clientApi.GetPlatform() == 0 and clientApi.IsTouchWithMouse(
        ) == False:
            self.sta = 'stack_'
            self.stb = 'mouse'
        else:
            self.sta = ''
            self.stb = 'touch'
        # 兜底用的路径，正常情况会被 RefreshScrollPath() 向引擎查到的结果覆盖
        self.stc = '/scroll_' + self.stb + '/scroll_view/' + self.sta + 'panel/background_and_viewport/scrolling_view_port/scrolling_content'

        comp = clientApi.GetEngineCompFactory().CreateGame(self.levelid)
        # comp.SimulateTouchWithMouse(True)
        self.uiNode1 = clientApi.PushScreen(modConfig.ModName,
                                            modConfig.TemplateUIName)
        self.uiNode1 = clientApi.GetUI(modConfig.ModName,
                                       modConfig.TemplateUIName)

    def ddk(self):
        self.RefreshScrollPath()
        if clientApi.GetPlatform() == 0:
            self.uiNode1.GetBaseUIControl("/panel").SetFullSize(
                "x", {
                    "followType": "parent",
                    "relativeValue": 1
                })
            self.uiNode1.GetBaseUIControl("/panel").SetFullSize(
                "y", {
                    "followType": "parent",
                    "relativeValue": 1
                })
        self.hdt_bg = None
        for i in self.mod:
            dic = self.mod[i]
            self.uiNode1.Clone(
                '/panel/image(0)/image(1)/mz_wz',
                '/panel/image(0)/image(1)/scroll_view' + self.stc, i)
            self.uiNode1.GetBaseUIControl(
                "/panel/image(0)/image(1)/scroll_view" + self.stc + '/' + i +
                '/label').asLabel().SetText(dic['mod_name'])
            for ii in dic['set_class_order']:
                self.uiNode1.Clone(
                    '/panel/image(0)/image(1)/mz_an',
                    '/panel/image(0)/image(1)/scroll_view' + self.stc,
                    i + ':' + ii)
                buttonControl = self.uiNode1.GetBaseUIControl(
                    '/panel/image(0)/image(1)/scroll_view' + self.stc + '/' +
                    i + ':' + ii).asButton()
                buttonControl.AddTouchEventParams({
                    "isSwallow": True,
                    'mod_id': i,
                    'class_id': ii
                })
                buttonControl.SetButtonTouchUpCallback(self.class_button)
                self.uiNode1.GetBaseUIControl(
                    "/panel/image(0)/image(1)/scroll_view" + self.stc + '/' +
                    i + ':' + ii + '/image/button_label').asLabel().SetText(
                        dic['set_class'][ii]['class_name'])
                self.uiNode1.GetBaseUIControl(
                    "/panel/image(0)/image(1)/scroll_view" + self.stc + '/' +
                    i + ':' + ii + '/image').asImage().SetSprite(
                        dic['set_class'][ii]['class_image'])
        buttonControl = self.uiNode1.GetBaseUIControl(
            '/panel/image(0)/button').asButton()
        buttonControl.AddTouchEventParams({"isSwallow": True})
        buttonControl.SetButtonTouchUpCallback(self.gb_ui)

    def set_ui(self):
        self.RefreshScrollPath()
        for ii in self.mod[self.mod_id]['set_class'][
                self.class_id]['set_list']:
            dic = self.mod[self.mod_id]['set_class'][
                self.class_id]['set_list'][ii]
            if dic['ui_type'] == 'ComboBoxUIControl' and dic[
                    'data_type'] == 'single_choice':
                if self.world_state['op'] >= dic['need_op_level']:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/button').SetTouchEnable(True)
                else:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/button').SetTouchEnable(False)
                text = dic['data'][self.set[self.mod_id][dic['save_place']]
                                   [ii]]
                self.uiNode1.GetBaseUIControl(
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                    '/' + ii + '/button/button_label').asLabel().SetText(text)
                for iii in self.mod[self.mod_id]['set_class'][
                        self.class_id]['set_list'][ii]['data']:
                    if iii == self.set[self.mod_id][dic['save_place']][ii]:
                        self.uiNode1.GetBaseUIControl(
                            '/panel/image(0)/image(1)(0)/scroll_view' +
                            self.stc + '/' + ii +
                            '/button/image(0)/scroll_view' + self.stc + '/' +
                            str(iii) + '/default').asImage().SetSprite(
                                'textures/ui/xlk_an4')
                        self.uiNode1.GetBaseUIControl(
                            '/panel/image(0)/image(1)(0)/scroll_view' +
                            self.stc + '/' + ii +
                            '/button/image(0)/scroll_view' + self.stc + '/' +
                            str(iii) + '/hover').asImage().SetSprite(
                                'textures/ui/xlk_an3')
                        self.uiNode1.GetBaseUIControl(
                            '/panel/image(0)/image(1)(0)/scroll_view' +
                            self.stc + '/' + ii +
                            '/button/image(0)/scroll_view' + self.stc + '/' +
                            str(iii) + '/pressed').asImage().SetSprite(
                                'textures/ui/xlk_an3')
                    else:
                        self.uiNode1.GetBaseUIControl(
                            '/panel/image(0)/image(1)(0)/scroll_view' +
                            self.stc + '/' + ii +
                            '/button/image(0)/scroll_view' + self.stc + '/' +
                            str(iii) + '/default').asImage().SetSprite(
                                'textures/ui/xlk_an2')
                        self.uiNode1.GetBaseUIControl(
                            '/panel/image(0)/image(1)(0)/scroll_view' +
                            self.stc + '/' + ii +
                            '/button/image(0)/scroll_view' + self.stc + '/' +
                            str(iii) + '/hover').asImage().SetSprite(
                                'textures/ui/xlk_an1')
                        self.uiNode1.GetBaseUIControl(
                            '/panel/image(0)/image(1)(0)/scroll_view' +
                            self.stc + '/' + ii +
                            '/button/image(0)/scroll_view' + self.stc + '/' +
                            str(iii) + '/pressed').asImage().SetSprite(
                                'textures/ui/xlk_an1')
            elif dic['ui_type'] == 'Button':
                if self.world_state['op'] >= dic['need_op_level']:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/button').SetTouchEnable(True)
                else:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/button').SetTouchEnable(False)
            elif dic['ui_type'] == 'SwitchToggle':
                if self.world_state['op'] >= dic['need_op_level']:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/button').SetTouchEnable(True)
                else:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/button').SetTouchEnable(False)
                if self.set[self.mod_id][dic['save_place']][ii] == True:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/button/default').asImage().SetSprite(
                            'textures/ui/toggle_on')
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/button/hover').asImage().SetSprite(
                            'textures/ui/toggle_on_hover')
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/button/pressed').asImage().SetSprite(
                            'textures/ui/toggle_on_hover')
                else:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/button/default').asImage().SetSprite(
                            'textures/ui/toggle_off')
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/button/hover').asImage().SetSprite(
                            'textures/ui/toggle_off_hover')
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/button/pressed').asImage().SetSprite(
                            'textures/ui/toggle_off_hover')
            elif dic['ui_type'] == 'TextEditBox':
                if self.world_state['op'] >= dic['need_op_level']:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/edit_box').SetTouchEnable(True)
                else:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/edit_box').SetTouchEnable(False)
                self.uiNode1.GetBaseUIControl(
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                    '/' + ii + '/edit_box').asTextEditBox().SetEditText(
                        str(self.set[self.mod_id][dic['save_place']][ii]))
            elif dic['ui_type'] == 'Slider':
                if self.world_state['op'] >= dic['need_op_level']:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/slider').SetTouchEnable(True)
                else:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/slider').SetTouchEnable(False)
                if dic['data_type'] == 'single_choice':
                    if self.world_state['op'] >= dic['need_op_level']:
                        self.uiNode1.GetBaseUIControl(
                            '/panel/image(0)/image(1)(0)/scroll_view' +
                            self.stc + '/' + ii + '/label').asLabel().SetText(
                                dic['text'] + '：' + dic['data'][self.set[
                                    self.mod_id][dic['save_place']][ii]])
                    else:
                        self.uiNode1.GetBaseUIControl(
                            '/panel/image(0)/image(1)(0)/scroll_view' +
                            self.stc + '/' + ii + '/label').asLabel().SetText(
                                dic['text'] + '：' + dic['data'][self.set[
                                    self.mod_id][dic['save_place']][ii]] +
                                '（权限不足）')
                    num = dic['data_order'].index(
                        self.set[self.mod_id][dic['save_place']][ii])
                    l = len(dic['data_order']) - 1
                    num = num / (l * 1.0)
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/slider').asSlider().SetSliderValue(num)
                elif dic['data_type'] == 'range_number':
                    num = self.set[self.mod_id][dic['save_place']][ii]
                    derta = dic['max'] - dic['min']
                    num2 = num - dic['min']
                    num3 = num2 / (derta * 1.0)
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + ii + '/slider').asSlider().SetSliderValue(num3)
                    text = str(num)
                    if 'data' in dic:
                        if num in dic['data']:
                            text = dic['data'][num]
                    if self.world_state['op'] >= dic['need_op_level']:
                        self.uiNode1.GetBaseUIControl(
                            '/panel/image(0)/image(1)(0)/scroll_view' +
                            self.stc + '/' + ii +
                            '/label').asLabel().SetText(dic['text'] + '：' +
                                                        text)
                    else:
                        self.uiNode1.GetBaseUIControl(
                            '/panel/image(0)/image(1)(0)/scroll_view' +
                            self.stc + '/' + ii +
                            '/label').asLabel().SetText(dic['text'] + '：' +
                                                        text + '（权限不足）')
                bl_num = self.uiNode1.GetBaseUIControl(
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                    '/' + ii + '/slider').asSlider().GetSliderValue()
                self.hdt_data[ii]['bl_num'] = bl_num
            elif dic['ui_type'] == 'Label':
                self.uiNode1.GetBaseUIControl(
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                    '/' + ii + '/label').asLabel().SetText(dic['text'])
        for i in self.mod:
            for ii in self.mod[i]['set_class']:
                if self.class_id == ii:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)/scroll_view' + self.stc +
                        '/' + i + ':' + ii + '/default').asImage().SetSprite(
                            'textures/ui/beacon_button_pressed')
                else:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)/scroll_view' + self.stc +
                        '/' + i + ':' + ii + '/default').asImage().SetSprite(
                            'textures/netease/download/btn01@3x')

    def open_set_class(self, mod_id, class_id):
        self.class_button(
            {'AddTouchEventParams': {
                'mod_id': mod_id,
                'class_id': class_id
            }})

    def class_button(self, args):
        self.RefreshScrollPath()
        bu = args['AddTouchEventParams']
        self.mod_id = bu['mod_id']
        self.class_id = bu['class_id']
        self.srk_data = {}
        self.hdt_data = {}
        set_list = self.mod[bu['mod_id']]['set_class'][
            bu['class_id']]['set_list']
        self.uiNode1.GetBaseUIControl("/panel/image(0)/label").asLabel(
        ).SetText(
            self.mod[bu['mod_id']]['set_class'][bu['class_id']]['class_text'])
        a = self.uiNode1.GetChildrenName(
            "/panel/image(0)/image(1)(0)/scroll_view" + self.stc)
        for i in a:
            self.uiNode1.RemoveComponent(
                "/panel/image(0)/image(1)(0)/scroll_view" + self.stc + '/' + i,
                "/panel/image(0)/image(1)(0)/scroll_view" + self.stc)
        for i in self.mod[bu['mod_id']]['set_class'][
                bu['class_id']]['set_list_order']:
            dic = set_list[i]
            if dic['ui_type'] == 'ComboBoxUIControl' and dic[
                    'data_type'] == 'single_choice':
                self.uiNode1.Clone(
                    '/panel/image(0)/image(1)(0)/xlk',
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc, i)
                if self.world_state['op'] >= dic['need_op_level']:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i + '/label').asLabel().SetText(dic['text'])
                else:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i + '/label').asLabel().SetText(dic['text'] +
                                                              '（权限不足）')
                buttonControl = self.uiNode1.GetBaseUIControl(
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                    '/' + i + '/button').asButton()
                buttonControl.AddTouchEventParams({
                    "isSwallow": True,
                    'mod_id': bu['mod_id'],
                    'class_id': bu['class_id'],
                    'set_id': i,
                    'op': dic['need_op_level']
                })
                buttonControl.SetButtonTouchUpCallback(self.xlk)
                for ii in dic['data_order']:
                    self.uiNode1.Clone(
                        '/panel/image(0)/image(1)(0)/xlk_xx',
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i + '/button/image(0)/scroll_view' + self.stc,
                        str(ii))
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i + '/button/image(0)/scroll_view' + self.stc +
                        '/' + str(ii) + '/button_label').asLabel().SetText(
                            dic['data'][ii])
                    buttonControl = self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i + '/button/image(0)/scroll_view' + self.stc +
                        '/' + str(ii)).asButton()
                    buttonControl.AddTouchEventParams({
                        "isSwallow":
                        True,
                        'mod_id':
                        bu['mod_id'],
                        'class_id':
                        bu['class_id'],
                        'set_id':
                        i,
                        'xx_id':
                        ii,
                        'save_place':
                        dic['save_place'],
                        'op':
                        dic['need_op_level']
                    })
                    buttonControl.SetButtonTouchUpCallback(self.xlk_xx)
                num = len(dic['data_order']) * 20
                if num > 112:
                    num = 112
                self.uiNode1.GetBaseUIControl(
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                    '/' + i + '/button/image(0)').SetFullSize(
                        "y", {"absoluteValue": num})
            elif dic['ui_type'] == 'Button':
                self.uiNode1.Clone(
                    '/panel/image(0)/image(1)(0)/an',
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc, i)
                if self.world_state['op'] >= dic['need_op_level']:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i + '/button/button_label').asLabel().SetText(
                            dic['text'])
                else:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i +
                        '/button/button_label').asLabel().SetText(dic['text'] +
                                                                  '（权限不足）')
                buttonControl = self.uiNode1.GetBaseUIControl(
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                    '/' + i + '/button').asButton()
                if dic['button_type'] == 'send_event':
                    buttonControl.AddTouchEventParams({
                        "isSwallow":
                        True,
                        'mod_id':
                        bu['mod_id'],
                        'class_id':
                        bu['class_id'],
                        'set_id':
                        i,
                        'op':
                        dic['need_op_level'],
                        'button_type':
                        dic['button_type'],
                        'system':
                        dic['system_name']
                    })
                else:
                    buttonControl.AddTouchEventParams({
                        "isSwallow":
                        True,
                        'mod_id':
                        bu['mod_id'],
                        'class_id':
                        bu['class_id'],
                        'set_id':
                        i,
                        'op':
                        dic['need_op_level'],
                        'button_type':
                        dic['button_type']
                    })
                buttonControl.SetButtonTouchUpCallback(self.dj_button)
            elif dic['ui_type'] == 'SwitchToggle' and dic[
                    'data_type'] == 'bool':
                self.uiNode1.Clone(
                    '/panel/image(0)/image(1)(0)/kg',
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc, i)
                if self.world_state['op'] >= dic['need_op_level']:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i + '/label').asLabel().SetText(dic['text'])
                else:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i + '/label').asLabel().SetText(dic['text'] +
                                                              '（权限不足）')
                buttonControl = self.uiNode1.GetBaseUIControl(
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                    '/' + i + '/button').asButton()
                buttonControl.AddTouchEventParams({
                    "isSwallow":
                    True,
                    'mod_id':
                    bu['mod_id'],
                    'class_id':
                    bu['class_id'],
                    'set_id':
                    i,
                    'save_place':
                    dic['save_place'],
                    'op':
                    dic['need_op_level']
                })
                buttonControl.SetButtonTouchUpCallback(self.dj_kg)
            elif dic['ui_type'] == 'TextEditBox':
                self.uiNode1.Clone(
                    '/panel/image(0)/image(1)(0)/srk',
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc, i)
                if self.world_state['op'] >= dic['need_op_level']:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i + '/label').asLabel().SetText(dic['text'])
                else:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i + '/label').asLabel().SetText(dic['text'] +
                                                              '（权限不足）')
                self.uiNode1.GetBaseUIControl(
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                    '/' + i +
                    '/edit_box').asTextEditBox().SetEditTextMaxLength(
                        dic['max_length'])
                self.srk_data[i] = {
                    'data': self.set[bu['mod_id']][dic['save_place']][i],
                    'data_type': dic['data_type'],
                    'save_place': dic['save_place'],
                    'min': dic['min'],
                    'max': dic['max'],
                    'default_data': dic['default_data']
                }
                buttonControl = self.uiNode1.GetBaseUIControl(
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                    '/' + i + '/button').asButton()
                buttonControl.AddTouchEventParams({
                    "isSwallow":
                    False,
                    'mod_id':
                    bu['mod_id'],
                    'class_id':
                    bu['class_id'],
                    'set_id':
                    i,
                    'save_place':
                    dic['save_place'],
                    'op':
                    dic['need_op_level'],
                    'handle':
                    dic['handle']
                })
                buttonControl.SetButtonTouchUpCallback(self.dj_srk)
            elif dic['ui_type'] == 'Slider':
                self.uiNode1.Clone(
                    '/panel/image(0)/image(1)(0)/hdt',
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc, i)
                if self.world_state['op'] >= dic['need_op_level']:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i + '/label').asLabel().SetText(dic['text'])
                else:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i + '/label').asLabel().SetText(dic['text'] +
                                                              '（权限不足）')
                if dic['data_type'] == 'range_number':
                    self.hdt_data[i] = {
                        'data': self.set[bu['mod_id']][dic['save_place']][i],
                        'data_type': dic['data_type'],
                        'save_place': dic['save_place'],
                        'min': dic['min'],
                        'max': dic['max'],
                        'default_data': dic['default_data'],
                        'handle': dic['handle'],
                        'step': dic['step'],
                        'op': dic['need_op_level']
                    }
                elif dic['data_type'] == 'single_choice':
                    self.hdt_data[i] = {
                        'data': self.set[bu['mod_id']][dic['save_place']][i],
                        'data_type': dic['data_type'],
                        'save_place': dic['save_place'],
                        'data': dic['data'],
                        'data_order': dic['data_order'],
                        'default_data': dic['default_data'],
                        'op': dic['need_op_level']
                    }
            elif dic['ui_type'] == 'Label':
                self.uiNode1.Clone(
                    '/panel/image(0)/image(1)(0)/wz',
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc, i)
                self.uiNode1.GetBaseUIControl(
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                    '/' + i + '/label').asLabel().SetText(dic['text'])
            elif dic['ui_type'] == 'Image':
                self.uiNode1.Clone(
                    '/panel/image(0)/image(1)(0)/tp',
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc, i)
                self.uiNode1.GetBaseUIControl(
                    '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                    '/' + i + '/image').asImage().SetSprite(dic['text'])
        self.set_ui()

    def SetUiLabelText(self, modname, class_id, set_id, text):
        self.mod[modname]['set_class'][class_id]['set_list'][set_id][
            'text'] = text
        self.set_ui()

    def get_hdt_data(self):
        self.RefreshScrollPath()
        for i in self.hdt_data:
            num = self.uiNode1.GetBaseUIControl(
                '/panel/image(0)/image(1)(0)/scroll_view' + self.stc + '/' +
                i + '/slider').asSlider().GetSliderValue()
            bl_num = copy.deepcopy(num)
            data = 0
            if self.hdt_data[i]['data_type'] == 'range_number':
                low = self.hdt_data[i]['min']
                high = self.hdt_data[i]['max']
                # 显式转浮点：GetSliderValue 万一是整数，下面的除法在
                # Python 2 里会变成整除
                num = float(low) + float(high - low) * num
                step = self.hdt_data[i]['step']
                if step > 0:
                    # 按 (读数 - 下限) / 步长 取整，不能直接用读数除步长：
                    # 下限不是步长整数倍时会整体偏一格，浮点余数判断还会把
                    # 0.9 抬成 1.0000000000000002 这种越界值
                    num = low + round((num - low) / step) * step
                num = round(num, 6)
                if num < low:
                    num = low
                elif num > high:
                    num = high
                if self.hdt_data[i]['handle'] == 'become_int':
                    num = int(round(num))
                elif self.hdt_data[i]['handle'] == 'become_float':
                    num = float(num)
                data = num
            elif self.hdt_data[i]['data_type'] == 'single_choice':
                derta = len(self.hdt_data[i]['data_order']) - 1
                derta = derta * num
                num2 = int(derta / 1)
                if derta % 1 >= 0.5:
                    num2 += 1
                num = int(num2)
                if num < 0:
                    num = 0
                elif num > len(self.hdt_data[i]['data_order']) - 1:
                    num = len(self.hdt_data[i]['data_order']) - 1
                data = self.hdt_data[i]['data_order'][num]
            if self.hdt_data[i]['data'] != data and self.world_state[
                    'op'] >= self.hdt_data[i]['op']:
                self.hdt_data[i]['data'] = copy.deepcopy(data)
                self.set[self.mod_id][self.hdt_data[i]
                                      ['save_place']][i] = copy.deepcopy(data)
                self.save_data(self.hdt_data[i]['save_place'], self.mod_id)
                self.set_ui()
                self._notify_setting_changed(self.mod_id, self.class_id, i,
                                             self.hdt_data[i]['save_place'],
                                             data, 'ui')
            if self.hdt_data[i]['bl_num'] != bl_num and self.world_state[
                    'op'] >= self.hdt_data[i]['op']:
                self.hdt_data[i]['bl_num'] = bl_num
                self.hdt_bg = i

    def dj_srk(self, args):
        self.RefreshScrollPath()
        bu = args['AddTouchEventParams']
        if self.world_state['op'] >= bu['op']:
            self.uiNode1.GetBaseUIControl("/panel/button(0)").SetPosition(
                (0, 0))
            self.uiNode1.SetSelectControl(
                '/panel/image(0)/image(1)(0)/scroll_view' + self.stc + '/' +
                bu['set_id'] + '/edit_box', True)
            buttonControl = self.uiNode1.GetBaseUIControl(
                '/panel/button(0)').asButton()
            buttonControl.AddTouchEventParams(bu)
            buttonControl.SetButtonTouchUpCallback(self.get_srk_data)

    def get_srk_data(self, args):
        self.RefreshScrollPath()
        bu = args['AddTouchEventParams']
        self.uiNode1.GetBaseUIControl("/panel/button(0)").SetPosition(
            (0, 10000))
        self.uiNode1.SetSelectControl(
            '/panel/image(0)/image(1)(0)/scroll_view' + self.stc + '/' +
            bu['set_id'] + '/edit_box', False)
        if self.world_state['op'] >= bu['op']:
            i = bu['set_id']
            data = self.uiNode1.GetBaseUIControl(
                '/panel/image(0)/image(1)(0)/scroll_view' + self.stc + '/' +
                i + '/edit_box').asTextEditBox().GetEditText()
            if self.srk_data[i]['data_type'] == 'range_number':
                flag = 1
                data2 = ''
                num = 0
                for ii in data:
                    if ii in [
                            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                            '.'
                    ] or (num == 0 and ii == '-'):
                        data2 += ii
                    else:
                        flag = 0
                    num += 1
                if data2 == '':
                    #data2=str(self.srk_data[i]['default_data'])
                    flag = 0
                data = copy.deepcopy(data2)
                if flag == 0:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i + '/edit_box').asTextEditBox().SetEditText(
                            str(self.set[self.mod_id][self.srk_data[i]
                                                      ['save_place']][i]))
                    data = str(self.set[self.mod_id][self.srk_data[i]
                                                     ['save_place']][i])
                flag = 1
                if '.' in data:
                    data = float(data)
                    if data > self.srk_data[i]['max']:
                        flag = 0
                        data = self.srk_data[i]['max']
                    elif data < self.srk_data[i]['min']:
                        flag = 0
                        data = self.srk_data[i]['min']
                    data = float(data)
                else:
                    data = int(data)
                    if data > self.srk_data[i]['max']:
                        flag = 0
                        data = self.srk_data[i]['max']
                    elif data < self.srk_data[i]['min']:
                        flag = 0
                        data = self.srk_data[i]['min']
                    data = int(data)
                if bu['handle'] == 'become_int':
                    data = int(data)
                elif bu['handle'] == 'become_float':
                    data = float(data)
                if flag == 0:
                    self.uiNode1.GetBaseUIControl(
                        '/panel/image(0)/image(1)(0)/scroll_view' + self.stc +
                        '/' + i + '/edit_box').asTextEditBox().SetEditText(
                            str(data))
            elif self.srk_data[i]['data_type'] == 'character_string':
                pass
            self.srk_data[i]['data'] = copy.deepcopy(data)
            self.set[self.mod_id][self.srk_data[i]
                                  ['save_place']][i] = copy.deepcopy(data)
            self.save_data(self.srk_data[i]['save_place'], self.mod_id)
            self.set_ui()
            self._notify_setting_changed(self.mod_id, self.class_id, i,
                                         self.srk_data[i]['save_place'], data,
                                         'ui')

    def dj_kg(self, args):
        bu = args['AddTouchEventParams']
        if self.world_state['op'] >= bu['op']:
            if self.set[bu['mod_id']][bu['save_place']][bu['set_id']] == True:
                self.set[bu['mod_id']][bu['save_place']][bu['set_id']] = False
            else:
                self.set[bu['mod_id']][bu['save_place']][bu['set_id']] = True
            self.save_data(bu['save_place'], bu['mod_id'])
            self.set_ui()
            self._notify_setting_changed(
                bu['mod_id'], bu['class_id'], bu['set_id'], bu['save_place'],
                self.set[bu['mod_id']][bu['save_place']][bu['set_id']], 'ui')

    def dj_button(self, args):
        bu = args['AddTouchEventParams']
        if self.world_state['op'] >= bu['op']:
            if bu['button_type'] == 'send_event':
                sys = clientApi.GetSystem(bu['mod_id'], bu['system'])
                sys.SetUiButtonIsPressed({
                    'set_id': bu['set_id'],
                    'player_id': self.pid
                })
            elif bu['button_type'] == 'reset_class_data':
                self.ResetClassSettings(bu['mod_id'], bu['class_id'])

    def xlk_xx(self, args):
        bu = args['AddTouchEventParams']
        if self.world_state['op'] >= bu['op']:
            self.set[bu['mod_id']][bu['save_place']][
                bu['set_id']] = bu['xx_id']
            self.save_data(bu['save_place'], bu['mod_id'])
            self.set_ui()
            self._notify_setting_changed(bu['mod_id'], bu['class_id'],
                                         bu['set_id'], bu['save_place'],
                                         bu['xx_id'], 'ui')
        self.qx_xlk(args)

    def xlk(self, args):
        self.RefreshScrollPath()
        bu = args['AddTouchEventParams']
        if self.world_state['op'] >= bu['op']:
            #self.uiNode1.GetBaseUIControl("/panel/image(0)/image(1)(0)/scroll_view").SetTouchEnable(False)
            self.uiNode1.GetBaseUIControl("/panel/button(0)").SetPosition(
                (0, 0))
            buttonControl = self.uiNode1.GetBaseUIControl(
                '/panel/button(0)').asButton()
            buttonControl.AddTouchEventParams(bu)
            buttonControl.SetButtonTouchUpCallback(self.qx_xlk)
            self.uiNode1.GetBaseUIControl(
                '/panel/image(0)/image(1)(0)/scroll_view' + self.stc + '/' +
                bu['set_id'] + '/button/image(0)').SetPosition((0, 0))

    def qx_xlk(self, args):
        self.RefreshScrollPath()
        bu = args['AddTouchEventParams']
        #self.uiNode1.GetBaseUIControl("/panel/image(0)/image(1)(0)/scroll_view").SetTouchEnable(True)
        self.uiNode1.GetBaseUIControl("/panel/button(0)").SetPosition(
            (0, 10000))
        self.uiNode1.GetBaseUIControl(
            '/panel/image(0)/image(1)(0)/scroll_view' + self.stc + '/' +
            bu['set_id'] + '/button/image(0)').SetPosition((0, 1000))

    def reload_set_data(self, args):
        comp = clientApi.GetEngineCompFactory().CreateConfigClient(
            self.levelid)
        self.set[args['data']['mod_id']] = {
            'client_local':
            comp.GetConfigData("mod_" + args['data']['mod_id'] + "_set", True),
            'client_player':
            comp.GetConfigData("mod_" + args['data']['mod_id'] + "_set",
                               False),
            'server_player':
            args['p_data'],
            'server_world':
            args['l_data']
        }
        self.mod[args['data']['mod_id']] = args['data']

        # GetConfigData / GetExtraData 在没写过数据时可能返回 None，统一成空字典，
        # 否则后面所有 set[mod_id][save_place][set_id] 的写法都会炸
        for place in self.set[args['data']['mod_id']]:
            if self.set[args['data']['mod_id']][place] is None:
                self.set[args['data']['mod_id']][place] = {}

        for i in args['data']['set_class']:
            for ii in args['data']['set_class'][i]['set_list']:
                dic = args['data']['set_class'][i]['set_list'][ii]
                if 'save_place' in dic:
                    if ii not in self.set[args['data']['mod_id']][
                            dic['save_place']]:
                        self.set[args['data']['mod_id']][
                            dic['save_place']][ii] = copy.deepcopy(
                                dic['default_data'])

        self.save_data('client_local', args['data']['mod_id'])
        self.save_data('client_player', args['data']['mod_id'])
        self.save_data('server_player', args['data']['mod_id'])
        self.save_data('server_world', args['data']['mod_id'])

    def save_data(self, local, mod_id):
        if local == 'client_local':
            comp = clientApi.GetEngineCompFactory().CreateConfigClient(
                self.levelid)
            comp.SetConfigData("mod_" + mod_id + "_set",
                               self.set[mod_id][local], True)
        elif local == 'client_player':
            comp = clientApi.GetEngineCompFactory().CreateConfigClient(
                self.levelid)
            comp.SetConfigData("mod_" + mod_id + "_set",
                               self.set[mod_id][local], False)
        elif local == 'server_player':
            self.NotifyToServer('save_data',
                                [mod_id, self.set[mod_id][local], self.pid])
        elif local == 'server_world':
            self.NotifyToServer(
                'save_data', [mod_id, self.set[mod_id][local], self.levelid])

    def gb_ui(self, args):
        if self.uiNode1 != None:
            self.hdt_bg = None
            self.srk_data = {}
            self.hdt_data = {}
            clientApi.PopScreen()
            comp = clientApi.GetEngineCompFactory().CreateCustomAudio(
                self.levelid)
            comp.PlayCustomMusic("close_ui", (1, 1, 1), 1, 1, False, self.pid)
            com = clientApi.GetEngineCompFactory().CreateGame(self.levelid)
            # com.AddTimer(0.5, self.gb3)
        self.uiNode1 = None

    # def gb3(self):
    # comp = clientApi.GetEngineCompFactory().CreateGame(self.levelid)
    # comp.SimulateTouchWithMouse(False)

    def OnKeyPressInGame(self, args):
        if args['isDown'] == '1' and args['key'] == '27':
            self.gb_ui(None)

    def jc_hdt_bg(self):
        if self.hdt_bg != None:
            self.hdt_bg = None
            self.set_ui()

    def GetEntityByCoordReleaseClientEvent(self, args):
        com = clientApi.GetEngineCompFactory().CreateGame(self.levelid)
        com.CancelTimer(self.hdt_timer)
        self.hdt_timer = com.AddTimer(0.1, self.jc_hdt_bg)

    def GetClientPlayerData(self, mod_id):
        comp = clientApi.GetEngineCompFactory().CreateConfigClient(
            self.levelid)
        data = comp.GetConfigData("mod_" + mod_id + "_set", False)
        return data

    def GetClientLocalData(self, mod_id):
        comp = clientApi.GetEngineCompFactory().CreateConfigClient(
            self.levelid)
        data = comp.GetConfigData("mod_" + mod_id + "_set", True)
        return data

    # 滚动列表（分类列表 / 设置列表 / 下拉框列表）的内容路径后缀。
    #
    # scroll_view 的内部结构在触控模式和键鼠模式（F11 可切）下不一样：触控是
    # /scroll_touch/scroll_view/panel/...，键鼠是 /scroll_mouse/scroll_view/stack_panel/...，
    # 手柄玩家两者都对不上。所以这段不能自己拼，必须问引擎要。
    # 引擎给的路径形如 "<控件路径>/scroll_xxx/scroll_view/..."，把控件路径那截去掉，
    # 剩下的后缀三种滚动列表通用，可以继续往后拼子控件。
    # 接口调不通时沿用 self.stc 里启动时按平台拼的旧值，不至于整页打不开。
    def RefreshScrollPath(self):
        if self.uiNode1 is None:
            return False
        base = '/panel/image(0)/image(1)(0)/scroll_view'
        try:
            control = self.uiNode1.GetBaseUIControl(base)
            if control is None:
                return False
            content = control.asScrollView().GetScrollViewContentPath()
            print("[设置] 取滚动列表路径成功：%s" % content)
        except Exception as e:
            print("[设置] 取滚动列表路径失败：%s" % e)
            return False
        if not content:
            return False
        if content.startswith(base):
            self.stc = content[len(base):]
            return True
        # 有些版本直接返回相对路径，形如 /scroll_touch/scroll_view/...
        if content.startswith('/scroll_'):
            self.stc = content
            return True
        print("[设置] 滚动列表路径格式不认识，继续用旧路径：%s" % content)
        return False

    # ==================== 对外读写接口 ====================
    # 供模组内其它脚本读写设置值。取实例：
    #   setsys = clientApi.GetSystem("set_nacalset2", "set_nacalset2temc")

    def GetSettingInfo(self, mod_id, set_id):
        """按选项 ID 找出它所属的分类和选项信息字典，返回 (class_id, item)"""
        mod = self.mod.get(mod_id)
        if not mod:
            return None, None
        for class_id in mod['set_class']:
            set_list = mod['set_class'][class_id]['set_list']
            if set_id in set_list:
                return class_id, set_list[set_id]
        return None, None

    def GetSetting(self, mod_id, set_id):
        """读一个设置项的当前值；读不到返回 None"""
        class_id, item = self.GetSettingInfo(mod_id, set_id)
        if item is None:
            return None
        save_place = item.get('save_place')
        if not save_place:
            return None
        return copy.deepcopy(
            self.set.get(mod_id, {}).get(save_place, {}).get(set_id))

    def GetSettings(self, mod_id, save_place=None):
        """读一个模组的全部设置值，返回 {选项ID: 值} 的副本。
        不传 save_place 就把四个存储位合并成一份
        """
        if mod_id not in self.set:
            return {}
        if save_place:
            return copy.deepcopy(self.set[mod_id].get(save_place) or {})
        out = {}
        for place in self.set[mod_id]:
            data = self.set[mod_id][place]
            if data:
                out.update(copy.deepcopy(data))
        return out

    def RegisterModSetting(self, mod_id, setdic):
        """客户端直接登记一份设置表，不需要服务端转发。

        给「原来是官方设置界面、现在改成本模块」的模组用：那些模组的设置项
        全是客户端本地的（client_local / client_player），没有必要绕服务端。
        server_player / server_world 两个存储位在这条路上不会生效。

        :param mod_id: 设置表里的 mod_id，同时也是模组注册名（按钮事件要用它取系统）
        :param setdic: 设置表，格式和 reload_set_data 收到的一样
        :return: bool
        """
        if not mod_id or not setdic or 'set_class' not in setdic:
            print("[设置] 设置表不完整，登记被忽略：%s" % mod_id)
            return False
        comp = clientApi.GetEngineCompFactory().CreateConfigClient(
            self.levelid)
        self.mod[mod_id] = setdic
        self.set[mod_id] = {
            'client_local': comp.GetConfigData("mod_" + mod_id + "_set", True)
            or {},
            'client_player':
            comp.GetConfigData("mod_" + mod_id + "_set", False) or {},
            'server_player': {},
            'server_world': {},
        }
        # 缺的键补默认值，缺的存储位补空字典
        for class_id in setdic['set_class']:
            for set_id in setdic['set_class'][class_id]['set_list']:
                item = setdic['set_class'][class_id]['set_list'][set_id]
                place = item.get('save_place')
                if not place:
                    continue
                bucket = self.set[mod_id].get(place)
                if bucket is None:
                    bucket = {}
                    self.set[mod_id][place] = bucket
                if set_id not in bucket:
                    bucket[set_id] = copy.deepcopy(item.get('default_data'))
        self.save_data('client_local', mod_id)
        self.save_data('client_player', mod_id)
        return True

    def CreateSettingShim(self,
                          mod_id,
                          mod_name,
                          class_image,
                          client_system_name,
                          slider_callback=None,
                          dropdown_callback=None):
        """建一个模拟官方 SettingInst 的适配器，见 setting_shim.py"""
        return setting_shim.SettingShim(self, mod_id, mod_name, class_image,
                                        client_system_name, slider_callback,
                                        dropdown_callback)

    def NormalizeNumber(self, item, value):
        """范围数字：夹进 [min, max]，按 step 对齐，再按 handle 转型。
        不合法返回 None
        """
        if isinstance(value, bool):
            return None
        try:
            num = float(value)
        except (TypeError, ValueError):
            return None
        if num != num:  # NaN
            return None
        low = item.get('min', 0)
        high = item.get('max', 0)
        if num < low:
            num = low
        elif num > high:
            num = high
        step = item.get('step') or 0
        if step > 0:
            # 必须显式转浮点：Python 2 里整数除整数是整除，会先截断再取整，
            # 比如 min=0、step=5 时 9 会被算成 5
            num = low + round(float(num - low) / step) * step
        # 收掉浮点误差，别把 0.30000000000000004 这种值存进去
        num = round(num, 6)
        if num > high:
            num = high
        if num < low:
            num = low
        handle = item.get('handle')
        if handle == 'become_int':
            return int(round(num))
        if handle == 'become_float':
            return float(num)
        return num

    def NormalizeChoiceKey(self, item, value):
        """把可选项换算成 data_order 里的 key。
        支持三种写法：key 本身、显示文字（data[key] 的值）、整数下标
        """
        order = item.get('data_order')
        if not order:
            return None
        data = item.get('data') or {}
        for key in order:
            if _SameKey(key, value):
                return key
        text = _ToComparableText(value)
        if text is not None:
            # 显示文字完全一致
            for key in order:
                if _ToComparableText(data.get(key)) == text:
                    return key
            # 忽略 § 颜色码再比一次：表里常写成 "§l关闭开火按钮"，
            # 而调用方拿到的是可见文字
            plain = _StripColorCode(text)
            if plain:
                for key in order:
                    if _StripColorCode(_ToComparableText(
                            data.get(key))) == plain:
                        return key
        if isinstance(value, int) and not isinstance(value, bool):
            if 0 <= value < len(order):
                return order[value]
        return None

    def NormalizeSettingValue(self, item, value):
        """把外部传进来的值换算成内部存储值；不合法返回 None"""
        ui_type = item.get('ui_type')
        data_type = item.get('data_type')
        if ui_type == 'SwitchToggle' and data_type == 'bool':
            if isinstance(value, bool):
                return value
            text = _ToComparableText(value)
            if text is not None:
                low = text.lower()
                if low in ('1', 'true', 'on'):
                    return True
                if low in ('0', 'false', 'off'):
                    return False
                return None
            if isinstance(value, (int, float)):
                return bool(value)
            return None
        if ui_type == 'TextEditBox':
            if data_type == 'character_string':
                text = value
                if not isinstance(text, _STRING_TYPES):
                    text = str(value)
                max_length = item.get('max_length')
                if max_length and len(text) > max_length:
                    text = text[:max_length]
                return text
            return self.NormalizeNumber(item, value)
        if ui_type == 'Slider':
            if data_type == 'single_choice':
                return self.NormalizeChoiceKey(item, value)
            return self.NormalizeNumber(item, value)
        if ui_type == 'ComboBoxUIControl':
            return self.NormalizeChoiceKey(item, value)
        # Button / Label 没有可写的数据
        return None

    def _apply_value(self,
                     mod_id,
                     class_id,
                     set_id,
                     item,
                     value,
                     source,
                     save=True,
                     refresh=True):
        """底层写入，value 必须已经是合法的存储值"""
        save_place = item.get('save_place')
        if not save_place:
            return False
        bucket = self.set[mod_id].get(save_place)
        if bucket is None:
            bucket = {}
            self.set[mod_id][save_place] = bucket
        old_value = bucket.get(set_id, _MISSING)
        bucket[set_id] = copy.deepcopy(value)
        # 同步滑条 / 输入框的读数缓存。不同步的话，0.1 秒一次的滑条轮询会把
        # 还没重画的旧读数当成“玩家拖动了滑条”，再写一遍
        if set_id in self.hdt_data:
            self.hdt_data[set_id]['data'] = copy.deepcopy(value)
        if set_id in self.srk_data:
            self.srk_data[set_id]['data'] = copy.deepcopy(value)
        if save:
            self.save_data(save_place, mod_id)
        if refresh:
            self.RefreshSettingUI(mod_id, class_id)
        if old_value is _MISSING or old_value != value:
            self._notify_setting_changed(mod_id, class_id, set_id, save_place,
                                         value, source)
        return True

    def SetSetting(self, mod_id, set_id, value, source='api', refresh=True):
        """写一个设置项的值。界面正开在这一页时立刻重画。
        :return: bool 是否写入成功（找不到选项、值不合法都返回 False）
        """
        if mod_id not in self.set or mod_id not in self.mod:
            print("[设置] 模组 %s 的设置还没注册，写入被忽略" % mod_id)
            return False
        class_id, item = self.GetSettingInfo(mod_id, set_id)
        if item is None:
            print("[设置] 找不到设置项 %s（模组 %s）" % (set_id, mod_id))
            return False
        if not item.get('save_place'):
            print("[设置] 设置项 %s 不存数据，不能写" % set_id)
            return False
        new_value = self.NormalizeSettingValue(item, value)
        if new_value is None:
            print("[设置] 设置项 %s 的值不合法：%s" % (set_id, str(value)))
            return False
        return self._apply_value(mod_id,
                                 class_id,
                                 set_id,
                                 item,
                                 new_value,
                                 source,
                                 save=True,
                                 refresh=refresh)

    def ApplySettingsDict(self, mod_id, settings, source='preset'):
        """批量写。全部写完后统一重画一次，避免每写一项就整页重画。
        :param settings: {选项ID: 值}
        :return: bool 是否至少写入了一项
        """
        if not settings:
            print("[设置] 传入的设置字典是空的")
            return False
        applied = []
        for set_id in settings:
            if self.SetSetting(mod_id,
                               set_id,
                               settings[set_id],
                               source=source,
                               refresh=False):
                applied.append(set_id)
        if not applied:
            return False
        self.RefreshSettingUI(mod_id)
        print("[设置] 模组 %s 批量写入 %d 项：%s" % (mod_id, len(applied), str(applied)))
        return True

    def ResetClassSettings(self, mod_id, class_id):
        """把一个分类下的选项全部恢复成 default_data。
        权限不足的跳过，跟界面上的重置按钮行为一致
        """
        mod = self.mod.get(mod_id)
        if not mod or class_id not in mod.get('set_class', {}):
            return False
        set_list = mod['set_class'][class_id]['set_list']
        op = self.world_state.get('op', 0)
        places = []
        for set_id in set_list:
            item = set_list[set_id]
            if item.get('ui_type') in ('Button', 'Label'):
                continue
            if 'default_data' not in item:
                continue
            if op < item.get('need_op_level', 0):
                continue
            # 默认值直接写，不经过 NormalizeSettingValue：那里会按 handle 改
            # 数值类型，重置应该跟原来一模一样
            if self._apply_value(mod_id,
                                 class_id,
                                 set_id,
                                 item,
                                 item['default_data'],
                                 'reset',
                                 save=False,
                                 refresh=False):
                place = item.get('save_place')
                if place not in places:
                    places.append(place)
        for place in places:
            self.save_data(place, mod_id)
        self.RefreshSettingUI(mod_id, class_id)
        return len(places) > 0

    def RefreshSettingUI(self, mod_id=None, class_id=None):
        """重画当前页。界面没开、或者当前看的不是这个模组 / 分类时什么都不做，
        下次打开会自动渲染成新值
        """
        if self.uiNode1 is None:
            return False
        if mod_id is not None and mod_id != self.mod_id:
            return False
        if class_id is not None and class_id != self.class_id:
            return False
        try:
            self.set_ui()
        except Exception as e:
            print("[设置] 刷新界面失败：%s" % e)
            return False
        return True

    # ---------- 设置变更回调（可选） ----------

    def AddSettingChangeListener(self, mod_id, callback):
        """注册设置变更回调。回调收到一个字典：
        {mod_id, class_id, set_id, save_place, value, source}
        source 为 'ui'（玩家在界面上改的）、'api'、'preset'、'reset'
        """
        if not callable(callback):
            print("[设置] 回调不是函数，已忽略")
            return False
        listeners = self.setting_listeners.setdefault(mod_id, [])
        if callback not in listeners:
            listeners.append(callback)
        return True

    def RemoveSettingChangeListener(self, mod_id, callback):
        listeners = self.setting_listeners.get(mod_id)
        if listeners and callback in listeners:
            listeners.remove(callback)
            return True
        return False

    def _notify_setting_changed(self, mod_id, class_id, set_id, save_place,
                                value, source):
        """把变更告诉注册过的回调。回调里抛异常不影响设置本身"""
        listeners = self.setting_listeners.get(mod_id)
        if not listeners:
            return
        payload = {
            'mod_id': mod_id,
            'class_id': class_id,
            'set_id': set_id,
            'save_place': save_place,
            'value': copy.deepcopy(value),
            'source': source
        }
        for callback in list(listeners):
            try:
                callback(payload)
            except Exception as e:
                print("[设置] 设置变更回调出错：%s" % e)
