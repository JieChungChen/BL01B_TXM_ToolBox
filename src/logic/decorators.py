"""Decorators for error handling and logging."""

import functools
from PyQt5.QtWidgets import QMessageBox


def handle_errors(title="Error"):
    """Decorator to handle exceptions and show error message boxes."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                QMessageBox.critical(self, title, error_msg)
                print(f"Error in {func.__name__}: {e}")
                import traceback
                traceback.print_exc()
        return wrapper
    return decorator
