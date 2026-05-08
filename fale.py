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
    
    usuario = {"nome": ""}
    chat = ft.Column(expand=True, scroll=ft.ScrollMode.ALWAYS)

    def on_message(msg):
        chat.controls.append(ft.Text(f"{msg['autor']}: {msg['texto']}"))
        page.update()

    page.pubsub.subscribe(on_message)

    def enviar(e):
        if txt_msg.value:
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO mensagens (autor, texto) VALUES (?, ?)", (usuario["nome"], txt_msg.value))
            db_conn.commit()
            page.pubsub.send_all({"autor": usuario["nome"], "texto": txt_msg.value})
            txt_msg.value = ""
            page.update()

    txt_msg = ft.TextField(label="Mensagem", expand=True)
    nome_input = ft.TextField(label="Seu Nome", width=200)

    def entrar(e):
        if nome_input.value:
            usuario["nome"] = nome_input.value
            page.clean()
            page.add(
                ft.Text(f"Logado como: {usuario['nome']}", weight="bold"),
                chat,
                ft.Row([txt_msg, ft.ElevatedButton("Enviar", on_click=enviar)])
            )
            # Carregar histórico
            cursor = db_conn.cursor()
            cursor.execute("SELECT autor, texto FROM mensagens ORDER BY id ASC")
            for row in cursor.fetchall():
                chat.controls.append(ft.Text(f"{row[0]}: {row[1]}"))
            page.update()

    # TELA DE LOGIN SIMPLES (Sem o comando 'alignment' que deu erro)
    page.add(
        ft.Text("Entrar no Chat", size=25),
        nome_input,
        ft.ElevatedButton("Entrar", on_click=entrar)
    )

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    # Usando o formato mais simples para evitar avisos de 'Deprecation'
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=porta, host="0.0.0.0")
