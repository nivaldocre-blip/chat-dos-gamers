import flet as ft
import os
import sqlite3
from datetime import datetime

# --- MOTOR DE BANCO DE DADOS (PERSISTÊNCIA TOTAL) ---
def init_db():
    conn = sqlite3.connect("chat.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS mensagens 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, autor TEXT, texto TEXT, hora TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                      (email TEXT PRIMARY KEY, nome TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

def main(page: ft.Page):
    # Configurações de Janela Estilo App Profissional
    page.title = "Gamers Messenger"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#E5DDD5"  # Fundo clássico do Zap
    page.window_width = 400
    page.window_height = 700
    page.padding = 0  # Remover padding para o cabeçalho colar no topo

    sessao = {"nome": "", "email": ""}
    
    # --- INTERFACE DE CHAT ---
    chat_container = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.ALWAYS,
        spacing=10,
        auto_scroll=True # Rola sozinho para baixo!
    )

    def criar_balao(texto, autor, hora=None):
        sou_eu = (autor == sessao["nome"])
        if not hora:
            hora = datetime.now().strftime("%H:%M")
            
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text(autor, size=12, color="#25D366" if not sou_eu else "#d9fdd3", weight="bold"),
                        ft.Text(texto, color="black" if not sou_eu else "black", size=16),
                        ft.Text(hora, size=9, color="gray", text_align=ft.TextAlign.RIGHT),
                    ], spacing=2, tight=True),
                    padding=ft.padding.only(left=12, right=12, top=8, bottom=8),
                    bgcolor="#FFFFFF" if not sou_eu else "#DCF8C6",
                    border_radius=ft.border_radius.only(
                        top_left=15, top_right=15, 
                        bottom_right=5 if sou_eu else 15, 
                        bottom_left=15 if sou_eu else 5
                    ),
                    shadow=ft.BoxShadow(blur_radius=1, color="black12"),
                    max_width=300,
                )
            ],
            alignment=ft.MainAxisAlignment.END if sou_eu else ft.MainAxisAlignment.START
        )

    def carregar_historico():
        chat_container.controls.clear()
        cursor = db_conn.cursor()
        cursor.execute("SELECT autor, texto, hora FROM mensagens ORDER BY id ASC")
        for row in cursor.fetchall():
            chat_container.controls.append(criar_balao(row[1], row[0], row[2]))
        page.update()

    def on_message(msg):
        chat_container.controls.append(criar_balao(msg['texto'], msg['autor'], msg['hora']))
        page.update()

    page.pubsub.subscribe(on_message)

    def enviar_msg(e):
        if campo_msg.value.strip() != "":
            hora_atual = datetime.now().strftime("%H:%M")
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO mensagens (autor, texto, hora) VALUES (?, ?, ?)", 
                           (sessao["nome"], campo_msg.value, hora_atual))
            db_conn.commit()
            
            page.pubsub.send_all({"autor": sessao["nome"], "texto": campo_msg.value, "hora": hora_atual})
            campo_msg.value = ""
            campo_msg.focus()
            page.update()

    # --- COMPONENTES DE INTERFACE ---
    campo_msg = ft.TextField(
        hint_text="Digite uma mensagem",
        expand=True,
        border_radius=30,
        bgcolor=ft.colors.WHITE,
        content_padding=15,
        border_color=ft.colors.TRANSPARENT,
        on_submit=enviar_msg
    )

    btn_enviar = ft.IconButton(
        icon=ft.icons.SEND_ROUNDED,
        icon_color="#075E54",
        icon_size=30,
        on_click=enviar_msg
    )

    # --- TELAS ---
    def abrir_chat():
        page.clean()
        
        # Header Estilo Whatsapp
        header = ft.Container(
            content=ft.Row([
                ft.CircleAvatar(content=ft.Icon(ft.icons.PERSON), bgcolor="#128C7E"),
                ft.Column([
                    ft.Text(sessao["nome"], color="white", weight="bold", size=16),
                    ft.Text("Online", color="#d9fdd3", size=12),
                ], spacing=0, expand=True),
                ft.IconButton(ft.icons.LOGOUT, icon_color="white", on_click=lambda _: desenhar_cadastro())
            ]),
            bgcolor="#075E54",
            padding=ft.padding.only(left=15, top=35, right=10, bottom=10),
        )

        input_area = ft.Container(
            content=ft.Row([campo_msg, btn_enviar], spacing=5),
            padding=10,
            bgcolor="#F0F2F5"
        )

        page.add(
            header,
            ft.Container(content=chat_container, expand=True, padding=10),
            input_area
        )
        carregar_historico()

    # Inputs globais para persistência
    input_nome = ft.TextField(label="Seu Nome", border_radius=10, prefix_icon=ft.icons.PERSON)
    input_email = ft.TextField(label="Seu E-mail", border_radius=10, prefix_icon=ft.icons.EMAIL)

    def finalizar_cadastro(e):
        if input_nome.value and input_email.value:
            sessao["nome"] = input_nome.value
            sessao["email"] = input_email.value.lower()
            
            # Gravação em dois níveis: Local e Servidor
            try:
                page.client_storage.set("chat_nome", sessao["nome"])
                page.client_storage.set("chat_email", sessao["email"])
            except: pass
            
            cursor = db_conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO usuarios (email, nome) VALUES (?, ?)", 
                           (sessao["email"], sessao["nome"]))
            db_conn.commit()
            abrir_chat()

    def desenhar_cadastro():
        page.clean()
        # Tenta recuperar dados de qualquer fonte disponível
        try:
            n = page.client_storage.get("chat_nome")
            e = page.client_storage.get("chat_email")
            if n: input_nome.value = n
            if e: input_email.value = e
        except: pass

        page.add(
            ft.Container(
                expand=True,
                gradient=ft.LinearGradient(begin=ft.alignment.top_center, end=ft.alignment.bottom_center, colors=["#075E54", "#128C7E"]),
                content=ft.Column([
                    ft.Icon(ft.icons.CHAT_ROUNDED, size=80, color="white"),
                    ft.Text("Gamers Messenger", color="white", size=28, weight="bold"),
                    ft.Text("Conecte-se com o mundo", color="#d9fdd3"),
                    ft.Container(height=20),
                    ft.Container(
                        content=ft.Column([
                            input_email,
                            input_nome,
                            ft.ElevatedButton(
                                "ENTRAR", 
                                color="white", 
                                bgcolor="#25D366", 
                                width=300, 
                                height=50,
                                on_click=finalizar_cadastro
                            ),
                        ], spacing=15),
                        bgcolor="white",
                        padding=30,
                        border_radius=20,
                        shadow=ft.BoxShadow(blur_radius=10, color="black26")
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER)
            )
        )

    desenhar_cadastro()

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=porta, host="0.0.0.0")
