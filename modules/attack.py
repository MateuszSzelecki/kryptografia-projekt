import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AttackModule(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.is_running = False
        self.create_widgets()

    def create_widgets(self):
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        input_frame = ttk.LabelFrame(main_container, text=" Parametry Ataku ")
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        params_grid = ttk.Frame(input_frame)
        params_grid.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(params_grid, text="Szerokość (w):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ent_w = ttk.Entry(params_grid, width=8)
        self.ent_w.insert(0, "64")
        self.ent_w.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(params_grid, text="Rundy:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.ent_rounds = ttk.Entry(params_grid, width=8)
        self.ent_rounds.insert(0, "24")
        self.ent_rounds.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(params_grid, text="Wejście (B):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.ent_in = ttk.Entry(params_grid, width=8)
        self.ent_in.insert(0, "16")
        self.ent_in.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(params_grid, text="Wyjście (B):").grid(row=0, column=6, padx=5, pady=5, sticky="e")
        self.ent_out = ttk.Entry(params_grid, width=8)
        self.ent_out.insert(0, "2")
        self.ent_out.grid(row=0, column=7, padx=5, pady=5)

        self.btn_start = ttk.Button(input_frame, text="URUCHOM ATAK", command=self.toggle_attack)
        self.btn_start.pack(pady=(0, 10))

        info_frame = ttk.Frame(main_container)
        info_frame.pack(fill=tk.X, padx=5)
        
        self.lbl_status = ttk.Label(info_frame, text="Status: Gotowy", font=('Arial', 10, 'bold'))
        self.lbl_status.pack(side=tk.LEFT, padx=10)
        
        self.lbl_attempts = ttk.Label(info_frame, text="Próby: 0", font=('Arial', 10))
        self.lbl_attempts.pack(side=tk.LEFT, padx=10)

        pw = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        pw.pack(fill=tk.BOTH, expand=True, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, pw)
        pw.add(self.canvas.get_tk_widget())

        self.txt_logs = tk.Text(pw, width=45, font=('Consolas', 9), state='disabled', bg="#f4f4f4")
        pw.add(self.txt_logs)

        self.reset_plot()

    def reset_plot(self):
        self.ax.clear()
        self.ax.set_title("Analiza prawdopodobieństwa kolizji")
        self.ax.set_xlabel("Liczba prób")
        self.ax.set_ylabel("Prawdopodobieństwo (%)")
        self.ax.set_ylim(0, 105)
        self.ax.grid(True, linestyle="--", alpha=0.6)
        self.canvas.draw_idle()

    def log(self, msg):
        self.txt_logs.config(state='normal')
        self.txt_logs.insert(tk.END, msg + "\n")
        self.txt_logs.see(tk.END)
        self.txt_logs.config(state='disabled')

    def calculate_prob(self, attempts, hash_bytes):
        N = 2**(hash_bytes * 8)
        if attempts > N: return 100.0
        return (1 - math.exp(-(attempts**2) / (2 * N))) * 100

    def toggle_attack(self):
        if self.is_running:
            self.is_running = False
            return

        try:
            config = {
                "w": int(self.ent_w.get()),
                "rounds": int(self.ent_rounds.get()),
                "in_size": int(self.ent_in.get()),
                "out_size": int(self.ent_out.get())
            }
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowe parametry wejściowe.")
            return

        self.is_running = True
        self.btn_start.config(text="STOP")
        self.lbl_status.config(text="Status: Praca...", foreground="orange")
        self.txt_logs.config(state='normal'); self.txt_logs.delete('1.0', tk.END); self.txt_logs.config(state='disabled')
        self.reset_plot()
        
        threading.Thread(target=self.attack_worker, args=(config,), daemon=True).start()

    def attack_worker(self, cfg):
        try:
            from main import KeccakSponge
        except ImportError:
            from keccak import KeccakSponge

        seen_hashes = {}
        attempts = 0
        x_data, y_data = [], []
        
        total_bits = 25 * cfg['w']
        rate = total_bits - (512 if total_bits > 512 else 64)
        cap = total_bits - rate

        while self.is_running:
            attempts += 1
            
            rand_input = os.urandom(cfg['in_size'])
            
            k = KeccakSponge(rate, cap, cfg['w'], cfg['rounds'])
            k.wchlanianie(rand_input)
            digest = k.wyciskanie(cfg['out_size'])
            
            if digest in seen_hashes:
                if seen_hashes[digest] != rand_input:
                    prob = self.calculate_prob(attempts, cfg['out_size'])
                    self.after(0, self.finish_attack, rand_input, seen_hashes[digest], digest, attempts, prob)
                    return
            
            seen_hashes[digest] = rand_input

            if attempts % 200 == 0 or attempts == 1:
                p = self.calculate_prob(attempts, cfg['out_size'])
                x_data.append(attempts)
                y_data.append(p)
                self.after(0, self.update_view, attempts, x_data, y_data)

            if attempts > 1000000:
                self.after(0, lambda: messagebox.showwarning("Przerwano", "Przekroczono limit prób."))
                break

        self.after(0, self.reset_ui)

    def update_view(self, att, x, y):
        self.lbl_attempts.config(text=f"Próby: {att}")
        self.ax.plot(x, y, color='red', lw=2)
        self.canvas.draw_idle()

    def finish_attack(self, m1, m2, h, att, pr):
        self.log(f"Znaleziono kolizję!")
        self.log(f"Próby: {att}")
        self.log(f"Prawdopodobieństwo: {pr:.4f}%")
        self.log(f"Hash (HEX): {h.hex().upper()}")
        self.log(f"M1: {m1.hex()}")
        self.log(f"M2: {m2.hex()}")
        self.lbl_status.config(text="Status: ZAKOŃCZONO", foreground="green")
        messagebox.showinfo("Wynik", f"Kolizja znaleziona po {att} krokach.")
        self.reset_ui()

    def reset_ui(self):
        self.is_running = False
        self.btn_start.config(text="URUCHOM ATAK")
        if "ZAKOŃCZONO" not in self.lbl_status.cget("text"):
            self.lbl_status.config(text="Status: Przerwano", foreground="red")