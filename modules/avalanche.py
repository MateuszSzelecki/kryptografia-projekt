import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from keccak import KeccakSponge
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


class AvalancheModule(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        self.results_cache = {}
        self.base_fontsize = 10
        self.create_widgets()

    # ================== UI ==================
    def create_widgets(self):
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ---------- INPUT ----------
        input_frame = ttk.LabelFrame(
            main_container,
            text="Konfiguracja Parametrów i Wiadomości"
        )
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.entries = []

        # Domyślne wartości (zostaną nadpisane przez scenariusze)
        defaults = [
            ('red',    24, 64, True,  "Standard SHA-3"),
            ('blue',   24, 32, True,  "Mniejszy stan"),
            ('green',  24, 16, True,  "Krótkie słowo"),
            ('orange', 24, 8,  True,  "Szybka dyfuzja"),
            ('purple', 12, 64, False, "Mało rund"),
            ('brown',  6,  64, False, "Bardzo mało rund")
        ]

        headers = [
            "Pokaż", "Kolor", "Rundy", "Szer",
            "Wiadomość (Input)", "Wynik (Hash)"
        ]

        for c, h in enumerate(headers):
            ttk.Label(
                input_frame,
                text=h,
                font=('Arial', 8, 'bold')
            ).grid(row=0, column=c, padx=2, pady=2, sticky="ew")

        # === ZMIANA TUTAJ ===
        # Zmniejszono weight dla kolumny 4 (Wiadomość) z 2 na 1
        # Zwiększono weight dla kolumny 5 (Hash) z 1 na 3
        input_frame.columnconfigure(4, weight=1)
        input_frame.columnconfigure(5, weight=3)
        # ====================

        for i, (color, r, w, vis, msg) in enumerate(defaults):
            row = i + 1

            visible = tk.BooleanVar(value=vis)
            cb = ttk.Checkbutton(
                input_frame,
                variable=visible,
                command=self.update_plot_view
            )
            cb.grid(row=row, column=0)

            ttk.Label(
                input_frame,
                text=color.upper(),
                foreground=color,
                font=('Arial', 9, 'bold')
            ).grid(row=row, column=1)

            e_r = ttk.Entry(input_frame, width=5)
            e_r.insert(0, r)
            e_r.grid(row=row, column=2)

            e_w = ttk.Entry(input_frame, width=5)
            e_w.insert(0, w)
            e_w.grid(row=row, column=3)

            e_m = ttk.Entry(input_frame)
            e_m.insert(0, msg)
            e_m.grid(row=row, column=4, sticky="ew")

            # Można też ewentualnie zwiększyć startowy width tutaj, np. na 50
            e_h = ttk.Entry(input_frame, width=50, state="readonly")
            e_h.grid(row=row, column=5, sticky="ew")

            self.entries.append({
                "index": i,
                "color": color,
                "rounds": e_r,
                "w": e_w,
                "msg": e_m,
                "hash_out": e_h,
                "visible": visible,
                "chk_btn": cb # przechowujemy referencje do checkboxa
            })

        # ---------- BUTTONS & SCENARIOS ----------
        # Ramka na przyciski sterujące
        ctrl_frame = ttk.Frame(main_container)
        ctrl_frame.pack(pady=5, fill=tk.X)

        # Sekcja Scenariuszy
        scen_frame = ttk.LabelFrame(ctrl_frame, text="Wybierz Scenariusz Badawczy")
        scen_frame.pack(side=tk.TOP, pady=5)

        ttk.Button(scen_frame, text="SCENARIUSZ 1\n(Wpływ rozmiaru stanu)", width=25,
                   command=lambda: self.load_scenario(1)).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(scen_frame, text="SCENARIUSZ 2\n(Szybkosc dyfuzji)", width=25,
                   command=lambda: self.load_scenario(2)).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(scen_frame, text="SCENARIUSZ 3\n(Odpornosc na wzorce)", width=25,
                   command=lambda: self.load_scenario(3)).pack(side=tk.LEFT, padx=5, pady=5)

        # Główny przycisk
        ttk.Button(
            ctrl_frame,
            text="PRZELICZ (Generuj Wykres)",
            command=self.calculate_all_data
        ).pack(side=tk.TOP, fill=tk.X, padx=50, pady=(5, 0))

        # ---------- PLOT ----------
        self.plot_frame = ttk.Frame(main_container)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.figure, self.ax = plt.subplots(dpi=100)
        self.figure.subplots_adjust(left=0.08, right=0.97, top=0.93, bottom=0.15)

        self.ax_zoom = inset_axes(
            self.ax,
            width="35%",
            height="35%",
            loc="lower right",
            borderpad=3.0
        )

        self.canvas = FigureCanvasTkAgg(self.figure, self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.plot_frame.bind("<Configure>", self.on_resize)
        self.after(100, self.force_resize)

    # ================== SCENARIOS ==================
    def load_scenario(self, scen_id):
        data = []
        
        if scen_id == 1:
            data = [
                (24, 256, "test"),     # Red
                (24, 128, "test"),     # Blue
                (24, 64, "test"),     # Green
                (24, 32,  "test"),     # Orange
                (24, 16,  "test"),     # Purple
                (24, 8,  "test")      # Brown
            ]
            
        elif scen_id == 2:
            msg = "bezpieczenstwo"
            data = [
                (24, 64, "A"), # Red
                (18,  64, "B"), # Blue
                (12,  64, "C"), # Green
                (8,  64, "D"), # Orange
                (6,  64, "E"), # Purple
                (3,  64, "F")  # Brown
            ]
            
        elif scen_id == 3:
            data = [
                (24,  64, ""),                       # Red - Pusty input
                (24,  64, "0000000000000000"),       # Blue - Same zera
                (24,  64, "AAAAAAAAAAAAAAAA"),       # Green - Wzorzec
                (24,  64, "LosowyTekst!@#123"),      # Orange - Losowy
                (24,  64, "1111111111111111"),       # Purple - Same jedynki
                (24, 64, "Krotki")                    # Brown - Referencja (ideał)
            ]

        # Aplikowanie danych do pól
        for i, (r, w, msg) in enumerate(data):
            if i < len(self.entries):
                entry = self.entries[i]
                
                # Ustaw widoczność na True
                entry["visible"].set(True)
                
                # Rundy
                entry["rounds"].delete(0, tk.END)
                entry["rounds"].insert(0, str(r))
                
                # Szerokość
                entry["w"].delete(0, tk.END)
                entry["w"].insert(0, str(w))
                
                # Wiadomość
                entry["msg"].delete(0, tk.END)
                entry["msg"].insert(0, msg)
                
                # Czyść stare wyniki
                entry["hash_out"].config(state="normal")
                entry["hash_out"].delete(0, tk.END)
                entry["hash_out"].config(state="readonly")
        
        # Wyczyść wykres po zmianie danych (wymaga ponownego przeliczenia)
        self.ax.clear()
        self.ax_zoom.clear()
        self.canvas.draw_idle()

    # ================== RESIZE + FONT ==================
    def force_resize(self):
        w = self.plot_frame.winfo_width()
        h = self.plot_frame.winfo_height()
        if w > 50 and h > 50:
            self.on_resize(type("E", (), {"width": w, "height": h})())

    def on_resize(self, event):
        if event.width < 50 or event.height < 50:
            return

        dpi = self.figure.get_dpi()
        self.figure.set_size_inches(
            event.width / dpi,
            event.height / dpi,
            forward=True
        )

        self.scale_fonts(event.width, event.height)
        self.canvas.draw_idle()

    def scale_fonts(self, width, height):
        scale = min(width / 900, height / 600)
        fs = max(8, int(self.base_fontsize * scale))

        self.ax.title.set_fontsize(fs + 4)
        self.ax.xaxis.label.set_fontsize(fs + 2)
        self.ax.yaxis.label.set_fontsize(fs + 2)

        for tick in self.ax.get_xticklabels() + self.ax.get_yticklabels():
            tick.set_fontsize(fs)

        for tick in self.ax_zoom.get_xticklabels() + self.ax_zoom.get_yticklabels():
            tick.set_fontsize(fs - 1)

        if self.ax.get_legend():
            for t in self.ax.get_legend().get_texts():
                t.set_fontsize(fs)

    # ================== KECCAK ==================
    def calculate_hamming_diff(self, s1, s2, w):
        return sum(
            1 for x in range(5)
            for y in range(5)
            for z in range(w)
            if s1[x][y][z] != s2[x][y][z]
        )

    def calculate_params(self, w):
        bits = 25 * w
        cap = 512 if 512 < bits else 8
        return bits - cap, cap

    def run_simulation(self, rounds, w, msg):
        rate, cap = self.calculate_params(w)
        msg_bytes = msg.encode("utf-8", errors="ignore")

        h = KeccakSponge(rate, cap, w, rounds)
        h.wchlanianie(msg_bytes)
        hexhash = h.wyciskanie(32).hex()

        s1 = KeccakSponge(rate, cap, w, rounds)
        s2 = KeccakSponge(rate, cap, w, rounds)

        m1 = bytearray(msg_bytes)
        m2 = bytearray(msg_bytes or b"\x00")
        m2[-1] ^= 1

        s1.xorowanie_do_stanu(m1)
        s2.xorowanie_do_stanu(m2)

        dist = [self.calculate_hamming_diff(s1.state, s2.state, w)]

        for r in range(rounds):
            s1.wykonaj_pojedyncza_runde(r)
            s2.wykonaj_pojedyncza_runde(r)
            dist.append(self.calculate_hamming_diff(s1.state, s2.state, w))

        return dist, 25 * w, hexhash

    # ================== CALC ==================
    def calculate_all_data(self):
        self.results_cache.clear()
        self.winfo_toplevel().config(cursor="wait")
        self.winfo_toplevel().update_idletasks()

        for e in self.entries:
            try:
                if not e["visible"].get():
                    continue

                r = int(e["rounds"].get())
                w = int(e["w"].get())
                msg = e["msg"].get()

                dist, bits, h = self.run_simulation(r, w, msg)
                self.results_cache[e["index"]] = (dist, bits)

                e["hash_out"].config(state="normal")
                e["hash_out"].delete(0, tk.END)
                e["hash_out"].insert(0, h)
                e["hash_out"].config(state="readonly")
            except Exception:
                # W przypadku błędu (np. zbyt małe w dla biblioteki) czyścimy pole
                e["hash_out"].config(state="normal")
                e["hash_out"].delete(0, tk.END)
                e["hash_out"].insert(0, "BŁĄD PARMETRÓW")
                e["hash_out"].config(state="readonly")

        self.winfo_toplevel().config(cursor="")
        self.update_plot_view()

    # ================== PLOT ==================
    def update_plot_view(self):
        self.ax.clear()
        self.ax_zoom.clear()

        for e in self.entries:
            idx = e["index"]
            if idx in self.results_cache and e["visible"].get():
                dist, bits = self.results_cache[idx]
                perc = [d / bits * 100 for d in dist]
                x = range(len(perc))

                label_text = f"R={e['rounds'].get()}, w={e['w'].get()}"
                msg = e['msg'].get()
                if len(msg) < 10 and msg != "":
                    label_text += f" [{msg}]"
                elif msg == "":
                     label_text += " [Pusty]"

                self.ax.plot(x, perc, marker='o', color=e["color"], label=label_text)
                self.ax_zoom.plot(x, perc, marker='o', color=e["color"])

        # main axis
        self.ax.set_title("Efekt Lawinowy")
        self.ax.set_xlabel("Numer rundy")
        self.ax.set_ylabel("% zmian")
        self.ax.set_ylim(0, 65) 
        self.ax.axhline(50, linestyle="--", color="gray", alpha=0.5)
        self.ax.grid(True, linestyle="--", alpha=0.6)
        
        self.ax.legend(loc="upper left")

        # zoom axis
        self.ax_zoom.set_ylim(40, 60)
        self.ax_zoom.set_title("Zoom 40–60%", fontsize=8)
        self.ax_zoom.grid(True, linestyle=":", alpha=0.5)

        self.canvas.draw_idle()