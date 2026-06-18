"""
命理理论解读引擎 - 简化版（用于测试）
基于五本经典命理书籍
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class SimpleInterpretationEngine:
    """简化的命理解读引擎"""
    
    def __init__(self, knowledge_base_path=None):
        """初始化"""
        if knowledge_base_path is None:
            knowledge_base_path = Path("C:/Users/xuanc/.qclaw/workspace-agent-170eadb1/knowledge_base")
        self.kb_path = knowledge_base_path
        self.knowledge = self._load_knowledge()
        
        # 基础映射
        self.wuxing_map = {
            "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
            "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
        }
        
        self.dizhi_wuxing = {
            "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
            "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
            "戌": "土", "亥": "水"
        }
    
    def _load_knowledge(self):
        """加载知识库"""
        knowledge = {}
        
        # 简化：只加载关键知识库
        try:
            with open(self.kb_path / "tiaohou" / "tiaohou_knowledge.json", "r", encoding="utf-8") as f:
                knowledge["tiaohou"] = json.load(f)
        except:
            knowledge["tiaohou"] = {}
            
        try:
            with open(self.kb_path / "geshi" / "geshi_knowledge.json", "r", encoding="utf-8") as f:
                knowledge["geshi"] = json.load(f)
        except:
            knowledge["geshi"] = {}
            
        try:
            with open(self.kb_path / "ten_gods" / "ten_gods_knowledge.json", "r", encoding="utf-8") as f:
                knowledge["ten_gods"] = json.load(f)
        except:
            knowledge["ten_gods"] = {}
        
        return knowledge
    
    def interpret(self, bazi_data):
        """
        主解读函数
        bazi_data: {
            "year_pillar": {"stem": "甲", "branch": "子"},
            "month_pillar": {"stem": "丙", "branch": "寅"},
            "day_pillar": {"stem": "丙", "branch": "午"},
            "hour_pillar": {"stem": "戊", "branch": "戌"},
            "day_master": "丙",
            "gender": "男"
        }
        """
        result = {
            "day_master_analysis": self._analyze_day_master(bazi_data),
            "wuxing_analysis": self._analyze_wuxing(bazi_data),
            "shishen_analysis": self._analyze_shishen(bazi_data),
            "tiaohou_analysis": self._analyze_tiaohou(bazi_data),
            "geshi_analysis": self._analyze_geshi(bazi_data),
            "yongshen_analysis": self._analyze_yongshen(bazi_data),
            "fortune_analysis": self._analyze_fortune(bazi_data),
            "suggestions": self._generate_suggestions(bazi_data),
            "overall_summary": ""
        }
        
        # 生成综合总结
        result["overall_summary"] = self._generate_summary(bazi_data, result)
        
        return result
    
    def _analyze_day_master(self, data):
        """分析日主"""
        day_master = data["day_master"]
        day_master_wuxing = self.wuxing_map.get(day_master, "")
        
        # 简化：只判断得令
        month_branch = data["month_pillar"]["branch"]
        season = self._get_season(month_branch)
        
        # 判断得令
        wang_wuxing = self._get_wang_wuxing(season)
        de_ling = (day_master_wuxing == wang_wuxing)
        
        return {
            "day_master": day_master,
            "day_master_wuxing": day_master_wuxing,
            "de_ling": de_ling,
            "strength": "身旺" if de_ling else "身弱"
        }
    
    def _get_season(self, month_branch):
        """获取季节"""
        if month_branch in ["寅", "卯", "辰"]:
            return "春"
        elif month_branch in ["巳", "午", "未"]:
            return "夏"
        elif month_branch in ["申", "酉", "戌"]:
            return "秋"
        else:
            return "冬"
    
    def _get_wang_wuxing(self, season):
        """获取当令五行"""
        mapping = {
            "春": "木",
            "夏": "火",
            "秋": "金",
            "冬": "水"
        }
        return mapping.get(season, "土")
    
    def _analyze_wuxing(self, data):
        """分析五行"""
        count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        
        pillars = ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]
        for pillar_key in pillars:
            pillar = data[pillar_key]
            stem = pillar["stem"]
            branch = pillar["branch"]
            
            # 天干五行
            wuxing = self.wuxing_map.get(stem)
            if wuxing:
                count[wuxing] += 1
            
            # 地支五行
            wuxing = self.dizhi_wuxing.get(branch)
            if wuxing:
                count[wuxing] += 0.5
        
        return {
            "count": count,
            "analysis": self._analyze_wuxing_balance(count)
        }
    
    def _analyze_wuxing_balance(self, count):
        """分析五行平衡"""
        result = {}
        for wx, cnt in count.items():
            if cnt >= 3:
                result[wx] = "旺"
            elif cnt >= 2:
                result[wx] = "中和"
            else:
                result[wx] = "弱"
        return result
    
    def _analyze_shishen(self, data):
        """分析十神"""
        day_master = data["day_master"]
        day_master_wuxing = self.wuxing_map.get(day_master)
        
        pillars = ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]
        result = {}
        
        for pillar_key in pillars:
            pillar = data[pillar_key]
            stem = pillar["stem"]
            stem_wuxing = self.wuxing_map.get(stem)
            
            # 简化十神判断
            shishen = self._get_shishen(day_master_wuxing, stem_wuxing, day_master, stem)
            
            result[pillar_key] = {
                "stem": stem,
                "shishen": shishen
            }
        
        return result
    
    def _get_shishen(self, dm_wx, other_wx, dm, other):
        """获取十神（简化版）"""
        # 同五行
        if dm_wx == other_wx:
            return "比肩" if dm == other else "劫财"
        
        # 我生
        sheng = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        if sheng.get(dm_wx) == other_wx:
            return "食神"  # 简化：不分食神伤官
        
        # 生我
        if sheng.get(other_wx) == dm_wx:
            return "正印"  # 简化：不分正印偏印
        
        # 我克
        ke = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
        if ke.get(dm_wx) == other_wx:
            return "正财"  # 简化：不分正财偏财
        
        # 克我
        if ke.get(other_wx) == dm_wx:
            return "正官"  # 简化：不分正官七杀
        
        return "未知"
    
    def _analyze_tiaohou(self, data):
        """分析调候"""
        day_master = data["day_master"]
        month_branch = data["month_pillar"]["branch"]
        season = self._get_season(month_branch)
        
        # 从知识库查询
        try:
            tiaohou_data = self.knowledge.get("tiaohou", {}).get("shi_tian_gan_tiaohou", {})
            dm_data = tiaohou_data.get(day_master, {})
            
            # 映射季节
            season_key = None
            if season == "春":
                season_key = "春月（寅卯辰）"
            elif season == "夏":
                season_key = "夏月（巳午未）"
            elif season == "秋":
                season_key = "秋月（申酉戌）"
            elif season == "冬":
                season_key = "冬月（亥子丑）"
            
            season_data = dm_data.get(season_key, {})
            
            return {
                "day_master": day_master,
                "season": season,
                "tiaohou_yongshen": season_data.get("调候用神", ""),
                "principle": season_data.get("原理", ""),
                "has_tiaohou": True if season_data else False
            }
        except:
            return {
                "day_master": day_master,
                "season": season,
                "has_tiaohou": False
            }
    
    def _analyze_geshi(self, data):
        """分析格局"""
        month_stem = data["month_pillar"]["stem"]
        day_master = data["day_master"]
        day_master_wuxing = self.wuxing_map.get(day_master)
        
        # 简化：根据月干判断格局
        month_stem_wuxing = self.wuxing_map.get(month_stem)
        shishen = self._get_shishen(day_master_wuxing, month_stem_wuxing, day_master, month_stem)
        
        geshi_mapping = {
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
        
        geshi = geshi_mapping.get(shishen, "未取格")
        
        return {
            "geshi_name": geshi,
            "month_stem": month_stem,
            "description": f"月干{month_stem}为{shishen}，故为{geshi}"
        }
    
    def _analyze_yongshen(self, data):
        """分析用神"""
        # 简化：综合调候和扶抑
        tiaohou = self._analyze_tiaohou(data)
        day_master_analysis = self._analyze_day_master(data)
        
        yongshen_list = []
        
        # 调候用神
        if tiaohou.get("has_tiaohou"):
            yongshen_list.append({
                "type": "调候用神",
                "yongshen": tiaohou.get("tiaohou_yongshen"),
                "priority": 1
            })
        
        # 扶抑用神
        strength = day_master_analysis.get("strength")
        if strength == "身旺":
            yongshen_list.append({
                "type": "扶抑用神",
                "yongshen": "官杀、食伤、财星",
                "priority": 2,
                "reason": "日主旺，宜抑之"
            })
        elif strength == "身弱":
            yongshen_list.append({
                "type": "扶抑用神",
                "yongshen": "印绶、比劫",
                "priority": 2,
                "reason": "日主弱，宜扶之"
            })
        
        # 按优先级排序
        yongshen_list.sort(key=lambda x: x["priority"])
        
        return {
            "yongshen_list": yongshen_list,
            "primary_yongshen": yongshen_list[0] if yongshen_list else None
        }
    
    def _analyze_fortune(self, data):
        """分析运势"""
        return {
            "personality": self._analyze_personality(data),
            "career": self._analyze_career(data),
            "wealth": self._analyze_wealth(data),
            "marriage": self._analyze_marriage(data),
            "health": self._analyze_health(data)
        }
    
    def _analyze_personality(self, data):
        """分析性格"""
        day_master_wuxing = self.wuxing_map.get(data["day_master"])
        
        personality_map = {
            "木": "仁慈、有进取心、直率",
            "火": "热情、开朗、急躁",
            "土": "诚信、稳重、包容",
            "金": "果断、刚毅、讲义气",
            "水": "聪明、机智、善变"
        }
        
        return {
            "day_master_personality": personality_map.get(day_master_wuxing, ""),
            "overall": personality_map.get(day_master_wuxing, "")
        }
    
    def _analyze_career(self, data):
        """分析事业"""
        shishen_analysis = self._analyze_shishen(data)
        
        career_indicators = []
        for pillar_key, info in shishen_analysis.items():
            shishen = info["shishen"]
            if shishen in ["正官", "七杀"]:
                career_indicators.append(f"{pillar_key}有{shishen}")
        
        return {
            "career_indicators": career_indicators,
            "overall": "适合管理公职" if career_indicators else "需综合分析"
        }
    
    def _analyze_wealth(self, data):
        """分析财运"""
        shishen_analysis = self._analyze_shishen(data)
        
        wealth_indicators = []
        for pillar_key, info in shishen_analysis.items():
            shishen = info["shishen"]
            if shishen in ["正财", "偏财"]:
                wealth_indicators.append(f"{pillar_key}有{shishen}")
        
        return {
            "wealth_indicators": wealth_indicators,
            "overall": "财运好" if wealth_indicators else "财运一般"
        }
    
    def _analyze_marriage(self, data):
        """分析婚姻"""
        gender = data.get("gender", "男")
        
        if gender == "男":
            return {"marriage_indicator": "财星", "overall": "男命看财星"}
        else:
            return {"marriage_indicator": "官星", "overall": "女命看官星"}
    
    def _analyze_health(self, data):
        """分析健康"""
        wuxing_analysis = self._analyze_wuxing(data)
        balance = wuxing_analysis.get("analysis", {})
        
        health_issues = []
        for wx, status in balance.items():
            if status == "旺":
                health_issues.append(f"{wx}过旺")
        
        return {
            "health_issues": health_issues,
            "overall": "健康需注意" if health_issues else "健康良好"
        }
    
    def _generate_suggestions(self, data):
        """生成改善建议"""
        yongshen_analysis = self._analyze_yongshen(data)
        primary = yongshen_analysis.get("primary_yongshen")
        
        if not primary:
            return {"suggestions": ["未找到明确用神"]}
        
        yongshen = primary.get("yongshen", "")
        suggestions = []
        
        if "木" in yongshen:
            suggestions.append("多用绿色，向东方发展")
        if "火" in yongshen:
            suggestions.append("多用红色，向南方发展")
        if "土" in yongshen:
            suggestions.append("多用黄色，向本地发展")
        if "金" in yongshen:
            suggestions.append("多用白色，向西方发展")
        if "水" in yongshen:
            suggestions.append("多用黑色，向北方发展")
        
        return {
            "primary_yongshen": yongshen,
            "suggestions": suggestions
        }
    
    def _generate_summary(self, data, result):
        """生成综合总结"""
        day_master = data["day_master"]
        day_master_wuxing = self.wuxing_map.get(day_master)
        strength = result["day_master_analysis"]["strength"]
        geshi = result["geshi_analysis"]["geshi_name"]
        tiaohou = result["tiaohou_analysis"].get("tiaohou_yongshen", "")
        
        summary = f"此命造日主为{day_master}（{day_master_wuxing}），{strength}。"
        summary += f"格局为{geshi}。"
        
        if tiaohou:
            summary += f"调候用神为{tiaohou}。"
        
        summary += "综合来看，此命造需结合大运流年进一步分析。"
        
        return summary


def test_engine():
    """测试引擎"""
    engine = SimpleInterpretationEngine()
    
    # 测试命盘
    test_data = {
        "year_pillar": {"stem": "甲", "branch": "子"},
        "month_pillar": {"stem": "丙", "branch": "寅"},
        "day_pillar": {"stem": "丙", "branch": "午"},
        "hour_pillar": {"stem": "戊", "branch": "戌"},
        "day_master": "丙",
        "gender": "男"
    }
    
    print("=== 命理解读引擎测试 ===\n")
    
    result = engine.interpret(test_data)
    
    print(f"日主分析：{result['day_master_analysis']}")
    print(f"\n五行分析：{result['wuxing_analysis']}")
    print(f"\n十神分析：{result['shishen_analysis']}")
    print(f"\n调候分析：{result['tiaohou_analysis']}")
    print(f"\n格局分析：{result['geshi_analysis']}")
    print(f"\n用神分析：{result['yongshen_analysis']}")
    print(f"\n运势分析：{result['fortune_analysis']}")
    print(f"\n改善建议：{result['suggestions']}")
    print(f"\n综合总结：{result['overall_summary']}")
    
    return result


if __name__ == "__main__":
    test_engine()
