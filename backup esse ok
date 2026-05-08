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
    page.title = "Chat Família"
    page.theme_mode = "light"
    # IMPORTANTE: Isso ajuda o app a não "morrer" em segundo plano
    page.auto_scroll = True  
    usuario = {"nome": ""}
    chat = ft.Column(expand=True, scroll="always", spacing=10)
    def criar_balao(texto, autor):
        sou_eu = (autor == usuario["nome"])
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
    def carregar_mensagens():
        chat.controls.clear() # Limpa para não duplicar na reconexão
        cursor = db_conn.cursor()
        cursor.execute("SELECT autor, texto FROM mensagens ORDER BY id ASC")
        for row in cursor.fetchall():
            chat.controls.append(criar_balao(row[1], row[0]))
        page.update()
    def on_message(msg):
        chat.controls.append(criar_balao(msg['texto'], msg['autor']))
        page.update()
    page.pubsub.subscribe(on_message)
    txt_msg = ft.TextField(
        hint_text="Mensagem...", 
        expand=True, 
        border_radius=20, 
        on_submit=lambda _: enviar(None)
    )
    def enviar(e):
        if txt_msg.value and usuario["nome"]:
            try:
                cursor = db_conn.cursor()
                cursor.execute("INSERT INTO mensagens (autor, texto) VALUES (?, ?)", (usuario["nome"], txt_msg.value))
                db_conn.commit()
                page.pubsub.send_all({"autor": usuario["nome"], "texto": txt_msg.value})
                txt_msg.value = ""
                page.update()
            except:
                # Se falhar (perdeu conexão), tenta recarregar a página
                page.update()
    nome_input = ft.TextField(label="Seu Nome", width=300)
    def entrar(e):
        if nome_input.value:
            usuario["nome"] = nome_input.value
            page.clean()
            page.add(
                ft.Container(content=ft.Text(f"Chat: {usuario['nome']}", color="white"), bgcolor="#008069", padding=15),
                chat,
                ft.Container(content=ft.Row([txt_msg, ft.ElevatedButton("Enviar", on_click=enviar)]), padding=10)
            )
            carregar_mensagens()
    page.add(
        ft.Column([
            ft.Text("Chat Família", size=30, weight="bold"),
            nome_input,
            ft.ElevatedButton("Entrar", on_click=entrar)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )
if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    # 'view=ft.AppView.WEB_BROWSER' é o que permite o "Adicionar à tela inicial" funcionar bem
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=porta, host="0.0.0.0")
