FROM python:latest

#:3.10.3-slim-bullseye

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN apt-get update && apt-get install -y \
        dialog apt-utils \
    && apt-get clean \
    && echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update && apt-get install -y \
        build-essential pkg-config cmake git wget \
        autotools-dev autoconf \
        cython3 python3-dev python3-setuptools \
        libncurses5-dev libreadline-dev nettle-dev libcppunit-dev \
        libgnutls28-dev libuv1-dev libjsoncpp-dev libargon2-dev \
        libssl-dev libfmt-dev libhttp-parser-dev libasio-dev libmsgpack-dev \
    && apt-get clean

RUN git clone --depth 1 https://github.com/savoirfairelinux/opendht.git
RUN pip3 install --upgrade cython
RUN cd opendht && mkdir build && cd build \
	&& cmake .. -DCMAKE_INSTALL_PREFIX=/usr -DOPENDHT_PYTHON=On -DOPENDHT_LTO=On -DOPENDHT_PROXY_SERVER=Off -DOPENDHT_PROXY_CLIENT=Off && make -j8 && make install \
	&& cd ../.. && rm -rf opendht


# System deps:
RUN pip install poetry

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Creating folders, and files for a project:
# COPY . /code
RUN echo "\nalias spm=\"poetry run python spm/__main__.py\"" >> ~/.bashrc
ENTRYPOINT ["poetry", "run", "python", "example.py", "pip", "install", "numpy"]