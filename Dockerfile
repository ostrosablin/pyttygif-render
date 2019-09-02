FROM debian:bullseye

LABEL version="1.0"
LABEL description="pyttygif: Render ttyrecs into GIFs and videos"
LABEL maintainer="tmp6154@yandex.ru"

RUN apt-get update
RUN apt-get upgrade -y

# Install decent monospace fonts 
RUN apt-get install fonts-dejavu -y
RUN apt-get install fonts-noto -y

# Install x11-apps for xwd (X Window Dump), needed for screenshots
RUN apt-get install x11-apps -y

# Install imagemagick, so that we can convert xwd to GIF
RUN apt-get install imagemagick -y

# Install gifsicle to build GIF animations
RUN apt-get install gifsicle -y

# Install Xvfb, so that we can run GUI apps in headless mode
RUN apt-get install xvfb -y

# Install Konsole, which can be used as ttyrec rendering terminal
RUN apt-get install konsole -y

# Install ncurses-term, for the terminfo database
RUN apt-get install ncurses-term -y

# Install ffmpeg, so that we can make videos from GIFs
RUN apt-get install ffmpeg -y

# Install python 3 and pip3
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y

# Install pyttygif
RUN pip3 install pyttygif

# Write Konsole config
RUN mkdir -p /root/.config/
RUN printf '[KonsoleWindow]\n\
SaveGeometryOnExit=false\n' > /root/.config/konsolerc

# Install helper script
COPY pyttygif-render.py /usr/bin/pyttygif-render.py
RUN chmod +x /usr/bin/pyttygif-render.py

CMD ["-h"]
ENTRYPOINT ["/usr/bin/pyttygif-render.py"]
