"""
Callbacks package - registers all callbacks with the app
"""
from callbacks.data_callbacks import register_data_callbacks
from callbacks.download_callbacks import register_download_callbacks
from callbacks.ui_callbacks import register_ui_callbacks


def register_callbacks(app):
    """Register all callbacks with the app"""
    register_data_callbacks(app)
    register_download_callbacks(app)
    register_ui_callbacks(app)
