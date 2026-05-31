import flet as ft

# 우리가 나중에 구현할 실제 구현체들을 import 할 준비
from repository.duckdb.fridge import FridgeRepository
from service.jachi_service import JachiService  # 서비스 계층
import views


def main(page: ft.Page):
    page.title = "자취 냉장고 매니저"
    page.theme_mode = ft.ThemeMode.LIGHT

    # 1. 의존성 주입 (Repository -> Service -> UI)
    fridge_repo = FridgeRepository()  # 나중에 DB 연결 객체를 전달하게 됩니다.
    service = JachiService(fridge_repo=fridge_repo)

    # 2. 탭 구성 (위에서 만든 서비스 전달)
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="내 냉장고", content=views.create_fridge_view(service)),
            ft.Tab(text="레시피", content=ft.Text("레시피 탭 준비 중...")),
        ],
        expand=1,
    )

    page.add(tabs)


if __name__ == "__main__":
    ft.app(target=main)
