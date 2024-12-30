import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from exceptions import InvalidAmountError, InvalidCategoryError

# Создаем или подключаемся к базе данных
conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

# Таблица для хранения данных
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS transactions ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    category TEXT NOT NULL, 
    amount REAL NOT NULL, 
    type TEXT NOT NULL -- income или expense
) 
''')
conn.commit()


class FinanceApp:
    """
    Класс для управления финансовым учётом.

    Реализует функции добавления транзакций, загрузки данных из базы,
    а также построения графиков для визуализации расходов.
    """

    def __init__(self, root):
        """
        Инициализация приложения и его интерфейса.
        Включает валидацию аргументов конструктора.

        Args:
            root (tk.Tk): Основное окно приложения.

        Raises:
            ValueError: Если root не является экземпляром tk.Tk.
        """
        if not isinstance(root, tk.Tk):
            raise ValueError("root должен быть экземпляром tk.Tk")

        self.root = root
        self.root.title("Финансовый учет")
        self.root.geometry("800x600")
        self.root.configure(bg="#ffc0cb")  # Розовый фон для окна

        self.create_widgets()

    def create_widgets(self):
        """
        Создаёт виджеты для графического интерфейса пользователя.
        """
        # Верхняя панель для ввода данных
        frame_top = tk.Frame(self.root, pady=10, bg="#ffc0cb")
        frame_top.pack(fill=tk.X)

        tk.Label(frame_top, text="Категория:", bg="#ffc0cb").pack(side=tk.LEFT, padx=5)
        self.category_entry = ttk.Entry(frame_top)
        self.category_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(frame_top, text="Сумма:", bg="#ffc0cb").pack(side=tk.LEFT, padx=5)
        self.amount_entry = ttk.Entry(frame_top)
        self.amount_entry.pack(side=tk.LEFT, padx=5)

        self.type_var = tk.StringVar(value="expense")
        ttk.Radiobutton(frame_top, text="Расход", variable=self.type_var, value="expense").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_top, text="Доход", variable=self.type_var, value="income").pack(side=tk.LEFT, padx=5)

        ttk.Button(frame_top, text="Добавить", command=self.add_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_top, text="Показать диаграмму", command=self.show_chart).pack(side=tk.LEFT, padx=5)

        # Таблица для отображения данных
        self.tree = ttk.Treeview(self.root, columns=("#1", "#2", "#3"), show="headings", height=15)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        self.tree.heading("#1", text="Категория")
        self.tree.heading("#2", text="Сумма")
        self.tree.heading("#3", text="Тип")

        self.tree.column("#1", anchor=tk.W)
        self.tree.column("#2", anchor=tk.CENTER)
        self.tree.column("#3", anchor=tk.CENTER)

        self.load_transactions()

    def add_transaction(self):
        """
        Добавляет новую транзакцию в базу данных.

        Проверяет корректность введённых данных и обновляет отображение транзакций.

        Raises:
            InvalidAmountError: Если введена некорректная сумма.
            InvalidCategoryError: Если введена пустая категория.
        """
        category = self.category_entry.get().strip()
        try:
            amount = float(self.amount_entry.get().strip())
            if amount <= 0:
                raise InvalidAmountError("Сумма должна быть положительным числом.")
        except ValueError:
            raise InvalidAmountError("Введите корректную сумму.")

        if not category:
            raise InvalidCategoryError("Введите категорию.")

        t_type = self.type_var.get()

        cursor.execute("INSERT INTO transactions (category, amount, type) VALUES (?, ?, ?)", (category, amount, t_type))
        conn.commit()

        self.category_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

        self.load_transactions()

    def load_transactions(self):
        """
        Загружает все транзакции из базы данных и отображает их в таблице.
        """
        for row in self.tree.get_children():
            self.tree.delete(row)

        cursor.execute("SELECT category, amount, type FROM transactions")
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)

    def show_chart(self):
        """
        Отображает диаграмму расходов.

        Диаграмма показывает, сколько средств потрачено на каждую категорию.

        Raises:
            ValueError: Если нет данных для отображения диаграммы.
        """
        cursor.execute("SELECT category, SUM(amount) FROM transactions WHERE type='expense' GROUP BY category")
        expenses = cursor.fetchall()

        if not expenses:
            raise ValueError("Нет данных для отображения диаграммы.")

        categories = [row[0] for row in expenses]
        amounts = [row[1] for row in expenses]

        fig, ax = plt.subplots()
        ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.set_title("Диаграмма расходов")

        # Встраивание диаграммы в окно Tkinter
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Диаграмма")

        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
