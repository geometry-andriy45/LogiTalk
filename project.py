import base64
import io
import threading
from random import randint
from socket import socket, AF_INET, SOCK_STREAM
from PIL import Image
from customtkinter import *

set_appearance_mode("System")
set_default_color_theme("blue")

HOST = '127.0.0.1'
PORT = 8080


class MainWindow(CTk):
    def __init__(self):
        super().__init__()

        self.geometry('950x650')
        self.minsize(650, 480)
        self.title("Chat Client")

        self.username = "User_" + str(randint(100, 999))
        self.loaded_images = []

        self.accent_color = "#3b8ed0"
        self.my_bubble_dark = "#2b4c7e"
        self.my_bubble_light = "#d0e1fd"

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.menu_frame = CTkFrame(self, width=60, corner_radius=0)
        self.menu_frame.grid(row=0, column=0, sticky="nsew")
        self.menu_frame.grid_rowconfigure(8, weight=1)

        self.is_menu_expanded = False

        self.toggle_btn = CTkButton(
            self.menu_frame, text="☰", width=40, height=40,
            command=self.toggle_menu, font=("Arial", 18)
        )
        self.toggle_btn.grid(row=0, column=0, padx=10, pady=15, sticky="w")

        self.init_menu_widgets()

        self.chat_container = CTkFrame(self, fg_color="transparent")
        self.chat_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.chat_container.grid_columnconfigure(0, weight=1)
        self.chat_container.grid_rowconfigure(0, weight=1)

        self.chat_field = CTkScrollableFrame(self.chat_container)
        self.chat_field.grid(row=0, column=0, sticky="nsew", padx=5, pady=(0, 10))
        self.chat_field.grid_columnconfigure(0, weight=1)

        self.input_frame = CTkFrame(self.chat_container, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=5)
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.message_entry = CTkEntry(
            self.input_frame, placeholder_text='Введіть повідомлення...', height=45, font=("Arial", 14)
        )
        self.message_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        self.open_img_button = CTkButton(
            self.input_frame, text='📷', width=45, height=45, command=self.open_image, font=("Arial", 16)
        )
        self.open_img_button.grid(row=0, column=1, padx=(0, 5))

        self.send_button = CTkButton(
            self.input_frame, text='➤', width=55, height=45, command=self.send_message, font=("Arial", 16),
            fg_color=self.accent_color
        )
        self.send_button.grid(row=0, column=2)

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((HOST, PORT))

            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))

            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_system_message(f"Не вдалося підключитися до сервера: {e}")

    def init_menu_widgets(self):
        self.name_label = CTkLabel(self.menu_frame, text="Ваш нікнейм:", font=("Arial", 12, "bold"))
        self.name_entry = CTkEntry(self.menu_frame, placeholder_text="Нік...")
        self.save_name_btn = CTkButton(self.menu_frame, text="Зберегти нік", command=self.save_name,
                                       fg_color=self.accent_color)

        self.theme_label = CTkLabel(self.menu_frame, text="Режим інтерфейсу:", font=("Arial", 12, "bold"))
        self.theme_option = CTkOptionMenu(
            self.menu_frame, values=["Системна", "Темна", "Світла"], command=self.change_theme
        )

        self.color_label = CTkLabel(self.menu_frame, text="Акцентний колір:", font=("Arial", 12, "bold"))
        self.color_option = CTkOptionMenu(
            self.menu_frame, values=["Синій", "Смарагдовий", "Фіолетовий", "Помаранчевий"],
            command=self.change_accent_color
        )

        self.clear_btn = CTkButton(self.menu_frame, text="🧹 Очистити чат", fg_color="gray", hover_color="#555555",
                                   command=self.clear_chat)

    def toggle_menu(self):
        if self.is_menu_expanded:
            self.is_menu_expanded = False
            self.menu_frame.configure(width=60)
            self.toggle_btn.configure(text="☰")

            for widget in [self.name_label, self.name_entry, self.save_name_btn,
                           self.theme_label, self.theme_option, self.color_label,
                           self.color_option, self.clear_btn]:
                widget.grid_forget()
        else:
            self.is_menu_expanded = True
            self.menu_frame.configure(width=230)
            self.toggle_btn.configure(text="✕")

            self.name_label.grid(row=1, column=0, padx=15, pady=(10, 2), sticky="w")
            self.name_entry.grid(row=2, column=0, padx=15, pady=(0, 8), sticky="ew")
            self.save_name_btn.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")

            self.theme_label.grid(row=4, column=0, padx=15, pady=(5, 2), sticky="w")
            self.theme_option.grid(row=5, column=0, padx=15, pady=(0, 15), sticky="ew")

            self.color_label.grid(row=6, column=0, padx=15, pady=(5, 2), sticky="w")
            self.color_option.grid(row=7, column=0, padx=15, pady=(0, 15), sticky="ew")

            self.clear_btn.grid(row=8, column=0, padx=15, pady=(0, 15), sticky="ew")

    def change_theme(self, choice):
        if choice == "Темна":
            set_appearance_mode("Dark")
        elif choice == "Світла":
            set_appearance_mode("Light")
        else:
            set_appearance_mode("System")

    def change_accent_color(self, choice):
        colors = {
            "Синій": ("#3b8ed0", "#2b4c7e"),
            "Смарагдовий": ("#2fa572", "#1b5e3b"),
            "Фіолетовий": ("#8a2be2", "#4a1578"),
            "Помаранчевий": ("#f59e0b", "#8c530b")
        }
        if choice in colors:
            self.accent_color, self.my_bubble_dark = colors[choice]
            all_buttons = [
                self.send_button,
                self.save_name_btn,
                self.open_img_button,
                self.toggle_btn
            ]
            for btn in all_buttons:
                btn.configure(fg_color=self.accent_color)
            self.theme_option.configure(fg_color=self.accent_color)
            self.color_option.configure(fg_color=self.accent_color)

            self.add_system_message(f"Акцентний колір змінено на '{choice}'")

    def clear_chat(self):
        for widget in self.chat_field.winfo_children():
            widget.destroy()
        self.add_system_message("Історію чату очищено.")

    def save_name(self):
        new_name = self.name_entry.get().strip()
        if new_name:
            old_name = self.username
            self.username = new_name
            self.add_system_message(f"Нік змінено: {old_name} ➔ {self.username}")
            self.toggle_menu()

    def add_system_message(self, text):
        sys_lbl = CTkLabel(self.chat_field, text=text, text_color="gray", font=("Arial", 11, "italic"))
        sys_lbl.pack(pady=6, anchor="center")

    def add_message(self, author, text="", img=None, is_my_message=False):
        is_dark = get_appearance_mode() == "Dark"
        bubble_color = self.my_bubble_dark if is_my_message else ("#2b2b2b" if is_dark else "#e5e5e5")

        bubble_frame = CTkFrame(self.chat_field, fg_color=bubble_color, corner_radius=12)
        align = "e" if is_my_message else "w"
        bubble_frame.pack(pady=4, padx=10, anchor=align, fill="none")

        if not is_my_message and author:
            author_lbl = CTkLabel(bubble_frame, text=author, font=("Arial", 10, "bold"), text_color=self.accent_color)
            author_lbl.pack(anchor="w", padx=10, pady=(4, 0))

        if text:
            text_color = "white" if is_dark else ("white" if is_my_message else "black")
            text_lbl = CTkLabel(bubble_frame, text=text, wraplength=450, justify="left", font=("Arial", 13),
                                text_color=text_color)
            text_lbl.pack(anchor="w", padx=10, pady=(2, 0))

        if img:
            self.loaded_images.append(img)
            img_lbl = CTkLabel(bubble_frame, text="", image=img)
            img_lbl.pack(anchor="w", padx=10, pady=5)

    def send_message(self):
        message = self.message_entry.get().strip()
        if message:
            self.add_message(self.username, text=message, is_my_message=True)
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode('utf-8'))
            except Exception as e:
                self.add_system_message(f"Не вдалося надіслати: {e}")
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode('utf-8', errors='ignore')

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.after(0, lambda l=line.strip(): self.handle_line(l))
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return

        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                if message.startswith("[SYSTEM]"):
                    self.add_system_message(message.replace("[SYSTEM] ", ""))
                else:
                    self.add_message(author, text=message, is_my_message=False)

        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                b64_img = parts[3]
                try:
                    img_data = base64.b64decode(b64_img)
                    pil_img = Image.open(io.BytesIO(img_data))
                    ctk_img = CTkImage(light_image=pil_img, dark_image=pil_img, size=(220, 220))
                    self.add_message(author, img=ctk_img, is_my_message=False)
                except Exception as e:
                    self.add_system_message(f"Помилка завантаження фото від {author}: {e}")

    def open_image(self):
        file_name = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")])
        if not file_name:
            return
        try:
            with open(file_name, "rb") as f:
                raw = f.read()
            b64_data = base64.b64encode(raw).decode()
            short_name = os.path.basename(file_name)

            data = f"IMAGE@{self.username}@{short_name}@{b64_data}\n"
            self.sock.sendall(data.encode('utf-8'))

            pil_img = Image.open(file_name)
            ctk_img = CTkImage(light_image=pil_img, dark_image=pil_img, size=(220, 220))
            self.add_message(self.username, img=ctk_img, is_my_message=True)
        except Exception as e:
            self.add_system_message(f"Не вдалося надіслати зображення: {e}")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()