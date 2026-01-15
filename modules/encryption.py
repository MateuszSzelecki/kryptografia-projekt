import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import sys

# Ensure we can import from root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from keccak import KeccakSponge

class EncryptionModule(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        
        # Determine paths
        if getattr(sys, 'frozen', False):
            self.base_path = sys._MEIPASS
        else:
            self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.image_path = os.path.join(self.base_path, "assets", "agh.png")
        
        self.original_image_pil = None
        self.encrypted_image_pil = None
        self.original_photo = None
        self.encrypted_photo = None
        
        self.setup_ui()
        self.load_and_display_image()

    def setup_ui(self):
        # Top Control Panel
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Key Entry
        ttk.Label(control_frame, text="Klucz:").pack(side=tk.LEFT, padx=5)
        self.key_entry = ttk.Entry(control_frame, width=20)
        self.key_entry.insert(0, "tajny_klucz_agh")
        self.key_entry.pack(side=tk.LEFT, padx=5)
        
        # Rounds Entry
        ttk.Label(control_frame, text="Rundy:").pack(side=tk.LEFT, padx=5)
        self.rounds_var = tk.IntVar(value=6) # Default reduced for speed demo
        self.rounds_spin = ttk.Spinbox(control_frame, from_=1, to=24, textvariable=self.rounds_var, width=5)
        self.rounds_spin.pack(side=tk.LEFT, padx=5)
        
        encrypt_btn = ttk.Button(control_frame, text="Szyfruj Obraz", command=self.encrypt_image)
        encrypt_btn.pack(side=tk.LEFT, padx=10)
        
        # Info Label
        ttk.Label(control_frame, text="(Obraz jest pomniejszany dla wydajności)", font=('Arial', 8, 'italic')).pack(side=tk.LEFT, padx=10)

        # Main Content Area (Split View)
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left Panel - Original
        self.left_panel = ttk.LabelFrame(content_frame, text="Oryginał")
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.original_label = ttk.Label(self.left_panel)
        self.original_label.pack(expand=True)
        
        # Right Panel - Encrypted
        self.right_panel = ttk.LabelFrame(content_frame, text="Obraz Zaszyfrowany")
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.encrypted_label = ttk.Label(self.right_panel, text="Tu pojawi się zaszyfrowany obraz")
        self.encrypted_label.pack(expand=True)

    def load_and_display_image(self):
        if not os.path.exists(self.image_path):
            self.original_label.config(text=f"Brak pliku: {self.image_path}")
            return
            
        try:
            pil_img = Image.open(self.image_path).convert("RGB")
            self.original_image_pil = pil_img
            
            # Defer resizing to after the window is drawn to get accurate dimensions
            self.after(100, self.resize_and_show_original)
        except Exception as e:
            self.original_label.config(text=f"Błąd: {e}")

    def resize_and_show_original(self):
        if self.original_image_pil is None:
            return
            
        # Calc available space in left panel
        w = self.left_panel.winfo_width() - 20
        h = self.left_panel.winfo_height() - 20
        
        if w <= 1 or h <= 1:
            # Retry if geometry isn't ready
            self.after(100, self.resize_and_show_original)
            return
            
        img_w, img_h = self.original_image_pil.size
        scale = min(w / img_w, h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        
        self.display_w = new_w
        self.display_h = new_h
        
        resized = self.original_image_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.original_photo = ImageTk.PhotoImage(resized)
        
        self.original_label.config(image=self.original_photo, text="")

    def encrypt_image(self):
        if self.original_image_pil is None:
            messagebox.showerror("Błąd", "Nie załadowano obrazu.")
            return
            
        key = self.key_entry.get() # Key is unused in visual permutation mode (or we could XOR it first)
        # For visualization of "Rounds vs Operations", unkeyed permutation or fixed key is better to see the mechanics.
        # But let's keep the key concept: Key mixing -> Initial State -> XOR Image Block -> Permute -> Output.
        
        try:
            rounds = int(self.rounds_var.get())
        except ValueError:
            rounds = 24
            
        # Optimization: Resize source image
        max_dim = 256
        img_to_process = self.original_image_pil.copy()
        img_to_process.thumbnail((max_dim, max_dim), Image.Resampling.BICUBIC)
        
        img_data = img_to_process.tobytes()
        
        # UI Update
        self.encrypted_label.config(text="Przetwarzanie...", image="")
        self.update_idletasks()
        
        try:
            # VISUALIZATION MODE: Direct Block Permutation (ECB-like)
            # We want to see how 'rounds' affect the mixing of pixels.
            # We will split image into 200-byte blocks (Full State), absorb, permute (N rounds), squeeze.
            
            # Rate = 1600 bits (200 bytes) to use full state for data
            # Capacity = 0 (Theoretical max for unkeyed sponge, insecure but good for vis)
            block_size = 200
            
            keccak = KeccakSponge(rate=1600, capacity=0, w=64, rounds=rounds)
            
            encrypted_bytes = bytearray()
            
            # Simple pre-calc for key to mix into initial state (optional, let's keep it simple: Pure Permutation of Data)
            # If we want to show "Encryption", we should XOR key. 
            # Let's do: State = Block ^ KeyHash; State = f(State); Output = State.
            # But simpler for "Rounds Effect": State = Block; State = f(State).
            
            # Let's stick to pure permutation of the image data to see the "Avalanche/Diffusion" of the structure.
            
            total_len = len(img_data)
            for i in range(0, total_len, block_size):
                chunk = img_data[i : i + block_size]
                
                # Reset state manually for "ECB" mode (independent blocks)
                keccak.state = [[[0] * 64 for _ in range(5)] for _ in range(5)]
                
                # Load data (XOR into zero state = set data)
                keccak.xorowanie_do_stanu(chunk)
                
                # Apply Permutation (specified rounds)
                keccak.keccak_f()
                
                # Extract Result
                processed_chunk = keccak.stan_na_bajty(len(chunk)) # Only take what we need
                encrypted_bytes.extend(processed_chunk)
                
            # Create image
            encrypted_img = Image.frombytes("RGB", img_to_process.size, bytes(encrypted_bytes))
            self.encrypted_image_pil = encrypted_img
            
            self.show_encrypted_result()
            
        except Exception as e:
            messagebox.showerror("Błąd Szyfrowania", str(e))

    def show_encrypted_result(self):
        if self.encrypted_image_pil is None:
            return
            
        # Resize to fit right panel, matching the "display" size of the original if possible
        # or just maximize to panel
        w = self.right_panel.winfo_width() - 20
        h = self.right_panel.winfo_height() - 20
        
        # We start from the small encrypted image, so we scale UP
        img_w, img_h = self.encrypted_image_pil.size
        
        # Use simple scaling to fit panel
        scale = min(w / img_w, h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        
        resized = self.encrypted_image_pil.resize((new_w, new_h), Image.Resampling.NEAREST) # Nearest to see the pixels
        self.encrypted_photo = ImageTk.PhotoImage(resized)
        
        self.encrypted_label.config(image=self.encrypted_photo, text="")
