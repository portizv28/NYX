import tkinter as tk
import math


class NyxOrb:

    def __init__(self):

        self.root = tk.Toplevel()

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        self.root.config(bg="magenta")
        self.root.wm_attributes("-transparentcolor", "magenta")

        # POSICIÓN VISIBLE (arriba izquierda)
        self.root.geometry("160x160+100+100")

        self.canvas = tk.Canvas(
            self.root,
            width=160,
            height=160,
            bg="magenta",
            highlightthickness=0
        )

        self.canvas.pack()

        # Halo
        self.glow = self.canvas.create_oval(
            30,
            30,
            130,
            130,
            fill="",
            outline="#00BFFF",
            width=10
        )

        # Núcleo
        self.circle = self.canvas.create_oval(
            50,
            50,
            110,
            110,
            fill="#00BFFF",
            outline=""
        )

        self.t = 0

        self.dx = 0
        self.dy = 0

        self.callback = None

        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<Double-Button-1>", self.abrir)
        self.canvas.bind("<B1-Motion>", self.drag)

        self.animate()

    def animate(self):

        self.t += 0.08

        escala = 1 + math.sin(self.t) * 0.05

        radio = 30 * escala

        self.canvas.coords(
            self.circle,
            80-radio,
            80-radio,
            80+radio,
            80+radio
        )

        halo = 50 + math.sin(self.t) * 3

        self.canvas.coords(
            self.glow,
            80-halo,
            80-halo,
            80+halo,
            80+halo
        )

        self.root.after(20, self.animate)

    def click(self, event):

        self.dx = event.x
        self.dy = event.y

    def abrir(self, event):

        if self.callback:
            self.callback()

    def drag(self, event):

        x = self.root.winfo_x() + event.x - self.dx
        y = self.root.winfo_y() + event.y - self.dy

        self.root.geometry(f"+{x}+{y}")

    def set_callback(self, callback):

        self.callback = callback

    def dormir(self):

        self.canvas.itemconfig(self.circle, fill="black")
        self.canvas.itemconfig(self.glow, outline="#333333")

    def escuchar(self):

        self.canvas.itemconfig(self.circle, fill="orange")
        self.canvas.itemconfig(self.glow, outline="orange")

    def pensar(self):

        self.canvas.itemconfig(self.circle, fill="yellow")
        self.canvas.itemconfig(self.glow, outline="yellow")

    def hablar(self):

        self.canvas.itemconfig(self.circle, fill="lime")
        self.canvas.itemconfig(self.glow, outline="lime")

    def normal(self):

        self.canvas.itemconfig(self.circle, fill="#00BFFF")
        self.canvas.itemconfig(self.glow, outline="#00BFFF")

    def ocultar(self):

        self.root.withdraw()

    def mostrar(self):

        self.root.deiconify()
        