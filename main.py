import flet as ft
import random
import json
import os
import requests


BASE_DIR = os.path.dirname(__file__)
ARQUIVO_PALAVRAS = os.path.join(BASE_DIR, "palavras.txt")
ARQUIVO_RANKING = os.path.join(BASE_DIR, "ranking.json")


# -------------------- Funcoes secundarias --------------------


def carregar_palavras():
    if not os.path.exists(ARQUIVO_PALAVRAS):
        return ["rato", "marimbondo", "esquilo", "tubarao", "ricardo"]
    with open(ARQUIVO_PALAVRAS, "r", encoding="utf-8") as f:
        return [linha.strip().lower() for linha in f if linha.strip()]




def palavra_aleatoria_en():
    url = "https://random-word-api.herokuapp.com/word"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            palavra = data[0] if isinstance(data, list) else None
            if palavra and palavra.isalpha():
                return palavra.lower()
    except Exception as e:
        print(f"Erro ao buscar palavra em inglês: {e}")
    return None




def salvar_ranking(nome, palavra, erros, venceu):
    entrada = {
        "nome": nome,
        "palavra": palavra,
        "erros": erros,
        "resultado": "venceu" if venceu else "perdeu"
    }
    ranking = []
    if os.path.exists(ARQUIVO_RANKING):
        with open(ARQUIVO_RANKING, "r", encoding="utf-8") as f:
            try:
                ranking = json.load(f)
            except json.JSONDecodeError:
                ranking = []
    ranking.append(entrada)
    with open(ARQUIVO_RANKING, "w", encoding="utf-8") as f:
        json.dump(ranking, f, indent=2, ensure_ascii=False)


def carregar_ranking():
    if not os.path.exists(ARQUIVO_RANKING):
        return []
    with open(ARQUIVO_RANKING, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


# -------------------- Função principal --------------------


def main(page: ft.Page):
    page.title = "🎯 Jogo da Forca"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = "light"
    page.window_width = 600
    page.window_height = 700


    palavra = palavra_aleatoria_en()
    letras_certas = []
    letras_erradas = []
    tentativas = 6


    jogador_nome = ft.TextField(label="Digite seu nome", width=300)
    palavra_exibida = ft.Text("", size=30, weight="bold", color="blue")
    letras_erradas_texto = ft.Text("", color="red")
    tentativas_texto = ft.Text(f"Tentativas restantes: {tentativas}", color="orange")
    resultado = ft.Text("", size=20, weight="bold", color="green")
    ranking_lista = ft.Column(spacing=2)


    entrada_letra = ft.TextField(label="Tente uma letra", width=100, max_length=1)


    def atualizar_interface():
        exibicao = " ".join([letra if letra in letras_certas else "_" for letra in palavra])
        palavra_exibida.value = exibicao
        letras_erradas_texto.value = f"❌ Letras erradas: {', '.join(letras_erradas)}"
        tentativas_texto.value = f"Tentativas restantes: {tentativas}"
        entrada_letra.value = ""
        page.update()
        entrada_letra.focus()


    def verificar_letra(e):
        nonlocal tentativas
        letra = entrada_letra.value.lower().strip()


        if not letra.isalpha() or len(letra) != 1 or resultado.value:
            return


        if letra in letras_certas or letra in letras_erradas:
            resultado.value = "⚠️ Letra já tentada!"
            page.update()
            return


        if letra in palavra:
            letras_certas.append(letra)
        else:
            letras_erradas.append(letra)
            tentativas -= 1


        if all(l in letras_certas for l in palavra):
            resultado.value = f"🎉 Parabéns, {jogador_nome.value}! Você venceu!"
            salvar_ranking(jogador_nome.value, palavra, len(letras_erradas), True)
        elif tentativas == 0:
            resultado.value = f"💀 Você perdeu! A palavra era: {palavra}"
            salvar_ranking(jogador_nome.value, palavra, len(letras_erradas), False)


        atualizar_interface()


    entrada_letra.on_submit = verificar_letra


    def nova_partida(e):
        nonlocal palavra, letras_certas, letras_erradas, tentativas
        if not jogador_nome.value.strip():
            resultado.value = "⚠️ Digite seu nome antes de jogar!"
            page.update()
            return
        palavra = palavra_aleatoria_en()
        letras_certas = []
        letras_erradas = []
        tentativas = 6
        resultado.value = ""
        atualizar_interface()


    def mostrar_ranking(e):
        ranking = carregar_ranking()
        ranking.sort(key=lambda x: x["erros"])
        ranking_lista.controls.clear()
        for i, r in enumerate(ranking[:10]):
            ranking_lista.controls.append(
                ft.Text(f"{i+1}. {r['nome']} - {r['resultado']} - Palavra: {r['palavra']} - Erros: {r['erros']}")
            )
        page.update()


    def resetar_ranking(e):
        if os.path.exists(ARQUIVO_RANKING):
            os.remove(ARQUIVO_RANKING)
            ranking_lista.controls.clear()
            ranking_lista.controls.append(ft.Text("📉 Ranking resetado!"))
            page.update()


    page.add(
        ft.Column(
            [
                ft.Text("👨‍🏫 Jogo da Forca", size=40, weight="bold", color="purple"),
                jogador_nome,
                ft.Row(
                    [entrada_letra, ft.ElevatedButton("🎯 Tentar", on_click=verificar_letra)],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                palavra_exibida,
                letras_erradas_texto,
                tentativas_texto,
                resultado,
                ft.Divider(),
                ft.Row([
                    ft.ElevatedButton("🆕 Nova Palavra", on_click=nova_partida),
                    ft.ElevatedButton("📊 Mostrar Ranking", on_click=mostrar_ranking),
                    ft.ElevatedButton("🧹 Resetar Ranking", on_click=resetar_ranking),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Text("🏆 Ranking:", size=20, weight="bold"),
                ranking_lista
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            spacing=15,
        )
    )


    atualizar_interface()


if __name__ == "__main__":
    ft.app(target=main)



