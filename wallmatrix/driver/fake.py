import threading
from PIL import Image

try:
    import tkinter as tk
    from PIL import ImageTk
except ImportError:
    tk = None


from wallmatrix.driver import MatrixDriver


class FakeMatrixApp(threading.Thread):
    def quit(self):
        self.root.quit()

    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.image_label = tk.Label(self.root)
        self.image_label.pack()

        self.root.mainloop()

    def update_image(self, image):
        resized_image = image.resize((800, 400), Image.NEAREST)

        self.image_tk = ImageTk.PhotoImage(resized_image)
        self.image_label.configure(image=self.image_tk)


class FakeMatrixDriver(MatrixDriver):
    def setup(self):
        self.app = FakeMatrixApp()
        self.app.start()

    def update_image(self):
        self.app.update_image(self.image)
