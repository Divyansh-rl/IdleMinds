import flet as ft
import numpy as np
import random

MAX_TRIES = 5

WORDS = [
    "apple", "grape", "mango", "peach", "berry",
    "lemon", "melon", "guava", "plums"
]

def check_guess(guess, word):
    guess_arr = np.array(list(guess))
    word_arr = np.array(list(word))

    result = ["⬛"] * 5
    used = [False] * 5

    for i in range(5):
        if guess_arr[i] == word_arr[i]:
            result[i] = "🟩"
            used[i] = True

    for i in range(5):
        if result[i] == "⬛":
            for j in range(5):
                if not used[j] and guess_arr[i] == word_arr[j]:
                    result[i] = "🟨"
                    used[j] = True
                    break

    return result

def main(page: ft.Page):
    page.title = "WordCraft"
    page.bgcolor = "#121213"

    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    current_word = random.choice(WORDS)
    guesses = []

    grid = ft.Column(
        spacing=10,
        alignment="center",
        horizontal_alignment="center"
    )

    input_box = ft.TextField(
        hint_text="Enter 5-letter word",
        width=220,
        text_align="center"
    )

    message = ft.Text(color="white")
    reveal = ft.Text(color="red", weight="bold")

    def build_grid():
        grid.controls.clear()

        for i in range(MAX_TRIES):
            row = ft.Row(alignment="center")

            if i < len(guesses):
                guess, result = guesses[i]
            else:
                guess, result = "     ", ["⬛"] * 5

            for j in range(5):
                letter = guess[j].upper() if guess[j] != " " else ""

                color = "#121213"

                if i < len(guesses):
                    color = "#3a3a3c"
                    if result[j] == "🟩":
                        color = "#66BB6A"
                    elif result[j] == "🟨":
                        color = "#FFD54F"

                box = ft.Container(
                    width=60,
                    height=60,
                    bgcolor=color,
                    border=ft.border.all(2, "#3a3a3c"),
                    border_radius=6,
                    content=ft.Column(
                        [ft.Text(letter, size=24, weight="bold", color="white")],
                        alignment="center",
                        horizontal_alignment="center"
                    )
                )

                row.controls.append(box)

            grid.controls.append(row)

        page.update()

    def submit(e=None):
        nonlocal current_word

        guess = (input_box.value or "").lower().strip()

        if len(guess) != 5:
            message.value = "Enter a 5-letter word"
            page.update()
            return

        if len(guesses) >= MAX_TRIES:
            return

        result = check_guess(guess, current_word)
        guesses.append((guess, result))

        input_box.value = ""

        if guess == current_word:
            message.value = "🎉 You won!"
            reveal.value = f"Word: {current_word}"
            input_box.disabled = True

        elif len(guesses) == MAX_TRIES:
            message.value = "❌ Game Over!"
            reveal.value = f"Word: {current_word}"
            input_box.disabled = True
        else:
            message.value = ""

        build_grid()

    input_box.on_submit = submit

    def reset(e):
        nonlocal current_word
        current_word = random.choice(WORDS)
        guesses.clear()

        input_box.value = ""
        input_box.disabled = False
        message.value = ""
        reveal.value = ""

        build_grid()

    submit_btn = ft.ElevatedButton("Submit", on_click=submit)
    reset_btn = ft.ElevatedButton("New Game", on_click=reset)

    page.add(
        ft.Text("WORDCRAFT", size=34, weight="bold", color="white"),
        grid,
        input_box,
        ft.Row([submit_btn, reset_btn], alignment="center"),
        message,
        reveal
    )

    build_grid()

ft.app(target=main, port=8003)