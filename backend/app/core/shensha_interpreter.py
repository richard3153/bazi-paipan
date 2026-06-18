"""
神煞深度解读引擎
基于《三命通会》《渊海子平》等经典，对30+核心神煞进行深度解读

每个解读结果包含：
1. 经典引用：出自哪本书、哪章、核心原句
2. 逻辑推导：为何得出此结论
3. 具体影响：对应现实的哪些方面
4. 程度量化：吉凶程度1-5星
5. 实用建议：如何趋吉避凶
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class ShenShaDetail:
    """单个神煞的详细解读"""
    name: str
    category: str  # 吉神/凶煞/中性
    position: str  # 出现在哪一柱（年/月/日/时）
    branch: str    # 具体地支
    classic_source: str  # 经典依据
    original_text: str   # 经典原文
    logical_derivation: str  # 逻辑推导
    effects: Dict[str, str]  # 对各方面的具体影响
    severity: int  # 吉凶程度1-5星
    resolve: Optional[str]  # 化解建议
    combined_analysis: str   # 综合判断


class ShenShaInterpreter:
    """神煞深度解读引擎"""

    # 天干地支
    HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # 五行映射
    WUXING_MAP = {
        "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
        "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
        "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
        "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
        "戌": "土", "亥": "水"
    }

    # 地支藏干
    BRANCH_HIDDEN_STEMS = {
        "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
        "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "庚", "戊"],
        "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
        "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"]
    }

    def __init__(self, knowledge_base_path: str = None):
        """初始化神煞解读引擎"""
        if knowledge_base_path is None:
            kb_path = Path(__file__).parent.parent.parent.parent / "knowledge_base"
        else:
            kb_path = Path(knowledge_base_path)

        self.knowledge = self._load_knowledge(kb_path)

    def _load_knowledge(self, kb_path: Path) -> Dict:
        """加载神煞知识库"""
        try:
            shensha_file = kb_path / "shensha" / "shensha_knowledge.json"
            if shensha_file.exists():
                with open(shensha_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data
        except Exception as e:
            print(f"加载神煞知识库失败: {e}")
        return {}

    def interpret(self, shensha_list: List[Dict], sizhu: Dict, day_master: str) -> List[ShenShaDetail]:
        """
        对每个神煞进行深度解读

        Args:
            shensha_list: 神煞列表，每项含 {name, position, branch, category}
            sizhu: 四柱信息 {year_pillar, month_pillar, day_pillar, hour_pillar}
            day_master: 日主天干

        Returns:
            List[ShenShaDetail]: 每个神煞的详细解读
        """
        results = []

        for shensha in shensha_list:
            name = shensha.get("name", "")
            position = shensha.get("position", "")
            branch = shensha.get("branch", "")
            category = self._get_shensha_category(name)

            detail = self._interpret_single_shensha(
                name=name,
                position=position,
                branch=branch,
                category=category,
                sizhu=sizhu,
                day_master=day_master
            )

            results.append(detail)

        return results

    def _get_shensha_category(self, name: str) -> str:
        """获取神煞类别"""
        # 从知识库获取
        for cat_key in ["吉神", "凶煞", "中性神煞"]:
            cat_map = {
                "吉神": self.knowledge.get("ji_shen", {}).get("吉神", {}),
                "凶煞": self.knowledge.get("xiong_sha", {}).get("凶煞", {}),
                "中性神煞": self.knowledge.get("neutral_shensha", {}).get("中性神煞", {})
            }
            if name in cat_map.get(cat_key, {}):
                return cat_key

        # 默认分类
        default_categories = {
            "天乙贵人": "吉神", "月德贵人": "吉神", "天德贵人": "吉神",
            "文昌": "吉神", "驿马": "吉神", "华盖": "中性", "桃花": "中性",
            "禄神": "吉神", "羊刃": "中性", "魁罡": "中性", "金舆": "吉神",
            "孤辰": "凶煞", "寡宿": "凶煞", "亡神": "凶煞", "劫煞": "凶煞",
            "元辰": "凶煞", "灾煞": "凶煞", "勾绞": "凶煞", "咸池": "中性",
            "飞廉": "凶煞", "披头": "凶煞", "流霞": "凶煞",
            "空亡": "中性", "十恶大败": "凶煞", "天罗地网": "凶煞",
            "红鸾": "吉神", "天喜": "吉神", "国印贵人": "吉神",
            "福星贵人": "吉神", "天医贵人": "吉神",
            "三奇贵人": "吉神", "天厨贵人": "吉神", "太极贵人": "吉神",
            "阴差阳错": "凶煞", "孤鸾寡鹄": "凶煞", "破煞": "凶煞",
            "刑煞": "凶煞", "红艳": "中性"
        }
        return default_categories.get(name, "中性")

    def _get_shensha_info(self, name: str) -> Dict:
        """从知识库获取神煞详细信息"""
        for cat_key in ["吉神", "凶煞", "中性神煞"]:
            cat_map = {
                "吉神": self.knowledge.get("ji_shen", {}).get("吉神", {}),
                "凶煞": self.knowledge.get("xiong_sha", {}).get("凶煞", {}),
                "中性神煞": self.knowledge.get("neutral_shensha", {}).get("中性神煞", {})
            }
            info = cat_map.get(cat_key, {}).get(name, {})
            if info:
                return info
        return {}

    def _position_to_pillar(self, position: str, sizhu: Dict) -> Dict:
        """根据位置获取该柱的详细信息"""
        pillar_map = {
            "年": "year_pillar",
            "月": "month_pillar",
            "日": "day_pillar",
            "时": "hour_pillar"
        }
        pillar_key = pillar_map.get(position, "")
        if pillar_key and pillar_key in sizhu:
            return sizhu[pillar_key] if isinstance(sizhu[pillar_key], dict) else {}
        return {}

    def _interpret_single_shensha(
        self, name: str, position: str, branch: str,
        category: str, sizhu: Dict, day_master: str
    ) -> ShenShaDetail:
        """对单个神煞进行深度解读"""
        info = self._get_shensha_info(name)
        pillar_info = self._position_to_pillar(position, sizhu)

        # 获取该柱的十神
        stem = pillar_info.get("stem", "")
        shishen = self._get_shishen(day_master, stem) if stem else ""

        # 经典依据
        classic_source = info.get("source", "《三命通会》")
        original_text = info.get("original_text", "")
        if not original_text:
            original_text = info.get("查法", "")

        # 逻辑推导
        logical_derivation = self._derive_logical(name, position, branch, category, shishen, sizhu)

        # 获取影响
        raw_effects = info.get("effect", {})
        effects = {
            "career": raw_effects.get("career", "见综合分析"),
            "wealth": raw_effects.get("wealth", "见综合分析"),
            "marriage": raw_effects.get("marriage", "见综合分析"),
            "health": raw_effects.get("health", "见综合分析"),
            "personality": raw_effects.get("personality", "见综合分析")
        }

        # 位置影响
        position_effects = self._get_position_effect(name, position)

        # 合并位置影响
        for key in ["career", "wealth", "marriage", "health"]:
            if position_effects.get(key):
                effects[key] = position_effects[key] + "。" + effects[key]

        # 吉凶程度
        severity = info.get("severity", 3)
        # 根据位置调整：年柱力量小，月日柱力量大
        position_weight = {"年": 0.8, "月": 1.2, "日": 1.0, "时": 0.9}
        adjusted_severity = min(5, round(severity * position_weight.get(position, 1.0)))

        # 化解建议
        resolve = info.get("resolve")

        # 综合判断
        combined = self._generate_combined_analysis(
            name, category, position, branch, adjusted_severity,
            shishen, resolve, sizhu, day_master
        )

        return ShenShaDetail(
            name=name,
            category=category,
            position=f"{position}柱",
            branch=branch,
            classic_source=classic_source,
            original_text=original_text,
            logical_derivation=logical_derivation,
            effects=effects,
            severity=adjusted_severity,
            resolve=resolve,
            combined_analysis=combined
        )

    def _get_shishen(self, day_master: str, target_stem: str) -> str:
        """获取十神关系"""
        if not day_master or not target_stem:
            return ""

        dm_idx = self.HEAVENLY_STEMS.index(day_master) if day_master in self.HEAVENLY_STEMS else -1
        tg_idx = self.HEAVENLY_STEMS.index(target_stem) if target_stem in self.HEAVENLY_STEMS else -1

        if dm_idx == -1 or tg_idx == -1:
            return ""

        dm_wx = self.WUXING_MAP.get(day_master, "")
        tg_wx = self.WUXING_MAP.get(target_stem, "")

        # 相同五行
        if dm_wx == tg_wx:
            return "比肩" if dm_idx % 2 == tg_idx % 2 else "劫财"

        # 我生者
        sheng = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        if sheng.get(dm_wx) == tg_wx:
            return "食神" if dm_idx % 2 == tg_idx % 2 else "伤官"

        # 生我者
        reverse_sheng = {v: k for k, v in sheng.items()}
        if sheng.get(tg_wx) == dm_wx:
            return "偏印" if dm_idx % 2 == tg_idx % 2 else "正印"

        # 我克者
        ke = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
        if ke.get(dm_wx) == tg_wx:
            return "偏财" if dm_idx % 2 == tg_idx % 2 else "正财"

        # 克我者
        reverse_ke = {v: k for k, v in ke.items()}
        if ke.get(tg_wx) == dm_wx:
            return "七杀" if dm_idx % 2 == tg_idx % 2 else "正官"

        return ""

    def _derive_logical(self, name: str, position: str, branch: str,
                        category: str, shishen: str, sizhu: Dict) -> str:
        """生成逻辑推导过程"""
        parts = []

        # 基础逻辑：位置
        position_desc = {"年": "祖上根基", "月": "青年环境", "日": "自身根基", "时": "晚年后代"}
        parts.append(f"{name}出现在{position}柱（{position_desc.get(position, position)}）")

        # 神煞类别逻辑
        if category == "吉神":
            parts.append(f"属于吉神，总体为吉")
        elif category == "凶煞":
            parts.append(f"属于凶煞，需注意其负面作用")
        else:
            parts.append(f"属于中性神煞，吉凶视组合而定")

        # 与十神的交互逻辑
        if shishen:
            shishen_desc = self._shishen_shensha_interaction(shishen, name)
            if shishen_desc:
                parts.append(shishen_desc)

        # 与该柱五行的关系
        branch_wx = self.WUXING_MAP.get(branch, "")
        if branch_wx:
            parts.append(f"所在{branch}为{branch_wx}")

        return "；".join(parts)

    def _shishen_shensha_interaction(self, shishen: str, shensha: str) -> str:
        """十神与神煞的交互解读"""
        interactions = {
            "正官": "正官与吉神相遇，贵气增强，与凶煞相遇则贵气受损",
            "七杀": "七杀与凶煞同柱，凶煞加成；七杀与吉神同柱，凶中有制",
            "正印": "正印与文昌同柱，学业大旺；正印与劫煞同柱，学业受阻",
            "偏印": "偏印与华盖同柱，玄学缘分深厚",
            "正财": "正财与禄神同柱，财富稳定增长",
            "偏财": "偏财与驿马同柱，动中求财大发",
            "食神": "食神与天乙贵人同柱，食神生财得贵人助",
            "伤官": "伤官与羊刃同柱，性格刚烈易惹是非",
            "比肩": "比肩与劫煞同柱，竞争中易遭劫夺",
            "劫财": "劫财与亡神同柱，破财之势明显"
        }
        return interactions.get(shishen, "")

    def _get_position_effect(self, name: str, position: str) -> Dict:
        """获取神煞在不同位置的特定影响"""
        # 通用位置影响
        position_meanings = {
            "年": {"career": "祖业根基", "wealth": "祖上财运", "marriage": "早年感情", "health": "先天体质"},
            "月": {"career": "青年事业发展", "wealth": "青年财运", "marriage": "恋爱时期", "health": "青年健康"},
            "日": {"career": "中年事业高峰", "wealth": "一生财运核心", "marriage": "婚姻状况", "health": "终身健康"},
            "时": {"career": "晚年事业", "wealth": "晚年财运", "marriage": "晚年感情", "health": "晚年健康"}
        }

        # 特殊神煞的位置影响
        special_positions = self._get_special_position_effects(name, position)

        base = position_meanings.get(position, {})
        if special_positions:
            for k, v in special_positions.items():
                base[k] = v

        return base

    def _get_special_position_effects(self, name: str, position: str) -> Dict:
        """获取特定神煞在特定位置的专属影响"""
        special = {
            "天乙贵人": {
                "年": {"marriage": "祖上有贵人，嫁娶得体"},
                "月": {"career": "青年遇良师提携"},
                "日": {"marriage": "配偶亦是贵人"},
                "时": {"career": "晚年有下属相助"}
            },
            "桃花": {
                "年": {"marriage": "墙内桃花，夫妻恩愛"},
                "月": {"marriage": "早年桃花旺"},
                "日": {"marriage": "配偶有魅力"},
                "时": {"marriage": "墙外桃花，需自制"}
            },
            "驿马": {
                "年": {"career": "祖上迁徙"},
                "月": {"career": "青年奔波"},
                "日": {"career": "一生劳碌"},
                "时": {"career": "老来奔走"}
            },
            "华盖": {
                "年": {"personality": "祖上有修行之人"},
                "月": {"personality": "少年老成"},
                "日": {"personality": "才华出众"},
                "时": {"personality": "晚年修行"}
            },
            "空亡": {
                "年": {"career": "祖上基业虚空"},
                "月": {"career": "青年努力付诸东流"},
                "日": {"marriage": "配偶缘分薄弱"},
                "时": {"wealth": "晚年财来财去"}
            }
        }
        return special.get(name, {}).get(position, {})

    def _generate_combined_analysis(
        self, name: str, category: str, position: str, branch: str,
        severity: int, shishen: str, resolve: Optional[str],
        sizhu: Dict, day_master: str
    ) -> str:
        """生成综合判断文本"""
        parts = []

        # 神煞基本定位
        parts.append(f"【{name}】出现在{position}柱（地支{branch}）")

        # 类别与程度
        severity_desc = {5: "非常强烈", 4: "较为显著", 3: "中等程度", 2: "轻微影响", 1: "几乎无影响"}
        parts.append(f"影响程度：{severity_desc.get(severity, '中等')}（{severity}/5星）")

        if category == "吉神":
            if shishen in ["正官", "正印", "食神"]:
                parts.append("与吉十神同柱，吉上加吉")
            elif shishen in ["七杀", "劫财", "伤官"]:
                parts.append("与凶十神同柱，吉中有小憾")

        elif category == "凶煞":
            if shishen in ["正官", "正印", "食神"]:
                parts.append("被吉十神制化，凶势大减")
            else:
                parts.append("需特别注意对应方面")

        # 经典引述
        info = self._get_shensha_info(name)
        if info.get("source") and info.get("original_text"):
            parts.append(f"经典引述：{info['source']}")
        elif info.get("查法"):
            parts.append(f"查法口诀：{info.get('查法', '')}")

        # 建议
        if resolve:
            parts.append(f"化解建议：{resolve}")

        return "；".join(parts)

    def get_all_shensha_names(self) -> List[str]:
        """获取所有支持的神煞名称列表"""
        names = []
        for cat_key in ["ji_shen", "xiong_sha", "neutral_shensha"]:
            cat_data = self.knowledge.get(cat_key, {})
            for sub_key in cat_data:
                sub_data = cat_data[sub_key]
                if isinstance(sub_data, dict):
                    names.extend(sub_data.keys())
        return names


# ============ 神煞计算函数 ============

# ============ 模块级常量 ============
_MODULE_WUXING_MAP = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
    "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
    "戌": "土", "亥": "水"
}


_MODULE_HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
_MODULE_EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def calculate_shensha(year_pillar: Dict, month_pillar: Dict,
                       day_pillar: Dict, hour_pillar: Dict,
                       day_master: str) -> List[Dict]:
    """
    计算八字中的所有神煞
    返回神煞列表，每项含 {name, position, branch, category}

    覆盖至少30个主要神煞的查法
    """
    shensha_list = []

    year_stem = year_pillar.get("stem", "")
    year_branch = year_pillar.get("branch", "")
    month_stem = month_pillar.get("stem", "")
    month_branch = month_pillar.get("branch", "")
    day_stem = day_pillar.get("stem", "")
    day_branch = day_pillar.get("branch", "")
    hour_stem = hour_pillar.get("stem", "")
    hour_branch = hour_pillar.get("branch", "")

    pillars = [
        ("年", year_stem, year_branch),
        ("月", month_stem, month_branch),
        ("日", day_stem, day_branch),
        ("时", hour_stem, hour_branch)
    ]

    # ============ 天乙贵人 ============
    # 甲戊庚牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸兔蛇藏，六辛逢马虎
    tianyi_rules = {
        "甲": ["丑", "未"], "戊": ["丑", "未"], "庚": ["丑", "未"],
        "乙": ["子", "申"], "己": ["子", "申"],
        "丙": ["亥", "酉"], "丁": ["亥", "酉"],
        "壬": ["卯", "巳"], "癸": ["卯", "巳"],
        "辛": ["寅", "午"]
    }
    day_master_tianyi = tianyi_rules.get(day_master, [])
    for pos, stem, branch in pillars:
        if branch in day_master_tianyi:
            shensha_list.append({"name": "天乙贵人", "position": pos, "branch": branch, "category": "吉神"})

    # ============ 月德贵人 ============
    # 寅午戌月在丙，申子辰月在壬，亥卯未月在甲，巳酉丑月在庚
    yuede_rules = {
        "寅": "丙", "午": "丙", "戌": "丙",
        "申": "壬", "子": "壬", "辰": "壬",
        "亥": "甲", "卯": "甲", "未": "甲",
        "巳": "庚", "酉": "庚", "丑": "庚"
    }
    month_yuede = yuede_rules.get(month_branch, "")
    if month_yuede:
        for pos, stem, branch in pillars:
            if stem == month_yuede:
                shensha_list.append({"name": "月德贵人", "position": pos, "branch": branch, "category": "吉神"})

    # ============ 天德贵人 ============
    # 正丁二申中，三壬四辛同，五亥六甲上，七癸八寅逢，九丙十居乙，子巳丑庚中
    tiande_rules = {
        "寅": "丁", "卯": "申", "辰": "壬", "巳": "辛",
        "午": "亥", "未": "甲", "申": "癸", "酉": "寅",
        "戌": "丙", "亥": "乙", "子": "巳", "丑": "庚"
    }
    month_tiande = tiande_rules.get(month_branch, "")
    if month_tiande:
        for pos, stem, branch in pillars:
            if stem == month_tiande or branch == month_tiande:
                shensha_list.append({"name": "天德贵人", "position": pos, "branch": branch, "category": "吉神"})

    # ============ 文昌贵人 ============
    # 甲乙巳午报君知，丙戊申宫丁己鸡，庚猪辛鼠壬逢虎，癸人见卯入云梯
    wenchang_rules = {
        "甲": "巳", "乙": "午",
        "丙": "申", "戊": "申", "丁": "酉", "己": "酉",
        "庚": "亥", "辛": "子",
        "壬": "寅", "癸": "卯"
    }
    dm_wenchang = wenchang_rules.get(day_master, "")
    if dm_wenchang:
        for pos, stem, branch in pillars:
            if branch == dm_wenchang:
                shensha_list.append({"name": "文昌", "position": pos, "branch": branch, "category": "吉神"})

    # ============ 驿马 ============
    # 申子辰马在寅，亥卯未马在巳，寅午戌马在申，巳酉丑马在亥
    yima_rules = {
        "申": "寅", "子": "寅", "辰": "寅",
        "亥": "巳", "卯": "巳", "未": "巳",
        "寅": "申", "午": "申", "戌": "申",
        "巳": "亥", "酉": "亥", "丑": "亥"
    }
    for pos, stem, branch in pillars:
        yima_branch = yima_rules.get(branch, "")
        if yima_branch:
            for p2, s2, b2 in pillars:
                if b2 == yima_branch:
                    shensha_list.append({"name": "驿马", "position": p2, "branch": b2, "category": "吉神"})

    # ============ 华盖 ============
    # 寅午戌见戌，巳酉丑见丑，申子辰见辰，亥卯未见未
    huagai_rules = {
        "寅": "戌", "午": "戌", "戌": "戌",
        "巳": "丑", "酉": "丑", "丑": "丑",
        "申": "辰", "子": "辰", "辰": "辰",
        "亥": "未", "卯": "未", "未": "未"
    }
    for pos, stem, branch in pillars:
        huagai_branch = huagai_rules.get(branch, "")
        if huagai_branch:
            for p2, s2, b2 in pillars:
                if b2 == huagai_branch:
                    shensha_list.append({"name": "华盖", "position": p2, "branch": b2, "category": "中性"})

    # ============ 桃花(咸池) ============
    # 寅午戌见卯，亥卯未见子，申子辰见酉，巳酉丑见午
    taohua_rules = {
        "寅": "卯", "午": "卯", "戌": "卯",
        "亥": "子", "卯": "子", "未": "子",
        "申": "酉", "子": "酉", "辰": "酉",
        "巳": "午", "酉": "午", "丑": "午"
    }
    for pos, stem, branch in pillars:
        th_branch = taohua_rules.get(branch, "")
        if th_branch:
            for p2, s2, b2 in pillars:
                if b2 == th_branch:
                    shensha_list.append({"name": "桃花", "position": p2, "branch": b2, "category": "中性"})

    # ============ 禄神 ============
    # 甲禄到寅，乙禄到卯，丙戊禄在巳，丁己禄在午，庚禄在申，辛禄在酉，壬禄在亥，癸禄在子
    lu_rules = {
        "甲": "寅", "乙": "卯", "丙": "巳", "戊": "巳",
        "丁": "午", "己": "午", "庚": "申", "辛": "酉",
        "壬": "亥", "癸": "子"
    }
    dm_lu = lu_rules.get(day_master, "")
    if dm_lu:
        for pos, stem, branch in pillars:
            if branch == dm_lu:
                shensha_list.append({"name": "禄神", "position": pos, "branch": branch, "category": "吉神"})

    # ============ 羊刃 ============
    # 甲刃在卯，乙刃在寅，丙戊刃在午，丁己刃在巳，庚刃在酉，辛刃在申，壬刃在子，癸刃在亥
    ren_rules = {
        "甲": "卯", "乙": "寅", "丙": "午", "戊": "午",
        "丁": "巳", "己": "巳", "庚": "酉", "辛": "申",
        "壬": "子", "癸": "亥"
    }
    dm_ren = ren_rules.get(day_master, "")
    if dm_ren:
        for pos, stem, branch in pillars:
            if branch == dm_ren:
                shensha_list.append({"name": "羊刃", "position": pos, "branch": branch, "category": "中性"})

    # ============ 魁罡 ============
    # 壬辰、庚戌、庚辰、戊戌
    kuigang_days = ["壬辰", "庚戌", "庚辰", "戊戌"]
    day_ganzhi = day_stem + day_branch
    if day_ganzhi in kuigang_days:
        shensha_list.append({"name": "魁罡", "position": "日", "branch": day_branch, "category": "中性"})

    # ============ 金舆 ============
    # 甲龙乙蛇丙午羊，丁己猴歌戊二方，己酉庚猪辛鼠位，壬牛癸虎
    jinyu_rules = {
        "甲": "辰", "乙": "巳", "丙": "午", "丁": "申",
        "戊": "未", "己": "酉", "庚": "亥", "辛": "子",
        "壬": "丑", "癸": "寅"
    }
    dm_jinyu = jinyu_rules.get(day_master, "")
    if dm_jinyu:
        for pos, stem, branch in pillars:
            if branch == dm_jinyu:
                shensha_list.append({"name": "金舆", "position": pos, "branch": branch, "category": "吉神"})

    # ============ 孤辰寡宿 ============
    guchen_rules = {
        "亥": ("寅", "戌"), "子": ("寅", "戌"), "丑": ("寅", "戌"),
        "寅": ("巳", "丑"), "卯": ("巳", "丑"), "辰": ("巳", "丑"),
        "巳": ("申", "辰"), "午": ("申", "辰"), "未": ("申", "辰"),
        "申": ("亥", "未"), "酉": ("亥", "未"), "戌": ("亥", "未")
    }
    for pos, stem, branch in pillars:
        if branch in guchen_rules:
            gc, gs = guchen_rules[branch]
            for p2, s2, b2 in pillars:
                if b2 == gc:
                    shensha_list.append({"name": "孤辰", "position": p2, "branch": b2, "category": "凶煞"})
                if b2 == gs:
                    shensha_list.append({"name": "寡宿", "position": p2, "branch": b2, "category": "凶煞"})

    # ============ 亡神 ============
    # 申子辰见亥，亥卯未见寅，寅午戌见巳，巳酉丑见申
    wangshen_rules = {
        "申": "亥", "子": "亥", "辰": "亥",
        "亥": "寅", "卯": "寅", "未": "寅",
        "寅": "巳", "午": "巳", "戌": "巳",
        "巳": "申", "酉": "申", "丑": "申"
    }
    for pos, stem, branch in pillars:
        ws = wangshen_rules.get(branch, "")
        if ws:
            for p2, s2, b2 in pillars:
                if b2 == ws:
                    shensha_list.append({"name": "亡神", "position": p2, "branch": b2, "category": "凶煞"})

    # ============ 劫煞 ============
    # 申子辰见巳，亥卯未见申，寅午戌见亥，巳酉丑见寅
    jiesha_rules = {
        "申": "巳", "子": "巳", "辰": "巳",
        "亥": "申", "卯": "申", "未": "申",
        "寅": "亥", "午": "亥", "戌": "亥",
        "巳": "寅", "酉": "寅", "丑": "寅"
    }
    for pos, stem, branch in pillars:
        js = jiesha_rules.get(branch, "")
        if js:
            for p2, s2, b2 in pillars:
                if b2 == js:
                    shensha_list.append({"name": "劫煞", "position": p2, "branch": b2, "category": "凶煞"})

    # ============ 灾煞 ============
    # 申子辰见午，亥卯未见酉，寅午戌见子，巳酉丑见卯
    zaisha_rules = {
        "申": "午", "子": "午", "辰": "午",
        "亥": "酉", "卯": "酉", "未": "酉",
        "寅": "子", "午": "子", "戌": "子",
        "巳": "卯", "酉": "卯", "丑": "卯"
    }
    for pos, stem, branch in pillars:
        zs = zaisha_rules.get(branch, "")
        if zs:
            for p2, s2, b2 in pillars:
                if b2 == zs:
                    shensha_list.append({"name": "灾煞", "position": p2, "branch": b2, "category": "凶煞"})

    # ============ 勾绞 ============
    # 阳年（甲丙戊庚壬）见前三辰为勾，后三辰为绞
    yang_year_stems = ["甲", "丙", "戊", "庚", "壬"]
    if year_stem in yang_year_stems:
        year_branch_idx = "子丑寅卯辰巳午未申酉戌亥".index(year_branch)
        gou_branch = "子丑寅卯辰巳午未申酉戌亥"[(year_branch_idx + 3) % 12]
        jiao_branch = "子丑寅卯辰巳午未申酉戌亥"[(year_branch_idx - 3) % 12]
        for pos, stem, branch in pillars:
            if branch == gou_branch:
                shensha_list.append({"name": "勾绞", "position": pos, "branch": branch, "category": "凶煞"})

    # ============ 飞廉 ============
    feilian_rules = {
        "子": "申", "丑": "酉", "寅": "戌", "卯": "巳",
        "辰": "午", "巳": "未", "午": "寅", "未": "卯",
        "申": "辰", "酉": "亥", "戌": "子", "亥": "丑"
    }
    year_fl = feilian_rules.get(year_branch, "")
    if year_fl:
        for pos, stem, branch in pillars:
            if branch == year_fl:
                shensha_list.append({"name": "飞廉", "position": pos, "branch": branch, "category": "凶煞"})

    # ============ 披头 ============
    pitou_rules = {
        "子": "戌", "丑": "亥", "寅": "子", "卯": "丑",
        "辰": "寅", "巳": "卯", "午": "辰", "未": "巳",
        "申": "午", "酉": "未", "戌": "申", "亥": "酉"
    }
    year_pt = pitou_rules.get(year_branch, "")
    if year_pt:
        for pos, stem, branch in pillars:
            if branch == year_pt:
                shensha_list.append({"name": "披头", "position": pos, "branch": branch, "category": "凶煞"})

    # ============ 流霞 ============
    liuxia_rules = {
        "甲": "酉", "乙": "戌", "丙": "未", "丁": "申",
        "戊": "未", "己": "申", "庚": "午", "辛": "巳",
        "壬": "乙", "癸": "卯"
    }
    dm_lx = liuxia_rules.get(day_master, "")
    if dm_lx:
        for pos, stem, branch in pillars:
            if stem == dm_lx or branch == dm_lx:
                shensha_list.append({"name": "流霞", "position": pos, "branch": branch, "category": "凶煞"})

    # ============ 空亡 ============
    # 甲子旬戌亥空，甲戌旬申酉空，甲申旬午未空，甲午旬辰巳空，甲辰旬寅卯空，甲寅旬子丑空
    kongwang_rules = {
        "甲子": "戌亥", "甲戌": "申酉", "甲申": "午未",
        "甲午": "辰巳", "甲辰": "寅卯", "甲寅": "子丑"
    }
    day_cycle = day_stem + day_branch
    for cycle_start, empty_branches in kongwang_rules.items():
        # 判断日柱是否在该旬中
        cycle_start_idx = "甲乙丙丁戊己庚辛壬癸".index(cycle_start[0])
        day_stem_idx = "甲乙丙丁戊己庚辛壬癸".index(day_stem)
        if day_stem_idx in range(cycle_start_idx, cycle_start_idx + 10):
            for pos, stem, branch in pillars:
                if branch in empty_branches:
                    shensha_list.append({"name": "空亡", "position": pos, "branch": branch, "category": "中性"})
            break

    # ============ 十恶大败 ============
    # 甲辰、乙巳、丙申、丁亥、戊戌、己丑、庚辰、辛巳、壬申、癸亥
    shi_e_days = ["甲辰", "乙巳", "丙申", "丁亥", "戊戌", "己丑", "庚辰", "辛巳", "壬申", "癸亥"]
    if day_ganzhi in shi_e_days:
        shensha_list.append({"name": "十恶大败", "position": "日", "branch": day_branch, "category": "凶煞"})

    # ============ 天罗地网 ============
    # 火命人见戌亥为天罗，水土命人见辰巳为地网
    day_master_wuxing = _MODULE_WUXING_MAP.get(day_master, "")
    if day_master_wuxing == "火":
        for pos, stem, branch in pillars:
            if branch in ["戌", "亥"]:
                shensha_list.append({"name": "天罗", "position": pos, "branch": branch, "category": "凶煞"})
    elif day_master_wuxing in ["水", "土"]:
        for pos, stem, branch in pillars:
            if branch in ["辰", "巳"]:
                shensha_list.append({"name": "地网", "position": pos, "branch": branch, "category": "凶煞"})

    # ============ 红鸾 ============
    # 子丑寅卯辰巳午未申酉戌亥 -> 红鸾在卯寅丑子亥戌酉申未午巳辰
    hongluan_rules = {
        "子": "卯", "丑": "寅", "寅": "丑", "卯": "子",
        "辰": "亥", "巳": "戌", "午": "酉", "未": "申",
        "申": "未", "酉": "午", "戌": "巳", "亥": "辰"
    }
    year_hl = hongluan_rules.get(year_branch, "")
    if year_hl:
        for pos, stem, branch in pillars:
            if branch == year_hl:
                shensha_list.append({"name": "红鸾", "position": pos, "branch": branch, "category": "吉神"})

    # ============ 天喜 ============
    # 红鸾对宫
    tianxi_rules = {
        "卯": "酉", "寅": "申", "丑": "未", "子": "午",
        "亥": "巳", "戌": "辰", "酉": "卯", "申": "寅",
        "未": "丑", "午": "子", "巳": "亥", "辰": "戌"
    }
    if year_hl:
        tx = tianxi_rules.get(year_hl, "")
        if tx:
            for pos, stem, branch in pillars:
                if branch == tx:
                    shensha_list.append({"name": "天喜", "position": pos, "branch": branch, "category": "吉神"})

    # ============ 国印贵人 ============
    guoyin_rules = {
        "甲": "戌", "乙": "亥", "丙": "丑", "丁": "寅",
        "戊": "丑", "己": "寅", "庚": "辰", "辛": "巳",
        "壬": "未", "癸": "申"
    }
    dm_gy = guoyin_rules.get(day_master, "")
    if dm_gy:
        for pos, stem, branch in pillars:
            if branch == dm_gy:
                shensha_list.append({"name": "国印贵人", "position": pos, "branch": branch, "category": "吉神"})

    # ============ 福星贵人 ============
    fuxing_rules = {
        "甲": ("寅", "子"), "丙": ("寅", "子"), "戊": ("申", "未"),
        "乙": ("丑", "卯"), "丁": ("亥",), "己": ("申",), "癸": ("丑",),
        "庚": ("午",), "辛": ("巳",), "壬": ("辰",)
    }
    dm_fx = fuxing_rules.get(day_master, [])
    if dm_fx:
        for pos, stem, branch in pillars:
            if branch in dm_fx:
                shensha_list.append({"name": "福星贵人", "position": pos, "branch": branch, "category": "吉神"})

    # ============ 天医贵人 ============
    tianyi_rules_month = {
        "寅": "戌", "卯": "亥", "辰": "子", "巳": "丑",
        "午": "寅", "未": "卯", "申": "辰", "酉": "巳",
        "戌": "午", "亥": "未", "子": "申", "丑": "酉"
    }
    month_ty = tianyi_rules_month.get(month_branch, "")
    if month_ty:
        for pos, stem, branch in pillars:
            if branch == month_ty:
                shensha_list.append({"name": "天医贵人", "position": pos, "branch": branch, "category": "吉神"})

    # ============ 三奇贵人 ============
    # 天三奇：甲戊庚 地三奇：乙丙丁 人三奇：辛壬癸
    year_month_day = [year_stem, month_stem, day_stem]
    san_qi_sets = [["甲", "戊", "庚"], ["乙", "丙", "丁"], ["辛", "壬", "癸"]]
    for sq_set in san_qi_sets:
        matched = all(s in year_month_day for s in sq_set)
        if matched:
            for idx, s in enumerate(sq_set):
                for pos, stem, branch in pillars:
                    if stem == s:
                        shensha_list.append({
                            "name": "三奇贵人",
                            "position": pos,
                            "branch": branch,
                            "category": "吉神"
                        })
            break

    # ============ 太极贵人 ============
    taiji_rules = {
        "甲": ("子", "午"), "乙": ("子", "午"),
        "丙": ("酉", "卯"), "丁": ("酉", "卯"),
        "戊": ("辰", "戌", "丑", "未"), "己": ("辰", "戌", "丑", "未"),
        "庚": ("寅", "亥"), "辛": ("寅", "亥"),
        "壬": ("巳", "申"), "癸": ("巳", "申")
    }
    dm_tj = taiji_rules.get(day_master, [])
    if dm_tj:
        for pos, stem, branch in pillars:
            if branch in dm_tj:
                shensha_list.append({"name": "太极贵人", "position": pos, "branch": branch, "category": "吉神"})

    # ============ 阴差阳错 ============
    yincha_days = ["丙子", "丁丑", "戊寅", "辛卯", "壬辰", "癸巳",
                   "丙午", "丁未", "戊申", "辛酉", "壬戌", "癸亥"]
    if day_ganzhi in yincha_days:
        shensha_list.append({"name": "阴差阳错", "position": "日", "branch": day_branch, "category": "凶煞"})

    # ============ 孤鸾寡鹄 ============
    guluan_days = ["乙巳", "丁巳", "辛亥", "戊申", "甲寅", "丙午", "戊午", "壬子"]
    if day_ganzhi in guluan_days:
        shensha_list.append({"name": "孤鸾寡鹄", "position": "日", "branch": day_branch, "category": "凶煞"})

    # ============ 元辰(大耗) ============
    # 阳男阴女冲前一位，阴男阳女冲后一位
    year_branch_idx = "子丑寅卯辰巳午未申酉戌亥".index(year_branch)
    yuan_chen_before = "子丑寅卯辰巳午未申酉戌亥"[(year_branch_idx + 6 + 1) % 12]
    yuan_chen_after = "子丑寅卯辰巳午未申酉戌亥"[(year_branch_idx + 6 - 1) % 12]
    for pos, stem, branch in pillars:
        if branch == yuan_chen_before or branch == yuan_chen_after:
            shensha_list.append({"name": "元辰", "position": pos, "branch": branch, "category": "凶煞"})

    # ============ 天厨贵人 ============
    tianchu_rules = {
        "甲": "巳", "乙": "午", "丙": "巳", "丁": "午",
        "戊": "申", "己": "酉", "庚": "亥", "辛": "子",
        "壬": "寅", "癸": "卯"
    }
    dm_tc = tianchu_rules.get(day_master, "")
    if dm_tc:
        for pos, stem, branch in pillars:
            if branch == dm_tc:
                shensha_list.append({"name": "天厨贵人", "position": pos, "branch": branch, "category": "吉神"})

    # ============ 红艳 ============
    hongyan_rules = {
        "甲": ("午", "申"), "乙": ("午", "申"),
        "丙": ("寅", "辰"), "丁": ("寅", "辰"),
        "戊": ("午", "辰"), "己": ("午", "辰"),
        "庚": ("戌", "亥"), "辛": ("戌", "亥"),
        "壬": ("申", "酉"), "癸": ("申", "酉")
    }
    dm_hy = hongyan_rules.get(day_master, [])
    if dm_hy:
        for pos, stem, branch in pillars:
            if branch in dm_hy or stem in dm_hy:
                shensha_list.append({"name": "红艳", "position": pos, "branch": branch, "category": "中性"})

    # ============ 去重 ============
    seen = set()
    unique_shensha = []
    for ss in shensha_list:
        key = (ss["name"], ss["position"])
        if key not in seen:
            seen.add(key)
            unique_shensha.append(ss)

    return unique_shensha


# ============ 测试 ============

def test_shensha_interpreter():
    """测试神煞解读引擎"""
    interpreter = ShenShaInterpreter()

    # 测试八字：甲子 丙寅 丙午 戊戌（丙火日主）
    sizhu = {
        "year_pillar": {"stem": "甲", "branch": "子"},
        "month_pillar": {"stem": "丙", "branch": "寅"},
        "day_pillar": {"stem": "丙", "branch": "午"},
        "hour_pillar": {"stem": "戊", "branch": "戌"}
    }
    day_master = "丙"

    shensha_list = calculate_shensha(
        sizhu["year_pillar"], sizhu["month_pillar"],
        sizhu["day_pillar"], sizhu["hour_pillar"],
        day_master
    )

    print("=== 神煞计算测试 ===")
    print(f"\n日主：{day_master}")
    print(f"四柱：{sizhu['year_pillar']['stem']}{sizhu['year_pillar']['branch']} "
          f"{sizhu['month_pillar']['stem']}{sizhu['month_pillar']['branch']} "
          f"{sizhu['day_pillar']['stem']}{sizhu['day_pillar']['branch']} "
          f"{sizhu['hour_pillar']['stem']}{sizhu['hour_pillar']['branch']}")

    print(f"\n命中所带神煞（{len(shensha_list)}个）：")
    for ss in shensha_list:
        print(f"  {ss['position']}柱：{ss['name']}（{ss['category']}）")

    # 解读
    print("\n=== 神煞深度解读 ===")
    results = interpreter.interpret(shensha_list, sizhu, day_master)
    for r in results:
        print(f"\n【{r.name}】（{r.category}）位于{r.position}")
        print(f"  经典依据：{r.classic_source}")
        print(f"  逻辑推导：{r.logical_derivation}")
        print(f"  事业影响：{r.effects['career']}")
        print(f"  财运影响：{r.effects['wealth']}")
        print(f"  婚姻影响：{r.effects['marriage']}")
        print(f"  健康影响：{r.effects['health']}")
        print(f"  性格影响：{r.effects['personality']}")
        print(f"  凶吉程度：{'★' * r.severity}{'☆' * (5 - r.severity)}（{r.severity}/5）")
        if r.resolve:
            print(f"  化解建议：{r.resolve}")
        print(f"  综合分析：{r.combined_analysis}")

    return results


if __name__ == "__main__":
    test_shensha_interpreter()
