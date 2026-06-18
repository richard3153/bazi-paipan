# data/init_db.py
"""
数据库初始化脚本
初始化城市经纬度和命理知识库数据
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal, Base
from app.models.city import City
from app.models.mingli import MingLiKnowledge, ShishenEntry, WuxingEntry, GeshiRule


# 中国主要城市经纬度数据（部分）
CITY_DATA = [
    # 直辖市
    {"name": "北京", "province": "北京", "longitude": 116.4074, "latitude": 39.9042, "timezone": 8, "adcode": "110000"},
    {"name": "上海", "province": "上海", "longitude": 121.4737, "latitude": 31.2304, "timezone": 8, "adcode": "310000"},
    {"name": "天津", "province": "天津", "longitude": 117.3616, "latitude": 39.3434, "timezone": 8, "adcode": "120000"},
    {"name": "重庆", "province": "重庆", "longitude": 106.5516, "latitude": 29.5630, "timezone": 8, "adcode": "500000"},
    # 省会城市
    {"name": "广州", "province": "广东", "longitude": 113.2644, "latitude": 23.1291, "timezone": 8, "adcode": "440100"},
    {"name": "深圳", "province": "广东", "longitude": 114.0579, "latitude": 22.5431, "timezone": 8, "adcode": "440300"},
    {"name": "杭州", "province": "浙江", "longitude": 120.1551, "latitude": 30.2741, "timezone": 8, "adcode": "330100"},
    {"name": "南京", "province": "江苏", "longitude": 118.7969, "latitude": 32.0603, "timezone": 8, "adcode": "320100"},
    {"name": "武汉", "province": "湖北", "longitude": 114.3055, "latitude": 30.5928, "timezone": 8, "adcode": "420100"},
    {"name": "成都", "province": "四川", "longitude": 104.0657, "latitude": 30.6598, "timezone": 8, "adcode": "510100"},
    {"name": "西安", "province": "陕西", "longitude": 108.9402, "latitude": 34.3416, "timezone": 8, "adcode": "610100"},
    {"name": "郑州", "province": "河南", "longitude": 113.6254, "latitude": 34.7466, "timezone": 8, "adcode": "410100"},
    {"name": "长沙", "province": "湖南", "longitude": 112.9388, "latitude": 28.2282, "timezone": 8, "adcode": "430100"},
    {"name": "济南", "province": "山东", "longitude": 116.9944, "latitude": 36.6753, "timezone": 8, "adcode": "370100"},
    {"name": "青岛", "province": "山东", "longitude": 120.3826, "latitude": 36.0671, "timezone": 8, "adcode": "370200"},
    {"name": "沈阳", "province": "辽宁", "longitude": 123.4315, "latitude": 41.8057, "timezone": 8, "adcode": "210100"},
    {"name": "大连", "province": "辽宁", "longitude": 121.6147, "latitude": 38.9140, "timezone": 8, "adcode": "210200"},
    {"name": "哈尔滨", "province": "黑龙江", "longitude": 126.5340, "latitude": 45.8038, "timezone": 8, "adcode": "230100"},
    {"name": "长春", "province": "吉林", "longitude": 125.3245, "latitude": 43.8868, "timezone": 8, "adcode": "220100"},
    {"name": "石家庄", "province": "河北", "longitude": 114.5149, "latitude": 38.0428, "timezone": 8, "adcode": "130100"},
    {"name": "太原", "province": "山西", "longitude": 112.5489, "latitude": 37.8706, "timezone": 8, "adcode": "140100"},
    {"name": "呼和浩特", "province": "内蒙古", "longitude": 111.6708, "latitude": 40.8189, "timezone": 8, "adcode": "150100"},
    {"name": "南昌", "province": "江西", "longitude": 115.8579, "latitude": 28.6830, "timezone": 8, "adcode": "360100"},
    {"name": "福州", "province": "福建", "longitude": 119.2965, "latitude": 26.0745, "timezone": 8, "adcode": "350100"},
    {"name": "厦门", "province": "福建", "longitude": 118.0894, "latitude": 24.4798, "timezone": 8, "adcode": "350200"},
    {"name": "南宁", "province": "广西", "longitude": 108.3661, "latitude": 22.8170, "timezone": 8, "adcode": "450100"},
    {"name": "昆明", "province": "云南", "longitude": 102.7129, "latitude": 25.0406, "timezone": 8, "adcode": "530100"},
    {"name": "贵阳", "province": "贵州", "longitude": 106.6302, "latitude": 26.6470, "timezone": 8, "adcode": "520100"},
    {"name": "拉萨", "province": "西藏", "longitude": 91.1172, "latitude": 29.6476, "timezone": 8, "adcode": "540100"},
    {"name": "兰州", "province": "甘肃", "longitude": 103.8343, "latitude": 36.0611, "timezone": 8, "adcode": "620100"},
    {"name": "西宁", "province": "青海", "longitude": 101.7782, "latitude": 36.6171, "timezone": 8, "adcode": "630100"},
    {"name": "银川", "province": "宁夏", "longitude": 106.2588, "latitude": 38.4683, "timezone": 8, "adcode": "640100"},
    {"name": "乌鲁木齐", "province": "新疆", "longitude": 87.6177, "latitude": 43.7928, "timezone": 8, "adcode": "650100"},
    {"name": "海口", "province": "海南", "longitude": 110.1999, "latitude": 20.0444, "timezone": 8, "adcode": "460100"},
    {"name": "苏州", "province": "江苏", "longitude": 120.5853, "latitude": 31.2990, "timezone": 8, "adcode": "320500"},
    {"name": "无锡", "province": "江苏", "longitude": 120.3017, "latitude": 31.5747, "timezone": 8, "adcode": "320200"},
    {"name": "宁波", "province": "浙江", "longitude": 121.5440, "latitude": 29.8683, "timezone": 8, "adcode": "330200"},
    {"name": "温州", "province": "浙江", "longitude": 120.6994, "latitude": 28.0006, "timezone": 8, "adcode": "330300"},
    {"name": "佛山", "province": "广东", "longitude": 113.1227, "latitude": 23.0288, "timezone": 8, "adcode": "440600"},
    {"name": "东莞", "province": "广东", "longitude": 113.7634, "latitude": 23.0430, "timezone": 8, "adcode": "441900"},
    {"name": "珠海", "province": "广东", "longitude": 113.5767, "latitude": 22.2711, "timezone": 8, "adcode": "440400"},
    {"name": "中山", "province": "广东", "longitude": 113.3917, "latitude": 22.5176, "timezone": 8, "adcode": "442000"},
    {"name": "合肥", "province": "安徽", "longitude": 117.2272, "latitude": 31.8206, "timezone": 8, "adcode": "340100"},
    {"name": "保定", "province": "河北", "longitude": 115.4574, "latitude": 38.8403, "timezone": 8, "adcode": "130600"},
    {"name": "唐山", "province": "河北", "longitude": 118.1802, "latitude": 39.6309, "timezone": 8, "adcode": "130200"},
    {"name": "香港", "province": "香港", "longitude": 114.1694, "latitude": 22.3193, "timezone": 8, "adcode": "810000"},
    {"name": "澳门", "province": "澳门", "longitude": 113.5491, "latitude": 22.1987, "timezone": 8, "adcode": "820000"},
    {"name": "台北", "province": "台湾", "longitude": 121.5654, "latitude": 25.0330, "timezone": 8, "adcode": "710000"},
    {"name": "高雄", "province": "台湾", "longitude": 120.2975, "latitude": 22.6273, "timezone": 8, "adcode": "710800"},
    {"name": "新加坡", "province": "新加坡", "longitude": 103.8198, "latitude": 1.3521, "timezone": 8, "country": "SG"},
    {"name": "纽约", "province": "美国", "longitude": -74.0060, "latitude": 40.7128, "timezone": -5, "country": "US"},
    {"name": "洛杉矶", "province": "美国", "longitude": -118.2437, "latitude": 34.0522, "timezone": -8, "country": "US"},
    {"name": "伦敦", "province": "英国", "longitude": -0.1276, "latitude": 51.5074, "timezone": 0, "country": "GB"},
    {"name": "东京", "province": "日本", "longitude": 139.6917, "latitude": 35.6895, "timezone": 9, "country": "JP"},
    {"name": "悉尼", "province": "澳大利亚", "longitude": 151.2093, "latitude": -33.8688, "timezone": 10, "country": "AU"},
]

# 十神释义数据
SHISHEN_DATA = [
    {
        "name": "比肩", "wuxing": "木", "yinyang": "阳",
        "definition": "五行与我相同者，阳干见阳干，阴干见阴干。比肩代表兄弟、同事、朋友、合作者。",
        "personality": "独立自主，刚健有力，不依赖他人，重信用。",
        "conditions": "身旺用比肩则朋友助力，身弱比肩则竞争破耗。",
        "preferences": "身旺宜官杀制比，身弱宜印绶生比。",
    },
    {
        "name": "劫财", "wuxing": "木", "yinyang": "阴",
        "definition": "五行与我相同者，阳干见阴干，阴干见阳干。劫财代表竞争、破财、异性缘分。",
        "personality": "争强好胜，冒险激进，慷慨大方，不服输。",
        "conditions": "身旺劫财旺则财来财去，身弱劫财则破财伤病。",
        "preferences": "身旺用食伤生财制劫，身弱用印绶化劫。",
    },
    {
        "name": "食神", "wuxing": "火", "yinyang": "阳",
        "definition": "我生之五行，阳干见阳干。食神代表福气、才华、儿女、饮食、思想。",
        "personality": "温和善良，聪明伶俐，乐观开朗，有口福。",
        "conditions": "食神为用则福气深厚，身旺食神泄秀则才华横溢。",
        "preferences": "食神最宜身旺，有财来生，身弱食神旺则反为消耗。",
    },
    {
        "name": "伤官", "wuxing": "火", "yinyang": "阴",
        "definition": "我生之五行，阳干见阴干。伤官代表才华、创新、口舌、叛逆、伤病。",
        "personality": "聪明过人，不受约束，言语犀利，爱表现。",
        "conditions": "伤官为用则才华横溢，身旺伤官旺则恃才傲物。",
        "preferences": "伤官宜配印（伤官配印），化伤为权；不宜多见官星。",
    },
    {
        "name": "偏财", "wuxing": "水", "yinyang": "阳",
        "definition": "我克之五行，阳干见阳干。偏财代表父亲、情人、意外之财、投机财运。",
        "personality": "慷慨大方，善于交际，精明能干，喜欢冒险。",
        "conditions": "偏财为用则财运亨通，身旺偏财旺则异性缘佳。",
        "preferences": "偏财宜身旺能任，弱则不聚财；配官杀护财则贵。",
    },
    {
        "name": "正财", "wuxing": "水", "yinyang": "阴",
        "definition": "我克之五行，阴干见阴干。正财代表正当财富、节俭、妻子、固定资产。",
        "personality": "勤俭节约，踏实稳重，理财有方，重视家庭。",
        "conditions": "正财为用则家业丰厚，身旺正财稳则婚姻和睦。",
        "preferences": "正财宜身旺能任，身弱财旺则反为财所累。",
    },
    {
        "name": "七杀", "wuxing": "金", "yinyang": "阳",
        "definition": "克我之五行，阳干见阳干。七杀代表压力、挑战、权力、权威、伤病灾。",
        "personality": "刚强果断，有魄力胆识，嫉恶如仇，敢作敢为。",
        "conditions": "七杀有制则化为权，无制则伤病灾祸。",
        "preferences": "七杀宜有食神制或印绶化，或日主身旺任杀。",
    },
    {
        "name": "正官", "wuxing": "金", "yinyang": "阴",
        "definition": "克我之五行，阴干见阴干。正官代表官运、约束、责任、法律、丈夫。",
        "personality": "循规蹈矩，有责任心，正直守法，名誉心重。",
        "conditions": "正官为用则仕途顺遂，身旺官清则受尊重。",
        "preferences": "正官宜身旺配合，有财生官则贵，有伤官则破格。",
    },
    {
        "name": "偏印", "wuxing": "水", "yinyang": "阳",
        "definition": "生我之五行，阳干见阳干。偏印代表权谋、学术、继母、偏门学问。",
        "personality": "独立思考，悟性极高，擅长钻研，不喜社交。",
        "conditions": "偏印为用则有一技之长，身旺偏印旺则孤独固执。",
        "preferences": "偏印宜有财星破之，有食神制之则吉。",
    },
    {
        "name": "正印", "wuxing": "水", "yinyang": "阴",
        "definition": "生我之五行，阴干见阴干。正印代表学业、名誉、母亲、慈悲、权力根基。",
        "personality": "仁慈厚道，有爱心，学识渊博，名声好。",
        "conditions": "正印为用则学业有成，身旺印旺则依赖心重。",
        "preferences": "正印宜身旺有托，弱则印来生身；不宜财星太旺。",
    },
]

# 五行释义
WUXING_DATA = [
    {
        "name": "木", "yinyang": "阳",
        "meaning": "木曰曲直，代表生长、仁慈、条达、东方青色。木主生发，有仁慈之心。",
        "states": "旺于春月（寅卯月），相于冬月（亥子月），休于夏月（巳午月），囚于四季土月，死于秋月（申酉月）。",
        "preferences": "木旺宜金砍伐；木弱宜水生扶。",
    },
    {
        "name": "火", "yinyang": "阳",
        "meaning": "火曰炎上，代表热情、文明、礼仪、南方赤色。火主礼，有文明之象。",
        "states": "旺于夏月（巳午月），相于春月（寅卯月），休于四季土月，囚于秋月（申酉月），死于冬月（亥子月）。",
        "preferences": "火旺宜水克制；火弱宜木生扶。",
    },
    {
        "name": "土", "yinyang": "阳",
        "meaning": "土曰稼穑，代表诚信、中庸、信义、中央黄色。土主信，有忠厚诚实之象。",
        "states": "旺于四季末月（辰戌丑未），相于夏月（巳午月），休于秋月（申酉月），囚于冬月（亥子月），死于春月（寅卯月）。",
        "preferences": "土旺宜木疏之；土弱宜火生之。",
    },
    {
        "name": "金", "yinyang": "阳",
        "meaning": "金曰从革，代表刚毅、义气、决断、西方白色。金主义，有肃杀之气。",
        "states": "旺于秋月（申酉月），相于四季土月（辰戌丑未），休于冬月（亥子月），囚于春月（寅卯月），死于夏月（巳午月）。",
        "preferences": "金旺宜火炼之；金弱宜土生之。",
    },
    {
        "name": "水", "yinyang": "阴",
        "meaning": "水曰润下，代表智慧、变通、流动性、北方黑色。水主智，有灵活变通之象。",
        "states": "旺于冬月（亥子月），相于秋月（申酉月），休于春月（寅卯月），囚于夏月（巳午月），死于四季土月。",
        "preferences": "水旺宜土制之；水弱宜金生之。",
    },
]

# 格局规则
GESHl_DATA = [
    {
        "name": "正官格", "category": "正格",
        "conditions": '{"month_stem": "正官"}',
        "jixiong": "吉",
        "interpretation": "以正官为月令之主气。正官代表约束、责任、名誉。成格者多为公职人员，循规蹈矩，有责任心。忌伤官见官，宜财印相随。",
        "source_book": "《子平真诠》《三命通会》",
    },
    {
        "name": "七杀格", "category": "正格",
        "conditions": '{"month_stem": "七杀"}',
        "jixiong": "中",
        "interpretation": "以七杀为月令之主气。七杀代表压力、挑战、权力。成格者多为创业者、企业家，有魄力敢闯。忌无制化，制化得宜则杀印相生，权柄自掌。",
        "source_book": "《子平真诠》《滴天髓》",
    },
    {
        "name": "正财格", "category": "正格",
        "conditions": '{"month_stem": "正财"}',
        "jixiong": "吉",
        "interpretation": "以正财为月令之主气。正财代表正当财富、节俭、妻子。成格者勤俭持家，理财有方，婚姻稳定。宜身旺能任财，忌日主太弱。",
        "source_book": "《三命通会》《渊海子平》",
    },
    {
        "name": "偏财格", "category": "正格",
        "conditions": '{"month_stem": "偏财"}',
        "jixiong": "中",
        "interpretation": "以偏财为月令之主气。偏财代表父亲、情人、投机财运。成格者善于经营，人缘佳，财运大起大落。宜身旺敢闯，忌坐实偏财。",
        "source_book": "《三命通会》",
    },
    {
        "name": "正印格", "category": "正格",
        "conditions": '{"month_stem": "正印"}',
        "jixiong": "吉",
        "interpretation": "以正印为月令之主气。正印代表学业、名誉、母亲、权力根基。成格者学业有成，名声好，有靠山。忌财星坏印。",
        "source_book": "《子平真诠》《三命通会》",
    },
    {
        "name": "偏印格", "category": "正格",
        "conditions": '{"month_stem": "偏印"}',
        "jixiong": "中",
        "interpretation": "以偏印为月令之主气。偏印代表权谋、学术、继母。成格者有一技之长，独立钻研，擅长偏门学问。忌财星破印，宜食神泄秀。",
        "source_book": "《滴天髓》《穷通宝鉴》",
    },
    {
        "name": "食神格", "category": "正格",
        "conditions": '{"month_stem": "食神"}',
        "jixiong": "吉",
        "interpretation": "以食神为月令之主气。食神代表福气、才华、儿女。成格者福气深厚，聪明伶俐，儿女孝顺。忌偏印夺食，宜财星引透。",
        "source_book": "《子平真诠》《三命通会》",
    },
    {
        "name": "伤官格", "category": "正格",
        "conditions": '{"month_stem": "伤官"}',
        "jixiong": "中",
        "interpretation": "以伤官为月令之主气。伤官代表才华、创新、口舌。成格者才华横溢，思维敏捷，不受束缚。宜伤官配印或伤官生财，忌伤官见官。",
        "source_book": "《子平真诠》《滴天髓》",
    },
    {
        "name": "从财格", "category": "从格",
        "conditions": '{"day_master_wuxing": "财", "total_wealth_ratio": ">0.8"}',
        "jixiong": "吉",
        "interpretation": "日主极弱，满局财星，不得不从财。成格者富甲一方，善于经营理财，以财为用。",
        "source_book": "《滴天髓》《穷通宝鉴》",
    },
    {
        "name": "从杀格", "category": "从格",
        "conditions": '{"day_master_wuxing": "官杀", "total_official_ratio": ">0.8"}',
        "jixiong": "吉",
        "interpretation": "日主极弱，满局官杀，不得不从杀。成格者权柄在握，有领导力，贵气逼人。",
        "source_book": "《滴天髓》",
    },
    {
        "name": "从儿格", "category": "从格",
        "conditions": '{"day_master_wuxing": "食伤", "total_food_god_ratio": ">0.8"}',
        "jixiong": "吉",
        "interpretation": "日主极弱，满局食伤，不得不从儿。成格者聪明绝顶，才华横溢，儿女有出息。",
        "source_book": "《滴天髓》",
    },
]


def init_cities(db):
    """初始化城市数据"""
    for city_data in CITY_DATA:
        existing = db.query(City).filter(City.name == city_data["name"]).first()
        if not existing:
            city = City(**city_data)
            db.add(city)
    db.commit()
    print(f"已初始化 {len(CITY_DATA)} 条城市数据")


def init_shishen(db):
    """初始化十神数据"""
    for entry in SHISHEN_DATA:
        existing = db.query(ShishenEntry).filter(ShishenEntry.name == entry["name"]).first()
        if not existing:
            db.add(ShishenEntry(**entry))
    db.commit()
    print(f"已初始化 {len(SHISHEN_DATA)} 条十神数据")


def init_wuxing(db):
    """初始化五行数据"""
    for entry in WUXING_DATA:
        existing = db.query(WuxingEntry).filter(WuxingEntry.name == entry["name"]).first()
        if not existing:
            db.add(WuxingEntry(**entry))
    db.commit()
    print(f"已初始化 {len(WUXING_DATA)} 条五行数据")


def init_geshi(db):
    """初始化格局数据"""
    for entry in GESHl_DATA:
        existing = db.query(GeshiRule).filter(GeshiRule.name == entry["name"]).first()
        if not existing:
            db.add(GeshiRule(**entry))
    db.commit()
    print(f"已初始化 {len(GESHl_DATA)} 条格局数据")


def main():
    """主函数"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        init_cities(db)
        init_shishen(db)
        init_wuxing(db)
        init_geshi(db)
        print("数据库初始化完成！")
    finally:
        db.close()


if __name__ == "__main__":
    main()
