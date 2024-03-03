import tkinter as tk
from itertools import cycle
from PIL import Image, ImageTk




class PhotoFrame(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # Set the size of the window
        self.geometry("1200x600")

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

        # Button to open the second window
        button = tk.Button(self, text="Open Second Window", command=self.open_second_window)  # Create button
        # button.pack(pady=20)  # Add button to the main window and specify padding
        button.place(x=1050, y=20)  # Position the button with an indentation of 200 pixels from the left and 40 pixels from the top
        # Button to open the second window
        button1 = tk.Button(self, text="Open Third Window", command=self.open_third_window)  # Create button
        # button1.pack(pady=40, padx=550)  # Add button to the main window and specify padding
        button1.place(x=1050, y=60)  # Position the button with an indentation of 200 pixels from the left and 40 pixels from the top
        # Start the animation
        self.animate()

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

    
if __name__ == "__main__":
    app = PhotoFrame()
    app.mainloop()

