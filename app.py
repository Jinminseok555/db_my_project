import flet as ft
from repository.duckdb.fridge import FridgeRepository


def main(page: ft.Page):
    page.title = "나의 냉장고 관리자"
    page.vertical_alignment = ft.MainAxisAlignment.START

    fridge_repo = FridgeRepository()
    df = fridge_repo.get_all()

    page.add(ft.Text("냉장고 재료 목록", size=20, weight="bold"))

    for _, row in df.iterrows():
        page.add(ft.Text(f"- {row['name']}: {row['qty']}{row['unit']}"))


# 아래 코드가 중요합니다!
if __name__ == "__main__":
    ft.app(target=main)
