import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import argparse
from PIL import Image, ImageTk

# Globalna zmienna do trybu timera
TIME_MODE = False

# Import modules
try:
    from modules.avalanche import AvalancheModule
    from modules.encryption import EncryptionModule
    from modules.attack import AttackModule
    # Upewnij się, że masz plik modules/pdf_handler.py
    from modules.pdf_handler import open_documentation_file
except ImportError as e:
    print(f"Module import error: {e}")
    # Fallback dla testów
    def open_documentation_file(f): print(f"Opening {f} (mock)")

class TimerWidget(tk.Frame):
    """Widget wyświetlający odliczający czas 1:30 w prawym górnym rogu."""
    def __init__(self, parent, total_seconds=90):
        super().__init__(parent, bg='#2c2c2c')
        self.total_seconds = total_seconds
        self.remaining = total_seconds
        self.running = False
        
        self.time_label = tk.Label(
            self, 
            text=self.format_time(self.remaining),
            font=('Consolas', 12, 'bold'),
            fg='#00ff00',
            bg='#2c2c2c',
            padx=8,
            pady=4
        )
        self.time_label.pack()
        
    def format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}:{secs:02d}"
    
    def start(self):
        self.running = True
        self.remaining = self.total_seconds
        self.countdown()
        
    def stop(self):
        self.running = False
        
    def countdown(self):
        if not self.running:
            return
        if self.remaining > 0:
            self.time_label.config(text=self.format_time(self.remaining))
            # Zmiana koloru gdy mało czasu
            if self.remaining <= 30:
                self.time_label.config(fg='#ff6600')  # Pomarańczowy
            if self.remaining <= 10:
                self.time_label.config(fg='#ff0000')  # Czerwony
            self.remaining -= 1
            self.after(1000, self.countdown)
        else:
            self.time_label.config(text="0:00", fg='#ff0000')


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Projekt Kryptografia: Keccak Advanced")
        self.timer_widget = None  # Referencja do aktywnego timera
        self.launcher_remaining = 30  # Zapamiętany czas timera launchera
        try:
            self.root.state('zoomed')
        except:
            self.root.attributes('-fullscreen', True)
            
        self.current_frame = None
        
        # --- KONFIGURACJA STYLÓW ---
        self.style = ttk.Style()
        
        # Styl głównych przycisków
        self.style.configure('Launcher.TButton', font=('Helvetica', 16, 'bold'))
        
        # Styl przycisku dokumentacji (zwiększona czcionka i padding)
        self.style.configure('Doc.TButton', font=('Helvetica', 14, 'bold'), padding=15)
        
        # Konfiguracja modułów
        self.modules_config = {
            "avalanche": {
                "slides": [
                    {
                        "image": "efekt1.png",
                        "title": "EFEKT LAWINOWY",
                        "text": "Mała zmiana, wielki chaos."
                    },
                    {
                        "image": "efekt2.png",
                        "title": "TEORIA I DZIAŁANIE",
                        "text": "Efekt lawinowy: zmiana 1 bitu wejścia zmienia ~50% bitów wyjścia.\n\nAplikacja wizualizuje propagację różnic w stanie Keccak runda po rundzie."
                    }
                ],
                "module_class": AvalancheModule if 'AvalancheModule' in globals() else None,
                "title": "Efekt Lawinowy"
            },
            "encryption": {
                "slides": [
                    {
                        "image": "szyfr1.png",
                        "title": "SZYFROWANIE OBRAZÓW",
                        "text": "Ukryj treść w szumie doskonałym."
                    },
                    {
                        "image": "szyfr2.png",
                        "title": "JAK TO DZIAŁA?",
                        "text": "Wykorzystujemy strumień SHAKE128 do XOR-owania pikseli.\n\nZobaczysz proces szyfrowania na żywo i wpływ klucza na wynik."
                    }
                ], 
                "module_class": EncryptionModule if 'EncryptionModule' in globals() else None, 
                "title": "Szyfrowanie Obrazów"
            },
            "attack": {
                "slides": [
                    {
                        "image": "atak1.png",
                        "title": "ANALIZA BEZPIECZEŃSTWA",
                        "text": "Czy Keccak jest niezniszczalny?"
                    },
                    {
                        "image": "atak2.png",
                        "title": "SZUKANIE KOLIZJI",
                        "text": "Prezentacja ataku urodzinowego na wersję o zredukowanej liczbie rund.\n\nSprawdzamy, jak szybko można znaleźć dwa różne wejścia dające ten sam skrót."
                    }
                ], 
                "module_class": AttackModule if 'AttackModule' in globals() else None, 
                "title": "Atak na Keccaka"
            }
        }
        
        self.show_launcher()
        
        self.root.bind('<space>', self.handle_space)
        self.slideshow_active = False
        self.current_slides = []
        self.current_slide_index = 0
        self.target_module_key = None

    def show_launcher(self):
        # Zatrzymaj i usuń timer jeśli istnieje
        if self.timer_widget:
            self.timer_widget.stop()
            self.timer_widget.destroy()
            self.timer_widget = None
            
        if self.current_frame:
            self.current_frame.destroy()
            
        self.slideshow_active = False
        self.root.unbind('<space>')
        self.root.unbind('<Shift-Return>')
        
        self.current_frame = ttk.Frame(self.root)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. Nagłówek - ZMIENIONO TEKST
        lbl = ttk.Label(self.current_frame, text="Analiza keccak-f", font=('Helvetica', 36, 'bold'))
        lbl.pack(pady=(80, 40))
        
        # 2. Kontener na przyciski modułów
        modules_frame = ttk.Frame(self.current_frame)
        modules_frame.pack(expand=True, fill=tk.X, padx=50)
        
        main_opts = [
            ("Efekt Lawinowy", "avalanche"),
            ("Szyfrowanie Obrazów", "encryption"),
            ("Atak (Kolizje)", "attack")
        ]
        
        # uniform="group_name" wymusza identyczną szerokość dla wszystkich kolumn w tej grupie
        for i in range(len(main_opts)):
            modules_frame.columnconfigure(i, weight=1, uniform="equal_buttons")
        
        modules_frame.rowconfigure(0, weight=1) 

        for i, (text, key) in enumerate(main_opts):
            cmd = lambda k=key: self.start_slideshow(k)
            btn = ttk.Button(modules_frame, text=text, command=cmd, style='Launcher.TButton')
            
            btn.grid(row=0, column=i, padx=15, pady=20, ipadx=40, ipady=100, sticky="nsew")

        # 3. Przycisk Dokumentacji (Prawy Dolny Róg)
        doc_btn = ttk.Button(self.current_frame, text="Dokumentacja PDF", 
                             command=self.launch_documentation, style='Doc.TButton')
        
        doc_btn.place(relx=0.97, rely=0.97, anchor='se')
        
        # Timer na stronie głównej w trybie --time (kontynuuje od zapamiętanego czasu)
        if TIME_MODE:
            self.timer_widget = TimerWidget(self.root, total_seconds=self.launcher_remaining)
            self.timer_widget.remaining = self.launcher_remaining  # Ustaw pozostały czas
            self.timer_widget.place(relx=0.99, rely=0.01, anchor='ne')
            self.timer_widget.start()

    def launch_documentation(self):
        try:
            open_documentation_file("Dokumentacja.pdf")
        except Exception as e:
            messagebox.showerror("Błąd dokumentacji", str(e))

    def start_slideshow(self, key):
        self.target_module_key = key
        config = self.modules_config[key]
        self.current_slides = config["slides"]
        self.current_slide_index = 0
        self.slideshow_active = True
        
        self.root.bind('<space>', self.handle_space)
        
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self.root, bg="black")
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
        # Timer w trybie --time - startuje od razu przy slideshow (1:20)
        if TIME_MODE:
            # Zapisz pozostały czas launchera przed zniszczeniem
            if self.timer_widget:
                self.launcher_remaining = self.timer_widget.remaining
                self.timer_widget.stop()
                self.timer_widget.destroy()
            self.timer_widget = TimerWidget(self.root, total_seconds=90)
            self.timer_widget.place(relx=0.99, rely=0.01, anchor='ne')
            self.timer_widget.start()
        
        self.display_current_slide()

    def display_current_slide(self):
        for widget in self.current_frame.winfo_children():
            widget.destroy()
            
        slide_data = self.current_slides[self.current_slide_index]
        if isinstance(slide_data, str):
            slide_name = slide_data
            title_text = None
            body_text = None
        else:
            slide_name = slide_data["image"]
            title_text = slide_data.get("title")
            body_text = slide_data.get("text")
            
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        path = os.path.join(base_path, "assets", slide_name)
        
        if not os.path.exists(path):
            lbl = tk.Label(self.current_frame, text=f"SLAJD: {slide_name}\n(Naciśnij SPACJĘ)", 
                           fg="white", bg="black", font=('Arial', 32))
            lbl.pack(expand=True)
            return
            
        try:
            img = Image.open(path)
            self.root.update_idletasks()
            win_w = self.current_frame.winfo_width()
            win_h = self.current_frame.winfo_height()
            
            img = img.resize((win_w, win_h), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            canvas = tk.Canvas(self.current_frame, width=win_w, height=win_h, highlightthickness=0, bg="black")
            canvas.pack(fill=tk.BOTH, expand=True)
            
            canvas.create_image(win_w//2, win_h//2, image=photo, anchor=tk.CENTER)
            canvas.image = photo
            
            if title_text:
                canvas.create_text(win_w//2, win_h * 0.2, text=title_text, 
                                   font=('Helvetica', 40, 'bold'), fill="white", justify=tk.CENTER)
            if body_text:
                canvas.create_text(win_w//2, win_h * 0.8, text=body_text, 
                                   font=('Helvetica', 24), fill="white", justify=tk.CENTER)
                                   
        except Exception as e:
            lbl = tk.Label(self.current_frame, text=f"Błąd ładowania: {slide_name}\n{e}", fg="red")
            lbl.pack(expand=True)

    def handle_space(self, event):
        if not self.slideshow_active:
            return
            
        if self.current_slide_index < len(self.current_slides) - 1:
            self.current_slide_index += 1
            self.display_current_slide()
        else:
            self.launch_module(self.target_module_key)

    def launch_module(self, key):
        self.slideshow_active = False
        self.root.unbind('<space>')
        
        if self.current_frame:
            self.current_frame.destroy()
            
        config = self.modules_config[key]
        module_class = config["module_class"]
        
        self.current_frame = ttk.Frame(self.root)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
        self.root.bind('<Shift-Return>', lambda e: self.show_launcher())
        
        # Upewnij się że timer jest na wierzchu
        if self.timer_widget:
            self.timer_widget.lift()
        
        if module_class:
            app = module_class(self.current_frame)
            app.pack(fill=tk.BOTH, expand=True)
        else:
            ttk.Label(self.current_frame, text=f"Moduł '{config['title']}' w budowie...", font=('Arial', 20)).pack(pady=50)

if __name__ == "__main__":
    # Parsowanie argumentów
    parser = argparse.ArgumentParser(description='Projekt Kryptografia: Keccak Advanced')
    parser.add_argument('--time', action='store_true', help='Włącz tryb odliczania czasu (1:30 na moduł)')
    args = parser.parse_args()
    
    TIME_MODE = args.time
    
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    root = tk.Tk()
    root.minsize(800, 600)
    app = MainApp(root)
    root.mainloop()