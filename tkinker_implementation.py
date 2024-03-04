import tkinter as tk
from itertools import cycle
from PIL import Image, ImageTk, ImageFont
from tkinter import font

class CustomButton(tk.Button):
    def __init__(self, master=None, text="Button", x=0, y=0, command=None, font=("Comic Sans MS", 15), bg="light blue", fg='black', width=10, height=1):
        tk.Button.__init__(self, master, text=text, command=command, font=font, bg=bg, fg=fg, width=width, height=height)
        self.config(padx=0, pady=0)
        self.relief = "groove"
        self.borderwidth = 1
        self.place(x=x, y=y)

class PhotoFrame(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # Set the size of the window
        self.geometry("1200x600")


    def open_second_window(self):
        # Function to open the second window
        second_window = tk.Toplevel(self)  # Create a new Toplevel window
        second_window.title("Second Window")  # Set title for the second window
        second_window.geometry("200x100")  # Set geometry for the second window
        second_window.configure(background='white')  # Set background color for the second window


    def open_third_window(self):
        # Function to open the second window
        third_window = tk.Toplevel(self)  # Create a new Toplevel window
        third_window.title("third Window")  # Set title for the second window
        third_window.geometry("500x300")  # Set geometry for the second window
        third_window.configure(background='white')  # Set background color for the second window

    def fish(self):
         # Load images for normal fish movement (right)
        self.image_paths_right = ["C:\\Users\\Ira\\Downloads\\Fish12.png", "C:\\Users\\Ira\\Downloads\\Fish11.png", "C:\\Users\\Ira\\Downloads\\Fish10.png"]
        self.images_right = [Image.open(path) for path in self.image_paths_right]
        self.images_resized_right = [img.resize((100, 100)) for img in self.images_right]  # Resize images to 100x100
        self.photo_iter_right = cycle(ImageTk.PhotoImage(img) for img in self.images_resized_right)

        # Load images for fish movement left
        self.image_paths_left = ["C:\\Users\\Ira\\Downloads\\Fish13.png", "C:\\Users\\Ira\\Downloads\\Fish14.png", "C:\\Users\\Ira\\Downloads\\Fish15.png"]
        self.images_left = [Image.open(path) for path in self.image_paths_left]
        self.images_resized_left = [img.resize((100, 100)) for img in self.images_left]  # Resize images to 100x100
        self.photo_iter_left = cycle(ImageTk.PhotoImage(img) for img in self.images_resized_left)

        # Set initial position and direction
        self.position = 0
        self.direction = 1

        # Set up the label to display the images
        self.label = tk.Label(self)
        self.label.pack()

        self.animate()

    def animate(self):
        # Move the fish image horizontally
        self.position += self.direction * 10  # Change this value to adjust the speed
        if self.position >= 1100:
            self.direction = -1
        elif self.position <= 0:
            self.direction = 1

        # Determine which set of images to use based on direction
        if self.direction == 1:
            photo = next(self.photo_iter_right)
        else:
            photo = next(self.photo_iter_left)

        self.label.config(image=photo)
        self.label.image = photo

        # Move the fish image to the new position
        self.label.place(x=self.position, y=250)

        # Schedule the next animation
        self.after(100, self.animate)  # Change animation speed as needed



    def add_right_bar_buttons(self):

         # Button to open the second window
        button = tk.Button(self, text="Open Second Window", command=self.open_second_window)  # Create button
        button.place(x=1050, y=20)  # Position the button with an indentation of 200 pixels from the left and 40 pixels from the top

        # Button to open the third window
        button1 = tk.Button(self, text="Open Third Window", command=self.open_third_window)  # Create button
        button1.place(x=1050, y=60)  # Position the button with an indentation of 200 pixels from the left and 40 pixels from the top

        # Start the animation
        # self.animate()

        # Create a custom button
        CustomButton(self, text="Manage Fish", x=10, y=10, command=lambda: print("Кнопка нажата!"))


if __name__ == "__main__":
    app = PhotoFrame()
    app.add_right_bar_buttons()
    app.fish()
    # app.animate()
    app.mainloop()

