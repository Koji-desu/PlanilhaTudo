from extractor365 import extrair_texto_imagem
from getValues365 import pegar_valores_aposta
import appendRow

def main():
    caminho_imagem = 'Imagens/2.png'  # Substitua pelo caminho da sua imagem

    # Extrair texto da imagem
    texto_extraido = extrair_texto_imagem(caminho_imagem)
    print(texto_extraido)
    # Extrair valores monetários do texto
    valores_extraidos = pegar_valores_aposta(texto_extraido)
    print("Aposta: "+ valores_extraidos[0])
    print("Retorno obtido: "+ valores_extraidos[1])
    print("Odd: "+ valores_extraidos[2])

    if str(valores_extraidos[1]) == 'R$0,00':
        valores_extraidos[1] = 'Perda'
    else:
        valores_extraidos[1] = 'Ganho'

    valores_extraidos.append(valores_extraidos.pop(1))  # Move o retorno para o final da lista
    bot_repetido = ['BOT'] * 6

    valores_extraidos = bot_repetido + valores_extraidos
    appendRow.append_valores(appendRow.aba, 'J', valores_extraidos)

if __name__ == "__main__":
    main()