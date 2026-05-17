import re
from typing import Tuple, Optional

ALLOWED_CHARS = set('0123456789+-*/() ')


def validate_expression(expression: str, card_values: list[int]) -> Tuple[bool, Optional[str]]:
    for char in expression:
        if char not in ALLOWED_CHARS:
            return False, '算式包含非法字符，只能使用数字、加减乘除和括号'

    tokens = re.findall(r'\d+', expression)
    used_numbers = [int(t) for t in tokens]

    if len(used_numbers) != len(card_values):
        return False, f'必须使用全部{len(card_values)}个数字，每个数字只能使用一次'

    sorted_used = sorted(used_numbers)
    sorted_cards = sorted(card_values)
    if sorted_used != sorted_cards:
        return False, '使用的数字必须与卡牌数字完全一致，每个数字只能使用一次'

    try:
        result = eval(expression)
        if abs(result - 24) < 1e-9:
            return True, None
        else:
            return False, f'算式结果为 {result}，不等于24'
    except ZeroDivisionError:
        return False, '算式中存在除数为零的错误'
    except SyntaxError:
        return False, '算式语法错误，请检查括号和运算符'
    except Exception as e:
        return False, f'算式错误：{str(e)}'
