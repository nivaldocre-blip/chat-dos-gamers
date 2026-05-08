import flet as ft
import os
import sqlite3

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect("chat.db", check_same_thread=False)
    cursor = conn.cursor()
    # Tabela de mensagens
    cursor.execute('''CREATE TABLE IF NOT EXISTS mensagens 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, autor TEXT, texto TEXT)''')
    # TABELA DE USUÁRIOS (Para não perder os dados no celular)
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                      (email TEXT PRIMARY KEY, nome TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

def main(page: ft.Page):
    page.title = "Chat Gamers"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    sessao = {"nome": "", "email": ""}
    chat = ft.Column(expand=True, scroll=ft.ScrollMode.ALWAYS, spacing=10)
    
    # Campos de entrada
    input_nome = ft.TextField(label="Nome", width=300)
    
    def buscar_usuario(e):
        """Busca o nome no banco de dados assim que o e-mail é digitado"""
        if input_email.value:
            cursor = db_conn.cursor()
            cursor.execute("SELECT nome FROM usuarios WHERE email = ?", (input_email.value.lower(),))
            row = cursor.fetchone()
            if row:
                input_nome.value = row[0]
                page.update()

    input_email = ft.TextField(
        label="E-mail (Chave de Acesso)", 
        width=300, 
        on_blur=buscar_usuario, # Busca quando clica fora do campo
        on_change=buscar_usuario # Busca enquanto digita
    )

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

    txt_msg = ft.TextField(hint_text="Mensagem...", expand=True, border_radius=20, on_submit=enviar_msg)

    def abrir_chat():
        page.clean()
        page.add(
            ft.Container(
                content=ft.Row([
                    ft.Text(f"Chat: {sessao['nome']}", color="white", weight="bold", expand=True),
                    ft.TextButton(content=ft.Text("Trocar Conta", color="white"), on_click=lambda _: desenhar_cadastro())
                ]),
                bgcolor="#008069", padding=15, border_radius=10
            ),
            chat,
            ft.Container(content=ft.Row([txt_msg, ft.ElevatedButton("Enviar", on_click=enviar_msg)]), padding=10)
        )
        carregar_historico()

    def finalizar_cadastro(e):
        if input_nome.value and input_email.value:
            sessao["nome"] = input_nome.value
            sessao["email"] = input_email.value.lower()
            
            # SALVA NO BANCO DE DADOS DO SERVIDOR (Garante que não apague)
            cursor = db_conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO usuarios (email, nome) VALUES (?, ?)", 
                           (sessao["email"], sessao["nome"]))
            db_conn.commit()
            
            abrir_chat()

    def desenhar_cadastro():
        page.clean()
        page.add(
            ft.Column([
                ft.Text("🎮 Cadastro Gamers", size=30, weight="bold"),
                ft.Text("O nome será lembrado pelo seu e-mail", size=12),
                ft.Container(height=10),
                input_email,
                input_nome,
                ft.Container(height=10),
                ft.ElevatedButton("Entrar no Chat", on_click=finalizar_cadastro)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

    desenhar_cadastro()

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=porta, host="0.0.0.0")
