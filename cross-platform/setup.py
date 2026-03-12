from setuptools import setup

setup(
    name="tMUG",
    version="1.0.0",
    description="tMUG - Tailscale Multi-platform User GUI",
    author="DEC-LLC (Diwan Enterprise Consulting LLC)",
    license="MIT",
    py_modules=["tailscale_manager"],
    install_requires=[
        "PyQt5",
    ],
    entry_points={
        "gui_scripts": [
            "tmug=tailscale_manager:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: System :: Networking",
    ],
)
