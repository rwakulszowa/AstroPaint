import subprocess


commands = [
    "python manage.py clear_db",
    "python manage.py clear_images",
    "python main.py J9BB04030 J9BB04010 J9BB04020 -i=5 -k=GALAXY",
    "python main.py J8D602010 J8D602020 J8D602030 -i=5 -k=GALAXY",
    "python main.py J9FL01010 J9FL01020 J9FL01030 -i=5 -k=GALAXY",
    "python main.py J9FB01040 J9FB01010 J9FB01020 -i=5 -k=GALAXY",
    "python main.py J8LW03030 J8LW03010 J8LW03020 -i=5 -k=GALAXY",
    "python main.py J96R23010 J96R23020 J96R23030 -i=5 -k=GALAXY",
    "python manage.py evaluate",
    "python main.py J9BB04030 J9BB04010 J9BB04020 -i=5 -k=GALAXY",
    "python main.py J8D602010 J8D602020 J8D602030 -i=5 -k=GALAXY",
    "python main.py J9FL01010 J9FL01020 J9FL01030 -i=5 -k=GALAXY",
    "python main.py J9FB01040 J9FB01010 J9FB01020 -i=5 -k=GALAXY",
    "python main.py J8LW03030 J8LW03010 J8LW03020 -i=5 -k=GALAXY",
    "python main.py J96R23010 J96R23020 J96R23030 -i=5 -k=GALAXY",
    "python manage.py evaluate",
    "python main.py J9BB04030 J9BB04010 J9BB04020 -k=GALAXY",
    "python main.py J8D602010 J8D602020 J8D602030 -k=GALAXY",
    "python main.py J9FL01010 J9FL01020 J9FL01030 -k=GALAXY",
    "python main.py J9FB01040 J9FB01010 J9FB01020 -k=GALAXY",
    "python main.py J8LW03030 J8LW03010 J8LW03020 -k=GALAXY",
    "python main.py J96R23010 J96R23020 J96R23030 -k=GALAXY",
    "python manage.py evaluate",
    "python main.py J9BB04030 J9BB04010 J9BB04020 -k=GALAXY",
    "python main.py J8D602010 J8D602020 J8D602030 -k=GALAXY",
    "python main.py J9FL01010 J9FL01020 J9FL01030 -k=GALAXY",
    "python main.py J9FB01040 J9FB01010 J9FB01020 -k=GALAXY",
    "python main.py J8LW03030 J8LW03010 J8LW03020 -k=GALAXY",
    "python main.py J96R23010 J96R23020 J96R23030 -k=GALAXY",
    "python manage.py evaluate",
    "python main.py J9BB04030 J9BB04010 J9BB04020 -k=GALAXY",
    "python main.py J8D602010 J8D602020 J8D602030 -k=GALAXY",
    "python main.py J9FL01010 J9FL01020 J9FL01030 -k=GALAXY",
    "python main.py J9FB01040 J9FB01010 J9FB01020 -k=GALAXY",
    "python main.py J8LW03030 J8LW03010 J8LW03020 -k=GALAXY",
    "python main.py J96R23010 J96R23020 J96R23030 -k=GALAXY",
    "python manage.py evaluate",
    "python main.py J9BB04030 J9BB04010 J9BB04020 -k=GALAXY",
    "python main.py J8D602010 J8D602020 J8D602030 -k=GALAXY",
    "python main.py J9FL01010 J9FL01020 J9FL01030 -k=GALAXY",
    "python main.py J9FB01040 J9FB01010 J9FB01020 -k=GALAXY",
    "python main.py J8LW03030 J8LW03010 J8LW03020 -k=GALAXY",
    "python main.py J96R23010 J96R23020 J96R23030 -k=GALAXY",
    "python main.py J93S01010 J93S01020 J93S02010 -k=GALAXY",
    "python main.py J91K10060 J91K10080 J91K10070 -k=GALAXY",
    "python main.py J9EE02010 J9CB07020 J9CB09010 -k=GALAXY",
    "python manage.py evaluate",
]


for c in commands:
    subprocess.call(c)