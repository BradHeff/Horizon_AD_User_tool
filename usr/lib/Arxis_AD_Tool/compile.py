from setuptools import setup, Extension
from Cython.Build import cythonize

ext_modules = [
    Extension("Functions", ["Functions.py"]),
    Extension("GUI", ["Gui.py"]),
    Extension("AADT", ["Main.pyw"]),
    Extension("icons", ["icon.py"]),
]

setup(
    name="Arxis AD Tool",
    ext_modules=cythonize(ext_modules),
)
