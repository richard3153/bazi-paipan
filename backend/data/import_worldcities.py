#!/usr/bin/env python3
"""
Import SimpleMaps worldcities.csv into our cities.csv format.
- For Chinese cities: map ASCII/pinyin names to Chinese names
- For international cities: keep English name (Chinese translation for major cities only)
- Deduplicate by (name, country, province)
"""

import csv
import os
import json

# ============================================================
# Chinese city name mapping (ASCII/pinyin -> Chinese)
# Source: manual mapping for major Chinese cities
# ============================================================
CN_CITY_MAP = {
    # Municipalities
    "Beijing": "北京", "Shanghai": "上海", "Tianjin": "天津", "Chongqing": "重庆",
    # Provinces - major cities
    "Guangzhou": "广州", "Shenzhen": "深圳", "Dongguan": "东莞", "Foshan": "佛山",
    "Zhuhai": "珠海", "Zhongshan": "中山", "Huizhou": "惠州", "Jiangmen": "江门",
    "Zhaoqing": "肇庆", "Shantou": "汕头", "Shaoguan": "韶关", "Meizhou": "梅州",
    "Zhanjiang": "湛江", "Maoming": "茂名", "Zhuhai": "珠海", "Shantou": "汕头",
    "Chaozhou": "潮州", "Jieyang": "揭阳", "Yunfu": "云浮", "Heyuan": "河源",
    "Yangjiang": "阳江", "Qingyuan": "清远", "Zhongshan": "中山", "Shanwei": "汕尾",
    "Heyuan": "河源", "Meizhou": "梅州", "Shaoguan": "韶关", "Shantou": "汕头",
    "Nanjing": "南京", "Suzhou": "苏州", "Wuxi": "无锡", "Changzhou": "常州",
    "Nantong": "南通", "Xuzhou": "徐州", "Huai'an": "淮安", "Yancheng": "盐城",
    "Yangzhou": "扬州", "Zhenjiang": "镇江", "Taizhou": "泰州", "Suqian": "宿迁",
    "Hangzhou": "杭州", "Ningbo": "宁波", "Wenzhou": "温州", "Jiaxing": "嘉兴",
    "Huzhou": "湖州", "Shaoxing": "绍兴", "Jinhua": "金华", "Quzhou": "衢州",
    "Zhoushan": "舟山", "Taizhou": "台州", "Lishui": "丽水",
    "Hefei": "合肥", "Wuhu": "芜湖", "Bengbu": "蚌埠", "Huainan": "淮南",
    "Ma'anshan": "马鞍山", "Huaibei": "淮北", "Tongling": "铜陵", "Anqing": "安庆",
    "Huangshan": "黄山", "Chuzhou": "滁州", "Fuyang": "阜阳", "Suzhou": "宿州",
    "Lu'an": "六安", "Bozhou": "亳州", "Chizhou": "池州", "Xuancheng": "宣城",
    "Fuzhou": "福州", "Xiamen": "厦门", "Quanzhou": "泉州", "Zhangzhou": "漳州",
    "Putian": "莆田", "Sanming": "三明", "Nanping": "南平", "Longyan": "龙岩",
    "Ningde": "宁德",
    "Nanchang": "南昌", "Jingdezhen": "景德镇", "Pingxiang": "萍乡", "Jiujiang": "九江",
    "Xinyu": "新余", "Yingtan": "鹰潭", "Ganzhou": "赣州", "Ji'an": "吉安",
    "Yichun": "宜春", "Fuzhou": "抚州", "Shangrao": "上饶",
    "Jinan": "济南", "Qingdao": "青岛", "Yantai": "烟台", "Weifang": "潍坊",
    "Linyi": "临沂", "Jining": "济宁", "Heze": "菏泽", "Taian": "泰安",
    "Zibo": "淄博", "Dezhou": "德州", "Dongying": "东营", "Weihai": "威海",
    "Zaozhuang": "枣庄", "Rizhao": "日照", "Liaocheng": "聊城", "Binzhou": "滨州",
    "Zhengzhou": "郑州", "Luoyang": "洛阳", "Nanyang": "南阳", "Kaifeng": "开封",
    "Shangqiu": "商丘", "Xinyang": "信阳", "Zhoukou": "周口", "Xuchang": "许昌",
    "Xinxiang": "新乡", "Jiaozuo": "焦作", "Anyang": "安阳", "Hebi": "鹤壁",
    "Puyang": "濮阳", "Luohe": "漯河", "Sanmenxia": "三门峡", "Zhumadian": "驻马店",
    "Wuhan": "武汉", "Xiangyang": "襄阳", "Yichang": "宜昌", "Huangshi": "黄石",
    "Ezhou": "鄂州", "Shiyan": "十堰", "Jingmen": "荆门", "Xiaogan": "孝感",
    "Huanggang": "黄冈", "Xianning": "咸宁", "Suizhou": "随州", "Enshi": "恩施",
    "Changsha": "长沙", "Hengyang": "衡阳", "Zhuzhou": "株洲", "Xiangtan": "湘潭",
    "Yueyang": "岳阳", "Changde": "常德", "Zhangjiajie": "张家界", "Yiyang": "益阳",
    "Chenzhou": "郴州", "Yongzhou": "永州", "Huaihua": "怀化", "Loudi": "娄底",
    "Chengdu": "成都", "Mianyang": "绵阳", "Deyang": "德阳", "Yibin": "宜宾",
    "Nanchong": "南充", "Luzhou": "泸州", "Dazhou": "达州", "Neijiang": "内江",
    "Sichuan": "遂宁", "Leshan": "乐山", "Nanchong": "南充", "Meishan": "眉山",
    "Guilin": "桂林", "Nanning": "南宁", "Liuzhou": "柳州", "Guigang": "贵港",
    "Yulin": "玉林", "Baise": "百色", "Hezhou": "贺州", "Hechi": "河池", "Chongzuo": "崇左",
    "Haikou": "海口", "Sanya": "三亚", "Sansha": "三沙",
    "Guiyang": "贵阳", "Zunyi": "遵义", "Anshun": "安顺", "Bijie": "毕节", "Tongren": "铜仁",
    "Kunming": "昆明", "Qujing": "曲靖", "Yuxi": "玉溪", "Baoshan": "保山", "Zhaotong": "昭通", "Lijiang": "丽江",
    "Xi'an": "西安", "Xianyang": "咸阳", "Baoji": "宝鸡", "Tongchuan": "铜川", "Weinan": "渭南",
    "Yan'an": "延安", "Hanzhong": "汉中", "Yulin": "榆林", "Ankang": "安康", "Shangluo": "商洛",
    "Lanzhou": "兰州", "Jinchang": "金昌", "Baiyin": "白银", "Tianshui": "天水",
    "Wuwei": "武威", "Zhangye": "张掖", "Pingliang": "平凉", "Jiuquan": "酒泉", "Qingyang": "庆阳",
    "Xining": "西宁", "Haidong": "海东", "Haibei": "海北", "Hainan": "海南", "Huangnan": "黄南",
    "Yinchuan": "银川", "Shizuishan": "石嘴山", "Wuzhong": "吴忠", "Guyuan": "固原", "Zhongwei": "中卫",
    "Urumqi": "乌鲁木齐", "Karamay": "克拉玛依", "Turpan": "吐鲁番", "Hami": "哈密",
    "Shenyang": "沈阳", "Dalian": "大连", "Anshan": "鞍山", "Fushun": "抚顺",
    "Benxi": "本溪", "Dandong": "丹东", "Jinzhou": "锦州", "Yingkou": "营口",
    "Fuxin": "阜新", "Liaoyang": "辽阳", "Panjin": "盘锦", "Tieling": "铁岭", "Chaoyang": "朝阳", "Huludao": "葫芦岛",
    "Changchun": "长春", "Jilin": "吉林", "Siping": "四平", "Liaoyuan": "辽源",
    "Tonghua": "通化", "Baishan": "白山", "Songyuan": "松原", "Baicheng": "白城",
    "Harbin": "哈尔滨", "Qiqihar": "齐齐哈尔", "Jixi": "鸡西", "Hegang": "鹤岗",
    "Shuangyashan": "双鸭山", "Daqing": "大庆", "Yichun": "伊春", "Jiamusi": "佳木斯",
    "Qitaihe": "七台河", "Heihe": "黑河", "Suihua": "绥化", "Mudanjiang": "牡丹江",
    "Hohhot": "呼和浩特", "Baotou": "包头", "Wuhai": "乌海", "Chifeng": "赤峰",
    "Tongliao": "通辽", "Ordos": "鄂尔多斯", "Hulunbuir": "呼伦贝尔",
    "Lhasa": "拉萨", "Shigatse": "日喀则", "Chamdo": "昌都", "Nyingchi": "林芝",
    "Shannan": "山南", "Nagqu": "那曲", "Ali": "阿里",
    "Taipei": "台北", "Kaohsiung": "高雄", "Taichung": "台中", "Tainan": "台南",
    "Hong Kong": "香港", "Macau": "澳门",
}

# Province name mapping (SimpleMaps admin_name -> Chinese)
CN_PROVINCE_MAP = {
    "Beijing": "北京", "Shanghai": "上海", "Tianjin": "天津", "Chongqing": "重庆",
    "Hebei": "河北", "Shanxi": "山西", "Liaoning": "辽宁", "Jilin": "吉林",
    "Heilongjiang": "黑龙江", "Jiangsu": "江苏", "Zhejiang": "浙江", "Anhui": "安徽",
    "Fujian": "福建", "Jiangxi": "江西", "Shandong": "山东", "Henan": "河南",
    "Hubei": "湖北", "Hunan": "湖南", "Guangdong": "广东", "Hainan": "海南",
    "Sichuan": "四川", "Guizhou": "贵州", "Yunnan": "云南", "Shaanxi": "陕西",
    "Gansu": "甘肃", "Qinghai": "青海", "Taiwan": "台湾",
    "Guangxi": "广西", "Nei Mongol": "内蒙古", "Ningxia": "宁夏", "Xinjiang": "新疆",
    "Tibet": "西藏", "Hong Kong": "香港", "Macau": "澳门",
}

# Timezone mapping by country (simplified)
COUNTRY_TZ = {
    "CN": "Asia/Shanghai", "HK": "Asia/Hong_Kong", "MO": "Asia/Macau", "TW": "Asia/Taipei",
    "JP": "Asia/Tokyo", "KR": "Asia/Seoul", "KP": "Asia/Pyongyang",
    "MN": "Asia/Ulaanbaatar",
    "SG": "Asia/Singapore", "TH": "Asia/Bangkok", "VN": "Asia/Ho_Chi_Minh",
    "ID": "Asia/Jakarta", "MY": "Asia/Kuala_Lumpur", "PH": "Asia/Manila",
    "MM": "Asia/Yangon", "KH": "Asia/Phnom_Penh", "LA": "Asia/Vientiane",
    "BN": "Asia/Brunei", "TL": "Asia/Dili",
    "IN": "Asia/Kolkata", "BD": "Asia/Dhaka", "PK": "Asia/Karachi",
    "LK": "Asia/Colombo", "NP": "Asia/Kathmandu", "BT": "Asia/Thimphu",
    "MV": "Indian/Maldives",
    "AE": "Asia/Dubai", "SA": "Asia/Riyadh", "QA": "Asia/Qatar",
    "OM": "Asia/Muscat", "KW": "Asia/Kuwait", "BH": "Asia/Bahrain",
    "YE": "Asia/Aden", "IQ": "Asia/Baghdad", "JO": "Asia/Amman",
    "LB": "Asia/Beirut", "SY": "Asia/Damascus", "IL": "Asia/Jerusalem",
    "TR": "Europe/Istanbul", "CY": "Asia/Nicosia",
    "KZ": "Asia/Almaty", "UZ": "Asia/Tashkent", "TM": "Asia/Ashgabat",
    "KG": "Asia/Bishkek", "TJ": "Asia/Dushanbe", "AF": "Asia/Kabul",
    "IR": "Asia/Tehran",
    "GB": "Europe/London", "FR": "Europe/Paris", "DE": "Europe/Berlin",
    "IT": "Europe/Rome", "ES": "Europe/Madrid", "PT": "Europe/Lisbon",
    "NL": "Europe/Amsterdam", "BE": "Europe/Brussels", "CH": "Europe/Zurich",
    "AT": "Europe/Vienna", "SE": "Europe/Stockholm", "NO": "Europe/Oslo",
    "DK": "Europe/Copenhagen", "FI": "Europe/Helsinki", "IS": "Atlantic/Reykjavik",
    "PL": "Europe/Warsaw", "CZ": "Europe/Prague", "HU": "Europe/Budapest",
    "RO": "Europe/Bucharest", "BG": "Europe/Sofia", "RS": "Europe/Belgrade",
    "HR": "Europe/Zagreb", "BA": "Europe/Sarajevo", "SI": "Europe/Ljubljana",
    "MK": "Europe/Skopje", "AL": "Europe/Tirane", "GR": "Europe/Athens",
    "LT": "Europe/Vilnius", "LV": "Europe/Riga", "EE": "Europe/Tallinn",
    "BY": "Europe/Minsk", "UA": "Europe/Kyiv", "MD": "Europe/Chisinau",
    "RU": "Europe/Moscow", "GE": "Asia/Tbilisi", "AM": "Asia/Yerevan", "AZ": "Asia/Baku",
    "IE": "Europe/Dublin", "LU": "Europe/Luxembourg",
    "US": "America/New_York", "CA": "America/Toronto", "MX": "America/Mexico_City",
    "BR": "America/Sao_Paulo", "AR": "America/Argentina/Buenos_Aires",
    "CL": "America/Santiago", "CO": "America/Bogota", "PE": "America/Lima",
    "EC": "America/Guayaquil", "VE": "America/Caracas", "BO": "America/La_Paz",
    "UY": "America/Montevideo", "PY": "America/Asuncion",
    "EG": "Africa/Cairo", "ZA": "Africa/Johannesburg", "NG": "Africa/Lagos",
    "KE": "Africa/Nairobi", "ET": "Africa/Addis_Ababa", "TZ": "Africa/Dar_es_Salaam",
    "MA": "Africa/Casablanca", "DZ": "Africa/Algiers", "TN": "Africa/Tunis",
    "GH": "Africa/Accra", "CI": "Africa/Abidjan", "SN": "Africa/Dakar",
    "AU": "Australia/Sydney", "NZ": "Pacific/Auckland", "FJ": "Pacific/Fiji",
    "PG": "Pacific/Port_Moresby",
}

# Major international cities Chinese name mapping
INTL_CITY_CN = {
    "Tokyo": "东京", "Osaka": "大阪", "Yokohama": "横滨", "Nagoya": "名古屋",
    "Sapporo": "札幌", "Kyoto": "京都", "Fukuoka": "福冈",
    "Seoul": "首尔", "Busan": "釜山", "Incheon": "仁川", "Daegu": "大邱",
    "Singapore": "新加坡",
    "Bangkok": "曼谷", "Chiang Mai": "清迈",
    "Ho Chi Minh City": "胡志明市", "Hanoi": "河内", "Da Nang": "岘港",
    "Jakarta": "雅加达", "Surabaya": "泗水", "Bandung": "万隆",
    "Manila": "马尼拉", "Cebu": "宿务",
    "Kuala Lumpur": "吉隆坡", "George Town": "槟城",
    "Yangon": "仰光", "Naypyidaw": "内比都",
    "Phnom Penh": "金边", "Vientiane": "万象",
    "Mumbai": "孟买", "Delhi": "德里", "Bangalore": "班加罗尔",
    "Hyderabad": "海德拉巴", "Ahmedabad": "艾哈迈达巴德", "Chennai": "金奈",
    "Kolkata": "加尔各答", "Pune": "浦那", "Jaipur": "斋浦尔", "Chandigarh": "昌迪加尔",
    "Dhaka": "达卡", "Chittagong": "吉大港",
    "Kathmandu": "加德满都", "Colombo": "科伦坡",
    "Dubai": "迪拜", "Abu Dhabi": "阿布扎比",
    "Riyadh": "利雅得", "Jeddah": "吉达", "Mecca": "麦加",
    "Doha": "多哈", "Muscat": "马斯喀特",
    "Baghdad": "巴格达", "Basra": "巴士拉",
    "Amman": "安曼", "Beirut": "贝鲁特", "Damascus": "大马士革", "Aleppo": "阿勒颇",
    "Jerusalem": "耶路撒冷", "Tel Aviv": "特拉维夫", "Haifa": "海法",
    "Istanbul": "伊斯坦布尔", "Ankara": "安卡拉", "Izmir": "伊兹密尔",
    "Astana": "阿斯塔纳", "Almaty": "阿拉木图", "Tashkent": "塔什干",
    "London": "伦敦", "Manchester": "曼彻斯特", "Birmingham": "伯明翰",
    "Liverpool": "利物浦", "Glasgow": "格拉斯哥", "Edinburgh": "爱丁堡",
    "Paris": "巴黎", "Marseille": "马赛", "Lyon": "里昂", "Toulouse": "图卢兹",
    "Bordeaux": "波尔多", "Nice": "尼斯",
    "Berlin": "柏林", "Hamburg": "汉堡", "Munich": "慕尼黑", "Cologne": "科隆",
    "Frankfurt": "法兰克福", "Stuttgart": "斯图加特",
    "Rome": "罗马", "Milan": "米兰", "Naples": "那不勒斯", "Turin": "都灵",
    "Florence": "佛罗伦萨", "Venice": "威尼斯",
    "Madrid": "马德里", "Barcelona": "巴塞罗那", "Valencia": "瓦伦西亚", "Seville": "塞维利亚",
    "Lisbon": "里斯本", "Porto": "波尔图",
    "Brussels": "布鲁塞尔", "Antwerp": "安特卫普",
    "Amsterdam": "阿姆斯特丹", "Rotterdam": "鹿特丹", "The Hague": "海牙",
    "Vienna": "维也纳", "Zurich": "苏黎世", "Geneva": "日内瓦", "Bern": "伯尔尼",
    "Stockholm": "斯德哥尔摩", "Gothenburg": "哥德堡",
    "Oslo": "奥斯陆", "Bergen": "卑尔根",
    "Copenhagen": "哥本哈根", "Helsinki": "赫尔辛基",
    "Moscow": "莫斯科", "Saint Petersburg": "圣彼得堡", "Novosibirsk": "新西伯利亚",
    "Warsaw": "华沙", "Krakow": "克拉科夫",
    "Prague": "布拉格", "Budapest": "布达佩斯", "Bucharest": "布加勒斯特",
    "Sofia": "索菲亚", "Belgrade": "贝尔格莱德", "Zagreb": "萨格勒布",
    "Athens": "雅典", "Thessaloniki": "塞萨洛尼基",
    "Vilnius": "维尔纽斯", "Riga": "里加", "Tallinn": "塔林",
    "Minsk": "明斯克", "Kyiv": "基辅", "Kharkiv": "哈尔科夫", "Odesa": "敖德萨",
    "Tbilisi": "第比利斯", "Yerevan": "埃里温", "Baku": "巴库",
    "Dublin": "都柏林",
    "New York": "纽约", "Los Angeles": "洛杉矶", "Chicago": "芝加哥",
    "Houston": "休斯顿", "Phoenix": "凤凰城", "Philadelphia": "费城",
    "San Antonio": "圣安东尼奥", "San Diego": "圣迭戈", "Dallas": "达拉斯",
    "San Jose": "圣何塞", "Austin": "奥斯汀", "Jacksonville": "杰克逊维尔",
    "San Francisco": "旧金山", "Columbus": "哥伦布", "Charlotte": "夏洛特",
    "Indianapolis": "印第安纳波利斯", "Seattle": "西雅图", "Denver": "丹佛",
    "Boston": "波士顿", "Nashville": "纳什维尔", "Baltimore": "巴尔的摩",
    "Oklahoma City": "俄克拉荷马城", "Louisville": "路易斯维尔", "Portland": "波特兰",
    "Las Vegas": "拉斯维加斯", "Milwaukee": "密尔沃基", "Albuquerque": "阿尔伯克基",
    "Tucson": "图森", "Fresno": "弗雷斯诺", "Sacramento": "萨克拉门托",
    "Long Beach": "长滩", "Kansas City": "堪萨斯城", "Atlanta": "亚特兰大",
    "Miami": "迈阿密", "Washington": "华盛顿", "Honolulu": "檀香山",
    "Anchorage": "安克雷奇",
    "Toronto": "多伦多", "Vancouver": "温哥华", "Montreal": "蒙特利尔",
    "Calgary": "卡尔加里", "Edmonton": "埃德蒙顿", "Ottawa": "渥太华",
    "Winnipeg": "温尼伯", "Quebec City": "魁北克城",
    "Mexico City": "墨西哥城", "Cancun": "坎昆", "Guadalajara": "瓜达拉哈拉",
    "Monterrey": "蒙特雷", "Tijuana": "蒂华纳", "Puebla": "普埃布拉",
    "Sao Paulo": "圣保罗", "Rio de Janeiro": "里约热内卢", "Brasilia": "巴西利亚",
    "Salvador": "萨尔瓦多", "Fortaleza": "福塔莱萨", "Belo Horizonte": "贝洛奥里藏特",
    "Manaus": "马瑙斯", "Curitiba": "库里蒂巴", "Recife": "累西腓",
    "Buenos Aires": "布宜诺斯艾利斯", "Cordoba": "科尔多瓦", "Rosario": "罗萨里奥",
    "Santiago": "圣地亚哥", "Valparaiso": "瓦尔帕莱索",
    "Bogota": "波哥大", "Medellin": "麦德林", "Cali": "卡利",
    "Lima": "利马", "Cusco": "库斯科",
    "Quito": "基多", "Guayaquil": "瓜亚基尔",
    "Caracas": "加拉加斯", "Maracaibo": "马拉开波",
    "La Paz": "拉巴斯", "Santa Cruz": "圣克鲁斯",
    "Montevideo": "蒙得维的亚", "Asuncion": "亚松森",
    "Cairo": "开罗", "Alexandria": "亚历山大", "Giza": "吉萨",
    "Lagos": "拉各斯", "Abuja": "阿布贾", "Ibadan": "伊巴丹", "Kano": "卡诺",
    "Nairobi": "内罗毕", "Mombasa": "蒙巴萨",
    "Addis Ababa": "亚的斯亚贝巴",
    "Dar es Salaam": "达累斯萨拉姆", "Dodoma": "多多马",
    "Johannesburg": "约翰内斯堡", "Cape Town": "开普敦",
    "Pretoria": "比勒陀利亚", "Durban": "德班",
    "Rabat": "拉巴特", "Casablanca": "卡萨布兰卡", "Marrakech": "马拉喀什",
    "Algiers": "阿尔及尔", "Tunis": "突尼斯", "Tripoli": "的黎波里",
    "Accra": "阿克拉", "Kumasi": "库马西",
    "Abidjan": "阿比让", "Dakar": "达喀尔", "Bamako": "巴马科",
    "Ouagadougou": "瓦加杜古", "Conakry": "科纳克里", "Bissau": "比绍",
    "Monrovia": "蒙罗维亚", "Freetown": "弗里敦",
    "Niamey": "尼亚美", "Lome": "洛美", "Porto-Novo": "波多诺伏",
    "Kampala": "坎帕拉", "Kigali": "基加利", "Bujumbura": "布琼布拉", "Juba": "朱巴",
    "Harare": "哈拉雷", "Lusaka": "卢萨卡", "Lilongwe": "利隆圭", "Maputo": "马普托",
    "Luanda": "罗安达", "Kinshasa": "金沙萨", "Lubumbashi": "卢本巴希",
    "Khartoum": "喀土穆", "Asmara": "阿斯马拉", "Djibouti": "吉布提", "Mogadishu": "摩加迪沙",
    "Antananarivo": "塔那那利佛", "Port Louis": "路易港", "Victoria": "维多利亚", "Moroni": "莫罗尼",
    "Windhoek": "温得和克", "Gaborone": "哈博罗内", "Mbabane": "姆巴巴内", "Maseru": "马塞卢",
    "Sydney": "悉尼", "Melbourne": "墨尔本", "Brisbane": "布里斯班",
    "Perth": "珀斯", "Adelaide": "阿德莱德", "Canberra": "堪培拉",
    "Gold Coast": "黄金海岸", "Darwin": "达尔文", "Hobart": "霍巴特", "Newcastle": "纽卡斯尔",
    "Auckland": "奥克兰", "Wellington": "惠灵顿", "Christchurch": "基督城",
    "Port Moresby": "莫尔兹比港", "Suva": "苏瓦", "Honiara": "霍尼亚拉",
    "Port Vila": "维拉港", "Apia": "阿皮亚", "Nukualofa": "努库阿洛法",
    "Tarawa": "塔拉瓦", "Majuro": "马朱罗", "Palikir": "帕利基尔", "Yaren": "亚伦",
    "Funafuti": "富纳富提", "Papeete": "帕皮提", "Noumea": "努美阿",
}


def get_timezone(iso2):
    return COUNTRY_TZ.get(iso2, "UTC")


def get_city_name(row):
    """Get city name in Chinese if possible, otherwise use ASCII name."""
    city_ascii = row['city_ascii']
    country = row['country']
    iso2 = row['iso2']

    # For Chinese cities, try to map to Chinese name
    if iso2 == 'CN':
        # Try direct mapping
        if city_ascii in CN_CITY_MAP:
            return CN_CITY_MAP[city_ascii]
        # Try the city field (might have Chinese)
        city_field = row['city']
        try:
            city_field.encode('ascii')
            # ASCII only, no Chinese
            return city_ascii
        except UnicodeEncodeError:
            # Has non-ASCII, likely Chinese
            return city_field
    else:
        # For international cities, use Chinese mapping if available
        if city_ascii in INTL_CITY_CN:
            return INTL_CITY_CN[city_ascii]
        return city_ascii


def get_province(row):
    """Get province/state name, mapped to Chinese if possible."""
    iso2 = row['iso2']
    admin_name = row['admin_name'].strip()

    if iso2 == 'CN':
        # Map Chinese province names
        if admin_name in CN_PROVINCE_MAP:
            return CN_PROVINCE_MAP[admin_name]
        return admin_name
    else:
        return admin_name


def main():
    src = r'C:\Users\xuanc\Downloads\simplemaps_worldcities_basicv1.91\worldcities.csv'
    dst = os.path.join(os.path.dirname(__file__), 'cities.csv')

    cities = []
    seen = set()

    print("Reading SimpleMaps worldcities.csv...")
    with open(src, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        total = 0
        for row in reader:
            total += 1
            name = get_city_name(row)
            country = row['country']
            province = get_province(row)
            lng = float(row['lng'])
            lat = float(row['lat'])
            tz = get_timezone(row['iso2'])

            # Deduplicate
            key = (name, country, province)
            if key in seen:
                continue
            seen.add(key)

            cities.append({
                'name': name,
                'country': country,
                'province': province,
                'longitude': lng,
                'latitude': lat,
                'timezone': tz,
            })

            if total % 10000 == 0:
                print(f"  Processed {total} rows...")

    print(f"Total rows processed: {total}")
    print(f"Unique cities after dedup: {len(cities)}")

    # Sort by country, then province, then name
    cities.sort(key=lambda x: (x['country'], x['province'] or '', x['name']))

    # Write output
    with open(dst, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'country', 'province', 'longitude', 'latitude', 'timezone'])
        writer.writeheader()
        for i, c in enumerate(cities, start=1):
            c['id'] = i
            writer.writerow(c)

    print(f"\nWrote {len(cities)} cities to {dst}")
    print(f"\nBreakdown:")
    cn = sum(1 for c in cities if c['country'] == 'China')
    print(f"  China: {cn}")
    print(f"  International: {len(cities) - cn}")


if __name__ == '__main__':
    main()
