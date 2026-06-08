import sys
import os

# 가장 먼저 필요한 라이브러리를 불러옵니다.
from datetime import datetime, timedelta

import flet as ft

# 현재 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from repository.duckdb.fridge import FridgeRepository


def main(page: ft.Page):
    # (나머지 코드 생략 - 이 아래부터는 기존 코드와 동일합니다)
    # ...
    page.title = "Jachi Fridge Planner"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    content_area = ft.Container(expand=True, padding=20)
    search_field = ft.TextField(label="식재료 검색", width=300)

    def show_search_dialog(e):
        search_query = search_field.value.lower().strip()
        df = FridgeRepository().get_all()
        filtered_df = df[df["name"].str.lower().str.contains(search_query, na=False)]

        # 결과 영역을 새로운 Column으로 구성
        if filtered_df.empty:
            result_content = ft.Column(
                [
                    ft.Text(f"'{search_query}'에 해당하는 식재료가 없습니다."),
                    ft.ElevatedButton("돌아가기", on_click=show_fridge),
                ]
            )
        else:
            rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(r[col])))
                        for col in ["name", "qty", "date"]
                    ]
                )
                for _, r in filtered_df.iterrows()
            ]
            result_content = ft.Column(
                [
                    ft.Text(f"검색 결과: {len(filtered_df)}건", size=20, weight="bold"),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text(c))
                            for c in ["식재료명", "수량", "유통기한"]
                        ],
                        rows=rows,
                    ),
                    ft.ElevatedButton("돌아가기", on_click=show_fridge),
                ]
            )

        # 메인 화면 전체를 결과 화면으로 교체 (이게 가장 확실합니다)
        content_area.content = result_content
        page.update()

    # --- 페이지 화면 함수들 ---
    def show_fridge(e):
        df = FridgeRepository().get_all()
        today = datetime.now()
        seven_days_later = today + timedelta(days=7)
        expiring_items = [
            r
            for _, r in df.iterrows()
            if today
            <= datetime.strptime(str(r["date"]), "%Y-%m-%d")
            <= seven_days_later
        ]

        content_area.content = ft.Column(
            [
                ft.Row(
                    [
                        search_field,
                        ft.ElevatedButton(
                            "검색", icon="search", on_click=show_search_dialog
                        ),
                    ]
                ),
                ft.Divider(),
                ft.Text(
                    "■ 유통기한 마감 임박 재료", size=16, weight="bold", color="red"
                ),
                ft.Row(
                    [
                        ft.Card(
                            content=ft.Container(
                                ft.Text(
                                    f"{item['name']} (D-{(datetime.strptime(str(item['date']), '%Y-%m-%d') - today).days})"
                                ),
                                padding=10,
                            )
                        )
                        for item in expiring_items
                    ]
                ),
                ft.Divider(),
                ft.Text("■ 일반 보관 식재료 목록", size=18, weight="bold"),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text(c))
                        for c in ["ID", "식재료", "수량", "유통기한"]
                    ],
                    rows=[
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(r[col])))
                                for col in ["id", "name", "qty", "date"]
                            ]
                        )
                        for _, r in df.iterrows()
                    ],
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        page.update()

    # 2. 레시피 조회 화면
    def show_recipes(e):
        content_area.content = ft.Column(
            [
                ft.Text("■ 전체 자치 레시피 목록", size=18, weight="bold"),
                ft.Row(
                    [
                        ft.Card(
                            content=ft.Container(ft.Text("스팸김치볶음밥"), padding=20),
                            width=200,
                        )
                    ],
                    wrap=True,
                ),
            ]
        )
        page.update()

    # 3. 상황별 해먹기 화면
    def show_matching(e):
        content_area.content = ft.Column(
            [
                ft.Text("상황 선택:", weight="bold"),
                ft.RadioGroup(
                    content=ft.Row(
                        [
                            ft.Radio(value="1", label="평상시"),
                            ft.Radio(value="2", label="시험기간"),
                        ]
                    )
                ),
                ft.Divider(),
                ft.Text("■ 추천 레시피", size=18, weight="bold"),
                ft.Row(
                    [
                        ft.Card(
                            content=ft.Container(ft.Text("계란간장밥"), padding=20),
                            width=200,
                        )
                    ]
                ),
            ]
        )
        page.update()

    # 1. 현재 선택된 메뉴를 저장할 변수
    selected_menu = "내 냉장고"

    # 2. 버튼의 배경색을 결정하는 함수
    def get_bg_color(menu_name):
        return "blue100" if selected_menu == menu_name else "transparent"

    # 3. 버튼 클릭 시 호출될 업데이트 함수
    def update_sidebar(e, menu_name):
        nonlocal selected_menu
        selected_menu = menu_name
        # 사이드바 전체를 다시 그려서 색상을 반영
        sidebar.content.controls[2].bgcolor = get_bg_color("내 냉장고")
        sidebar.content.controls[3].bgcolor = get_bg_color("레시피 조회")
        sidebar.content.controls[4].bgcolor = get_bg_color("상황별 해먹기")
        page.update()

    # 사이드바 구성 (ListTile 대신 Container 활용)
    sidebar = ft.Container(
        content=ft.Column(
            [
                ft.Text("Jachi Fridge Planner", size=20, weight="bold", color="blue"),
                ft.Divider(),
                # 버튼들을 Container로 감싸서 클릭 이벤트와 배경색을 제어
                ft.Container(
                    ft.Text("내 냉장고", size=16),
                    bgcolor=get_bg_color("내 냉장고"),
                    padding=10,
                    border_radius=5,
                    on_click=lambda e: [update_sidebar(e, "내 냉장고"), show_fridge(e)],
                ),
                ft.Container(
                    ft.Text("레시피 조회", size=16),
                    bgcolor=get_bg_color("레시피 조회"),
                    padding=10,
                    border_radius=5,
                    on_click=lambda e: [
                        update_sidebar(e, "레시피 조회"),
                        show_recipes(e),
                    ],
                ),
                ft.Container(
                    ft.Text("상황별 해먹기", size=16),
                    bgcolor=get_bg_color("상황별 해먹기"),
                    padding=10,
                    border_radius=5,
                    on_click=lambda e: [
                        update_sidebar(e, "상황별 해먹기"),
                        show_matching(e),
                    ],
                ),
            ]
        ),
        width=250,
        bgcolor="blue50",
        padding=15,
    )
    # 초기 실행
    show_fridge(None)

    page.add(
        ft.Row(
            [sidebar, ft.Container(content=content_area, expand=True)],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
