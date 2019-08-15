#Object Oriented Programming
#Navegação entre páginas
import tkinter as tk
from tkinter import ttk

LARGE_FONT= ("Nexa", 12)

screen_y = 200
screen_x = 200

class Vistools(tk.Tk) :
#classe principal, adiciona toda a logica "controller"
  def __init__(self, *args, **kwargs):

    tk.Tk.__init__(self, *args, **kwargs)
    tk.Tk.iconbitmap(self, default=r"E:\Google Drive\Scripts\vistools\resources\teste.ico")
    tk.Tk.wm_title(self, "TESTE :O")

    container = tk.Frame(self)

    container.pack(side="top", fill="both", expand = True)

    container.grid_rowconfigure(0, weight = 1, )
    container.grid_columnconfigure(0, weight = 1, )

    self.frames = {}

    for F in (StartPage, PageOne, PageTwo):

      frame = F(container, self)

      self.frames[F] = frame

      frame.grid(row = 0, column = 0, sticky = "nsew")

    self.show_frame(StartPage)

  def show_frame(self, cont):

    frame = self.frames[cont]
    frame.tkraise()

def qf(stringtoprint):
  print(stringtoprint)



class StartPage(tk.Frame):

  def __init__(self, parent, controller):
    tk.Frame.__init__(self, parent)
    label = tk.Label(self, text="Start Page", font=LARGE_FONT)
    label.pack(pady=screen_y, padx=screen_x)

    button1 = ttk.Button(self, text = "Switch Page", command=lambda: controller.show_frame(PageOne))
    button1.pack()
    





class PageOne(tk.Frame):

  def __init__(self, parent, controller):
    tk.Frame.__init__(self, parent)
    label = tk.Label(self, text="Second Page", font=LARGE_FONT)
    label.pack(pady=screen_y, padx=screen_x)

    button1 = ttk.Button(self, text = "Home", command=lambda: controller.show_frame(StartPage))
    button1.pack()

    button2 = ttk.Button(self, text = "Next", command=lambda: controller.show_frame(PageTwo))
    button2.pack()

    
class PageTwo(tk.Frame):

  def __init__(self, parent, controller):
    tk.Frame.__init__(self, parent)
    label = tk.Label(self, text="Third Page", font=LARGE_FONT)
    label.pack(pady=screen_y, padx=screen_x)

    button1 = ttk.Button(self, text = "Home", command=lambda: controller.show_frame(StartPage))
    button1.pack()

    button2 = ttk.Button(self, text = "Previous Page", command=lambda: controller.show_frame(PageOne))
    button2.pack()

    


app = Vistools()
app.mainloop()
