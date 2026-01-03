FROM public.ecr.aws/docker/library/python:3.11-slim
WORKDIR /app
COPY bot.py .
COPY requirements.txt .
RUN pip install -r requirements.txt 
CMD ["python", "bot.py"]
