from setuptools import setup, find_packages

setup(
    name="webnify-bot",
    version="1.0.0",
    description="Telegram bot for Web-Nify payment services",
    author="Web-Nify",
    packages=find_packages(),
    install_requires=[
        'python-telegram-bot==20.3',
        'psycopg2-binary==2.9.6',
        'python-dotenv==1.0.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
