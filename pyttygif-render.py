#!/usr/bin/python3

#      This file is part of pyttygif.
#
#      pyttygif is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      pyttygif is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with pyttygif.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import os
import sys
import subprocess
import shlex
import pathlib
import math

# Consts
X_TOKEN = '/tmp/pyttygif.xvfb.auth'

# Arg parsing and initial handling
args = None

parser = argparse.ArgumentParser(description='pyttygif-render - Convert a ttyrec to GIF/MP4 animation')
xgroup = parser.add_argument_group("Xvfb settings")
xgroup.add_argument('--screen-size', default="1920x1080x24",
                    help="Screen size to use for virtual X server")

termgroup = parser.add_argument_group("Konsole visualization settings")
termgroup.add_argument('--no-antialias', default=False,
                       action='store_true',
                       help="Disable font antialiasing")
termgroup.add_argument('--bold-intense', default=False,
                       action='store_true',
                       help="Use bold font with bright colors")
termgroup.add_argument('--color-scheme', default="Linux",
                       help="Color scheme to use in Konsole")
termgroup.add_argument('--font', default="DejaVu Sans Mono",
                       help="Name of font to use in Konsole")
termgroup.add_argument('-S', '--font-size', default=9, type=int,
                       help="Size of font to use (in pts)")
termgroup.add_argument('--font-family', default='Regular',
                       help="Font family to use")
termgroup.add_argument('--font-linechars', default=False,
                       action='store_true',
                       help="Use font's native line-drawing characters")
termgroup.add_argument('--cursor-shape', default=0, choices=range(0, 3),
                       type=int,
                       help="Set cursor shape (Block/Vertical Bar/Underscore)")
termgroup.add_argument('-W', '--width', default=80, type=int,
                       help="Terminal size, columns")
termgroup.add_argument('-H', '--height', default=24, type=int,
                       help="Terminal size, rows")
termgroup.add_argument('-a', '--autodetect-size', action='store_true',
                       help="Try to autodetect minimal needed terminal size")

maingroup = parser.add_argument_group("pyttygif basic conversion settings")
maingroup.add_argument('input', default=None,
                       help="Path to the ttyrec file to convert")
maingroup.add_argument('output', default=None,
                       help="Path to save the resulting GIF")
maingroup.add_argument('-s', '--speed', default=1.0,
                       type=float, help="Speed multiplier")
maingroup.add_argument('-l', '--loop', default=1, type=int,
                       help="Number of times to play the GIF (0 = infinity)")

advgroup = parser.add_argument_group("pyttygif advanced conversion settings")
advgroup.add_argument('-L', '--lastframe', default=5.0, type=float,
                      help="How long to display the last frame")
advgroup.add_argument('-o', '--optimize-level', default=2, choices=range(0, 4),
                      type=int, help="Optimize the GIF (levels 0-3)")
advgroup.add_argument('-f', '--fps', default=25, type=int,
                      help="How many frames to screenshot per second")
advgroup.add_argument('-c', '--delaycap', default=None, type=float,
                      help="Cap the display time of single frame (in seconds)")
advgroup.add_argument('-x', '--lossy', default=None, type=int,
                      help="Use gifsicle lossy GIF compression ratio")
advgroup.add_argument('-e', '--encoding', default=None,
                      help="Reencode ttyrec to match terminal (source:target)")
advgroup.add_argument(
    '-C', '--logarithmic', const=math.e, default=None,
    type=float, nargs="?",
    help="Enable logarithmic time compression (default base = e)"
)

videogroup = parser.add_argument_group("MP4 conversion settings")
videogroup.add_argument('-v', '--video', default=False, action='store_true',
                        help="Whether to create a video")
videogroup.add_argument('--video-only', default=False,
                       action='store_true',
                       help="Delete GIF after encoding an MP4 video from it")
videogroup.add_argument('--crf', default=22, type=int,
                        help="A CRF level for video (default - 22)")
videogroup.add_argument('--tune', default="animation",
                        help="Use codec tune preset (default - animation)")
videogroup.add_argument('--preset', default="medium",
                        help="Use codec preset (default - medium)")
videogroup.add_argument('-r', '--framerate', default=30, type=int,
                        help="Framerate to encode video with (default - 30)")

try:
    args = parser.parse_args()
except argparse.ArgumentError:
    parser.print_help()
    sys.exit(0)

width = args.width
height = args.height

if args.autodetect_size:
    import pyte
    from pyttygif.ttyplay import TtyPlay

    class Cursor(pyte.screens.Cursor):

        maxx = maxy = 0

        @property
        def x(self):
            return self._x

        @x.setter
        def x(self, value):
            self._x = value
            Cursor.maxx = max(Cursor.maxx, value)

        @property
        def y(self):
            return self._y

        @y.setter
        def y(self, value):
            self._y = value
            Cursor.maxy = max(Cursor.maxy, value + 1)

    pyte.screens.Cursor = Cursor
    screen = pyte.Screen(4096, 1024)
    stream = pyte.Stream(screen)
    with TtyPlay(args.input) as player:
        while player.read_frame():
            stream.feed(str(player.frame, errors='ignore'))

    width = Cursor.maxx
    height = Cursor.maxy

# Prepare a xvfb commandline

xvfbargs = ['xvfb-run', '-f', X_TOKEN, '-a', '-s',
            f'-screen 0 {args.screen_size} -auth {X_TOKEN}']

# Prepare a Konsole profile from commandline args

konsoleprofile = f"""[Appearance]
AntiAliasFonts={str(not args.no_antialias).lower()}
BoldIntense={str(args.bold_intense).lower()}
ColorScheme={args.color_scheme}
Font={args.font},{args.font_size},-1,5,50,0,0,0,0,0,{args.font_family}
UseFontLineChararacters={str(args.font_linechars).lower()}

[Cursor Options]
CursorShape={args.cursor_shape}

[General]
Environment=TERM=konsole-256color,COLORTERM=truecolor
Name=pyttygif
Parent=FALLBACK/
TerminalColumns={width}
TerminalRows={height}

[KonsoleWindow]
ShowMenuBarByDefault=false

[Scrolling]
HistoryMode=0
ScrollBarPosition=2

[Terminal Features]
BlinkingCursorEnabled=false
BlinkingTextEnabled=false
FlowControlEnabled=false"""

# Write a new profile file

try:
    os.makedirs(pathlib.Path(pathlib.Path.home(), '.local/share/konsole/'))
except FileExistsError:
    pass
prof_path = pathlib.Path(pathlib.Path.home(), 
                         '.local/share/konsole/pyttygif.profile')
prof_fd = open(prof_path, 'w')
prof_fd.write(konsoleprofile)
prof_fd.close()

# Prepare Konsole commandline

konsoleargs = ['konsole', '--profile=pyttygif', '--hide-menubar',
               '--hide-tabbar', '--notransparency', '-e']

# Prepare a pyttygif commandline, this one is actually a single string
# with shell escape hell, we have to make it a single arg.

pyttygifargs = ["bash -c 'sleep 2 && python3 -m pyttygif",
                shlex.quote(args.input).replace("'", r"'\''"),
                shlex.quote(args.output).replace("'", r"'\''"),
                f"-s {args.speed}", f"-l {args.loop}", f"-L {args.lastframe}",
                f"-o {args.optimize_level}", '-S', f"-f {args.fps}"]

if args.delaycap is not None:
    pyttygifargs.append(f"-c {args.delaycap}")
if args.lossy is not None:
    pyttygifargs.append(f"-x {args.lossy}")
if args.encoding is not None:
    pyttygifargs.append(f"-e {args.encoding}")
if args.logarithmic is not None:
    pyttygifargs.append(f"-C {args.logarithmic}")
pyttygifargs.append(f"2>| {args.output}.log\'")
pyttygifargs = ' '.join(pyttygifargs)

# Build a commandline, by joining xvfb, Konsole and pyttygif args

cmdline = xvfbargs.copy()
cmdline.extend(konsoleargs)
cmdline.append(pyttygifargs)

# Finally, call this pack of commands

subprocess.check_call(cmdline)

os.remove(prof_path)  # Cleanup profile

# Print conversion log

os.system('clear')
log_path = f"{args.output}.log"
log_f = open(log_path)
print(log_f.read())
log_f.close()
os.remove(log_path)

# If video conversion requested - call ffmpeg to do this

if args.video:
    cmd = ["ffmpeg", "-i", args.output, "-movflags", "faststart", "-pix_fmt",
           "yuv420p", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-an", "-r",
           str(args.framerate), "-crf", str(args.crf), "-tune", args.tune,
           "-y", "-preset", args.preset, f'{args.output}.mp4']
    subprocess.check_call(cmd)

# If we want video only - remove source GIF

if args.video and args.video_only:
    os.remove(args.output)
