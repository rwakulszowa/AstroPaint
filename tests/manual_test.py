import subprocess

commands = [
    "python manage.py clear_db",
    "python manage.py clear_images",
    "python main.py ICOM21030 ICOM21030 ICOM21020 -i=3",
    "python main.py ICOM22030 ICOM22030 ICOM22020 -i=3",
    "python main.py IBY111010 IBY110010 IBY110020 -i=3",
    "python main.py IBHI01030 IBHI03030 IBHI06020 -i=3",
    "python main.py IBDP08040 IBDP08020 IBDP08030 -i=3",
    "python manage.py evaluate",
    "python main.py ICOM21030 ICOM21030 ICOM21020 -i=3",
    "python main.py ICOM22030 ICOM22030 ICOM22020 -i=3",
    "python main.py IBY111010 IBY110010 IBY110020 -i=3",
    "python main.py IBHI01030 IBHI03030 IBHI06020 -i=3",
    "python main.py IBDP08040 IBDP08020 IBDP08030 -i=3",
    "python manage.py evaluate",
    "python main.py ICOM21030 ICOM21030 ICOM21020",
    "python main.py ICOM22030 ICOM22030 ICOM22020",
    "python main.py IBY111010 IBY110010 IBY110020",
    "python main.py IBHI01030 IBHI03030 IBHI06020",
    "python main.py IBDP08040 IBDP08020 IBDP08030",
    "python manage.py evaluate"
    ]

for c in commands:
    subprocess.call(c)