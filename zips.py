import flet as ft
import numpy as np
import random
import time
import threading
import requests
import urllib

class ZipLogic:
    def __init__(self, grid_size, anchors):
        self.grid_size = grid_size
        self.anchors = anchors
        self.grid = np.zeros((grid_size, grid_size), dtype=int)
        self.path = []
        self.max_anchor = max(anchors.values())
        
        for pos, val in anchors.items():
            self.grid[pos] = val

    def get_start_pos(self):
        for pos, val in self.anchors.items():
            if val == 1: return pos
        return None

    def is_valid_move(self, r, c):
        if not (0 <= r < self.grid_size and 0 <= c < self.grid_size): return False
        if (r, c) in self.path: return False
        if not self.path: return self.grid[r, c] == 1
        
        last_r, last_c = self.path[-1]
        if abs(last_r - r) + abs(last_c - c) != 1: return False
            
        cell_val = self.grid[r, c]
        if cell_val > 0:
            current_anchor_reached = sum(1 for pos in self.path if self.grid[pos] > 0)
            if cell_val != current_anchor_reached + 1: return False
                
        return True

    def add_move(self, r, c):
        if self.is_valid_move(r, c):
            self.path.append((r, c))
            return True
        return False
        
    def undo_move(self):
        if len(self.path) > 1: self.path.pop()

    def check_win(self):
        return len(self.path) == self.grid_size ** 2 and self.grid[self.path[-1]] == self.max_anchor

def generate_random_puzzle(level_index):
    if level_index < 3:
        size = 4
        num_anchors = 5
    elif level_index < 8:
        size = 5
        num_anchors = 6
    else:
        size = 6
        num_anchors = 8
        
    visited = set()
    path = []
    
    def dfs(r, c):
        visited.add((r, c))
        path.append((r, c))
        
        if len(path) == size * size:
            return True
            
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(dirs)
        
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size and (nr, nc) not in visited:
                if dfs(nr, nc):
                    return True
                    
        visited.remove((r, c))
        path.pop()
        return False
        
    while True:
        visited.clear()
        path.clear()
        start_r = random.randint(0, size - 1)
        start_c = random.randint(0, size - 1)
        
        if dfs(start_r, start_c):
            break
    
    max_idx = (size * size) - 1
    indices = [0, max_idx] 
    
    intermediate = random.sample(range(1, max_idx), num_anchors - 2)
    indices.extend(intermediate)
    indices.sort()
    
    anchors = {}
    for anchor_val, path_idx in enumerate(indices):
        anchors[path[path_idx]] = anchor_val + 1
        
    return size, anchors
        
    dfs(random.randint(0, size-1), random.randint(0, size-1))
    
    max_idx = (size * size) - 1
    indices = [0, max_idx] 
    
    intermediate = random.sample(range(1, max_idx), num_anchors - 2)
    indices.extend(intermediate)
    indices.sort()
    
    anchors = {}
    for anchor_val, path_idx in enumerate(indices):
        anchors[path[path_idx]] = anchor_val + 1
        
    return size, anchors


def main(page: ft.Page):
    page.title = "LinkedIn Zip Clone - Endless Mode"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLUE_GREY_900

    current_level = 0
    game_instance = None
    cells = {}
    
    start_time = 0.0
    is_solved = False

    status_text = ft.Text("", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    timer_text = ft.Text("00:00", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE70)
    board_ui = ft.Column(spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def next_level_clicked(e):
        nonlocal current_level
        current_level += 1
        load_level(current_level)

    next_btn = ft.ElevatedButton("Next Level", on_click=next_level_clicked, visible=False, color=ft.Colors.BLACK, bgcolor=ft.Colors.GREEN_400)
    
    page.add(status_text, timer_text, board_ui, next_btn)

    def update_clock():
        while True:
            if game_instance is not None and not is_solved:
                elapsed = int(time.time() - start_time)
                mins, secs = divmod(elapsed, 60)
                timer_text.value = f"{mins:02d}:{secs:02d}"
                
                try:
                    page.update()
                except Exception:
                    break
            time.sleep(1)

    threading.Thread(target=update_clock, daemon=True).start()

    def update_board():
        if game_instance is None: 
            return
            
        for (r, c), container in cells.items():
            if (r, c) in game_instance.path:
                container.bgcolor = ft.Colors.TEAL_400
                container.border = ft.border.all(2, ft.Colors.TEAL_200)
            else:
                container.bgcolor = ft.Colors.BLUE_GREY_700
                container.border = ft.border.all(1, ft.Colors.BLUE_GREY_500)
            
            if game_instance.path and game_instance.path[-1] == (r, c):
                container.bgcolor = ft.Colors.TEAL_600
        page.update()

    def handle_click(e, r, c):
        nonlocal is_solved
        
        if game_instance is None: 
            return
            
        if next_btn.visible: 
            return 
            
        if game_instance.path and game_instance.path[-1] == (r, c):
            game_instance.undo_move()
        else:
            game_instance.add_move(r, c)
            
        update_board()
        
        if game_instance.check_win():
            is_solved = True
            status_text.value = "Puzzle Solved! 🎉"
            status_text.color = ft.Colors.GREEN_400
            timer_text.color = ft.Colors.GREEN_300
            next_btn.visible = True
            page.update()
            try:
                parsed_url = urllib.parse.urlparse(page.route)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                current_user = query_params.get("user", [None])[0]
                if current_user:
                    requests.post(f"http://127.0.0.1:5000/api/server_win?user={current_user}")
            except Exception as e:
                print(f"Background API Error (Game is still safe!): {e}")

    def load_level(lvl_idx):
        nonlocal game_instance, start_time, is_solved
        
        grid_size, anchors = generate_random_puzzle(lvl_idx)
        game_instance = ZipLogic(grid_size, anchors)
        
        start_time = time.time()
        is_solved = False
        timer_text.color = ft.Colors.WHITE70
        timer_text.value = "00:00"
        
        cells.clear()
        board_ui.controls.clear()
        status_text.value = f"Level {lvl_idx + 1}"
        status_text.color = ft.Colors.WHITE
        next_btn.visible = False
        
        for r in range(grid_size):
            row_ui = ft.Row(spacing=5, alignment=ft.MainAxisAlignment.CENTER)
            for c in range(grid_size):
                val = game_instance.grid[r, c]
                text = str(val) if val > 0 else ""
                
                def make_click_handler(row, col):
                    return lambda e: handle_click(e, row, col)

                block_size = 70 if grid_size <= 4 else 55 

                cell = ft.Container(
                    width=block_size, height=block_size,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(text, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.BLUE_GREY_700,
                    border_radius=8,
                    on_click=make_click_handler(r, c)
                )
                cells[(r, c)] = cell
                row_ui.controls.append(cell)
            board_ui.controls.append(row_ui)

        start_pos = game_instance.get_start_pos()
        if start_pos:
            game_instance.add_move(*start_pos)
        
        update_board()

    load_level(0)

ft.app(target=main, port=8002)