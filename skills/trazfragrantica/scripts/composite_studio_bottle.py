import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFilter

def make_transparent_bottle(real_path):
    img = Image.open(real_path).convert("RGBA")
    width, height = img.size
    arr = img.load()
    
    # 1. BFS Flood Fill para isolar o frasco
    visited = [[False for _ in range(width)] for _ in range(height)]
    queue = []
    
    # Inicializa bordas
    for x in range(width):
        for y in [0, height - 1]:
            if not visited[y][x]:
                visited[y][x] = True
                queue.append((x, y))
    for y in range(height):
        for x in [0, width - 1]:
            if not visited[y][x]:
                visited[y][x] = True
                queue.append((x, y))
                
    idx = 0
    while idx < len(queue):
        cx, cy = queue[idx]
        idx += 1
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                if not visited[ny][nx]:
                    r, g, b = arr[nx, ny][:3]
                    avg = (r + g + b) / 3.0
                    if avg > 175:
                        visited[ny][nx] = True
                        queue.append((nx, ny))
                        
    # Aplica transparência
    for y in range(height):
        for x in range(width):
            if visited[y][x]:
                arr[x, y] = (255, 255, 255, 0)
            else:
                r, g, b, a = arr[x, y]
                arr[x, y] = (r, g, b, 255)
                
    return img

def composite_on_empty_bg(bg_path, real_path, output_path, base_y=750, scale_height=560):
    if not os.path.exists(bg_path):
        print(f"Error: Background path {bg_path} does not exist.")
        return False
    if not os.path.exists(real_path):
        print(f"Error: Real path {real_path} does not exist.")
        return False

    img_bg = Image.open(bg_path).convert("RGBA")
    bg_w, bg_h = img_bg.size
    
    # 1. Obtém o frasco transparente
    transparent_bottle = make_transparent_bottle(real_path)
    real_w, real_h = transparent_bottle.size
    real_aspect = real_w / real_h
    
    # 2. Redimensiona o frasco preservando proporção
    target_h = scale_height
    target_w = int(target_h * real_aspect)
    resized_bottle = transparent_bottle.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # 3. Cria a camada de sombra de contato para o pedestal
    shadow_layer = Image.new("RGBA", img_bg.size, (0, 0, 0, 0))
    draw_shadow = ImageDraw.Draw(shadow_layer)
    
    cx = bg_w // 2
    shadow_w = int(target_w * 0.9)
    shadow_h = int(target_h * 0.04)
    
    x1 = cx - shadow_w // 2
    y1 = base_y - shadow_h // 2
    x2 = cx + shadow_w // 2
    y2 = base_y + shadow_h // 2
    
    draw_shadow.ellipse([x1, y1, x2, y2], fill=(0, 0, 0, 160))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(8))
    
    # 4. Combina as camadas
    img_bg.paste(shadow_layer, (0, 0), shadow_layer)
    
    paste_x = cx - target_w // 2
    paste_y = base_y - target_h
    img_bg.paste(resized_bottle, (paste_x, paste_y), resized_bottle)
    
    # Salva
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    final_img = img_bg.convert("RGB")
    final_img.save(output_path, "PNG")
    print(f"Composited successfully saved to {output_path}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Composição de estúdio: insere o frasco real transparente com sombra sobre o fundo vazio.")
    parser.add_argument("--bg", required=True, help="Caminho do fundo vazio gerado pela IA.")
    parser.add_argument("--real", required=True, help="Caminho da foto oficial do frasco.")
    parser.add_argument("--output", required=True, help="Caminho do arquivo de saída.")
    parser.add_argument("--base_y", type=int, default=750, help="Coordenada Y da base do pedestal.")
    parser.add_argument("--height", type=int, default=560, help="Altura do frasco na composição.")
    args = parser.parse_args()
    
    composite_on_empty_bg(args.bg, args.real, args.output, args.base_y, args.height)
