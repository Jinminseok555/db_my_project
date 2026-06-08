import duckdb
from repository.base import BaseRepository


class FridgeRepository(BaseRepository):
    def __init__(self, db_path="jachi.db"):
        self.db_path = db_path
        self._init_table()

    def _init_table(self):
        with duckdb.connect(self.db_path) as con:
            con.execute(
                "CREATE TABLE IF NOT EXISTS fridge (id INTEGER PRIMARY KEY, name VARCHAR, qty INTEGER, unit VARCHAR, date VARCHAR)"
            )
            # 초기 데이터 추가
            con.execute(
                "INSERT OR REPLACE INTO fridge VALUES (1, '양파', 1, '개', '2026-06-10')"
            )
            con.execute(
                "INSERT OR REPLACE INTO fridge VALUES (2, '스팸', 2, '개', '2026-08-15')"
            )

    def get_all(self):
        with duckdb.connect(self.db_path) as con:
            return con.execute("SELECT * FROM fridge").df()
