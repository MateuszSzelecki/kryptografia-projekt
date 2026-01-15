import tkinter as tk
from tkinter import ttk
import os
import sys
from PIL import Image, ImageTk

# Import modules
try:
    from modules.avalanche import AvalancheModule
    from modules.encryption import EncryptionModule
    from modules.visualization import VisualizationModule
    from modules.attack import AttackModule
except ImportError as e:
    print(f"Module import error: {e}")

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Projekt Kryptografia: Keccak Advanced")
        try:
            self.root.state('zoomed')
        except:
            self.root.attributes('-fullscreen', True)
            
        self.current_frame = None
        
        # Mapping buttons to (slides_list, module_class)
        self.modules_config = {
            "avalanche": {
                "slides": ["efekt1.png", "efekt2.png"],
                "module_class": AvalancheModule,
                "title": "Efekt Lawinowy"
            },
            "encryption": {
                "slides": ["szyfr1.png", "szyfr2.png"], 
                "module_class": EncryptionModule, 
                "title": "Szyfrowanie Obrazów"
            },
            "visualization": {
                "slides": ["viz1.png", "viz2.png"], 
                "module_class": VisualizationModule, 
                "title": "Wizualizacja Stanu"
            },
            "attack": {
                "slides": ["atak1.png", "atak2.png"], 
                "module_class": AttackModule, 
                "title": "Atak na Keccaka"
            }
        }
        
        self.show_launcher()
        
        # Bind global space for slideshow navigation
        self.root.bind('<space>', self.handle_space)
        self.slideshow_active = False
        self.current_slides = []
        self.current_slide_index = 0
        self.target_module_key = None

    def show_launcher(self):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.slideshow_active = False
        self.root.unbind('<space>') # Unbind space on launcher
        self.root.unbind('<Shift-Return>') # Unbind back shortcut
        
        self.current_frame = ttk.Frame(self.root)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        lbl = ttk.Label(self.current_frame, text="Wybierz Moduł", font=('Helvetica', 24, 'bold'))
        lbl.pack(pady=40)
        
        # Buttons Grid
        btn_frame = ttk.Frame(self.current_frame)
        btn_frame.pack(expand=True)
        
        opts = [
            ("Efekt Lawinowy", "avalanche"),
            ("Szyfrowanie Obrazów", "encryption"),
            ("Wizualizacja Stanu", "visualization"),
            ("Atak (Kolizje)", "attack")
        ]
        
        for i, (text, key) in enumerate(opts):
            btn = ttk.Button(btn_frame, text=text, command=lambda k=key: self.start_slideshow(k))
            # Make buttons big
            btn.grid(row=i//2, column=i%2, padx=20, pady=20, ipadx=40, ipady=30, sticky="nsew")

    def start_slideshow(self, key):
        self.target_module_key = key
        config = self.modules_config[key]
        self.current_slides = config["slides"]
        self.current_slide_index = 0
        self.slideshow_active = True
        
        # Re-bind space
        self.root.bind('<space>', self.handle_space)
        
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = tk.Frame(self.root, bg="black")
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
        self.display_current_slide()

    def display_current_slide(self):
        # Clear previous slide content
        for widget in self.current_frame.winfo_children():
            widget.destroy()
            
        slide_name = self.current_slides[self.current_slide_index]
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        path = os.path.join(base_path, "assets", slide_name)
        
        # Fallback if image doesn't exist
        if not os.path.exists(path):
            lbl = tk.Label(self.current_frame, text=f"SLAJD: {slide_name}\n(Naciśnij SPACJĘ)", 
                           fg="white", bg="black", font=('Arial', 32))
            lbl.pack(expand=True)
            return
            
        try:
            img = Image.open(path)
            
            # Get current window size
            self.root.update_idletasks() # Ensure geometry is up to date
            win_w = self.current_frame.winfo_width()
            win_h = self.current_frame.winfo_height()
            
            # Resize image to fit
            img = img.resize((win_w, win_h), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(self.current_frame, image=photo, bg="black")
            lbl.image = photo # Keep reference
            lbl.pack(fill=tk.BOTH, expand=True)
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
            # End of slideshow -> Launch Module
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
        
        # Bind Back only when module is active
        self.root.bind('<Shift-Return>', lambda e: self.show_launcher())
        
        if module_class:
            app = module_class(self.current_frame)
            app.pack(fill=tk.BOTH, expand=True)
        else:
            ttk.Label(self.current_frame, text=f"Moduł '{config['title']}' w budowie...", font=('Arial', 20)).pack(pady=50)

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
