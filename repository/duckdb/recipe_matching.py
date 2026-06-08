import duckdb


class RecipeMatcher:
    def __init__(self, db_path="jachi.db"):
        self.db_path = db_path

    def get_match(self):
        with duckdb.connect(self.db_path) as con:
            # 냉장고에 있는 재료를 포함하는 레시피만 가져오기
            query = """
            SELECT r.name 
            FROM recipes r 
            JOIN fridge f ON r.ingredients LIKE '%' || f.name || '%'
            """
            return con.execute(query).df()
