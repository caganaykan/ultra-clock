import customtkinter as ctk
import time
from datetime import datetime
from tkinter import messagebox

# Tema Ayarları
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ModernUltraApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(" Ultra Clock  - Tam Sürüm")
        self.geometry("650x850")

        # --- Değişkenler ---
        self.timer_vals = {"h": 0, "m": 0, "s": 0}
        self.alarm_vals = {"h": 8, "m": 30}
        self.alarm_active = False
        self.alarm_triggered_today = False

        self.sw_running = False
        self.sw_start_time = 0
        self.sw_elapsed = 0

        self.repeat_job = None
        self.timer_running = False
        self.remaining_time = 0
        self.total_time = 0

        self.create_widgets()
        self.update_master_loop()

    def create_widgets(self):
        self.tabs = ctk.CTkTabview(self, segmented_button_fg_color="#111")
        self.tabs.pack(padx=20, pady=20, fill="both", expand=True)

        self.tab_clock = self.tabs.add("🕒 SAAT")
        self.tab_alarm = self.tabs.add("🔔 ALARM")
        self.tab_timer = self.tabs.add("⏳ SAYAÇ")
        self.tab_sw = self.tabs.add("⏱️ KRONOMETRE")

        self.init_clock_tab()
        self.init_alarm_tab()
        self.init_timer_tab()
        self.init_sw_tab()

    # --- 🕒 SAAT VE ANA DÖNGÜ ---
    def init_clock_tab(self):
        self.lbl_main_time = ctk.CTkLabel(self.tab_clock, text="00:00:00", font=("Arial", 90, "bold"),
                                          text_color="#3498db")
        self.lbl_main_time.pack(pady=(200, 10))
        self.lbl_main_date = ctk.CTkLabel(self.tab_clock, text="", font=("Arial", 24), text_color="gray")
        self.lbl_main_date.pack()

    def update_master_loop(self):
        now = datetime.now()
        self.lbl_main_time.configure(text=now.strftime("%H:%M:%S"))
        self.lbl_main_date.configure(text=now.strftime("%d %B %Y %A"))

        # Alarm Kontrolü
        if self.alarm_active:
            if now.hour == self.alarm_vals["h"] and now.minute == self.alarm_vals["m"]:
                if not self.alarm_triggered_today:
                    self.trigger_alarm()
            else:
                self.alarm_triggered_today = False

        self.after(1000, self.update_master_loop)

    # --- 🔔 ALARM SİSTEMİ ---
    def init_alarm_tab(self):
        self.alarm_frame = ctk.CTkFrame(self.tab_alarm, fg_color="transparent")
        self.alarm_frame.pack(pady=100)

        for i, k in enumerate(["h", "m"]):
            box = ctk.CTkFrame(self.alarm_frame, fg_color="#222", corner_radius=12, width=140)
            box.grid(row=0, column=i, padx=20)
            ctk.CTkButton(box, text="▲", width=60, command=lambda x=k: self.adj_alarm(x, 1)).pack(pady=10)
            lbl = ctk.CTkLabel(box, text=f"{self.alarm_vals[k]:02d}", font=("Arial", 60, "bold"))
            lbl.pack()
            if k == "h":
                self.lbl_alarm_h = lbl
            else:
                self.lbl_alarm_m = lbl
            ctk.CTkButton(box, text="▼", width=60, command=lambda x=k: self.adj_alarm(x, -1)).pack(pady=10)

        self.btn_alarm_toggle = ctk.CTkButton(self.tab_alarm, text="ALAMI KUR", fg_color="#27ae60", width=250,
                                              height=60, font=("Arial", 20, "bold"), command=self.toggle_alarm)
        self.btn_alarm_toggle.pack(pady=50)

    def adj_alarm(self, unit, amt):
        self.alarm_vals[unit] = (self.alarm_vals[unit] + amt) % (24 if unit == "h" else 60)
        self.lbl_alarm_h.configure(text=f"{self.alarm_vals['h']:02d}")
        self.lbl_alarm_m.configure(text=f"{self.alarm_vals['m']:02d}")

    def toggle_alarm(self):
        self.alarm_active = not self.alarm_active
        self.btn_alarm_toggle.configure(text="ALARM AKTİF" if self.alarm_active else "ALAMI KUR",
                                        fg_color="#c0392b" if self.alarm_active else "#27ae60")

    def trigger_alarm(self):
        self.alarm_triggered_today = True
        messagebox.showinfo("ALARM! 🔔", f"Saat Geldi: {self.alarm_vals['h']:02d}:{self.alarm_vals['m']:02d}")

    # --- ⏳ SAYAÇ (İSTEDİĞİN GÜNCELLEME BURADA) ---
    def init_timer_tab(self):
        t_frame = ctk.CTkFrame(self.tab_timer, fg_color="transparent")
        t_frame.pack(pady=50)
        self.timer_labels = {}

        for i, (k, name) in enumerate([("h", "SAAT"), ("m", "DAK"), ("s", "SAN")]):
            box = ctk.CTkFrame(t_frame, fg_color="#222", corner_radius=12, width=120)
            box.grid(row=0, column=i, padx=10)
            ctk.CTkLabel(box, text=name, font=("Arial", 12, "bold")).pack(pady=5)

            btn_up = ctk.CTkButton(box, text="▲", width=40)
            btn_up.pack()
            btn_up.bind("<ButtonPress-1>", lambda e, x=k: self.start_timer_adj(x, 1))
            btn_up.bind("<ButtonRelease-1>", lambda e: self.stop_timer_adj())

            self.timer_labels[k] = ctk.CTkLabel(box, text="00", font=("Arial", 55, "bold"))
            self.timer_labels[k].pack()

            btn_down = ctk.CTkButton(box, text="▼", width=40)
            btn_down.pack(pady=5)
            btn_down.bind("<ButtonPress-1>", lambda e, x=k: self.start_timer_adj(x, -1))
            btn_down.bind("<ButtonRelease-1>", lambda e: self.stop_timer_adj())

        self.t_bar = ctk.CTkProgressBar(self.tab_timer, width=500, height=14)
        self.t_bar.set(0)
        self.t_bar.pack(pady=30)

        btn_box = ctk.CTkFrame(self.tab_timer, fg_color="transparent")
        btn_box.pack()
        self.btn_t_main = ctk.CTkButton(btn_box, text="BAŞLAT", fg_color="#27ae60", width=180, height=50,
                                        command=self.toggle_timer)
        self.btn_t_main.grid(row=0, column=0, padx=10)
        ctk.CTkButton(btn_box, text="SIFIRLA", fg_color="#c0392b", width=180, height=50, command=self.reset_timer).grid(
            row=0, column=1, padx=10)

    def start_timer_adj(self, unit, amt):
        if not self.timer_running:
            self.timer_vals[unit] = (self.timer_vals[unit] + amt) % (24 if unit == "h" else 60)
            self.timer_labels[unit].configure(text=f"{self.timer_vals[unit]:02d}")
            self.repeat_job = self.after(150, lambda: self.start_timer_adj(unit, amt))

    def stop_timer_adj(self):
        if self.repeat_job: self.after_cancel(self.repeat_job); self.repeat_job = None

    def toggle_timer(self):
        if not self.timer_running:
            self.remaining_time = self.timer_vals["h"] * 3600 + self.timer_vals["m"] * 60 + self.timer_vals["s"]
            if self.remaining_time > 0:
                self.total_time = self.remaining_time
                self.timer_running = True
                self.btn_t_main.configure(text="DURDUR", fg_color="#e67e22")
                self.timer_tick()
        else:
            self.timer_running = False
            self.btn_t_main.configure(text="BAŞLAT", fg_color="#27ae60")

    def timer_tick(self):
        if self.timer_running and self.remaining_time > 0:
            self.remaining_time -= 1
            h, rem = divmod(self.remaining_time, 3600)
            m, s = divmod(rem, 60)
            self.timer_labels["h"].configure(text=f"{int(h):02d}")
            self.timer_labels["m"].configure(text=f"{int(m):02d}")
            self.timer_labels["s"].configure(text=f"{int(s):02d}")
            self.t_bar.set(1 - (self.remaining_time / self.total_time))
            self.after(1000, self.timer_tick)
        elif self.remaining_time == 0 and self.timer_running:
            # SÜRE DOLUNCA BURASI ÇALIŞIR 📢
            self.reset_timer()
            self.btn_t_main.configure(text="SÜRE DOLDU!", fg_color="#f1c40f")

    def reset_timer(self):
        self.timer_running = False
        self.timer_vals = {"h": 0, "m": 0, "s": 0}
        for k in self.timer_labels: self.timer_labels[k].configure(text="00")
        self.t_bar.set(0)
        self.btn_t_main.configure(text="BAŞLAT", fg_color="#27ae60")

    # --- ⏱️ KRONOMETRE ---
    def init_sw_tab(self):
        self.lbl_sw = ctk.CTkLabel(self.tab_sw, text="00:00:00.00", font=("Arial", 80, "bold"))
        self.lbl_sw.pack(pady=80)
        sw_btns = ctk.CTkFrame(self.tab_sw, fg_color="transparent")
        sw_btns.pack()
        self.btn_sw_main = ctk.CTkButton(sw_btns, text="BAŞLAT", fg_color="#27ae60", width=180, height=50,
                                         command=self.toggle_sw)
        self.btn_sw_main.grid(row=0, column=0, padx=10)
        ctk.CTkButton(sw_btns, text="SIFIRLA", fg_color="#c0392b", width=180, height=50, command=self.reset_sw).grid(
            row=0, column=1, padx=10)
        self.lap_box = ctk.CTkScrollableFrame(self.tab_sw, width=500, height=250)
        self.lap_box.pack(pady=30)
        ctk.CTkButton(self.tab_sw, text="TUR EKLE", command=self.add_lap).pack()

    def toggle_sw(self):
        if not self.sw_running:
            self.sw_running = True
            self.sw_start_time = time.time() - self.sw_elapsed
            self.btn_sw_main.configure(text="DURDUR", fg_color="#e67e22")
            self.sw_tick()
        else:
            self.sw_running = False
            self.btn_sw_main.configure(text="BAŞLAT", fg_color="#27ae60")

    def sw_tick(self):
        if self.sw_running:
            self.sw_elapsed = time.time() - self.sw_start_time
            m, s = divmod(self.sw_elapsed, 60)
            h, m = divmod(m, 60)
            self.lbl_sw.configure(text=f"{int(h):02d}:{int(m):02d}:{int(s):02d}.{int((s % 1) * 100):02d}")
            self.after(40, self.sw_tick)

    def add_lap(self):
        if self.sw_running:
            ctk.CTkLabel(self.lap_box, text=f"Tur: {self.lbl_sw.cget('text')}", font=("Arial", 14)).pack(pady=2)

    def reset_sw(self):
        self.sw_running = False
        self.sw_elapsed = 0
        self.lbl_sw.configure(text="00:00:00.00")
        for child in self.lap_box.winfo_children(): child.destroy()


if __name__ == "__main__":
    app = ModernUltraApp()
    app.mainloop()