import sys
import os
import subprocess

def open_documentation_file(filename="Dokumentacja.pdf"):
    """
    Ustala ścieżkę do pliku PDF i otwiera go w domyślnej przeglądarce systemowej.
    Zwraca True, jeśli się uda, lub podnosi wyjątek w przypadku błędu.
    """
    
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(current_dir)
        
    pdf_path = os.path.join(base_path, filename)
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Nie znaleziono pliku w ścieżce:\n{pdf_path}")

    if sys.platform == 'win32':
        os.startfile(pdf_path)
    elif sys.platform == 'darwin': # macOS
        subprocess.call(['open', pdf_path])
    else: # Linux
        subprocess.call(['xdg-open', pdf_path])