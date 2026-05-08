import flet as ft
import os
import sqlite3

# --- BANCO DE DADOS (Mensagens e Usuários) ---
def init_db():
    conn = sqlite3.connect("chat.db", check_same_thread=False)
    cursor = conn.cursor()
    # Tabela de Mensagens
    cursor.execute('''CREATE TABLE IF NOT EXISTS mensagens 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, autor TEXT, texto TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

def main(page: ft.Page):
    page.title = "Chat Gamers"
    page.theme_mode = "light"
    page.auto_scroll = True

    # Variável simples de Python para segurar o nome nesta sessão
    sessao_usuario = {"nome": "", "email": ""}
    
    chat = ft.Column(expand=True, scroll="always", spacing=10)

    def criar_balao(texto, autor):
        sou_eu = (autor == sessao_usuario["nome"])
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text(autor, size=10, color="white", weight="bold"),
                        ft.Text(texto, color="white", size=16),
                    ], spacing=2, tight=True),
                    padding=12,
                    bgcolor="#005c4b" if sou_eu else "#333333",
                    border_radius=ft.border_radius.only(
                        top_left=15, top_right=15, 
                        bottom_left=0 if not sou_eu else 15, 
                        bottom_right=0 if sou_eu else 15
                    ),
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

    txt_msg = ft.TextField(hint_text="Mensagem...", expand=True, border_radius=20, on_submit=lambda _: enviar(None))

    def enviar(e):
        if txt_msg.value and sessao_usuario["nome"]:
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO mensagens (autor, texto) VALUES (?, ?)", (sessao_usuario["nome"], txt_msg.value))
            db_conn.commit()
            page.pubsub.send_all({"autor": sessao_usuario["nome"], "texto": txt_msg.value})
            txt_msg.value = ""
            page.update()

    def abrir_chat():
        page.clean()
        page.add(
            ft.Container(
                content=ft.Row([
                    ft.Text(f"Chat: {sessao_usuario['nome']}", color="white", weight="bold", expand=True),
                    ft.IconButton(icon=ft.icons.REFRESH, icon_color="white", on_click=lambda _: carregar_historico())
                ]),
                bgcolor="#008069", padding=10
            ),
            chat,
            ft.Container(content=ft.Row([txt_msg, ft.ElevatedButton("Enviar", on_click=enviar)]), padding=10)
        )
        carregar_historico()

    def salvar_cadastro(e):
        if input_nome.value and input_email.value:
            sessao_usuario["nome"] = input_nome.value
            sessao_usuario["email"] = input_email.value
            abrir_chat()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha tudo!"))
            page.snack_bar.open = True
            page.update()

    input_nome = ft.TextField(label="Nome", width=300)
    input_email = ft.TextField(label="E-mail", width=300)

    # Tela de Cadastro Inicial (Sem usar storage para evitar erros)
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("Cadastro Gamers", size=30, weight="bold"),
                input_nome,
                input_email,
                ft.ElevatedButton("Entrar no Chat", on_click=salvar_cadastro)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=50, alignment=ft.alignment.center
        )
    )

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=porta, host="0.0.0.0")
