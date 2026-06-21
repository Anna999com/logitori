import threading

from customtkinter import *
from socket import *


class MainWindow(CTk):
    def __init__(self):
        super().__init__()

        self.geometry('400x300')
        self.title('LogiTalk')

        # Ім'я користувача
        self.username = 'Artem'

        self.label = None
        self.entry = None

        # ------------------- SOCKET -------------------

        # Створюємо клієнтський сокет
        self.sock = socket(AF_INET, SOCK_STREAM)

        # Підключаємося до сервера
        self.sock.connect(('0.tcp.eu.ngrok.io', 10453))

        threading.Thread(
            target=self.recv_message,
            daemon=True
        ).start()

        # ------------------- MENU -------------------

        self.menu_frame = CTkFrame(self, width=30, height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)

        self.is_show_menu = False
        self.speed_animate_menu = -5

        self.btn = CTkButton(
            self,
            text='▶️',
            command=self.toggle_show_menu,
            width=30
        )
        self.btn.place(x=0, y=0)

        # ------------------- MAIN -------------------

        # Поле чату (тільки для читання)
        self.chat_field = CTkTextbox(
            self,
            font=('Arial', 14),
            state='disabled'
        )
        self.chat_field.place(x=0, y=0)

        # Поле введення повідомлення
        self.message_entry = CTkEntry(
            self,
            placeholder_text='Введіть повідомлення:',
            height=40
        )
        self.message_entry.place(x=0, y=0)

        # Кнопка надсилання повідомлення
        self.send_button = CTkButton(
            self,
            text='>',
            width=50,
            height=40,
            command=self.send_message
        )
        self.send_button.place(x=0, y=0)

        self.adaptive_ui()

    # ------------------- РОБОТА З ПОВІДОМЛЕННЯМИ -------------------

    def add_message(self, text):
        """
        Додає повідомлення в чат
        """

        # Тимчасово розблоковуємо TextBox
        self.chat_field.configure(state='normal')

        # Додаємо текст в кінець чату
        self.chat_field.insert(
            END,
            text + '\n'
        )

        self.chat_field.see(END)

        # Знову блокуємо TextBox
        self.chat_field.configure(state='disabled')

    def send_message(self):
        """
        Надсилання повідомлення
        """

        # Отримуємо текст із поля вводу
        message = self.message_entry.get()

        if message:

            # Показуємо повідомлення у своєму чаті
            self.add_message(
                f'{self.username}: {message}'
            )

            # Формуємо повідомлення для сервера
            data = f"TEXT@{self.username}@{message}\n"

            try:
                # Відправляємо повідомлення серверу
                self.sock.sendall(
                    data.encode()
                )

            except:
                pass

        # Очищаємо поле вводу
        self.message_entry.delete(0, END)


    # постійно слухаємо сервер
    def recv_message(self):

        buffer = ""

        while True:

            try:

                chunk = self.sock.recv(4096)

                if not chunk:
                    break

                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)

                    self.handle_line(
                        line.strip()
                    )

            except:
                break

        self.sock.close()

    # обробляємо повідомлення від сервера
    def handle_line(self, line):

        if not line:
            return

        parts = line.split("@", 3)

        msg_type = parts[0]

        if msg_type == "TEXT":

            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]

                self.add_message(
                    f"{author}: {message}"
                )

    # ------------------- MENU -------------------

    def toggle_show_menu(self):

        if self.is_show_menu:

            self.is_show_menu = False

            # Змінюємо напрям анімації
            self.speed_animate_menu *= -1

            self.btn.configure(text='▶️')

            self.show_menu()

        else:

            self.is_show_menu = True

            # Змінюємо напрям анімації
            self.speed_animate_menu *= -1

            self.btn.configure(text='◀️')

            self.show_menu()

            # Віджети меню

            self.label = CTkLabel(
                self.menu_frame,
                text='Імʼя'
            )
            self.label.pack(pady=30)

            self.entry = CTkEntry(
                self.menu_frame
            )
            self.entry.pack()

    def show_menu(self):

        # Змінюємо ширину меню
        self.menu_frame.configure(
            width=self.menu_frame.winfo_width() +
                  self.speed_animate_menu
        )

        # Відкриття меню
        if self.menu_frame.winfo_width() < 200 and self.is_show_menu:

            self.after(
                10,
                self.show_menu
            )

        # Закриття меню
        elif self.menu_frame.winfo_width() > 40 and not self.is_show_menu:

            self.after(
                10,
                self.show_menu
            )

            if self.label:
                self.label.destroy()
                self.label = None

            if self.entry:
                self.entry.destroy()
                self.entry = None

    # ------------------- ADAPTIVE UI -------------------

    def adaptive_ui(self):

        # Висота меню дорівнює висоті вікна
        self.menu_frame.configure(
            height=self.winfo_height()
        )

        # Розташування чату
        self.chat_field.place(
            x=self.menu_frame.winfo_width(),
            y=0
        )

        self.chat_field.configure(
            width=self.winfo_width() -
                  self.menu_frame.winfo_width(),

            height=self.winfo_height() - 40
        )

        # Кнопка надсилання
        self.send_button.place(
            x=self.winfo_width() - 50,
            y=self.winfo_height() - 40
        )

        # Поле введення
        self.message_entry.place(
            x=self.menu_frame.winfo_width(),
            y=self.send_button.winfo_y()
        )

        self.message_entry.configure(
            width=self.winfo_width()
                  - self.menu_frame.winfo_width()
                  - self.send_button.winfo_width()
        )

        # Оновлюємо інтерфейс кожні 50 мс
        self.after(
            50,
            self.adaptive_ui
        )


win = MainWindow()
win.mainloop()