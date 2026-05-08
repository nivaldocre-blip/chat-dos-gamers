import flet as ft
import os
import sqlite3

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect("chat.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS mensagens 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, autor TEXT, texto TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

def main(page: ft.Page):
    page.title = "Chat Gamers"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    sessao = {"nome": "", "email": ""}
    chat = ft.Column(expand=True, scroll=ft.ScrollMode.ALWAYS, spacing=10)

    def criar_balao(texto, autor):
        sou_eu = (autor == sessao["nome"])
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text(autor, size=10, color="white", weight="bold"),
                        ft.Text(texto, color="white", size=16),
                    ], spacing=2, tight=True),
                    padding=12,
                    bgcolor="#005c4b" if sou_eu else "#333333",
                    # CORREÇÃO: Usando valor numérico direto para evitar o erro de 'attribute all'
                    border_radius=15, 
                )
            ],
            alignment=ft.MainAxisAlignment.END if sou_eu else ft.MainAxisAlignment.START
        )

    def carregar_historico():
        chat.controls.clear()
        cursor = db_conn.cursor()
        cursor.execute("SELECT autor, texto FROM mensagens ORDER BY id ASC")
        for row in cursor.fetchall():
            chat.controls.append(criar_balao(row[1], row[0]))
        page.update()

    def on_message(msg):
        chat.controls.append(criar_balao(msg['texto'], msg['autor']))
        page.update()

    page.pubsub.subscribe(on_message)

    def enviar_msg(e):
        if txt_msg.value and sessao["nome"]:
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO mensagens (autor, texto) VALUES (?, ?)", (sessao["nome"], txt_msg.value))
            db_conn.commit()
            page.pubsub.send_all({"autor": sessao["nome"], "texto": txt_msg.value})
            txt_msg.value = ""
            page.update()

    txt_msg = ft.TextField(
        hint_text="Mensagem...", 
        expand=True, 
        border_radius=20,
        on_submit=enviar_msg
    )

    def abrir_chat():
        page.clean()
        page.add(
            ft.Container(
                content=ft.Row([
                    ft.Text(f"Chat: {sessao['nome']}", color="white", weight="bold", expand=True),
                    ft.TextButton(
                        content=ft.Text("Atualizar", color="white"), 
                        on_click=lambda _: carregar_historico()
                    )
                ]),
                bgcolor="#008069", padding=15, border_radius=10
            ),
            chat,
            ft.Container(
                content=ft.Row([
                    txt_msg, 
                    ft.ElevatedButton("Enviar", on_click=enviar_msg)
                ]), 
                padding=10
            )
        )
        carregar_historico()

    input_nome = ft.TextField(label="Nome", width=300)
    input_email = ft.TextField(label="E-mail", width=300)

    def finalizar_cadastro(e):
        if input_nome.value:
            sessao["nome"] = input_nome.value
            sessao["email"] = input_email.value
            abrir_chat()
        else:
            page.update()

    page.add(
        ft.Column([
            ft.Text("🎮 Cadastro Gamers", size=30, weight="bold"),
            ft.Container(height=10),
            input_nome,
            input_email,
            ft.Container(height=10),
            ft.ElevatedButton("Entrar no Chat", on_click=finalizar_cadastro)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=porta, host="0.0.0.0")
