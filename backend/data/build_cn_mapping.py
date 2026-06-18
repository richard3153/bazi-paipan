#!/usr/bin/env python3
"""
Build Chinese city name mapping from pinyin (SimpleMaps city_ascii) to Chinese characters.
Uses modood/Administrative-divisions-of-China as the source for Chinese names.
"""

import json
import csv
import os
from pypinyin import pinyin, Style


def normalize_pinyin(chinese_name):
    """Convert Chinese name to pinyin without tone marks and spaces."""
    # Strip administrative suffixes
    name = chinese_name.replace('新区', '').replace('市', '').replace('区', '').replace('县', '').replace('自治州', '').replace('自治县', '').replace('地区', '').replace('盟', '').replace('旗', '')
    py = pinyin(name, style=Style.NORMAL)
    return ''.join([p[0] for p in py])


# Special English spellings in SimpleMaps that don't match pypinyin output
ENGLISH_TO_CHINESE = {
    "urumqi": "乌鲁木齐",
    "hohhot": "呼和浩特",
    "harbin": "哈尔滨",
    "karamay": "克拉玛依",
    "turpan": "吐鲁番",
    "korla": "库尔勒",
    "aksu": "阿克苏",
    "kashgar": "喀什",
    "hotan": "和田",
    "ili": "伊宁",
    "bole": "博乐",
    "tacheng": "塔城",
    "altay": "阿勒泰",
    "aral": "阿拉尔",
    "tumxuk": "图木舒克",
    "wujiaqu": "五家渠",
    "kokdala": "可克达拉",
    "kunyu": "昆玉",
    "shuanghe": "双河",
    "bengbu": "蚌埠",
    "huainan": "淮南",
    "maanshan": "马鞍山",
    "huaibei": "淮北",
    "tongling": "铜陵",
    "anqing": "安庆",
    "huangshan": "黄山",
    "chuzhou": "滁州",
    "fuyang": "阜阳",
    "suzhou": "宿州",
    "bozhou": "亳州",
    "liuan": "六安",
    "chizhou": "池州",
    "xuancheng": "宣城",
    "lhasa": "拉萨",
    "rikaze": "日喀则",
    "shannan": "山南",
    "linzhi": "林芝",
    "changdu": "昌都",
    "naqu": "那曲",
    "ali": "阿里",
    "eerduosi": "鄂尔多斯",
    "bayannur": "巴彦淖尔",
    "wulanchabu": "乌兰察布",
    "xilinhot": "锡林浩特",
    "alxa": "阿拉善",
    "hulunbeier": "呼伦贝尔",
    "xingan": "兴安",
    "tongliao": "通辽",
    "chifeng": "赤峰",
    "xilingol": "锡林郭勒",
    "chongqing": "重庆",
    "qiqihar": "齐齐哈尔",
    "changzhi": "长治",
    "shigatse": "日喀则",
}


def build_mapping():
    mapping = {}  # pinyin -> Chinese
    
    # 1. Load prefecture-level cities from pcas-code.json
    with open(r'C:\Users\xuanc\AppData\Local\Temp\pcas-code.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for province in data:
        prov_name = province['name'].replace('市', '').replace('省', '').replace('自治区', '').replace('壮族', '').replace('回族', '').replace('维吾尔', '').replace('特别行政区', '')
        children = province.get('children', [])
        
        # Handle municipalities (Beijing, Tianjin, Shanghai, Chongqing): province has one child "市辖区"
        if len(children) == 1 and children[0]['name'] == '市辖区':
            py = normalize_pinyin(prov_name)
            if py:
                mapping[py] = prov_name
            continue
        
        for city in children:
            city_name = city['name']
            cn = city_name.replace('新区', '').replace('市', '').replace('区', '').replace('县', '').replace('地区', '').replace('自治州', '').replace('盟', '')
            py = normalize_pinyin(city_name)
            if py:
                mapping[py] = cn
    
    # 2. Load city-level and county-level entries from district-full.csv (chideat/district)
    district_path = r'C:\Users\xuanc\AppData\Local\Temp\district-full.csv'
    if os.path.exists(district_path):
        count = 0
        with open(district_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if len(row) < 8:
                    continue
                name_cn = row[1].strip()
                city_type = row[7].strip()
                pinyin_full = row[5].strip().lower()
                if not name_cn or not pinyin_full:
                    continue
                # Only include city-level (市) and county-level (县) entries
                if city_type not in ('市', '县'):
                    continue
                # Give city-level priority over county-level
                if city_type == '县' and pinyin_full in mapping:
                    continue
                # Strip suffixes
                cn = name_cn.replace('新区', '').replace('市', '').replace('区', '').replace('县', '')
                if cn:
                    # Use dataset's pinyin as primary key
                    if pinyin_full:
                        mapping[pinyin_full] = cn
                        count += 1
                    # Also add normalized pinyin from Chinese name (corrects dataset errors)
                    py = normalize_pinyin(name_cn)
                    if py and py != pinyin_full:
                        mapping[py] = cn
                        count += 1
        print(f"Added {count} city/county entries from district-full.csv")
    
    # 3. Load district-level entries from areas.csv (fenbol/Administrative-divisions-of-China)
    areas_path = r'C:\Users\xuanc\AppData\Local\Temp\areas.csv'
    if os.path.exists(areas_path):
        count = 0
        with open(areas_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name_cn = row['name'].strip()
                if not name_cn:
                    continue
                # Strip suffixes
                cn = name_cn.replace('新区', '').replace('市', '').replace('区', '').replace('县', '').replace('自治县', '').replace('旗', '')
                if not cn:
                    continue
                py = normalize_pinyin(name_cn)
                if not py:
                    continue
                # Only add if not already covered by a city/county entry
                if py in mapping:
                    continue
                # Also add without tone/diacritic normalization
                mapping[py] = cn
                count += 1
        print(f"Added {count} district entries from areas.csv")
    
    # 4. Add special English spellings
    for en, cn in ENGLISH_TO_CHINESE.items():
        mapping[en] = cn
    
    return mapping


def main():
    mapping = build_mapping()
    print(f"Built mapping with {len(mapping)} Chinese cities")
    
    # Test some lookups
    test_names = ['Beijing', 'Shanghai', 'Shijiazhuang', 'Tangshan', 'Xi\'an', 'Urumqi', 'Hohhot', 'Harbin']
    for en in test_names:
        en_lower = en.lower().replace("'", "")
        cn = mapping.get(en_lower)
        print(f"{en} -> {cn}")
    
    # Save mapping
    with open(r'C:\Users\xuanc\AppData\Local\Temp\cn_city_map.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print(f"Saved mapping to cn_city_map.json")

if __name__ == '__main__':
    main()
