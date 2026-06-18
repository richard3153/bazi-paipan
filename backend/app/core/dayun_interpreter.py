"""
大运深度解读引擎
基于《渊海子平》《子平真诠》《穷通宝鉴》《滴天髓》等经典

对每步大运进行10个维度的深度解读：
1. 五行属性与日主关系
2. 大运与原局作用（合化、冲刑、害）
3. 调候得失（《穷通宝鉴》）
4. 格局成败影响（《子平真诠》）
5. 用神得失（《渊海子平》）
6. 总体运势评级（上/中/下）
7. 事业运势详解
8. 财运走势
9. 婚姻感情
10. 健康注意
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class DaYunDetail:
    """单步大运的深度解读"""
    dayun_index: int           # 大运序号（0起）
    dayun_ganzhi: str          # 大运干支
    age_start: int             # 起始年龄
    age_end: int               # 结束年龄
    wuxing_analysis: Dict      # 五行属性与日主关系
    interaction: Dict           # 与原局的合冲刑害
    tiaohou: Dict               # 调候得失
    geshi_effect: Dict          # 格局成败影响
    yongshen: Dict              # 用神得失
    rating: str                 # 综合评价：上/中/下
    career: str                 # 事业运势
    wealth: str                 # 财运走势
    marriage: str               # 婚姻感情
    health: str                 # 健康注意
    summary: str                # 总结


class DaYunInterpreter:
    """大运深度解读引擎"""

    # 天干地支与五行
    HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    STEM_WUXING = {
        "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
        "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
    }
    BRANCH_WUXING = {
        "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
        "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
        "戌": "土", "亥": "水"
    }

    # 地支相冲
    BRANCH_CHONG = {
        "子": "午", "丑": "未", "寅": "申", "卯": "酉", "辰": "戌", "巳": "亥",
        "午": "子", "未": "丑", "申": "寅", "酉": "卯", "戌": "辰", "亥": "巳"
    }

    # 地支六合
    BRANCH_HE = {
        "子": "丑", "丑": "子", "寅": "亥", "亥": "寅",
        "卯": "戌", "戌": "卯", "辰": "酉", "酉": "辰",
        "巳": "申", "申": "巳", "午": "未", "未": "午"
    }

    # 地支三合
    BRANCH_SANHE = {
        "申": ("申子辰", "水"), "子": ("申子辰", "水"), "辰": ("申子辰", "水"),
        "亥": ("亥卯未", "木"), "卯": ("亥卯未", "木"), "未": ("亥卯未", "木"),
        "寅": ("寅午戌", "火"), "午": ("寅午戌", "火"), "戌": ("寅午戌", "火"),
        "巳": ("巳酉丑", "金"), "酉": ("巳酉丑", "金"), "丑": ("巳酉丑", "金")
    }

    # 地支相刑
    BRANCH_XING = {
        "寅": ["巳"], "巳": ["申"], "申": ["寅"],
        "丑": ["戌"], "戌": ["未"], "未": ["丑"],
        "子": ["卯"], "卯": ["子"],
        "辰": ["辰"], "午": ["午"], "酉": ["酉"], "亥": ["亥"]
    }

    # 地支相害
    BRANCH_HAI = {
        "子": "未", "丑": "午", "寅": "巳", "卯": "辰",
        "辰": "卯", "巳": "寅", "午": "丑", "未": "子",
        "申": "亥", "酉": "戌", "戌": "酉", "亥": "申"
    }

    # 十神本地映射（减少外部依赖）
    SHISHEN_LOCAL = {
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

    def _get_shishen_local(self, day_master: str, target_stem: str) -> str:
        """获取十神关系"""
        return self.SHISHEN_LOCAL.get(day_master, {}).get(target_stem, "")

    # 天干五合
    STEM_HE = {
        "甲": "己", "己": "甲",
        "乙": "庚", "庚": "乙",
        "丙": "辛", "辛": "丙",
        "丁": "壬", "壬": "丁",
        "戊": "癸", "癸": "戊"
    }

    # 天干相克
    STEM_KE = {
        "甲": "戊己", "乙": "戊己", "丙": "庚辛", "丁": "庚辛",
        "戊": "壬癸", "己": "壬癸", "庚": "甲乙", "辛": "甲乙",
        "壬": "丙丁", "癸": "丙丁"
    }

    def __init__(self, knowledge_base_path: str = None):
        """初始化大运解读引擎"""
        if knowledge_base_path is None:
            kb_path = Path(__file__).parent.parent.parent.parent / "knowledge_base"
        else:
            kb_path = Path(knowledge_base_path)
        self.kb_path = kb_path
        self.knowledge = self._load_knowledge(kb_path)

    def _load_knowledge(self, kb_path: Path) -> Dict:
        """加载知识库"""
        try:
            patterns_file = kb_path / "dayun" / "dayun_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载大运知识库失败: {e}")
        return {}

    def interpret(self, dayun_list: List[Dict], chart: Dict,
                  yongshen: Dict = None) -> List[DaYunDetail]:
        """
        对每步大运进行10个维度的深度解读

        Args:
            dayun_list: 大运列表，每项 {ganzhi, age_start, age_end, ...}
            chart: 八字命盘完整信息
            yongshen: 用神分析结果

        Returns:
            List[DaYunDetail]: 每步大运的详细解读
        """
        results = []
        wuxing_balance = chart.get("wuxing_balance", {})

        for i, dayun in enumerate(dayun_list):
            ganzhi = dayun.get("ganzhi", "")
            age_start = dayun.get("age_start", 0)
            age_end = dayun.get("age_end", 0)

            # 1. 五行属性与日主关系
            wuxing_analysis = self._analyze_wuxing_relation(ganzhi, chart)

            # 2. 与原局的合冲刑害
            interaction = self._analyze_interaction(ganzhi, chart)

            # 3. 调候得失
            tiaohou = self._analyze_tiaohou(ganzhi, chart)

            # 4. 格局成败
            geshi_effect = self._analyze_geshi_effect(ganzhi, chart)

            # 5. 用神得失
            yongshen_detail = self._analyze_yongshen(ganzhi, yongshen, chart)

            # 6-10. 综合运势
            rating, career, wealth, marriage, health = self._analyze_comprehensive(
                wuxing_analysis, interaction, tiaohou, geshi_effect, yongshen_detail,
                ganzhi, chart
            )

            summary = self._generate_summary(i, ganzhi, age_start, age_end, rating,
                                              wuxing_analysis, yongshen_detail)

            detail = DaYunDetail(
                dayun_index=i,
                dayun_ganzhi=ganzhi,
                age_start=age_start,
                age_end=age_end,
                wuxing_analysis=wuxing_analysis,
                interaction=interaction,
                tiaohou=tiaohou,
                geshi_effect=geshi_effect,
                yongshen=yongshen_detail,
                rating=rating,
                career=career,
                wealth=wealth,
                marriage=marriage,
                health=health,
                summary=summary
            )

            results.append(detail)

        return results

    def _get_stem_branch(self, ganzhi: str) -> Tuple[str, str]:
        """从干支获取天干和地支"""
        if len(ganzhi) >= 2:
            return ganzhi[0], ganzhi[1:]
        return "", ""

    def _analyze_wuxing_relation(self, dayun_ganzhi: str, chart: Dict) -> Dict:
        """分析大运五行与日主的关系"""
        day_master = chart.get("day_master", "")
        day_master_wuxing = chart.get("day_master_wuxing", "")

        stem, branch = self._get_stem_branch(dayun_ganzhi)
        stem_wx = self.STEM_WUXING.get(stem, "")
        branch_wx = self.BRANCH_WUXING.get(branch, "")

        # 整体五行
        gan_wx = stem_wx
        zhi_wx = branch_wx

        # 关系判断
        relations = []
        for wx, source in [(gan_wx, "天干"), (zhi_wx, "地支")]:
            if wx == day_master_wuxing:
                relations.append(f"大运{source}{wx}与日主{day_master}五行相同，为比劫运")
            elif self._is_sheng(wx, day_master_wuxing):
                relations.append(f"大运{source}{wx}生日主{day_master_wuxing}（{day_master}），为印星运，得贵人助")
            elif self._is_sheng(day_master_wuxing, wx):
                relations.append(f"日主{day_master}生大运{source}{wx}（{day_master_wuxing}生{wx}），为食伤运，才华展现")
            elif self._is_ke(wx, day_master_wuxing):
                relations.append(f"大运{source}{wx}克日主{day_master_wuxing}（{day_master}），为官杀运，压力与机遇并存")
            elif self._is_ke(day_master_wuxing, wx):
                relations.append(f"日主{day_master}克大运{source}{wx}（{day_master_wuxing}克{wx}），为财运")

        day_master_strength = chart.get("day_master_strength", "中和")
        strength_advice = ""
        if "旺" in day_master_strength:
            if any("印" in r for r in relations):
                strength_advice = f"但日主{day_master_strength}，再见印运则过旺，需官杀制或食伤泄"
            else:
                strength_advice = f"日主{day_master_strength}，喜克泄，此运总体配合"
        elif "弱" in day_master_strength:
            if any("官杀" in r for r in relations):
                strength_advice = f"日主{day_master_strength}，逢官杀运压力倍增，需印星化杀"
            else:
                strength_advice = f"日主{day_master_strength}，喜生扶"

        return {
            "dayun_gan": stem,
            "dayun_zhi": branch,
            "gan_wuxing": gan_wx,
            "zhi_wuxing": zhi_wx,
            "day_master": day_master,
            "day_master_wuxing": day_master_wuxing,
            "relations": relations,
            "strength_advice": strength_advice
        }

    def _is_sheng(self, wx1: str, wx2: str) -> bool:
        """判断wx1是否生wx2"""
        sheng = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        return sheng.get(wx1) == wx2

    def _is_ke(self, wx1: str, wx2: str) -> bool:
        """判断wx1是否克wx2"""
        ke = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
        return ke.get(wx1) == wx2

    def _analyze_interaction(self, dayun_ganzhi: str, chart: Dict) -> Dict:
        """分析大运与原局的合冲刑害"""
        stem, branch = self._get_stem_branch(dayun_ganzhi)

        results = {
            "he": [],
            "chong": [],
            "xing": [],
            "hai": [],
            "summary": ""
        }

        # 获取四柱
        pillars = {
            "年柱": chart.get("year_pillar", {}),
            "月柱": chart.get("month_pillar", {}),
            "日柱": chart.get("day_pillar", {}),
            "时柱": chart.get("hour_pillar", {})
        }

        # 检查天干五合
        for pos_name, pillar in pillars.items():
            p_stem = pillar.get("stem", "")
            if p_stem and self.STEM_HE.get(stem) == p_stem:
                results["he"].append(f"大运天干{stem}与{pos_name}天干{p_stem}天干五合")

        # 检查地支六冲
        for pos_name, pillar in pillars.items():
            p_branch = pillar.get("branch", "")
            if p_branch and self.BRANCH_CHONG.get(branch) == p_branch:
                results["chong"].append(f"大运地支{branch}与{pos_name}地支{p_branch}相冲")

        # 检查地支相刑
        for pos_name, pillar in pillars.items():
            p_branch = pillar.get("branch", "")
            if p_branch and p_branch in self.BRANCH_XING.get(branch, []):
                results["xing"].append(f"大运地支{branch}与{pos_name}地支{p_branch}相刑")

        # 检查地支相害
        for pos_name, pillar in pillars.items():
            p_branch = pillar.get("branch", "")
            if p_branch and self.BRANCH_HAI.get(branch) == p_branch:
                results["hai"].append(f"大运地支{branch}与{pos_name}地支{p_branch}相害")

        # 生成总结
        parts = []
        if results["he"]:
            parts.append("天干有合，有合作、合好之意")
        if results["chong"]:
            parts.append("地支有冲，主变动、激荡")
        if results["xing"]:
            parts.append("地支有刑，需防是非、争执")
        if results["hai"]:
            parts.append("地支有害，背后易有小人是非")
        if not any([results["he"], results["chong"], results["xing"], results["hai"]]):
            parts.append("大运与原局无激烈冲合，运势相对平稳")

        results["summary"] = "。".join(parts)

        return results

    def _analyze_tiaohou(self, dayun_ganzhi: str, chart: Dict) -> Dict:
        """分析大运的调候得失"""
        stem, branch = self._get_stem_branch(dayun_ganzhi)
        gan_wx = self.STEM_WUXING.get(stem, "")
        zhi_wx = self.BRANCH_WUXING.get(branch, "")

        # 命局的季节
        month_branch = chart.get("month_pillar", {}).get("branch", "")
        season_map = {"寅": "春", "卯": "春", "辰": "春",
                       "巳": "夏", "午": "夏", "未": "夏",
                       "申": "秋", "酉": "秋", "戌": "秋",
                       "亥": "冬", "子": "冬", "丑": "冬"}
        season = season_map.get(month_branch, "")

        # 调候需求
        tiaohou_needs = {
            "春": "木旺需金克或火泄，五行宜金火",
            "夏": "火旺需水调候，五行喜水",
            "秋": "金旺需火制或水泄，五行喜火水",
            "冬": "水旺需火暖局，五行喜火"
        }

        need = tiaohou_needs.get(season, "")

        # 判断大运是否符合调候
        is_good_tiaohou = False
        if season == "夏" and (gan_wx == "水" or zhi_wx == "水"):
            is_good_tiaohou = True
        elif season == "冬" and (gan_wx == "火" or zhi_wx == "火"):
            is_good_tiaohou = True
        elif season == "春" and (gan_wx == "金" or zhi_wx == "金" or gan_wx == "火" or zhi_wx == "火"):
            is_good_tiaohou = True
        elif season == "秋" and (gan_wx == "火" or zhi_wx == "火" or gan_wx == "水" or zhi_wx == "水"):
            is_good_tiaohou = True

        desc = ""
        if is_good_tiaohou:
            desc = f"符合调候需求。此运五行（{gan_wx}{zhi_wx}）有助于调节命局寒暖，为调候得力之运。"
        else:
            desc = f"与调候需求无直接呼应。该运五行（{gan_wx}{zhi_wx}），对命局寒暖无明显调节作用，运势吉凶更多取决于格局配合。"

        return {
            "season": season,
            "tiaohou_need": need,
            "is_good_tiaohou": is_good_tiaohou,
            "description": desc,
            "theory_source": "《穷通宝鉴》调候理论"
        }

    def _analyze_geshi_effect(self, dayun_ganzhi: str, chart: Dict) -> Dict:
        """分析大运对格局的影响"""
        stem, branch = self._get_stem_branch(dayun_ganzhi)

        geshi_name = chart.get("geshi_name", "")
        geshi_type = chart.get("geshi_type", "")

        # 基于格局知识库的大运影响
        geshi_effects = self.knowledge.get("geshi_effects", {})

        geshi_effect_info = {}
        if geshi_name in geshi_effects:
            geshi_effect_info = geshi_effects[geshi_name]

        # 通用格局判断
        effect_desc = f"格局为{geshi_name}"
        if geshi_effect_info:
            pref = geshi_effect_info.get("大运偏好", "")
            effect_desc += f"。{pref}"

        # 大运天干与格局的关系
        stem_wx = self.STEM_WUXING.get(stem, "")
        day_master = chart.get("day_master", "")

        # 判断大运是否破坏格局
        is_po_ge = False
        po_ge_reason = ""

        # 正官格怕见伤官
        if geshi_name == "正官格":
            for pos_name, pillar in [("月柱", chart.get("month_pillar", {})),
                                      ("日柱", chart.get("day_pillar", {}))]:
                p_stem = pillar.get("stem", "")
                if self._get_shishen_local(day_master, stem) == "伤官":
                    is_po_ge = True
                    po_ge_reason = "正官格逢伤官大运，为破格之象，需防官非、职位变动"

        # 七杀格见财星生杀
        if geshi_name == "七杀格":
            ss = self._get_shishen_local(day_master, stem)
            if ss == "正财" or ss == "偏财":
                is_po_ge = True
                po_ge_reason = "七杀格遇财星大运，财生杀旺，压力大增"

        return {
            "geshi_name": geshi_name,
            "effect": effect_desc,
            "is_po_ge": is_po_ge,
            "po_ge_reason": po_ge_reason,
            "theory_source": "《子平真诠》格局理论"
        }

    def _analyze_yongshen(self, dayun_ganzhi: str, yongshen: Dict, chart: Dict) -> Dict:
        """分析大运的用神得失"""
        stem, branch = self._get_stem_branch(dayun_ganzhi)
        stem_wx = self.STEM_WUXING.get(stem, "")
        branch_wx = self.BRANCH_WUXING.get(branch, "")

        if not yongshen:
            return {
                "has_yongshen": False,
                "analysis": "未找到明确用神，无法判断此运用神得失"
            }

        primary_yongshen = yongshen.get("primary_yongshen", {})
        yongshen_wx = primary_yongshen.get("yongshen", [])
        if isinstance(yongshen_wx, str):
            yongshen_wx = [yongshen_wx]

        # 判断大运五行是否包含用神
        dayun_wx_set = {stem_wx, branch_wx}
        match = [wx for wx in yongshen_wx if wx in dayun_wx_set]
        total_match = len(match)

        if total_match >= 2:
            status = "大吉"
            desc = f"大运与用神高度匹配（{','.join(match)}），是用神得力之运，十年好运，当大展宏图"
        elif total_match == 1:
            status = "中吉"
            desc = f"大运含有用神（{match[0]}），运势中上，宜顺势而为"
        else:
            # 检查是否为大运克用神
            for wx in yongshen_wx:
                if self._is_ke(stem_wx, wx) or self._is_ke(branch_wx, wx):
                    status = "凶"
                    desc = f"大运克制用神（{wx}），运势不利，宜守不宜攻"
                    break
                if self._is_ke(wx, stem_wx) or self._is_ke(wx, branch_wx):
                    status = "小凶"
                    desc = f"大运被用神所克，运势平平"
                    break
            else:
                status = "平"
                desc = "大运与用神无直接生克关系，运势需视具体组合而定"

        return {
            "has_yongshen": True,
            "yongshen_wx": yongshen_wx,
            "dayun_wx": list(dayun_wx_set),
            "match_count": total_match,
            "status": status,
            "analysis": desc,
            "theory_source": "《渊海子平》用神理论"
        }

    def _analyze_comprehensive(self,
                                wuxing_analysis: Dict,
                                interaction: Dict,
                                tiaohou: Dict,
                                geshi_effect: Dict,
                                yongshen_detail: Dict,
                                dayun_ganzhi: str,
                                chart: Dict) -> Tuple[str, str, str, str, str]:
        """综合分析得出评级和各方面运势"""
        # 评分系统
        score = 60  # 基础分

        # 用神得分
        ys = yongshen_detail
        if ys.get("status") == "大吉":
            score += 20
        elif ys.get("status") == "中吉":
            score += 10
        elif ys.get("status") == "凶":
            score -= 15

        # 调候得分
        if tiaohou.get("is_good_tiaohou"):
            score += 10

        # 合冲得分
        if interaction.get("he"):
            score += 5
        if interaction.get("chong"):
            score -= 8
        if interaction.get("xing"):
            score -= 5
        if interaction.get("hai"):
            score -= 3

        # 格局得分
        if geshi_effect.get("is_po_ge"):
            score -= 15

        # 日主强弱与五行关系
        wuxing_rel = wuxing_analysis
        dm_wx = wuxing_rel.get("day_master_wuxing", "")
        gan_wx = wuxing_rel.get("gan_wuxing", "")
        zhi_wx = wuxing_rel.get("zhi_wuxing", "")
        dm_strength = chart.get("day_master_strength", "中和")

        # 身弱喜生扶
        if "弱" in dm_strength:
            if self._is_sheng(gan_wx, dm_wx) or self._is_sheng(zhi_wx, dm_wx):
                score += 10

        # 身旺喜克泄
        if "旺" in dm_strength:
            if self._is_ke(gan_wx, dm_wx) or self._is_ke(zhi_wx, dm_wx):
                score += 10

        stem, branch = self._get_stem_branch(dayun_ganzhi)

        # 确定评级
        if score >= 80:
            rating = "上"
        elif score >= 60:
            rating = "中上"
        elif score >= 40:
            rating = "中"
        elif score >= 20:
            rating = "中下"
        else:
            rating = "下"

        # 事业运势
        career = self._generate_career(stem, branch, score, wuxing_analysis,
                                       interaction, chart)
        # 财运
        wealth = self._generate_wealth(stem, branch, score, wuxing_analysis,
                                       yongshen_detail, chart)
        # 婚姻
        marriage = self._generate_marriage(stem, branch, score, chart)
        # 健康
        health = self._generate_health(stem, branch, wuxing_analysis, chart)

        return rating, career, wealth, marriage, health

    def _generate_career(self, stem: str, branch: str, score: int,
                          wuxing_analysis: Dict, interaction: Dict, chart: Dict) -> str:
        """生成事业运势描述"""
        stem_wx = self.STEM_WUXING.get(stem, "")
        branch_wx = self.BRANCH_WUXING.get(branch, "")

        desc = ""

        # 基于得分
        if score >= 80:
            desc = "事业运势极佳，宜大展宏图，积极开拓。"
        elif score >= 60:
            desc = "事业运势良好，稳步前进，有望获得新机会。"
        elif score >= 40:
            desc = "事业运势平平，宜守不宜攻，稳扎稳打。"
        else:
            desc = "事业运势低迷，需谨言慎行，避免冒险。"

        # 五行影响补充
        wx = stem_wx
        career_desc = {
            "木": "木有生发之意，利于创业、开拓新领域。",
            "火": "火有光明之象，利于文化、传播、电子行业。",
            "土": "土有承载之德，利于房地产、管理、仓储。",
            "金": "金有收敛之力，利于金融、法律、精密行业。",
            "水": "水有流通之性，利于贸易、物流、服务行业。"
        }
        if wx in career_desc:
            desc += career_desc[wx]

        # 合冲影响
        if interaction.get("he"):
            desc += "天干有合，有合作之机，宜借力发展。"
        if interaction.get("chong"):
            desc += "地支逢冲，事业多变动，宜灵活应对。"

        return desc

    def _generate_wealth(self, stem: str, branch: str, score: int,
                          wuxing_analysis: Dict, yongshen_detail: Dict, chart: Dict) -> str:
        """生成财运描述"""
        stem_wx = self.STEM_WUXING.get(stem, "")
        branch_wx = self.BRANCH_WUXING.get(branch, "")

        if score >= 80:
            return f"财运旺盛，正财偏财皆有收获，大胆投资可获利。"
        elif score >= 60:
            return f"财运平稳，正财收入稳定，适合稳健理财。"
        elif score >= 40:
            return f"财运一般，不宜大额投资，以守成为主。"
        else:
            return f"财运不济，防破产破财，保守理财为佳。"

    def _generate_marriage(self, stem: str, branch: str, score: int, chart: Dict) -> str:
        """生成婚姻感情描述"""
        gender = chart.get("gender", "男")
        day_master = chart.get("day_master", "")
        stem_shishen = self._get_shishen_local(day_master, stem)
        branch_shishen = SHISHEN_MAP_C.get(day_master, {}).get(branch[:1] if branch else "", "")

        parts = []
        if gender == "男":
            if "财" in stem_shishen:
                parts.append("大运逢财星，异性缘佳")
            elif "印" in stem_shishen:
                parts.append("大运逢印星，家庭关系和睦")
        else:
            if "官" in stem_shishen:
                parts.append("大运逢官星，感情运势佳")
            elif "印" in stem_shishen:
                parts.append("大运逢印星，家庭和谐")

        if score >= 80:
            parts.append("感情生活美满")
        elif score < 40:
            parts.append("感情方面需用心经营，多沟通理解")

        return "。".join(parts) if parts else "感情运势中等，顺其自然。"

    def _generate_health(self, stem: str, branch: str,
                          wuxing_analysis: Dict, chart: Dict) -> str:
        """生成健康描述"""
        stem_wx = self.STEM_WUXING.get(stem, "")
        branch_wx = self.BRANCH_WUXING.get(branch, "")

        health_map = {
            "木": "木主肝胆、筋骨。此运注意肝胆功能、筋骨损伤。",
            "火": "火主心脏、眼睛、血压。此运注意心脑血管、血压问题。",
            "土": "土主脾胃、消化系统。此运注意肠胃功能、饮食健康。",
            "金": "金主肺、气管、皮肤。此运注意呼吸系统、皮肤过敏。",
            "水": "水主肾、泌尿系统。此运注意肾功能、腰膝酸软。"
        }

        # 大运五行过旺则对应脏腑易出问题
        parts = []
        if stem_wx in health_map:
            parts.append(health_map[stem_wx])

        # 冲刑影响
        interaction = self._analyze_interaction(stem + branch, chart)
        if interaction.get("chong"):
            parts.append("地支逢冲，注意意外伤病。")

        return "；".join(parts) if parts else "健康状况总体平稳，注意劳逸结合。"

    def _generate_summary(self, index: int, ganzhi: str, age_start: int,
                           age_end: int, rating: str, wuxing_analysis: Dict,
                           yongshen_detail: Dict) -> str:
        """生成大运总结"""
        rel = wuxing_analysis.get("relations", [])
        wuxing_desc = "；".join(rel) if rel else ""
        yongshen_status = yongshen_detail.get("status", "")
        yongshen_desc = yongshen_detail.get("analysis", "")

        summary_parts = [
            f"第{index + 1}步大运（{ganzhi}），年龄{age_start}~{age_end}岁",
            f"综合评级：{rating}等运",
        ]
        if wuxing_desc:
            summary_parts.append(wuxing_desc)
        if yongshen_desc:
            summary_parts.append(yongshen_desc)

        return "。".join(summary_parts)


def test_dayun_interpreter():
    """测试大运解读引擎"""
    interpreter = DaYunInterpreter()

    # 测试数据
    test_dayun = [
        {"ganzhi": "乙丑", "age_start": 6, "age_end": 15},
        {"ganzhi": "丙寅", "age_start": 16, "age_end": 25},
        {"ganzhi": "丁卯", "age_start": 26, "age_end": 35},
        {"ganzhi": "戊辰", "age_start": 36, "age_end": 45},
        {"ganzhi": "己巳", "age_start": 46, "age_end": 55},
        {"ganzhi": "庚午", "age_start": 56, "age_end": 65},
    ]

    test_chart = {
        "year_pillar": {"stem": "甲", "branch": "子"},
        "month_pillar": {"stem": "丙", "branch": "寅"},
        "day_pillar": {"stem": "丙", "branch": "午"},
        "hour_pillar": {"stem": "戊", "branch": "戌"},
        "day_master": "丙",
        "day_master_wuxing": "火",
        "day_master_strength": "身旺",
        "gender": "男",
        "geshi_name": "正官格",
        "geshi_type": "正格"
    }

    test_yongshen = {
        "primary_yongshen": {"yongshen": ["水", "金"], "type": "调候用神", "priority": 1, "source": "《穷通宝鉴》"},
        "yongshen_list": [
            {"yongshen": ["水", "金"], "type": "调候用神", "priority": 1, "source": "《穷通宝鉴》"},
            {"yongshen": ["土", "金"], "type": "格局用神", "priority": 2, "source": "《子平真诠》"},
        ]
    }

    results = interpreter.interpret(test_dayun, test_chart, test_yongshen)

    print("=== 大运深度解读测试 ===")
    print(f"八字：甲子 丙寅 丙午 戊戌（丙火日主，身旺）")

    for r in results:
        print(f"\n{'='*60}")
        print(f"【{r.dayun_ganzhi}运】{r.age_start}~{r.age_end}岁")
        print(f"  评  级：{r.rating}等运")
        print(f"  五行关系：{r.wuxing_analysis['relations']}")
        print(f"  用神得失：{r.yongshen['analysis']}")
        print(f"  调候状态：{r.tiaohou['description'][:40]}...")
        print(f"  合冲状态：{r.interaction['summary']}")
        print(f"  事  业：{r.career[:50]}...")
        print(f"  财  运：{r.wealth[:30]}...")
        print(f"  婚  姻：{r.marriage[:30]}...")
        print(f"  健  康：{r.health[:30]}...")
        print(f"  总  结：{r.summary[:60]}...")

    return results


if __name__ == "__main__":
    test_dayun_interpreter()
