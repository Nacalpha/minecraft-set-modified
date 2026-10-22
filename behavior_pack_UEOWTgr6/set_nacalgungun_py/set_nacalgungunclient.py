# -*- coding: utf-8 -*-
import modConfig
import random
import copy
import mod.client.extraClientApi as clientApi

ClientSystem = clientApi.GetClientSystemCls()


class set_nacalgunguncl(ClientSystem):

    def __init__(self, namespace, systemName):
        super(set_nacalgunguncl, self).__init__(namespace, systemName)
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
        if clientApi.GetPlatform() == 0:
            self.sta = 'stack_'
            self.stb = 'mouse'
        else:
            self.sta = ''
            self.stb = 'touch'
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
        self.stc = '/scroll_' + self.stb + '/scroll_view/' + self.sta + 'panel/background_and_viewport/scrolling_view_port/scrolling_content'

        comp = clientApi.GetEngineCompFactory().CreateGame(self.levelid)
        # comp.SimulateTouchWithMouse(True)
        self.uiNode1 = clientApi.PushScreen(modConfig.ModName,
                                            modConfig.TemplateUIName)
        self.uiNode1 = clientApi.GetUI(modConfig.ModName,
                                       modConfig.TemplateUIName)

    def ddk(self):
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
        for i in self.hdt_data:
            num = self.uiNode1.GetBaseUIControl(
                '/panel/image(0)/image(1)(0)/scroll_view' + self.stc + '/' +
                i + '/slider').asSlider().GetSliderValue()
            bl_num = copy.deepcopy(num)
            data = 0
            if self.hdt_data[i]['data_type'] == 'range_number':
                derta = self.hdt_data[i]['max'] - self.hdt_data[i]['min']
                derta *= num
                num = self.hdt_data[i]['min'] + derta
                if self.hdt_data[i]['step'] > 0:
                    num2 = num // self.hdt_data[i]['step']
                    if num % self.hdt_data[i]['step'] >= self.hdt_data[i][
                            'step'] / 2.0:
                        num2 += 1
                    num = num2 * self.hdt_data[i]['step']
                if self.hdt_data[i]['handle'] == 'become_int':
                    num = int(num)
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
                data = self.hdt_data[i]['data_order'][num]
            if self.hdt_data[i]['data'] != data and self.world_state[
                    'op'] >= self.hdt_data[i]['op']:
                self.hdt_data[i]['data'] = copy.deepcopy(data)
                self.set[self.mod_id][self.hdt_data[i]
                                      ['save_place']][i] = copy.deepcopy(data)
                self.save_data(self.hdt_data[i]['save_place'], self.mod_id)
                self.set_ui()
            if self.hdt_data[i]['bl_num'] != bl_num and self.world_state[
                    'op'] >= self.hdt_data[i]['op']:
                self.hdt_data[i]['bl_num'] = bl_num
                self.hdt_bg = i

    def dj_srk(self, args):
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

    def dj_kg(self, args):
        bu = args['AddTouchEventParams']
        if self.world_state['op'] >= bu['op']:
            if self.set[bu['mod_id']][bu['save_place']][bu['set_id']] == True:
                self.set[bu['mod_id']][bu['save_place']][bu['set_id']] = False
            else:
                self.set[bu['mod_id']][bu['save_place']][bu['set_id']] = True
            self.save_data(bu['save_place'], bu['mod_id'])
            self.set_ui()

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
                for i in self.mod[bu['mod_id']]['set_class'][
                        bu['class_id']]['set_list']:
                    if self.mod[bu['mod_id']]['set_class'][bu['class_id']][
                            'set_list'][i]['ui_type'] != 'Button' and self.mod[
                                bu['mod_id']]['set_class'][bu['class_id']][
                                    'set_list'][i]['ui_type'] != 'Label':
                        if self.world_state['op'] >= self.mod[bu['mod_id']][
                                'set_class'][bu['class_id']]['set_list'][i][
                                    'need_op_level'] and 'default_data' in self.mod[
                                        bu['mod_id']]['set_class'][
                                            bu['class_id']]['set_list'][i]:
                            self.set[bu['mod_id']][
                                self.mod[bu['mod_id']]['set_class'][
                                    bu['class_id']]['set_list'][i]
                                ['save_place']][i] = copy.deepcopy(
                                    self.mod[bu['mod_id']]['set_class'][
                                        bu['class_id']]['set_list'][i]
                                    ['default_data'])
                self.save_data('client_local', bu['mod_id'])
                self.save_data('client_player', bu['mod_id'])
                self.save_data('server_player', bu['mod_id'])
                self.save_data('server_world', bu['mod_id'])
                self.set_ui()

    def xlk_xx(self, args):
        bu = args['AddTouchEventParams']
        if self.world_state['op'] >= bu['op']:
            self.set[bu['mod_id']][bu['save_place']][
                bu['set_id']] = bu['xx_id']
            self.save_data(bu['save_place'], bu['mod_id'])
            self.set_ui()
        self.qx_xlk(args)

    def xlk(self, args):
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
