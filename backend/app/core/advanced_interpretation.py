"""
高级命理解读引擎 - 统一入口
整合神煞、大运、流年、小运、童运五大深度解读模块

基于五本经典：
- 《三命通会》神煞理论
- 《渊海子平》日主强弱、用神、十神
- 《子平真诠》格局理论
- 《穷通宝鉴》调候理论
- 《滴天髓》通关、源流体系
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class AdvancedResult:
    """高级解读结果"""
    shensha_analysis: List[Dict] = field(default_factory=list)        # 神煞深度解读
    dayun_analysis: List[Dict] = field(default_factory=list)          # 大运详细解读
    current_liunian: Optional[Dict] = None                            # 当前流年解读
    xiaoyun_analysis: Optional[Dict] = None                           # 小运解读
    tongyun_analysis: List[Dict] = field(default_factory=list)        # 童运解读
    overall_fortune: Dict = field(default_factory=dict)               # 命运层次评估
    key_years: List[Dict] = field(default_factory=list)               # 一生关键年份
    suggestions: List[str] = field(default_factory=list)              # 改善建议


class AdvancedInterpretationEngine:
    """
    高级命理解读引擎 - 整合五本经典

    提供完整的八字深度解读，涵盖神煞、大运、流年、小运、童运
    每个解读结果均包含：经典引用、逻辑推导、具体影响、程度量化、实用建议
    """

    def __init__(self, knowledge_base_path: str = None):
        """初始化高级解读引擎，加载所有子模块"""
        if knowledge_base_path is None:
            kb_path = Path(__file__).parent.parent.parent.parent / "knowledge_base"
        else:
            kb_path = Path(knowledge_base_path)

        self.knowledge_base_path = kb_path
        self.knowledge = self._load_knowledge(kb_path)

        # 加载子模块
        from .shensha_interpreter import ShenShaInterpreter, calculate_shensha
        from .dayun_interpreter import DaYunInterpreter
        from .liunian_interpreter import LiuNianInterpreter
        from .xiaoyun_interpreter import XiaoYunInterpreter, calculate_xiaoyun
        from .tongyun_interpreter import TongYunInterpreter

        self.shensha_interpreter = ShenShaInterpreter(str(kb_path))
        self.dayun_interpreter = DaYunInterpreter(str(kb_path))
        self.liunian_interpreter = LiuNianInterpreter(str(kb_path))
        self.xiaoyun_interpreter = XiaoYunInterpreter(str(kb_path))
        self.tongyun_interpreter = TongYunInterpreter(str(kb_path))

        self.calculate_shensha = calculate_shensha
        self.calculate_xiaoyun = calculate_xiaoyun

        # 核心常量
        self.tian_gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.di_zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

        self.wuxing_map = {
            "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
            "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
        }

    def _load_knowledge(self, kb_path: Path) -> Dict:
        """加载所有知识库"""
        knowledge = {}
        kb_files = {
            "shensha": "shensha/shensha_knowledge.json",
            "dayun": "dayun/dayun_patterns.json",
            "liunian": "liunian/liunian_patterns.json",
            "xiaoyun": "xiaoyun/xiaoyun_knowledge.json",
            "tongyun": "tongyun/tongyun_knowledge.json"
        }

        for key, rel_path in kb_files.items():
            try:
                file_path = kb_path / rel_path
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        knowledge[key] = json.load(f)
                else:
                    knowledge[key] = {}
            except Exception as e:
                print(f"加载{key}知识库失败: {e}")
                knowledge[key] = {}

        return knowledge

    def full_interpretation(self, bazi_result: Dict) -> AdvancedResult:
        """
        完整高级解读

        Args:
            bazi_result: 八字排盘结果（包含四柱、日主、大运等信息）

        Returns:
            AdvancedResult: 完整的高级解读结果
        """
        # 提取命盘信息
        chart = self._build_chart(bazi_result)

        # 1. 神煞解读
        shensha_analysis = self._interpret_shensha(chart)

        # 2. 大运解读
        dayun_analysis = self._interpret_dayun(chart)

        # 3. 流年解读
        current_liunian = self._interpret_current_liunian(chart)

        # 4. 小运解读
        xiaoyun_analysis = self._interpret_xiaoyun(chart)

        # 5. 童运解读
        tongyun_analysis = self._interpret_tongyun(chart)

        # 6. 命运层次评估
        overall_fortune = self._evaluate_overall_fortune(chart)

        # 7. 关键年份
        key_years = self._find_key_years(chart, dayun_analysis)

        # 8. 改善建议
        suggestions = self._generate_improvement_suggestions(chart, shensha_analysis)

        return AdvancedResult(
            shensha_analysis=shensha_analysis,
            dayun_analysis=dayun_analysis,
            current_liunian=current_liunian,
            xiaoyun_analysis=xiaoyun_analysis,
            tongyun_analysis=tongyun_analysis,
            overall_fortune=overall_fortune,
            key_years=key_years,
            suggestions=suggestions
        )

    def _build_chart(self, bazi_result: Dict) -> Dict:
        """从排盘结果构建命盘信息"""
        chart = dict(bazi_result)

        # 确保包含必要字段
        if "day_master" not in chart:
            chart["day_master"] = bazi_result.get("day_pillar", {}).get("stem", "")

        if "day_master_wuxing" not in chart:
            dm = chart.get("day_master", "")
            chart["day_master_wuxing"] = self.wuxing_map.get(dm, "")

        # 提取大运列表
        dayun_list = []
        raw_dayun = bazi_result.get("dayun", [])

        if raw_dayun:
            for item in raw_dayun:
                if isinstance(item, dict):
                    dayun_list.append(item)
                elif isinstance(item, str):
                    dayun_list.append({"ganzhi": item})
        else:
            # 使用通用格式：年柱大运
            dayun_list = [
                {"ganzhi": "乙丑"}, {"ganzhi": "丙寅"}, {"ganzhi": "丁卯"},
                {"ganzhi": "戊辰"}, {"ganzhi": "己巳"}, {"ganzhi": "庚午"},
                {"ganzhi": "辛未"}, {"ganzhi": "壬申"}, {"ganzhi": "癸酉"},
                {"ganzhi": "甲戌"}
            ]

        chart["dayun"] = dayun_list
        chart["current_age"] = bazi_result.get("current_age", 0)

        # 获取当前大运（简化）
        if dayun_list:
            current_age = chart["current_age"]
            found = False
            for item in dayun_list:
                try:
                    age_s = item.get("age_start", 0)
                    age_e = item.get("age_end", 99)
                    if age_s <= current_age <= age_e:
                        chart["current_dayun"] = item
                        found = True
                        break
                except (TypeError, ValueError):
                    pass
            if not found and dayun_list:
                chart["current_dayun"] = dayun_list[0]

        return chart

    def _interpret_shensha(self, chart: Dict) -> List[Dict]:
        """神煞深度解读"""
        try:
            # 计算神煞
            shensha_list = self.calculate_shensha(
                chart.get("year_pillar", {}),
                chart.get("month_pillar", {}),
                chart.get("day_pillar", {}),
                chart.get("hour_pillar", {}),
                chart.get("day_master", "")
            )

            # 解读
            details = self.shensha_interpreter.interpret(
                shensha_list,
                {
                    "year_pillar": chart.get("year_pillar", {}),
                    "month_pillar": chart.get("month_pillar", {}),
                    "day_pillar": chart.get("day_pillar", {}),
                    "hour_pillar": chart.get("hour_pillar", {})
                },
                chart.get("day_master", "")
            )

            # 转换为字典
            return [
                {
                    "name": d.name,
                    "category": d.category,
                    "position": d.position,
                    "branch": d.branch,
                    "classic_source": d.classic_source,
                    "original_text": d.original_text,
                    "logical_derivation": d.logical_derivation,
                    "effects": d.effects,
                    "severity": d.severity,
                    "resolve": d.resolve,
                    "combined_analysis": d.combined_analysis
                }
                for d in details
            ]
        except Exception as e:
            return [{"error": f"神煞解读失败: {str(e)}"}]

    def _interpret_dayun(self, chart: Dict) -> List[Dict]:
        """大运深度解读"""
        try:
            dayun_list = chart.get("dayun", [])

            # 构建用神信息（从解析引擎获取或使用默认）
            yongshen = self._build_yongshen(chart)

            details = self.dayun_interpreter.interpret(dayun_list, chart, yongshen)

            return [
                {
                    "dayun_index": d.dayun_index,
                    "dayun_ganzhi": d.dayun_ganzhi,
                    "age_range": f"{d.age_start}-{d.age_end}",
                    "wuxing_analysis": d.wuxing_analysis,
                    "interaction": d.interaction,
                    "tiaohou": d.tiaohou,
                    "geshi_effect": d.geshi_effect,
                    "yongshen": d.yongshen,
                    "rating": d.rating,
                    "career": d.career,
                    "wealth": d.wealth,
                    "marriage": d.marriage,
                    "health": d.health,
                    "summary": d.summary
                }
                for d in details
            ]
        except Exception as e:
            return [{"error": f"大运解读失败: {str(e)}"}]

    def _interpret_current_liunian(self, chart: Dict) -> Optional[Dict]:
        """当前流年解读"""
        try:
            # 获取当前年份
            from datetime import datetime
            current_year = datetime.now().year

            # 计算流年干支
            year_cycle = (current_year - 4) % 60
            liunian_stem = self.tian_gan[year_cycle % 10]
            liunian_branch = self.di_zhi[year_cycle % 12]
            liunian_ganzhi = liunian_stem + liunian_branch

            # 当前大运
            current_dayun = chart.get("current_dayun", {})

            result = self.liunian_interpreter.interpret(
                current_year,
                liunian_ganzhi,
                current_dayun,
                chart
            )

            return {
                "year": result.year,
                "ganzhi": result.ganzhi,
                "ganzhi_analysis": result.ganzhi_analysis,
                "dayun_relationship": result.dayun_relationship,
                "chongke_analysis": result.chongke_analysis,
                "warnings": result.warnings,
                "month_fortune": result.month_fortune,
                "summary": result.summary
            }
        except Exception as e:
            return {"error": f"流年解读失败: {str(e)}"}

    def _interpret_xiaoyun(self, chart: Dict) -> Optional[Dict]:
        """小运解读"""
        try:
            current_age = chart.get("current_age", 0)
            if current_age == 0:
                return {"note": "未提供当前年龄"}

            xiaoyun_ganzhi = self.calculate_xiaoyun(current_age, chart)
            result = self.xiaoyun_interpreter.interpret(xiaoyun_ganzhi, current_age, chart)

            return {
                "xiaoyun_ganzhi": result.xiaoyun_ganzhi,
                "age": result.age,
                "direction": result.direction,
                "wuxing_effect": result.wuxing_effect,
                "dayun_micro": result.dayun_micro,
                "liunian_supplement": result.liunian_supplement,
                "specific_hints": result.specific_hints,
                "summary": result.summary
            }
        except Exception as e:
            return {"error": f"小运解读失败: {str(e)}"}

    def _interpret_tongyun(self, chart: Dict) -> List[Dict]:
        """童运解读（12岁以内）"""
        try:
            # 提取前几个大运（12岁以内）
            dayun_list = chart.get("dayun", [])
            tongyun_list = []

            for item in dayun_list:
                try:
                    age_start = item.get("age_start", 0)
                    if age_start <= 12:
                        tongyun_list.append(item)
                except (TypeError, ValueError):
                    continue

            if not tongyun_list:
                return [{"note": "无前12岁大运数据，无法进行童运解读"}]

            results = self.tongyun_interpreter.interpret(tongyun_list, chart)

            return [
                {
                    "age_range": r.age_range,
                    "physical": r.physical,
                    "education": r.education,
                    "parent_relation": r.parent_relation,
                    "precautions": r.precautions,
                    "key_points": r.key_points,
                    "summary": r.summary
                }
                for r in results
            ]
        except Exception as e:
            return [{"error": f"童运解读失败: {str(e)}"}]

    def _build_yongshen(self, chart: Dict) -> Dict:
        """构建用神信息（如果已有用神分析则直接用，否则生成）"""
        yongshen = chart.get("yongshen", {})

        if yongshen and yongshen.get("primary_yongshen"):
            return yongshen

        # 简单生成用神（基于身强身弱）
        day_master_wx = chart.get("day_master_wuxing", "")
        strength = chart.get("day_master_strength", "中和")

        sheng = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        ke = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
        sheng_relation = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}

        if "旺" in strength:
            yong = [ke.get(day_master_wx, ""), sheng.get(day_master_wx, "")]
        elif "弱" in strength:
            yong = [sheng_relation.get(day_master_wx, ""), day_master_wx]
        else:
            yong = ["水", "火"]  # 调候

        return {
            "primary_yongshen": {
                "yongshen": [y for y in yong if y],
                "type": "扶抑用神",
                "priority": 1,
                "source": "《渊海子平》"
            },
            "yongshen_list": [
                {
                    "yongshen": [y for y in yong if y],
                    "type": "扶抑用神",
                    "priority": 1,
                    "source": "《渊海子平》"
                }
            ]
        }

    def _evaluate_overall_fortune(self, chart: Dict) -> Dict:
        """综合命运层次评估"""
        day_master = chart.get("day_master", "")
        day_master_wx = chart.get("day_master_wuxing", "")
        strength = chart.get("day_master_strength", "中和")
        geshi_name = chart.get("geshi_name", "")
        gender = chart.get("gender", "男")

        # 评分
        score = 60

        # 格局加分
        good_geshi = ["正官格", "正印格", "食神格", "正财格"]
        if geshi_name in good_geshi:
            score += 10

        # 身强身弱
        if "旺" in strength and geshi_name in ["七杀格", "伤官格"]:
            score += 10  # 身旺有格
        elif "弱" in strength and geshi_name in good_geshi:
            score -= 5  # 身弱好格但需扶

        # 调候
        tiaohou_info = chart.get("tiaohou_analysis", {})
        if tiaohou_info.get("has_tiaohou") and tiaohou_info.get("has_tiaohou_in_chart"):
            score += 10

        # 神煞
        # 天乙贵人加分
        score = max(0, min(100, score))

        # 等级
        if score >= 85:
            level = "上等命局"
            desc = "命局组合上佳，格局清奇，用神得力，人生机遇多，事业有成。"
        elif score >= 70:
            level = "中上命局"
            desc = "命局组合较好，有一定格局，用神得助，通过努力可获成功。"
        elif score >= 55:
            level = "中等命局"
            desc = "命局平常，格局一般，但通过后天努力可以改善。"
        elif score >= 40:
            level = "中下命局"
            desc = "命局略弱，需大运流年配合，保守守成为宜。"
        else:
            level = "下等命局"
            desc = "命局坎坷较多，需大运流年补益，积德行善。"
            score = 50

        return {
            "score": score,
            "level": level,
            "description": desc,
            "day_master": day_master,
            "day_master_wuxing": day_master_wx,
            "strength": strength,
            "geshi": geshi_name,
            "theory_source": "综合五本经典理论"
        }

    def _find_key_years(self, chart: Dict, dayun_analysis: List[Dict]) -> List[Dict]:
        """寻找一生关键年份（转折点）"""
        key_years = []

        # 大运交接年
        for dayun in dayun_analysis:
            if isinstance(dayun, dict) and dayun.get("rating") in ["上", "下"]:
                age_range = dayun.get("age_range", "")
                if age_range:
                    try:
                        start, end = age_range.split("-")
                        key_years.append({
                            "type": "大运转折",
                            "age": int(start),
                            "dayun": dayun.get("dayun_ganzhi", ""),
                            "rating": dayun.get("rating", ""),
                            "description": f"大运交接至{dayun.get('dayun_ganzhi', '')}运，"
                                          f"综合评级{dayun.get('rating', '')}等运"
                        })
                    except ValueError:
                        pass

        # 岁运并临年（如果有流年信息）
        # 这里简化为每个大运包含的年份

        # 仅保留前5个关键年份
        return key_years[:5]

    def _generate_improvement_suggestions(self, chart: Dict,
                                           shensha_analysis: List[Dict]) -> List[str]:
        """生成改善建议"""
        suggestions = []

        day_master_wx = chart.get("day_master_wuxing", "")
        strength = chart.get("day_master_strength", "中和")
        gender = chart.get("gender", "男")

        # 五行建议
        wx_suggestions = {
            "木": "建议多参与户外运动，绿色环境有益身心",
            "火": "建议保持心态平和，避免急躁冲动",
            "土": "建议饮食有节，锻炼脾胃功能",
            "金": "建议注意呼吸健康，多做深呼吸练习",
            "水": "建议注意保暖，多做有氧运动"
        }
        if day_master_wx in wx_suggestions:
            suggestions.append(wx_suggestions[day_master_wx])

        # 身强身弱建议
        if "旺" in strength:
            suggestions.append("日主偏旺，宜多付出，少计较得失，以德服人")
        elif "弱" in strength:
            suggestions.append("日主偏弱，宜多学习充电，结交正能量朋友")

        # 神煞化解建议
        for ss in shensha_analysis:
            if isinstance(ss, dict) and ss.get("resolve"):
                suggestions.append(ss["resolve"])

        # 通用建议
        suggestions.append("多行善事，积德累功，命运可改")

        return suggestions[:6]  # 最多6条


# ============ 测试函数 ============

def test_advanced_engine():
    """测试高级解读引擎"""
    engine = AdvancedInterpretationEngine()

    # 创建测试数据
    test_result = {
        "year_pillar": {"stem": "甲", "branch": "子"},
        "month_pillar": {"stem": "丙", "branch": "寅"},
        "day_pillar": {"stem": "丙", "branch": "午"},
        "hour_pillar": {"stem": "戊", "branch": "戌"},
        "day_master": "丙",
        "day_master_wuxing": "火",
        "day_master_strength": "身旺",
        "gender": "男",
        "current_age": 35,
        "dayun": [
            {"ganzhi": "乙丑", "age_start": 6, "age_end": 15},
            {"ganzhi": "丙寅", "age_start": 16, "age_end": 25},
            {"ganzhi": "丁卯", "age_start": 26, "age_end": 35},
            {"ganzhi": "戊辰", "age_start": 36, "age_end": 45},
            {"ganzhi": "己巳", "age_start": 46, "age_end": 55},
            {"ganzhi": "庚午", "age_start": 56, "age_end": 65},
            {"ganzhi": "辛未", "age_start": 66, "age_end": 75},
            {"ganzhi": "壬申", "age_start": 76, "age_end": 85},
        ],
        "geshi_name": "正官格",
        "geshi_type": "正格"
    }

    result = engine.full_interpretation(test_result)

    print("=" * 60)
    print("高级命理解读引擎测试")
    print("=" * 60)

    print(f"\n八字：甲子 丙寅 丙午 戊戌")
    print(f"日主：丙（火）- 身旺")
    print(f"格局：正官格")

    print(f"\n【命运层次】")
    print(f"  等级：{result.overall_fortune['level']}（{result.overall_fortune['score']}分）")
    print(f"  描述：{result.overall_fortune['description']}")

    print(f"\n【神煞】（{len(result.shensha_analysis)}个）")
    for ss in result.shensha_analysis[:5]:
        if isinstance(ss, dict) and "name" in ss:
            print(f"  · {ss['name']}（{ss['category']}@{ss['position']}）程度：{'★' * ss['severity']}{'☆' * (5 - ss['severity'])}")

    print(f"\n【大运】")
    for dy in result.dayun_analysis[:4]:
        if isinstance(dy, dict):
            print(f"  · {dy.get('dayun_ganzhi', '')}运（{dy.get('age_range', '')}）：{dy.get('rating', '')}等运 — {dy.get('summary', '')[:40]}...")

    print(f"\n【流年】")
    if result.current_liunian:
        print(f"  当前：{result.current_liunian.get('ganzhi', '')}年")
        for w in result.current_liunian.get('warnings', []):
            print(f"  · {w}")

    print(f"\n【小运】")
    if result.xiaoyun_analysis:
        print(f"  · {result.xiaoyun_analysis.get('summary', '')}")

    print(f"\n【改善建议】")
    for s in result.suggestions:
        print(f"  · {s}")

    return result


if __name__ == "__main__":
    test_advanced_engine()
