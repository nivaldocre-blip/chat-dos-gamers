import flet as ft
import os
import sqlite3

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect("chat.db", check_same_thread=False)
    cursor = conn.cursor()
    # Adicionamos uma tabela para salvar os usuários também (opcional, para controle seu)
    cursor.execute('''CREATE TABLE IF NOT EXISTS mensagens 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, autor TEXT, texto TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

def main(page: ft.Page):
    page.title = "Chat Gamers"
    page.theme_mode = "light"
    page.auto_scroll = True

    # --- FUNÇÃO PARA CARREGAR MENSAGENS ---
    chat = ft.Column(expand=True, scroll="always", spacing=10)

    def criar_balao(texto, autor):
        # Busca o nome que está salvo no storage do celular agora
        meu_nome = page.client_storage.get("user_name")
        sou_eu = (autor == meu_nome)
        
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
        nome_salvo = page.client_storage.get("user_name")
        if txt_msg.value and nome_salvo:
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO mensagens (autor, texto) VALUES (?, ?)", (nome_salvo, txt_msg.value))
            db_conn.commit()
            page.pubsub.send_all({"autor": nome_salvo, "texto": txt_msg.value})
            txt_msg.value = ""
            page.update()

    # --- TELA DE CHAT ---
    def abrir_chat():
        page.clean()
        nome = page.client_storage.get("user_name")
        page.add(
            ft.Container(
                content=ft.Row([
                    ft.Text(f"Logado como: {nome}", color="white", weight="bold", expand=True),
                    ft.IconButton(icon=ft.icons.LOGOUT, icon_color="white", on_click=lambda _: fazer_logout())
                ]),
                bgcolor="#008069", padding=10
            ),
            chat,
            ft.Container(content=ft.Row([txt_msg, ft.ElevatedButton("Enviar", on_click=enviar)]), padding=10)
        )
        carregar_historico()

    def fazer_logout():
        page.client_storage.clear()
        page.window_destroy() # Ou apenas recarregar a página

    # --- LÓGICA DE CADASTRO ---
    def salvar_cadastro(e):
        if input_nome.value and input_email.value:
            # Salva no "disco rígido" do navegador/celular
            page.client_storage.set("user_name", input_nome.value)
            page.client_storage.set("user_email", input_email.value)
            abrir_chat()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha nome e email!"))
            page.snack_bar.open = True
            page.update()

    input_nome = ft.TextField(label="Nome", width=300)
    input_email = ft.TextField(label="E-mail", width=300)

    # VERIFICAÇÃO INICIAL: Já tem cadastro?
    if page.client_storage.contains_key("user_name"):
        abrir_chat()
    else:
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Cadastro Gamers", size=30, weight="bold"),
                    ft.Text("Entre uma vez para ficar salvo", size=14),
                    input_nome,
                    input_email,
                    ft.ElevatedButton("Finalizar Cadastro", on_click=salvar_cadastro)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=50, alignment=ft.alignment.center
            )
        )

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=porta, host="0.0.0.0")
