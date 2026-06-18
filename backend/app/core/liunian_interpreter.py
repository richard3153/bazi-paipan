"""
流年深度解读引擎
基于《渊海子平》《三命通会》《滴天髓》等经典

对单年流年进行5个维度的深度解读：
1. 流年天干地支分析
2. 流年与大运的关系（承启）
3. 流年与原局的冲克（岁运并临、天克地冲等）
4. 该年重点事项预警
5. 月份运势分布（12个月粗略）
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class LiuNianDetail:
    """单年流年深度解读"""
    year: int                    # 公历年份
    ganzhi: str                  # 流年干支
    ganzhi_analysis: Dict        # 干支分析
    dayun_relationship: Dict     # 与大运的关系
    chongke_analysis: Dict       # 与原局的冲克
    warnings: List[str]          # 重点事项预警
    month_fortune: List[Dict]    # 月份运势
    summary: str                 # 全年总结


class LiuNianInterpreter:
    """流年深度解读引擎"""

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

    # 天干五合
    STEM_HE = {
        "甲": "己", "己": "甲", "乙": "庚", "庚": "乙",
        "丙": "辛", "辛": "丙", "丁": "壬", "壬": "丁",
        "戊": "癸", "癸": "戊"
    }

    # 十神映射
    SHISHEN_MAP_LOCAL = {
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

    def _get_shishen(self, day_master: str, target_stem: str) -> str:
        """获取十神"""
        return self.SHISHEN_MAP_LOCAL.get(day_master, {}).get(target_stem, "")

    # 天干相克
    STEM_KE = {
        "甲": "戊己", "乙": "戊己", "丙": "庚辛", "丁": "庚辛",
        "戊": "壬癸", "己": "壬癸", "庚": "甲乙", "辛": "甲乙",
        "壬": "丙丁", "癸": "丙丁"
    }

    # 月份对应地支
    MONTH_BRANCH_MAP = {
        1: "寅", 2: "卯", 3: "辰", 4: "巳", 5: "午", 6: "未",
        7: "申", 8: "酉", 9: "戌", 10: "亥", 11: "子", 12: "丑"
    }

    def __init__(self, knowledge_base_path: str = None):
        """初始化流年解读引擎"""
        if knowledge_base_path is None:
            kb_path = Path(__file__).parent.parent.parent.parent / "knowledge_base"
        else:
            kb_path = Path(knowledge_base_path)
        self.kb_path = kb_path
        self.knowledge = self._load_knowledge(kb_path)

    def _load_knowledge(self, kb_path: Path) -> Dict:
        """加载流年知识库"""
        try:
            patterns_file = kb_path / "liunian" / "liunian_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载流年知识库失败: {e}")
        return {}

    def interpret(self, year: int, liunian_ganzhi: str,
                  current_dayun: Dict, chart: Dict) -> LiuNianDetail:
        """
        单年流年深度解读

        Args:
            year: 公历年份
            liunian_ganzhi: 流年干支，如"甲子"
            current_dayun: 当前大运信息
            chart: 八字命盘

        Returns:
            LiuNianDetail: 流年详细解读
        """
        stem = liunian_ganzhi[0] if len(liunian_ganzhi) >= 2 else ""
        branch = liunian_ganzhi[1:] if len(liunian_ganzhi) >= 2 else ""

        # 1. 流年干支分析
        ganzhi_analysis = self._analyze_ganzhi(stem, branch, chart)

        # 2. 与大运的关系（承启）
        dayun_relationship = self._analyze_dayun_relation(stem, branch, current_dayun, chart)

        # 3. 与原局的冲克
        chongke_analysis = self._analyze_chongke(stem, branch, chart)

        # 4. 重点事项预警
        warnings = self._generate_warnings(ganzhi_analysis, dayun_relationship,
                                            chongke_analysis, chart)

        # 5. 月份运势
        month_fortune = self._generate_month_fortune(stem, branch, current_dayun, chart)

        # 总结
        summary = self._generate_summary(year, liunian_ganzhi, ganzhi_analysis,
                                          dayun_relationship, chongke_analysis, warnings)

        return LiuNianDetail(
            year=year,
            ganzhi=liunian_ganzhi,
            ganzhi_analysis=ganzhi_analysis,
            dayun_relationship=dayun_relationship,
            chongke_analysis=chongke_analysis,
            warnings=warnings,
            month_fortune=month_fortune,
            summary=summary
        )

    def _analyze_ganzhi(self, stem: str, branch: str, chart: Dict) -> Dict:
        """分析流年天干地支"""
        stem_wx = self.STEM_WUXING.get(stem, "")
        branch_wx = self.BRANCH_WUXING.get(branch, "")
        day_master = chart.get("day_master", "")
        day_master_wx = chart.get("day_master_wuxing", "")

        shishen_stem = self._get_shishen(day_master, stem) if day_master and stem else ""
        shishen_branch = self._get_shishen(day_master, branch[:1] if branch else "") if day_master and branch else ""

        # 纳音
        nayin = self._get_nayin(stem, branch)
        season = self._get_season(branch)

        stem_wx_desc = f"流年天干{stem}五行属{stem_wx}"
        branch_wx_desc = f"流年地支{branch}五行属{branch_wx}，季节为{season}"
        shishen_desc = f"天干十神为{shishen_stem}，地支藏干综合" if shishen_stem else ""

        # 十神解读
        shishen_meaning = self._shishen_meaning(shishen_stem)

        return {
            "stem": stem,
            "branch": branch,
            "stem_wuxing": stem_wx,
            "branch_wuxing": branch_wx,
            "nayin": nayin,
            "season": season,
            "shishen_stem": shishen_stem,
            "shishen_meaning": shishen_meaning,
            "description": f"{stem_wx_desc}；{branch_wx_desc}；{shishen_desc}"
        }

    def _get_nayin(self, stem: str, branch: str) -> str:
        """获取纳音五行"""
        # 精简纳音映射
        nayin_map = {
            "甲子": "海中金", "乙丑": "海中金", "丙寅": "炉中火", "丁卯": "炉中火",
            "戊辰": "大林木", "己巳": "大林木", "庚午": "路旁土", "辛未": "路旁土",
            "壬申": "剑锋金", "癸酉": "剑锋金", "甲戌": "山头火", "乙亥": "山头火",
            "丙子": "涧下水", "丁丑": "涧下水", "戊寅": "城头土", "己卯": "城头土",
            "庚辰": "白蜡金", "辛巳": "白蜡金", "壬午": "杨柳木", "癸未": "杨柳木",
            "甲申": "泉中水", "乙酉": "泉中水", "丙戌": "屋上土", "丁亥": "屋上土",
            "戊子": "霹雳火", "己丑": "霹雳火", "庚寅": "松柏木", "辛卯": "松柏木",
            "壬辰": "长流水", "癸巳": "长流水", "甲午": "沙中金", "乙未": "沙中金",
            "丙申": "山下火", "丁酉": "山下火", "戊戌": "平地木", "己亥": "平地木",
            "庚子": "壁上土", "辛丑": "壁上土", "壬寅": "金箔金", "癸卯": "金箔金",
            "甲辰": "覆灯火", "乙巳": "覆灯火", "丙午": "天河水", "丁未": "天河水",
            "戊申": "大驿土", "己酉": "大驿土", "庚戌": "钗钏金", "辛亥": "钗钏金",
            "壬子": "桑柘木", "癸丑": "桑柘木", "甲寅": "大溪水", "乙卯": "大溪水",
            "丙辰": "沙中土", "丁巳": "沙中土", "戊午": "天上火", "己未": "天上火",
            "庚申": "石榴木", "辛酉": "石榴木", "壬戌": "大海水", "癸亥": "大海水"
        }
        return nayin_map.get(stem + branch, "")

    def _get_season(self, branch: str) -> str:
        """根据地支获取季节"""
        season_map = {
            "寅": "春季（寅月）", "卯": "春季（卯月）", "辰": "春季（辰月）",
            "巳": "夏季（巳月）", "午": "夏季（午月）", "未": "夏季（未月）",
            "申": "秋季（申月）", "酉": "秋季（酉月）", "戌": "秋季（戌月）",
            "亥": "冬季（亥月）", "子": "冬季（子月）", "丑": "冬季（丑月）"
        }
        return season_map.get(branch, "")

    def _shishen_meaning(self, shishen: str) -> str:
        """十神流年含义"""
        meanings = {
            "正官": "正官之年，事业稳定，遵纪守法，易得贵人赏识。",
            "七杀": "七杀之年，压力与机遇并存，挑战中求发展。",
            "正印": "正印之年，学习、进修、名誉提升之年。",
            "偏印": "偏印之年，独特思维，冷门领域有收获。",
            "正财": "正财之年，正职收入增加，理财稳健。",
            "偏财": "偏财之年，偏财运好，投资、副业有收获。",
            "食神": "食神之年，福气好，享受生活，事业顺遂。",
            "伤官": "伤官之年，才华展现，但需防口舌是非。",
            "比肩": "比肩之年，朋友帮助，但也竞争激烈。",
            "劫财": "劫财之年，消费增多，需防破财。"
        }
        return meanings.get(shishen, "")

    def _analyze_dayun_relation(self, stem: str, branch: str,
                                 current_dayun: Dict, chart: Dict) -> Dict:
        """分析流年与大运的关系"""
        dayun_ganzhi = current_dayun.get("ganzhi", "")
        if not dayun_ganzhi:
            return {"no_dayun": True, "description": "缺少大运信息"}

        dy_stem = dayun_ganzhi[0] if len(dayun_ganzhi) >= 2 else ""
        dy_branch = dayun_ganzhi[1:] if len(dayun_ganzhi) >= 2 else ""

        results = {
            "year_dayun": f"流年{stem}{branch}，大运{dayun_ganzhi}",
            "patterns": [],
            "month_effects": []
        }

        # 岁运并临
        if stem == dy_stem and branch == dy_branch:
            results["patterns"].append({
                "name": "岁运并临",
                "source": "《三命通会》",
                "description": "流年与大运干支完全相同，是命运转折之年。吉则大吉，凶则大凶。",
                "severity": 5
            })

        # 天克地冲
        stem_is_ke = False
        branch_is_chong = False
        if stem and dy_stem:
            if self.STEM_KE.get(stem, "").find(dy_stem) >= 0:
                stem_is_ke = True
        if branch and dy_branch:
            if self.BRANCH_CHONG.get(branch) == dy_branch:
                branch_is_chong = True

        if stem_is_ke or branch_is_chong:
            desc_parts = []
            if stem_is_ke:
                desc_parts.append(f"天干{stem}克{dy_stem}")
            if branch_is_chong:
                desc_parts.append(f"地支{branch}冲{dy_branch}")
            results["patterns"].append({
                "name": "天克地冲" if (stem_is_ke and branch_is_chong) else "天克" if stem_is_ke else "地冲",
                "source": "《渊海子平》",
                "description": f"流年{'与'.join(desc_parts)}，变动剧烈。",
                "severity": 4
            })

        # 流年合大运
        if stem and dy_stem:
            if self.STEM_HE.get(stem) == dy_stem:
                results["patterns"].append({
                    "name": "流年与大运天干合化",
                    "source": "《三命通会》",
                    "description": f"流年天干{stem}与大运天干{dy_stem}相合，有合作、化合之事。",
                    "severity": 3
                })

        # 流年冲大运地支
        if branch and dy_branch:
            if self.BRANCH_CHONG.get(branch) == dy_branch:
                results["patterns"].append({
                    "name": "流年冲大运地支",
                    "description": f"流年地支{branch}冲大运地支{dy_branch}，此年大运能量受冲击，运势多变。",
                    "severity": 4
                })

        # 描述总结
        if not results["patterns"]:
            results["description"] = "流年与大运无特殊冲合关系，运势延续大运主线。"
        else:
            pattern_names = [p["name"] for p in results["patterns"]]
            results["description"] = "流年与大运形成：" + "、".join(pattern_names)

        return results

    def _analyze_chongke(self, stem: str, branch: str, chart: Dict) -> Dict:
        """分析流年与原局的冲克"""
        results = {
            "chong": [],
            "ke": [],
            "he": [],
            "summary": ""
        }

        pillars = {
            "年柱": chart.get("year_pillar", {}),
            "月柱": chart.get("month_pillar", {}),
            "日柱": chart.get("day_pillar", {}),
            "时柱": chart.get("hour_pillar", {})
        }

        # 检查地支相冲
        for pos_name, pillar in pillars.items():
            p_branch = pillar.get("branch", "")
            if p_branch and self.BRANCH_CHONG.get(branch) == p_branch:
                results["chong"].append({
                    "position": pos_name,
                    "branch": p_branch,
                    "description": f"流年地支{branch}冲{pos_name}地支{p_branch}"
                })

        # 特殊：冲太岁（冲年柱）
        year_pillar = chart.get("year_pillar", {})
        if self.BRANCH_CHONG.get(branch) == year_pillar.get("branch", ""):
            results["chong"].append({
                "position": "年柱（太岁）",
                "branch": year_pillar.get("branch", ""),
                "description": f"流年地支{branch}冲年支（冲太岁），变动最大之年，家宅、事业、健康皆需注意",
                "is_tai_sui": True
            })

        # 检查天干相克
        for pos_name, pillar in pillars.items():
            p_stem = pillar.get("stem", "")
            if p_stem:
                if self.STEM_KE.get(stem, "").find(p_stem) >= 0:
                    results["ke"].append({
                        "position": pos_name,
                        "stem": p_stem,
                        "description": f"流年天干{stem}克{pos_name}天干{p_stem}"
                    })

        # 检查天干五合
        for pos_name, pillar in pillars.items():
            p_stem = pillar.get("stem", "")
            if p_stem and self.STEM_HE.get(stem) == p_stem:
                results["he"].append({
                    "position": pos_name,
                    "stem": p_stem,
                    "description": f"流年天干{stem}与{pos_name}天干{p_stem}相合"
                })

        # 总结
        if results["chong"]:
            chong_parts = [c["description"] for c in results["chong"]]
            results["summary"] += "地支有冲。" + "；".join(chong_parts)
        if results["ke"]:
            ke_parts = [k["description"] for k in results["ke"]]
            results["summary"] += "天干有克。" + "；".join(ke_parts)
        if results["he"]:
            he_parts = [h["description"] for h in results["he"]]
            results["summary"] += "天干有合。" + "；".join(he_parts)
        if not any([results["chong"], results["ke"], results["he"]]):
            results["summary"] = "流年与原局无严重冲克，相对平静。"

        return results

    def _generate_warnings(self, ganzhi_analysis: Dict, dayun_relation: Dict,
                           chongke: Dict, chart: Dict) -> List[str]:
        """生成重点事项预警"""
        warnings = []

        # 岁运并临预警
        for p in dayun_relation.get("patterns", []):
            if p["name"] == "岁运并临":
                warnings.append(f"【重大】{p['name']}：{p['description']}")
            elif p["name"] == "天克地冲":
                warnings.append(f"【重要】{p['name']}：{p['description']}")

        # 冲太岁预警
        for c in chongke.get("chong", []):
            if c.get("is_tai_sui"):
                warnings.append(f"【重要】冲太岁：{c['description']}")

        # 十神相关预警
        shishen = ganzhi_analysis.get("shishen_stem", "")
        if shishen == "伤官":
            warnings.append("【注意】流年逢伤官，谨防口舌是非、官非诉讼")
        elif shishen == "七杀":
            warnings.append("【注意】流年逢七杀，压力增大，注意健康和人际关系")
        elif shishen == "劫财":
            warnings.append("【注意】流年逢劫财，注意财不外露，防小人劫财")

        # 冲日柱预警
        for c in chongke.get("chong", []):
            if "日柱" in c.get("position", ""):
                warnings.append(f"【重要】流年冲日柱：{c['description']}，已婚者注意夫妻关系")

        if not warnings:
            warnings.append("【平稳】本年度无明显重大冲克，生活工作相对平稳。")

        return warnings

    def _generate_month_fortune(self, year_stem: str, year_branch: str,
                                 current_dayun: Dict, chart: Dict) -> List[Dict]:
        """生成月份运势分布"""
        month_fortune = []

        for month_num in range(1, 13):
            month_branch = self.MONTH_BRANCH_MAP[month_num]

            # 月柱天干（五虎遁）
            from app.core.constants import MONTH_STEM_START
            year_pillar_stem = chart.get("year_pillar", {}).get("stem", "")
            month_start_stem = MONTH_STEM_START.get(year_pillar_stem, "甲")
            stem_idx = self.HEAVENLY_STEMS.index(month_start_stem)
            month_stem = self.HEAVENLY_STEMS[(stem_idx + month_num - 1) % 10]

            # 月份五行
            month_wx = self.BRANCH_WUXING.get(month_branch, "")
            year_wx = self.STEM_WUXING.get(year_stem, "")

            # 月份评分（简化）
            score = 50

            # 月令生流年天干 - 加分
            if self._is_sheng(month_wx, year_wx):
                score += 10
            # 月令克流年天干 - 减分
            if self._is_ke(month_wx, year_wx):
                score -= 10

            if score >= 60:
                rating = "吉"
            elif score >= 40:
                rating = "平"
            else:
                rating = "凶"

            month_labels = {
                1: "正月", 2: "二月", 3: "三月", 4: "四月", 5: "五月", 6: "六月",
                7: "七月", 8: "八月", 9: "九月", 10: "十月", 11: "十一月", 12: "十二月"
            }

            month_fortune.append({
                "month": month_num,
                "label": month_labels.get(month_num, f"{month_num}月"),
                "ganzhi": month_stem + month_branch,
                "wuxing": month_wx,
                "rating": rating,
                "description": f"{month_labels.get(month_num, '')}（{month_stem}{month_branch}），"
                              f"{'运势较好' if rating == '吉' else '运势平稳' if rating == '平' else '运势欠佳'}"
            })

        return month_fortune

    def _is_sheng(self, wx1: str, wx2: str) -> bool:
        """判断wx1是否生wx2"""
        sheng = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        return sheng.get(wx1) == wx2

    def _is_ke(self, wx1: str, wx2: str) -> bool:
        """判断wx1是否克wx2"""
        ke = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
        return ke.get(wx1) == wx2

    def _get_nayin_from_map(self, ganzhi: str) -> str:
        """从纳音映射获取纳音"""
        nayin_map = {
            "甲子": "海中金", "乙丑": "海中金", "丙寅": "炉中火", "丁卯": "炉中火",
            "戊辰": "大林木", "己巳": "大林木", "庚午": "路旁土", "辛未": "路旁土",
            "壬申": "剑锋金", "癸酉": "剑锋金", "甲戌": "山头火", "乙亥": "山头火",
            "丙子": "涧下水", "丁丑": "涧下水", "戊寅": "城头土", "己卯": "城头土",
            "庚辰": "白蜡金", "辛巳": "白蜡金", "壬午": "杨柳木", "癸未": "杨柳木",
            "甲申": "泉中水", "乙酉": "泉中水", "丙戌": "屋上土", "丁亥": "屋上土",
            "戊子": "霹雳火", "己丑": "霹雳火", "庚寅": "松柏木", "辛卯": "松柏木",
            "壬辰": "长流水", "癸巳": "长流水", "甲午": "沙中金", "乙未": "沙中金",
            "丙申": "山下火", "丁酉": "山下火", "戊戌": "平地木", "己亥": "平地木",
            "庚子": "壁上土", "辛丑": "壁上土", "壬寅": "金箔金", "癸卯": "金箔金",
            "甲辰": "覆灯火", "乙巳": "覆灯火", "丙午": "天河水", "丁未": "天河水",
            "戊申": "大驿土", "己酉": "大驿土", "庚戌": "钗钏金", "辛亥": "钗钏金",
            "壬子": "桑柘木", "癸丑": "桑柘木", "甲寅": "大溪水", "乙卯": "大溪水",
            "丙辰": "沙中土", "丁巳": "沙中土", "戊午": "天上火", "己未": "天上火",
            "庚申": "石榴木", "辛酉": "石榴木", "壬戌": "大海水", "癸亥": "大海水"
        }
        return nayin_map.get(ganzhi, "")

    def _generate_summary(self, year: int, ganzhi: str, ganzhi_analysis: Dict,
                           dayun_relation: Dict, chongke: Dict, warnings: List[str]) -> str:
        """生成全年总结"""
        parts = [
            f"{year}年为{ganzhi}年"
        ]

        # 纳音
        nayin = ganzhi_analysis.get("nayin", "")
        if nayin:
            parts.append(f"纳音为{nayin}")

        # 季节
        season = ganzhi_analysis.get("season", "")
        shishen = ganzhi_analysis.get("shishen_stem", "")
        shishen_desc = ganzhi_analysis.get("shishen_meaning", "")
        if shishen:
            parts.append(f"年度基调：{shishen_desc}")

        # 与大运关系
        dy_desc = dayun_relation.get("description", "")
        if dy_desc:
            parts.append(dy_desc)

        # 冲克
        ck_summary = chongke.get("summary", "")
        if ck_summary:
            parts.append(ck_summary)

        # 总评
        patterns = dayun_relation.get("patterns", [])
        if any(p.get("severity", 0) >= 4 for p in patterns):
            parts.append("总体而言，此年变动较大，宜顺势而为，把握机遇。")
        elif warnings and "平稳" in str(warnings):
            parts.append("总体而言，此年相对平稳，宜稳中求进。")
        else:
            parts.append("总体而言，此年运势中庸，注意上述重点事项即可。")

        return "。".join(parts)


def test_liunian_interpreter():
    """测试流年解读引擎"""
    interpreter = LiuNianInterpreter()

    test_year = 2024
    test_ganzhi = "甲辰"
    test_dayun = {"ganzhi": "戊辰", "age_start": 36, "age_end": 45}
    test_chart = {
        "year_pillar": {"stem": "甲", "branch": "子"},
        "month_pillar": {"stem": "丙", "branch": "寅"},
        "day_pillar": {"stem": "丙", "branch": "午"},
        "hour_pillar": {"stem": "戊", "branch": "戌"},
        "day_master": "丙",
        "day_master_wuxing": "火"
    }

    result = interpreter.interpret(test_year, test_ganzhi, test_dayun, test_chart)

    print("=== 流年深度解读测试 ===")
    print(f"年份：{result.year}年（{result.ganzhi}）")
    print(f"\n干支分析：")
    print(f"  天干：{result.ganzhi_analysis['stem']}（{result.ganzhi_analysis['stem_wuxing']}）")
    print(f"  地支：{result.ganzhi_analysis['branch']}（{result.ganzhi_analysis['branch_wuxing']}）")
    print(f"  纳音：{result.ganzhi_analysis['nayin']}")
    print(f"  十神：{result.ganzhi_analysis['shishen_stem']}——{result.ganzhi_analysis['shishen_meaning']}")

    print(f"\n与大运关系：{result.dayun_relationship.get('description', '')}")
    for p in result.dayun_relationship.get("patterns", []):
        print(f"  · {p['name']}：{p['description'][:40]}...")

    print(f"\n与原局冲克：{result.chongke_analysis.get('summary', '')[:60]}")

    print(f"\n重点预警：")
    for w in result.warnings:
        print(f"  · {w}")

    print(f"\n月份运势（前6个月）：")
    for m in result.month_fortune[:6]:
        print(f"  {m['label']}（{m['ganzhi']}）：{m['rating']}——{m['description']}")

    print(f"\n全年总结：{result.summary[:80]}...")

    return result


if __name__ == "__main__":
    test_liunian_interpreter()
