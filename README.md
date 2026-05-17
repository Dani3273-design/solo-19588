# 24点游戏

使用 Python + Pygame 开发的24点纸牌游戏。

## 游戏规则

1. 系统随机发放4张扑克牌
2. 玩家需要使用这4张牌的数字，通过加、减、乘、除和括号组成算式
3. 每个数字只能使用一次，最终结果必须等于24
4. A = 1, J = 11, Q = 12, K = 13

## 目录结构

```
main/
├── game/
│   ├── __init__.py    # 包初始化
│   ├── card.py        # 扑克牌相关代码（Card类、发牌逻辑）
│   ├── check.py       # 算式校验逻辑
│   ├── count.py       # 计时器（多线程）
│   └── ui.py          # Pygame 界面与游戏流程
├── main.py            # 游戏入口
├── requirements.txt   # 依赖包
└── README.md          # 项目说明
```

## 模块说明

### [card.py](game/card.py)
- `Card` 类：表示单张扑克牌，包含花色和数字
- `generate_deck()`：生成一副52张的扑克牌
- `draw_unique_cards(count=4)`：随机抽取不重复的扑克牌

### [check.py](game/check.py)
- `validate_expression(expression, card_values)`：校验算式
  - 检查非法字符
  - 检查数字是否与卡牌一致且只使用一次
  - 计算结果是否等于24

### [count.py](game/count.py)
- `Timer` 类：多线程计时器
  - 独立线程运行，不阻塞UI
  - 支持开始、暂停、继续、停止
  - 格式化时间显示

### [ui.py](game/ui.py)
- `GameUI` 类：游戏主界面
  - 菜单页面：游戏标题、说明、开始按钮
  - 游戏页面：4张扑克牌、输入框、提交按钮、计时器
  - 结算页面：卡牌展示、算式、用时、返回按钮
- `Button` 类：通用按钮组件
- `InputBox` 类：输入框组件
- `draw_card()`：绘制扑克牌

### [main.py](main.py)
- 游戏入口，创建并运行 `GameUI`

## 运行方式

```bash
cd main
pip install -r requirements.txt
python main.py
```

## 操作说明

- 输入框：直接键盘输入算式
- 提交答案：点击"提交答案"按钮或按回车键
- 退出游戏：按 ESC 键或关闭窗口
