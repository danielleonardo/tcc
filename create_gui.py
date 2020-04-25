import tkinter as tk
import pygame


class Alerta:
    sounda = None

    def __init__(self):
        pygame.mixer.init()
        root = tk.Tk()
        frame = tk.Frame(root)
        frame.pack()
        self.button2 = tk.Button(frame, text='stop', command=self.stop_sound)
        self.button2.pack(side=tk.LEFT)
        self.sounda= pygame.mixer.Sound("/Users/danielcosta/desenv/GitHub/tcc/Police-TheCristi95-214716303.wav")
        self.sounda.play()
        root.mainloop()

    def stop_sound(self):
        self.sounda.stop()
