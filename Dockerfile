FROM python:3.9.13 as builder
WORKDIR /app
COPY . .
RUN apt update && apt install patchelf
RUN pip install -U pip wheel setuptools pyopenssl uvicorn fastapi pyinstaller staticx scons
RUN pyinstaller -F certs.py
RUN staticx dist/certs dist/certs-static

FROM scratch
WORKDIR /app
COPY --from=builder /app/dist/certs-static /app/certs-static

