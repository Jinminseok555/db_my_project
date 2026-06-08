import duckdb
from repository.base import BaseRepository


class IngredientRepository(BaseRepository):
    def __init__(self, db_path="jachi.db"):
        self.db_path = db_path
        self._init_table()

    def _init_table(self):
        with duckdb.connect(self.db_path) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS ingredients (
                    id INTEGER PRIMARY KEY, 
                    name VARCHAR, 
                    category VARCHAR
                )
            """)
            # 초기 데이터 (예시)
            con.execute(
                "INSERT OR REPLACE INTO ingredients VALUES (1, '양파', '채소'), (2, '스팸', '가공식품'), (3, '김치', '반찬')"
            )

    def get_all(self):
        with duckdb.connect(self.db_path) as con:
            return con.execute("SELECT * FROM ingredients").df()
