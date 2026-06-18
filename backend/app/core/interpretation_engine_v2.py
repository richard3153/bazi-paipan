"""
命理理论解读引擎 - 核心算法 v2
基于五本经典命理书籍的理论数字化
理论应用优先级：调候为急 > 格局为本 > 源流体系
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class BaZiChart:
    """八字命盘数据结构"""
    year_pillar: Dict
    month_pillar: Dict
    day_pillar: Dict
    hour_pillar: Dict
    day_master: str
    day_master_wuxing: str
    gender: str


@dataclass
class InterpretationResult:
    """解读结果数据结构"""
    day_master_analysis: Dict
    wuxing_analysis: Dict
    shishen_analysis: Dict
    geshi_analysis: Dict
    tiaohou_analysis: Dict
    yongshen_analysis: Dict
    fortune_analysis: Dict
    suggestions: Dict
    overall_summary: str


class InterpretationEngine:
    """
    命理解读引擎核心类
    融合五本经典命理书籍的理论
    """

    def __init__(self, knowledge_base_path: str = None):
        """初始化引擎，加载知识库"""
        if knowledge_base_path is None:
            # 从 backend/app/core/ 往上4级到项目根目录
            knowledge_base_path = Path(__file__).parent.parent.parent.parent / "knowledge_base"
        else:
            knowledge_base_path = Path(knowledge_base_path)

        self.knowledge_base_path = knowledge_base_path
        self.knowledge = self._load_knowledge_base()

        # 天干地支基础数据
        self.tian_gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.di_zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

        # 五行映射
        self.wuxing_map = {
            "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
            "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
        }

        # 地支五行
        self.dizhi_wuxing = {
            "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
            "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
            "戌": "土", "亥": "水"
        }

        # 十神映射表
        self.shishen_map = self._build_shishen_map()

        # 月令旺相休囚死
        self.month_wang_xiang = {
            "寅": {"旺": "木", "相": "火", "休": "水", "囚": "金", "死": "土"},
            "卯": {"旺": "木", "相": "火", "休": "水", "囚": "金", "死": "土"},
            "辰": {"旺": "土", "相": "金", "休": "火", "囚": "木", "死": "水"},
            "巳": {"旺": "火", "相": "土", "休": "木", "囚": "水", "死": "金"},
            "午": {"旺": "火", "相": "土", "休": "木", "囚": "水", "死": "金"},
            "未": {"旺": "土", "相": "金", "休": "火", "囚": "木", "死": "水"},
            "申": {"旺": "金", "相": "水", "休": "土", "囚": "火", "死": "木"},
            "酉": {"旺": "金", "相": "水", "休": "土", "囚": "火", "死": "木"},
            "戌": {"旺": "土", "相": "金", "休": "火", "囚": "木", "死": "水"},
            "亥": {"旺": "水", "相": "木", "休": "金", "囚": "土", "死": "火"},
            "子": {"旺": "水", "相": "木", "休": "金", "囚": "土", "死": "火"},
            "丑": {"旺": "土", "相": "金", "休": "火", "囚": "木", "死": "水"}
        }

    def _load_knowledge_base(self) -> Dict:
        """加载知识库"""
        knowledge = {}
        kb_path = self.knowledge_base_path

        # 加载十神知识库
        try:
            with open(kb_path / "ten_gods" / "ten_gods_knowledge.json", "r", encoding="utf-8") as f:
                knowledge["ten_gods"] = json.load(f)
        except Exception as e:
            print(f"加载十神知识库失败: {e}")
            knowledge["ten_gods"] = {}

        # 加载五行知识库
        try:
            with open(kb_path / "wuxing" / "wuxing_knowledge.json", "r", encoding="utf-8") as f:
                knowledge["wuxing"] = json.load(f)
        except Exception as e:
            print(f"加载五行知识库失败: {e}")
            knowledge["wuxing"] = {}

        # 加载调候知识库
        try:
            with open(kb_path / "tiaohou" / "tiaohou_knowledge.json", "r", encoding="utf-8") as f:
                knowledge["tiaohou"] = json.load(f)
        except Exception as e:
            print(f"加载调候知识库失败: {e}")
            knowledge["tiaohou"] = {}

        # 加载格局知识库
        try:
            with open(kb_path / "geshi" / "geshi_knowledge.json", "r", encoding="utf-8") as f:
                knowledge["geshi"] = json.load(f)
        except Exception as e:
            print(f"加载格局知识库失败: {e}")
            knowledge["geshi"] = {}

        # 加载用神知识库
        try:
            with open(kb_path / "yongshen" / "yongshen_knowledge.json", "r", encoding="utf-8") as f:
                knowledge["yongshen"] = json.load(f)
        except Exception as e:
            print(f"加载用神知识库失败: {e}")
            knowledge["yongshen"] = {}

        # 加载神煞知识库
        try:
            with open(kb_path / "shensha" / "shensha_knowledge.json", "r", encoding="utf-8") as f:
                knowledge["shensha"] = json.load(f)
        except Exception as e:
            print(f"加载神煞知识库失败: {e}")
            knowledge["shensha"] = {}

        return knowledge

    def _build_shishen_map(self) -> Dict:
        """构建十神映射表"""
        shishen_map = {}

        for i, gan in enumerate(self.tian_gan):
            day_master_wuxing = self.wuxing_map[gan]
            shishen_map[gan] = {}

            for j, other_gan in enumerate(self.tian_gan):
                other_wuxing = self.wuxing_map[other_gan]
                shishen = self._determine_shishen(day_master_wuxing, other_wuxing, i, j)
                shishen_map[gan][other_gan] = shishen

        return shishen_map

    def _determine_shishen(self, dm_wx: str, other_wx: str, dm_idx: int, other_idx: int) -> str:
        """判断十神关系"""
        # 五行相同
        if dm_wx == other_wx:
            dm_yin_yang = dm_idx % 2
            other_yin_yang = other_idx % 2
            if dm_yin_yang == other_yin_yang:
                return "比肩"
            else:
                return "劫财"

        # 我生者
        sheng_relation = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        if sheng_relation.get(dm_wx) == other_wx:
            dm_yin_yang = dm_idx % 2
            other_yin_yang = other_idx % 2
            if dm_yin_yang == other_yin_yang:
                return "食神"
            else:
                return "伤官"

        # 生我者
        if sheng_relation.get(other_wx) == dm_wx:
            dm_yin_yang = dm_idx % 2
            other_yin_yang = other_idx % 2
            if dm_yin_yang == other_yin_yang:
                return "偏印"
            else:
                return "正印"

        # 我克者
        ke_relation = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
        if ke_relation.get(dm_wx) == other_wx:
            dm_yin_yang = dm_idx % 2
            other_yin_yang = other_idx % 2
            if dm_yin_yang == other_yin_yang:
                return "偏财"
            else:
                return "正财"

        # 克我者
        if ke_relation.get(other_wx) == dm_wx:
            dm_yin_yang = dm_idx % 2
            other_yin_yang = other_idx % 2
            if dm_yin_yang == other_yin_yang:
                return "七杀"
            else:
                return "正官"

        return "未知"

    def interpret(self, bazi_chart: BaZiChart) -> InterpretationResult:
        """
        主解读函数
        按照理论优先级：调候 > 格局 > 扶抑
        """
        # 1. 日主分析
        day_master_analysis = self._analyze_day_master(bazi_chart)

        # 2. 五行分析
        wuxing_analysis = self._analyze_wuxing(bazi_chart)

        # 3. 十神分析
        shishen_analysis = self._analyze_shishen(bazi_chart)

        # 4. 调候分析（优先级最高）
        tiaohou_analysis = self._analyze_tiaohou(bazi_chart)

        # 5. 格局分析（优先级第二）
        geshi_analysis = self._analyze_geshi(bazi_chart)

        # 6. 用神分析（综合调候、格局、扶抑）
        yongshen_analysis = self._analyze_yongshen(bazi_chart, tiaohou_analysis, geshi_analysis, wuxing_analysis)

        # 7. 运势分析
        fortune_analysis = self._analyze_fortune(bazi_chart, yongshen_analysis)

        # 8. 改善建议
        suggestions = self._generate_suggestions(bazi_chart, yongshen_analysis)

        # 9. 综合总结
        overall_summary = self._generate_overall_summary(
            bazi_chart, day_master_analysis, wuxing_analysis,
            geshi_analysis, tiaohou_analysis, yongshen_analysis
        )

        return InterpretationResult(
            day_master_analysis=day_master_analysis,
            wuxing_analysis=wuxing_analysis,
            shishen_analysis=shishen_analysis,
            geshi_analysis=geshi_analysis,
            tiaohou_analysis=tiaohou_analysis,
            yongshen_analysis=yongshen_analysis,
            fortune_analysis=fortune_analysis,
            suggestions=suggestions,
            overall_summary=overall_summary
        )

    def _analyze_day_master(self, chart: BaZiChart) -> Dict:
        """分析日主强弱"""
        day_master = chart.day_master
        day_master_wuxing = chart.day_master_wuxing

        score = 0
        analysis_details = {
            "得令": False,
            "得地": False,
            "得势": False,
            "score": 0
        }

        # 1. 得令（月令）
        month_branch = chart.month_pillar["branch"]
        if self.month_wang_xiang[month_branch]["旺"] == day_master_wuxing:
            analysis_details["得令"] = True
            score += 3
        elif self.month_wang_xiang[month_branch]["相"] == day_master_wuxing:
            analysis_details["得令"] = True
            score += 2

        # 2. 得地（地支有根）
        pillars = [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]
        for pillar in pillars:
            branch = pillar["branch"]
            if self.dizhi_wuxing[branch] == day_master_wuxing:
                analysis_details["得地"] = True
                score += 1
            hidden_stems = self._get_hidden_stems(branch)
            if day_master in hidden_stems:
                analysis_details["得地"] = True
                score += 0.5

        # 3. 得势（天干有助）
        for pillar in pillars:
            stem = pillar["stem"]
            if stem == day_master:
                analysis_details["得势"] = True
                score += 1
            if self.wuxing_map.get(stem) == day_master_wuxing and stem != day_master:
                analysis_details["得势"] = True
                score += 0.5

        analysis_details["score"] = score

        # 判断日主强弱
        if score >= 5:
            strength = "身旺"
        elif score >= 3:
            strength = "中和偏旺"
        elif score >= 2:
            strength = "中和"
        elif score >= 1:
            strength = "中和偏弱"
        else:
            strength = "身弱"

        return {
            "day_master": day_master,
            "day_master_wuxing": day_master_wuxing,
            "strength": strength,
            "score": score,
            "details": analysis_details,
            "theory_source": "《渊海子平》日主强弱理论"
        }

    def _get_hidden_stems(self, branch: str) -> List[str]:
        """获取地支藏干"""
        hidden_stems_map = {
            "子": ["癸"],
            "丑": ["己", "癸", "辛"],
            "寅": ["甲", "丙", "戊"],
            "卯": ["乙"],
            "辰": ["戊", "乙", "癸"],
            "巳": ["丙", "庚", "戊"],
            "午": ["丁", "己"],
            "未": ["己", "丁", "乙"],
            "申": ["庚", "壬", "戊"],
            "酉": ["辛"],
            "戌": ["戊", "辛", "丁"],
            "亥": ["壬", "甲"],
        }
        return hidden_stems_map.get(branch, [])

    def _analyze_wuxing(self, chart: BaZiChart) -> Dict:
        """分析五行平衡"""
        wuxing_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}

        pillars = [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]
        for pillar in pillars:
            stem = pillar["stem"]
            wuxing = self.wuxing_map.get(stem)
            if wuxing:
                wuxing_count[wuxing] += 1

            branch = pillar["branch"]
            wuxing = self.dizhi_wuxing.get(branch)
            if wuxing:
                wuxing_count[wuxing] += 0.5

            hidden_stems = self._get_hidden_stems(branch)
            for hidden_stem in hidden_stems:
                wuxing = self.wuxing_map.get(hidden_stem)
                if wuxing:
                    wuxing_count[wuxing] += 0.3

        # 月令权重
        month_branch = chart.month_pillar["branch"]
        month_wuxing = self.dizhi_wuxing[month_branch]
        wuxing_count[month_wuxing] += 2

        # 分析五行平衡
        balance_analysis = {}
        for wx, count in wuxing_count.items():
            if count >= 4:
                balance_analysis[wx] = "过旺"
            elif count >= 3:
                balance_analysis[wx] = "偏旺"
            elif count >= 2:
                balance_analysis[wx] = "中和"
            elif count >= 1:
                balance_analysis[wx] = "偏弱"
            else:
                balance_analysis[wx] = "过弱"

        return {
            "wuxing_count": wuxing_count,
            "balance_analysis": balance_analysis,
            "month_wuxing": month_wuxing,
            "theory_source": "《三命通会》五行理论"
        }

    def _analyze_shishen(self, chart: BaZiChart) -> Dict:
        """分析十神配置"""
        day_master = chart.day_master
        pillars = [
            ("年柱", chart.year_pillar),
            ("月柱", chart.month_pillar),
            ("日柱", chart.day_pillar),
            ("时柱", chart.hour_pillar)
        ]

        shishen_analysis = {}
        for pillar_name, pillar in pillars:
            stem = pillar["stem"]
            shishen = self.shishen_map[day_master].get(stem, "未知")

            shishen_info = self.knowledge.get("ten_gods", {}).get("ten_gods", {}).get(shishen, {})

            shishen_analysis[pillar_name] = {
                "stem": stem,
                "shishen": shishen,
                "wuxing": self.wuxing_map.get(stem),
                "nature": shishen_info.get("basic", {}).get("nature", "未知"),
                "definition": shishen_info.get("basic", {}).get("definition", ""),
                "characteristics": shishen_info.get("characteristics", {}),
                "preferences": shishen_info.get("preferences", {})
            }

        return {
            "pillars_shishen": shishen_analysis,
            "theory_source": "《渊海子平》十神理论"
        }

    def _analyze_tiaohou(self, chart: BaZiChart) -> Dict:
        """分析调候（优先级最高）"""
        day_master = chart.day_master
        month_branch = chart.month_pillar["branch"]

        season = self._determine_season(month_branch)

        tiaohou_data = self.knowledge.get("tiaohou", {}).get("shi_tian_gan_tiaohou", {})
        day_master_tiaohou = tiaohou_data.get(day_master, {})
        season_tiaohou = day_master_tiaohou.get(season, {})

        if not season_tiaohou:
            return {
                "has_tiaohou": False,
                "reason": "未找到对应调候用神",
                "theory_source": "《穷通宝鉴》"
            }

        tiaohou_yongshen = season_tiaohou.get("调候用神")
        secondary = season_tiaohou.get("次用")
        principle = season_tiaohou.get("原理")
        taboo = season_tiaohou.get("忌")

        has_tiaohou_in_chart = self._check_yongshen_in_chart(chart, tiaohou_yongshen)

        return {
            "has_tiaohou": True,
            "day_master": day_master,
            "season": season,
            "tiaohou_yongshen": tiaohou_yongshen,
            "secondary_yongshen": secondary,
            "principle": principle,
            "taboo": taboo,
            "has_tiaohou_in_chart": has_tiaohou_in_chart,
            "priority": "最高",
            "theory_source": "《穷通宝鉴》调候理论"
        }

    def _determine_season(self, month_branch: str) -> str:
        """确定月令季节"""
        season_map = {
            "寅": "春月（寅卯辰）",
            "卯": "春月（寅卯辰）",
            "辰": "春月（寅卯辰）",
            "巳": "夏月（巳午未）",
            "午": "夏月（巳午未）",
            "未": "夏月（巳午未）",
            "申": "秋月（申酉戌）",
            "酉": "秋月（申酉戌）",
            "戌": "秋月（申酉戌）",
            "亥": "冬月（亥子丑）",
            "子": "冬月（亥子丑）",
            "丑": "冬月（亥子丑）"
        }
        return season_map.get(month_branch, "未知")

    def _check_yongshen_in_chart(self, chart: BaZiChart, yongshen: str) -> bool:
        """检查命局中是否有用神"""
        pillars = [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]
        for pillar in pillars:
            stem_wuxing = self.wuxing_map.get(pillar["stem"])
            if stem_wuxing and stem_wuxing in yongshen:
                return True

            branch_wuxing = self.dizhi_wuxing.get(pillar["branch"])
            if branch_wuxing and branch_wuxing in yongshen:
                return True

        return False

    def _analyze_geshi(self, chart: BaZiChart) -> Dict:
        """分析格局（优先级第二）"""
        month_stem = chart.month_pillar["stem"]
        month_branch = chart.month_pillar["branch"]

        month_hidden_stems = self._get_hidden_stems(month_branch)
        month_benqi = month_hidden_stems[0] if month_hidden_stems else None

        geshi_name = None
        geshi_type = None

        # 检查月令本气透干
        if month_benqi:
            benqi_shishen = self.shishen_map[chart.day_master].get(month_benqi)
            if benqi_shishen:
                geshi_name = self._shishen_to_geshi(benqi_shishen)
                geshi_type = "正格"

        # 如果月令本气不透，检查余气透干
        if not geshi_name:
            for hidden_stem in month_hidden_stems[1:]:
                hidden_shishen = self.shishen_map[chart.day_master].get(hidden_stem)
                if hidden_shishen:
                    geshi_name = self._shishen_to_geshi(hidden_shishen)
                    geshi_type = "正格"
                    break

        # 检查月令是否为禄或刃
        if not geshi_name:
            lu_branch = self._get_lu_branch(chart.day_master)
            ren_branch = self._get_ren_branch(chart.day_master)

            if month_branch == lu_branch:
                geshi_name = "建禄格"
                geshi_type = "变格"
            elif month_branch == ren_branch:
                geshi_name = "月刃格"
                geshi_type = "变格"

        # 检查是否为杂气格
        if not geshi_name and month_branch in ["辰", "戌", "丑", "未"]:
            geshi_name = "杂气格"
            geshi_type = "变格"

        # 如果仍未取格，使用月干取格
        if not geshi_name:
            month_stem_shishen = self.shishen_map[chart.day_master].get(month_stem)
            if month_stem_shishen:
                geshi_name = self._shishen_to_geshi(month_stem_shishen)
                geshi_type = "正格"

        if not geshi_name:
            geshi_name = "未取格"
            geshi_type = "未知"

        # 从格局知识库获取解释
        geshi_info = self.knowledge.get("geshi", {}).get("zheng_ge_eight", {}).get("八正格", {}).get(geshi_name, {})

        return {
            "geshi_name": geshi_name,
            "geshi_type": geshi_type,
            "month_stem": month_stem,
            "month_branch": month_branch,
            "description": geshi_info.get("取格条件", ""),
            "yongshen": geshi_info.get("用神", ""),
            "xiangshen": geshi_info.get("相神", []),
            "jishen": geshi_info.get("忌神", []),
            "chengge_condition": geshi_info.get("成格条件", ""),
            "poge_condition": geshi_info.get("破格条件", ""),
            "theory_source": "《子平真诠》格局理论"
        }

    def _shishen_to_geshi(self, shishen: str) -> str:
        """十神转换为格局名称"""
        mapping = {
            "正官": "正官格",
            "七杀": "七杀格",
            "正印": "正印格",
            "偏印": "偏印格",
            "正财": "正财格",
            "偏财": "偏财格",
            "食神": "食神格",
            "伤官": "伤官格",
            "比肩": "比肩格",
            "劫财": "劫财格"
        }
        return mapping.get(shishen, "未知")

    def _get_lu_branch(self, day_master: str) -> str:
        """获取日主的禄位地支"""
        lu_map = {
            "甲": "寅", "乙": "卯", "丙": "巳", "丁": "午",
            "戊": "巳", "己": "午", "庚": "申", "辛": "酉",
            "壬": "亥", "癸": "子"
        }
        return lu_map.get(day_master, "")

    def _get_ren_branch(self, day_master: str) -> str:
        """获取日主的羊刃地支"""
        ren_map = {
            "甲": "卯", "乙": "寅", "丙": "午", "丁": "巳",
            "戊": "午", "己": "巳", "庚": "酉", "辛": "申",
            "壬": "子", "癸": "亥"
        }
        return ren_map.get(day_master, "")

    def _analyze_yongshen(self, chart: BaZiChart, tiaohou_analysis: Dict,
                          geshi_analysis: Dict, wuxing_analysis: Dict) -> Dict:
        """分析用神（综合调候、格局、扶抑）"""
        yongshen_list = []
        analysis_details = {}

        # 1. 调候用神（优先级最高）
        if tiaohou_analysis.get("has_tiaohou", False):
            tiaohou_yongshen = tiaohou_analysis.get("tiaohou_yongshen")
            if tiaohou_yongshen:
                yongshen_list.append({
                    "type": "调候用神",
                    "yongshen": tiaohou_yongshen,
                    "priority": 1,
                    "source": "《穷通宝鉴》"
                })
                analysis_details["tiaohou"] = tiaohou_yongshen

        # 2. 格局用神（优先级第二）
        if geshi_analysis.get("geshi_name") not in ["未取格", "未知"]:
            geshi_yongshen = geshi_analysis.get("yongshen")
            if geshi_yongshen:
                yongshen_list.append({
                    "type": "格局用神",
                    "yongshen": geshi_yongshen,
                    "priority": 2,
                    "source": "《子平真诠》"
                })
                analysis_details["geshi"] = geshi_yongshen

        # 3. 扶抑用神（优先级第三）
        day_master_analysis = self._analyze_day_master(chart)
        strength = day_master_analysis.get("strength")

        if "旺" in strength:
            fuyi_yongshen = self._get_restraining_wuxing(chart.day_master_wuxing)
            yongshen_list.append({
                "type": "扶抑用神",
                "yongshen": fuyi_yongshen,
                "priority": 3,
                "source": "《渊海子平》",
                "reason": f"日主{strength}，宜抑之"
            })
            analysis_details["fuyi"] = fuyi_yongshen
        elif "弱" in strength:
            fuyi_yongshen = self._get_supporting_wuxing(chart.day_master_wuxing)
            yongshen_list.append({
                "type": "扶抑用神",
                "yongshen": fuyi_yongshen,
                "priority": 3,
                "source": "《渊海子平》",
                "reason": f"日主{strength}，宜扶之"
            })
            analysis_details["fuyi"] = fuyi_yongshen

        # 按优先级排序
        yongshen_list.sort(key=lambda x: x["priority"])

        return {
            "yongshen_list": yongshen_list,
            "primary_yongshen": yongshen_list[0] if yongshen_list else None,
            "analysis_details": analysis_details,
            "theory_source": "综合五本经典理论"
        }

    def _get_restraining_wuxing(self, dm_wx: str) -> List[str]:
        """获取抑日主的五行"""
        ke_relation = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}
        return [ke_relation.get(dm_wx, "")]

    def _get_supporting_wuxing(self, dm_wx: str) -> List[str]:
        """获取扶日主的五行"""
        sheng_relation = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
        return [sheng_relation.get(dm_wx, ""), dm_wx]

    def _analyze_fortune(self, chart: BaZiChart, yongshen_analysis: Dict) -> Dict:
        """分析各方面运势"""
        personality = self._analyze_personality(chart)
        career = self._analyze_career(chart)
        wealth = self._analyze_wealth(chart)
        marriage = self._analyze_marriage(chart)
        health = self._analyze_health(chart)
        education = self._analyze_education(chart)

        return {
            "personality": personality,
            "career": career,
            "wealth": wealth,
            "marriage": marriage,
            "health": health,
            "education": education,
            "theory_source": "综合五本经典理论"
        }

    def _analyze_personality(self, chart: BaZiChart) -> Dict:
        """分析性格"""
        day_master_wuxing = chart.day_master_wuxing

        wuxing_personality = {
            "木": "仁慈、有进取心、直率、有主见",
            "火": "热情、开朗、急躁、有礼貌",
            "土": "诚信、稳重、包容、固执",
            "金": "果断、刚毅、讲义气、爱面子",
            "水": "聪明、机智、善变、多情"
        }

        pillars = [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]
        shishen_personality = []

        for pillar in pillars:
            stem = pillar["stem"]
            shishen = self.shishen_map[chart.day_master].get(stem, "")
            shishen_info = self.knowledge.get("ten_gods", {}).get("ten_gods", {}).get(shishen, {})
            characteristics = shishen_info.get("characteristics", {}).get("positive", [])
            shishen_personality.extend(characteristics)

        return {
            "day_master_personality": wuxing_personality.get(day_master_wuxing, ""),
            "shishen_influence": list(set(shishen_personality)),
            "overall": f"{wuxing_personality.get(day_master_wuxing, '')}，{','.join(list(set(shishen_personality))[:3])}"
        }

    def _analyze_career(self, chart: BaZiChart) -> Dict:
        """分析事业"""
        shishen_analysis = self._analyze_shishen(chart)
        pillars_shishen = shishen_analysis.get("pillars_shishen", {})

        career_indicators = []
        for pillar_name, data in pillars_shishen.items():
            shishen = data.get("shishen")
            if shishen in ["正官", "七杀"]:
                career_indicators.append(f"{pillar_name}有{shishen}，适合管理、公职")
            elif shishen in ["正印", "偏印"]:
                career_indicators.append(f"{pillar_name}有{shishen}，适合学术、教育")
            elif shishen in ["食神", "伤官"]:
                career_indicators.append(f"{pillar_name}有{shishen}，适合艺术、创作")

        return {
            "career_indicators": career_indicators,
            "suitable_careers": self._recommend_careers(chart),
            "overall": "；".join(career_indicators) if career_indicators else "需综合分析"
        }

    def _recommend_careers(self, chart: BaZiChart) -> List[str]:
        """推荐适合的职业"""
        day_master_wuxing = chart.day_master_wuxing

        career_map = {
            "木": ["教育", "文化", "艺术", "环保", "农业"],
            "火": ["电子", "能源", "餐饮", "娱乐", "公关"],
            "土": ["房地产", "建筑", "矿业", "管理", "仓储"],
            "金": ["金融", "金属", "机械", "法律", "军警"],
            "水": ["贸易", "运输", "旅游", "水利", "服务"]
        }

        return career_map.get(day_master_wuxing, [])

    def _analyze_wealth(self, chart: BaZiChart) -> Dict:
        """分析财运"""
        shishen_analysis = self._analyze_shishen(chart)
        pillars_shishen = shishen_analysis.get("pillars_shishen", {})

        wealth_indicators = []
        for pillar_name, data in pillars_shishen.items():
            shishen = data.get("shishen")
            if shishen in ["正财", "偏财"]:
                wealth_indicators.append(f"{pillar_name}有{shishen}，财运好")
            elif shishen in ["食神", "伤官"]:
                wealth_indicators.append(f"{pillar_name}有{shishen}，生财有道")

        return {
            "wealth_indicators": wealth_indicators,
            "overall": "财运" + ("佳" if wealth_indicators else "需努力")
        }

    def _analyze_marriage(self, chart: BaZiChart) -> Dict:
        """分析婚姻"""
        gender = chart.gender
        shishen_analysis = self._analyze_shishen(chart)

        if gender == "男":
            marriage_indicator = "财星"
        else:
            marriage_indicator = "官星"

        return {
            "marriage_indicator": marriage_indicator,
            "overall": "婚姻分析需结合大运流年"
        }

    def _analyze_health(self, chart: BaZiChart) -> Dict:
        """分析健康"""
        wuxing_analysis = self._analyze_wuxing(chart)
        balance_analysis = wuxing_analysis.get("balance_analysis", {})

        health_issues = []
        for wx, balance in balance_analysis.items():
            if balance in ["过旺", "过弱"]:
                health_issues.append(f"{wx}五行{balance}，注意相关脏腑健康")

        return {
            "health_issues": health_issues,
            "overall": "健康" + ("需注意" if health_issues else "良好")
        }

    def _analyze_education(self, chart: BaZiChart) -> Dict:
        """分析学业"""
        shishen_analysis = self._analyze_shishen(chart)

        education_indicators = []
        for pillar_name, data in shishen_analysis.get("pillars_shishen", {}).items():
            shishen = data.get("shishen")
            if shishen in ["正印", "偏印"]:
                education_indicators.append(f"{pillar_name}有{shishen}，学业好")

        return {
            "education_indicators": education_indicators,
            "overall": "学业" + ("优秀" if education_indicators else "需努力")
        }

    def _generate_suggestions(self, chart: BaZiChart, yongshen_analysis: Dict) -> Dict:
        """生成改善建议"""
        primary_yongshen = yongshen_analysis.get("primary_yongshen")

        if not primary_yongshen:
            return {
                "suggestions": ["未找到明确用神，需综合分析"],
                "theory_source": "综合五本经典理论"
            }

        yongshen = primary_yongshen.get("yongshen")
        yongshen_type = primary_yongshen.get("type")

        suggestions = []

        if "木" in yongshen:
            suggestions.append("多用绿色，向东方发展，从事木相关行业")
        if "火" in yongshen:
            suggestions.append("多用红色，向南方发展，从事火相关行业")
        if "土" in yongshen:
            suggestions.append("多用黄色，向本地发展，从事土相关行业")
        if "金" in yongshen:
            suggestions.append("多用白色，向西方发展，从事金相关行业")
        if "水" in yongshen:
            suggestions.append("多用黑色，向北方发展，从事水相关行业")

        return {
            "primary_yongshen": yongshen,
            "yongshen_type": yongshen_type,
            "suggestions": suggestions,
            "theory_source": "综合五本经典理论"
        }

    def _generate_overall_summary(self, chart: BaZiChart, day_master_analysis: Dict,
                                   wuxing_analysis: Dict, geshi_analysis: Dict,
                                   tiaohou_analysis: Dict, yongshen_analysis: Dict) -> str:
        """生成综合总结"""
        day_master = chart.day_master
        day_master_wuxing = chart.day_master_wuxing
        strength = day_master_analysis.get("strength")
        geshi_name = geshi_analysis.get("geshi_name")
        primary_yongshen = yongshen_analysis.get("primary_yongshen")

        summary = f"此命造日主为{day_master}（{day_master_wuxing}），{strength}。"

        if geshi_name and geshi_name not in ["未取格", "未知"]:
            summary += f"格局为{geshi_name}。"

        if tiaohou_analysis.get("has_tiaohou"):
            tiaohou_yongshen = tiaohou_analysis.get("tiaohou_yongshen")
            summary += f"调候用神为{tiaohou_yongshen}。"

        if primary_yongshen:
            yongshen = primary_yongshen.get("yongshen")
            yongshen_type = primary_yongshen.get("type")
            summary += f"最终用神为{yongshen}（{yongshen_type}）。"

        summary += "综合来看，此命造" + self._evaluate_fortune(geshi_name, strength)

        return summary

    def _evaluate_fortune(self, geshi_name: str, strength: str) -> str:
        """评估命运层次"""
        if geshi_name in ["正官格", "正印格", "食神格"] and "旺" not in strength:
            return "命运层次较高，事业有成，人生顺遂。"
        elif geshi_name in ["七杀格", "伤官格"] and "旺" in strength:
            return "命运层次中等，需努力奋斗，方能有成。"
        else:
            return "命运层次中等，需把握机遇，努力进取。"


def test_interpretation_engine():
    """测试解读引擎"""
    test_chart = BaZiChart(
        year_pillar={"stem": "甲", "branch": "子"},
        month_pillar={"stem": "丙", "branch": "寅"},
        day_pillar={"stem": "丙", "branch": "午"},
        hour_pillar={"stem": "戊", "branch": "戌"},
        day_master="丙",
        day_master_wuxing="火",
        gender="男"
    )

    engine = InterpretationEngine()
    result = engine.interpret(test_chart)

    print("=== 命理解读结果 ===")
    print(f"\n日主分析：{result.day_master_analysis}")
    print(f"\n五行分析：{result.wuxing_analysis}")
    print(f"\n十神分析：{result.shishen_analysis}")
    print(f"\n调候分析：{result.tiaohou_analysis}")
    print(f"\n格局分析：{result.geshi_analysis}")
    print(f"\n用神分析：{result.yongshen_analysis}")
    print(f"\n运势分析：{result.fortune_analysis}")
    print(f"\n改善建议：{result.suggestions}")
    print(f"\n综合总结：{result.overall_summary}")

    return result


if __name__ == "__main__":
    test_interpretation_engine()
