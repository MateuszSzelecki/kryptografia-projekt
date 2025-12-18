import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

from main import KeccakSponge

class KeccakAvalancheApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Projekt Kryptografia: Analiza Lawinowości SHA-3 + Haszowanie")
        
        try:
            self.root.state('zoomed')
        except:
            self.root.attributes('-fullscreen', True)

        self.results_cache = {}

        input_frame = ttk.LabelFrame(root, text="Konfiguracja Parametrów i Wiadomości")
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.entries = []
        
        defaults = [
            ('red',    24, 64, True,  "Standard SHA-3"),
            ('blue',   24, 32, True,  "Mniejszy stan"),
            ('green',  24, 16, True,  "Krotkie slowo"),
            ('orange', 24, 8,  True,  "Szybka dyfuzja"),
            ('purple', 12, 64, False, "Malo rund"),
            ('brown',  6,  64, False, "Bardzo malo rund")
        ]
        
        headers = ["Pokaż?", "Kolor", "Liczba Rund", "Szerokość (w)", "Wiadomość (Input)", "Wynik (Hash - pierwsze 16 bajtów)"]
        for col, text in enumerate(headers):
            ttk.Label(input_frame, text=text, font=('Arial', 9, 'bold')).grid(row=0, column=col, padx=5, pady=5)

        for i, (color, def_r, def_w, def_visible, def_msg) in enumerate(defaults):
            row_idx = i + 1
            
            visible_var = tk.BooleanVar(value=def_visible)
            check = ttk.Checkbutton(input_frame, variable=visible_var, command=self.update_plot_view)
            check.grid(row=row_idx, column=0, padx=5, pady=2)
            
            lbl = ttk.Label(input_frame, text=color.upper(), foreground=color, font=('bold'))
            lbl.grid(row=row_idx, column=1, padx=5, pady=2)
            
            rounds_entry = ttk.Entry(input_frame, width=10)
            rounds_entry.insert(0, str(def_r))
            rounds_entry.grid(row=row_idx, column=2, padx=5, pady=2)
            
            w_entry = ttk.Entry(input_frame, width=10)
            w_entry.insert(0, str(def_w)) 
            w_entry.grid(row=row_idx, column=3, padx=5, pady=2)
            
            msg_entry = ttk.Entry(input_frame, width=30)
            msg_entry.insert(0, def_msg)
            msg_entry.grid(row=row_idx, column=4, padx=5, pady=2)
            
            hash_entry = ttk.Entry(input_frame, width=70) 
            hash_entry.state(['readonly']) 
            hash_entry.grid(row=row_idx, column=5, padx=5, pady=2)
            
            self.entries.append({
                'index': i,
                'color': color, 
                'rounds': rounds_entry, 
                'w': w_entry,
                'msg': msg_entry,
                'hash_out': hash_entry,
                'visible': visible_var
            })
        
        btn_frame = ttk.Frame(root)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=10)
        
        self.calc_btn = ttk.Button(btn_frame, text="PRZELICZ (Generuj hashe i wykresy)", command=self.calculate_all_data)
        self.calc_btn.pack(pady=10)

        
        self.plot_frame = ttk.Frame(root)
        self.plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def calculate_hamming_diff(self, state1, state2, w):
        diff = 0
        for x in range(5):
            for y in range(5):
                for z in range(w):
                    if state1[x][y][z] != state2[x][y][z]:
                        diff += 1
        return diff

    def calculate_params(self, w):
        state_bits = 25 * w
        
        capacity = 512
        if capacity >= state_bits: capacity = 8 
        rate = state_bits - capacity
        return rate, capacity

    def run_simulation(self, rounds, w, message_text):
        """
        Zwraca: (distances, total_bits, computed_hash_hex)
        """
        rate, capacity = self.calculate_params(w)

        try:
            msg_bytes = message_text.encode('utf-8')
        except:
            msg_bytes = b'error'
        
        hasher = KeccakSponge(rate=rate, capacity=capacity, w=w, rounds=rounds)
        hasher.wchlanianie(msg_bytes)
        
        digest = hasher.wyciskanie(32) 
        hash_hex = digest.hex()

        sponge1 = KeccakSponge(rate=rate, capacity=capacity, w=w, rounds=rounds)
        sponge2 = KeccakSponge(rate=rate, capacity=capacity, w=w, rounds=rounds)
        
        msg_arr = bytearray(msg_bytes)
        msg_arr_flipped = bytearray(msg_bytes)
        if len(msg_arr_flipped) > 0:
            msg_arr_flipped[-1] ^= 1 
        else:
            
            msg_arr.append(0)
            msg_arr_flipped.append(1)

        sponge1.xorowanie_do_stanu(msg_arr)
        sponge2.xorowanie_do_stanu(msg_arr_flipped)

        distances = []
        total_bits = 25 * w
        
        distances.append(self.calculate_hamming_diff(sponge1.state, sponge2.state, w))

        for r in range(rounds):
            sponge1.wykonaj_pojedyncza_runde(r)
            sponge2.wykonaj_pojedyncza_runde(r)
            dist = self.calculate_hamming_diff(sponge1.state, sponge2.state, w)
            distances.append(dist)

        return distances, total_bits, hash_hex

    def calculate_all_data(self):
        self.results_cache = {}
        self.root.config(cursor="wait")
        self.root.update()

        for entry in self.entries:
            try:
                r_val = int(entry['rounds'].get())
                w_val = int(entry['w'].get())
                msg_txt = entry['msg'].get()
                idx = entry['index']
                
                if w_val <= 0: continue

                distances, total_bits, hash_hex = self.run_simulation(r_val, w_val, msg_txt)
                                
                self.results_cache[idx] = (distances, total_bits)
                
                entry['hash_out'].state(['!readonly'])
                entry['hash_out'].delete(0, tk.END)
                entry['hash_out'].insert(0, hash_hex)
                entry['hash_out'].state(['readonly'])
                
            except ValueError:
                continue

        self.root.config(cursor="")
        self.update_plot_view()

    def update_plot_view(self):
        self.ax.clear()
        has_plots = False

        for entry in self.entries:
            idx = entry['index']
            if idx in self.results_cache and entry['visible'].get():
                distances, total_bits = self.results_cache[idx]
                r_val = entry['rounds'].get()
                w_val = entry['w'].get()
                color = entry['color']

                percentages = [d / total_bits * 100 for d in distances]
                
                self.ax.plot(range(len(percentages)), percentages, 
                             marker='o', linestyle='-', color=color, 
                             label=f'R={r_val}, w={w_val}')
                has_plots = True

        self.ax.set_title("Efekt Lawinowy (Zmiana % bitów stanu)")
        self.ax.set_xlabel("Numer Rundy")
        self.ax.set_ylabel("% Zmian (Cel: ~50%)")
        self.ax.set_ylim(0, 60)
        self.ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50%')
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        if has_plots:
            self.ax.legend()
        
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = KeccakAvalancheApp(root)
    root.mainloop()