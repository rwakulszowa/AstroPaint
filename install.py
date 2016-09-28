import subprocess


if __name__ == "__main__":
    # Upgrade pip, fixes 99% of problems
    subprocess.run("pip install --upgrade pip", shell=True)

    # Install each package manually, fixes 1% of problems
    with open("./requirements.txt", 'r') as r:
        for l in r.readlines():
            if not(l.startswith('#') or not l.strip()):
                subprocess.run("pip install " + l, shell=True)
