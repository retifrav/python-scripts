# My Python scripts

I always try to use the latest version of Python 3. Haven't tested any of the scripts with Python 2.

- [ssh-known-hosts](#ssh-known-hosts)
- [mp3-idv3-tags](#mp3-idv3-tags)
- [generate-iconset](#generate-iconset)
- [oxps-to-pdf](#oxps-to-pdf)

## ssh-known-hosts

SSH config known hosts analysis.

## mp3-idv3-tags

Mass ID3v2 tags editing.

``` bash
python mp3-idv3-tags.py /path/to/folder/with/mp3files/
```

## generate-iconset

Generate `.icns` file for Mac OS application from `.png` picture.

``` bash
python generate-iconset.py /path/to/original/icon.png
```

Result (`icon.icns`) will be saved to `/path/to/original/`.

More information in the following [article](https://retifrav.github.io/blog/2018/10/09/macos-convert-png-to-icns/).

## oxps-to-pdf

Convert OXPS files into PDF. Requires `ghostscript`/`gxps` to be installed.

``` bash
python oxps-to-pdf.py /path/to/folder/with/oxps/files
```

## create-folders-for-files 

I needed that to reorganize my Octopress blog posts to a new folder structure for Hugo.

Original structure:

```
.
├── first-post.md
├── ios-player-buttons-areas.md
├── gta-iv-final-mission-bug.md
├── sidebar-in-octopress.md
├── no-more-overlicensed.md
...
```

New structure:

```
.
├── first-post
│   └── index.md
├── ios-player-buttons-areas
│   └── index.md
├── gta-iv-final-mission-bug
│   └── index.md
├── sidebar-in-octopress
│   └── index.md
├── no-more-overlicensed
...
```

It takes only one argument which is the path to folder with the files you want to reorganize:

``` bash
python create-folders-for-files.py ~/Desktop/posts/
```
