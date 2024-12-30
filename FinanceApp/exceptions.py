# exceptions.py

class FinanceAppError(Exception):
    """Базовый класс для всех ошибок в приложении."""
    pass

class InvalidAmountError(FinanceAppError):
    """Ошибка, если сумма транзакции некорректна (не число или отрицательное значение)."""
    pass

class InvalidCategoryError(FinanceAppError):
    """Ошибка, если категория транзакции пустая."""
    pass
