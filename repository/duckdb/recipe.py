import duckdb
from repository.base import BaseRepository


class RecipeRepository(BaseRepository):
    def __init__(self, db_path="jachi.db"):
        self.db_path = db_path
        self._init_table()

    def _init_table(self):
        with duckdb.connect("jachi.db") as con:
            con.execute("""CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY, name VARCHAR, time INTEGER, difficulty VARCHAR, ingredients VARCHAR)""")
            # 초기 데이터 추가
            con.execute(
                "INSERT OR REPLACE INTO recipes VALUES (1, '스팸김치볶음밥', 10, '하', '스팸,김치')"
            )
            con.execute(
                "INSERT OR REPLACE INTO recipes VALUES (2, '알리오올리오', 12, '중', '마늘,올리브유')"
            )

    def get_all(self):
        with duckdb.connect("jachi.db") as con:
            return con.execute("SELECT * FROM recipes").df()
