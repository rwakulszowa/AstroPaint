import subprocess

commands = [
    "python manage.py clear_db",
    "python manage.py clear_images",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -i=30 -k=CLUSTER",
    "python manage.py evaluate",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -i=20 -k=CLUSTER",
    "python manage.py evaluate",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -k=CLUSTER",
    "python manage.py evaluate",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -k=CLUSTER",
    "python manage.py evaluate",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -k=CLUSTER",
    "python manage.py evaluate",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -k=CLUSTER",
    "python manage.py evaluate",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -k=CLUSTER",
    "python manage.py evaluate",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -k=CLUSTER",
    "python manage.py evaluate",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -k=CLUSTER",
    "python manage.py evaluate",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -k=CLUSTER",
    "python manage.py evaluate",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -k=CLUSTER",
    "python manage.py evaluate",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -k=CLUSTER",
    "python manage.py evaluate",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -k=CLUSTER",
    "python manage.py evaluate",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -k=CLUSTER",
    "python manage.py evaluate",
    "python main.py J8OW01010 J8OW01010 J8OW02010 -k=CLUSTER",
    "python manage.py evaluate",
]


for c in commands:
    subprocess.call(c)