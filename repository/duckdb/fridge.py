# repository/duckdb/fridge.py 수정본
import duckdb


class FridgeRepository:
    def __init__(self, db_path="jachi.db"):
        self.db_path = db_path
        self._init_table()

    def _init_table(self):
        with duckdb.connect(self.db_path) as con:
            # 1. 엔티티 1: 식재료 정보
            con.execute(
                "CREATE TABLE IF NOT EXISTS ingredients (id INTEGER PRIMARY KEY, name VARCHAR)"
            )
            # 2. 엔티티 2: 레시피 정보
            con.execute(
                "CREATE TABLE IF NOT EXISTS recipes (id INTEGER PRIMARY KEY, name VARCHAR, difficulty VARCHAR)"
            )
            # 3. 관계: 레시피-재료 매핑
            con.execute(
                "CREATE TABLE IF NOT EXISTS recipe_ingredients (recipe_id INTEGER, ingredient_id INTEGER, qty INTEGER)"
            )
            # 4. 재고: 내 냉장고
            con.execute(
                "CREATE TABLE IF NOT EXISTS fridge_inventory (id INTEGER PRIMARY KEY, ingredient_id INTEGER, qty INTEGER, expiry_date VARCHAR)"
            )

            # 초기 데이터 (예시)
            con.execute(
                "INSERT OR REPLACE INTO ingredients VALUES (1, '양파'), (2, '스팸')"
            )
            con.execute(
                "INSERT OR REPLACE INTO fridge_inventory VALUES (1, 1, 3, '2026-06-15'), (2, 2, 2, '2026-08-20')"
            )

    def get_all(self):
        # 4개 테이블 구조를 JOIN하여 기존 main.py가 쓰던 'name', 'qty', 'date' 컬럼명 그대로 반환
        query = """
            SELECT f.id, i.name, f.qty, f.expiry_date as date
            FROM fridge_inventory f
            JOIN ingredients i ON f.ingredient_id = i.id
        """
        with duckdb.connect(self.db_path) as con:
            return con.execute(query).df()
