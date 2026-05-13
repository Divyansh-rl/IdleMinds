import flet as ft
import numpy as np
import random
import requests
import urllib.parse

def is_safe(board, r, c, num):
    if num in board[r, :] or num in board[:, c]: return False
    box_r, box_c = (r // 3) * 3, (c // 3) * 3
    if num in board[box_r:box_r + 3, box_c:box_c + 3]: return False
    return True

def find_empty(board):
    empty_spots = np.argwhere(board == 0)
    return empty_spots[0] if empty_spots.size > 0 else None

def generate_full_board(board):
    empty = find_empty(board)
    if empty is None: return True
    r, c = empty
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    for val in numbers:
        if is_safe(board, r, c, val):
            board[r, c] = val
            if generate_full_board(board): return True
            board[r, c] = 0 
    return False

def count_solutions(board):
    empty = find_empty(board)
    if empty is None: return 1 
    r, c = empty
    solutions = 0
    for val in range(1, 10):
        if is_safe(board, r, c, val):
            board[r, c] = val
            solutions += count_solutions(board)
            board[r, c] = 0 
            if solutions > 1: return solutions
    return solutions

def create_puzzle(difficulty):
    board = np.zeros((9, 9), dtype=int)
    generate_full_board(board)
    
    if difficulty == "Easy": target_givens = random.randint(40, 45)
    elif difficulty == "Medium": target_givens = random.randint(32, 36)
    else: target_givens = random.randint(28, 30)
        
    coordinates = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(coordinates)
    
    current_givens = 81
    attempts = 0          
    MAX_ATTEMPTS = 15     
    
    for r, c in coordinates:
        if current_givens <= target_givens or attempts >= MAX_ATTEMPTS: break
        temp_val = board[r, c]
        board[r, c] = 0
        if count_solutions(board.copy()) == 1:
            current_givens -= 1
            attempts = 0 
        else:
            board[r, c] = temp_val 
            attempts += 1 
    return board

def get_conflicts(board, r, c, num):
    conflicts = set()
    for i in range(9):
        if i != c and board[r, i] == num: conflicts.add((r, i))
        if i != r and board[i, c] == num: conflicts.add((i, c))
    box_r, box_c = (r // 3) * 3, (c // 3) * 3
    for i in range(box_r, box_r + 3):
        for j in range(box_c, box_c + 3):
            if (i, j) != (r, c) and board[i, j] == num: conflicts.add((i, j))
    return list(conflicts)

CELL_SIZE = 65    
NUMPAD_SIZE = 80  

def main(page: ft.Page):
    page.title = "Sudoku"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT 
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_300

    game_state = {}

    landing_view = ft.Container(visible=True)
    game_view = ft.Container(visible=False)

    loading_ring = ft.ProgressRing(visible=False)
    
    def on_difficulty_click(e, difficulty):
        loading_ring.visible = True
        page.update()

        generated_board = create_puzzle(difficulty)

        game_state["sample_board"] = generated_board
        game_state["current_board"] = generated_board.copy()
        game_state["locked_cells"] = (generated_board != 0)
        game_state["selected"] = None
        game_state["conflicts"] = []

        build_game_ui()
        loading_ring.visible = False
        landing_view.visible = False
        game_view.visible = True

        page.bgcolor = ft.Colors.WHITE
        page.update()

    landing_view.content = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        controls=[
            ft.Text("Sudoku", size=50, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            ft.Text("Select difficulty", size=22, color=ft.Colors.BLACK),
            ft.Container(height=20),
            
            ft.Button(
                content=ft.Text("Easy", size=20, weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE, 
                width=250, height=60, on_click=lambda e: on_difficulty_click(e, "Easy")
            ),
            ft.Button(
                content=ft.Text("Medium", size=20, weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE, 
                width=250, height=60, on_click=lambda e: on_difficulty_click(e, "Medium")
            ),
            ft.Button(
                content=ft.Text("Hard", size=20, weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE, 
                width=250, height=60, on_click=lambda e: on_difficulty_click(e, "Hard")
            ),
            ft.Container(height=20),
            loading_ring 
        ]
    )

    def build_game_ui():
        cells = {}           
        cell_containers = {} 
        error_dots = {} 

        sample = game_state["sample_board"]
        current = game_state["current_board"]
        locked = game_state["locked_cells"]

        def solve_sudoku(board):
            empty_spots = np.argwhere(board == 0)
            if empty_spots.size == 0: return True 
            r, c = empty_spots[0]
            for val in range(1, 10):
                if is_safe(board, r, c, val):
                    board[r, c] = val
                    if solve_sudoku(board): return True
                    board[r, c] = 0 
            return False

        def execute_solve(e):
            confirm_dialog.open = False
            page.update()
            current[:] = sample[:]
            if solve_sudoku(current):
                for r in range(9):
                    for c in range(9):
                        cells[(r, c)].value = str(current[r, c])
                        error_dots[(r, c)].visible = False
                        if not locked[r, c]: cells[(r, c)].color = ft.Colors.GREEN_700
                game_state["selected"] = None
                game_state["conflicts"] = []
                update_board_colors()
                snack = ft.SnackBar(content=ft.Text("Puzzle Solved!", weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.GREEN_700)
                page.overlay.append(snack)
                snack.open = True
                page.update()

        confirm_dialog = ft.AlertDialog(
            modal=True, 
            title=ft.Text("Confirm Auto-Solve"),
            content=ft.Text("Are you sure you want the computer to solve this puzzle? This will overwrite your progress."),
            actions=[
                ft.TextButton("Yes, solve it!", on_click=execute_solve),
                ft.TextButton("No, let me play", on_click=lambda e: setattr(confirm_dialog, 'open', False) or page.update()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(confirm_dialog)

        def update_board_colors():
            sel_r, sel_c = game_state["selected"] if game_state["selected"] else (-1, -1)
            conflicts = game_state["conflicts"]
            related = set()
            if sel_r != -1:
                for i in range(9):
                    related.add((sel_r, i)) 
                    related.add((i, sel_c)) 
                box_r, box_c = (sel_r // 3) * 3, (sel_c // 3) * 3
                for i in range(box_r, box_r + 3):
                    for j in range(box_c, box_c + 3): related.add((i, j)) 

            for r in range(9):
                for c in range(9):
                    if (r, c) in conflicts: cell_containers[(r, c)].bgcolor = ft.Colors.RED_200
                    elif (r, c) == (sel_r, sel_c): cell_containers[(r, c)].bgcolor = ft.Colors.BLUE_200
                    elif (r, c) in related: cell_containers[(r, c)].bgcolor = ft.Colors.GREY_400 if locked[r, c] else ft.Colors.BLUE_50
                    elif locked[r, c]: cell_containers[(r, c)].bgcolor = ft.Colors.GREY_300
                    else: cell_containers[(r, c)].bgcolor = ft.Colors.TRANSPARENT
                    cell_containers[(r, c)].update()

        def select_cell(r, c):
            if locked[r, c]: return
            game_state["selected"] = (r, c)
            val = current[r, c]
            if val != 0 and error_dots[(r, c)].visible:
                game_state["conflicts"] = get_conflicts(current, r, c, val)
            else:
                game_state["conflicts"] = []
            update_board_colors()

        def numpad_click(val):
            if not game_state["selected"]: return
            r, c = game_state["selected"]
                
            if val == "X":
                current[r, c] = 0
                cells[(r, c)].value = ""
                cells[(r, c)].color = ft.Colors.BLACK
                error_dots[(r, c)].visible = False
                game_state["conflicts"] = []
            else:
                val = int(val)
                conflicts = get_conflicts(current, r, c, val)
                current[r, c] = val
                cells[(r, c)].value = str(val)
                
                if conflicts:
                    cells[(r, c)].color = ft.Colors.RED_700
                    error_dots[(r, c)].visible = True
                    game_state["conflicts"] = conflicts
                else:
                    cells[(r, c)].color = ft.Colors.BLACK
                    error_dots[(r, c)].visible = False
                    game_state["conflicts"] = []

            if np.count_nonzero(current == 0) == 0 and not game_state["conflicts"]:
                snack = ft.SnackBar(content=ft.Text("🎉 YOU WON! 🎉", size=20, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.GREEN_700)
                page.overlay.append(snack)
                snack.open = True
                page.update()
                try:
                    parsed_url = urllib.parse.urlparse(page.route)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    current_user = query_params.get("user", [None])[0]
                    if current_user:
                        requests.post(f"http://127.0.0.1:5000/api/server_win?user={current_user}")
                except Exception as e:
                    print(f"Background API Error (Game is still safe!): {e}")

            cells[(r, c)].update()
            error_dots[(r, c)].update()
            update_board_colors()

        board_ui = ft.Column(spacing=0)
        for row in range(9):
            row_ui = ft.Row(spacing=0, alignment=ft.MainAxisAlignment.CENTER)
            for col in range(9):
                border_top = 2 if row % 3 == 0 else 0.5
                border_left = 2 if col % 3 == 0 else 0.5
                border_bottom = 2 if row == 8 else 0.5
                border_right = 2 if col == 8 else 0.5

                start_val = sample[row, col]
                display_text = str(start_val) if start_val != 0 else ""
                
                cell_text = ft.Text(display_text, size=28, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)
                cells[(row, col)] = cell_text

                error_dot = ft.Container(width=8, height=8, bgcolor=ft.Colors.RED_700, border_radius=4, visible=False)
                error_dots[(row, col)] = error_dot

                cell_content = ft.Stack(
                    controls=[
                        ft.Container(content=cell_text, alignment=ft.Alignment.CENTER, width=CELL_SIZE, height=CELL_SIZE),
                        ft.Container(content=error_dot, bottom=5, left=5) 
                    ], width=CELL_SIZE, height=CELL_SIZE
                )

                initial_bg = ft.Colors.GREY_300 if locked[row, col] else ft.Colors.TRANSPARENT

                cell = ft.Container(
                    width=CELL_SIZE, height=CELL_SIZE, bgcolor=initial_bg,
                    border=ft.Border.only(
                        top=ft.BorderSide(border_top, ft.Colors.BLACK), left=ft.BorderSide(border_left, ft.Colors.BLACK),
                        bottom=ft.BorderSide(border_bottom, ft.Colors.BLACK), right=ft.BorderSide(border_right, ft.Colors.BLACK),
                    ),
                    content=cell_content, on_click=lambda e, r=row, c=col: select_cell(r, c)
                )
                cell_containers[(row, col)] = cell
                row_ui.controls.append(cell)
            board_ui.controls.append(row_ui)

        def create_btn(val):
            text_color = ft.Colors.RED_700 if val == "X" else ft.Colors.BLACK
            return ft.Container(
                width=NUMPAD_SIZE, height=NUMPAD_SIZE, alignment=ft.Alignment.CENTER,
                bgcolor=ft.Colors.GREY_200, border_radius=8, 
                content=ft.Text(str(val), size=32, weight=ft.FontWeight.BOLD, color=text_color),
                on_click=lambda e, v=val: numpad_click(v)
            )

        solve_btn = ft.Container(
            width=(NUMPAD_SIZE * 2) + 10, height=NUMPAD_SIZE, 
            alignment=ft.Alignment.CENTER, bgcolor=ft.Colors.GREY_200, border_radius=8,
            content=ft.Text("Auto-Solve", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            on_click=lambda e: setattr(confirm_dialog, 'open', True) or page.update()
        )

        numpad_ui = ft.Column(
            spacing=10, alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Row([create_btn(1), create_btn(2), create_btn(3)]),
                ft.Row([create_btn(4), create_btn(5), create_btn(6)]),
                ft.Row([create_btn(7), create_btn(8), create_btn(9)]),
                ft.Row([create_btn("X"), solve_btn]),
            ]
        )

        def go_back(e):
            game_view.visible = False
            landing_view.visible = True
            page.bgcolor = ft.Colors.GREY_300
            page.update()

        back_btn = ft.Button("← Back", on_click=go_back)

        game_view.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row([back_btn], alignment=ft.MainAxisAlignment.START),
                ft.Text("Sudoku", size=40, weight=ft.FontWeight.BOLD), 
                ft.Container(height=10), 
                ft.Row(spacing=80, alignment=ft.MainAxisAlignment.CENTER, controls=[board_ui, numpad_ui])
            ]
        )

    page.add(landing_view, game_view)

ft.app(target=main, port=8000)