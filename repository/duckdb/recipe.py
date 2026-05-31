import pandas as pd
import duckdb
from repository.interfaces import IRecipeRepository


class RecipeRepository(IRecipeRepository):
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_recipe_by_id(self, recipe_id: int) -> dict:
        """특정 레시피 상세 정보 조회"""
        query = "SELECT * FROM easy_cook_books WHERE recipe_id = ?"
        result = self.db_manager.fetch_all(query, (recipe_id,))
        return result.iloc[0].to_dict() if not result.empty else {}

    def get_recipes_by_filter(self, cooking_time: int, difficulty: str) -> pd.DataFrame:
        """조건(시간, 난이도)에 따른 레시피 필터링 조회"""
        query = """
        SELECT * FROM easy_cook_books 
        WHERE cooking_time <= ? AND difficulty = ?
        """
        return self.db_manager.fetch_all(query, (cooking_time, difficulty))

    def get_all_recipes(self) -> pd.DataFrame:
        """모든 레시피 목록 조회"""
        query = "SELECT * FROM easy_cook_books"
        return self.db_manager.fetch_all(query)
