"""
小运解读引擎
基于《渊海子平》「论小运」理论

小运用于补充大运和流年，提供更精细的年度运势微调信息
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class XiaoYunDetail:
    """小运解读"""
    xiaoyun_ganzhi: str        # 小运干支
    age: int                    # 年龄
    direction: str              # 顺行/逆行
    wuxing_effect: str          # 五行影响
    dayun_micro: str            # 对大运的微调作用
    liunian_supplement: str     # 对流年的补充
    specific_hints: List[str]   # 具体应期参考
    summary: str                # 总结


class XiaoYunInterpreter:
    """小运解读引擎"""

    HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    WUXING_MAP = {
        "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
        "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
        "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
        "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
        "戌": "土", "亥": "水"
    }

    def __init__(self, knowledge_base_path: str = None):
        """初始化小运解读引擎"""
        if knowledge_base_path is None:
            kb_path = Path(__file__).parent.parent.parent.parent / "knowledge_base"
        else:
            kb_path = Path(knowledge_base_path)
        self.knowledge = self._load_knowledge(kb_path)

    def _load_knowledge(self, kb_path: Path) -> Dict:
        """加载小运知识库"""
        try:
            file = kb_path / "xiaoyun" / "xiaoyun_knowledge.json"
            if file.exists():
                with open(file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def interpret(self, xiaoyun: str, age: int, chart: Dict) -> XiaoYunDetail:
        """
        小运补充解读

        Args:
            xiaoyun: 小运干支，如"甲子"
            age: 当前年龄
            chart: 八字命盘

        Returns:
            XiaoYunDetail: 小运详细解读
        """
        stem = xiaoyun[0] if len(xiaoyun) >= 2 else ""
        branch = xiaoyun[1:] if len(xiaoyun) >= 2 else ""

        stem_wx = self.WUXING_MAP.get(stem, "")
        branch_wx = self.WUXING_MAP.get(branch, "")

        # 方向
        gender = chart.get("gender", "男")
        year_stem = chart.get("year_pillar", {}).get("stem", "")
        direction = self._get_direction(gender, year_stem)

        # 五行影响
        wuxing_effect = self._analyze_wuxing_effect(stem_wx, branch_wx, chart)

        # 对大运的微调
        dayun_micro = self._analyze_dayun_micro(stem_wx, branch_wx, chart)

        # 对流年的补充
        liunian_supplement = self._analyze_liunian_supplement(stem_wx, chart)

        # 具体应期
        specific_hints = self._generate_hints(stem, branch, stem_wx, chart)

        # 总结
        summary = f"{age}岁小运为{xiaoyun}（{direction}），{wuxing_effect}。{dayun_micro}"

        return XiaoYunDetail(
            xiaoyun_ganzhi=xiaoyun,
            age=age,
            direction=direction,
            wuxing_effect=wuxing_effect,
            dayun_micro=dayun_micro,
            liunian_supplement=liunian_supplement,
            specific_hints=specific_hints,
            summary=summary
        )

    def _get_direction(self, gender: str, year_stem: str) -> str:
        """判断小运行运方向"""
        yang_stems = ["甲", "丙", "戊", "庚", "壬"]
        is_yang = year_stem in yang_stems

        # 阳男阴女顺行，阴男阳女逆行
        if (gender == "男" and is_yang) or (gender == "女" and not is_yang):
            return "顺行"
        else:
            return "逆行"

    def _analyze_wuxing_effect(self, stem_wx: str, branch_wx: str, chart: Dict) -> str:
        """分析小运五行对命局的影响"""
        day_master = chart.get("day_master", "")
        day_master_wx = chart.get("day_master_wuxing", "")

        effects = []

        # 天干五行影响
        if stem_wx and day_master_wx:
            if stem_wx == day_master_wx:
                effects.append(f"小运天干{stem_wx}同日主{day_master}五行，为比劫之助/争")
            elif self._is_sheng(stem_wx, day_master_wx):
                effects.append(f"小运天干{stem_wx}生日主{day_master_wx}，有贵人相助")
            elif self._is_sheng(day_master_wx, stem_wx):
                effects.append(f"日主生小运，输出之年，才华展现")
            elif self._is_ke(stem_wx, day_master_wx):
                effects.append(f"小运天干{stem_wx}克日主{day_master_wx}，压力之年")
            elif self._is_ke(day_master_wx, stem_wx):
                effects.append(f"日主克小运，财运之年")

        return "。".join(effects) if effects else "小运五行对命局影响有限。"

    def _is_sheng(self, wx1: str, wx2: str) -> bool:
        sheng = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        return sheng.get(wx1) == wx2

    def _is_ke(self, wx1: str, wx2: str) -> bool:
        ke = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
        return ke.get(wx1) == wx2

    def _analyze_dayun_micro(self, stem_wx: str, branch_wx: str, chart: Dict) -> str:
        """分析小运对大运的微调作用"""
        # 获取当前大运
        current_dayun = chart.get("current_dayun", {})
        dayun_ganzhi = current_dayun.get("ganzhi", "")

        if not dayun_ganzhi:
            return "小运对大运的微调作用见具体分析。"

        dy_stem = dayun_ganzhi[0] if len(dayun_ganzhi) >= 2 else ""
        dy_stem_wx = self.WUXING_MAP.get(dy_stem, "")

        # 比较小运与大运
        if stem_wx and dy_stem_wx:
            if stem_wx == dy_stem_wx:
                return f"小运{stem_wx}与大运{dy_stem_wx}同向，加强大运之能量。"
            elif self._is_sheng(stem_wx, dy_stem_wx):
                return f"小运{stem_wx}生大运{dy_stem_wx}，大运能量得到助力。"
            elif self._is_ke(stem_wx, dy_stem_wx):
                return f"小运{stem_wx}克大运{dy_stem_wx}，削弱大运之影响，是本年的变数。"
            else:
                return f"小运{stem_wx}与大运{dy_stem_wx}无特殊生克关系。"

        return ""

    def _analyze_liunian_supplement(self, stem_wx: str, chart: Dict) -> str:
        """分析小运对流年的补充"""
        return f"小运五行{stem_wx}，与流年互动需结合具体干支判断。"

    def _generate_hints(self, stem: str, branch: str, stem_wx: str, chart: Dict) -> List[str]:
        """生成具体应期参考"""
        hints = []

        day_master = chart.get("day_master", "")
        day_master_wx = chart.get("day_master_wuxing", "")

        if stem_wx == "木" and day_master_wx == "火":
            hints.append(f"小运{stem}生助日主{day_master}，此年有学习、进修之机")
        elif stem_wx == "火" and day_master_wx == "土":
            hints.append(f"小运{stem}生助日主{day_master}，利于团队合作")
        elif stem_wx == "土" and day_master_wx == "金":
            hints.append(f"小运{stem}生助日主{day_master}，有财运之信号")
        elif stem_wx == "金" and day_master_wx == "水":
            hints.append(f"小运{stem}生助日主{day_master}，利于人际关系")
        elif stem_wx == "水" and day_master_wx == "木":
            hints.append(f"小运{stem}生助日主{day_master}，利于事业发展")

        if not hints:
            hints.append(f"小运{stem}{branch}为补充参考，需结合大运流年综合判断。")

        return hints


def calculate_xiaoyun(age: int, chart: Dict) -> str:
    """
    计算某岁的小运干支

    规则：男命顺推，女命逆推，从年柱开始
    """
    year_pillar = chart.get("year_pillar", {})
    year_stem = year_pillar.get("stem", "")
    year_branch = year_pillar.get("branch", "")
    gender = chart.get("gender", "男")

    HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    yang_stems = ["甲", "丙", "戊", "庚", "壬"]
    is_yang = year_stem in yang_stems

    # 确定方向
    if (gender == "男" and is_yang) or (gender == "女" and not is_yang):
        direction = 1  # 顺行
    else:
        direction = -1  # 逆行

    # 年柱索引
    stem_idx = HEAVENLY_STEMS.index(year_stem)
    branch_idx = EARTHLY_BRANCHES.index(year_branch)

    # 小运 = 年柱 +/- 年龄-1
    shift = age - 1
    xiaoyun_stem = HEAVENLY_STEMS[(stem_idx + direction * shift) % 10]
    xiaoyun_branch = EARTHLY_BRANCHES[(branch_idx + direction * shift) % 12]

    return xiaoyun_stem + xiaoyun_branch


def test_xiaoyun_interpreter():
    """测试小运解读引擎"""
    interpreter = XiaoYunInterpreter()

    test_chart = {
        "year_pillar": {"stem": "甲", "branch": "子"},
        "month_pillar": {"stem": "丙", "branch": "寅"},
        "day_pillar": {"stem": "丙", "branch": "午"},
        "hour_pillar": {"stem": "戊", "branch": "戌"},
        "day_master": "丙",
        "day_master_wuxing": "火",
        "gender": "男",
        "current_dayun": {"ganzhi": "戊辰", "age_start": 36, "age_end": 45}
    }

    ages = [30, 35, 40, 42]
    for age in ages:
        xiaoyun = calculate_xiaoyun(age, test_chart)
        result = interpreter.interpret(xiaoyun, age, test_chart)

        print(f"\n=== {age}岁小运 ===")
        print(f"  小运干支：{result.xiaoyun_ganzhi}（{result.direction}）")
        print(f"  五行影响：{result.wuxing_effect[:50]}")
        print(f"  大运微调：{result.dayun_micro[:50]}")
        for hint in result.specific_hints:
            print(f"  · {hint}")

    return result


if __name__ == "__main__":
    test_xiaoyun_interpreter()
