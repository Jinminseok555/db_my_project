import duckdb
from repository.base import BaseRepository


class InventoryRepository(BaseRepository):
    def __init__(self, db_path="jachi.db"):
        self.db_path = db_path
        self._init_table()

    def _init_table(self):
        with duckdb.connect("jachi.db") as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS fridge_inventory (
                    id INTEGER PRIMARY KEY, 
                    ingredient_id INTEGER, 
                    qty INTEGER, 
                    expiry_date DATE,
                    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
                )
            """)
            con.execute(
                "INSERT OR REPLACE INTO fridge_inventory VALUES (1, 1, 3, '2026-06-20')"
            )
            con.execute(
                "INSERT OR REPLACE INTO fridge_inventory VALUES (2, 2, 2, '2026-08-15')"
            )

    def get_fridge_list(self):
        query = """
            SELECT f.id, i.name, f.qty, f.expiry_date 
            FROM fridge_inventory f
            JOIN ingredients i ON f.ingredient_id = i.id
        """
        with duckdb.connect("jachi.db") as con:
            return con.execute(query).df()

    def get_item_detail(self, item_id):
        """DB에서 데이터만 가져오는 역할!"""
        query = """
            SELECT i.name, i.type, f.qty, f.expiry_date, i.storage_method
            FROM fridge_inventory f 
            JOIN ingredients i ON f.ingredient_id = i.id 
            WHERE f.id = ?
        """
        with duckdb.connect("jachi.db") as con:
            return con.execute(query, [item_id]).fetchone()

    def add_item(self, ingredient_id, qty, expiry_date):
        with duckdb.connect("jachi.db") as con:
            con.execute(
                "INSERT INTO fridge_inventory (ingredient_id, qty, expiry_date) VALUES (?, ?, ?)",
                [ingredient_id, qty, expiry_date],
            )

    def update_qty(self, item_id, new_qty):
        with duckdb.connect("jachi.db") as con:
            con.execute(
                "UPDATE fridge_inventory SET qty = ? WHERE id = ?", [new_qty, item_id]
            )

    def delete_item(self, item_id):
        with duckdb.connect("jachi.db") as con:
            con.execute("DELETE FROM fridge_inventory WHERE id = ?", [item_id])
