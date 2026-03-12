from setuptools import setup

setup(
    name="tailscale-manager",
    version="1.0.0",
    description="Cross-platform GUI for managing Tailscale VPN connections",
    author="DEC-LLC (Diwan Enterprise Consulting LLC)",
    license="MIT",
    py_modules=["tailscale_manager"],
    install_requires=[
        "PyQt5",
    ],
    entry_points={
        "gui_scripts": [
            "tailscale-manager=tailscale_manager:main",
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
