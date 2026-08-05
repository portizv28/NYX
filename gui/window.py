import tkinter as tk
from tkinter import scrolledtext


class NyxWindow:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title("NYX")
        self.root.geometry("900x600")
        self.root.configure(bg="#050505")


        # Título

        self.title = tk.Label(
            self.root,
            text="NYX",
            fg="white",
            bg="#050505",
            font=("Segoe UI", 34, "bold")
        )

        self.title.pack(pady=20)



        # Núcleo de NYX

        self.canvas = tk.Canvas(
            self.root,
            width=900,
            height=130,
            bg="#050505",
            highlightthickness=0
        )

        self.canvas.pack()


        self.circle = self.canvas.create_oval(
            420,
            20,
            480,
            80,
            fill="#00BFFF",
            outline=""
        )



        # Caja de conversación

        self.chat = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            width=80,
            height=15,
            bg="#101010",
            fg="white",
            font=("Segoe UI", 12),
            insertbackground="white"
        )

        self.chat.pack(
            padx=40,
            pady=10
        )

        self.chat.config(
            state="disabled"
        )



        # Entrada de texto

        self.entry = tk.Entry(
            self.root,
            font=("Segoe UI", 16),
            width=50
        )

        self.entry.pack(
            side="left",
            padx=40,
            pady=15
        )


        self.entry.bind(
            "<Return>",
            lambda event: self.enviar()
        )


        self.entry.focus()



        # Botón enviar

        self.button = tk.Button(
            self.root,
            text="Enviar",
            font=("Segoe UI", 12),
            command=self.enviar
        )

        self.button.pack(
            side="left"
        )



        # Botón voz

        self.voice_button = tk.Button(
            self.root,
            text="🎤",
            font=("Segoe UI", 12),
            command=self.escuchar
        )

        self.voice_button.pack(
            side="left",
            padx=10
        )


        self.growing = True

        self.animate()



    def animate(self):

        x1, y1, x2, y2 = self.canvas.coords(
            self.circle
        )


        if self.growing:

            self.canvas.coords(
                self.circle,
                x1-0.3,
                y1-0.3,
                x2+0.3,
                y2+0.3
            )

            if x1 < 410:
                self.growing = False

        else:

            self.canvas.coords(
                self.circle,
                x1+0.3,
                y1+0.3,
                x2-0.3,
                y2-0.3
            )

            if x1 > 420:
                self.growing = True


        self.root.after(
            20,
            self.animate
        )



    def escribir_chat(self, texto):

        self.chat.config(
            state="normal"
        )

        self.chat.insert(
            "end",
            texto + "\n\n"
        )

        self.chat.see(
            "end"
        )

        self.chat.config(
            state="disabled"
        )



    def set_callback(self, callback):

        self.callback = callback



    def set_voice_callback(self, callback):

        self.voice_callback = callback



    def enviar(self):

        texto = self.entry.get()


        if texto.strip() == "":
            return


        self.entry.delete(
            0,
            "end"
        )


        self.escribir_chat(
            "Tú:\n" + texto
        )


        if hasattr(self, "callback"):

            respuesta = self.callback(texto)

            self.escribir_chat(
                "NYX:\n" + respuesta
            )



    def escuchar(self):

        if hasattr(self, "voice_callback"):

            self.voice_callback()



    def cambiar_color(self, color):

        self.canvas.itemconfig(
            self.circle,
            fill=color
        )



    def cambiar_estado(self, texto):

        self.escribir_chat(
            "NYX:\n" + texto
        )



    def run(self):

        self.root.mainloop()
        