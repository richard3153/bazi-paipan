# app/services/interpretation.py
"""
命理解读服务
基于五本经典命理书籍进行八字解读
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.mingli import MingLiKnowledge, ShishenEntry, GeshiRule


def interpret_bazi(bazi_result: dict, db: Session,
                   include_geshi: bool = True,
                   include_yongshen: bool = True,
                   source_books: Optional[List[str]] = None) -> dict:
    """
    命理解读主函数
    
    分析：十神旺衰、格局判断、用神分析、喜忌判断
    """
    day_master = bazi_result["day_master"]
    day_master_wuxing = bazi_result["day_master_wuxing"]
    
    # 计算五行旺衰（简化版）
    wuxing_strength = _calculate_wuxing_strength(bazi_result)
    
    # 分析十神
    shishen_analysis = _analyze_shishen(bazi_result, db)
    
    # 格局判断
    geshi = None
    if include_geshi:
        geshi = _judge_geshi(bazi_result, db)
    
    # 用神分析
    yongshen = None
    if include_yongshen:
        yongshen = _analyze_yongshen(bazi_result, wuxing_strength)
    
    # 综合评断
    overall = _overall_judgment(bazi_result, wuxing_strength, geshi, yongshen)
    
    return {
        "day_master": day_master,
        "day_master_wuxing": day_master_wuxing,
        "wuxing_strength": wuxing_strength,
        "shishen_analysis": shishen_analysis,
        "geshi": geshi,
        "yongshen": yongshen,
        "overall": overall,
    }


def _calculate_wuxing_strength(bazi_result: dict) -> dict:
    """计算五行旺衰得分"""
    pillars = [
        bazi_result["year_pillar"],
        bazi_result["month_pillar"],
        bazi_result["day_pillar"],
        bazi_result["hour_pillar"],
    ]
    
    # 四柱+地支藏干全部纳入计算
    all_stems = [p["stem"] for p in pillars]
    all_branches = [p["branch"] for p in pillars]
    for p in pillars:
        all_stems.extend(p.get("hidden_stems", []))
    
    wuxing_counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for stem in all_stems:
        from app.core.constants import WU_XING_MAP
        wx = WU_XING_MAP.get(stem)
        if wx:
            wuxing_counts[wx] += 1
    
    # 月令权重最高
    month_branch = bazi_result["month_pillar"]["branch"]
    from app.core.constants import WU_XING_MAP
    month_wuxing = WU_XING_MAP.get(month_branch, "")
    
    # 五行旺相休囚死（月令）
    # 木：旺春三月（寅卯月），相冬三月（亥子月）...
    wang_months = {
        "木": ["寅", "卯"],
        "火": ["巳", "午"],
        "土": ["辰", "戌", "丑", "未"],  # 土旺四季
        "金": ["申", "酉"],
        "水": ["亥", "子"],
    }
    xiang_months = {
        "木": "亥子", "火": "寅卯", "土": "巳午",
        "金": "巳午", "水": "辰戌丑未",
    }
    
    # 得分计算
    scores = {}
    for wx in ["木", "火", "土", "金", "水"]:
        score = wuxing_counts[wx] * 1.0
        if month_branch in wang_months[wx]:
            score += 2.0  # 月令旺加2分
        elif month_branch in xiang_months[wx]:
            score -= 0.5  # 月令相减分
        scores[wx] = round(score, 1)
    
    return {
        "counts": wuxing_counts,
        "scores": scores,
        "month_wuxing": month_wuxing,
        "analysis": _interpret_scores(scores, day_master_wuxing=bazi_result["day_master_wuxing"]),
    }


def _interpret_scores(scores: dict, day_master_wuxing: str) -> str:
    """解读旺衰得分"""
    dm_wx = day_master_wuxing
    dm_score = scores.get(dm_wx, 0)
    
    # 扶抑原则
    # 日主旺则抑之（克泄），日主弱则扶之（比助）
    if dm_score >= 4.0:
        return "日主旺"
    elif dm_score <= 1.5:
        return "日主弱"
    else:
        return "日主中和"


def _analyze_shishen(bazi_result: dict, db: Session) -> dict:
    """分析十神配置"""
    analysis = {}
    shishen_list = ["year_shishen", "month_shishen", "hour_shishen"]
    
    for key in shishen_list:
        item = bazi_result.get(key)
        if not item:
            continue
        ss_name = item["shishen"]
        if not ss_name:
            continue
        
        # 从数据库查询详细解释
        entry = db.query(ShishenEntry).filter(ShishenEntry.name == ss_name).first()
        
        analysis[key] = {
            "shishen": ss_name,
            "stem": item["stem"],
            "wuxing": item["wuxing"],
            "definition": entry.definition if entry else _default_shishen_def(ss_name),
        }
    
    return analysis


def _default_shishen_def(shishen: str) -> str:
    """十神默认释义"""
    defaults = {
        "比肩": "与我同类五行，代表同事、朋友、合作。",
        "劫财": "与我同类五行阴差阳错，代表竞争、破财、异性缘分。",
        "食神": "我生之五行，代表福气、才华、儿女。",
        "伤官": "我生之五行，代表才华、创新、口舌。",
        "偏财": "我克之五行，代表财运、父亲、情人。",
        "正财": "我克之五行，代表正当财富、勤俭。",
        "七杀": "克我之五行，代表压力、挑战、权力。",
        "正官": "克我之五行，代表官运、约束、责任。",
        "偏印": "生我之五行，代表权谋、学术、继母。",
        "正印": "生我之五行，代表学业、名誉、母亲。",
    }
    return defaults.get(shishen, "")


def _judge_geshi(bazi_result: dict, db: Session) -> Optional[dict]:
    """判断格局"""
    month_stem = bazi_result["month_pillar"]["stem"]
    month_branch = bazi_result["month_pillar"]["branch"]
    day_master = bazi_result["day_master"]
    
    # 格局判断基本规则
    geshi_rules = {
        "正官格": month_stem == "正官",
        "七杀格": month_stem == "七杀",
        "正财格": month_stem == "正财",
        "偏财格": month_stem == "偏财",
        "正印格": month_stem == "正印",
        "偏印格": month_stem == "偏印",
        "食神格": month_stem == "食神",
        "伤官格": month_stem == "伤官",
        "比肩格": month_stem == "比肩",
        "劫财格": month_stem == "劫财",
    }
    
    geshi_name = None
    for name, cond in geshi_rules.items():
        if cond:
            geshi_name = name
            break
    
    if not geshi_name:
        geshi_name = "杂格"
    
    # 从数据库获取解读
    rule = db.query(GeshiRule).filter(GeshiRule.name == geshi_name).first()
    
    return {
        "name": geshi_name,
        "description": rule.interpretation if rule else _default_geshi_desc(geshi_name),
        "month_stem": month_stem,
        "month_branch": month_branch,
    }


def _default_geshi_desc(geshi: str) -> str:
    defaults = {
        "正官格": "以正官为月令，主人循规蹈矩，有责任心事业心。",
        "七杀格": "以七杀为月令，主人刚强果断，有魄力胆识。",
        "正财格": "以正财为月令，主人勤俭节约，理财有方。",
        "偏财格": "以偏财为月令，主人慷慨大方，善于经营。",
        "正印格": "以正印为月令，主人仁慈厚道，学业有成。",
        "偏印格": "以偏印为月令，主人独立钻研，有技术专长。",
        "食神格": "以食神为月令，主人温和有福，才华出众。",
        "伤官格": "以伤官为月令，主人聪明才华，不受约束。",
        "比肩格": "以比肩为月令，主人独立自主，人缘广泛。",
        "劫财格": "以劫财为月令，主人争强好胜，财运不稳。",
        "杂格": "月令无用神，需综合全局分析。",
    }
    return defaults.get(geshi, "")


def _analyze_yongshen(bazi_result: dict, wuxing_strength: dict) -> dict:
    """用神分析"""
    scores = wuxing_strength["scores"]
    dm_wx = bazi_result["day_master_wuxing"]
    dm_score = scores.get(dm_wx, 0)
    
    # 旺则抑之，弱则扶之
    if dm_score >= 4.0:
        yong_type = "抑"
        # 抑日主之五行：官杀克之、食伤泄之、财耗之
        prefer_wuxing = _get_restraining_wuxing(dm_wx)
        avoid_wuxing = [dm_wx]
    elif dm_score <= 1.5:
        yong_type = "扶"
        # 扶日主之五行：印绶生之、比劫助之
        prefer_wuxing = _get_supporting_wuxing(dm_wx)
        avoid_wuxing = []
    else:
        yong_type = "调候"
        prefer_wuxing = ["水", "火"]  # 中和以调候为急
        avoid_wuxing = []
    
    return {
        "type": yong_type,
        "prefer_wuxing": prefer_wuxing,
        "avoid_wuxing": avoid_wuxing,
        "recommendation": _yongshen_recommendation(yong_type, dm_wx),
    }


def _get_restraining_wuxing(dm_wx: str) -> List[str]:
    """抑日主宜用的五行"""
    map_ = {
        "木": ["金"],
        "火": ["水"],
        "土": ["木"],
        "金": ["火"],
        "水": ["土"],
    }
    return map_.get(dm_wx, [])


def _get_supporting_wuxing(dm_wx: str) -> List[str]:
    """扶日主宜用的五行"""
    map_ = {
        "木": ["水", "木"],
        "火": ["木", "火"],
        "土": ["火", "土"],
        "金": ["土", "金"],
        "水": ["金", "水"],
    }
    return map_.get(dm_wx, [])


def _yongshen_recommendation(yong_type: str, dm_wx: str) -> str:
    recs = {
        "抑": f"{dm_wx}日主偏旺，宜克宜泄，官杀、食伤、财星为用。",
        "扶": f"{dm_wx}日主偏弱，宜生宜助，印绶、比劫为用。",
        "调候": f"{dm_wx}日主中和，调候为急，寒命喜暖，热命喜凉。",
    }
    return recs.get(yong_type, "")


def _overall_judgment(bazi_result: dict, wuxing_strength: dict,
                      geshi, yongshen) -> dict:
    """综合评断"""
    # 简单评分
    score = 60  # 基础分
    
    # 加分项
    month_stem = bazi_result["month_pillar"]["stem"]
    if month_stem in ["食神", "正印", "正官"]:
        score += 10
    if geshi and geshi["name"] in ["正官格", "正印格", "食神格"]:
        score += 10
    
    # 扣分项
    day_stem = bazi_result["day_master"]
    if day_stem in ["壬", "癸"] and bazi_result["month_pillar"]["stem"] == "七杀":
        score -= 10
    
    score = max(0, min(100, score))
    
    level_map = {
        range(0, 40): "平常",
        range(40, 60): "中等",
        range(60, 80): "良好",
        range(80, 100): "优秀",
    }
    level = "平常"
    for r, l in level_map.items():
        if score in r:
            level = l
            break
    
    return {
        "score": score,
        "level": level,
        "summary": f"此命造为{bazi_result['day_master_wuxing']}命，{wuxing_strength['analysis']}，{geshi['name'] if geshi else '格局待定'}。",
    }
