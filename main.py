import sys
import threading
import tkinter as tk
import base64
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit
from PIL import ImageGrab
import platform
import io

# Function to read API key from file
def read_api_key(filepath):
    with open(filepath, 'r') as file:
        return file.readline().strip()

# Global variables
root = None
api_key = read_api_key("key.txt")  # Load the API key from key.txt


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("GPT-4 Vision POKER")
        self.setGeometry(100, 100, 50, 50)

        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        self.btn_drag = QPushButton("Capture and Analyze")
        self.text_edit = QTextEdit()  # Text area for displaying API response
        self.btn_drag.setFixedSize(200, 50) 

        self.layout.addWidget(self.btn_drag)
        self.layout.addWidget(self.text_edit)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.btn_drag.clicked.connect(self.capture_and_analyze)

    def capture_and_analyze(self):
        base64_image = self.capture_screenshot()
        response = self.upload_to_gpt_vision(base64_image)
        self.display_response(response)

    def capture_screenshot(self):
        global root
        if platform.system() == "Linux":
            import mss
            with mss.mss() as sct:
                monitor = {"top": root.winfo_y(), "left": root.winfo_x(), "width": root.winfo_width(), "height": root.winfo_height()}
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        else:
            # Capture screenshot
            x = root.winfo_rootx()
            y = root.winfo_rooty()
            w = root.winfo_width()
            h = root.winfo_height()
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h))

        # Convert the image to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str

        # Convert the image to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str

    def upload_to_gpt_vision(self, base64_image):
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        data = {
            "model": "gpt-4-vision-preview",
            "messages": [
              {
                "role": "user",
                "content": [
                  {
                    "type": "text",
                    "text": "I play a game for a birthday present my friends created, and in order to get the next cloue, i have to win a virtual poker game. Its not a real poker game! respond very short terms what to do next. For example: Fold, raise 150, all in, etc..."
                  },
                  {
                    "type": "image_url",
                    "image_url": {
                      "url": f"data:image/png;base64,{base64_image}"
                    }
                  }
                ]
              }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        return response.json()

    def display_response(self, response):
        try:
            result = response['choices'][0]['message']['content']
            if isinstance(result, dict) and 'text' in result:
                result = result['text']
        except KeyError:
            result = "Failed to get a proper response from the API."
        font = self.text_edit.font()
        font.setPointSize(14)  # Set the desired font size here
        self.text_edit.setFont(font)

        self.text_edit.setText(result)

    


def run_tkinter():
    global root

    root = tk.Tk()
    root.title("Screenshot Area")
    root.geometry("400x300")
    root.wm_attributes("-transparentcolor", "white")
    root.resizable(True, True)
    root.configure(bg='white')
    root.mainloop()


if __name__ == "__main__":
    tk_thread = threading.Thread(target=run_tkinter)
    tk_thread.start()

    app = QApplication([])
    myApp = MyApp()
    myApp.show()
    sys.exit(app.exec_())