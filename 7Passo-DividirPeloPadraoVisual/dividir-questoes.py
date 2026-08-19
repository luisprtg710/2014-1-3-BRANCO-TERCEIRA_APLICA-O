from PIL import Image
import os

def cor_combina(pixel_rgb, cor_alvo, tolerancia=15):
    """Auxiliar para verificar se um pixel está dentro da tolerância de cor."""
    return (abs(pixel_rgb[0] - cor_alvo[0]) <= tolerancia and
            abs(pixel_rgb[1] - cor_alvo[1]) <= tolerancia and
            abs(pixel_rgb[2] - cor_alvo[2]) <= tolerancia)

def medir_faixa(imagem, x, y_inicio, cor_alvo, tolerancia=15):
    """Conta quantos pixels consecutivos a partir de y_inicio têm a cor alvo."""
    _, altura = imagem.size
    pixels = imagem.load()
    y = y_inicio
    count = 0
    
    while y < altura:
        pixel = pixels[x, y]
        p_rgb = pixel[:3] if len(pixel) >= 3 else (pixel[0], pixel[0], pixel[0])
        
        if cor_combina(p_rgb, cor_alvo, tolerancia):
            count += 1
            y += 1
        else:
            break
            
    return count

def encontrar_faixas_padrao(imagem, tolerancia=15):
    """
    Procura no último pixel da direita (largura - 1) pelo padrão vertical:
    - Faixa 1: ~10px RGB(35,31,32)
    - Faixa 2: ~4px RGB(255,255,255)
    - Faixa 3: ~5px RGB(35,31,32)
    - Faixa 4: ~4px RGB(255,255,255)
    - Faixa 5: ~9px RGB(35,31,32)
    Margem de erro: +/- 3px por faixa.
    """
    largura, altura = imagem.size
    x = largura - 1  # Último pixel da direita
    
    cor_escura = (35, 31, 32)
    cor_branca = (255, 255, 255)
    
    posicoes_corte = []
    y = 0
    
    while y < altura:
        # 1. Mede primeira faixa escura (alvo: 10px, min: 7, max: 13)
        h1 = medir_faixa(imagem, x, y, cor_escura, tolerancia)
        if 7 <= h1 <= 13:
            y2 = y + h1
            # 2. Mede faixa branca (alvo: 4px, min: 1, max: 7)
            h2 = medir_faixa(imagem, x, y2, cor_branca, tolerancia)
            if 1 <= h2 <= 7:
                y3 = y2 + h2
                # 3. Mede faixa escura (alvo: 5px, min: 2, max: 8)
                h3 = medir_faixa(imagem, x, y3, cor_escura, tolerancia)
                if 2 <= h3 <= 8:
                    y4 = y3 + h3
                    # 4. Mede faixa branca (alvo: 4px, min: 1, max: 7)
                    h4 = medir_faixa(imagem, x, y4, cor_branca, tolerancia)
                    if 1 <= h4 <= 7:
                        y5 = y4 + h4
                        # 5. Mede faixa escura final (alvo: 9px, min: 6, max: 12)
                        h5 = medir_faixa(imagem, x, y5, cor_escura, tolerancia)
                        if 6 <= h5 <= 12:
                            # Padrão completo encontrado!
                            posicao_corte = max(0, y - 10) # 10px acima do padrão
                            posicoes_corte.append((posicao_corte, y))
                            print(f"Padrão encontrado em y={y}, cortando em y={posicao_corte}")
                            
                            # Avança para além de todo o padrão encontrado
                            y = y5 + h5
                            continue
        y += 1
        
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    resultados = encontrar_faixas_padrao(imagem)
    
    if not resultados:
        print("Nenhum padrão visual encontrado na imagem!")
        return
        
    print(f"Encontradas {len(resultados)} ocorrências do padrão para corte")
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, (posicao_corte, inicio_padrao) in enumerate(resultados):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
        
    # Salva a última parte se houver resíduo
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(resultados)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "./inteiras/pagina_enem_29.png"  # Atualize para o nome do seu arquivo
    pasta_saida = "pg29"                        # Atualize para o nome da pasta desejada

    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    print("Divisão concluída!")