from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any
import random


@dataclass(frozen=True)
class Strategy:
    opening: str
    rhythm: str
    camera: str
    dialogue_density: str


STRATEGIES: List[Strategy] = [
    Strategy(opening="对话开场", rhythm="短句偏多，断得利索", camera="近景为主（手、物件、细小动作）", dialogue_density="对白偏多"),
    Strategy(opening="动作开场", rhythm="中短句混合", camera="中景为主（两人关系、走位）", dialogue_density="对白适中"),
    Strategy(opening="环境声开场", rhythm="中长句偏多，允许一两段碎碎念", camera="远景切入（城市、天气、路灯）", dialogue_density="对白偏少但要扎心"),
    Strategy(opening="物件开场", rhythm="短句 + 偶尔一条长句压节奏", camera="近景中景渐推", dialogue_density="对白适中"),
]

BANNED_FILLERS = [
    "与此同时", "不禁", "显然", "仿佛", "注定", "无疑", "这一刻", "渐渐地",
]

EDITOR_DONTS = [
    "别在段尾总结人生道理；让事件自己说话。",
    "少用垫词和模板转折；能用动作/对话顶过去就别解释。",
    "避免每段都很工整（同长度、同节奏、同句式）。",
]

OBJECTS = [
    "皱巴巴的烟盒", "钥匙串", "旧手机壳", "皮手套", "一次性打火机",
    "塑料袋里的热豆包", "小票", "车钥匙", "发黄的名片", "折断的牙签",
]

SOUNDS = [
    "远处的狗叫", "暖气片咔哒声", "走廊脚步声", "玻璃门的风铃响",
    "收银机按键声", "车门关上的闷响", "电梯的嗡鸣",
]

SENSES = [
    "冷风钻进领口", "烟味黏在衣服上", "手指被冻得发麻", "屋里一股潮气",
    "热气扑脸又立刻散掉",
]

GESTURES = [
    "把烟在烟盒边上磕了磕", "手指在桌面敲两下", "抬眼又迅速移开",
    "把袖口往上拽", "下意识摸口袋", "咽了口唾沫", "笑了一声不太像笑",
    "把椅子往后蹭出一声刺耳响",
]

PLACE_DETAILS = [
    "洗浴门口厚门帘", "路口彩票站的灯箱", "老小区楼道的广告贴纸",
    "服务区白得发蓝的灯", "夜市油烟和塑料凳", "公交站牌掉漆的边",
]

DIALOGUE_SEEDS = [
    "你别跟我说这些虚的。",
    "行，那你现在想咋整？",
    "我给你面子，不代表我怕你。",
    "说清楚点，别绕。",
    "你信不信随你，但我话放这儿。",
    "别装了，你心里有数。",
    "我不欠你，但我也不怕你。",
    "你今天来，是为了谈，还是为了闹？",
]


def choose_strategy(seed: int) -> Strategy:
    r = random.Random(seed)
    return r.choice(STRATEGIES)


def sample_materials(seed: int) -> Dict[str, Any]:
    r = random.Random(seed + 101)
    return {
        "objects": r.sample(OBJECTS, k=min(3, len(OBJECTS))),
        "sounds": r.sample(SOUNDS, k=min(2, len(SOUNDS))),
        "senses": r.sample(SENSES, k=1),
        "gestures": r.sample(GESTURES, k=min(2, len(GESTURES))),
        "place_details": r.sample(PLACE_DETAILS, k=min(2, len(PLACE_DETAILS))),
        "dialogue_seeds": r.sample(DIALOGUE_SEEDS, k=min(6, len(DIALOGUE_SEEDS))),
    }
