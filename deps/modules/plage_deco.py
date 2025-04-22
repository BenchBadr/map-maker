from PIL import Image, ImageDraw


def is_non_white(x:int, y:int) -> bool:
    '''
    Teste si le pixel (x, y) est non blanc.
    '''
    return pixels[x, y] < 240

def parcours_image(x:int, y:int, width:int, height:int, visited:list) -> tuple:
    '''
    Parcours en profondeur pour marquer les pixels non blancs.
    Returns:
        tuple: (min_x, min_y, max_x, max_y) 
        les coins du rectangle blanc trouvé en partant de (x, y)
    '''

    s = [(x, y)]

    # On enregistre les coins pour construire les rectangles
    min_x, min_y, max_x, max_y = x, y, x, y

    while s:
        cx, cy = s.pop()

        if visited[cx][cy]:
            continue

        if not is_non_white(cx, cy):
            continue

        visited[cx][cy] = True

        # On met a jour les coins
        min_x, min_y = min(min_x, cx), min(min_y, cy)
        max_x, max_y = max(max_x, cx), max(max_y, cy)

        for nx, ny in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]:
            
            if not (0 <= nx < width and 0 <= ny < height):
                continue

            if not visited[nx][ny] and is_non_white(nx, ny):
                s.append((nx, ny))

    return (min_x, min_y, max_x, max_y)


image_path = "deps/assets/tuiles/SHRH.png"
image = Image.open(image_path).convert("L")

image_copy = image.copy()
draw = ImageDraw.Draw(image_copy)

# Trouver les zones non blanches
pixels = image.load()
width, height = image.size
visited = [[False] * height for _ in range(width)]


for x in range(width):
    for y in range(height):
        if not visited[x][y] and is_non_white(x, y):
            min_x, min_y, max_x, max_y = parcours_image(x, y, width, height, visited)
            print(min_x, min_y, max_x, max_y)
            # Dessine le rectangle rouge autour de la zone blanche trouvée
            draw.rectangle([min_x, min_y, max_x, max_y], fill="red", width=0)

image_copy.show()