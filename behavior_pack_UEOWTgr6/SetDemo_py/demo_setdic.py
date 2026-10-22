# -*- coding: utf-8 -*-
# 演示用的设置表，覆盖了所有控件类型。
# 自己写模组时照着改：每个选项的 ui_type / data_type 必须搭配正确，否则界面会画错。

setdic = {
    "mod_id": "setdemo",
    "mod_name": "设置模块演示",
    "set_class_order": ["demo_basic", "demo_about"],
    "set_class": {
        "demo_basic": {
            "class_name": "演示设置",
            "class_text": "演示设置",
            "class_image": "textures/ui/set_lb",
            "set_list_order": [
                "demo_label",
                "demo_combo",
                "demo_switch",
                "demo_slider",
                "demo_float",
                "demo_choice",
                "demo_text",
                "demo_reset",
            ],
            "set_list": {
                "demo_label": {
                    "ui_type": "Label",
                    "data_type": "none",
                    "text":
                    "聊天栏发送 §a测试设置§f 打开本界面\n发送 §a测试改设置§f 由脚本改写下面的值\n改上面的下拉框会套用一整套设置（演示预设组合）"
                },
                "demo_combo": {
                    "ui_type": "ComboBoxUIControl",
                    "data_type": "single_choice",
                    "save_place": "client_local",
                    "need_op_level": -1,
                    "default_data": 0,
                    "text": "下拉框",
                    "data_order": [0, 1, 2],
                    "data": {
                        0: "选项零",
                        1: "选项一",
                        2: "选项二"
                    }
                },
                "demo_switch": {
                    "ui_type": "SwitchToggle",
                    "data_type": "bool",
                    "save_place": "client_local",
                    "need_op_level": -1,
                    "default_data": True,
                    "text": "开关"
                },
                "demo_slider": {
                    "ui_type": "Slider",
                    "data_type": "range_number",
                    "save_place": "client_local",
                    "need_op_level": -1,
                    "default_data": 3,
                    "step": 1,
                    "min": 0,
                    "max": 10,
                    "handle": "become_int",
                    "text": "整数滑条（0-10）",
                    "data": {
                        0: "最小",
                        10: "最大"
                    }
                },
                "demo_float": {
                    "ui_type": "Slider",
                    "data_type": "range_number",
                    "save_place": "client_local",
                    "need_op_level": -1,
                    "default_data": 0.5,
                    "step": 0.1,
                    "min": 0.0,
                    "max": 1.0,
                    "handle": "become_float",
                    "text": "小数滑条（0-1）"
                },
                "demo_choice": {
                    "ui_type": "Slider",
                    "data_type": "single_choice",
                    "save_place": "client_local",
                    "need_op_level": -1,
                    "default_data": "a",
                    "text": "滑条单选",
                    "data_order": ["a", "b", "c"],
                    "data": {
                        "a": "甲",
                        "b": "乙",
                        "c": "丙"
                    }
                },
                "demo_text": {
                    "ui_type": "TextEditBox",
                    "data_type": "character_string",
                    "save_place": "client_local",
                    "need_op_level": -1,
                    "default_data": "默认文字",
                    "handle": "none",
                    "text": "输入框",
                    "min": 0,
                    "max": 20,
                    "max_length": 10
                },
                "demo_reset": {
                    "ui_type": "Button",
                    "data_type": "none",
                    "need_op_level": -1,
                    "button_type": "reset_class_data",
                    "text": "重置本页设置"
                }
            }
        },
        "demo_about": {
            "class_name": "关于",
            "class_text": "关于",
            "class_image": "textures/ui/set_hg",
            "set_list_order": ["demo_about_label"],
            "set_list": {
                "demo_about_label": {
                    "ui_type": "Label",
                    "data_type": "none",
                    "text": "设置模块演示\n\n设置值存在哪里、怎么读写，见项目根目录的设置模块说明.md"
                }
            }
        }
    }
}

# 下拉框每个选项对应一整套设置，用来演示“预设组合”。
# 键是 demo_combo 的 data_order 里的值（也就是存下来的原始值）。
# 这套预设故意不包含 demo_combo 自己，否则套用时会再次触发下拉框改动，转不停。
preset_dic = {
    0: {
        "demo_slider": 3,
        "demo_float": 0.5,
        "demo_switch": True,
        "demo_choice": "a",
        "demo_text": "默认文字"
    },
    1: {
        "demo_slider": 8,
        "demo_float": 0.9,
        "demo_switch": False,
        "demo_choice": "b",
        "demo_text": "方案一"
    },
    2: {
        "demo_slider": 1,
        "demo_float": 0.1,
        "demo_switch": True,
        "demo_choice": "c",
        "demo_text": "方案二"
    }
}