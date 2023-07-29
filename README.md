# Footage Gap Detector for Dashcams
Dashcams can sometimes have a few seconds of gap between recordings when ending the current file and starting the next.

This is bad because of the chance that an emergency event during your drive occurs during one of those gaps.

It's best to detect that your dashcam has such gaps and address it before it matters most.

So, here's a quick tool to flag these gaps.

Example command:
```
detect.py --dir "/memory_card/recordings"
```

Can output something like:
```
Detected 6408ms gap between ".../2017_0114_141750_008.MP4" and ".../2017_0114_141805_009.MP4"
Detected 3520ms gap between ".../2017_0114_141805_009.MP4" and ".../2017_0114_141816_010.MP4"
Detected 1000ms gap between ".../2017_0116_121056_017.MP4" and ".../2017_0116_121557_018.MP4"
Detected 1000ms gap between ".../2017_0205_153459_307.MP4" and ".../2017_0205_153959_308.MP4"
```

## How to Install
Every platform is different so these instructions are only in general terms.

1. Download the *.py files in the [detector](https://github.com/nekorevend/Footage-Gap-Detector/tree/main/detector) directory.
    - Or install [git](https://git-scm.com/) and `git clone` this repository.
1. Use a [Python virtual environment](https://docs.python.org/3/library/venv.html) with [pip](https://packaging.python.org/en/latest/key_projects/#pip) to set up the dependencies for this tool.
