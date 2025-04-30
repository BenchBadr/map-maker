from PIL import Image, ImageDraw


def is_non_white(pixels:list, x:int, y:int) -> bool:
    '''
    Teste si le pixel (x, y) est non blanc.
    '''
    return pixels[x, y] < 240

def parcours_image(pixels:list, x:int, y:int, width:int, height:int, visited:list) -> tuple:
    '''
    Parcours en profondeur pour marquer les pixels non blancs.
    Returns:
        tuple: (min_x, min_y, max_x, max_y) 
        les coins du rectangle blanc trouvé en partant de (x, y)
    '''

    s = [(x, y)]
    step = 0

    # On enregistre les coins pour construire les rectangles
    min_x, min_y, max_x, max_y = x, y, x, y

    while s and step < 1000:
        cx, cy = s.pop()

        if visited[cx][cy]:
            continue

        if not is_non_white(pixels, cx, cy):
            continue

        visited[cx][cy] = True

        # On met a jour les coins
        min_x, min_y = min(min_x, cx), min(min_y, cy)
        max_x, max_y = max(max_x, cx), max(max_y, cy)

        for nx, ny in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]:
            
            if not (0 <= nx < width and 0 <= ny < height):
                continue

            if not visited[nx][ny] and is_non_white(pixels, nx, ny):
                s.append((nx, ny))
            
        step += 1


    return (min_x, min_y, max_x, max_y)


def analyse_tuile(tuile, debug=False):
    image_path = f"deps/assets/tuiles/{tuile}.png"
    image = Image.open(image_path).convert("L")

    image_copy = image.copy()

    # Trouver les zones non blanches
    pixels = image.load()
    width, height = image.size
    visited = [[False] * height for _ in range(width)]


    bbox = []
    # biomes = [c for c in tuile if c in ['P','S']]
    # idx = 0
    if debug:
        overlay = Image.new("RGBA", image_copy.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
    for x in range(width):
        for y in range(height):
            if not visited[x][y] and is_non_white(pixels, x, y):
                min_x, min_y, max_x, max_y = parcours_image(pixels, x, y, width, height, visited)
                if debug:
                    draw.rectangle([min_x, min_y, max_x, max_y], fill=(255, 0,0, 32), outline='#3c3c3c', width=1)
                bbox.append([min_x / 100, min_y / 100, max_x / 100, max_y / 100])


    if not debug:
        image.close()
        image_copy.close()
        return bbox
    else:
        image_copy = image_copy.convert("RGBA")
        return bbox, Image.alpha_composite(image_copy, overlay)


if __name__ == '__main__':
    bbox, img = analyse_tuile('PMMP', debug=True)
    print(bbox)
    img.show()