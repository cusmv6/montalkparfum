import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont

def get_font(font_name, size):
    paths = [
        f"C:\\Windows\\Fonts\\{font_name}.ttf",
        f"C:\\Windows\\Fonts\\{font_name.lower()}.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf"
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def create_soft_mask(size, border=12):
    w, h = size
    mask = Image.new("L", size, 255)
    pixels = mask.load()
    for y in range(h):
        for x in range(w):
            dx = min(x, w - 1 - x)
            dy = min(y, h - 1 - y)
            d = min(dx, dy)
            if d < border:
                factor = d / border
                pixels[x, y] = int(255 * factor)
    return mask

def draw_tracked_text(draw, text, cx, y, font, fill, spacing):
    chars = list(text)
    char_widths = []
    for c in chars:
        w = draw.textlength(c, font=font)
        char_widths.append(w)
    total_w = sum(char_widths) + spacing * (len(chars) - 1)
    current_x = cx - total_w / 2
    for i, c in enumerate(chars):
        draw.text((current_x, y), c, fill=fill, font=font)
        current_x += char_widths[i] + spacing

def process_image(mockup_path, output_path):
    if not os.path.exists(mockup_path):
        print(f"Error: Mockup path {mockup_path} does not exist.")
        return False

    img = Image.open(mockup_path).convert("RGBA")
    width, height = img.size
    
    # 1. Detecta BBox no Mockup (procura o frasco matte black)
    # Usamos detecção híbrida:
    # - Todos os pixels escuros centrais determinam a altura (topo da tampa e base do frasco).
    # - Apenas pixels escuros e neutros (sem saturação) determinam a largura (excluindo folhas e flores).
    pixels = img.load()
    black_pixels_for_height = []
    black_pixels_for_width = []
    for y in range(100, height - 100):
        for x in range(200, width - 200):
            r, g, b = pixels[x, y][:3]
            if r < 40 and g < 40 and b < 40:
                # Altura: analisa a faixa horizontal central
                if 320 < x < 700:
                    black_pixels_for_height.append((x, y))
                
                # Largura: analisa a faixa horizontal central e aplica filtro cromático de saturação
                if abs(r - g) < 8 and abs(g - b) < 8 and abs(r - b) < 8:
                    if 350 < x < 674:
                        black_pixels_for_width.append((x, y))
                    
    if not black_pixels_for_height or not black_pixels_for_width:
        print(f"Error: Could not locate bottle in {mockup_path}.")
        return False
        
    ys = [p[1] for p in black_pixels_for_height]
    min_y, max_y = min(ys), max(ys)
    
    xs = [p[0] for p in black_pixels_for_width]
    min_x, max_x = min(xs), max(xs)
    
    w = max_x - min_x
    h = max_y - min_y
    cx = min_x + w // 2
    
    print(f"Retouching and drawing on {os.path.basename(mockup_path)}: BBox w={w}, h={h}, cx={cx}")
    
    # 2. Executa In-Painting por interpolação vertical coluna a coluna
    # O retângulo de retoque cobre a região de texto/typos na base (de 65% a 88% do frasco)
    y_start = min_y + int(h * 0.65)
    y_end = min_y + int(h * 0.88)
    target_h = y_end - y_start
    # Limita o patch a no máximo 140 pixels para proteger elementos decorativos laterais
    patch_w = min(int(w * 0.65), 140)
    
    crop_x1 = cx - patch_w // 2
    
    # Cria o patch retocável vazio
    retouch_patch = Image.new("RGBA", (patch_w, target_h))
    retouch_pixels = retouch_patch.load()
    orig_pixels = img.load()
    
    for x_p in range(patch_w):
        orig_x = crop_x1 + x_p
        orig_x = max(0, min(width - 1, orig_x))
        
        color_top = orig_pixels[orig_x, y_start]
        color_bottom = orig_pixels[orig_x, y_end]
        
        for y_p in range(target_h):
            t = y_p / float(target_h - 1) if target_h > 1 else 0.0
            
            # Interpolação linear dos canais de cor
            r = int(color_top[0] * (1.0 - t) + color_bottom[0] * t)
            g = int(color_top[1] * (1.0 - t) + color_bottom[1] * t)
            b = int(color_top[2] * (1.0 - t) + color_bottom[2] * t)
            
            if len(color_top) > 3 and len(color_bottom) > 3:
                a = int(color_top[3] * (1.0 - t) + color_bottom[3] * t)
                retouch_pixels[x_p, y_p] = (r, g, b, a)
            else:
                retouch_pixels[x_p, y_p] = (r, g, b, 255)
                
    # Cria a soft mask para mesclagem invisível
    soft_mask = create_soft_mask((patch_w, target_h), border=12)
    
    # Cola o patch com interpolação de pixels para apagar a escrita de baixo da garrafa
    img.paste(retouch_patch, (crop_x1, y_start), soft_mask)
    
    # 3. Desenha a tipografia oficial limpa e vetorizada (Segoe UI Regular fina)
    text_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    
    # Fontes
    font_small_size = max(7, int(h * 0.013))   # Tamanho do "DE PÈRE EN FILS..." (bem pequeno e fino)
    font_medium_size = max(8, int(h * 0.016))  # Tamanho do "100 ML..." (ligeiramente maior)
    
    font_small = get_font("segoeui", font_small_size)  # Segoe UI Regular
    font_medium = get_font("segoeui", font_medium_size)
    
    # Textos oficiais da Creed
    text_l1 = "DE PÈRE EN FILS DEPUIS 1760"
    text_l2 = "FROM FATHER TO SON SINCE 1760"
    text_l3 = "100 ML          3.33 FL. OZ."
    
    # Cor prata oficial da marca (com ligeira transparência para mesclar com o vidro)
    silver_color = (205, 208, 212, 230)
    
    # Posições verticais calibradas na parte inferior do frasco
    y_l1 = min_y + int(h * 0.72)
    y_l2 = min_y + int(h * 0.76)
    y_l3 = min_y + int(h * 0.83)
    
    # Desenha os textos com espaçamento elegante (tracking)
    draw_tracked_text(draw, text_l1, cx, y_l1, font_small, silver_color, spacing=2)
    draw_tracked_text(draw, text_l2, cx, y_l2, font_small, silver_color, spacing=2)
    draw_tracked_text(draw, text_l3, cx, y_l3, font_medium, silver_color, spacing=3)
    
    # 4. Combina as camadas
    final_img = Image.alpha_composite(img, text_layer).convert("RGB")
    
    # Garante a criação da pasta de destino e salva
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    final_img.save(output_path, "PNG")
    print(f"Successfully processed and saved to {output_path}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retoca o frasco da IA apagando textos com textura nativa e desenhando a tipografia oficial.")
    parser.add_argument("--mockup", required=True, help="Caminho do mockup de entrada.")
    parser.add_argument("--output", required=True, help="Caminho para salvar o resultado.")
    args = parser.parse_args()
    
    process_image(args.mockup, args.output)
