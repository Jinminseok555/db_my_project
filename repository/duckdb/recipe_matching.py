import duckdb


class RecipeMatcherRepository:  # 클래스 이름을 repository로 통일해주세요!
    def __init__(self, db_path="jachi.db"):
        self.db_path = db_path

    def get_match(self):
        with duckdb.connect("jachi.db") as con:
            # 모든 재료를 가진 레시피만 찾기
            query = """
                SELECT r.name
                FROM recipes r
                JOIN recipe_ingredients ri ON r.id = ri.recipe_id
                JOIN fridge_inventory f ON ri.ingredient_id = f.ingredient_id
                WHERE f.qty >= ri.required_qty
                GROUP BY r.id, r.name
                HAVING COUNT(ri.ingredient_id) = (
                    SELECT COUNT(*) 
                    FROM recipe_ingredients 
                    WHERE recipe_id = r.id
                )
            """
            return con.execute(query).df()
