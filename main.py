import sys
import os

# 가장 먼저 필요한 라이브러리를 불러옵니다.
from datetime import datetime, timedelta

import flet as ft

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from repository.duckdb.fridge import FridgeRepository
from repository.duckdb.fridge_inventory import InventoryRepository
from repository.duckdb.recipe import RecipeRepository
from repository.duckdb.recipe_matching import RecipeMatcherRepository
# 필요하다면 IngredientRepository도 추가

import duckdb

files = ["jachi.db", "test_jachi.db"]

for db_file in files:
    try:
        con = duckdb.connect("jachi.db")
        tables = con.execute("SHOW TABLES").fetchall()
        print(f"--- 파일: {db_file} ---")
        print(f"테이블 목록: {tables}")
    except Exception as e:
        print(f"--- 파일: {db_file} ---")
        print(f"열 수 없음: {e}")


def main(page: ft.Page):
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
    def show_fridge(e=None):
        df = FridgeRepository().get_all()
        today = datetime.now()
        seven_days_later = today + timedelta(days=7)

        # 1. 유통기한 로직 (기존 유지)
        expiring_items = [
            r
            for _, r in df.iterrows()
            if today
            <= datetime.strptime(str(r["date"]), "%Y-%m-%d")
            <= seven_days_later
        ]

        # 2. 클릭 가능한 행(row)을 만드는 함수 (내부에 선언하여 사용)
        def create_clickable_row(item):
            # 상세창을 띄우는 함수를 람다로 연결
            on_tap_func = lambda e: show_detail_dialog(page, item["id"], show_fridge)
            return ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(item["id"])), on_tap=on_tap_func),
                    ft.DataCell(ft.Text(item["name"]), on_tap=on_tap_func),
                    ft.DataCell(ft.Text(str(item["qty"])), on_tap=on_tap_func),
                    ft.DataCell(ft.Text(str(item["date"])), on_tap=on_tap_func),
                ]
            )

        # 3. 데이터프레임의 각 행을 클릭 가능한 row로 변환
        # (r.to_dict()를 통해 데이터를 딕셔너리로 넘겨줍니다)
        rows = [create_clickable_row(r.to_dict()) for _, r in df.iterrows()]

        # 4. 화면 구성 (DataTable에 위에서 만든 rows를 전달)
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
                    rows=rows,  # 여기서 드디어 완성된 클릭 가능한 행들을 사용합니다!
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        page.update()

    # 테이블 행 생성 예시
    def create_table_row(page, item, refresh_callback):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(item["id"]))),
                ft.DataCell(ft.Text(item["name"])),
                ft.DataCell(ft.Text(str(item["qty"]))),
                ft.DataCell(ft.Text(str(item["expiry_date"]))),
            ],
            # 핵심! 행 전체를 클릭 가능하게 만들고 상세창 띄우기
            on_select_changed=lambda e: show_detail_dialog(
                page, item["id"], refresh_callback
            ),
        )

        # main.py - 리스트 생성 부분
        def create_fridge_list_item(page, item, refresh_callback):
            return ft.ListTile(
                title=ft.Text(
                    item["name"], weight=ft.FontWeight.BOLD
                ),  # 텍스트 클릭 가능
                subtitle=ft.Text(f"수량: {item['qty']}"),
                # 이름을 클릭하면 팝업 오픈!
                on_click=lambda e: show_detail_dialog(
                    page, item["id"], refresh_callback
                ),
            )

    # --- 1.1 상세 페이지 화면 함수들 ---
    # main.py

    def show_detail_dialog(page, item_id, refresh_callback):
        repo = InventoryRepository()
        detail = repo.get_item_detail(
            item_id
        )  # (이름, 카테고리, 수량, 유통기한, 보관방법)

        # 수량을 수정할 입력창
        qty_field = ft.TextField(label="수량 수정", value=str(detail[2]), width=100)

        def on_update_click(e):
            repo.update_qty(item_id, qty_field.value)
            dlg.open = False
            refresh_callback()  # 메인 화면의 리스트를 새로고침하는 함수
            page.update()

        def on_delete_click(e):
            repo.delete_item(item_id)
            dlg.open = False
            refresh_callback()
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"재료 상세: {detail[0]}"),
            content=ft.Column(
                [
                    ft.Text(f"카테고리: {detail[1]}"),
                    ft.Text(f"보관 방법: {detail[4]}"),  # 여기서 보관 방법 표시!
                    ft.Text(f"유통기한: {detail[3]}"),
                    qty_field,
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("수정", on_click=on_update_click),
                ft.TextButton(
                    "삭제",
                    on_click=on_delete_click,
                    icon=ft.icons.DELETE,
                    icon_color="red",
                ),
                ft.TextButton(
                    "닫기",
                    on_click=lambda e: (setattr(dlg, "open", False), page.update()),
                ),
            ],
        )
        page.dialog = dlg
        dlg.open = True
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
