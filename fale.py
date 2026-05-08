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
    
    # Variável de sessão (Saber quem está logado agora)
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
                    border_radius=ft.border_radius.all(15),
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

    txt_msg = ft.TextField(hint_text="Digite sua mensagem...", expand=True, border_radius=20)

    def enviar(e):
        if txt_msg.value and sessao["nome"]:
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO mensagens (autor, texto) VALUES (?, ?)", (sessao["nome"], txt_msg.value))
            db_conn.commit()
            page.pubsub.send_all({"autor": sessao["nome"], "texto": txt_msg.value})
            txt_msg.value = ""
            page.update()

    # --- TELA DE CHAT ---
    def abrir_chat():
        page.clean()
        page.add(
            ft.Container(
                content=ft.Row([
                    ft.Text(f"Usuário: {sessao['nome']}", color="white", weight="bold", expand=True),
                    ft.IconButton(icon=ft.icons.REFRESH, icon_color="white", on_click=lambda _: carregar_historico())
                ]),
                bgcolor="#008069", padding=15, border_radius=10
            ),
            chat,
            ft.Container(
                content=ft.Row([
                    txt_msg, 
                    ft.IconButton(icon=ft.icons.SEND, on_click=enviar, icon_color="#008069")
                ]), 
                padding=10
            )
        )
        carregar_historico()

    # --- TELA DE CADASTRO (Centralizada com Column) ---
    input_nome = ft.TextField(label="Seu Nome", width=300, border_radius=10)
    input_email = ft.TextField(label="Seu E-mail", width=300, border_radius=10)

    def finalizar_cadastro(e):
        if input_nome.value and input_email.value:
            sessao["nome"] = input_nome.value
            sessao["email"] = input_email.value
            abrir_chat()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, preencha nome e e-mail!"))
            page.snack_bar.open = True
            page.update()

    # Montando a tela de cadastro centralizada de forma segura
    page.add(
        ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("🎮 Cadastro Gamers", size=32, weight="bold"),
                        ft.Text("Preencha para entrar no chat", size=16, color="grey"),
                        ft.VerticalDivider(height=20, color="transparent"),
                        input_nome,
                        input_email,
                        ft.VerticalDivider(height=10, color="transparent"),
                        ft.ElevatedButton(
                            "Entrar no Chat", 
                            on_click=finalizar_cadastro,
                            style=ft.ButtonStyle(padding=20)
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=porta, host="0.0.0.0")
