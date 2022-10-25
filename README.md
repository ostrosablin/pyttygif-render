# pyttygif-render

## Convert ttyrec to GIFs or MP4 files

This project prepares a Docker image with a pyttygif-render script, which is basically a wrapper around [pyttygif](https://github.com/tmp6154/pyttygif) and it leverages several other tools, such as Xvfb and Konsole, to allow user to easily convert a ttyrec file into GIF animations and MP4 videos, even on headless servers. Image is based on Debian Bullseye.

For the description of original pyttygif, see it's [project page](https://github.com/tmp6154/pyttygif).

You can install the latest build of this image by running `docker pull tmp6154/pyttygif-render`.

## Basic usage example

Let's assume you want to convert a `sample.ttyrec` in the current directory into GIF:

    docker run -v $PWD:/test tmp6154/pyttygif-render /test/sample.ttyrec /test/sample.gif

This would produce a `sample.gif` in the current directory, converted with default settings.

## Customizing the conversion

You can see the full usage help by running container without options:

    usage: pyttygif-render.py [-h] [--screen-size SCREEN_SIZE] [--no-antialias]
                              [--bold-intense] [--color-scheme COLOR_SCHEME]
                              [--font FONT] [-S FONT_SIZE]
                              [--font-family FONT_FAMILY] [--font-linechars]
                              [--cursor-shape {0,1,2}] [-W WIDTH] [-H HEIGHT]
                              [-s SPEED] [-l LOOP] [-L LASTFRAME] [-o {0,1,2,3}]
                              [-f FPS] [-c DELAYCAP] [-x LOSSY] [-e ENCODING]
                              [-C [LOGARITHMIC]] [-v] [--video-only] [--crf CRF]
                              [--tune TUNE] [--preset PRESET] [-r FRAMERATE]
                              input output
    
    pyttygif-render - Convert a ttyrec to GIF/MP4 animation
    
    options:
      -h, --help            show this help message and exit
    
    Xvfb settings:
      --screen-size SCREEN_SIZE
                            Screen size to use for virtual X server
    
    Konsole visualization settings:
      --no-antialias        Disable font antialiasing
      --bold-intense        Use bold font with bright colors
      --color-scheme COLOR_SCHEME
                            Color scheme to use in Konsole
      --font FONT           Name of font to use in Konsole
      -S FONT_SIZE, --font-size FONT_SIZE
                            Size of font to use (in pts)
      --font-family FONT_FAMILY
                            Font family to use
      --font-linechars      Use font's native line-drawing characters
      --cursor-shape {0,1,2}
                            Set cursor shape (Block/Vertical Bar/Underscore)
      -W WIDTH, --width WIDTH
                            Terminal size, columns
      -H HEIGHT, --height HEIGHT
                            Terminal size, rows
    
    pyttygif basic conversion settings:
      input                 Path to the ttyrec file to convert
      output                Path to save the resulting GIF
      -s SPEED, --speed SPEED
                            Speed multiplier
      -l LOOP, --loop LOOP  Number of times to play the GIF (0 = infinity)
    
    pyttygif advanced conversion settings:
      -L LASTFRAME, --lastframe LASTFRAME
                            How long to display the last frame
      -o {0,1,2,3}, --optimize-level {0,1,2,3}
                            Optimize the GIF (levels 0-3)
      -f FPS, --fps FPS     How many frames to screenshot per second
      -c DELAYCAP, --delaycap DELAYCAP
                            Cap the display time of single frame (in seconds)
      -x LOSSY, --lossy LOSSY
                            Use gifsicle lossy GIF compression ratio
      -e ENCODING, --encoding ENCODING
                            Reencode ttyrec to match terminal (source:target)
      -C [LOGARITHMIC], --logarithmic [LOGARITHMIC]
                            Enable logarithmic time compression (default base = e)
    
    MP4 conversion settings:
      -v, --video           Whether to create a video
      --video-only          Delete GIF after encoding an MP4 video from it
      --crf CRF             A CRF level for video (default - 22)
      --tune TUNE           Use codec tune preset (default - animation)
      --preset PRESET       Use codec preset (default - medium)
      -r FRAMERATE, --framerate FRAMERATE
                            Framerate to encode video with (default - 30)

Most options are intended to have sane defaults, but can be customized.

### GIF conversion settings

`-s` allows to speed up or slow down GIF (relatively to original ttyrec speed) by a floating-point factor. Default speed is 1.0 (original speed).  
`-l` allows to set a number of loops for resulting GIF. It defaults to 1 (single play). You can set it to integer number of loops, or 0 to loop infinitely.  
`-L` allows to set last frame display time (floating point number of seconds) for looping GIFs and defaults to 5.0 seconds.  
`-o` sets the GIF optimization level and defaults to 2. To achieve maximum optimization, you can set it to 3, and to get more speed at the cost of the resulting GIF size - you can set optimization to lower level.  
`-f` sets the number of frames for pyttygif to screenshot per second. It defaults to 25, but if resulting GIF has stuttering or frame skip artifacts - you can lower it.  
`-c` allows to cap delay of single frame to at most this number of seconds (floating point). It's disabled by default. For example, if it's set to 5.0, then any frames taking longer than 5 seconds would display for exactly 5 seconds.  
`-x` sets lossiness for gifsicle lossy mode.  
`-e` allows to specify source terminal (ttyrec) encoding and comma-separated target terminal encoding and re-encode ttyrec on-the-fly. This is intended e.g. for NetHack ttyrecs with IBMgraphics, where resulting ttyrecs are CP437 and they don't play back correctly on UTF-8 terminals. By specifying `-e cp437:utf-8` option, pyttygif would produce a correct GIF.  
`-C` enables logarithmic time compression. By default, natural logarithm (base e) is used, like in IPBT, however you may optionally specify any other valid base. This option will cause delays to be scaled non-linearly. Extremely large delays will be compressed significantly (e.g. hour-long delay will turn into several seconds), while small delays will have negligible difference. It works together with speed adjustment, too.

### Konsole visualization settings

`-W` sets terminal size in columns (width). Defaults to 80.  
`-H` sets terminal size in rows (height). Defaults to 24.  
`-S` sets the font size in pts. Defaults to 9.  
`--no-antialias` disables font antialiasing.  
`--bold-intense` prints bright colors with bold font.  
`--font-linechars` forces to use native font's line-drawing characters.  
`--font` sets name of font to use. Defaults to "DejaVu Sans Mono".  
`--font-family` sets family of font to use. Defaults to "Regular".  
`--color-scheme` sets the Konsole color scheme to use. Defaults to "Linux".  
`--cursor-shape` sets the shape of cursor, where 0 - block, 1 - vertical bar, 2 - underscore. Defaults to 0.  

### Video conversion settings

`-v` enables video conversion, and after finishing GIF creation, ffmpeg would be launched to produce MP4 file.  
`-r` sets the video framerate and defaults to 30.  
`--video-only` forces GIF to be deleted, keeping only MP4 video.  
`--crf` sets H.264 constant rate factor. It defaults to 22, which should give a good quality.  
`--tune` sets fine-tuning codec preset. It defaults to "animation".  
`--preset` sets the codec preset. It defaults to "medium".  

### Xvfb settings

`--screen-size` sets the Xvfb screen size. Generally shouldn't be necessary to change and defaults to "1920x1080x24".  

## License

![GPLv3](https://github.com/tmp6154/pyttygif/blob/master/img/gplv3.png?raw=true "GPLv3")
