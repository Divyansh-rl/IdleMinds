import numpy as np
from enum import Enum
from dataclasses import dataclass, field
import flet as ft
import threading
import time
import random

# ---------------------------------------------------------
# 1. Data Models & Game Logic
# ---------------------------------------------------------
class RuleType(Enum):
    EQUAL = "="
    NOT_EQUAL = "≠"
    SUM = "SUM "
    GREATER_THAN = ">"
    LESS_THAN = "<"
    NONE = ""

class Orientation(Enum):
    HORIZONTAL = "H"
    VERTICAL = "V"

@dataclass
class Region:
    region_id: int
    rule_type: RuleType
    target_value: int | None = None
    cells: list[tuple[int, int]] = field(default_factory=list) 

@dataclass
class Domino:
    domino_id: int
    val1: int
    val2: int
    is_placed: bool = False
    orientation: Orientation = Orientation.HORIZONTAL 
    
    def get_values(self) -> tuple[int, int]:
        return (self.val1, self.val2)

class PipsGame:
    def __init__(self, difficulty: str):
        self.difficulty = difficulty
        self.placed_count = 0 
        self.regions: dict[int, Region] = {}
        self.dominoes: list[Domino] = []
        
        self.variation = random.choice([1, 2]) 
        
        if difficulty == "Easy":
            self.rows, self.cols = 2, 4
            self.required_dominoes = 4
        else: 
            self.rows, self.cols = 3, 6
            self.required_dominoes = 7
            
        self.board = np.full((self.rows, self.cols), -1, dtype=int)
        self.load_dynamic_level()
        
    def load_dynamic_level(self):
        level_dominoes = []
        
        if self.difficulty == "Easy":
            if self.variation == 1:
                level_dominoes = [(1, 1), (3, 4), (2, 2), (1, 3), (6, 6)] 
                self.add_region(Region(0, RuleType.EQUAL, None, [(0,0), (1,0)]))
                self.add_region(Region(1, RuleType.SUM, 7, [(0,1), (0,2)]))
                self.add_region(Region(2, RuleType.EQUAL, None, [(0,3), (1,3)]))
                self.add_region(Region(3, RuleType.LESS_THAN, 5, [(1,1), (1,2)]))
            else:
                level_dominoes = [(2, 3), (4, 6), (5, 5), (0, 0), (1, 2)]
                self.add_region(Region(0, RuleType.SUM, 5, [(0,0), (0,1)]))
                self.add_region(Region(1, RuleType.SUM, 10, [(1,0), (1,1)]))
                self.add_region(Region(2, RuleType.EQUAL, None, [(0,2), (1,2)]))
                self.add_region(Region(3, RuleType.EQUAL, None, [(0,3), (1,3)]))
                
        elif self.difficulty == "Medium":
            if self.variation == 1:
                level_dominoes = [(3, 5), (1, 3), (1, 2), (2, 6), (4, 4), (1, 6), (4, 5), (0, 0), (5, 5)] 
                self.add_region(Region(0, RuleType.EQUAL, None, [(0,1), (0,2)]))
                self.add_region(Region(1, RuleType.LESS_THAN, 4, [(0,3), (0,4)]))
                self.add_region(Region(2, RuleType.EQUAL, None, [(1,0), (1,1)]))
                self.add_region(Region(3, RuleType.EQUAL, None, [(1,4), (2,4)]))
                self.add_region(Region(4, RuleType.EQUAL, None, [(1,5), (2,5)]))
                self.add_region(Region(5, RuleType.EQUAL, 1, [(2,0)]))
                self.add_region(Region(6, RuleType.EQUAL, None, [(2,1), (2,2), (2,3)]))
            else:
                level_dominoes = [(2, 4), (5, 5), (2, 6), (1, 2), (3, 3), (1, 6), (4, 0), (6, 6), (1, 1)]
                self.add_region(Region(0, RuleType.SUM, 6, [(0,1), (0,2)]))
                self.add_region(Region(1, RuleType.EQUAL, None, [(0,3), (0,4)]))
                self.add_region(Region(2, RuleType.SUM, 8, [(1,0), (1,1)]))
                self.add_region(Region(3, RuleType.LESS_THAN, 4, [(1,4), (2,4)]))
                self.add_region(Region(4, RuleType.EQUAL, None, [(1,5), (2,5)]))
                self.add_region(Region(5, RuleType.EQUAL, 1, [(2,0)]))
                self.add_region(Region(6, RuleType.SUM, 10, [(2,1), (2,2), (2,3)]))
                
        elif self.difficulty == "Hard":
            if self.variation == 1:
                level_dominoes = [(4, 6), (5, 6), (0, 1), (2, 3), (1, 1), (6, 0), (3, 4), (5, 5), (2, 2), (4, 4), (6, 6)] 
                self.add_region(Region(0, RuleType.SUM, 10, [(0,1), (0,2)]))
                self.add_region(Region(1, RuleType.GREATER_THAN, 8, [(0,3), (0,4)]))
                self.add_region(Region(2, RuleType.NOT_EQUAL, None, [(1,0), (1,1)]))
                self.add_region(Region(3, RuleType.SUM, 5, [(1,4), (2,4)]))
                self.add_region(Region(4, RuleType.EQUAL, None, [(1,5), (2,5)]))
                self.add_region(Region(5, RuleType.EQUAL, 6, [(2,0)]))
                self.add_region(Region(6, RuleType.SUM, 12, [(2,1), (2,2), (2,3)]))
            else:
                level_dominoes = [(6, 6), (0, 0), (3, 4), (5, 6), (2, 2), (1, 5), (3, 1), (4, 4), (1, 2), (2, 5), (6, 1)]
                self.add_region(Region(0, RuleType.EQUAL, None, [(0,1), (0,2)]))
                self.add_region(Region(1, RuleType.SUM, 0, [(0,3), (0,4)]))
                self.add_region(Region(2, RuleType.SUM, 7, [(1,0), (1,1)]))
                self.add_region(Region(3, RuleType.GREATER_THAN, 10, [(1,4), (2,4)]))
                self.add_region(Region(4, RuleType.EQUAL, None, [(1,5), (2,5)]))
                self.add_region(Region(5, RuleType.EQUAL, 1, [(2,0)]))
                self.add_region(Region(6, RuleType.NOT_EQUAL, None, [(2,1), (2,2), (2,3)]))
        
        random.shuffle(level_dominoes)
        self.dominoes = [Domino(domino_id=i, val1=a, val2=b) for i, (a, b) in enumerate(level_dominoes)]
        
    def add_region(self, region: Region):
        self.regions[region.region_id] = region
        
    def get_region_at(self, r: int, c: int) -> Region | None:
        for region in self.regions.values():
            if (r, c) in region.cells:
                return region
        return None

    def check_region_valid(self, region: Region) -> bool:
        values: list[int] = []
        is_full = True
        
        for r, c in region.cells:
            val = int(self.board[r, c])
            if val == -1:
                is_full = False
            else:
                values.append(val)
                
        if not values: return True
            
        if region.rule_type == RuleType.EQUAL:
            return len(set(values)) == 1 
        elif region.rule_type == RuleType.NOT_EQUAL:
            return len(set(values)) == len(values) 
            
        current_sum = sum(values)
        if region.rule_type == RuleType.SUM:
            if is_full: return current_sum == region.target_value
            else: return current_sum <= region.target_value # type: ignore
        elif region.rule_type == RuleType.GREATER_THAN:
            if is_full: return current_sum > region.target_value # type: ignore
            else: return True 
        elif region.rule_type == RuleType.LESS_THAN:
            return current_sum < region.target_value # type: ignore
            
        return True

# ---------------------------------------------------------
# 2. UI Components (SCALED FOR WEB)
# ---------------------------------------------------------

def get_pip_face(val: int, color: str) -> ft.Control:
    if val <= 0:
        return ft.Container(width=70, height=70) 
        
    def dot(left: float, top: float):
        return ft.Container(width=14, height=14, border_radius=7, bgcolor=color, left=left, top=top)
        
    dots: list[ft.Control] = []
    if val in [1, 3, 5]: dots.append(dot(28, 28)) # Center
    if val in [2, 3, 4, 5, 6]:
        dots.append(dot(12, 12)) # Top Left
        dots.append(dot(44, 44)) # Bottom Right
    if val in [4, 5, 6]:
        dots.append(dot(44, 12)) # Top Right
        dots.append(dot(12, 44)) # Bottom Left
    if val == 6:
        dots.append(dot(12, 28)) # Middle Left
        dots.append(dot(44, 28)) # Middle Right

    return ft.Container(width=70, height=70, content=ft.Stack(controls=dots, width=70, height=70))

def create_domino_ui(domino: Domino) -> ft.Control:
    face1 = get_pip_face(domino.val1, ft.Colors.BLACK) # type: ignore
    face2 = get_pip_face(domino.val2, ft.Colors.BLACK) # type: ignore
    
    divider = ft.Container(width=2, height=70, bgcolor=ft.Colors.BLACK) # type: ignore
    
    def make_horizontal():
        divider.width, divider.height = 2, 70
        return ft.Row([
            ft.Container(content=face1, alignment=ft.Alignment(0, 0), expand=1),
            divider,
            ft.Container(content=face2, alignment=ft.Alignment(0, 0), expand=1),
        ], spacing=0)
        
    def make_vertical():
        divider.width, divider.height = 70, 2
        return ft.Column([
            ft.Container(content=face1, alignment=ft.Alignment(0, 0), expand=1),
            divider,
            ft.Container(content=face2, alignment=ft.Alignment(0, 0), expand=1),
        ], spacing=0)

    inner_box = ft.Container(
        width=140, height=70, 
        border=ft.Border.all(2, ft.Colors.BLACK), # type: ignore
        border_radius=12, 
        bgcolor=ft.Colors.WHITE, # type: ignore
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=4, color=ft.Colors.with_opacity(0.15, "black"), offset=ft.Offset(0, 2)), # type: ignore
        content=make_horizontal()
    )

    def rotate_domino(e: ft.ControlEvent):
        if domino.orientation == Orientation.HORIZONTAL:
            domino.orientation = Orientation.VERTICAL
            inner_box.width, inner_box.height = 70, 140
            inner_box.content = make_vertical()
        else:
            domino.orientation = Orientation.HORIZONTAL
            inner_box.width, inner_box.height = 140, 70
            inner_box.content = make_horizontal()
        inner_box.update()

    inner_box.on_click = rotate_domino
    return ft.Draggable(group="domino", content=inner_box, data=str(domino.domino_id))

# ---------------------------------------------------------
# 3. Game State & Screen Navigation
# ---------------------------------------------------------

app_state = {
    "timer_running": False,
    "time_left": 60,
    "timer_text": ft.Text("01:00", size=36, weight=ft.FontWeight.W_900, color="#D9534F")
}

def main(page: ft.Page):
    page.title = "NYT Pips Game"
    page.padding = 60
    page.theme = ft.Theme(font_family="Helvetica") # type: ignore

    def show_popup(message: str, btn_text: str, color: str):
        def on_close(e):
            dialog.open = False
            page.update()
            
            def transition_to_home():
                time.sleep(0.2) 
                if dialog in page.overlay:
                    page.overlay.remove(dialog) 
                show_home_screen() 
                
            threading.Thread(target=transition_to_home, daemon=True).start()
            
        dialog = ft.AlertDialog(
            modal=True, 
            title=ft.Text(message, size=24, color=color, weight=ft.FontWeight.W_900, text_align=ft.TextAlign.CENTER), # type: ignore
            actions=[
                ft.ElevatedButton(btn_text, on_click=on_close, bgcolor=color, color=ft.Colors.WHITE, style=ft.ButtonStyle(padding=20)) # type: ignore
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER, # type: ignore
            shape=ft.RoundedRectangleBorder(radius=16) 
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def run_timer():
        while app_state["timer_running"] and app_state["time_left"] > 0:
            time.sleep(1)
            if not app_state["timer_running"]:
                break
                
            app_state["time_left"] -= 1
            
            try:
                seconds = app_state["time_left"]
                app_state["timer_text"].value = f"00:{seconds:02d}"
                app_state["timer_text"].update()
            except Exception:
                pass
                
        if app_state["time_left"] == 0 and app_state["timer_running"]:
            app_state["timer_running"] = False
            try:
                show_popup("Time's Up, restart again!", "OK", "#D9534F")
            except Exception:
                pass

    def show_home_screen(e=None):
        app_state["timer_running"] = False 
        page.controls.clear()
        page.overlay.clear() 
        page.vertical_alignment = ft.MainAxisAlignment.CENTER # type: ignore
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER # type: ignore
        
        page.bgcolor = "#DAA8D0" 

        menu_ui = ft.Column([
            ft.Text("PIPS", size=72, weight=ft.FontWeight.W_900, color=ft.Colors.BLUE_GREY_900), # type: ignore
            ft.Container(height=20),
            
            ft.Text("Select Difficulty", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900), # type: ignore
            ft.Container(height=10),
            
            ft.ElevatedButton("Easy", on_click=lambda _: show_game_screen("Easy"), bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE, width=250, height=60, style=ft.ButtonStyle(text_style=ft.TextStyle(size=20))), # type: ignore
            ft.ElevatedButton("Medium", on_click=lambda _: show_game_screen("Medium"), bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE, width=250, height=60, style=ft.ButtonStyle(text_style=ft.TextStyle(size=20))), # type: ignore
            ft.ElevatedButton("Hard", on_click=lambda _: show_game_screen("Hard"), bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE, width=250, height=60, style=ft.ButtonStyle(text_style=ft.TextStyle(size=20))), # type: ignore
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER) # type: ignore

        page.add(menu_ui)
        page.update()

    def show_game_screen(difficulty: str):
        page.controls.clear()
        
        page.bgcolor = "#FFF0F5" 
        page.vertical_alignment = ft.MainAxisAlignment.CENTER # type: ignore
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER # type: ignore
        
        app_state["time_left"] = 60
        app_state["timer_text"].value = "01:00"
        app_state["timer_text"].color = "#D9534F"
        app_state["timer_running"] = True
        threading.Thread(target=run_timer, daemon=True).start()

        game = PipsGame(difficulty) 
        
        ui_grid: dict[tuple[int, int], ft.Container] = {}

        region_styles = {
            0: {"bg": "#B89CC7", "border": "#632782"}, 
            1: {"bg": "#DE95A3", "border": "#B9123A"}, 
            2: {"bg": "#8EB1B6", "border": "#0F5B64"}, 
            3: {"bg": "#DFB387", "border": "#C15200"}, 
            4: {"bg": "#939CA8", "border": "#133454"}, 
            5: {"bg": "#A5B895", "border": "#2E550B"}, 
            6: {"bg": "#B89CC7", "border": "#632782"}, 
        }

        def on_domino_drop(e: ft.DragTargetEvent):
            target_zone = e.control 
            dragged_item = page.get_control(e.src_id) 
            domino = game.dominoes[int(dragged_item.data)] # type: ignore
            
            r1, c1 = target_zone.data # type: ignore
            if domino.orientation == Orientation.HORIZONTAL:
                r2, c2 = r1, c1 + 1
            else:
                r2, c2 = r1 + 1, c1
                
            if r2 >= game.rows or c2 >= game.cols or game.board[r1, c1] != -1 or game.board[r2, c2] != -1:
                return 
                
            if game.get_region_at(r1, c1) is None or game.get_region_at(r2, c2) is None:
                return

            game.board[r1, c1] = domino.val1
            game.board[r2, c2] = domino.val2
            
            region1 = game.get_region_at(r1, c1)
            region2 = game.get_region_at(r2, c2)
            
            valid = True
            if region1 and not game.check_region_valid(region1): valid = False
            if region2 and not game.check_region_valid(region2): valid = False
            
            if not valid:
                game.board[r1, c1] = -1 
                game.board[r2, c2] = -1
                
                error_snack = ft.SnackBar(
                    content=ft.Text("Invalid Placement! Breaks region math.", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=18), # type: ignore
                    bgcolor="#D9534F",
                    duration=2000
                )
                page.overlay.append(error_snack)
                error_snack.open = True
                page.update()
                return 

            domino.is_placed = True
            game.placed_count += 1
            
            for (r, c), val in [((r1, c1), domino.val1), ((r2, c2), domino.val2)]:
                cell_ui = ui_grid[(r, c)]
                number_layer = cell_ui.content.controls[1] # type: ignore
                number_layer.content = get_pip_face(val, ft.Colors.BLACK) # type: ignore
                cell_ui.bgcolor = ft.Colors.WHITE # type: ignore
                cell_ui.update()
            
            dragged_item.visible = False 
            dragged_item.update()
            
            if game.placed_count == game.required_dominoes:
                app_state["timer_running"] = False 
                app_state["timer_text"].color = "#4CAF50" 
                app_state["timer_text"].update()
                
                show_popup("Yes you solved it!", "OK", "#4CAF50")

        grid_rows: list[ft.Control] = []
        for r in range(game.rows):
            row_cells: list[ft.Control] = []
            for c in range(game.cols):
                region = game.get_region_at(r, c)
                
                if region is None:
                    row_cells.append(ft.Container(width=70, height=70, bgcolor=ft.Colors.TRANSPARENT)) # type: ignore
                    continue
                    
                style = region_styles.get(region.region_id, {"bg": ft.Colors.WHITE, "border": ft.Colors.BLACK}) # type: ignore
                bg_color = style["bg"]
                border_color = style["border"]
                rule_text = ""
                
                if region.cells[0] == (r, c):
                    if region.rule_type == RuleType.SUM:
                        rule_text = str(region.target_value) if region.target_value is not None else ""
                    else:
                        rule_text = f"{region.rule_type.value}"
                        if region.target_value is not None:
                            rule_text += str(region.target_value)
                
                rule_display = ft.Container()
                if rule_text:
                    # FIX: Using ft.Alignment(0, 0) instead of ft.alignment.center
                    rule_display = ft.Container(
                        width=42, height=42, 
                        bgcolor=border_color,
                        border_radius=6,
                        rotate=0.785398, 
                        alignment=ft.Alignment(0, 0), # Correct version-safe centering
                        shadow=ft.BoxShadow(spread_radius=0, blur_radius=4, color=ft.Colors.with_opacity(0.3, "black"), offset=ft.Offset(2, 2)), # type: ignore
                        content=ft.Container(
                            rotate=-0.785398, 
                            alignment=ft.Alignment(0, 0), # Correct version-safe centering
                            content=ft.Text(rule_text, size=18, color=ft.Colors.WHITE, weight=ft.FontWeight.W_900, text_align=ft.TextAlign.CENTER) # type: ignore
                        )
                    )
                
                cell_content = ft.Stack(
                    clip_behavior=ft.ClipBehavior.NONE, # type: ignore
                    controls=[
                        ft.Container(content=rule_display, alignment=ft.Alignment(-1.1, -1.1)),
                        ft.Container(content=ft.Container(), alignment=ft.Alignment(0, 0)) 
                    ]
                )

                cell_container = ft.Container(
                    width=70, height=70, 
                    border=ft.Border.all(3, border_color), 
                    border_radius=8, 
                    bgcolor=bg_color,
                    content=cell_content
                )
                
                ui_grid[(r, c)] = cell_container
                
                drop_zone = ft.DragTarget(group="domino", content=cell_container, data=(r, c), on_accept=on_domino_drop)
                row_cells.append(drop_zone)
            
            grid_rows.append(ft.Row(controls=row_cells, spacing=0, alignment=ft.MainAxisAlignment.CENTER)) # type: ignore
            
        board_ui = ft.Column(controls=grid_rows, spacing=0, alignment=ft.MainAxisAlignment.CENTER) # type: ignore
        
        bank_row = ft.Row(wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=20, run_spacing=20) # type: ignore
        for d in game.dominoes:
            bank_row.controls.append(create_domino_ui(d)) # type: ignore
            
        bank_ui = ft.Container(
            content=ft.Column([bank_row], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), # type: ignore
            width=900, height=250, 
            margin=ft.Margin.only(top=50), # type: ignore
            border=ft.Border.all(2, "#F8BBD0"), 
            bgcolor=ft.Colors.WHITE, # type: ignore
            border_radius=16,
            padding=25,
            alignment=ft.Alignment(0, 0)
        )

        header = ft.Row([
            ft.TextButton("← Main Menu", on_click=show_home_screen, style=ft.ButtonStyle(color=ft.Colors.BLUE_GREY_900, text_style=ft.TextStyle(size=18))), # type: ignore
            app_state["timer_text"]
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=900) # type: ignore

        page.add(
            header,
            ft.Container(height=10),
            ft.Text("Pips", size=56, weight=ft.FontWeight.W_900, color=ft.Colors.BLUE_GREY_900), # type: ignore
            ft.Text("Place every domino in the right spot.", size=22, color=ft.Colors.BLUE_GREY_700), # type: ignore
            ft.Container(height=20),
            board_ui, 
            bank_ui
        ) 

    show_home_screen()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)