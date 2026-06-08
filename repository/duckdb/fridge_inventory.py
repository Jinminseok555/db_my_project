import duckdb

# 만약 BaseRepository가 있는 폴더 위치가 다르다면 import 경로를 수정하세요
from repository.base import BaseRepository


class InventoryRepository(BaseRepository):
    def __init__(self, db_path="jachi.db"):
        self.db_path = db_path
        self._init_table()

    def _init_table(self):
        with duckdb.connect(self.db_path) as con:
            # 냉장고 재고 테이블 생성 (ingredients 테이블의 id를 참조)
            con.execute("""
                CREATE TABLE IF NOT EXISTS fridge_inventory (
                    id INTEGER PRIMARY KEY, 
                    ingredient_id INTEGER, 
                    qty INTEGER, 
                    expiry_date DATE,
                    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
                )
            """)
            # 초기 샘플 데이터 (앱을 처음 실행했을 때 데이터가 없으면 불편하니까요!)
            # 1: 양파, 2: 스팸, 3: 김치 (ingredients 테이블의 id값 기준)
            con.execute(
                "INSERT OR REPLACE INTO fridge_inventory VALUES (1, 1, 3, '2026-06-20')"
            )
            con.execute(
                "INSERT OR REPLACE INTO fridge_inventory VALUES (2, 2, 2, '2026-08-15')"
            )

    def get_fridge_list(self):
        """내 냉장고에 있는 재료를 이름과 함께 보기 좋게 가져오기"""
        query = """
            SELECT f.id, i.name, f.qty, f.expiry_date 
            FROM fridge_inventory f
            JOIN ingredients i ON f.ingredient_id = i.id
        """
        with duckdb.connect(self.db_path) as con:
            return con.execute(query).df()

    def add_item(self, ingredient_id, qty, expiry_date):
        """새로운 재료를 냉장고에 넣기"""
        with duckdb.connect(self.db_path) as con:
            con.execute(
                f"INSERT INTO fridge_inventory (ingredient_id, qty, expiry_date) VALUES ({ingredient_id}, {qty}, '{expiry_date}')"
            )

    def update_qty(self, item_id, new_qty):
        """재료 수량 변경 (요리 후 차감할 때 사용!)"""
        with duckdb.connect(self.db_path) as con:
            con.execute(
                f"UPDATE fridge_inventory SET qty = {new_qty} WHERE id = {item_id}"
            )

    def delete_item(self, item_id):
        """냉장고에서 재료 빼기"""
        with duckdb.connect(self.db_path) as con:
            con.execute(f"DELETE FROM fridge_inventory WHERE id = {item_id}")
