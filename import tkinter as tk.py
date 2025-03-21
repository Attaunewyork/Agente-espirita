import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

class StandCreator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Crie Seu Stand - JoJo's Bizarre Adventure")
        self.geometry('900x600')
        self.config(bg='#232323')

        self.parts = {
            'Cabelo': ['Cabelo do Jotaro', 'Cabelo do Dio', 'Cabelo do Giorno'],
            'Rosto': ['Rosto do Star Platinum', 'Rosto do The World', 'Rosto do Killer Queen'],
            'Corpo': ['Corpo musculoso', 'Corpo magro', 'Corpo mecânico'],
            'Pernas': ['Pernas rápidas', 'Pernas fortes', 'Pernas robóticas'],
            'Pés': ['Pés ágeis', 'Pés pesados', 'Pés voadores']
        }

        self.selected_parts = {}
        self.images = {}

        self.create_ui()

    def create_ui(self):
        ttk.Label(self, text="Crie Seu Stand", font=('Arial', 20), background='#232323', foreground='white').pack(pady=20)

        container = ttk.Frame(self)
        container.pack(side='left', fill='y', padx=10)

        display_frame = ttk.Frame(self)
        display_frame.pack(side='right', expand=True, fill='both', padx=10)

        self.display_area = tk.Text(display_frame, font=('Arial', 12), state='disabled', bg='#111111', fg='white', height=10)
        self.display_area.pack(expand=False, fill='x', pady=10)

        self.canvas = tk.Canvas(display_frame, bg='#111111', width=400, height=400)
        self.canvas.pack(expand=True)

        for part, options in self.parts.items():
            label = ttk.Label(container, text=part, background='#232323', foreground='white', font=('Arial', 12, 'bold'))
            label.pack(anchor='w', pady=5)

            combo = ttk.Combobox(container, values=options, state="readonly")
            combo.pack(anchor='w', pady=5)
            combo.bind("<<ComboboxSelected>>", lambda e, p=part, c=combo: self.select_part(p, c.get()))

        create_btn = ttk.Button(container, text="Finalizar Stand", command=self.finalize_stand)
        create_btn.pack(pady=20)

        reset_btn = ttk.Button(container, text="Resetar", command=self.reset_stand)
        reset_btn.pack(pady=10)

    def select_part(self, part, choice):
        self.selected_parts[part] = choice
        self.update_display()

    def update_display(self):
        self.display_area.config(state='normal')
        self.display_area.delete('1.0', tk.END)
        self.display_area.insert(tk.END, 'Seu Stand atual:\n\n')

        for part in self.parts:
            choice = self.selected_parts.get(part, "Não selecionado")
            self.display_area.insert(tk.END, f'{part}: {choice}\n')

        self.display_area.config(state='disabled')

    def finalize_stand(self):
        if len(self.selected_parts) < len(self.parts):
            messagebox.showwarning("Stand Incompleto", "Por favor, selecione todos os acessórios para criar seu stand!")
        else:
            self.display_stand_image()
            messagebox.showinfo("Stand Criado!", "Seu stand foi criado com sucesso! Veja a imagem!")

    def display_stand_image(self):
        self.canvas.delete("all")
        order = ['Pés', 'Pernas', 'Corpo', 'Rosto', 'Cabelo']

        for part in order:
            img_path = self.selected_parts[part] + ".png"
            try:
                img = Image.open(img_path).resize((400, 400), Image.LANCZOS)
                self.images[part] = ImageTk.PhotoImage(img)
                self.canvas.create_image(200, 200, image=self.images[part])
            except FileNotFoundError:
                print(f"Aviso: Imagem {img_path} não encontrada, pulando.")
                continue

    def reset_stand(self):
        self.selected_parts.clear()
        self.update_display()
        self.canvas.delete("all")

if __name__ == "__main__":
    app = StandCreator()
    app.mainloop()
