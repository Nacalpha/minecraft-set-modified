# 模组设置界面模板（改造版）

## 来源

原版「模组设置界面引擎」的作者是 **直爽的作图武士**，从 MCStudio 资源库下载，原版开源免费商用。感谢原作者。

这个仓库是改造版：在原版基础上加了脚本读写接口，修了几处会直接崩或者打不开界面的问题。原版的设置表字段说明（`ui_type` / `data_type` / `save_place` 等）见 [模组设置界面文档.docx](模组设置界面文档.docx)，原作者写的，一并放在仓库里；改造版新增的接口和存储位置见 [设置模块说明.md](设置模块说明.md)。

## 改造了什么

**能从脚本读写设置值。** 原版只能在界面上点，外部拿不到也改不了。现在有：

| 接口 | 作用 |
|---|---|
| `GetSetting(mod_id, set_id)` | 读一项 |
| `GetSettings(mod_id)` | 读整个模组（四个存储位合并） |
| `SetSetting(mod_id, set_id, value)` | 写一项，界面开着就立刻重画 |
| `ApplySettingsDict(mod_id, {...})` | 批量写，全部写完后只重画一次 |
| `ResetClassSettings(mod_id, class_id)` | 整类恢复默认值（界面上的重置按钮也用它） |
| `AddSettingChangeListener` | 可选，设置变更回调 |

写入会做校验：数字夹到 `min`/`max`、按 `step` 对齐、超出 `max_length` 截断、下拉框认 key 也认显示文字（颜色码 `§x` 会忽略）。

**能接官方设置界面的写法。** `setting_shim.py` 把官方 `SettingInst` 的方法（`AddSlider` / `AddDropDown` / `AddButton` / `GetSliderValue` / `SetSliderValue` / `GetDropDownValue` / `SetDropDownValue` / `CloseSettingUI`）实现了一遍，底下转到本模块。原来用官方设置界面的模组，改几行就能换过来，设置表和换算逻辑不用动。

## 修了什么问题

1. **滚动列表控件路径**。原版按平台拼 `/scroll_touch/...` 或 `/scroll_mouse/...`，手柄玩家的路径两者都对不上，界面打不开；中途按 F11 切换操作方式也会错位。改成用 `GetScrollViewContentPath()` 向引擎要路径，触控、键鼠、手柄都走引擎给的路径。取不到时回退到旧的拼法并打日志。
2. **滑条取整**。原版 `num // step` 丢了 `min` 偏移，浮点余数判断还会把 `0.9` 抬成 `1.0000000000000002`（越界）。改成按 `(读数 - 下限) / 步长` 取整并夹回范围。顺带修了 Python 2 里整数除整数会先截断再取整的问题（`min=0`、`step=5` 时写 9 会落到 5）。
3. **首次读配置崩**。`GetConfigData` 在没写过数据时返回 `None`，原版 `reload_set_data` 直接拿它当字典用，会崩。现在统一成空字典。
4. **权限未同步时崩**。界面早于服务端权限推送打开时，`world_state` 还没赋值，原版会 AttributeError。现在有默认值。
5. **写入和滑条轮询打架**。滑条每 0.1 秒读一次控件读数，外部写值后如果不同步缓存，轮询会把这当成玩家拖动再处理一遍（多一次保存和重画）。现在写值时同步缓存。

## 目录

```
behavior_pack_UEOWTgr6/
  set_nacalset2_py/          设置模块本体
    modConfig.py             模组名 / UI 名 / UI 定义名
    modMain.py               注册系统
    set_nacalset2client.py   界面逻辑 + 对外接口
    set_nacalset2server.py   读存档数据、下发权限等级
    setting_shim.py          官方 SettingInst 适配器
    ui1.py / templateUI.py   界面节点入口
  SetDemo_py/                演示模组
resource_pack_jkHZiSQe/
  ui/                        界面定义（四个 json）
  textures/ui/               界面贴图
```

搬到别的工程要带：行为包的 `set_nacalset2_py` 整个目录、资源包 `ui` 里四个 json、`textures/ui` 整个目录。

改名要同时改 `modConfig.py` 里三处（`ModName`、`TemplateUIName`、`TemplateUIScreenDef`），以及 UI json 的 `namespace`、内部 `@名字.xxx` 动画引用、`_ui_defs.json`。

## Demo 怎么用

`SetDemo_py` 是一个独立的小模组，只做两件事：喂一份示例设置表、演示怎么用脚本改值。进游戏后：

- 聊天栏发 `测试设置`：打开设置界面
- 聊天栏发 `测试改设置`：由脚本改一套值，界面开着能直接看到滑块、下拉、开关、输入框一起变
- 界面开着时 `SetDemo_py` 每 5 tick 轮询一次设置，改哪一项就打印一行；**改下拉框会套用一整套设置**（`demo_setdic.py` 里的 `preset_dic`），演示「预设组合」

不需要演示就把整个 `SetDemo_py` 目录删掉，模块本身不依赖它。

自己写模组时照 `setdemoclient.py` 抄：轮询看 `OnScriptTickClient`，写值看 `OnDemoWrite`。

## 其他要注意的

- 游戏内脚本是 **Python 2.7**，所有 `.py` 首行必须是 `# -*- coding: utf-8 -*-`，文件存 UTF-8 无 BOM。
- 不要绕过模块直接 `SetConfigData` / `SetExtraData`。模块每次保存写的是整份字典，你改一项，玩家下次在界面上动任何控件就会被整份覆盖回去，界面也不会跟着变。要写就调 `SetSetting`。
- 存储键是 `mod_` + 设置表里的 `mod_id` + `_set`，跟模块叫什么名字无关。模块改名不丢存档。
- 一切读写都要等设置表注册过之后（`reload_set_data` 或 `RegisterModSetting`）。
- 滚动列表用的是 `common.scrolling_panel` 模板，取路径靠它。换自己的 UI 时如果把这层模板换了，会退回旧拼法（手柄仍然不可用）。
- 脚本写入不检查 `need_op_level`（界面交互才检查）。要按权限限制，自己在调用前判断。
- 只支持改「选中值」，不支持运行时增删下拉框的选项。

## 关于仓库

Mod Studio 生成的 `studio.json`、`work.mcscfg`、`.mcs/` 里有账号、昵称、本机路径，已经写进 `.gitignore` 并从版本库移除，不要提交。
