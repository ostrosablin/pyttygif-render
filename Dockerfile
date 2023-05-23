FROM debian:bullseye

LABEL version="1.0"
LABEL description="pyttygif: Render ttyrecs into GIFs and videos"
LABEL maintainer="tmp6154@yandex.ru"

# Upgrade distro & install dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install fonts-dejavu \
    x11-apps \
    imagemagick \
    gifsicle \
    xvfb \
    konsole \
    ncurses-term \
    ffmpeg \
    python3 \
    python3-pip -y

# Install pyttygif and pyte
RUN pip3 install pyttygif pyte

# Write Konsole config
RUN mkdir -p /root/.config/
RUN printf '[KonsoleWindow]\n\
SaveGeometryOnExit=false\n' > /root/.config/konsolerc

# Install helper script
COPY pyttygif-render.py /usr/bin/pyttygif-render.py
RUN chmod +x /usr/bin/pyttygif-render.py

CMD ["-h"]
ENTRYPOINT ["/usr/bin/pyttygif-render.py"]
