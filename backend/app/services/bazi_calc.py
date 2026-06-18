# app/services/bazi_calc.py
"""
四柱八字排盘计算引擎（修复版）
核心算法：年柱、月柱（节气）、日柱、时柱计算 + 大运 + 神煞
"""
from datetime import date, timedelta
from typing import Tuple, Optional, List, Dict
from app.core.constants import (
    HEAVENLY_STEMS, EARTHLY_BRANCHES, CYCLE60, CYCLE60_INDEX,
    STEM_INDEX, BRANCH_INDEX, BRANCH_HIDDEN_STEMS, WU_XING_MAP,
    SHISHEN_MAP, MONTH_STEM_START, HOUR_STEM_START,
    WU_XING_WEAK, WU_XING_STRONG, WU_XING_COLORS,
    SOLAR_TERMS, SOLAR_TERM_MONTHS, get_solar_term_dates,
    TWELVE_LIFECYCLE_YANG, TWELVE_LIFECYCLE_YIN, NAYIN_MAP, BRANCH_HOURS,
)

# 日主禄位（建禄格判断用）
LU_POSITION = {
    "甲": "寅", "乙": "卯", "丙": "巳", "丁": "午",
    "戊": "巳", "己": "午", "庚": "申", "辛": "酉",
    "壬": "亥", "癸": "子"
}

# ============ 穷通宝鉴调候用神表 ============
TIAOHOU_TABLE = {
    "寅": {
        "甲": ["丙", "癸"], "乙": ["丙", "癸"], "丙": ["壬"],
        "丁": ["甲", "庚"], "戊": ["丙", "甲"], "己": ["丙", "甲"],
        "庚": ["丙", "甲", "戊"], "辛": ["丙", "壬", "戊"],
        "壬": ["丙", "庚"], "癸": ["丙", "戊"],
    },
    "卯": {
        "甲": ["丙", "癸", "庚"], "乙": ["丙", "癸"], "丙": ["壬"],
        "丁": ["甲", "庚"], "戊": ["丙", "甲", "癸"], "己": ["丙", "甲", "癸"],
        "庚": ["丙", "甲", "戊"], "辛": ["丙", "壬"],
        "壬": ["庚", "戊"], "癸": ["庚", "戊"],
    },
    "辰": {
        "甲": ["丙", "癸", "庚"], "乙": ["丙", "癸"], "丙": ["壬", "甲"],
        "丁": ["甲", "庚"], "戊": ["丙", "甲", "癸"], "己": ["丙", "甲", "癸"],
        "庚": ["丙", "甲", "戊"], "辛": ["丙", "壬"],
        "壬": ["甲", "庚"], "癸": ["甲", "庚"],
    },
    "巳": {
        "甲": ["丙", "癸", "庚"], "乙": ["癸", "丙"], "丙": ["壬", "庚"],
        "丁": ["甲", "壬"], "戊": ["丙", "甲", "癸"], "己": ["癸", "丙", "甲"],
        "庚": ["丙", "甲", "壬"], "辛": ["丙", "壬"],
        "壬": ["癸", "甲"], "癸": ["癸", "辛"],
    },
    "午": {
        "甲": ["丙", "癸", "庚"], "乙": ["癸", "丙"], "丙": ["壬", "庚"],
        "丁": ["甲", "壬"], "戊": ["丙", "甲", "癸"], "己": ["癸", "丙", "甲"],
        "庚": ["丙", "甲", "壬"], "辛": ["丙", "壬"],
        "壬": ["癸", "庚"], "癸": ["癸", "辛"],
    },
    "未": {
        "甲": ["丙", "癸", "庚"], "乙": ["癸", "丙"], "丙": ["壬", "甲"],
        "丁": ["甲", "壬"], "戊": ["丙", "甲", "癸"], "己": ["癸", "丙", "甲"],
        "庚": ["丙", "甲", "壬"], "辛": ["壬"],
        "壬": ["甲", "庚"], "癸": ["甲", "庚"],
    },
    "申": {
        "甲": ["丙", "癸", "庚"], "乙": ["丙", "癸"], "丙": ["壬", "甲"],
        "丁": ["甲", "庚"], "戊": ["丙", "甲", "癸"], "己": ["丙", "甲", "癸"],
        "庚": ["丙", "甲"], "辛": ["壬"],
        "壬": ["戊", "庚"], "癸": ["戊", "庚"],
    },
    "酉": {
        "甲": ["丙", "癸", "庚"], "乙": ["丙", "癸"], "丙": ["壬", "甲"],
        "丁": ["甲", "庚"], "戊": ["丙", "甲", "癸"], "己": ["丙", "甲", "癸"],
        "庚": ["丙", "甲"], "辛": ["壬"],
        "壬": ["戊", "庚"], "癸": ["戊", "庚"],
    },
    "戌": {
        "甲": ["丙", "癸", "庚"], "乙": ["丙", "癸"], "丙": ["壬", "甲"],
        "丁": ["甲", "庚"], "戊": ["丙", "甲", "癸"], "己": ["癸", "丙", "甲"],
        "庚": ["丙", "甲"], "辛": ["壬"],
        "壬": ["甲", "庚"], "癸": ["甲", "庚"],
    },
    "亥": {
        "甲": ["丙", "庚"], "乙": ["丙"], "丙": ["甲", "壬"],
        "丁": ["甲", "庚"], "戊": ["丙", "甲"], "己": ["丙", "甲"],
        "庚": ["丙", "甲"], "辛": ["丙", "戊", "壬"],
        "壬": ["丙", "戊"], "癸": ["丙", "戊"],
    },
    "子": {
        "甲": ["丙", "庚"], "乙": ["丙"], "丙": ["甲", "壬"],
        "丁": ["甲", "庚"], "戊": ["丙", "甲"], "己": ["丙", "甲"],
        "庚": ["丙", "甲"], "辛": ["丙", "壬"],
        "壬": ["丙", "戊"], "癸": ["丙", "戊"],
    },
    "丑": {
        "甲": ["丙", "庚"], "乙": ["丙"], "丙": ["甲", "壬"],
        "丁": ["甲", "庚"], "戊": ["丙", "甲"], "己": ["丙", "甲"],
        "庚": ["丙", "甲"], "辛": ["丙", "壬"],
        "壬": ["丙", "戊"], "癸": ["丙", "戊"],
    },
}

# 寒暖描述模板
_HANNUAN_DESC = {
    "寒": "生于{month}月，命局偏寒，需丙火温暖为先",
    "暖": "生于{month}月，命局偏热，需壬癸水调候为先",
    "平": "生于{month}月，寒暖适中",
}

# 燥湿描述模板
_ZAOSHI_DESC = {
    "燥": "{month}土燥，需癸水润之",
    "湿": "{month}土湿，需丙火燥之",
    "平": "",
}

# 日主调候描述模板
_TIAOHOU_DESC = {
    "寅": {
        "甲": "初春寒，用丙暖局，用癸润木",
        "乙": "初春寒，用丙暖局，用癸润木",
        "丙": "春火初生，用壬济火",
        "丁": "春丁弱，用甲引丁，庚劈甲",
        "戊": "春土寒，用丙暖，甲疏土",
        "己": "春土寒，用丙暖，甲疏土",
        "庚": "春庚弱，用丙暖、甲生火、戊生金",
        "辛": "初春辛弱，用丙暖、壬洗金、戊制水",
        "壬": "春水寒，用丙暖、庚生水",
        "癸": "冬癸寒，用丙暖、戊制水",
    },
    "卯": {
        "甲": "仲春木旺，丙癸调候，庚制木",
        "乙": "仲春木旺，用丙癸调候",
        "丙": "春火渐旺，用壬制火",
        "丁": "春丁弱，用甲引丁，庚劈甲",
        "戊": "春土弱，丙暖、甲疏、癸润",
        "己": "春土弱，丙暖、甲疏、癸润",
        "庚": "春庚弱，用丙暖、甲生火、戊生金",
        "辛": "春辛弱，用丙暖、壬洗金",
        "壬": "春水旺，用庚生、戊制",
        "癸": "春水旺，用庚生、戊制",
    },
    "辰": {
        "甲": "季春土旺，用丙暖、癸润、庚制",
        "乙": "季春木退气，用丙癸",
        "丙": "辰月湿土，用壬济火、甲生火",
        "丁": "春丁弱，用甲引丁、庚劈甲",
        "戊": "辰土湿，用丙暖、甲疏、癸润",
        "己": "辰土湿，用丙暖、甲疏、癸润",
        "庚": "辰土生金，用丙暖、甲生火",
        "辛": "春辛弱，用丙暖、壬洗金",
        "壬": "辰月水墓，用甲泄水、庚生水",
        "癸": "辰月水墓，用甲泄水、庚生水",
    },
    "巳": {
        "甲": "夏木焦，用癸润、庚制",
        "乙": "夏乙弱，用癸润为先",
        "丙": "夏火旺，用壬制火、庚生壬",
        "丁": "夏丁旺，用壬济火、甲生丁",
        "戊": "夏土燥，用癸润为先",
        "己": "夏土燥，用癸润为先",
        "庚": "夏金弱，用壬泄火、丙暖金",
        "辛": "夏辛弱，用壬洗金",
        "壬": "夏水弱，用癸助水、甲泄火",
        "癸": "夏水弱，用癸助水、辛生水",
    },
    "午": {
        "甲": "夏木焦，用癸润为先",
        "乙": "夏乙弱，用癸润为先",
        "丙": "夏火旺，用壬制火",
        "丁": "夏丁旺，用壬济火、甲生丁",
        "戊": "夏土燥，用癸润为先",
        "己": "夏土燥，用癸润为先",
        "庚": "夏金弱，用壬泄火",
        "辛": "夏辛弱，用壬洗金",
        "壬": "夏水弱，用癸助水",
        "癸": "夏水弱，用癸助水、辛生水",
    },
    "未": {
        "甲": "季夏土旺，用癸润、庚制",
        "乙": "季夏土旺，用癸润为先",
        "丙": "未土燥，用壬济火",
        "丁": "夏丁旺，用壬济火、甲生丁",
        "戊": "未土燥，用癸润为先",
        "己": "未土燥，用癸润为先",
        "庚": "未土生金，用壬泄火",
        "辛": "夏辛弱，用壬洗金",
        "壬": "未月水弱，用甲泄火、庚生水",
        "癸": "未月水弱，用甲泄火、庚生水",
    },
    "申": {
        "甲": "秋木退气，用癸润、庚制",
        "乙": "秋乙弱，用癸润",
        "丙": "秋火退气，用甲生火、壬济火",
        "丁": "秋丁弱，用甲生丁",
        "戊": "秋土弱，用丙暖",
        "己": "秋土弱，用丙暖",
        "庚": "秋金旺，用丙暖、甲生火",
        "辛": "秋金旺，用壬洗金",
        "壬": "秋水旺，用戊制水",
        "癸": "秋水旺，用戊制水",
    },
    "酉": {
        "甲": "秋木凋零，用癸润、庚制",
        "乙": "秋乙弱，用癸润",
        "丙": "秋火弱，用甲生火",
        "丁": "秋丁弱，用甲生丁",
        "戊": "秋土弱，用丙暖",
        "己": "秋土弱，用丙暖",
        "庚": "秋金旺，用丙暖",
        "辛": "秋金旺，用壬洗金",
        "壬": "秋水旺，用戊制水",
        "癸": "秋水旺，用戊制水",
    },
    "戌": {
        "甲": "季秋土旺，用癸润、庚制",
        "乙": "季秋木弱，用癸润",
        "丙": "戌土燥，用壬济火",
        "丁": "秋丁弱，用甲生丁",
        "戊": "戌土燥，用癸润为先",
        "己": "戌土燥，用癸润为先",
        "庚": "秋金旺，用丙暖",
        "辛": "秋辛弱，用壬洗金",
        "壬": "戌月水弱，用甲泄火、庚生水",
        "癸": "戌月水弱，用甲泄火、庚生水",
    },
    "亥": {
        "甲": "冬木寒，用丙暖为先",
        "乙": "冬乙寒，用丙暖",
        "丙": "冬火弱，用甲生火、壬济火",
        "丁": "冬丁弱，用甲生丁",
        "戊": "冬土寒，用丙暖、甲疏土",
        "己": "冬土寒，用丙暖、甲疏土",
        "庚": "冬金寒，用丙暖、甲生火",
        "辛": "冬金寒，用丙暖、壬洗金",
        "壬": "冬水寒，用丙暖、戊制水",
        "癸": "冬水寒，用丙暖、戊制水",
    },
    "子": {
        "甲": "冬木寒，用丙暖为先",
        "乙": "冬乙寒，用丙暖",
        "丙": "冬火弱，用甲生火、壬济火",
        "丁": "冬丁弱，用甲生丁",
        "戊": "冬土寒，用丙暖、甲疏土",
        "己": "冬土寒，用丙暖、甲疏土",
        "庚": "冬金寒，用丙暖、甲生火",
        "辛": "冬金寒，用丙暖、壬洗金",
        "壬": "冬水旺，用丙暖、戊制水",
        "癸": "冬水旺，用丙暖、戊制水",
    },
    "丑": {
        "甲": "冬木寒，用丙暖为先",
        "乙": "冬乙寒，用丙暖",
        "丙": "丑土湿，用甲生火",
        "丁": "冬丁弱，用甲生丁",
        "戊": "丑土寒，用丙暖、甲疏土",
        "己": "丑土寒，用丙暖、甲疏土",
        "庚": "冬金寒，用丙暖、甲生火",
        "辛": "冬金寒，用丙暖、壬洗金",
        "壬": "丑月水墓，用丙暖、戊制水",
        "癸": "丑月水墓，用丙暖、戊制水",
    },
}

# 日主羊刃位（月刃格判断用）
YANGREN_POSITION = {
    "甲": "卯", "乙": "辰", "丙": "午", "丁": "未",
    "戊": "午", "己": "未", "庚": "酉", "辛": "戌",
    "壬": "子", "癸": "丑"
}


# ============ 基础工具函数 ============

def get_stem_branch(index60: int) -> Tuple[str, str]:
    comb = CYCLE60[index60 % 60]
    return comb[0], comb[1]


def yinyang(stem_or_branch: str) -> str:
    yang = ["甲", "丙", "戊", "庚", "壬", "子", "寅", "辰", "午", "申", "戌"]
    return "阳" if stem_or_branch in yang else "阴"


def wuxing(elem: str) -> str:
    return WU_XING_MAP.get(elem, "")


# ============ 节气工具 ============

def _get_term_dates_for_year(year: int) -> List[Tuple[int, int]]:
    """获取某年24节气日期表"""
    return get_solar_term_dates(year)


def _date_ordinal(y: int, m: int, d: int) -> int:
    """日期转序号（用于比较）"""
    return date(y, m, d).toordinal()


def get_lichun_date(year: int) -> Tuple[int, int]:
    """获取立春日期，节气序号2"""
    terms = _get_term_dates_for_year(year)
    return terms[2]  # 立春


def get_month_branch_by_terms(year: int, month: int, day: int) -> int:
    """
    根据节气确定月支序号（0=子, 1=丑, ..., 11=亥）
    节气与月支的对应关系：
      小寒→丑月(1), 大寒→丑月
      立春→寅月(2), 雨水→寅月
      惊蛰→卯月(3), 春分→卯月
      ...
      大雪→子月(0), 冬至→子月
    """
    terms = _get_term_dates_for_year(year)
    birth_ord = _date_ordinal(year, month, day)

    # 节气序号→月支映射
    # 0:小寒→丑(1), 1:大寒→丑(1)
    # 2:立春→寅(2), 3:雨水→寅(2)
    # 4:惊蛰→卯(3), 5:春分→卯(3)
    # ...
    # 节气i对应的月支 = (i // 2 + 1) % 12
    # 但小寒(0)→丑(1), 所以是 (0//2 + 1) % 12 = 1 ✓
    # 立春(2)→寅(2), (2//2 + 1) % 12 = 2 ✓

    # 从后往前找：出生日在哪个节气区间
    # 遍历节气，找到出生日所在区间
    month_branch = 1  # 默认丑月
    for i in range(24):
        term_m, term_d = terms[i]
        term_ord = _date_ordinal(year, term_m, term_d)
        if birth_ord >= term_ord:
            # 这个节气已过，更新月支
            branch_idx = (i // 2 + 1) % 12
            month_branch = branch_idx

    return month_branch


def get_nearest_jie_term(year: int, month: int, day: int):
    """
    获取最近的一个"节"（非"气"）。
    节是：立春、惊蛰、清明、立夏、芒种、小暑、立秋、白露、寒露、立冬、大雪、小寒
    对应节气序号：2,4,6,8,10,12,14,16,18,20,22,0
    返回 (term_name, term_month, term_day, direction)
    direction: 1=下一个节, -1=上一个节
    """
    terms = _get_term_dates_for_year(year)
    birth_ord = _date_ordinal(year, month, day)

    jie_indices = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
    jie_names = ["小寒", "立春", "惊蛰", "清明", "立夏", "芒种",
                 "小暑", "立秋", "白露", "寒露", "立冬", "大雪"]

    next_jie = None
    prev_jie = None

    for idx_in_list, term_i in enumerate(jie_indices):
        t_m, t_d = terms[term_i]
        t_ord = _date_ordinal(year, t_m, t_d)
        if t_ord > birth_ord and next_jie is None:
            next_jie = (jie_names[idx_in_list], t_m, t_d, t_ord)
        if t_ord <= birth_ord:
            prev_jie = (jie_names[idx_in_list], t_m, t_d, t_ord)

    return prev_jie, next_jie


# ============ 年柱计算 ============

def get_year_pillar(year: int, month: int, day: int) -> Tuple[str, str]:
    """
    计算年柱（考虑立春）
    立春前属上一年
    """
    lichun_m, lichun_d = get_lichun_date(year)
    if month < lichun_m or (month == lichun_m and day < lichun_d):
        # 立春前，属上一年
        actual_year = year - 1
    else:
        actual_year = year
    cycle_index = (actual_year - 4) % 60
    return get_stem_branch(cycle_index)


# ============ 月柱计算 ============

def get_month_pillar(year_stem: str, year: int, month: int, day: int) -> Tuple[str, str]:
    """
    计算月柱（以节气为界）
    月支由节气区间决定
    月干由年干通过五虎遁推出
    """
    branch_idx = get_month_branch_by_terms(year, month, day)
    month_branch = EARTHLY_BRANCHES[branch_idx]

    # 五虎遁：年干 → 寅月(2月)天干
    yin_stem = MONTH_STEM_START.get(year_stem, "甲")
    yin_stem_idx = STEM_INDEX[yin_stem]
    # 寅月 = branch_idx=2, 所以月干 = (寅月干 + (当前月支 - 寅)) % 10
    month_stem_idx = (yin_stem_idx + branch_idx - 2) % 10
    month_stem = HEAVENLY_STEMS[month_stem_idx]

    return month_stem, month_branch


# ============ 日柱计算 ============

def get_day_pillar(year: int, month: int, day: int) -> Tuple[str, str]:
    """
    计算日柱
    基准：1899年12月22日 = 甲子日（六十甲子第0位）
    """
    base = date(1899, 12, 22)
    target = date(year, month, day)
    days_diff = (target - base).days
    cycle_index = days_diff % 60
    return get_stem_branch(cycle_index)


# ============ 时柱计算 ============

def get_hour_branch_index(hour: int, minute: int) -> int:
    """获取时辰地支序号 (0=子 ... 11=亥)"""
    total_min = hour * 60 + minute
    if total_min >= 23 * 60:  # 23:00-23:59 夜子时
        return 0  # 子时
    elif total_min < 1 * 60:  # 00:00-00:59 早子时
        return 0  # 子时
    else:
        return ((total_min // 60) + 1) // 2


def is_early_zi_hour(hour: int, minute: int) -> bool:
    """判断是否为早子时 (00:00-00:59)"""
    total_min = hour * 60 + minute
    return total_min < 1 * 60  # 00:00-00:59


def get_hour_pillar(day_stem: str, hour: int, minute: int = 0, use_prev_day: bool = False) -> Tuple[str, str]:
    """
    计算时柱
    时柱天干用五鼠遁日诀
    
    Args:
        day_stem: 日干
        hour: 小时
        minute: 分钟
        use_prev_day: 是否使用前一日日干（早子时时需要）
    """
    branch_idx = get_hour_branch_index(hour, minute)
    hour_branch = EARTHLY_BRANCHES[branch_idx]

    # 五鼠遁日诀：日干 → 子时天干
    # 早子时 (00:00-00:59) 需用前一日日干推五鼠遁
    effective_day_stem = day_stem
    if use_prev_day:
        # 使用前一日日干
        day_stem_idx = STEM_INDEX[day_stem]
        prev_day_stem_idx = (day_stem_idx - 1) % 10
        effective_day_stem = HEAVENLY_STEMS[prev_day_stem_idx]
    
    zi_stem = HOUR_STEM_START.get(effective_day_stem, "甲")
    zi_stem_idx = STEM_INDEX[zi_stem]
    hour_stem_idx = (zi_stem_idx + branch_idx) % 10
    hour_stem = HEAVENLY_STEMS[hour_stem_idx]

    return hour_stem, hour_branch


# ============ 十神 ============

def get_shishen(day_master: str, target_stem: str) -> str:
    return SHISHEN_MAP.get(day_master, {}).get(target_stem, "")


# ============ 格局判定（子平真诠核心） ============

def determine_geju(bazi_dict: dict, day_master: str) -> dict:
    """
    格局判定（子平真诠核心）
    
    取格规则：
    1. 先看月支本气是否透出（在年干/月干/日干/时干中出现）
    2. 本气不透，看月支余气/杂气是否透出（优先取本气）
    3. 透出多干时，取月令本气优先，或力量最强者
    4. 月支为日主禄/刃时，为建禄格/月刃格（外格）
    
    返回：
    {
        "geju": "正印格",      # 格局名称
        "chengge": True,      # 是否成格
        "desc": "...",        # 描述
        "touchu_stem": "甲",  # 透出天干
        "touchu_shishen": "正印",  # 透出天干的十神
    }
    """
    month_branch = bazi_dict.get("month_branch", "")
    if not month_branch:
        return {"geju": "未知", "chengge": False, "desc": "月支未知", "touchu_stem": "", "touchu_shishen": ""}
    
    # 获取所有天干
    year_stem = bazi_dict.get("year_stem", "")
    month_stem = bazi_dict.get("month_stem", "")
    day_stem = bazi_dict.get("day_stem", "")
    hour_stem = bazi_dict.get("hour_stem", "")
    all_stems = [year_stem, month_stem, day_stem, hour_stem]
    
    # 获取月支藏干（本气、中气、余气）
    hidden_stems = BRANCH_HIDDEN_STEMS.get(month_branch, [])
    if not hidden_stems:
        return {"geju": "未知", "chengge": False, "desc": "月支藏干未知", "touchu_stem": "", "touchu_shishen": ""}
    
    # 检查特殊格局：建禄格、月刃格
    if LU_POSITION.get(day_master) == month_branch:
        return {
            "geju": "建禄格",
            "chengge": True,
            "desc": f"月支{month_branch}为日主{day_master}之禄位，建禄格",
            "touchu_stem": "",
            "touchu_shishen": ""
        }
    
    if YANGREN_POSITION.get(day_master) == month_branch:
        return {
            "geju": "月刃格",
            "chengge": True,
            "desc": f"月支{month_branch}为日主{day_master}之羊刃位，月刃格",
            "touchu_stem": "",
            "touchu_shishen": ""
        }
    
    # 按优先级（本气 > 中气 > 余气）查找透出的藏干
    benqi = hidden_stems[0] if len(hidden_stems) > 0 else None
    zhongqi = hidden_stems[1] if len(hidden_stems) > 1 else None
    yuqi = hidden_stems[2] if len(hidden_stems) > 2 else None
    
    # 检查本气是否透出
    touchu_stem = None
    if benqi and benqi in all_stems:
        touchu_stem = benqi
    elif zhongqi and zhongqi in all_stems:
        touchu_stem = zhongqi
    elif yuqi and yuqi in all_stems:
        touchu_stem = yuqi
    
    # 如果没有透出，取本气（即使不透也取，这是子平法的一种处理方式）
    if not touchu_stem:
        touchu_stem = benqi  # 取本气
    
    if not touchu_stem:
        return {"geju": "无格", "chengge": False, "desc": "月支藏干无透出", "touchu_stem": "", "touchu_shishen": ""}
    
    # 确定十神关系
    shishen = get_shishen(day_master, touchu_stem)
    
    # 根据十神确定格局
    geju_map = {
        "正官": "正官格",
        "七杀": "七杀格",
        "正财": "正财格",
        "偏财": "偏财格",
        "正印": "正印格",
        "偏印": "偏印格",
        "食神": "食神格",
        "伤官": "伤官格",
    }
    
    geju = geju_map.get(shishen, "无格")
    
    # 判断成格/破格（简化版：无严重冲克即成格）
    # 简化：暂不考虑刑冲，默认成格
    chengge = True
    
    desc = f"月支{month_branch}藏干{touchu_stem}"
    if touchu_stem in all_stems:
        # 找到透出的位置
        positions = []
        if year_stem == touchu_stem:
            positions.append("年干")
        if month_stem == touchu_stem:
            positions.append("月干")
        if day_stem == touchu_stem:
            positions.append("日干")
        if hour_stem == touchu_stem:
            positions.append("时干")
        desc += f"透出在{''.join(positions)}"
    else:
        desc += "（不透）"
    desc += f"，{shishen}，故为{geju}"
    
    return {
        "geju": geju,
        "chengge": chengge,
        "desc": desc,
        "touchu_stem": touchu_stem,
        "touchu_shishen": shishen
    }


# ============ 纳音 ============

def get_nayin(stem: str, branch: str) -> str:
    return NAYIN_MAP.get(stem + branch, "")


# ============ 大运计算 ============

def calculate_dayun(
    year_stem: str, month_stem: str, month_branch: str,
    birth_year: int, birth_month: int, birth_day: int,
    gender: str = "男",
    day_master: str = ""
) -> dict:
    """
    计算大运
    阳年男命/阴年女命 → 顺行
    阴年男命/阳年女命 → 逆行
    起运年龄 = 出生到最近节的天数 / 3
    
    返回详细信息包括：
    - qiyun: 起运详细信息（天数计算、方向、交运年份）
    - dayun: 8步大运列表（含纳音）
    - tongyun: 童运列表（1-12岁）
    """
    year_yy = yinyang(year_stem)
    is_male = gender in ("男", "male", "Male", "M")
    forward = (year_yy == "阳" and is_male) or (year_yy == "阴" and not is_male)
    direction_text = "顺行" if forward else "逆行"

    # 计算起运年龄
    prev_jie, next_jie = get_nearest_jie_term(birth_year, birth_month, birth_day)
    if forward and next_jie:
        days = next_jie[3] - _date_ordinal(birth_year, birth_month, birth_day)
        ref_term = next_jie[0]  # 下一个节
    elif not forward and prev_jie:
        days = _date_ordinal(birth_year, birth_month, birth_day) - prev_jie[3]
        ref_term = prev_jie[0]  # 上一个节
    else:
        days = 90
        ref_term = "立春"

    # 转换为岁、月
    years = days // 3
    remaining_days = days % 3
    months = remaining_days * 4  # 一天 = 四个月
    
    # 计算起运年龄（实岁）
    start_age = max(1, years)
    # 虚岁起运
    start_age_xu = start_age + 1

    # 计算交运年份
    # 顺行：出生年 + 实岁起运
    # 逆行：出生年 + 实岁起运
    jiaoyun_year = birth_year + start_age
    
    # 计算起运月（简化版：按月份推进）
    jiaoyun_month_offset = months % 12
    jiaoyun_month = birth_month + jiaoyun_month_offset if jiaoyun_month_offset <= 12 else jiaoyun_month_offset - 12
    if jiaoyun_month > 12:
        jiaoyun_month -= 12
        jiaoyun_year += 1

    # 大运从月柱出发
    m_stem_idx = STEM_INDEX[month_stem]
    m_branch_idx = BRANCH_INDEX[month_branch]

    dayun_list = []
    for i in range(1, 9):
        if forward:
            s_idx = (m_stem_idx + i) % 10
            b_idx = (m_branch_idx + i) % 12
        else:
            s_idx = (m_stem_idx - i) % 10
            b_idx = (m_branch_idx - i) % 12
        stem = HEAVENLY_STEMS[s_idx]
        branch = EARTHLY_BRANCHES[b_idx]
        # 计算每步大运的起始年份
        d_start_year = jiaoyun_year + (i - 1) * 10
        d_end_year = d_start_year + 9
        ss = get_shishen(day_master, stem) if day_master else ""
        dayun_list.append({
            "index": i,
            "startAge": start_age + (i - 1) * 10,
            "endAge": start_age + i * 10 - 1,
            "stem": stem,
            "branch": branch,
            "nayin": get_nayin(stem, branch),
            "shishen": ss,
            "startYear": d_start_year,
            "endYear": d_end_year,
        })

    # 计算童运（1-12岁）
    # 渊海子平：童运从月柱起（1岁=月柱本身，offset=0）
    tongyun_list = []
    for age in range(1, 13):
        offset = age - 1  # 1岁=月柱，offset=0
        if forward:
            s_idx = (m_stem_idx + offset) % 10
            b_idx = (m_branch_idx + offset) % 12
        else:
            s_idx = (m_stem_idx - offset) % 10
            b_idx = (m_branch_idx - offset) % 12
        stem = HEAVENLY_STEMS[s_idx]
        branch = EARTHLY_BRANCHES[b_idx]
        ss = get_shishen(day_master, stem) if day_master else ""
        tongyun_list.append({
            "age": age,
            "stem": stem,
            "branch": branch,
            "nayin": get_nayin(stem, branch),
            "shishen": ss,
        })

    return {
        "forward": forward,
        "direction": direction_text,
        "startAge": start_age,  # 实岁
        "startAgeXu": start_age_xu,  # 虚岁
        "qiyunDays": days,  # 起运天数
        "qiyunMonths": months,  # 起运月数（天数的余月）
        "refTerm": ref_term,  # 参考节气
        "jiaoyunYear": jiaoyun_year,  # 交运年份
        "jiaoyunMonth": jiaoyun_month,  # 交运月份
        "dayun": dayun_list,
        "tongyun": tongyun_list,
    }


# ============ 神煞计算 ============

def calculate_shensha(
    year_stem: str, year_branch: str,
    month_stem: str, month_branch: str,
    day_stem: str, day_branch: str,
    hour_stem: str, hour_branch: str,
    gender: str = "男",
) -> Dict[str, List[str]]:
    """计算神煞，返回 {干支位置: [神煞名]}
    
    分类方式：年干/年支/月干/月支/日干/日支/时干/时支
    神煞归属于「生成该神煞」的干或支
    gender参数用于元辰等需性别区别的神煞
    """
    result = {
        "year_stem": [], "year_branch": [],
        "month_stem": [], "month_branch": [],
        "day_stem": [], "day_branch": [],
        "hour_stem": [], "hour_branch": [],
    }
    dm = day_stem
    all_branches = [year_branch, month_branch, day_branch, hour_branch]
    all_stems = [year_stem, month_stem, day_stem, hour_stem]
    # 地支 → 位置 映射（用于干查神煞标在对应地支位置）
    # 用列表存储，以处理相同地支值的情况（如年月支相同）
    branch_positions = [
        (year_branch, "year_branch"),
        (month_branch, "month_branch"),
        (day_branch, "day_branch"),
        (hour_branch, "hour_branch"),
    ]

    # 判断阴阳年（以年干阴阳性为准）
    yang_stems = ["甲", "丙", "戊", "庚", "壬"]
    is_yang_year = year_stem in yang_stems

    # ===== 天乙贵人（年干查 + 日干查）=====
    # 甲戊庚牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸兔蛇藏，六辛马虎方
    # 天乙贵人口诀：甲戊庚牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸兔蛇藏，六辛马虎方
    # 庚日见午寅（六辛马虎方），辛日见午寅
    tianyi_map = {"甲": ["丑", "未"], "乙": ["子", "申"], "丙": ["亥", "酉"],
                  "丁": ["亥", "酉"], "戊": ["丑", "未"], "己": ["子", "申"],
                  "庚": ["午", "寅"], "辛": ["午", "寅"], "壬": ["卯", "巳"],
                  "癸": ["卯", "巳"]}
    # 年干查天乙贵人（参考盘不显示，注释掉）
    # tianyi_ys = tianyi_map.get(year_stem, [])
    # if tianyi_ys:
    #     for b in tianyi_ys:
    #         for b2, pos in branch_positions:
    #             if b == b2 and "天乙贵人" not in result[pos]:
    #                 result[pos].append("天乙贵人")
    #                 break
    # 日干查天乙贵人（参考盘不显示，注释掉）
    # tianyi_ds = tianyi_map.get(dm, [])
    # if tianyi_ds:
    #     for b in tianyi_ds:
    #         for b2, pos in branch_positions:
    #             if b == b2 and "天乙贵人" not in result[pos]:
    #                 result[pos].append("天乙贵人")
    #                 break

    # ===== 太极贵人（年干查 + 日干查）=====
    # 甲乙生人子午中，丙丁兔鸡定，戊己四墓库，庚辛寅亥寻，壬癸巳申同
    taiji_map = {"甲": ["子", "午"], "乙": ["子", "午"],
                 "丙": ["卯", "酉"], "丁": ["卯", "酉"],
                 "戊": ["辰", "戌", "丑", "未"], "己": ["辰", "戌", "丑", "未"],
                 "庚": ["寅", "亥"], "辛": ["寅", "亥"],
                 "壬": ["巳", "申"], "癸": ["巳", "申"]}
    # ===== 太极贵人（年干查→标年干，日干查→标日干）=====
    taiji_ys = taiji_map.get(year_stem, [])
    if taiji_ys and any(b in taiji_ys for b in all_branches):
        result["year_stem"].append("太极贵人")
    taiji_ds = taiji_map.get(dm, [])
    if taiji_ds and any(b in taiji_ds for b in all_branches):
        result["day_stem"].append("太极贵人")

    # ===== 文昌贵人（日干查→标日干）=====
    wenchang_map = {"甲": "巳", "乙": "午", "丙": "申", "丁": "酉", "戊": "申",
                    "己": "酉", "庚": "亥", "辛": "子", "壬": "寅", "癸": "卯"}
    wc = wenchang_map.get(dm, "")
    if wc and wc in all_branches:
        result["day_stem"].append("文昌贵人")

    # ===== 学堂（年干查，十干学堂）=====
    # 子平法：年干对应纳音五行的长生位
    # 金长生在巳（辛巳为正），木长生在亥（己亥为正），
    # 水长生在申（甲申为正），土长生在申（戊申为正），火长生在寅（丙寅为正）
    xuetang_map = {
        "甲": "亥",  # 阳木长生在亥
        "乙": "亥",  # 阴木长生在亥
        "丙": "寅",  # 阳火长生在寅
        "丁": "寅",  # 阴火长生在寅
        "戊": "寅",  # 阳土长生在寅（甲己土同论长生在寅）
        "己": "寅",  # 阴土长生在寅
        "庚": "巳",  # 阳金长生在巳
        "辛": "巳",  # 阴金长生在巳
        "壬": "申",  # 阳水长生在申
        "癸": "申",  # 阴水长生在申
    }
    xt = xuetang_map.get(year_stem, "")
    if xt and xt in all_branches:
        result["year_stem"].append("学堂")

    # ===== 国印贵人（年干查 + 日干查）=====
    # 甲见戌，乙见亥，丙见丑，丁见寅，戊见丑，己见寅，庚见辰，辛见巳，壬见未，癸见申
    guoyin_map = {"甲": "戌", "乙": "亥", "丙": "丑", "丁": "寅",
                  "戊": "丑", "己": "寅", "庚": "辰", "辛": "巳",
                  "壬": "未", "癸": "申"}
    # ===== 国印贵人（年干查 → 标在结果地支所在柱的干位）=====
    # 规则：查法来源与结果地支所在柱不同时，结果标在该柱的干位
    # 例如：年干戊查戌（不在四柱），戌在月柱→标在月干
    gy_ys = guoyin_map.get(year_stem, "")
    if gy_ys:
        # 查找结果地支在四柱中的位置
        found_pos = None
        for b2, pos in branch_positions:
            if gy_ys == b2:
                found_pos = pos
                break
        if found_pos:
            # 结果地支在四柱中，标在该地支所在柱的干位
            stem_pos = found_pos.replace("_branch", "_stem")
            if "国印贵人" not in result[stem_pos]:
                result[stem_pos].append("国印贵人")
        else:
            # 结果地支不在四柱中，标在月支（参考盘风格）
            if "国印贵人" not in result["month_branch"]:
                result["month_branch"].append("国印贵人")
    # 日干查国印：丁日查寅→月在月支→标月支（与年干查结果去重）
    gy_ds = guoyin_map.get(dm, "")
    if gy_ds:
        found_pos = None
        for b2, pos in branch_positions:
            if gy_ds == b2:
                found_pos = pos
                break
        if found_pos:
            if "国印贵人" not in result[found_pos]:
                result[found_pos].append("国印贵人")

    # ===== 金舆（年干查 + 日干查）=====
    # 甲见辰，乙见巳，丙见未，丁见申，戊见未，己见申，庚见戌，辛见亥，壬见丑，癸见寅
    jinyu_map = {"甲": "辰", "乙": "巳", "丙": "未", "丁": "申",
                 "戊": "未", "己": "申", "庚": "戌", "辛": "亥",
                 "壬": "丑", "癸": "寅"}
    # 年干查金舆（参考盘不显示，注释掉）
    # jy_ys = jinyu_map.get(year_stem, "")
    # if jy_ys:
    #     for b2, pos in branch_positions:
    #         if jy_ys == b2 and "金舆" not in result[pos]:
    #             result[pos].append("金舆")
    #             break
    # 日干查金舆（参考盘不显示，注释掉）
    # jy_ds = jinyu_map.get(dm, "")
    # if jy_ds:
    #     for b2, pos in branch_positions:
    #         if jy_ds == b2 and "金舆" not in result[pos]:
    #             result[pos].append("金舆")
    #             break

    # ===== 驿马（年支查 + 日支查）=====
    # 申子辰马在寅，寅午戌马在申，巳酉丑马在亥，亥卯未马在巳
    yima_map = {"寅": "申", "午": "申", "戌": "申",
                "申": "寅", "子": "寅", "辰": "寅",
                "巳": "亥", "酉": "亥", "丑": "亥",
                "亥": "巳", "卯": "巳", "未": "巳"}
    yima_yr = yima_map.get(year_branch, "")
    if yima_yr and yima_yr in all_branches:
        result["year_branch"].append("驿马")
    yima_dr = yima_map.get(day_branch, "")
    if yima_dr and yima_dr in all_branches:
        result["day_branch"].append("驿马")

    # ===== 桃花/咸池（年支查 + 日支查）=====
    # 申子辰在酉，寅午戌在卯，巳酉丑在子，亥卯未在午
    taohua_map = {"寅": "卯", "午": "卯", "戌": "卯",
                  "申": "酉", "子": "酉", "辰": "酉",
                  "巳": "子", "酉": "子", "丑": "子",
                  "亥": "午", "卯": "午", "未": "午"}
    taohua_yr = taohua_map.get(year_branch, "")
    if taohua_yr and taohua_yr in all_branches:
        result["year_branch"].append("桃花")
    taohua_dr = taohua_map.get(day_branch, "")
    if taohua_dr and taohua_dr in all_branches:
        result["day_branch"].append("桃花")

    # ===== 华盖（年支查 + 日支查）=====
    # 申子辰在辰，亥卯未在未，寅午戌在戌，巳酉丑在丑
    sanhe_huagai = {"寅": "戌", "午": "戌", "戌": "戌",
                    "申": "辰", "子": "辰", "辰": "辰",
                    "巳": "丑", "酉": "丑", "丑": "丑",
                    "亥": "未", "卯": "未", "未": "未"}
    hg_yr = sanhe_huagai.get(year_branch, "")
    if hg_yr and hg_yr in all_branches:
        result["year_branch"].append("华盖")
    hg_dr = sanhe_huagai.get(day_branch, "")
    # 华盖去重：若年支已有华盖，日支不再显示（参考盘风格）
    if hg_dr and hg_dr in all_branches and "华盖" not in result["year_branch"]:
        result["day_branch"].append("华盖")

    # ===== 将星（年支查 + 日支查）=====
    jiangxing_map = {"寅": "午", "午": "午", "戌": "午",
                      "申": "子", "子": "子", "辰": "子",
                      "巳": "酉", "酉": "酉", "丑": "酉",
                      "亥": "卯", "卯": "卯", "未": "卯"}
    jx_yr = jiangxing_map.get(year_branch, "")
    if jx_yr and jx_yr in all_branches:
        result["year_branch"].append("将星")
    jx_dr = jiangxing_map.get(day_branch, "")
    if jx_dr and jx_dr in all_branches:
        result["day_branch"].append("将星")

    # ===== 羊刃（日干查）=====
    # 子平真诠：羊刃为帝旺之位（帝旺后退一位即刃）
    # 甲帝旺卯→刃寅，乙帝旺寅→刃卯；丙戊帝旺午→刃巳，丁己帝旺巳→刃午；
    # 庚帝旺酉→刃申，辛帝旺申→刃酉；壬帝旺子→刃亥，癸帝旺亥→刃子
    yangren_map = {"甲": "卯", "乙": "寅", "丙": "午", "丁": "巳",
                   "戊": "午", "己": "巳", "庚": "酉", "辛": "申",
                   "壬": "子", "癸": "亥"}
    yr = yangren_map.get(dm, "")
    if yr:
        for b2, pos in branch_positions:
            if yr == b2 and "羊刃" not in result[pos]:
                result[pos].append("羊刃")
                break

    # ===== 禄神（日干查）=====
    lushen_map = {"甲": "寅", "乙": "卯", "丙": "巳", "丁": "午",
                  "戊": "巳", "己": "午", "庚": "申", "辛": "酉",
                  "壬": "亥", "癸": "子"}
    ls = lushen_map.get(dm, "")
    if ls:
        for b2, pos in branch_positions:
            if ls == b2 and "禄神" not in result[pos]:
                result[pos].append("禄神")
                break

    # ===== 空亡（日柱干支所在旬空亡）=====
    day_60_idx = CYCLE60_INDEX.get(day_stem + day_branch, 0)
    xun_start = (day_60_idx // 10) * 10
    # 本旬中出现的地支
    xun_branches = set()
    for i in range(xun_start, xun_start + 10):
        if i < 60:
            xun_branches.add(EARTHLY_BRANCHES[i % 12])
    # 空亡：本旬没有的地支（恰好2个）
    kong_branches = [EARTHLY_BRANCHES[bi] for bi in range(12) if EARTHLY_BRANCHES[bi] not in xun_branches]
    # 空亡标在「四柱中出现空亡地支」的支位
    # 注意：空亡本身不属于该柱，而是该柱的地支落在空亡列表中
    for label, branch in [("year_branch", year_branch), ("month_branch", month_branch),
                          ("day_branch", day_branch), ("hour_branch", hour_branch)]:
        if branch in kong_branches:
            result[label].append("空亡")

    # ===== 天德贵人（月支查→标月干+月支）=====
    # 规则：查法来源是月支，结果不在月支（在天干位）时，同时标在月干和月支
    # 月支寅→丁（丁=日干）→结果不在月支→标月干+月支
    tiande_map = {"寅": "丁", "卯": "申", "辰": "壬", "巳": "辛",
                  "午": "亥", "未": "甲", "申": "癸", "酉": "寅",
                  "戌": "丙", "亥": "乙", "子": "巳", "丑": "庚"}
    td = tiande_map.get(month_branch, "")
    if td:
        result["month_branch"].append("天德贵人")
        result["month_stem"].append("天德贵人")

    # ===== 月德贵人（月支三合局查→标月干+月支）=====
    # 月支寅三合寅午戌→丙→结果丙不在月支→标月干+月支
    yuede_map = {"寅": "丙", "午": "丙", "戌": "丙",
                 "申": "壬", "子": "壬", "辰": "壬",
                 "巳": "庚", "酉": "庚", "丑": "庚",
                 "亥": "甲", "卯": "甲", "未": "甲"}
    yd = yuede_map.get(month_branch, "")
    if yd:
        result["month_branch"].append("月德贵人")
        result["month_stem"].append("月德贵人")

    # ===== 魁罡（日柱查）=====
    kuigang = ["庚辰", "壬辰", "庚戌", "戊戌"]
    if day_stem + day_branch in kuigang:
        result["day_stem"].append("魁罡")

    # ===== 亡神（年支查 + 日支查）=====
    # 申子辰亡在亥，寅午戌亡在巳，巳酉丑亡在申，亥卯未亡在寅
    wangshen_map = {"寅": "巳", "午": "巳", "戌": "巳",
                    "申": "亥", "子": "亥", "辰": "亥",
                    "巳": "申", "酉": "申", "丑": "申",
                    "亥": "寅", "卯": "寅", "未": "寅"}
    # ===== 亡神（年支查 + 日支查，年支日支同时出现时只显示日支）=====
    # 规则：亡神从年支和日支分别查得，若两者同时存在于四柱，
    # 参考盘只显示日支的亡神（年支的亡神被日支版本"吸收"）
    ws_yr = wangshen_map.get(year_branch, "")
    ws_dr = wangshen_map.get(day_branch, "")
    # 规则：若日支有亡神则显示日支的亡神；若日支没有亡神才考虑年支的亡神
    # 参考盘中年支辰的亡神（亥）不显示，只显示日支未的亡神（寅）
    ws_dr = wangshen_map.get(day_branch, "")
    if ws_dr and ws_dr in all_branches:
        result["day_branch"].append("亡神")
    else:
        ws_yr = wangshen_map.get(year_branch, "")
        if ws_yr and ws_yr in all_branches:
            result["year_branch"].append("亡神")

    # ===== 劫煞（年支查）=====
    # 申子辰劫在巳，寅午戌劫在亥，巳酉丑劫在寅，亥卯未劫在申
    jiesha_map = {"寅": "亥", "午": "亥", "戌": "亥",
                  "申": "巳", "子": "巳", "辰": "巳",
                  "巳": "寅", "酉": "寅", "丑": "寅",
                  "亥": "申", "卯": "申", "未": "申"}
    js = jiesha_map.get(year_branch, "")
    if js and js in all_branches:
        result["year_branch"].append("劫煞")

    # ===== 绞煞（年支查）=====
    # 绞煞是劫煞的对冲位（三命通会）：
    # 劫煞：申子辰→巳，寅午戌→亥，巳酉丑→寅，亥卯未→申
    # 绞煞：取劫煞的地支冲位
    # 申子辰→亥（巳冲亥），寅午戌→巳（亥冲巳），巳酉丑→申（寅冲申），亥卯未→丑（申冲丑）
    jiaosha_map = {"申": "亥", "子": "亥", "辰": "亥",
                   "寅": "巳", "午": "巳", "戌": "巳",
                   "巳": "申", "酉": "申", "丑": "申",
                   "亥": "丑", "卯": "丑", "未": "丑"}
    jiaos = jiaosha_map.get(year_branch, "")
    if jiaos and jiaos in all_branches:
        result["year_branch"].append("绞煞")

    # ===== 元辰（年支查，需性别）=====
    # 阳男阴女：冲前一位；阴男阳女：冲后一位
    # 百度百科+三命通会标准口诀：
    yuanchen_yang_nv = {"子": "未", "丑": "申", "寅": "酉", "卯": "戌",
                        "辰": "亥", "巳": "子", "午": "丑", "未": "寅",
                        "申": "卯", "酉": "辰", "戌": "巳", "亥": "午"}
    yuanchen_yin_nan = {"子": "巳", "丑": "午", "寅": "未", "卯": "申",
                        "辰": "酉", "巳": "戌", "午": "亥", "未": "子",
                        "申": "丑", "酉": "寅", "戌": "卯", "亥": "辰"}
    # 元辰：三命通会"阳男阴女查阳表，阴男阳女查阴表"
    yang_male = is_yang_year and gender in ["男", "男命", "male", "Male", "M"]
    yin_female = not is_yang_year and gender in ["女", "女命", "female", "Female", "F"]
    # 阳男/阴女查阳表（yuanchen_yang_nv），阴男/阳女查阴表（yuanchen_yin_nan）
    if yang_male or yin_female:
        yc = yuanchen_yang_nv.get(year_branch, "")  # 辰→亥
    else:
        yc = yuanchen_yin_nan.get(year_branch, "")  # 辰→酉
    if yc and yc in all_branches:
        for b2, pos in branch_positions:
            if yc == b2 and "元辰" not in result[pos]:
                result[pos].append("元辰")
                break

    # ===== 孤辰寡宿（年支查）=====
    # 渊海子平标准：三合局前一位为孤辰，后一位为寡宿
    # 但"三合局本宫无孤寡"——寅卯辰本宫卯无孤寡，巳午未本宫午无孤寡
    # 修正：本宫年（卯、午、酉、子）及相邻年（寅、辰、巳、未、申、戌、亥、丑）都不应查
    # 实际上，只有"局外"的年份才有孤寡：申酉戌、亥子丑局
    guchen_map = {"申": "申", "酉": "申", "戌": "申",
                   "亥": "亥", "子": "亥", "丑": "亥"}
    guasv_map = {"申": "戌", "酉": "戌", "戌": "戌",
                 "亥": "未", "子": "未", "丑": "未"}
    gc = guchen_map.get(year_branch, "")
    if gc and gc in all_branches:
        result["year_branch"].append("孤辰")
    sv = guasv_map.get(year_branch, "")
    if sv and sv in all_branches:
        result["year_branch"].append("寡宿")

    # ===== 红鸾（年支查）=====
    hongluan_map = {"子": "卯", "丑": "寅", "寅": "丑", "卯": "子",
                    "辰": "亥", "巳": "戌", "午": "酉", "未": "申",
                    "申": "未", "酉": "午", "戌": "巳", "亥": "辰"}
    hl = hongluan_map.get(year_branch, "")
    if hl and hl in all_branches:
        result["year_branch"].append("红鸾")

    # ===== 天喜（年支查，红鸾对冲）=====
    # 渊海子平标准：春喜在戌（寅卯辰→戌），夏喜在亥（巳午未→亥），
    #                 秋喜在子（申酉戌→子），冬喜在丑（亥子丑→丑）
    tianxi_map = {"寅": "戌", "卯": "戌", "辰": "戌",
                  "巳": "亥", "午": "亥", "未": "亥",
                  "申": "子", "酉": "子", "戌": "子",
                  "亥": "丑", "子": "丑", "丑": "丑"}
    tx = tianxi_map.get(year_branch, "")
    if tx and tx in all_branches:
        result["year_branch"].append("天喜")

    # ===== 十二长生（日干查，看四柱地支落在哪个长生位）=====
    # 阳干：甲 丙 戊 庚 壬 — 顺行：长生→沐浴→冠带→临官→帝旺→衰→病→死→墓→绝→胎→养
    # 阴干：乙 丁 己 辛 癸 — 逆行
    yang_cs = ["甲", "丙", "戊", "庚", "壬"]
    is_yang_dm = dm in yang_cs
    # 十二长生地支顺序（阳干顺行）
    cs12_yang = ["亥", "子", "丑", "寅", "卯", "辰",
                 "巳", "午", "未", "申", "酉", "戌"]
    cs12_names = ["长生", "沐浴", "冠带", "临官", "帝旺",
                  "衰", "病", "死", "墓", "绝", "胎", "养"]
    # 阴干逆行起点：午(长生) 巳(沐浴) 辰(冠带) 卯(临官) 寅(帝旺)
    #           丑(衰) 子(病) 亥(死) 戌(墓) 酉(绝) 申(胎) 未(养)
    cs12_yin = ["午", "巳", "辰", "卯", "寅", "丑",
                "子", "亥", "戌", "酉", "申", "未"]
    if is_yang_dm:
        branch_to_state = dict(zip(cs12_yang, cs12_names))
    else:
        branch_to_state = dict(zip(cs12_yin, cs12_names))
    for label, branch in [("year_branch", year_branch), ("month_branch", month_branch),
                          ("day_branch", day_branch), ("hour_branch", hour_branch)]:
        state = branch_to_state.get(branch, "")
        if state:
            result[label].append(state)

    # ===== 天罗地网（年支/日支查）===== 
    # 辰戌为天罗，巳亥为地网，标在出现该地支的位置
    tianluo = ["辰", "戌"]
    diwang = ["巳", "亥"]
    for label, branch in [("year_branch", year_branch), ("month_branch", month_branch),
                          ("day_branch", day_branch), ("hour_branch", hour_branch)]:
        if branch in tianluo and "天罗" not in result[label]:
            result[label].append("天罗")
        if branch in diwang and "地网" not in result[label]:
            result[label].append("地网")

    return result


# ============ 用神/忌神 ============

from typing import Dict, Tuple, List

# 五行生克关系（以某五行为"我"）
# 生我者：我生者循环的逆
# 木生火 → 火生土 → 土生金 → 金生水 → 水生木
# 所以：生我 = 水生木 = 木，木生火 = 火生我 = 火，火生土 = 土生我，土生金 = 金生我，金生水 = 水生我
# 克我：我克循环的逆
# 木克土 → 土克水 → 水克火 → 火克金 → 金克木
# 所以：克我 = 金克木 = 木，土克水 = 水克我，火克金 = 金克我，水克火 = 火克我，土克木 = 木克我

_WX_SHENG = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}  # 生我者
_WX_KEX = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}  # 克我者
_WX_WOKE = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}  # 我克者
_WX_WOSHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}  # 我生者
_WX_TONGWO = {"木": "木", "火": "火", "土": "土", "金": "金", "水": "水"}  # 同我者

# 五行 → 天干映射
_WUXING_TO_STEMS = {
    "木": ["甲", "乙"],
    "火": ["丙", "丁"],
    "土": ["戊", "己"],
    "金": ["庚", "辛"],
    "水": ["壬", "癸"],
}

# 用神/忌神天干计算：给定日主强弱，返回用神天干列表、忌神天干列表
def _calc_yongshen_jishen(day_wx: str, strength: str) -> Tuple[List[str], List[str]]:
    """
    根据日主五行和强弱，返回用神天干列表和忌神天干列表。
    日主强：克我(官杀)、我生(食伤)、我克(财星) 为用神
    日主弱：生我(印绶)、同我(比劫) 为用神
    """
    if strength == "强":
        yongshen_wx = [_WX_KEX[day_wx], _WX_WOSHENG[day_wx], _WX_WOKE[day_wx]]
        jishen_wx = [_WX_SHENG[day_wx], _WX_TONGWO[day_wx]]
    elif strength == "弱":
        yongshen_wx = [_WX_SHENG[day_wx], _WX_TONGWO[day_wx]]
        jishen_wx = [_WX_KEX[day_wx], _WX_WOSHENG[day_wx], _WX_WOKE[day_wx]]
    else:
        return [], []

    # 五行名 → 天干列表
    yongshen_stems = []
    jishen_stems = []
    for wx in yongshen_wx:
        yongshen_stems.extend(_WUXING_TO_STEMS.get(wx, []))
    for wx in jishen_wx:
        jishen_stems.extend(_WUXING_TO_STEMS.get(wx, []))
    return yongshen_stems, jishen_stems

# 十神→五行映射（以日主为中心）
_SHISHEN_WUXING = {
    "比肩": None,    # 同我
    "劫财": None,
    "偏印": None,
    "正印": None,
    "食神": None,
    "伤官": None,
    "正财": None,
    "偏财": None,
    "七杀": None,
    "正官": None,
}

# 日主强弱配置：各天干在十二地支的长生状态
# 用于月令判断
_DAYMASTER_MONTH_STRENGTH = {
    # 甲乙木
    "甲": {"寅": "长生", "卯": "帝旺", "辰": "衰", "巳": "病", "午": "死",
          "未": "墓", "申": "绝", "酉": "胎", "戌": "养", "子": "沐浴",
          "丑": "冠带", "亥": "临官"},
    "乙": {"寅": "长生", "卯": "帝旺", "辰": "衰", "巳": "病", "午": "死",
          "未": "墓", "申": "绝", "酉": "胎", "戌": "养", "子": "沐浴",
          "丑": "冠带", "亥": "临官"},
    # 丙丁火
    "丙": {"寅": "长生", "卯": "沐浴", "辰": "冠带", "巳": "帝旺", "午": "帝旺",
          "未": "衰", "申": "病", "酉": "死", "戌": "墓", "子": "绝",
          "丑": "胎", "亥": "养"},
    "丁": {"寅": "长生", "卯": "沐浴", "辰": "冠带", "巳": "临官", "午": "帝旺",
          "未": "衰", "申": "病", "酉": "死", "戌": "墓", "子": "绝",
          "丑": "胎", "亥": "养"},
    # 戊己土
    "戊": {"寅": "病", "卯": "死", "辰": "墓", "巳": "长生", "午": "帝旺",
          "未": "帝旺", "申": "衰", "酉": "病", "戌": "衰", "子": "绝",
          "丑": "墓", "亥": "养"},
    "己": {"寅": "病", "卯": "死", "辰": "墓", "巳": "长生", "午": "帝旺",
          "未": "帝旺", "申": "衰", "酉": "病", "戌": "墓", "子": "绝",
          "丑": "墓", "亥": "养"},
    # 庚辛金
    "庚": {"寅": "绝", "卯": "胎", "辰": "养", "巳": "死", "午": "病",
          "未": "衰", "申": "长生", "酉": "帝旺", "戌": "衰", "子": "沐浴",
          "丑": "冠带", "亥": "临官"},
    "辛": {"寅": "绝", "卯": "胎", "辰": "养", "巳": "死", "午": "病",
          "未": "衰", "申": "长生", "酉": "帝旺", "戌": "养", "子": "沐浴",
          "丑": "冠带", "亥": "临官"},
    # 壬癸水
    "壬": {"寅": "泻", "卯": "死", "辰": "墓", "巳": "绝", "午": "胎",
          "未": "养", "申": "病", "酉": "死", "戌": "墓", "子": "帝旺",
          "丑": "衰", "亥": "长生"},
    "癸": {"寅": "泻", "卯": "死", "辰": "墓", "巳": "绝", "午": "胎",
          "未": "养", "申": "病", "酉": "死", "戌": "墓", "子": "临官",
          "丑": "衰", "亥": "长生"},
}

# 月令旺相判断阈值
_MONTH_BRANCH_FAVORABLE = {"长生", "帝旺", "临官", "冠带", "衰"}
_MONTH_BRANCH_UNFAVORABLE = {"死", "绝", "墓", "病", "泻"}


def _get_day_master_strength_from_bazi(bazi_dict: dict, day_master: str) -> str:
    """
    根据命局数据计算日主强弱
    依据：
    1. 天干地支中同我/生我五行数量
    2. 月令是否得令（地支藏干本气是否与日主同五行）
    """
    day_wx = WU_XING_MAP.get(day_master, "")
    if not day_wx:
        return "中和"

    # 统计天干中同我/生我的数量
    all_stems = [
        bazi_dict["year_pillar"]["stem"],
        bazi_dict["month_pillar"]["stem"],
        bazi_dict["day_pillar"]["stem"],
        bazi_dict["hour_pillar"]["stem"],
    ]
    # 统计地支藏干中的本气
    all_branches = [
        bazi_dict["year_pillar"]["branch"],
        bazi_dict["month_pillar"]["branch"],
        bazi_dict["day_pillar"]["branch"],
        bazi_dict["hour_pillar"]["branch"],
    ]

    # 天干同/生我数量
    count_from_stems = 0
    for s in all_stems:
        s_wx = WU_XING_MAP.get(s, "")
        if s_wx == day_wx:  # 同我
            count_from_stems += 1
        elif s_wx in _WX_SHENG:  # 生我
            count_from_stems += 1

    # 地支藏干本气（权重0.6）+ 月令判断
    month_branch = bazi_dict["month_pillar"]["branch"]
    hidden = BRANCH_HIDDEN_STEMS.get(month_branch, [])
    branch_benqi_wx = WU_XING_MAP.get(hidden[0], "") if hidden else ""

    count_from_branch = 0
    if branch_benqi_wx == day_wx:
        count_from_branch = 1.0  # 月支本气同我（子平法：本气权重最高）
    elif branch_benqi_wx in _WX_SHENG:
        count_from_branch = 0.5  # 月支本气生我（中气得令权重）

    # 月令得令判断（十二长生）
    month_branch_state = _DAYMASTER_MONTH_STRENGTH.get(day_master, {}).get(month_branch, "")
    month_favorable = month_branch_state in _MONTH_BRANCH_FAVORABLE
    month_unfavorable = month_branch_state in _MONTH_BRANCH_UNFAVORABLE

    total = count_from_stems + count_from_branch

    # 得令加0.5，失令减0.5
    if month_favorable:
        total += 0.5
    elif month_unfavorable:
        total -= 0.5

    if total >= 3.0:
        return "强"
    elif total <= 1.5:
        return "弱"
    else:
        return "中和"


def _get_conflict_pairs() -> Dict[Tuple[str, str], str]:
    """返回真正相战的克对及通关用神映射。
    仅包含五行相克关系（同层相克），不含反向（反向即生助，无战）。
    通关：木克土→水通关，水克火→木通关，火克金→土通关，金克木→水通关。
    """
    # 克：木克土, 土克水, 水克火, 火克金, 金克木
    return {
        ("木", "土"): "水",  # 木克土 → 水通关
        ("土", "水"): "木",  # 土克水 → 木通关
        ("水", "火"): "木",  # 水克火 → 木通关
        ("火", "金"): "土",  # 火克金 → 土通关
        ("金", "木"): "水",  # 金克木 → 水通关
    }


def _is_stem_of_wuxing(stems: List[str], target_wx: str) -> bool:
    """检查干支列表中是否包含某五行"""
    for s in stems:
        if WU_XING_MAP.get(s) == target_wx:
            return True
    return False


def _collect_visible_wuxing(bazi_dict: dict) -> Dict[str, bool]:
    """
    收集命局中各五行是否在四柱天干中出现（仅看天干，不含地支/藏干）。
    避免将地支(如辰=土)误判为天干导致的错误。
    """
    result = {wx: False for wx in ["金", "木", "水", "火", "土"]}
    ten_stems = set(HEAVENLY_STEMS)  # {"甲","乙",...,"癸"}
    for pillar in ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]:
        stem = bazi_dict[pillar]["stem"]
        # 只处理天干（戊、庚等），排除地支
        if stem not in ten_stems:
            continue
        wx = WU_XING_MAP.get(stem, "")
        if wx and wx in result:
            result[wx] = True
    return result


def determine_yongshen(bazi_dict: dict, day_master: str, day_master_strength: str = None) -> dict:
    """
    判定用神/忌神

    Args:
        bazi_dict: 四柱数据（calculate_bazi返回的result）
        day_master: 日主天干
        day_master_strength: 日主强弱字符串（"强"/"弱"/"中和"），
                             若为None则自动从bazi_dict计算

    Returns:
        {
            "yongshen": ["壬", "庚"],    # 用神天干列表
            "jishen": ["甲", "乙", "丁"],  # 忌神天干列表
            "tiaohou": [],              # 调候用神（预留）
            "tongguan": [],             # 通关用神（预留）
            "type": "扶抑",
            "strength_auto": "强",      # 自动计算的强弱
            "desc": "..."
        }
    """
    day_wx = WU_XING_MAP.get(day_master, "")
    if not day_wx:
        return {"yongshen": [], "jishen": [], "type": "未知",
                "strength_auto": "未知", "desc": "无法判定",
                "tiaohou": [], "tongguan": []}

    # 若未提供强弱，自动计算
    if day_master_strength is None:
        strength = _get_day_master_strength_from_bazi(bazi_dict, day_master)
    else:
        strength = day_master_strength

    # 扶抑用神
    if strength == "强":
        # 日主强：用神为克/泄/耗（官杀、食伤、财星）
        yongshen, jishen = _calc_yongshen_jishen(day_wx, strength)
        desc = f"日主{day_master}（{day_wx}）身强，宜克、泄、耗以制衡。用神：官杀、食伤、财星；忌神：印绶、比劫。"
    elif strength == "弱":
        # 日主弱：用神为生/扶（印绶、比劫）
        yongshen, jishen = _calc_yongshen_jishen(day_wx, strength)
        desc = f"日主{day_master}（{day_wx}）身弱，宜生、扶以增强。用神：印绶、比劫；忌神：官杀、食伤、财星。"
    else:  # 中和
        yongshen, jishen = [], []
        desc = f"日主{day_master}（{day_wx}）中和，用神忌神不明显，需结合格局综合判定（预留）。"

    result = {
        "yongshen": yongshen,
        "jishen": jishen,
        "type": "扶抑",
        "strength_auto": strength,
        "desc": desc,
        "tiaohou": [],   # 调候用神（预留接口，后续可接入穷通宝鉴）
        "tongguan": [],  # 通关用神（见下方增强）
    }

    # ============ 通关用神增强 ============
    # 检查命局中是否有两行相战（仅看天干，不含藏干，避免误判）
    wx_visible = _collect_visible_wuxing(bazi_dict)
    conflict_map = _get_conflict_pairs()
    tongguan = []

    for (wx1, wx2), tg_wx in conflict_map.items():
        has_wx1 = wx_visible.get(wx1, False)
        has_wx2 = wx_visible.get(wx2, False)
        if has_wx1 and has_wx2 and tg_wx not in tongguan:
            tongguan.append(tg_wx)
            result["desc"] += f" 命局{wx1}与{wx2}相战，{tg_wx}通关。"

    if tongguan:
        result["tongguan"] = tongguan
        result["type"] = "扶抑+通关"

    return result


# ============ 旺衰 ============

def calculate_wangshuai(day_stem: str, branch: str) -> str:
    """十二长生查表"""
    dm_wx = wuxing(day_stem)
    dm_yy = yinyang(day_stem)
    if dm_yy == "阳":
        table = TWELVE_LIFECYCLE_YANG.get(dm_wx, {})
    else:
        table = TWELVE_LIFECYCLE_YIN.get(dm_wx, {})
    return table.get(branch, "未知")


# ============ 胎元、命宫、身宫 ============

def get_taiyuan(month_stem: str, month_branch: str) -> Tuple[str, str]:
    stem_idx = STEM_INDEX[month_stem]
    branch_idx = BRANCH_INDEX[month_branch]
    return (HEAVENLY_STEMS[(stem_idx + 3) % 10],
            EARTHLY_BRANCHES[(branch_idx + 3) % 12])


def get_minggong(year_stem: str, month_branch: str, hour_branch: str) -> Tuple[str, str]:
    """命宫地支推算：以寅=1编号，14-(月支+时支)，超过14则用26减"""
    # 寅=1, 卯=2, ..., 子=11, 丑=12 的编号
    branch_yin_num = {"寅": 1, "卯": 2, "辰": 3, "巳": 4, "午": 5, "未": 6,
                     "申": 7, "酉": 8, "戌": 9, "亥": 10, "子": 11, "丑": 12}
    m_num = branch_yin_num.get(month_branch, 1)
    h_num = branch_yin_num.get(hour_branch, 1)
    total = m_num + h_num
    if total < 14:
        mg_num = 14 - total
    else:
        mg_num = 26 - total
    # 将编号转回地支（寅=1,...丑=12）
    num_to_branch = {v: k for k, v in branch_yin_num.items()}
    mg_branch = num_to_branch.get(mg_num, "寅")
    # 命宫天干：以年干按五虎遁（年起月法）推出
    yin_stem = MONTH_STEM_START.get(year_stem, "甲")
    yin_stem_idx = STEM_INDEX[yin_stem]
    mg_branch_idx = BRANCH_INDEX[mg_branch]
    mg_stem_idx = (yin_stem_idx + mg_branch_idx - 2) % 10  # 寅=2在EARTHLY_BRANCHES中
    mg_stem = HEAVENLY_STEMS[mg_stem_idx]
    return mg_stem, mg_branch


def get_shengong(year_stem: str, month_branch: str, hour_branch: str) -> Tuple[str, str]:
    """身宫地支推算：子上起正月顺推到生月，时支落生月上逆推到酉"""
    # 身宫地支 = (月支 + 时支 + 2) % 12 （简化公式，等价于子上起正月法）
    midx = BRANCH_INDEX[month_branch]
    hidx = BRANCH_INDEX[hour_branch]
    sg_idx = (midx + hidx + 2) % 12
    sg_branch = EARTHLY_BRANCHES[sg_idx]
    # 身宫天干：以年干按五虎遁推出
    yin_stem = MONTH_STEM_START.get(year_stem, "甲")
    yin_stem_idx = STEM_INDEX[yin_stem]
    sg_branch_idx = BRANCH_INDEX[sg_branch]
    sg_stem_idx = (yin_stem_idx + sg_branch_idx - 2) % 10  # 寅=2在EARTHLY_BRANCHES中
    sg_stem = HEAVENLY_STEMS[sg_stem_idx]
    return sg_stem, sg_branch


# ============ 穷通宝鉴调候用神 ============

def determine_hannuan_zaoshi(month_branch: str, bazi_dict: dict = None) -> dict:
    """
    判定命局寒暖燥湿
    
    Args:
        month_branch: 月支
        bazi_dict: 四柱干支（备用，当前按月令判定）
    
    Returns:
        {"hannuan": "寒"/"暖"/"平", "zaoshi": "燥"/"湿"/"平", "desc": "..."}
    """
    # 寒暖判定
    cold_months = {"亥", "子", "丑"}  # 冬
    hot_months = {"巳", "午", "未"}  # 夏
    spring_cold = {"寅"}  # 初春尚寒
    
    if month_branch in cold_months:
        hannuan = "寒"
    elif month_branch in hot_months:
        hannuan = "暖"
    elif month_branch in spring_cold:
        hannuan = "寒"  # 初春仍寒
    else:
        hannuan = "平"
    
    # 燥湿判定（仅辰戌丑未土月）
    wet_months = {"辰", "丑"}  # 湿土
    dry_months = {"戌", "未"}   # 燥土
    
    if month_branch in wet_months:
        zaoshi = "湿"
    elif month_branch in dry_months:
        zaoshi = "燥"
    else:
        zaoshi = "平"
    
    # 描述
    month_name = month_branch + "月"
    hannuan_desc = _HANNUAN_DESC[hannuan].format(month=month_branch) if hannuan != "平" else _HANNUAN_DESC["平"].format(month=month_branch)
    zaoshi_desc = _ZAOSHI_DESC[zaoshi].format(month=month_name) if zaoshi != "平" else ""
    
    parts = []
    if hannuan_desc:
        parts.append(hannuan_desc)
    if zaoshi_desc:
        parts.append(zaoshi_desc)
    desc = "；".join(parts) if parts else f"生于{month_branch}月，寒暖燥湿适中"
    
    return {"hannuan": hannuan, "zaoshi": zaoshi, "desc": desc}


def determine_tiaohou(bazi_dict: dict, day_master: str, month_branch: str) -> dict:
    """
    判定调候用神（穷通宝鉴）
    
    Args:
        bazi_dict: 四柱干支字典
        day_master: 日主天干
        month_branch: 月支地支
    
    Returns:
        {
            "tiaohou_yongshen": ["丙", "癸"],
            "hannuan": "寒",
            "zaoshi": "湿",
            "desc": "生于寅月，木寒，需丙火温暖为先"
        }
    """
    # 查表获取调候用神
    month_data = TIAOHOU_TABLE.get(month_branch, {})
    tiaohou_yongshen = month_data.get(day_master, [])
    
    # 寒暖燥湿判定
    hannuan_zaoshi = determine_hannuan_zaoshi(month_branch, bazi_dict)
    
    # 生成描述
    tiaohou_desc = _TIAOHOU_DESC.get(month_branch, {}).get(day_master, "")
    hannuan_desc = hannuan_zaoshi["desc"]
    
    if tiaohou_desc and hannuan_desc:
        desc = f"{hannuan_desc}。{day_master}日主：{tiaohou_desc}"
    elif tiaohou_desc:
        desc = f"{day_master}日主生于{month_branch}月：{tiaohou_desc}"
    elif hannuan_desc:
        desc = hannuan_desc
    else:
        desc = f"{day_master}日主生于{month_branch}月"
    
    return {
        "tiaohou_yongshen": tiaohou_yongshen,
        "hannuan": hannuan_zaoshi["hannuan"],
        "zaoshi": hannuan_zaoshi["zaoshi"],
        "desc": desc,
    }


# ============ 主入口 ============

def calculate_bazi(
    year: int, month: int, day: int,
    hour: int, minute: int = 0,
    gender: str = "男",
    use_true_solar: bool = False,
    true_solar_adjustment: int = 0,
) -> dict:
    """
    四柱八字排盘主函数
    """
    # 真太阳时调整
    adj_hour = hour
    adj_minute = minute
    adj_day = day
    adj_month = month
    adj_year = year
    
    if use_true_solar and true_solar_adjustment != 0:
        total_min = hour * 60 + minute + true_solar_adjustment
        # 处理跨日情况
        if total_min < 0:
            # 跨到前一天
            total_min += 1440
            adj_day -= 1
            if adj_day < 1:
                adj_month -= 1
                if adj_month < 1:
                    adj_month = 12
                    adj_year -= 1
                # 获取上月天数
                import calendar
                adj_day = calendar.monthrange(adj_year, adj_month)[1]
        elif total_min >= 1440:
            # 跨到后一天
            total_min -= 1440
            adj_day += 1
            import calendar
            max_day = calendar.monthrange(adj_year, adj_month)[1]
            if adj_day > max_day:
                adj_day = 1
                adj_month += 1
                if adj_month > 12:
                    adj_month = 1
                    adj_year += 1
        adj_hour = total_min // 60
        adj_minute = total_min % 60

    # 1. 年柱（考虑立春）
    year_stem, year_branch = get_year_pillar(adj_year, adj_month, adj_day)

    # 2. 月柱（节气为界）
    month_stem, month_branch = get_month_pillar(year_stem, adj_year, adj_month, adj_day)

    # 3. 日柱
    day_stem, day_branch = get_day_pillar(adj_year, adj_month, adj_day)

    # 4. 时柱（处理早晚子时）
    # 早子时 (00:00-00:59) 需用前一日日干推五鼠遁
    use_prev_day = is_early_zi_hour(adj_hour, adj_minute)
    hour_stem, hour_branch = get_hour_pillar(day_stem, adj_hour, adj_minute, use_prev_day)

    # 日主
    day_master = day_stem

    def make_pillar(stem, branch) -> dict:
        return {
            "stem": stem, "branch": branch,
            "hidden_stems": BRANCH_HIDDEN_STEMS.get(branch, []),
            "wuxing": wuxing(stem), "yinyang": yinyang(stem),
        }

    def make_shishen(target_stem: str) -> dict:
        return {
            "stem": target_stem, "target": day_master,
            "shishen": get_shishen(day_master, target_stem),
            "wuxing": wuxing(target_stem),
        }

    # 大运
    dayun_result = calculate_dayun(
        year_stem, month_stem, month_branch,
        year, month, day, gender,
        day_master=day_master
    )

    # 神煞
    shensha = calculate_shensha(
        year_stem, year_branch, month_stem, month_branch,
        day_stem, day_branch, hour_stem, hour_branch,
        gender=gender
    )

    # 旺衰
    wangshuai_month = calculate_wangshuai(day_stem, month_branch)
    wangshuai_year = calculate_wangshuai(day_stem, year_branch)
    wangshuai_day = calculate_wangshuai(day_stem, day_branch)
    wangshuai_hour = calculate_wangshuai(day_stem, hour_branch)

    # 用神/忌神（自动计算强弱 + 扶抑判定）
    bazi_for_yongshen = {
        "year_pillar": make_pillar(year_stem, year_branch),
        "month_pillar": make_pillar(month_stem, month_branch),
        "day_pillar": make_pillar(day_stem, day_branch),
        "hour_pillar": make_pillar(hour_stem, hour_branch),
    }
    yongshen_result = determine_yongshen(bazi_for_yongshen, day_master)

    # 格局判定（子平真诠核心）
    bazi_dict_for_geju = {
        "year_stem": year_stem, "year_branch": year_branch,
        "month_stem": month_stem, "month_branch": month_branch,
        "day_stem": day_stem, "day_branch": day_branch,
        "hour_stem": hour_stem, "hour_branch": hour_branch,
    }
    geju_result = determine_geju(bazi_dict_for_geju, day_master)

    result = {
        "year_pillar": make_pillar(year_stem, year_branch),
        "month_pillar": make_pillar(month_stem, month_branch),
        "day_pillar": make_pillar(day_stem, day_branch),
        "hour_pillar": make_pillar(hour_stem, hour_branch),
        "day_master": day_master,
        "day_master_wuxing": wuxing(day_master),
        "day_master_yinyang": yinyang(day_master),
        "year_shishen": make_shishen(year_stem),
        "month_shishen": make_shishen(month_stem),
        "hour_shishen": make_shishen(hour_stem),
        "year_nayin": get_nayin(year_stem, year_branch),
        "month_nayin": get_nayin(month_stem, month_branch),
        "day_nayin": get_nayin(day_stem, day_branch),
        "hour_nayin": get_nayin(hour_stem, hour_branch),
        "taiyuan": make_pillar(*get_taiyuan(month_stem, month_branch)),
        "minggong": make_pillar(*get_minggong(year_stem, month_branch, hour_branch)),
        "shengong": make_pillar(*get_shengong(year_stem, month_branch, hour_branch)),
        "dayun": dayun_result,
        "shensha": shensha,
        "wangshuai": {
            "year": wangshuai_year, "month": wangshuai_month,
            "day": wangshuai_day, "hour": wangshuai_hour,
        },
        "geju": geju_result,  # 格局判定结果
        "yongshen": yongshen_result,  # 用神/忌神
        "tiaohou": determine_tiaohou(bazi_for_yongshen, day_master, month_branch),  # 调候用神
    }
    return result


def parse_birth_time(time_str: str) -> Tuple[int, int]:
    parts = time_str.split(":")
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0
    return hour, minute


# ============ 命理解读分析 ============

def generate_analysis_report(bazi_result: dict) -> dict:
    """
    基于八字生成通俗易懂的命理解读报告
    风格：说人话，不掉书袋，让普通人都能看懂
    """
    year_stem = bazi_result["year_pillar"]["stem"]
    year_branch = bazi_result["year_pillar"]["branch"]
    month_stem = bazi_result["month_pillar"]["stem"]
    month_branch = bazi_result["month_pillar"]["branch"]
    day_stem = bazi_result["day_pillar"]["stem"]
    day_branch = bazi_result["day_pillar"]["branch"]
    hour_stem = bazi_result["hour_pillar"]["stem"]
    hour_branch = bazi_result["hour_pillar"]["branch"]

    day_master = bazi_result["day_master"]
    day_master_wuxing = bazi_result["day_master_wuxing"]
    day_master_yinyang = bazi_result["day_master_yinyang"]

    wuxing_counts = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    pillars_stems = [year_stem, month_stem, day_stem, hour_stem]
    pillars_branches = [year_branch, month_branch, day_branch, hour_branch]

    for stem in pillars_stems:
        wx = WU_XING_MAP.get(stem, "")
        if wx:
            wuxing_counts[wx] += 1

    for branch in pillars_branches:
        hidden = BRANCH_HIDDEN_STEMS.get(branch, [])
        if hidden:
            wx = WU_XING_MAP.get(hidden[0], "")
            if wx:
                wuxing_counts[wx] += 0.6
            if len(hidden) > 1:
                wx = WU_XING_MAP.get(hidden[1], "")
                if wx:
                    wuxing_counts[wx] += 0.3
            if len(hidden) > 2:
                wx = WU_XING_MAP.get(hidden[2], "")
                if wx:
                    wuxing_counts[wx] += 0.1

    day_wx = day_master_wuxing
    day_count = sum(1 for s in pillars_stems if WU_XING_MAP.get(s) == day_wx)
    day_count += sum(0.6 for b in pillars_branches if b == month_branch and BRANCH_HIDDEN_STEMS.get(b, []) and WU_XING_MAP.get(BRANCH_HIDDEN_STEMS[b][0]) == day_wx)

    strength = "中和"
    if day_count >= 3:
        strength = "偏强"
    elif day_count <= 1.5:
        strength = "偏弱"

    year_nayin = bazi_result.get("year_nayin", "")
    month_nayin = bazi_result.get("month_nayin", "")
    day_nayin = bazi_result.get("day_nayin", "")

    strongest = max(wuxing_counts.items(), key=lambda x: x[1])
    weakest = min(wuxing_counts.items(), key=lambda x: x[1])

    overview = (
        f"你的命盘属于「{day_nayin}」，日主是{day_stem}（{day_master_yinyang}{day_wx}）。\n\n"
        f"年柱：{year_stem}{year_branch}，纳音{year_nayin}\n"
        f"月柱：{month_stem}{month_branch}，纳音{month_nayin}\n"
        f"日柱：{day_stem}{day_branch}，纳音{day_nayin}\n"
        f"时柱：{hour_stem}{hour_branch}\n\n"
        f"五行分布：木 {wuxing_counts['木']:.1f}分　火 {wuxing_counts['火']:.1f}分　土 {wuxing_counts['土']:.1f}分　金 {wuxing_counts['金']:.1f}分　水 {wuxing_counts['水']:.1f}分\n\n"
        f"整体来看，你的命属于「{strength}」，五行中{strongest[0]}最旺（{strongest[1]:.1f}分），{weakest[0]}最弱（{weakest[1]:.1f}分）。"
    )

    day_master_tips = {
        "甲": "甲木就像一棵大树，天生有上进心、责任心强，喜欢被人需要。性格直爽，但有时候过于固执。",
        "乙": "乙木就像花草藤蔓，性格温柔随和，适应能力强，善于变通。外表柔弱，内心有自己的坚持。",
        "丙": "丙火就像太阳，热情开朗，爱表现，有领导力。但也容易三分钟热度，脾气来得快去得也快。",
        "丁": "丁火就像蜡烛灯光，外冷内热，善于观察细节，第六感很强。适合做顾问、策划这类幕后工作。",
        "戊": "戊土就像城墙泥土，为人稳重厚道，讲信用，靠得住。但有时候想法比较保守，不够灵活。",
        "己": "己土就像田园泥土，性格包容谦让，善于协调关系，适合做行政、人事这类需要耐心的工作。",
        "庚": "庚金就像刀斧矿石，性格刚毅果断，立场坚定，认准的事不容易改变。有魄力，适合创业或管理。",
        "辛": "辛金就像珠玉首饰，精致细腻，追求完美，善于审美和打磨。适合做设计、精品类的工作。",
        "壬": "壬水就像江河湖海，性格豪放洒脱，善于变通，适应力强。想法多，点子多，但有时候不够专注。",
        "癸": "癸水就像雨露清泉，性格柔和内敛，直觉敏锐，善于思考。适合做研究、分析这类需要沉下心的工作。",
    }

    strength_desc = "身强" if "强" in strength else "身弱" if "弱" in strength else "中和"
    day_analysis = day_master_tips.get(day_stem, f"{day_stem}属于{day_wx}。")
    day_analysis += f"\n\n你的日主{day_stem}是{day_master_yinyang}{day_wx}，整体{strength_desc}。"

    if strength == "偏强":
        day_analysis += "\n身强说明你本身能量充足，精力充沛，面对压力也能扛得住。不过要注意别太自我，多听听别人的意见。"
    elif strength == "偏弱":
        day_analysis += "\n身弱说明你本身能量偏弱，容易受外界影响，需要借助外力来增强自己。多关注健康，学会借力。"
    else:
        day_analysis += "\n你的能量比较平衡，既不会太激进也不会太消极，适应能力不错。"

    wuxing_analysis_lines = [
        "你的命里五行分布如下：",
        "",
        f"木 {wuxing_counts['木']:.1f}分 | 火 {wuxing_counts['火']:.1f}分 | 土 {wuxing_counts['土']:.1f}分 | 金 {wuxing_counts['金']:.1f}分 | 水 {wuxing_counts['水']:.1f}分",
        "",
    ]

    wx_desc = {
        "木": "木代表生发、成长，对应肝胆、手脚、头发，也代表学业、思考能力。",
        "火": "火代表热情、活力，对应心脏、眼睛、血液循环，也代表表达能力、人际交往。",
        "土": "土代表稳重、承载，对应脾胃、皮肤、肌肉，也代表信用、踏实程度。",
        "金": "金代表刚毅、决断，对应肺、大肠、呼吸系统，也代表魄力、行动力。",
        "水": "水代表智慧、流动，对应肾、膀胱、水液系统，也代表思维能力、适应能力。",
    }

    for wx_name in ["木", "火", "土", "金", "水"]:
        score = wuxing_counts[wx_name]
        if score >= 3.0:
            wuxing_analysis_lines.append(f"▸ {wx_name}很旺（{score:.1f}分）：这个方面你天赋很强，但也可能过犹不及。{wx_desc[wx_name]}")
        elif score >= 2.0:
            wuxing_analysis_lines.append(f"▸ {wx_name}偏旺（{score:.1f}分）：这个方面你条件不错，可以发挥优势。{wx_desc[wx_name]}")
        elif score >= 1.0:
            wuxing_analysis_lines.append(f"▸ {wx_name}一般（{score:.1f}分）：基本够用，但没太多余力。{wx_desc[wx_name]}")
        else:
            wuxing_analysis_lines.append(f"▸ {wx_name}偏弱（{score:.1f}分）：这是你的短板，需要注意补足。{wx_desc[wx_name]}")

    wuxing_analysis_lines.extend(["", "命局中五行生克关系："])

    if wuxing_counts["木"] > 0 and wuxing_counts["火"] > 0:
        rel = "木能生火，你的木可以助旺火。" if wuxing_counts["木"] >= wuxing_counts["火"] else "木生火，但你的火相对更旺，木的力量被火消耗。"
        wuxing_analysis_lines.append(f"  • 木生火：{rel}")

    if wuxing_counts["火"] > 0 and wuxing_counts["土"] > 0:
        rel = "火能生土，你的火可以滋养土。" if wuxing_counts["火"] >= wuxing_counts["土"] else "火生土，但土相对更旺。"
        wuxing_analysis_lines.append(f"  • 火生土：{rel}")

    if wuxing_counts["土"] > 0 and wuxing_counts["金"] > 0:
        rel = "土能生金，你的土可以孕育金。" if wuxing_counts["土"] >= wuxing_counts["金"] else "土生金，但金相对更旺。"
        wuxing_analysis_lines.append(f"  • 土生金：{rel}")

    if wuxing_counts["金"] > 0 and wuxing_counts["水"] > 0:
        rel = "金能生水，你的金可以流通成水。" if wuxing_counts["金"] >= wuxing_counts["水"] else "金生水，但水相对更旺。"
        wuxing_analysis_lines.append(f"  • 金生水：{rel}")

    if wuxing_counts["水"] > 0 and wuxing_counts["木"] > 0:
        rel = "水能生木，你的水可以滋养木。" if wuxing_counts["水"] >= wuxing_counts["木"] else "水生木，但木相对更旺。"
        wuxing_analysis_lines.append(f"  • 水生木：{rel}")

    if strongest[1] - weakest[1] >= 2.5:
        wuxing_analysis_lines.append(f"\n五行平衡的关键在于各元素互相配合。你的命里{strongest[0]}和{weakest[0]}差距较大，需要特别注意补足{weakest[0]}，让五行流转更顺畅。")

    wuxing_analysis = "\n".join(wuxing_analysis_lines)

    year_shishen = bazi_result.get("year_shishen", {})
    month_shishen = bazi_result.get("month_shishen", {})
    hour_shishen = bazi_result.get("hour_shishen", {})

    year_ss = year_shishen.get("shishen", "比肩") if year_shishen else "比肩"
    month_ss = month_shishen.get("shishen", "比肩") if month_shishen else "比肩"
    hour_ss = hour_shishen.get("shishen", "比肩") if hour_shishen else "比肩"

    shishen_tips = {
        "比肩": "代表兄弟姐妹、同事、合作伙伴，也是你的竞争者。比肩旺的人独立性很强，喜欢自己干，不太擅长依靠别人。",
        "劫财": "代表兄弟姐妹，也代表破财、竞争。劫财旺的人敢冲敢闯，但容易因为朋友或投资破财。",
        "食神": "代表才华、技艺、创意，也代表口福、享受。食神旺的人脑子灵光，动手能力强，适合做技术或创意工作。",
        "伤官": "代表才华、创新、不服管教。伤官旺的人想法独特，不喜欢被束缚，适合自由职业或创业。",
        "偏财": "代表意外之财、投资、男命的桃花（妻子以外的女性缘分）。偏财旺的人敢于冒险，理财能力强。",
        "正财": "代表正当收入、稳定的工作、男命的妻子（老婆）。正财旺的人脚踏实地，靠勤劳致富。",
        "偏官": "代表压力、挑战、魄力，男命的女儿。偏官旺的人有冲劲，但要注意压力太大时学会放松。",
        "正官": "代表正当事业、官职、贵人，男命的儿子。正官旺的人有责任心，适合走正道、当领导。",
        "偏印": "代表继母、偏门学问、钻研能力。偏印旺的人善于思考、有悟性，但有时候想太多。",
        "正印": "代表文凭、母亲、证书、靠山。正印旺的人学业运好，容易得到贵人帮助。",
    }

    shishen_lines = [
        "十神是你命里的社会角色，它们代表了你与周围世界的互动方式。",
        "",
        f"年柱{year_stem}：{year_ss}",
        f"月柱{month_stem}：{month_ss}",
        f"时柱{hour_stem}：{hour_ss}",
        "",
    ]

    all_shishen = list(dict.fromkeys([year_ss, month_ss, hour_ss]))
    for ss in all_shishen:
        if ss in shishen_tips:
            shishen_lines.append(f"【{ss}】{shishen_tips[ss]}")

    has_pianyin = False
    has_shishen_flag = False
    for stem in pillars_stems:
        ss = SHISHEN_MAP.get(day_master, {}).get(stem, "")
        if ss == "偏印":
            has_pianyin = True
        if ss in ["食神", "伤官"]:
            has_shishen_flag = True

    if has_pianyin and has_shishen_flag:
        shishen_lines.extend([
            "",
            "特别提醒：你的命里有「枭神夺食」的组合（偏印和食神同时出现）。",
            "这种情况意味着你的才华和福气容易受到压制，可能会怀才不遇，或者在重要场合发挥失常。",
            "解决方法是多靠自己的努力去争取机会，不要太依赖别人的认可。",
        ])

    shishen_analysis = "\n".join(shishen_lines)

    # 财运
    wealth_lines = ["财运分析", ""]
    cai_list = []
    for stem in pillars_stems:
        ss = SHISHEN_MAP.get(day_master, {}).get(stem, "")
        if ss in ["正财", "偏财"]:
            cai_list.append((stem, ss))

    if cai_list:
        for stem, ss_type in cai_list:
            if ss_type == "正财":
                wealth_lines.append(f"• 正财{stem}：代表你靠正常工作赚到的钱，收入稳定，是你的财库来源。")
            else:
                wealth_lines.append(f"• 偏财{stem}：代表投资理财、意外之财，也代表你的财源门路比较广。")
        wealth_lines.append("")
        wealth_lines.append("有财星透出，说明你这辈子不缺钱花，财运基础不错。")
    else:
        wealth_lines.append("你的命里正偏财都不明显，财运需要靠大运来引动。")
        wealth_lines.append("这种情况下，努力工作、提升技能是你最主要的来财方式。")

    if strength == "偏强":
        wealth_lines.append("身强能担财，你赚钱的动力和能力都比较强。")
    elif strength == "偏弱":
        wealth_lines.append("身弱的话，赚了钱要注意存下来，别大手大脚。")
    else:
        wealth_lines.append("身中和，财运平稳，属于细水长流的类型。")

    wealth = "\n".join(wealth_lines)

    # 事业
    career_lines = ["事业分析", ""]
    guan_list = []
    for stem in pillars_stems:
        ss = SHISHEN_MAP.get(day_master, {}).get(stem, "")
        if ss in ["正官", "偏官"]:
            guan_list.append((stem, ss))

    if guan_list:
        for stem, ss_type in guan_list:
            if ss_type == "正官":
                career_lines.append(f"• 正官{stem}：代表正当的事业平台、有编制的职位、正规的发展路径。")
            else:
                career_lines.append(f"• 七杀{stem}：代表竞争激烈的环境、有挑战性的工作、或者需要你独当一面的岗位。")
        career_lines.extend(["", "官星透出，说明你适合在职场发展，或者走体制内路线。"])
    else:
        career_lines.extend([
            "你的命里没有明显的官星，不适合走传统的职场晋升路线。",
            "这种情况下，你更适合自由职业、创业、或者技术路线，靠真本事吃饭。",
        ])

    if has_pianyin and has_shishen_flag:
        career_lines.extend(["", "枭神夺食的组合对你的事业有一定影响，容易遇到怀才不遇的情况，建议低调做事、积蓄力量。"])

    career = "\n".join(career_lines)

    # 健康
    health_lines = ["健康分析", "", "中医认为五行对应五脏，你的命里：", ""]
    health_map = {
        "木": "肝、胆、手脚、筋脉，头发相关问题",
        "火": "心、小肠、血液循环、眼睛",
        "土": "脾、胃、消化系统、皮肤",
        "金": "肺、大肠、呼吸系统",
        "水": "肾、膀胱、生殖系统、水液代谢",
    }
    for wx_name in ["木", "火", "土", "金", "水"]:
        score = wuxing_counts[wx_name]
        if score < 1.0:
            health_lines.append(f"  • {wx_name}偏弱：{health_map[wx_name]}，需要特别注意养护。")
        elif score >= 3.0:
            health_lines.append(f"  • {wx_name}偏旺：{health_map[wx_name]}，对应器官容易上火或亢奋。")

    if weakest[1] < 1.0:
        health_lines.append(f"\n命里{weakest[0]}最弱，建议重点关注{health_map.get(weakest[0], '相应脏腑')}的保养。")

    health_lines.append("\n当然，这只是命理角度的参考建议，身体有问题还是要看医生。")
    health = "\n".join(health_lines)

    # 婚姻
    marriage_lines = ["婚姻分析", ""]
    spouse_stars = []
    for stem in pillars_stems:
        ss = SHISHEN_MAP.get(day_master, {}).get(stem, "")
        if ss in ["正财", "偏财"]:
            spouse_stars.append((stem, ss))

    if spouse_stars:
        for stem, ss_type in spouse_stars:
            if ss_type == "正财":
                marriage_lines.append(f"• {ss_type}{stem}：代表稳定的姻缘，你未来的伴侣可能比较顾家、务实。")
            else:
                marriage_lines.append(f"• {ss_type}{stem}：代表多变的姻缘，或者你的伴侣比较活跃、社交能力强。")
        marriage_lines.extend(["", "有财星透出，说明你的姻缘基础不错，婚姻运相对顺利。"])
    else:
        marriage_lines.extend([
            "你的命里财星不显，姻缘需要靠大运来引动。",
            "这种情况下，遇到合适的人可能需要一些时间，建议多参加社交活动。",
        ])

    if wuxing_counts["水"] < 1.0:
        marriage_lines.append("\n五行水代表感情流动和沟通协调，水弱的话在感情表达上可能略显笨拙，需要多主动沟通。")

    marriage = "\n".join(marriage_lines)

    # 学业
    education_lines = ["学业分析", ""]
    yin_list = []
    for stem in pillars_stems:
        ss = SHISHEN_MAP.get(day_master, {}).get(stem, "")
        if ss in ["正印", "偏印"]:
            yin_list.append((stem, ss))

    if yin_list:
        for stem, ss_type in yin_list:
            if ss_type == "正印":
                education_lines.append(f"• 正印{stem}：代表正统的学习，文凭学历这块，你的基础比较扎实。")
            else:
                education_lines.append(f"• 偏印{stem}：代表自学、钻研、偏门学问，你可能更适合自学或深造某个专业领域。")
        education_lines.extend(["", "印星代表学业和靠山，你这方面的运气不错，学习能力较强。"])
    else:
        education_lines.extend([
            "你的命里印星不明显，不属于那种应试教育型的选手。",
            "但没关系，你可能更擅长从实践中学习，多动手、多经历对你更有帮助。",
        ])

    if strength == "偏强":
        education_lines.append("身强旺印，说明你学习起来效率很高，记忆力、理解力都不错。")

    education = "\n".join(education_lines)

    # 改善建议
    suggestions = []

    if strength == "偏强":
        suggestions.append("身强，宜静不宜动：遇到事情不要硬刚，学会以柔克刚，退一步海阔天空。")
    elif strength == "偏弱":
        suggestions.append("身弱，宜动不宜静：多出去走走，多结交朋友，多借助别人的力量来增强自己。")

    weak = weakest[0]
    weak_score = weakest[1]
    advice_map = {
        "木": ("木代表生长和生发：多接触大自然，早睡早起（23点前），多吃蔬菜水果，对你很有帮助。", ["火", "土"]),
        "火": ("火代表热情和活力：多晒太阳，适度运动，少熬夜，保持积极的心态，会让你状态更好。", ["土", "金"]),
        "土": ("土代表稳重和信用：多接触泥土或陶瓷，适当做一些慢下来、沉住气的事情，比如书法、瑜伽。", ["金", "水"]),
        "金": ("金代表魄力和决断：多做一些需要下定决心的事情来锻炼自己，比如定期整理房间、断舍离。", ["水", "木"]),
        "水": ("水代表智慧和流动：多喝水，多思考，多接触水（游泳、泡温泉），可以提升你的思维能力。", ["木", "火"]),
    }
    if weak_score < 1.0:
        advice_text, _ = advice_map.get(weak, ("", []))
        if advice_text:
            suggestions.append(advice_text)

    guan_found = bool(guan_list)
    cai_found = bool(cai_list)
    yin_found = bool(yin_list)

    if not guan_found:
        suggestions.append("没有官星：不适合走传统职场路线，建议发展一技之长，或者考虑创业、自由职业。")
    else:
        suggestions.append("有官星：适合在正规平台发展，职场晋升对你来说是可行的路径。")

    if not cai_found:
        suggestions.append("财星不显：努力工作、提升技能是最实在的来财方式，不要想着走捷径。")
    else:
        suggestions.append("有财星：善于理财是你的优势，但也要注意风险，别把所有钱都拿去冒险。")

    if not yin_found:
        suggestions.append("印星不显：不适合纯粹的理论学习，多从实践中积累经验，边做边学对你更有效。")

    if has_pianyin and has_shishen_flag:
        suggestions.append("枭神夺食：遇到怀才不遇的时候不要气馁，是金子总会发光的，关键是持续提升自己。")

    if not suggestions:
        suggestions.append("你的命局五行比较平衡，没有明显的短板，保持现在的状态，稳扎稳打就好。")

    return {
        "overview": overview,
        "dayMasterAnalysis": day_analysis,
        "wuxingAnalysis": wuxing_analysis,
        "shishenAnalysis": shishen_analysis,
        "wealth": wealth,
        "career": career,
        "health": health,
        "marriage": marriage,
        "education": education,
        "suggestions": suggestions,
    }

