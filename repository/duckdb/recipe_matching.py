import pandas as pd
import duckdb
from repository.interfaces import IMappingRepository


class MappingRepository(IMappingRepository):
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_ingredients_by_recipe(self, recipe_id: int) -> pd.DataFrame:
        """
        특정 레시피를 만들기 위해 필요한 재료 목록 조회
        매핑 테이블과 식재료 테이블을 JOIN하여 재료명과 요구 수량을 함께 반환
        """
        query = """
        SELECT 
            M.recipe_id, 
            M.fridge_item_id, 
            F.item_name, 
            M.required_quantity,
            M.is_required_essential
        FROM recipe_matching_maps M
        JOIN fresh_jachi_fridge F ON M.fridge_item_id = F.fridge_item_id
        WHERE M.recipe_id = ?
        """
        return self.db_manager.fetch_all(query, (recipe_id,))

    def add_mapping(self, recipe_id: int, fridge_item_id: int, quantity: int):
        """레시피와 식재료 간의 매핑 정보 추가"""
        query = """
        INSERT INTO recipe_matching_maps (recipe_id, fridge_item_id, required_quantity)
        VALUES (?, ?, ?)
        """
        self.db_manager.execute(query, (recipe_id, fridge_item_id, quantity))
