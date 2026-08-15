FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./

RUN python -c 'import tomllib, subprocess, sys; deps = tomllib.load(open("pyproject.toml", "rb"))["project"]["dependencies"]; subprocess.check_call([sys.executable, "-m", "pip", "install", *deps])'

COPY day23.py dep_test.py config.json ./

CMD ["python", "dep_test.py"]
