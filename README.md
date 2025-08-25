# My Python scripts

Just some scripts I made to carry out certain tasks or try out various things.

<!-- MarkdownTOC -->

- [ssh-known-hosts](#ssh-known-hosts)
- [mp3-idv3-tags](#mp3-idv3-tags)
- [generate-iconset](#generate-iconset)
- [oxps-to-pdf](#oxps-to-pdf)
- [create-folders-for-files](#create-folders-for-files)
- [tinyurl](#tinyurl)
- [folders-creation-datetimes](#folders-creation-datetimes)
- [get-possible-quiz-results](#get-possible-quiz-results)
- [coub-likes-list](#coub-likes-list)
- [pack-the-folder](#pack-the-folder)
- [srt-translation-generator](#srt-translation-generator)
- [normalize-filenames](#normalize-filenames)
- [parallelization-example](#parallelization-example)
- [padding-indexes](#padding-indexes)
- [website-availability](#website-availability)

<!-- /MarkdownTOC -->

## ssh-known-hosts

SSH config known hosts analysis.

## mp3-idv3-tags

Mass ID3v2 tags editing.

``` sh
$ python mp3-idv3-tags.py /path/to/folder/with/mp3files/
```

## generate-iconset

Moved to a [separate repository](https://github.com/retifrav/generate-iconset).

## oxps-to-pdf

Convert OXPS files into PDF. Requires `ghostscript`/`gxps` to be installed.

``` sh
$ python oxps-to-pdf.py /path/to/folder/with/oxps/files
```

## create-folders-for-files

I [needed that](http://retifrav.github.io/blog/2019/03/17/migrating-from-octopress-to-hugo/#reorganizing-the-posts) to reorganize my Octopress blog posts to a new folder structure for Hugo.

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
│   └── index.md
├── ios-player-buttons-areas
│   └── index.md
├── gta-iv-final-mission-bug
│   └── index.md
├── sidebar-in-octopress
│   └── index.md
├── no-more-overlicensed
...
```

It takes only one argument which is the path to folder with the files you want to reorganize:

``` sh
$ python create-folders-for-files.py ~/Desktop/posts/
```

## tinyurl

A [TinyURL](http://tinyurl.com) API caller:

``` sh
$ python tinyurl.py http://example.org
```

Part of [my Alfred workflow](http://retifrav.github.io/blog/2019/04/02/tinyurl-alfred-workflow/).

## folders-creation-datetimes

There is the following folders structure:

```
/tmp/revisions/
├── 37829
│   └── Tools
├── 37976
│   └── Tools
└── 37993
    └── Tools

Nov 24 18:30 37829/Tools
Nov 24 18:37 37976/Tools
Nov 24 18:31 37993/Tools
```

Need to get UTC datetimes of `Tools` folders and form a list of SQL queries for inserting like this:

``` sql
insert into revisions(dt_published,release_id,revision,content_id) values('2019-11-24 17:31:07',1,'37993',3);
insert into revisions(dt_published,release_id,revision,content_id) values('2019-11-24 17:30:21',1,'37829',3);
insert into revisions(dt_published,release_id,revision,content_id) values('2019-11-24 17:37:17',1,'37976',3);
```

Run:

``` sh
$ python folders-creation-datetimes.py /tmp/revisions/
```

## get-possible-quiz-results

There is some online test and you want to get all the possible results. Having a results URL like `http://mindmix.ru/result?t=23147&1=3&2=3&3=2&4=3&5=4&6=2&7=2&8=2&9=3&10=4`, you can send a 1000 requests with random values.

## coub-likes-list

Getting a list of liked [coubs](https://coub.com/). Created for [this issue/question](https://github.com/HelpSeeker/CoubDownloader/issues/11).

Before running the script, replace the following:

- `aythenticationCookie`: your actual `Cookie` HTTP header value, you get it from the browser console;
- `whereToSaveLikesList`: path to the file where to save the list of links of your liked coubs;
    + optionally, also set `whereToSaveLikesDetails` and uncomment the block with `json.dump()`

Script is run without parameters:

``` sh
$ python ./coub-likes-list.py
```

Once you have the resulting file with links, you can download all of them using [CoubDownloader](https://github.com/HelpSeeker/CoubDownloader):

``` sh
$ python /path/to/coub-downloader/coub.py /tmp/my-coub-likes.txt
```

## pack-the-folder

Pack the current folder into a ZIP archive. Creates an archive in a folder one level up and then moves it into the current folder.

``` sh
$ ls -L1 .
Screenshot1.png
Screenshot2.png
document.pdf
pack-the-folder.py
some/

$ python ./pack-the-folder.py

$ ls -L1 .
Screenshot1.png
Screenshot2.png
document.pdf
folder.zip
pack-the-folder.py
some/
```

## srt-translation-generator

Creates a copy of an original SRT file, keeping only the titles numbers and time codes. The generated copy can be used for translating the original file.

``` sh
$ python ./srt-translation-generator.py --help
```

## normalize-filenames

Normalizing the names of files in a given directory:

- replaces spaces and underscores with dashes
- removes non-alphanumeric symbols
- makes all letters small

```
$ ls -L1 /path/to/somewhere
Dota 2 WTF Moments 444.mkv
Johnny Depp Performs ‘Nothing Else Matters’ (Metallica Cover) During His Testimony, Then Wins Case.mkv
Video 4 Det snør!!!❄️❄️❄️❄️.mkv
dota-2-wtf-moments-444.mkv

$ python /path/to/normalize-filenames.py /path/to/somewhere --not-a-drill
THIS IS NOT A DRILL!
All the files in /path/to/somewhere folder will be renamed.
Hopefully, you've made a backup.

- renaming: Video 4 Det snør!!!❄️❄️❄️❄️.mkv
OK

- renaming: dota-2-wtf-moments-444.mkv
[WARNING] The file dota-2-wtf-moments-444.mkv already exists

- renaming: Johnny Depp Performs ‘Nothing Else Matters’ (Metallica Cover) During His Testimony, Then Wins Case.mkv
OK

- renaming: Dota 2 WTF Moments 444.mkv
[WARNING] The file dota-2-wtf-moments-444.mkv already exists

---
Total files processed: 2

$ ls -L1 /path/to/somewhere
Dota 2 WTF Moments 444.mkv
dota-2-wtf-moments-444.mkv
johnny-depp-performs-nothing-else-matters-metallica-cover-during-his-testimony-then-wins-case.mkv
video-4-det-snr.mkv
```

## parallelization-example

An example of parallelizing some function.

``` sh
$ python ./parallelization-example.py --help
```

## padding-indexes

Pads (*to "left" and "right"*) every element in the list of indexes for some other list/array:

``` py
paddedList = addPaddingToList(
    incomingList, # the original list
    3,            # how many positions/indexes to "pad"
    32            # maximum allowed index
)
```

So for original list like this:

```
[2, 4, 11, 19, 21, 30]
```

it will return the following "padded" list:

```
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 27, 28, 29, 30, 31, 32]
```

It should have also contained `33`, but we've limited it with `32`.

## website-availability

Checks website availability based on HTTP responses status code (*and request exceptions*):

``` sh
$ python ./website-availability.py https://decovar.dev/
$ echo $?
0

$ python ./website-availability.py http://decovar.dev/
[ERROR] HTTP response status code: 301
$ echo $?
1

$ python ./website-availability.py http://decovar.dev/ --allow-redirects
$ echo $?
0

$ python ./website-availability.py https://some.unreachable.host.in.a.galaxy.far.far.away/
[ERROR] Host unreachable or a DNS issue
$ echo $?
1
```
