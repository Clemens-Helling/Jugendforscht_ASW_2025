import tkinter as tk
from tkinter import ttk
root = tk.Tk()
style = ttk.Style()
root.title("Hello World!")
root.geometry("800x400")
root.minsize(400, 200)
root.maxsize(1200, 800)	
label = ttk.Label(root, text="Hello World!", background="yellow")
label.pack()
#for item in label.keys():
  #print(item, ":", label[item])

root.mainloop()
