# -*- coding: utf-8 -*-
# 官方 SettingInst 接口的适配器
#
# 原来走官方设置界面的模组用的是这一套调用：
#   settingInst = comp.RegisterSettingInst(...)
#   settingInst = settingInst.AddSlider(key, label, max, cb, priority, default)
#   settingInst = settingInst.AddDropDown(key, label, options, cb, priority, default)
#   settingInst.AddButton(key, label, text, cb)
#   settingInst.GetSliderValue(key) / SetSliderValue(key, value)
#   settingInst.GetDropDownValue(key) / SetDropDownValue(key, value)
#   comp.CloseSettingUI()
#
# 本类把这几个方法原样实现一遍，底下换成「设置界面引擎」（set_nacalset2）：
#   * Add* 只记录控件规格，最后转成设置表交给设置模块，界面由设置模块画；
#   * Get/Set 走设置模块的 GetSetting / SetSetting；
#   * 官方界面改值会回调，这边靠 Poll() 轮询发现变化再回调，所以每帧/每几帧
#     要调一次 Poll()；
#   * CloseSettingUI() 换成 CloseUI()。
#
# 值的形态和官方一致：滑块是 0..max 的整数读数，下拉是选项的 0 基下标。
# 这样模组里「读数 -> 真实参数」的换算代码（offset + 读数 * scale）完全不用改。

CLASS_ID = "main"


class SettingShim(object):

    def __init__(self, set_client_system, mod_id, mod_name, class_image,
                 client_system_name, slider_callback=None,
                 dropdown_callback=None):
        self.setsys = set_client_system
        self.mod_id = mod_id
        self.mod_name = mod_name
        self.class_image = class_image
        self.client_system_name = client_system_name
        self.slider_callback = slider_callback
        self.dropdown_callback = dropdown_callback
        self.items = []              # 按 Add* 顺序记录，顺序就是界面顺序
        self.item_map = {}
        self.button_callbacks = {}
        self.last_values = {}
        self.registered = False

    # ---------- 注册控件（链式，跟官方一样返回 self） ----------

    def AddSlider(self, key, label, max_value, callback, priority=None,
                  default=None):
        self._add_item({
            'kind': 'slider',
            'key': key,
            'label': label,
            'max': max_value,
            'default': default,
        })
        if callback is not None:
            self.slider_callback = callback
        return self

    def AddDropDown(self, key, label, options, callback, priority=None,
                    default=None):
        self._add_item({
            'kind': 'dropdown',
            'key': key,
            'label': label,
            'options': list(options),
            'default': default,
        })
        if callback is not None:
            self.dropdown_callback = callback
        return self

    def AddButton(self, key, label, text, callback):
        self._add_item({
            'kind': 'button',
            'key': key,
            'label': label,
            'text': text,
        })
        self.button_callbacks[key] = callback
        return self

    def _add_item(self, record):
        key = record['key']
        if key in self.item_map:
            return
        self.items.append(record)
        self.item_map[key] = record
        # 官方写法里按钮通常加在最后，而中间 SyncQuickPresetLabel() 之类
        # 可能已经触发过一次登记；这里把标记清掉，下次用到时重建设置表
        self.registered = False

    # ---------- 生成设置表 ----------

    def BuildSetDic(self):
        """把 Add* 记录下来的控件转成设置模块的 setdic"""
        set_list_order = []
        set_list = {}
        for record in self.items:
            key = record['key']
            set_list_order.append(key)
            if record['kind'] == 'slider':
                # 官方滑块是 0..max 的整数读数，这里照搬
                set_list[key] = {
                    'ui_type': 'Slider',
                    'data_type': 'range_number',
                    'save_place': 'client_local',
                    'need_op_level': -1,
                    'default_data': record['default'],
                    'step': 1,
                    'min': 0,
                    'max': record['max'],
                    'handle': 'become_int',
                    'text': record['label'],
                }
            elif record['kind'] == 'dropdown':
                # 存 0 基下标，控件名叫 str(下标)，避免中文选项名变成控件名
                options = record['options']
                order = list(range(len(options)))
                default = record['default']
                # 默认值可能是选项文字（登记表里写的），也可能是下标
                # （从模组自己的全局配置里读回来的），统一成下标
                if isinstance(default, int) and not isinstance(default, bool):
                    default_index = default
                elif default in options:
                    default_index = options.index(default)
                else:
                    default_index = 0
                if default_index < 0 or default_index >= len(options):
                    default_index = 0
                set_list[key] = {
                    'ui_type': 'ComboBoxUIControl',
                    'data_type': 'single_choice',
                    'save_place': 'client_local',
                    'need_op_level': -1,
                    'default_data': default_index,
                    'text': record['label'],
                    'data_order': order,
                    'data': dict([(i, options[i]) for i in order]),
                }
            else:
                # 按钮：交给原模组客户端系统的 SetUiButtonIsPressed 处理
                set_list[key] = {
                    'ui_type': 'Button',
                    'data_type': 'none',
                    'need_op_level': -1,
                    'button_type': 'send_event',
                    'system_name': self.client_system_name,
                    'text': record['text'],
                }
        return {
            'mod_id': self.mod_id,
            'mod_name': self.mod_name,
            'set_class_order': [CLASS_ID],
            'set_class': {
                CLASS_ID: {
                    'class_name': self.mod_name,
                    'class_text': self.mod_name,
                    'class_image': self.class_image,
                    'set_list_order': set_list_order,
                    'set_list': set_list,
                }
            },
        }

    # ---------- 读写（官方同名接口） ----------

    def GetSliderValue(self, key):
        if not self._EnsureRegistered():
            return None
        return self.setsys.GetSetting(self.mod_id, key)

    def GetDropDownValue(self, key):
        return self.GetSliderValue(key)

    def SetSliderValue(self, key, value):
        if not self._EnsureRegistered():
            return self
        if self.setsys.SetSetting(self.mod_id, key, value):
            # 自己写的值不算「界面改动」，同步进快照，Poll 不要回调
            self.last_values[key] = self.setsys.GetSetting(self.mod_id, key)
            # 下标可能被夹取过，读回来才是真值
        return self

    def SetDropDownValue(self, key, value):
        return self.SetSliderValue(key, value)

    # ---------- 轮询界面改动 ----------

    def Poll(self):
        """把设置界面上的改动转成回调。官方界面会主动回调，这边只能自己查。"""
        if not self._EnsureRegistered():
            return
        current = self.setsys.GetSettings(self.mod_id)
        if not self.last_values:
            self.last_values = current
            return
        changed = []
        for key in current:
            if key not in self.item_map:
                continue
            if key not in self.last_values:
                continue
            if self.last_values[key] != current[key]:
                changed.append(key)
        self.last_values = current
        for key in changed:
            record = self.item_map[key]
            value = current[key]
            if record['kind'] == 'slider':
                if self.slider_callback is not None:
                    self.slider_callback(key, value)
            elif record['kind'] == 'dropdown':
                if self.dropdown_callback is not None:
                    self.dropdown_callback(key, value)

    # ---------- 按钮 / 开关界面 ----------

    def OnButtonPressed(self, key):
        callback = self.button_callbacks.get(key)
        if callback is None:
            return False
        try:
            callback(key, None, None)
            return True
        except Exception as e:
            print("[设置] 按钮回调出错 %s: %s" % (key, e))
            return False

    def OpenUI(self):
        try:
            self.setsys.dk(None)
            return True
        except Exception as e:
            print("[设置] 打开设置界面失败: %s" % e)
            return False

    def CloseUI(self):
        try:
            self.setsys.gb_ui(None)
        except Exception as e:
            print("[设置] 关闭设置界面失败: %s" % e)
        return True

    def IsOpen(self):
        return self.setsys.uiNode1 is not None

    # ---------- 内部 ----------

    def _EnsureRegistered(self):
        """第一次用到时才把设置表交给设置模块（那时 Add* 已经全部调完）"""
        if self.registered:
            return True
        if not self.items:
            return False
        ok = self.setsys.RegisterModSetting(self.mod_id, self.BuildSetDic())
        if ok:
            self.registered = True
            self.last_values = self.setsys.GetSettings(self.mod_id)
        return ok
