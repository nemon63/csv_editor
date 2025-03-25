from setuptools import setup, find_packages

setup(
    name="csv_editor",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'PyQt5>=5.15',
        'openpyxl>=3.0',
        'sqlite3>=3.35'  # Обычно входит в стандартную библиотеку
    ],
    python_requires='>=3.8',
)
