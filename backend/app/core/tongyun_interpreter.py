"""
童运解读引擎（12岁以内）
基于《三命通会》「小儿贵格」、《渊海子平》等经典

对儿童运势进行专项解读：
1. 幼年体质强弱
2. 学业天赋（文昌位置）
3. 父母缘份
4. 注意事项（防什么）
5. 各年龄段关键点
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class TongYunDetail:
    """童运专项解读"""
    age_range: str              # 年龄段
    physical: str               # 体质
    education: str              # 学业天赋
    parent_relation: str        # 父母缘份
    precautions: List[str]      # 注意事项
    key_points: str             # 关键点
    summary: str                # 总结


class TongYunInterpreter:
    """童运解读引擎（12岁以内）"""

    HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    WUXING_MAP = {
        "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
        "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
        "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
        "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
        "戌": "土", "亥": "水"
    }

    BRANCH_HIDDEN_STEMS = {
        "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
        "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "庚", "戊"],
        "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
        "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"]
    }

    def __init__(self, knowledge_base_path: str = None):
        """初始化童运解读引擎"""
        if knowledge_base_path is None:
            kb_path = Path(__file__).parent.parent.parent.parent / "knowledge_base"
        else:
            kb_path = Path(knowledge_base_path)
        self.knowledge = self._load_knowledge(kb_path)

    def _load_knowledge(self, kb_path: Path) -> Dict:
        """加载童运知识库"""
        try:
            file = kb_path / "tongyun" / "tongyun_knowledge.json"
            if file.exists():
                with open(file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def interpret(self, tongyun_list: List[Dict], chart: Dict) -> List[TongYunDetail]:
        """
        童运专项解读

        Args:
            tongyun_list: 早期大运列表（0-12岁），每项 {ganzhi, age_start, age_end}
            chart: 八字命盘

        Returns:
            List[TongYunDetail]: 各阶段童运解读
        """
        if not tongyun_list:
            return []

        results = []
        current_age = chart.get("current_age", 0)

        # 体质分析（全局）
        body_strength = self._analyze_physical_constitution(chart)

        # 学业天赋
        wenchang_positions = self._find_wenchang(chart)
        education_nature = self._analyze_education_nature(chart)

        # 父母缘份
        parent_relation = self._analyze_parent_relation(chart)

        # 各年龄段的注意事项
        general_precautions = self._general_precautions(chart)

        for i, yun in enumerate(tongyun_list):
            ganzhi = yun.get("ganzhi", "")
            age_start = yun.get("age_start", 0)
            age_end = yun.get("age_end", 0)

            if age_start > 12:
                continue

            stem = ganzhi[0] if len(ganzhi) >= 2 else ""
            branch = ganzhi[1:] if len(ganzhi) >= 2 else ""

            # 年龄段
            if age_end <= 3:
                age_range = f"{age_start}-{age_end}岁（幼婴期）"
            elif age_end <= 6:
                age_range = f"{age_start}-{age_end}岁（幼儿期）"
            elif age_end <= 9:
                age_range = f"{age_start}-{age_end}岁（学龄期）"
            else:
                age_range = f"{age_start}-{age_end}岁（少年期）"

            # 体质
            phase_physical = self._phase_physical(body_strength, age_start, stem, chart)

            # 学业
            phase_education = self._phase_education(education_nature, age_start, wenchang_positions, chart)

            # 父母
            phase_parent = self._phase_parent(parent_relation, age_start, chart)

            # 该阶段注意事项
            phase_precautions = self._phase_precautions(general_precautions, age_start, stem, chart)

            # 关键点
            key_points = self._key_points(age_start, age_end, chart)

            # 总结
            summary_parts = [
                f"年龄{age_start}-{age_end}岁",
                f"体质：{phase_physical[:30]}",
                f"学业：{phase_education[:30]}"
            ]
            summary = "；".join(summary_parts)

            detail = TongYunDetail(
                age_range=age_range,
                physical=phase_physical,
                education=phase_education,
                parent_relation=phase_parent,
                precautions=phase_precautions,
                key_points=key_points,
                summary=summary
            )

            results.append(detail)

        # 如果没有任何大运数据，生成一个从0-12的默认解读
        if not results:
            results.append(TongYunDetail(
                age_range="0-12岁（综合）",
                physical=body_strength,
                education=education_nature,
                parent_relation=parent_relation,
                precautions=general_precautions,
                key_points="综合各阶段分析",
                summary=f"童运综合：{body_strength[:20]}；{education_nature[:20]}"
            ))

        return results

    def _analyze_physical_constitution(self, chart: Dict) -> str:
        """分析幼年体质强弱"""
        day_master = chart.get("day_master", "")
        day_master_wx = chart.get("day_master_wuxing", "")
        month_branch = chart.get("month_pillar", {}).get("branch", "")

        # 月令生助日主则体质好
        month_wx = self.WUXING_MAP.get(month_branch, "")

        sheng_relation = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}

        if month_wx == day_master_wx:
            return f"日主{day_master}（{day_master_wx}）得月令{month_branch}（{month_wx}）之助，幼年体质较佳，少生病。"
        elif sheng_relation.get(month_wx) == day_master_wx:
            return f"月令{month_branch}（{month_wx}）生日主{day_master}（{day_master_wx}），体质中等偏上，注意季节交替时防病。"
        elif sheng_relation.get(day_master_wx) == month_wx:
            return f"日主{day_master}（{day_master_wx}）生月令{month_branch}（{month_wx}），体质偏弱，需注意日常养护。"
        else:
            return f"日主{day_master}（{day_master_wx}）与月令{month_branch}（{month_wx}）相克，体质较弱，需加强营养。"
    
    def _find_wenchang(self, chart: Dict) -> List[str]:
        """查找文昌位置"""
        day_master = chart.get("day_master", "")

        wenchang_rules = {
            "甲": "巳", "乙": "午", "丙": "申", "丁": "酉",
            "戊": "申", "己": "酉", "庚": "亥", "辛": "子",
            "壬": "寅", "癸": "卯"
        }

        target_branch = wenchang_rules.get(day_master, "")

        positions = []
        pillars = {
            "年柱": chart.get("year_pillar", {}),
            "月柱": chart.get("month_pillar", {}),
            "日柱": chart.get("day_pillar", {}),
            "时柱": chart.get("hour_pillar", {})
        }

        for pos_name, pillar in pillars.items():
            if pillar.get("branch", "") == target_branch:
                positions.append(pos_name)

        return positions if positions else ["未发现文昌"]

    def _analyze_education_nature(self, chart: Dict) -> str:
        """分析学业天赋"""
        day_master = chart.get("day_master", "")

        # 检查文昌
        wc = self._find_wenchang(chart)
        wc_desc = ""
        if "未发现" not in str(wc):
            wc_desc = f"文昌在{','.join(wc)}，主聪明好学"

        # 检查十神（使用本地映射避免依赖）
        _SHISHEN_MAP = {
            "甲": {"甲": "比肩", "乙": "劫财", "丙": "食神", "丁": "伤官", "戊": "偏财", "己": "正财", "庚": "七杀", "辛": "正官", "壬": "偏印", "癸": "正印"},
            "乙": {"甲": "劫财", "乙": "比肩", "丙": "伤官", "丁": "食神", "戊": "正财", "己": "偏财", "庚": "正官", "辛": "七杀", "壬": "正印", "癸": "偏印"},
            "丙": {"甲": "偏印", "乙": "正印", "丙": "比肩", "丁": "劫财", "戊": "食神", "己": "伤官", "庚": "偏财", "辛": "正财", "壬": "七杀", "癸": "正官"},
            "丁": {"甲": "正印", "乙": "偏印", "丙": "劫财", "丁": "比肩", "戊": "伤官", "己": "食神", "庚": "正财", "辛": "偏财", "壬": "正官", "癸": "七杀"},
            "戊": {"甲": "七杀", "乙": "正官", "丙": "偏印", "丁": "正印", "戊": "比肩", "己": "劫财", "庚": "食神", "辛": "伤官", "壬": "偏财", "癸": "正财"},
            "己": {"甲": "正官", "乙": "七杀", "丙": "正印", "丁": "偏印", "戊": "劫财", "己": "比肩", "庚": "伤官", "辛": "食神", "壬": "正财", "癸": "偏财"},
            "庚": {"甲": "偏财", "乙": "正财", "丙": "七杀", "丁": "正官", "戊": "偏印", "己": "正印", "庚": "比肩", "辛": "劫财", "壬": "食神", "癸": "伤官"},
            "辛": {"甲": "正财", "乙": "偏财", "丙": "正官", "丁": "七杀", "戊": "正印", "己": "偏印", "庚": "劫财", "辛": "比肩", "壬": "伤官", "癸": "食神"},
            "壬": {"甲": "食神", "乙": "伤官", "丙": "偏财", "丁": "正财", "戊": "七杀", "己": "正官", "庚": "偏印", "辛": "正印", "壬": "比肩", "癸": "劫财"},
            "癸": {"甲": "伤官", "乙": "食神", "丙": "正财", "丁": "偏财", "戊": "正官", "己": "七杀", "庚": "正印", "辛": "偏印", "壬": "劫财", "癸": "比肩"}
        }
        pillars = {
            "年柱": chart.get("year_pillar", {}),
            "月柱": chart.get("month_pillar", {}),
            "日柱": chart.get("day_pillar", {}),
            "时柱": chart.get("hour_pillar", {})
        }

        shishen_analysis = []
        for pos_name, pillar in pillars.items():
            stem = pillar.get("stem", "")
            shishen = _SHISHEN_MAP.get(day_master, {}).get(stem, "")
            if shishen in ["正印", "偏印"]:
                shishen_analysis.append(f"{pos_name}有{shishen}，学术型人才")
            elif shishen in ["食神", "伤官"]:
                shishen_analysis.append(f"{pos_name}有{shishen}，创造型人才")

        result_parts = []
        if wc_desc:
            result_parts.append(wc_desc)
        if shishen_analysis:
            result_parts.extend(shishen_analysis[:2])
        if not result_parts:
            result_parts.append(f"日主{day_master}，学业运势中等，后天的努力更重要")

        return "。".join(result_parts)

    def _analyze_parent_relation(self, chart: Dict) -> str:
        """分析父母缘份"""
        year_pillar = chart.get("year_pillar", {})
        year_stem = year_pillar.get("stem", "")
        year_branch = year_pillar.get("branch", "")
        month_pillar = chart.get("month_pillar", {})
        month_stem = month_pillar.get("stem", "")
        month_branch = month_pillar.get("branch", "")

        parts = []

        # 年柱分析
        if year_stem and year_branch:
            parts.append(f"年柱{year_stem}{year_branch}为祖上根基")

        # 年柱是否被冲
        eq_branches = {"子": "午", "丑": "未", "寅": "申", "卯": "酉", "辰": "戌", "巳": "亥",
                        "午": "子", "未": "丑", "申": "寅", "酉": "卯", "戌": "辰", "亥": "巳"}
        if eq_branches.get(year_branch) == chart.get("month_pillar", {}).get("branch", ""):
            parts.append("年柱被冲，可能早年离家或与父母聚少离多")

        # 月柱为财官
        _SS_MAP = {
            "甲": {"甲": "比肩", "乙": "劫财", "丙": "食神", "丁": "伤官", "戊": "偏财", "己": "正财", "庚": "七杀", "辛": "正官", "壬": "偏印", "癸": "正印"},
            "乙": {"甲": "劫财", "乙": "比肩", "丙": "伤官", "丁": "食神", "戊": "正财", "己": "偏财", "庚": "正官", "辛": "七杀", "壬": "正印", "癸": "偏印"},
            "丙": {"甲": "偏印", "乙": "正印", "丙": "比肩", "丁": "劫财", "戊": "食神", "己": "伤官", "庚": "偏财", "辛": "正财", "壬": "七杀", "癸": "正官"},
            "丁": {"甲": "正印", "乙": "偏印", "丙": "劫财", "丁": "比肩", "戊": "伤官", "己": "食神", "庚": "正财", "辛": "偏财", "壬": "正官", "癸": "七杀"},
            "戊": {"甲": "七杀", "乙": "正官", "丙": "偏印", "丁": "正印", "戊": "比肩", "己": "劫财", "庚": "食神", "辛": "伤官", "壬": "偏财", "癸": "正财"},
            "己": {"甲": "正官", "乙": "七杀", "丙": "正印", "丁": "偏印", "戊": "劫财", "己": "比肩", "庚": "伤官", "辛": "食神", "壬": "正财", "癸": "偏财"},
            "庚": {"甲": "偏财", "乙": "正财", "丙": "七杀", "丁": "正官", "戊": "偏印", "己": "正印", "庚": "比肩", "辛": "劫财", "壬": "食神", "癸": "伤官"},
            "辛": {"甲": "正财", "乙": "偏财", "丙": "正官", "丁": "七杀", "戊": "正印", "己": "偏印", "庚": "劫财", "辛": "比肩", "壬": "伤官", "癸": "食神"},
            "壬": {"甲": "食神", "乙": "伤官", "丙": "偏财", "丁": "正财", "戊": "七杀", "己": "正官", "庚": "偏印", "辛": "正印", "壬": "比肩", "癸": "劫财"},
            "癸": {"甲": "伤官", "乙": "食神", "丙": "正财", "丁": "偏财", "戊": "正官", "己": "七杀", "庚": "正印", "辛": "偏印", "壬": "劫财", "癸": "比肩"}
        }
        month_shishen = _SS_MAP.get(chart.get("day_master", ""), {}).get(month_stem, "")
        if month_shishen in ["正财", "偏财", "正官"]:
            parts.append(f"月柱为{month_shishen}，父母事业有成")

        return "。".join(parts) if parts else "父母缘份一般，需多沟通。"

    def _general_precautions(self, chart: Dict) -> List[str]:
        """通用注意事项"""
        precautions = []

        day_master_wx = chart.get("day_master_wuxing", "")
        month_branch = chart.get("month_pillar", {}).get("branch", "")
        month_wx = self.WUXING_MAP.get(month_branch, "")
        hour_branch = chart.get("hour_pillar", {}).get("branch", "")
        hour_wx = self.WUXING_MAP.get(hour_branch, "")

        # 五行分析
        if day_master_wx == "木":
            precautions.append("注意呼吸系统健康，春季防过敏")
        elif day_master_wx == "火":
            precautions.append("注意心脏和眼睛健康，夏季防中暑上火")
        elif day_master_wx == "土":
            precautions.append("注意消化系统，饮食需规律")
        elif day_master_wx == "金":
            precautions.append("注意皮肤和呼吸道，秋季防干燥")
        elif day_master_wx == "水":
            precautions.append("注意肾脏和泌尿系统，冬季防寒")

        if not precautions:
            precautions.append("注意均衡营养，增强体质。")

        return precautions

    def _phase_physical(self, body_strength: str, age: int, stem: str, chart: Dict) -> str:
        """该阶段体质"""
        if age < 3:
            if "较佳" in body_strength:
                return f"婴幼儿期体质较好，注重营养均衡即可。"
            elif "偏弱" in body_strength:
                return f"婴幼儿期体质偏弱，注意保暖，定期体检。"
            else:
                return "婴幼儿期需要细心照护，注意季节变化。"
        elif age < 7:
            return f"幼儿期活泼好动，{body_strength[:20]}，注意安全防护。"
        else:
            return f"学龄期体质逐渐稳定，{body_strength[:20]}，注意用眼卫生。"

    def _phase_education(self, education_nature: str, age: int,
                          wenchang_positions: List[str], chart: Dict) -> str:
        """该阶段学业"""
        if age < 3:
            return "启蒙阶段，以感官刺激和亲子互动为主。"
        elif age < 7:
            return f"学前教育期，{education_nature[:30]}，适合培养兴趣和习惯。"
        else:
            return f"正式入学阶段，{education_nature[:40]}，学习能力开始显现。"

    def _phase_parent(self, parent_relation: str, age: int, chart: Dict) -> str:
        """该阶段父母关系"""
        if age < 3:
            return "婴幼儿期与父母关系最为亲密，需要高质量的陪伴。"
        elif age < 7:
            return "幼儿期开始探索世界，父母需要给予安全感和引导。"
        else:
            return "学龄期与父母关系逐步独立，父母需要尊重孩子的自主性。"

    def _phase_precautions(self, general: List[str], age: int,
                            stem: str, chart: Dict) -> List[str]:
        """该阶段注意事项"""
        phase_precautions = list(general)

        if age < 3:
            phase_precautions.append("注意饮食卫生，预防消化系统疾病")
            phase_precautions.append("注意睡眠规律，保证充足休息")
        elif age < 7:
            phase_precautions.append("注意安全防护，防止摔倒、烫伤等意外")
            phase_precautions.append("注意培养良好的生活习惯")
        else:
            phase_precautions.append("注意用眼卫生，保护视力")
            phase_precautions.append("注意心理健康，培养积极心态")

        return phase_precautions[:3]  # 最多3条

    def _key_points(self, age_start: int, age_end: int, chart: Dict) -> str:
        """各年龄段关键点"""
        if age_end <= 3:
            return f"{age_start}-{age_end}岁以喂养和睡眠为核心，建立良好的亲子关系"
        elif age_end <= 6:
            return f"{age_start}-{age_end}岁开始形成独立人格，性格养成关键期"
        elif age_end <= 9:
            return f"{age_start}-{age_end}岁学习能力快速提升，培养学习兴趣"
        else:
            return f"{age_start}-{age_end}岁进入青春期前期，需关注心理健康"


def test_tongyun_interpreter():
    """测试童运解读引擎"""
    interpreter = TongYunInterpreter()

    test_tongyun = [
        {"ganzhi": "乙丑", "age_start": 0, "age_end": 3},
        {"ganzhi": "丙寅", "age_start": 4, "age_end": 7},
        {"ganzhi": "丁卯", "age_start": 8, "age_end": 11},
    ]

    test_chart = {
        "year_pillar": {"stem": "甲", "branch": "子"},
        "month_pillar": {"stem": "丙", "branch": "寅"},
        "day_pillar": {"stem": "丙", "branch": "午"},
        "hour_pillar": {"stem": "戊", "branch": "戌"},
        "day_master": "丙",
        "day_master_wuxing": "火",
        "gender": "男"
    }

    results = interpreter.interpret(test_tongyun, test_chart)

    print("=== 童运深度解读测试 ===")
    for r in results:
        print(f"\n【{r.age_range}】")
        print(f"  体质：{r.physical}")
        print(f"  学业：{r.education}")
        print(f"  父母：{r.parent_relation}")
        for p in r.precautions:
            print(f"  注意：{p}")
        print(f"  关键：{r.key_points}")

    return results


if __name__ == "__main__":
    test_tongyun_interpreter()
