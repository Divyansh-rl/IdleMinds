import numpy as np
import flet as ft
import random

weekly_groups = {
    "Monday": {
        "Fruits": ["Apple", "Mango", "Banana", "Orange"],
        "Colors": ["Red", "Blue", "Green", "Yellow"],
        "Animals": ["Dog", "Cat", "Lion", "Tiger"],
        "Vehicles": ["Car", "Bus", "Bike", "Truck"]
    },
    "Tuesday": {
        "Sports": ["Cricket", "Football", "Tennis", "Hockey"],
        "Countries": ["India", "USA", "Japan", "Brazil"],
        "Birds": ["Parrot", "Crow", "Sparrow", "Eagle"],
        "Tech": ["Laptop", "Mobile", "Tablet", "Camera"]
    },
    "Wednesday": {
        "Subjects": ["Math", "Science", "English", "History"],
        "Clothes": ["Shirt", "Pants", "Jacket", "Tshirt"],
        "Drinks": ["Tea", "Coffee", "Juice", "Milk"],
        "Flowers": ["Rose", "Lily", "Lotus", "Sunflower"]
    },
    "Thursday": {
        "Shapes": ["Circle", "Square", "Triangle", "Rectangle"],
        "Planets": ["Earth", "Mars", "Jupiter", "Venus"],
        "Body": ["Head", "Hand", "Leg", "Eye"],
        "Music": ["Guitar", "Piano", "Drum", "Flute"]
    },
    "Friday": {
        "Jobs": ["Doctor", "Engineer", "Teacher", "Police"],
        "Games": ["Chess", "Ludo", "Carrom", "Poker"],
        "Languages": ["Hindi", "English", "Spanish", "French"],
        "Weather": ["Hot", "Cold", "Rainy", "Windy"]
    },
    "Saturday": {
        "Food": ["Pizza", "Burger", "Pasta", "Noodles"],
        "Transport": ["Train", "Plane", "Ship", "Cycle"],
        "Nature": ["River", "Mountain", "Forest", "Desert"],
        "Time": ["Morning", "Noon", "Evening", "Night"]
    },
    "Sunday": {
        "Festivals": ["Diwali", "Holi", "Eid", "Christmas"],
        "Emotions": ["Happy", "Sad", "Angry", "Excited"],
        "Tools": ["Hammer", "Screwdriver", "Wrench", "Drill"],
        "School": ["Book", "Pen", "Bag", "Board"]
    }
}

all_groups = sum([list(day.values()) for day in weekly_groups.values()], [])
group_names = sum([list(day.keys()) for day in weekly_groups.values()], [])

def generate_random_groups():
    selected = random.sample(list(zip(group_names, all_groups)), 4)
    return dict(selected)

groups = generate_random_groups()

all_words = np.array(sum(groups.values(), []))
np.random.shuffle(all_words)

def check_group(selected_words):
    for group_name, words in groups.items():
        if set(selected_words) == set(words):
            return True, group_name
    return False, None

def main(page: ft.Page):
    page.title = "Connections Game"
    page.window_width = 350
    page.window_height = 600
    page.bgcolor = "#fafafa"

    selected = []
    buttons = []
    solved_words = set()
    mistakes = 0
    solved_groups = 0

    result_text = ft.Text("Select 4 words", size=18, weight="bold")
    mistake_text = ft.Text("Mistakes: 0 / 4", size=14)

    def word_click(e):
        word = e.control.content.value

        if word in solved_words:
            return

        if word in selected:
            selected.remove(word)
            e.control.bgcolor = "#ffffff"
        else:
            if len(selected) < 4:
                selected.append(word)
                e.control.bgcolor = "#ffe082"

        page.update()

    def check_click(e):
        nonlocal mistakes, solved_groups

        if len(selected) == 4:
            correct, group = check_group(selected)

            if correct:
                solved_groups += 1
                result_text.value = f"✅ {group}"

                for btn in buttons:
                    if btn.content.value in selected:
                        btn.bgcolor = "#81c784"
                        btn.disabled = True
                        solved_words.add(btn.content.value)

            else:
                mistakes += 1
                result_text.value = "❌ Wrong group!"
                mistake_text.value = f"Mistakes: {mistakes} / 4"

            selected.clear()

            for btn in buttons:
                if btn.content.value not in solved_words:
                    btn.bgcolor = "#ffffff"

            if solved_groups == 4:
                result_text.value = "🎉 You Won The Game"

            if mistakes == 4:
                result_text.value = "💀 Game Over!"

            page.update()

    def on_hover(e):
        e.control.bgcolor = "#1e88e5" if e.data == "true" else "#64b5f6"
        e.control.update()

    for word in all_words:
        btn = ft.ElevatedButton(
            content=ft.Text(
                word,
                size=10,
                color="#424242",
                weight="bold"
            ),
            on_click=word_click,
            width=65,
            height=35,
            bgcolor="#ffffff",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6)
            )
        )
        buttons.append(btn)

    check_btn = ft.ElevatedButton(
        content=ft.Text("Check", color="white"),
        on_click=check_click,
        bgcolor="#64b5f6",
        on_hover=on_hover
    )

    page.add(
        ft.Column(
            [
                ft.Text("🧠 Connections Game", size=22, weight="bold"),
                result_text,
                mistake_text,
                ft.GridView(
                    controls=buttons,
                    runs_count=4,
                    spacing=5,
                    run_spacing=5,
                    expand=True
                ),
                check_btn
            ],
            alignment="center",
            horizontal_alignment="center",
            expand=True
        )
    )

ft.app(target=main, port=8004)