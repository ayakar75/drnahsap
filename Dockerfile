# Pull official base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# GPG ve saat sorunları için update işlemini güvenlik doğrulaması kapalı şekilde yap
RUN apt-get -o Acquire::AllowInsecureRepositories=true \
            -o Acquire::AllowUnauthenticated=true \
            -o Acquire::Check-Valid-Until=false \
            update && \
    apt-get install -y --allow-unauthenticated \
        tzdata \
        ca-certificates \
        gnupg \
        libpq-dev \
        python3-dev \
        build-essential \
        postgresql-client && \
    ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Python ortamını kur
RUN pip install --upgrade pip && \
    pip install virtualenv && \
    python -m virtualenv $VIRTUAL_ENV

# Gereksinimleri yükle
COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Entrypoint scriptini kopyala ve hazırla
COPY entrypoint.sh /srv/entrypoint.sh
RUN sed -i 's/\r$//g' /srv/entrypoint.sh && chmod +x /srv/entrypoint.sh

# Uygulama dosyalarını kopyala
COPY . /srv/app
WORKDIR /srv/app

ENTRYPOINT ["/srv/entrypoint.sh"]