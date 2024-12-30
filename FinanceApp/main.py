from Finance_App import *


if __name__ == "__main__":
    """
    Основной файл приложения.

    Создаёт окно приложения и запускает главный цикл Tkinter.
    """
    root = tk.Tk()
    try:
        app = FinanceApp(root)
        root.mainloop()
    except ValueError as e:
        messagebox.showerror("Ошибка", str(e))
    except FinanceAppError as e:
        messagebox.showerror("Ошибка приложения", str(e))
    finally:
        # Закрываем соединение с базой данных при выходе
        conn.close()
