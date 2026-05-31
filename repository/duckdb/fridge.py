import pandas as pd
import duckdb
from repository.interfaces import IFridgeRepository


class FridgeRepository(IFridgeRepository):
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_item(self, item_data: dict):
        """냉장고에 식재료 추가"""
        query = """
        INSERT INTO fresh_jachi_fridge (item_name, quantity_val, unit, expiration_date)
        VALUES (?, ?, ?, ?)
        """
        self.db_manager.execute(
            query,
            (
                item_data["item_name"],
                item_data["quantity_val"],
                item_data["unit"],
                item_data["expiration_date"],
            ),
        )

    def get_all_items(self) -> pd.DataFrame:
        """냉장고 전체 식재료 목록 조회"""
        query = "SELECT * FROM fresh_jachi_fridge ORDER BY expiration_date ASC"
        return self.db_manager.fetch_all(query)

    def update_quantity(self, fridge_item_id: int, new_quantity: int):
        """식재료 수량 갱신 (해먹기 완료 후 호출)"""
        query = (
            "UPDATE fresh_jachi_fridge SET quantity_val = ? WHERE fridge_item_id = ?"
        )
        self.db_manager.execute(query, (new_quantity, fridge_item_id))

    def delete_item(self, fridge_item_id: int):
        """식재료 삭제 (소진 시)"""
        query = "DELETE FROM fresh_jachi_fridge WHERE fridge_item_id = ?"
        self.db_manager.execute(query, (fridge_item_id,))
