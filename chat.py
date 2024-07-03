import os
import flet as ft
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Kustomisasi pertanyaan pertama dan peran
question = ''
role = 'Anda adalah seorang guru profesional Python.'

isAsking = False

# Kunci API Google Gemini
api_key = os.getenv('GEMINI_API_KEY')

genai.configure(
    api_key=api_key
)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

def filter_islam_nabi(response_text):
    # Fungsi untuk memfilter data hanya untuk topik Islam dan Nabi
    lines = response_text.split('\n')
    islam_nabi_responses = [line for line in lines if 'Islam' in line or 'Nabi' in line]
    if not islam_nabi_responses:
        return "Maaf, saya tidak memiliki informasi tentang topik ini."
    return '\n'.join(islam_nabi_responses)

def main(page: ft.Page):
    messages = []
    tf = ft.TextField(value=question, expand=True, 
                      autofocus=True, shift_enter=True,
                      bgcolor=ft.colors.GREY_700, icon=ft.icons.WECHAT_OUTLINED)
    lf = ft.ListView(controls=messages, auto_scroll=False, expand=True, reverse=True)
    btt = ft.IconButton(icon=ft.icons.SEND_OUTLINED)

    def getMD(mdtxt):
        return ft.Markdown(
            mdtxt,
            selectable=True,
            code_theme="atom-one-dark",
            code_style=ft.TextStyle(font_family="Roboto Mono"),
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=lambda e: page.launch_url(e.data),
        )

    def ask(e):
        global isAsking
        if isAsking:
            return
        
        question = tf.value.strip()  # Menghilangkan spasi ekstra di sekitar teks
        if not question:  # Memastikan tidak mengirim pesan jika pertanyaan kosong
            return
        
        isAsking = True
        btt.disabled = True
        responseText = ''

        tf.value = ''  # Mengosongkan nilai TextField setelah mengirim pertanyaan
        mdQuestion = getMD(question)

        messages.insert(0, ft.Card(
            content=ft.Container(padding=5, content=mdQuestion), 
            color=ft.colors.BLUE_400, margin=ft.Margin(left=10, right=0, top=5, bottom=5)))
        
        try: 
            if "islam" in question.lower() or "nabi" in question.lower():
                response_text = chat.send_message(question).text
                responseText = filter_islam_nabi(response_text)
            else:
                responseText = "Maaf, saya hanya memberikan informasi tentang Islam dan Nabi."
            
            mdTxt = getMD(response_text)
            messages.insert(0, ft.Card(
                content=ft.Container(padding=5, content=mdTxt),
                color=ft.colors.GREY_700, margin=ft.Margin(left=0, right=10, top=5, bottom=5)))
            
            lf.scroll_to(0.0, duration=500)
            page.update()

        except Exception as e:
            mdTxt = getMD(str(e))
            messages.insert(0, ft.Card(
                content=ft.Container(padding=5, content=mdTxt),
                color=ft.colors.GREY_700, margin=ft.Margin(left=0, right=10, top=5, bottom=5)))
            page.update()
        
        btt.disabled = False
        page.update()
        isAsking = False

    btt.on_click = ask
    tf.on_submit = ask
    container = ft.Container(
        expand=True,
        content=ft.Column(
            controls=[
                lf,
                ft.Row(
                    controls=[
                        tf,
                        btt
                    ]
                )
            ]
        )
    )

    page.add(container)

ft.app(main)
