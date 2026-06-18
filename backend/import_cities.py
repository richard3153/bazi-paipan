"""
导入城市数据到数据库
"""
import csv
from app.database import SessionLocal, init_db
from app.models import City

def import_cities():
    """从CSV文件导入城市数据"""
    # 初始化数据库
    init_db()
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 读取CSV文件
        with open('data/cities.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # 清空现有数据
            db.query(City).delete()
            print("已清空现有城市数据")
            
            # 导入新数据
            count = 0
            for row in reader:
                population = int(row['population']) if row.get('population') else None
                capital = row.get('capital') if row.get('capital') else None
                city = City(
                    name=row['name'],
                    name_en=row.get('name_en') if row.get('name_en') else None,
                    country=row['country'],
                    province=row['province'] if row['province'] else None,
                    longitude=float(row['longitude']),
                    latitude=float(row['latitude']),
                    timezone=row['timezone'],
                    population=population,
                    capital=capital,
                )
                db.add(city)
                count += 1
            
            db.commit()
            print(f"成功导入 {count} 个城市")
            
    except Exception as e:
        print(f"导入失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    import_cities()
