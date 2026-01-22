import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import sys

# Upewniamy się, że importujemy Twój moduł keccak
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from keccak import KeccakSponge
except ImportError:
    print("Błąd: Nie znaleziono pliku keccak.py lub operations.py")

class EncryptionModule(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.parent = parent
        
        self.original_image_pil = None
        self.password_locked = False 
        
        # --- USTAWIENIA WIZUALIZACJI ---
        self.process_size = (100, 100) 
        self.display_size = (500, 500)
        # -------------------------------

        self.setup_ui()
        self.setup_bindings()
        
        self.after(100, self.generate_perfect_checkerboard)
        self.focus_set()

    def setup_ui(self):
        # Główny kontener
        control = ttk.Frame(self)
        control.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # --- GÓRNY PASEK: HASŁO I SUWAK ---
        top_bar = ttk.Frame(control)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        # 1. Hasło (Lewa)
        pass_frame = ttk.Frame(top_bar)
        pass_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(pass_frame, text="Klucz:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        self.pass_entry = ttk.Entry(pass_frame, width=12)
        self.pass_entry.pack(side=tk.LEFT, padx=5)
        self.pass_entry.bind("<Return>", lambda e: self.lock_password())
        self.pass_entry.bind("<KeyRelease>", lambda e: self.process_image() if not self.password_locked else None)
        
        self.lock_btn = ttk.Button(pass_frame, text="OK", width=4, command=self.lock_password)
        self.lock_btn.pack(side=tk.LEFT)

        # 2. Suwak (Prawa)
        slider_frame = ttk.Frame(top_bar)
        slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.step_var = tk.DoubleVar(value=0)
        self.scale = ttk.Scale(slider_frame, from_=0, to=15, variable=self.step_var, orient=tk.HORIZONTAL)
        self.scale.pack(side=tk.TOP, fill=tk.X, pady=2)
        self.scale.bind("<ButtonRelease-1>", self.on_slider_release)
        self.scale.configure(command=self.on_scale_change)

        # --- DOLNY PASEK: OPIS ETAPU ---
        # Tutaj dajemy dużo miejsca na tekst
        self.desc_frame = ttk.LabelFrame(control, text="Analiza Operacji")
        self.desc_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
        
        self.info_label = ttk.Label(
            self.desc_frame, 
            text="Wybierz etap...", 
            font=("Segoe UI", 10), 
            wraplength=780, # Zwijanie tekstu
            justify="left"
        )
        self.info_label.pack(fill=tk.X, padx=5, pady=5)

        # --- OBSZAR ROBOCZY ---
        content = ttk.Frame(self)
        content.pack(fill=tk.BOTH, expand=True, padx=5, pady=0)
        
        self.left_panel = ttk.LabelFrame(content, text="Wejście")
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.lbl_orig = ttk.Label(self.left_panel)
        self.lbl_orig.pack(expand=True)
        
        self.right_panel = ttk.LabelFrame(content, text="Stan Wewnętrzny")
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.lbl_enc = ttk.Label(self.right_panel, text="...")
        self.lbl_enc.pack(expand=True)

    def setup_bindings(self):
        self.winfo_toplevel().bind_all('<Left>', self.move_left)
        self.winfo_toplevel().bind_all('<Right>', self.move_right)
        self.bind('<Button-1>', lambda e: self.focus_set())

    def lock_password(self):
        if self.pass_entry.get():
            self.password_locked = True
            self.pass_entry.config(state='disabled')
            self.lock_btn.config(state='disabled')
            self.process_image()
            self.focus_set()

    def move_left(self, event):
        if self.focus_get() == self.pass_entry and not self.password_locked: return
        if self.focus_get() == self.scale: return
        val = self.step_var.get()
        if val > 0:
            self.step_var.set(val - 1)
            self.update_label_text_only(val - 1)
            self.process_image()

    def move_right(self, event):
        if self.focus_get() == self.pass_entry and not self.password_locked: return
        if self.focus_get() == self.scale: return
        val = self.step_var.get()
        if val < 15:
            self.step_var.set(val + 1)
            self.update_label_text_only(val + 1)
            self.process_image()

    def on_scale_change(self, val):
        self.update_label_text_only(val)
        if float(val).is_integer():
             self.process_image()

    def generate_perfect_checkerboard(self):
        img = Image.new("L", self.process_size, color=0)
        pixels = img.load()
        square_w = 5 
        for y in range(self.process_size[1]):
            for x in range(self.process_size[0]):
                if ((x // square_w) + (y // square_w)) % 2 == 1:
                    pixels[x, y] = 255
                else:
                    pixels[x, y] = 0
        self.load_image_object(img)

    def load_image_object(self, img_pil):
        self.processing_source = img_pil
        disp = self.processing_source.resize(self.display_size, Image.Resampling.NEAREST)
        self.photo_orig = ImageTk.PhotoImage(disp)
        self.lbl_orig.config(image=self.photo_orig)
        self.step_var.set(0)
        self.update_label_text_only(0)
        self.process_image()

    def get_detailed_description(self, steps):
        if steps == 0: 
            return "STAN 0: START (INICJALIZACJA)\nTo jest Twój stan początkowy (macierz 5x5). Każdy duży kwadrat to 1 bajt (8 bitów) danych. Jeśli wpisałeś hasło, kolory są już zmienione przez XOR z kluczem, zanim algorytm ruszył."
        
        round_num = (steps - 1) // 5
        step_idx = (steps - 1) % 5
        
        # Słownik z dokładnymi opisami
        descs = {
            "Theta": (
                "KROK 1: THETA (DYFUZJA / ROZMYCIE)",
                "Operacja: XOR z sumą sąsiednich kolumn.\n"
                "Efekt wizualny: Szachownica zanika lub 'szarzeje'.\n"
                "Dlaczego? Każdy piksel 'zaciąga' informację od 10 innych pikseli (sąsiednie kolumny). "
                "Jeśli obok był biały piksel, wpływa on na czarny piksel. To niszczy lokalne wzory."
            ),
            "Rho": (
                "KROK 2: RHO (PRZESUNIĘCIE WARTOŚCI)",
                "Operacja: Rotacja bitowa (Bitwise Rotate) wzdłuż osi Z.\n"
                "Efekt wizualny: Zmiana odcieni szarości (ale kształty zostają).\n"
                "Dlaczego? Przesuwamy bity wewnątrz bajtu (np. 00000011 -> 00000110). "
                "Piksel nie zmienia miejsca (x,y), zmienia się tylko jego wartość liczbowa (jasność)."
            ),
            "Pi": (
                "KROK 3: PI (PERMUTACJA / TASOWANIE)",
                "Operacja: Przestawienie współrzędnych (x, y) -> (y, 2x+3y).\n"
                "Efekt wizualny: Pocięcie obrazu i 'teleportacja' kwadratów.\n"
                "Dlaczego? To fizyczne przeniesienie bajtu w inne miejsce macierzy 5x5. "
                "Struktura geometryczna (np. linie szachownicy) zostaje rozerwana i rozrzucona po całym stanie."
            ),
            "Chi": (
                "KROK 4: CHI (KONFUZJA / CHAOS)",
                "Operacja: Nieliniowa funkcja A = A ^ ((~B) & C).\n"
                "Efekt wizualny: Całkowita utrata przewidywalności kolorów.\n"
                "Dlaczego? To jedyny krok, którego nie da się prosto odwrócić (przez bramkę AND). "
                "Kolor piksela zależy teraz od skomplikowanej relacji z dwoma sąsiadami. Obraz zaczyna przypominać szum."
            ),
            "Iota": (
                "KROK 5: IOTA (ASYMETRIA)",
                "Operacja: XOR z losową stałą rundy (tylko w rogu).\n"
                "Efekt wizualny: Niewielka zmiana (często niewidoczna dla oka).\n"
                "Dlaczego? Matematycznie zapobiega to sytuacji, w której identyczne wejścia w różnych rundach dawałyby ten sam wynik. Łamie symetrię."
            )
        }
        
        keys = ["Theta", "Rho", "Pi", "Chi", "Iota"]
        key = keys[step_idx]
        title, body = descs[key]
        
        return f"RUNDA {round_num} | {title}\n{body}"

    def update_label_text_only(self, val):
        steps = int(float(val))
        txt = self.get_detailed_description(steps)
        self.info_label.config(text=txt)

    def on_slider_release(self, event):
        self.process_image()

    def process_image(self):
        if not hasattr(self, 'processing_source'): return
        
        target_steps = int(self.step_var.get())
        password = self.pass_entry.get()
        
        if target_steps == 0 and not password:
            self.lbl_enc.config(image=self.photo_orig)
            return

        w = 8 
        block_size = 25 
        k = KeccakSponge(rate=200, capacity=0, w=w, rounds=10)
        
        img_bytes = self.processing_source.tobytes()
        key_bytes = password.encode('utf-8')
        out_bytes = bytearray()
        
        class StopProcessing(Exception): pass
        current_step_counter = 0
        
        def my_callback(name, state):
            nonlocal current_step_counter
            current_step_counter += 1
            if current_step_counter >= target_steps:
                raise StopProcessing

        for i in range(0, len(img_bytes), block_size):
            chunk = img_bytes[i : i + block_size]
            k.state = [[[0] * w for _ in range(5)] for _ in range(5)]
            
            if key_bytes:
                k.xorowanie_do_stanu((key_bytes * 10)[:block_size])

            k.xorowanie_do_stanu(chunk)
            
            current_step_counter = 0
            if target_steps > 0:
                try:
                    k.keccak_f(callback=my_callback)
                except StopProcessing:
                    pass 
                except Exception: pass

            processed = k.stan_na_bajty(block_size)
            out_bytes.extend(processed[:len(chunk)])

        try:
            res_img = Image.frombytes("L", self.process_size, bytes(out_bytes))
            disp_large = res_img.resize(self.display_size, Image.Resampling.NEAREST)
            self.photo_enc = ImageTk.PhotoImage(disp_large)
            self.lbl_enc.config(image=self.photo_enc)
        except Exception as e:
            print(f"Display error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Wizualizacja Keccak SHA-3")
    app = EncryptionModule(root)
    root.mainloop()