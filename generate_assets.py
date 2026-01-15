from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs('assets', exist_ok=True)

def create_slide(filename, text, color):
    img = Image.new('RGB', (1280, 720), color=color)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    # Text positioning (rough center)
    d.text((100, 300), text, fill="white", font=font)
    d.text((100, 500), "(Nacisnij SPACJE)", fill="white", font=font)
    
    img.save(os.path.join('assets', filename))

slides = [
    ("efekt1.png", "Efekt Lawinowy - Slajd 1\nZmiana 1 bitu wejscia...", "darkred"),
    ("efekt2.png", "Efekt Lawinowy - Slajd 2\n...zmienia 50% bitow wyjscia!", "red"),
    
    ("szyfr1.png", "Szyfrowanie Obrazow - Slajd 1\nKeccak jako strumien...", "darkblue"),
    ("szyfr2.png", "Szyfrowanie Obrazow - Slajd 2\nPelna dyfuzja vs malo rund", "blue"),
    
    ("viz1.png", "Wizualizacja - Slajd 1\nStan wewnetrzny 5x5", "darkgreen"),
    ("viz2.png", "Wizualizacja - Slajd 2\nOperacje Theta, Rho, Pi...", "green"),
    
    ("atak1.png", "Atak - Slajd 1\nSzukanie kolizji...", "black"),
    ("atak2.png", "Atak - Slajd 2\nBrute force na malych rundach", "gray"),
]

for name, txt, col in slides:
    create_slide(name, txt, col)
    
print("Assets created.")
