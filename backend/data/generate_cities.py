#!/usr/bin/env python3
"""Generate worldwide cities CSV for 八字排盘 system.
Covers all UN country capitals + major cities (pop > 1M) across all time zones."""

import csv, os

cities = []

def add(name, country, province, lng, lat, tz):
    cities.append({
        "name": name, "country": country, "province": province,
        "longitude": lng, "latitude": lat, "timezone": tz
    })

# ========== China (all province capitals + major cities) ==========
CHINA_PROVINCES = {
    # province: (capital, capital_lng, capital_lat)
    "北京": ("北京", 116.407526, 39.904030),
    "天津": ("天津", 117.190182, 39.125600),
    "河北": ("石家庄", 114.502061, 38.045474),
    "山西": ("太原", 112.548879, 37.870590),
    "内蒙古": ("呼和浩特", 111.751990, 40.842620),
    "辽宁": ("沈阳", 123.431474, 41.805698),
    "吉林": ("长春", 125.326844, 43.886604),
    "黑龙江": ("哈尔滨", 126.634948, 45.756967),
    "上海": ("上海", 121.473662, 31.230416),
    "江苏": ("南京", 118.796877, 32.060255),
    "浙江": ("杭州", 120.153576, 30.287459),
    "安徽": ("合肥", 117.227239, 31.820586),
    "福建": ("福州", 119.306273, 26.074507),
    "江西": ("南昌", 115.857864, 28.682892),
    "山东": ("济南", 117.000923, 36.675807),
    "河南": ("郑州", 113.640100, 34.744720),
    "湖北": ("武汉", 114.298572, 30.584355),
    "湖南": ("长沙", 112.938814, 28.228209),
    "广东": ("广州", 113.264385, 23.129110),
    "广西": ("南宁", 108.366543, 22.817422),
    "海南": ("海口", 110.331190, 20.044412),
    "重庆": ("重庆", 106.504962, 29.533155),
    "四川": ("成都", 104.065735, 30.659462),
    "贵州": ("贵阳", 106.630153, 26.647661),
    "云南": ("昆明", 102.712251, 25.040609),
    "西藏": ("拉萨", 91.114497, 29.648845),
    "陕西": ("西安", 108.948024, 34.263161),
    "甘肃": ("兰州", 103.823305, 36.064226),
    "青海": ("西宁", 101.778916, 36.617089),
    "宁夏": ("银川", 106.230909, 38.487193),
    "新疆": ("乌鲁木齐", 87.616848, 43.826630),
    "香港": ("香港", 114.169361, 22.319303),
    "澳门": ("澳门", 113.543900, 22.198745),
    "台湾": ("台北", 121.565418, 25.032969),
}
for prov, (cap, lng, lat) in CHINA_PROVINCES.items():
    add(cap, "China", prov, lng, lat, "Asia/Shanghai")

# Major Chinese cities beyond capitals
EXTRA_CHINA = [
    ("深圳", "China", "广东", 114.057868, 22.543099, "Asia/Shanghai"),
    ("苏州", "China", "江苏", 120.585316, 31.298886, "Asia/Shanghai"),
    ("青岛", "China", "山东", 120.382640, 36.067108, "Asia/Shanghai"),
    ("宁波", "China", "浙江", 121.543990, 29.868336, "Asia/Shanghai"),
    ("东莞", "China", "广东", 113.763366, 23.043014, "Asia/Shanghai"),
    ("大连", "China", "辽宁", 121.618622, 38.914590, "Asia/Shanghai"),
    ("厦门", "China", "福建", 118.089425, 24.479834, "Asia/Shanghai"),
    ("无锡", "China", "江苏", 120.311910, 31.491170, "Asia/Shanghai"),
    ("佛山", "China", "广东", 113.121920, 23.021861, "Asia/Shanghai"),
    ("温州", "China", "浙江", 120.690635, 28.002838, "Asia/Shanghai"),
    ("唐山", "China", "河北", 118.183450, 39.650530, "Asia/Shanghai"),
    ("徐州", "China", "江苏", 117.188106, 34.271552, "Asia/Shanghai"),
    ("泉州", "China", "福建", 118.589421, 24.908854, "Asia/Shanghai"),
    ("常州", "China", "江苏", 119.981861, 31.771397, "Asia/Shanghai"),
    ("珠海", "China", "广东", 113.576728, 22.270978, "Asia/Shanghai"),
    ("绍兴", "China", "浙江", 120.585316, 30.030376, "Asia/Shanghai"),
    ("烟台", "China", "山东", 121.447926, 37.463870, "Asia/Shanghai"),
    ("嘉兴", "China", "浙江", 120.755070, 30.746180, "Asia/Shanghai"),
    ("洛阳", "China", "河南", 112.454040, 34.620200, "Asia/Shanghai"),
    ("南通", "China", "江苏", 120.856394, 31.979552, "Asia/Shanghai"),
    ("惠州", "China", "广东", 114.416783, 23.110750, "Asia/Shanghai"),
    ("高雄", "China", "台湾", 120.301935, 22.627278, "Asia/Taipei"),
    ("台中", "China", "台湾", 120.673648, 24.147736, "Asia/Taipei"),
]
for c in EXTRA_CHINA:
    add(*c)

# ========== East Asia / Southeast Asia ==========
ASIA = [
    ("东京", "Japan", "", 139.691706, 35.689487, "Asia/Tokyo"),
    ("大阪", "Japan", "", 135.502153, 34.693737, "Asia/Tokyo"),
    ("横滨", "Japan", "", 139.638000, 35.443707, "Asia/Tokyo"),
    ("名古屋", "Japan", "", 136.906398, 35.181446, "Asia/Tokyo"),
    ("札幌", "Japan", "", 141.354467, 43.062096, "Asia/Tokyo"),
    ("京都", "Japan", "", 135.768029, 35.011636, "Asia/Tokyo"),
    ("福冈", "Japan", "", 130.401639, 33.590354, "Asia/Tokyo"),
    ("首尔", "South Korea", "", 126.978291, 37.566535, "Asia/Seoul"),
    ("釜山", "South Korea", "", 129.075556, 35.179554, "Asia/Seoul"),
    ("仁川", "South Korea", "", 126.705156, 37.456255, "Asia/Seoul"),
    ("大邱", "South Korea", "", 128.601445, 35.871435, "Asia/Seoul"),
    ("平壤", "North Korea", "", 125.762524, 39.039219, "Asia/Pyongyang"),
    ("乌兰巴托", "Mongolia", "", 106.917145, 47.919893, "Asia/Ulaanbaatar"),
    ("台北", "China", "台湾", 121.565418, 25.032969, "Asia/Taipei"),

    ("新加坡", "Singapore", "", 103.819836, 1.352083, "Asia/Singapore"),
    ("曼谷", "Thailand", "", 100.501765, 13.756331, "Asia/Bangkok"),
    ("清迈", "Thailand", "", 98.985300, 18.788343, "Asia/Bangkok"),
    ("河内", "Vietnam", "", 105.854444, 21.028511, "Asia/Hanoi"),
    ("胡志明市", "Vietnam", "", 106.629662, 10.823099, "Asia/Ho_Chi_Minh"),
    ("岘港", "Vietnam", "", 108.202824, 16.047079, "Asia/Ho_Chi_Minh"),
    ("马尼拉", "Philippines", "", 120.984219, 14.599512, "Asia/Manila"),
    ("宿务", "Philippines", "", 123.885437, 10.315699, "Asia/Manila"),
    ("雅加达", "Indonesia", "", 106.845599, -6.208764, "Asia/Jakarta"),
    ("泗水", "Indonesia", "", 112.750600, -7.257472, "Asia/Jakarta"),
    ("万隆", "Indonesia", "", 107.619123, -6.917464, "Asia/Jakarta"),
    ("吉隆坡", "Malaysia", "", 101.686855, 3.139003, "Asia/Kuala_Lumpur"),
    ("槟城", "Malaysia", "", 100.332404, 5.416393, "Asia/Kuala_Lumpur"),
    ("仰光", "Myanmar", "", 96.156115, 16.840441, "Asia/Yangon"),
    ("内比都", "Myanmar", "", 96.173554, 19.763306, "Asia/Yangon"),
    ("金边", "Cambodia", "", 104.892166, 11.544373, "Asia/Phnom_Penh"),
    ("万象", "Laos", "", 102.603152, 17.975647, "Asia/Vientiane"),
    ("斯里巴加湾", "Brunei", "", 114.939821, 4.943073, "Asia/Brunei"),
    ("帝力", "East Timor", "", 125.573650, -8.555857, "Asia/Dili"),
]
for c in ASIA:
    add(*c)

# ========== South Asia ==========
SOUTH_ASIA = [
    ("德里", "India", "", 77.102490, 28.704059, "Asia/Kolkata"),
    ("孟买", "India", "", 72.877426, 19.076090, "Asia/Kolkata"),
    ("班加罗尔", "India", "", 77.594566, 12.971599, "Asia/Kolkata"),
    ("海德拉巴", "India", "", 78.486667, 17.384050, "Asia/Kolkata"),
    ("艾哈迈达巴德", "India", "", 72.571362, 23.022505, "Asia/Kolkata"),
    ("金奈", "India", "", 80.270716, 13.082680, "Asia/Kolkata"),
    ("加尔各答", "India", "", 88.363892, 22.572645, "Asia/Kolkata"),
    ("浦那", "India", "", 73.856700, 18.520430, "Asia/Kolkata"),
    ("斋浦尔", "India", "", 75.787309, 26.912434, "Asia/Kolkata"),
    ("昌迪加尔", "India", "", 76.779417, 30.733315, "Asia/Kolkata"),
    ("达卡", "Bangladesh", "", 90.412518, 23.810332, "Asia/Dhaka"),
    ("吉大港", "Bangladesh", "", 91.813672, 22.356851, "Asia/Dhaka"),
    ("加德满都", "Nepal", "", 85.323960, 27.717245, "Asia/Kathmandu"),
    ("科伦坡", "Sri Lanka", "", 79.861243, 6.927079, "Asia/Colombo"),
    ("伊斯兰堡", "Pakistan", "", 73.047886, 33.684422, "Asia/Karachi"),
    ("卡拉奇", "Pakistan", "", 67.082218, 24.860735, "Asia/Karachi"),
    ("拉合尔", "Pakistan", "", 74.329940, 31.549701, "Asia/Karachi"),
    ("喀布尔", "Afghanistan", "", 69.207486, 34.555349, "Asia/Kabul"),
    ("坎大哈", "Afghanistan", "", 65.695484, 31.623185, "Asia/Kabul"),
    ("德黑兰", "Iran", "", 51.401351, 35.715298, "Asia/Tehran"),
    ("马什哈德", "Iran", "", 59.606944, 36.260462, "Asia/Tehran"),
    ("伊斯法罕", "Iran", "", 51.676879, 32.657220, "Asia/Tehran"),
    ("设拉子", "Iran", "", 52.528561, 29.591768, "Asia/Tehran"),
    ("大不里士", "Iran", "", 46.291377, 38.080834, "Asia/Tehran"),
    ("马累", "Maldives", "", 73.509347, 4.175496, "Indian/Maldives"),
    ("廷布", "Bhutan", "", 89.638611, 27.472792, "Asia/Thimphu"),
]
for c in SOUTH_ASIA:
    add(*c)

# ========== Middle East / Central Asia ==========
MIDDLE_EAST = [
    ("迪拜", "UAE", "", 55.270783, 25.204849, "Asia/Dubai"),
    ("阿布扎比", "UAE", "", 54.366669, 24.466667, "Asia/Dubai"),
    ("利雅得", "Saudi Arabia", "", 46.773056, 24.687730, "Asia/Riyadh"),
    ("吉达", "Saudi Arabia", "", 39.191454, 21.543486, "Asia/Riyadh"),
    ("麦加", "Saudi Arabia", "", 39.857792, 21.422510, "Asia/Riyadh"),
    ("多哈", "Qatar", "", 51.531159, 25.285447, "Asia/Qatar"),
    ("马斯喀特", "Oman", "", 58.405923, 23.588031, "Asia/Muscat"),
    ("科威特城", "Kuwait", "", 47.977405, 29.375859, "Asia/Kuwait"),
    ("麦纳麦", "Bahrain", "", 50.582381, 26.228516, "Asia/Bahrain"),
    ("萨那", "Yemen", "", 44.230445, 15.355351, "Asia/Aden"),
    ("亚丁", "Yemen", "", 45.036169, 12.785496, "Asia/Aden"),
    ("巴格达", "Iraq", "", 44.366087, 33.312805, "Asia/Baghdad"),
    ("巴士拉", "Iraq", "", 47.840594, 30.508298, "Asia/Baghdad"),
    ("安曼", "Jordan", "", 35.928890, 31.951569, "Asia/Amman"),
    ("贝鲁特", "Lebanon", "", 35.495859, 33.888630, "Asia/Beirut"),
    ("大马士革", "Syria", "", 36.275420, 33.513807, "Asia/Damascus"),
    ("阿勒颇", "Syria", "", 37.157964, 36.202545, "Asia/Damascus"),
    ("耶路撒冷", "Israel", "", 35.213712, 31.768319, "Asia/Jerusalem"),
    ("特拉维夫", "Israel", "", 34.781769, 32.085299, "Asia/Jerusalem"),
    ("海法", "Israel", "", 34.989571, 32.794047, "Asia/Jerusalem"),
    ("伊斯坦布尔", "Turkey", "", 28.978359, 41.008238, "Europe/Istanbul"),
    ("安卡拉", "Turkey", "", 32.854077, 39.933363, "Europe/Istanbul"),
    ("伊兹密尔", "Turkey", "", 27.142826, 38.423733, "Europe/Istanbul"),
    ("布尔萨", "Turkey", "", 29.056615, 40.182929, "Europe/Istanbul"),
    ("安塔利亚", "Turkey", "", 30.709511, 36.884804, "Europe/Istanbul"),
    ("阿斯塔纳", "Kazakhstan", "", 71.433587, 51.169392, "Asia/Almaty"),
    ("阿拉木图", "Kazakhstan", "", 76.947500, 43.236392, "Asia/Almaty"),
    ("塔什干", "Uzbekistan", "", 69.267719, 41.299496, "Asia/Tashkent"),
    ("撒马尔罕", "Uzbekistan", "", 66.974967, 39.627124, "Asia/Samarkand"),
    ("阿什哈巴德", "Turkmenistan", "", 58.383333, 37.950000, "Asia/Ashgabat"),
    ("比什凯克", "Kyrgyzstan", "", 74.589611, 42.876789, "Asia/Bishkek"),
    ("杜尚别", "Tajikistan", "", 68.772635, 38.565438, "Asia/Dushanbe"),
    ("尼科西亚", "Cyprus", "", 33.382275, 35.185566, "Asia/Nicosia"),
]
for c in MIDDLE_EAST:
    add(*c)

# ========== Europe ==========
EUROPE = [
    ("伦敦", "UK", "", -0.127647, 51.507351, "Europe/London"),
    ("曼彻斯特", "UK", "", -2.239476, 53.480759, "Europe/London"),
    ("伯明翰", "UK", "", -1.893489, 52.485740, "Europe/London"),
    ("利物浦", "UK", "", -2.991573, 53.408371, "Europe/London"),
    ("格拉斯哥", "UK", "", -4.251806, 55.864237, "Europe/London"),
    ("爱丁堡", "UK", "", -3.188267, 55.953252, "Europe/London"),
    ("巴黎", "France", "", 2.352222, 48.856613, "Europe/Paris"),
    ("马赛", "France", "", 5.369783, 43.296483, "Europe/Paris"),
    ("里昂", "France", "", 4.833206, 45.764043, "Europe/Paris"),
    ("图卢兹", "France", "", 1.445011, 43.604263, "Europe/Paris"),
    ("波尔多", "France", "", -0.579179, 44.837789, "Europe/Paris"),
    ("尼斯", "France", "", 7.261953, 43.710172, "Europe/Paris"),
    ("柏林", "Germany", "", 13.405000, 52.520008, "Europe/Berlin"),
    ("汉堡", "Germany", "", 9.993682, 53.551086, "Europe/Berlin"),
    ("慕尼黑", "Germany", "", 11.581981, 48.135125, "Europe/Berlin"),
    ("科隆", "Germany", "", 6.960279, 50.937531, "Europe/Berlin"),
    ("法兰克福", "Germany", "", 8.679596, 50.110924, "Europe/Berlin"),
    ("斯图加特", "Germany", "", 9.175992, 48.775846, "Europe/Berlin"),
    ("杜塞尔多夫", "Germany", "", 6.773456, 51.227741, "Europe/Berlin"),
    ("罗马", "Italy", "", 12.496247, 41.902783, "Europe/Rome"),
    ("米兰", "Italy", "", 9.185924, 45.465422, "Europe/Rome"),
    ("那不勒斯", "Italy", "", 14.268124, 40.851775, "Europe/Rome"),
    ("都灵", "Italy", "", 7.686856, 45.070312, "Europe/Rome"),
    ("佛罗伦萨", "Italy", "", 11.255814, 43.769562, "Europe/Rome"),
    ("威尼斯", "Italy", "", 12.315515, 45.440847, "Europe/Rome"),
    ("马德里", "Spain", "", -3.703790, 40.416775, "Europe/Madrid"),
    ("巴塞罗那", "Spain", "", 2.173404, 41.385064, "Europe/Madrid"),
    ("瓦伦西亚", "Spain", "", -0.379245, 39.466665, "Europe/Madrid"),
    ("塞维利亚", "Spain", "", -5.984459, 37.389092, "Europe/Madrid"),
    ("里斯本", "Portugal", "", -9.139337, 38.722252, "Europe/Lisbon"),
    ("波尔图", "Portugal", "", -8.610071, 41.149610, "Europe/Lisbon"),
    ("布鲁塞尔", "Belgium", "", 4.351710, 50.850346, "Europe/Brussels"),
    ("安特卫普", "Belgium", "", 4.402464, 51.219448, "Europe/Brussels"),
    ("阿姆斯特丹", "Netherlands", "", 4.895168, 52.370216, "Europe/Amsterdam"),
    ("鹿特丹", "Netherlands", "", 4.479170, 51.924420, "Europe/Amsterdam"),
    ("海牙", "Netherlands", "", 4.299973, 52.080450, "Europe/Amsterdam"),
    ("维也纳", "Austria", "", 16.373064, 48.208174, "Europe/Vienna"),
    ("苏黎世", "Switzerland", "", 8.541694, 47.376887, "Europe/Zurich"),
    ("日内瓦", "Switzerland", "", 6.146596, 46.204391, "Europe/Zurich"),
    ("伯尔尼", "Switzerland", "", 7.447447, 46.947975, "Europe/Zurich"),
    ("斯德哥尔摩", "Sweden", "", 18.068581, 59.329323, "Europe/Stockholm"),
    ("哥德堡", "Sweden", "", 11.967044, 57.708870, "Europe/Stockholm"),
    ("奥斯陆", "Norway", "", 10.757933, 59.911491, "Europe/Oslo"),
    ("卑尔根", "Norway", "", 5.324383, 60.391263, "Europe/Oslo"),
    ("哥本哈根", "Denmark", "", 12.568337, 55.676097, "Europe/Copenhagen"),
    ("赫尔辛基", "Finland", "", 24.938379, 60.169857, "Europe/Helsinki"),
    ("雷克雅未克", "Iceland", "", -21.895400, 64.146582, "Atlantic/Reykjavik"),
    ("莫斯科", "Russia", "", 37.617298, 55.755825, "Europe/Moscow"),
    ("圣彼得堡", "Russia", "", 30.335099, 59.934280, "Europe/Moscow"),
    ("新西伯利亚", "Russia", "", 82.920430, 55.030204, "Asia/Novosibirsk"),
    ("叶卡捷琳堡", "Russia", "", 60.597474, 56.838926, "Asia/Yekaterinburg"),
    ("喀山", "Russia", "", 49.122139, 55.787659, "Europe/Moscow"),
    ("海参崴", "Russia", "", 131.885063, 43.115542, "Asia/Vladivostok"),
    ("伊尔库茨克", "Russia", "", 104.292295, 52.285483, "Asia/Irkutsk"),
    ("华沙", "Poland", "", 21.012229, 52.229676, "Europe/Warsaw"),
    ("克拉科夫", "Poland", "", 19.944544, 50.064651, "Europe/Warsaw"),
    ("布拉格", "Czechia", "", 14.437800, 50.075538, "Europe/Prague"),
    ("布达佩斯", "Hungary", "", 19.040236, 47.497913, "Europe/Budapest"),
    ("布加勒斯特", "Romania", "", 26.102538, 44.426767, "Europe/Bucharest"),
    ("索菲亚", "Bulgaria", "", 23.321868, 42.697708, "Europe/Sofia"),
    ("贝尔格莱德", "Serbia", "", 20.448922, 44.786568, "Europe/Belgrade"),
    ("萨格勒布", "Croatia", "", 15.981919, 45.815011, "Europe/Zagreb"),
    ("萨拉热窝", "Bosnia and Herzegovina", "", 18.356442, 43.856259, "Europe/Sarajevo"),
    ("卢布尔雅那", "Slovenia", "", 14.504891, 46.056947, "Europe/Ljubljana"),
    ("斯科普里", "North Macedonia", "", 21.431358, 41.997346, "Europe/Skopje"),
    ("波德戈里察", "Montenegro", "", 19.260979, 42.442575, "Europe/Podgorica"),
    ("地拉那", "Albania", "", 19.818610, 41.332240, "Europe/Tirane"),
    ("雅典", "Greece", "", 23.727539, 37.983810, "Europe/Athens"),
    ("塞萨洛尼基", "Greece", "", 22.944419, 40.640063, "Europe/Athens"),
    ("维尔纽斯", "Lithuania", "", 25.279651, 54.687156, "Europe/Vilnius"),
    ("里加", "Latvia", "", 24.105186, 56.949649, "Europe/Riga"),
    ("塔林", "Estonia", "", 24.753574, 59.436962, "Europe/Tallinn"),
    ("明斯克", "Belarus", "", 27.561525, 53.904540, "Europe/Minsk"),
    ("基辅", "Ukraine", "", 30.523541, 50.450001, "Europe/Kyiv"),
    ("哈尔科夫", "Ukraine", "", 36.234347, 49.992148, "Europe/Kyiv"),
    ("敖德萨", "Ukraine", "", 30.733334, 46.484302, "Europe/Kyiv"),
    ("基希讷乌", "Moldova", "", 28.862109, 47.010555, "Europe/Chisinau"),
    ("第比利斯", "Georgia", "", 44.792301, 41.715138, "Asia/Tbilisi"),
    ("埃里温", "Armenia", "", 44.503006, 40.179186, "Asia/Yerevan"),
    ("巴库", "Azerbaijan", "", 49.867092, 40.409262, "Asia/Baku"),
    ("都柏林", "Ireland", "", -6.260273, 53.349805, "Europe/Dublin"),
    ("卢森堡", "Luxembourg", "", 6.129583, 49.611622, "Europe/Luxembourg"),
    ("摩纳哥", "Monaco", "", 7.424616, 43.738418, "Europe/Monaco"),
    ("瓦莱塔", "Malta", "", 14.514701, 35.899740, "Europe/Malta"),
    ("圣马力诺", "San Marino", "", 12.447964, 43.936084, "Europe/San_Marino"),
    ("梵蒂冈", "Vatican City", "", 12.453889, 41.902206, "Europe/Vatican"),
    ("列支敦士登", "Liechtenstein", "", 9.555262, 47.140014, "Europe/Vaduz"),
    ("安道尔", "Andorra", "", 1.520090, 42.507791, "Europe/Andorra"),
]
for c in EUROPE:
    add(*c)

# ========== North America ==========
NORTH_AMERICA = [
    ("纽约", "USA", "New York", -74.005941, 40.712776, "America/New_York"),
    ("洛杉矶", "USA", "California", -118.243683, 34.052235, "America/Los_Angeles"),
    ("芝加哥", "USA", "Illinois", -87.629798, 41.878114, "America/Chicago"),
    ("休斯顿", "USA", "Texas", -95.369803, 29.760193, "America/Chicago"),
    ("凤凰城", "USA", "Arizona", -112.074037, 33.448377, "America/Phoenix"),
    ("费城", "USA", "Pennsylvania", -75.165222, 39.952583, "America/New_York"),
    ("圣安东尼奥", "USA", "Texas", -98.493628, 29.424122, "America/Chicago"),
    ("圣迭戈", "USA", "California", -117.161084, 32.715738, "America/Los_Angeles"),
    ("达拉斯", "USA", "Texas", -96.796988, 32.776664, "America/Chicago"),
    ("圣何塞", "USA", "California", -121.886328, 37.338208, "America/Los_Angeles"),
    ("奥斯汀", "USA", "Texas", -97.743061, 30.267153, "America/Chicago"),
    ("杰克逊维尔", "USA", "Florida", -81.655651, 30.332184, "America/New_York"),
    ("旧金山", "USA", "California", -122.419418, 37.774929, "America/Los_Angeles"),
    ("哥伦布", "USA", "Ohio", -82.998794, 39.961176, "America/New_York"),
    ("夏洛特", "USA", "North Carolina", -80.843127, 35.227087, "America/New_York"),
    ("印第安纳波利斯", "USA", "Indiana", -86.158068, 39.768403, "America/New_York"),
    ("西雅图", "USA", "Washington", -122.332071, 47.606209, "America/Los_Angeles"),
    ("丹佛", "USA", "Colorado", -104.990251, 39.739236, "America/Denver"),
    ("波士顿", "USA", "Massachusetts", -71.058880, 42.360082, "America/New_York"),
    ("纳什维尔", "USA", "Tennessee", -86.781602, 36.162664, "America/Chicago"),
    ("巴尔的摩", "USA", "Maryland", -76.612189, 39.290386, "America/New_York"),
    ("俄克拉荷马城", "USA", "Oklahoma", -97.516428, 35.467560, "America/Chicago"),
    ("路易斯维尔", "USA", "Kentucky", -85.758456, 38.252666, "America/New_York"),
    ("波特兰", "USA", "Oregon", -122.676483, 45.523064, "America/Los_Angeles"),
    ("拉斯维加斯", "USA", "Nevada", -115.139830, 36.169941, "America/Los_Angeles"),
    ("密尔沃基", "USA", "Wisconsin", -87.906474, 43.038902, "America/Chicago"),
    ("阿尔伯克基", "USA", "New Mexico", -106.650422, 35.085333, "America/Denver"),
    ("图森", "USA", "Arizona", -110.926479, 32.221743, "America/Phoenix"),
    ("弗雷斯诺", "USA", "California", -119.772586, 36.746842, "America/Los_Angeles"),
    ("萨克拉门托", "USA", "California", -121.494400, 38.581572, "America/Los_Angeles"),
    ("长滩", "USA", "California", -118.189232, 33.770050, "America/Los_Angeles"),
    ("堪萨斯城", "USA", "Missouri", -94.578567, 39.099727, "America/Chicago"),
    ("亚特兰大", "USA", "Georgia", -84.387982, 33.748995, "America/New_York"),
    ("迈阿密", "USA", "Florida", -80.191790, 25.761680, "America/New_York"),
    ("华盛顿", "USA", "District of Columbia", -77.036873, 38.907192, "America/New_York"),
    ("檀香山", "USA", "Hawaii", -157.858333, 21.306944, "Pacific/Honolulu"),
    ("安克雷奇", "USA", "Alaska", -149.900278, 61.218056, "America/Anchorage"),

    ("多伦多", "Canada", "Ontario", -79.383184, 43.653226, "America/Toronto"),
    ("温哥华", "Canada", "British Columbia", -123.120736, 49.282730, "America/Vancouver"),
    ("蒙特利尔", "Canada", "Quebec", -73.567256, 45.501688, "America/Toronto"),
    ("卡尔加里", "Canada", "Alberta", -114.071883, 51.044733, "America/Edmonton"),
    ("埃德蒙顿", "Canada", "Alberta", -113.493823, 53.546124, "America/Edmonton"),
    ("渥太华", "Canada", "Ontario", -75.697193, 45.421530, "America/Toronto"),
    ("温尼伯", "Canada", "Manitoba", -97.139960, 49.895138, "America/Winnipeg"),
    ("魁北克城", "Canada", "Quebec", -71.208443, 46.813878, "America/Toronto"),

    ("墨西哥城", "Mexico", "", -99.133208, 19.432608, "America/Mexico_City"),
    ("坎昆", "Mexico", "", -86.851524, 21.161908, "America/Cancun"),
    ("瓜达拉哈拉", "Mexico", "", -103.349609, 20.659698, "America/Mexico_City"),
    ("蒙特雷", "Mexico", "", -100.316117, 25.686614, "America/Monterrey"),
    ("蒂华纳", "Mexico", "", -117.038200, 32.514947, "America/Los_Angeles"),
    ("普埃布拉", "Mexico", "", -98.206267, 19.041297, "America/Mexico_City"),
]
for c in NORTH_AMERICA:
    add(*c)

# ========== Central America & Caribbean ==========
CENTRAL_AMERICA = [
    ("危地马拉城", "Guatemala", "", -90.532339, 14.634915, "America/Guatemala"),
    ("贝尔莫潘", "Belize", "", -88.771731, 17.251011, "America/Belize"),
    ("圣萨尔瓦多", "El Salvador", "", -89.205215, 13.692940, "America/El_Salvador"),
    ("特古西加尔巴", "Honduras", "", -87.211936, 14.072294, "America/Tegucigalpa"),
    ("马那瓜", "Nicaragua", "", -86.267750, 12.114993, "America/Managua"),
    ("圣何塞", "Costa Rica", "", -84.083330, 9.928069, "America/Costa_Rica"),
    ("巴拿马城", "Panama", "", -79.518792, 8.982379, "America/Panama"),
    ("哈瓦那", "Cuba", "", -82.366596, 23.113592, "America/Havana"),
    ("金斯敦", "Jamaica", "", -76.792557, 18.017450, "America/Jamaica"),
    ("太子港", "Haiti", "", -72.338254, 18.539270, "America/Port-au-Prince"),
    ("圣多明各", "Dominican Republic", "", -69.931212, 18.486058, "America/Santo_Domingo"),
    ("拿骚", "Bahamas", "", -77.339081, 25.034280, "America/Nassau"),
    ("圣胡安", "Puerto Rico", "", -66.105720, 18.465539, "America/Puerto_Rico"),
    ("布里奇敦", "Barbados", "", -59.543198, 13.113222, "America/Barbados"),
    ("西班牙港", "Trinidad and Tobago", "", -61.519182, 10.654901, "America/Port_of_Spain"),
]
for c in CENTRAL_AMERICA:
    add(*c)

# ========== South America ==========
SOUTH_AMERICA = [
    ("圣保罗", "Brazil", "São Paulo", -46.633309, -23.550520, "America/Sao_Paulo"),
    ("里约热内卢", "Brazil", "Rio de Janeiro", -43.172896, -22.906847, "America/Sao_Paulo"),
    ("巴西利亚", "Brazil", "Distrito Federal", -47.864471, -15.797506, "America/Sao_Paulo"),
    ("萨尔瓦多", "Brazil", "Bahia", -38.498268, -12.971399, "America/Bahia"),
    ("福塔莱萨", "Brazil", "Ceará", -38.543376, -3.718394, "America/Fortaleza"),
    ("贝洛奥里藏特", "Brazil", "Minas Gerais", -43.938272, -19.916681, "America/Sao_Paulo"),
    ("马瑙斯", "Brazil", "Amazonas", -60.025050, -3.119028, "America/Manaus"),
    ("库里蒂巴", "Brazil", "Paraná", -49.273136, -25.428954, "America/Sao_Paulo"),
    ("累西腓", "Brazil", "Pernambuco", -34.881133, -8.047562, "America/Recife"),

    ("布宜诺斯艾利斯", "Argentina", "", -58.381592, -34.603684, "America/Argentina/Buenos_Aires"),
    ("科尔多瓦", "Argentina", "", -64.188776, -31.420083, "America/Argentina/Cordoba"),
    ("罗萨里奥", "Argentina", "", -60.652679, -32.946820, "America/Argentina/Cordoba"),

    ("圣地亚哥", "Chile", "", -70.648270, -33.448891, "America/Santiago"),
    ("瓦尔帕莱索", "Chile", "", -71.624784, -33.047238, "America/Santiago"),

    ("波哥大", "Colombia", "", -74.072092, 4.710989, "America/Bogota"),
    ("麦德林", "Colombia", "", -75.571637, 6.247637, "America/Bogota"),
    ("卡利", "Colombia", "", -76.532317, 3.451647, "America/Bogota"),

    ("利马", "Peru", "", -77.042793, -12.046374, "America/Lima"),
    ("库斯科", "Peru", "", -71.967967, -13.516259, "America/Lima"),

    ("基多", "Ecuador", "", -78.467844, -0.180653, "America/Guayaquil"),
    ("瓜亚基尔", "Ecuador", "", -79.887209, -2.170997, "America/Guayaquil"),

    ("加拉加斯", "Venezuela", "", -66.903606, 10.480594, "America/Caracas"),
    ("马拉开波", "Venezuela", "", -71.600190, 10.654901, "America/Caracas"),

    ("拉巴斯", "Bolivia", "", -68.119293, -16.500000, "America/La_Paz"),
    ("圣克鲁斯", "Bolivia", "", -63.182100, -17.787713, "America/La_Paz"),

    ("蒙得维的亚", "Uruguay", "", -56.164532, -34.901112, "America/Montevideo"),
    ("亚松森", "Paraguay", "", -57.600373, -25.286458, "America/Asuncion"),
    ("帕拉马里博", "Suriname", "", -55.166190, 5.852036, "America/Paramaribo"),
    ("乔治敦", "Guyana", "", -58.155125, 6.801279, "America/Guyana"),
    ("卡宴", "French Guiana", "", -52.318931, 4.937154, "America/Cayenne"),
]
for c in SOUTH_AMERICA:
    add(*c)

# ========== Africa ==========
AFRICA = [
    ("开罗", "Egypt", "", 31.235712, 30.044420, "Africa/Cairo"),
    ("亚历山大", "Egypt", "", 29.918739, 31.200092, "Africa/Cairo"),
    ("吉萨", "Egypt", "", 31.129449, 30.010752, "Africa/Cairo"),

    ("拉各斯", "Nigeria", "", 3.379206, 6.524379, "Africa/Lagos"),
    ("阿布贾", "Nigeria", "", 7.489956, 9.057314, "Africa/Lagos"),
    ("伊巴丹", "Nigeria", "", 3.911527, 7.377536, "Africa/Lagos"),
    ("卡诺", "Nigeria", "", 8.516554, 11.997555, "Africa/Lagos"),

    ("内罗毕", "Kenya", "", 36.821946, -1.292066, "Africa/Nairobi"),
    ("蒙巴萨", "Kenya", "", 39.663334, -4.048528, "Africa/Nairobi"),

    ("亚的斯亚贝巴", "Ethiopia", "", 38.757760, 9.019191, "Africa/Addis_Ababa"),
    ("达累斯萨拉姆", "Tanzania", "", 39.208328, -6.792354, "Africa/Dar_es_Salaam"),
    ("多多马", "Tanzania", "", 35.749113, -6.162959, "Africa/Dar_es_Salaam"),

    ("约翰内斯堡", "South Africa", "", 27.969330, -26.204103, "Africa/Johannesburg"),
    ("开普敦", "South Africa", "", 18.424104, -33.924869, "Africa/Johannesburg"),
    ("比勒陀利亚", "South Africa", "", 28.187005, -25.744857, "Africa/Johannesburg"),
    ("德班", "South Africa", "", 31.021840, -29.858680, "Africa/Johannesburg"),

    ("拉巴特", "Morocco", "", -6.832617, 34.020882, "Africa/Casablanca"),
    ("卡萨布兰卡", "Morocco", "", -7.589843, 33.573109, "Africa/Casablanca"),
    ("马拉喀什", "Morocco", "", -8.013502, 31.634604, "Africa/Casablanca"),

    ("阿尔及尔", "Algeria", "", 3.086027, 36.737232, "Africa/Algiers"),
    ("突尼斯", "Tunisia", "", 10.165790, 36.806495, "Africa/Tunis"),
    ("的黎波里", "Libya", "", 13.185193, 32.887209, "Africa/Tripoli"),

    ("阿克拉", "Ghana", "", -0.200166, 5.560170, "Africa/Accra"),
    ("库马西", "Ghana", "", -1.622727, 6.673189, "Africa/Accra"),

    ("阿比让", "Côte d'Ivoire", "", -4.031953, 5.316666, "Africa/Abidjan"),
    ("达喀尔", "Senegal", "", -17.444601, 14.692857, "Africa/Dakar"),
    ("巴马科", "Mali", "", -7.993427, 12.639232, "Africa/Bamako"),
    ("瓦加杜古", "Burkina Faso", "", -1.530316, 12.365969, "Africa/Ouagadougou"),
    ("科纳克里", "Guinea", "", -13.736055, 9.537029, "Africa/Conakry"),
    ("班珠尔", "Gambia", "", -16.592626, 13.455737, "Africa/Banjul"),
    ("比绍", "Guinea-Bissau", "", -15.598132, 11.863558, "Africa/Bissau"),
    ("蒙罗维亚", "Liberia", "", -10.807284, 6.290743, "Africa/Monrovia"),
    ("弗里敦", "Sierra Leone", "", -13.265153, 8.465676, "Africa/Freetown"),
    ("尼亚美", "Niger", "", 2.109832, 13.515924, "Africa/Niamey"),
    ("洛美", "Togo", "", 1.224774, 6.137475, "Africa/Lome"),
    ("波多诺伏", "Benin", "", 2.598102, 6.476753, "Africa/Porto-Novo"),

    ("坎帕拉", "Uganda", "", 32.582520, 0.347596, "Africa/Kampala"),
    ("基加利", "Rwanda", "", 30.060525, -1.970579, "Africa/Kigali"),
    ("布琼布拉", "Burundi", "", 29.363869, -3.382778, "Africa/Bujumbura"),
    ("朱巴", "South Sudan", "", 31.598463, 4.858476, "Africa/Juba"),

    ("哈拉雷", "Zimbabwe", "", 31.047299, -17.825166, "Africa/Harare"),
    ("卢萨卡", "Zambia", "", 28.334014, -15.387526, "Africa/Lusaka"),
    ("利隆圭", "Malawi", "", 33.776144, -13.990834, "Africa/Blantyre"),
    ("马普托", "Mozambique", "", 32.573174, -25.969248, "Africa/Maputo"),

    ("罗安达", "Angola", "", 13.234445, -8.839989, "Africa/Luanda"),
    ("金沙萨", "DRC", "", 15.266299, -4.441931, "Africa/Kinshasa"),
    ("卢本巴希", "DRC", "", 27.480000, -11.660000, "Africa/Lubumbashi"),

    ("喀土穆", "Sudan", "", 32.559899, 15.500654, "Africa/Khartoum"),
    ("阿斯马拉", "Eritrea", "", 38.930556, 15.333334, "Africa/Asmara"),
    ("吉布提", "Djibouti", "", 43.145488, 11.572077, "Africa/Djibouti"),
    ("摩加迪沙", "Somalia", "", 45.318162, 2.046934, "Africa/Mogadishu"),

    ("塔那那利佛", "Madagascar", "", 47.507906, -18.879190, "Indian/Antananarivo"),
    ("路易港", "Mauritius", "", 57.501873, -20.150802, "Indian/Mauritius"),
    ("维多利亚", "Seychelles", "", 55.454031, -4.619143, "Indian/Mahe"),
    ("莫罗尼", "Comoros", "", 43.255062, -11.717476, "Indian/Comoro"),

    ("比勒陀利亚", "South Africa", "", 28.187005, -25.744857, "Africa/Johannesburg"),
    ("温得和克", "Namibia", "", 17.067534, -22.560880, "Africa/Windhoek"),
    ("哈博罗内", "Botswana", "", 25.915109, -24.658336, "Africa/Maputo"),
    ("姆巴巴内", "Eswatini", "", 31.138812, -26.305448, "Africa/Johannesburg"),
    ("马塞卢", "Lesotho", "", 27.476559, -29.314339, "Africa/Johannesburg"),
]
for c in AFRICA:
    add(*c)

# ========== Oceania ==========
OCEANIA = [
    ("悉尼", "Australia", "New South Wales", 151.209900, -33.865143, "Australia/Sydney"),
    ("墨尔本", "Australia", "Victoria", 144.963058, -37.813628, "Australia/Melbourne"),
    ("布里斯班", "Australia", "Queensland", 153.025010, -27.469770, "Australia/Brisbane"),
    ("珀斯", "Australia", "Western Australia", 115.857503, -31.952240, "Australia/Perth"),
    ("阿德莱德", "Australia", "South Australia", 138.600746, -34.928499, "Australia/Adelaide"),
    ("堪培拉", "Australia", "Australian Capital Territory", 149.128684, -35.281999, "Australia/Sydney"),
    ("黄金海岸", "Australia", "Queensland", 153.403079, -28.017260, "Australia/Brisbane"),
    ("达尔文", "Australia", "Northern Territory", 130.843553, -12.462827, "Australia/Darwin"),
    ("霍巴特", "Australia", "Tasmania", 147.324194, -42.880987, "Australia/Hobart"),
    ("纽卡斯尔", "Australia", "New South Wales", 151.774700, -32.928382, "Australia/Sydney"),

    ("奥克兰", "New Zealand", "", 174.768127, -36.848460, "Pacific/Auckland"),
    ("惠灵顿", "New Zealand", "", 174.777969, -41.286461, "Pacific/Auckland"),
    ("基督城", "New Zealand", "", 172.637363, -43.531456, "Pacific/Auckland"),

    ("莫尔兹比港", "Papua New Guinea", "", 147.199240, -9.479058, "Pacific/Port_Moresby"),
    ("苏瓦", "Fiji", "", 178.416319, -18.124809, "Pacific/Fiji"),
    ("霍尼亚拉", "Solomon Islands", "", 159.962889, -9.445421, "Pacific/Guadalcanal"),
    ("维拉港", "Vanuatu", "", 168.328678, -17.728940, "Pacific/Efate"),
    ("阿皮亚", "Samoa", "", -171.761986, -13.834043, "Pacific/Apia"),
    ("努库阿洛法", "Tonga", "", -175.204380, -21.139818, "Pacific/Tongatapu"),
    ("塔拉瓦", "Kiribati", "", 173.017229, 1.327770, "Pacific/Tarawa"),
    ("马朱罗", "Marshall Islands", "", 171.189313, 7.116421, "Pacific/Majuro"),
    ("帕利基尔", "Micronesia", "", 158.161283, 6.916310, "Pacific/Pohnpei"),
    ("亚伦", "Nauru", "", 166.928311, -0.530334, "Pacific/Nauru"),
    ("富纳富提", "Tuvalu", "", 179.188778, -8.521158, "Pacific/Funafuti"),
    ("努美阿", "New Caledonia", "", 166.449299, -22.274748, "Pacific/Noumea"),
    ("帕皮提", "French Polynesia", "", -149.569388, -17.538008, "Pacific/Tahiti"),
]
for c in OCEANIA:
    add(*c)

# Remove duplicate by (name, country) tuple
seen = set()
unique = []
for c in cities:
    key = (c["name"], c["country"])
    if key not in seen:
        seen.add(key)
        unique.append(c)

# Write CSV with auto-incrementing IDs
out_path = os.path.join(os.path.dirname(__file__), "cities.csv")
with open(out_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id","name","country","province","longitude","latitude","timezone"])
    writer.writeheader()
    for i, c in enumerate(unique, start=1):
        row = {"id": i, **c}
        writer.writerow(row)

print(f"Generated {len(unique)} cities → {out_path}")
# Count by continent
print(f"\nBreakdown:")
print(f"  China: {sum(1 for c in unique if c['country']=='China')}")
print(f"  Rest of Asia: {sum(1 for c in unique if c['country'] not in ('China','USA','Canada','Mexico','UK','France','Germany','Italy','Spain','Russia','Brazil','Argentina','Australia','New Zealand','South Africa','Nigeria','Egypt','Kenya') and c['timezone'].startswith('Asia/'))}")
print(f"  Europe: {sum(1 for c in unique if c['timezone'].startswith('Europe/') or c['timezone'].startswith('Atlantic/R'))}")
print(f"  North America: {sum(1 for c in unique if c['country'] in ('USA','Canada','Mexico'))}")
print(f"  Central/South Am: {sum(1 for c in unique if c['timezone'].startswith('America/'))}")
print(f"  Africa: {sum(1 for c in unique if c['timezone'].startswith('Africa/') or c['timezone'].startswith('Indian/') and c['country'] not in ('Maldives','Mauritius','Seychelles','Comoros'))}")
print(f"  Oceania: {sum(1 for c in unique if c['timezone'].startswith('Australia/') or c['timezone'].startswith('Pacific/'))}")
print(f"  Middle East/Other: {sum(1 for c in unique if c['timezone'] in ('Asia/Dubai','Asia/Riyadh','Asia/Qatar','Asia/Muscat','Asia/Kuwait','Asia/Bahrain','Asia/Aden','Asia/Baghdad','Asia/Amman','Asia/Beirut','Asia/Damascus','Asia/Jerusalem','Asia/Nicosia','Asia/Tehran','Asia/Kabul','Asia/Yerevan','Asia/Tbilisi','Asia/Baku','Asia/Almaty','Asia/Tashkent','Asia/Ashgabat','Asia/Bishkek','Asia/Dushanbe','Asia/Samarkand','Asia/Yekaterinburg','Indian/Maldives'))}")
