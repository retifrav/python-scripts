# My Python scripts

I always try to use the latest version of Python 3. Haven't tested any of the scripts with Python 2.

- [ssh-known-hosts](#ssh-known-hosts)
- [mp3-idv3-tags](#mp3-idv3-tags)
- [generate-iconset](#generate-iconset)
- [oxps-to-pdf](#oxps-to-pdf)
- [create-folders-for-files](#create-folders-for-files)
- [tinyurl](#tinyurl)
- [folders-creation-datetimes](#folders-creation-datetimes)
- [get-possible-quiz-results](#get-possible-quiz-results)

## ssh-known-hosts

SSH config known hosts analysis.

## mp3-idv3-tags

Mass ID3v2 tags editing.

``` bash
python mp3-idv3-tags.py /path/to/folder/with/mp3files/
```

## generate-iconset

Moved to a [separate repository](https://github.com/retifrav/generate-iconset).

## oxps-to-pdf

Convert OXPS files into PDF. Requires `ghostscript`/`gxps` to be installed.

``` bash
python oxps-to-pdf.py /path/to/folder/with/oxps/files
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

## tinyurl

A [TinyURL](http://tinyurl.com) API caller:

``` bash
python tinyurl.py http://example.org
```

Part of [my Alfred workflow](http://retifrav.github.io/blog/2019/04/02/tinyurl-alfred-workflow/).

## folders-creation-datetimes

There is the following folders structure:

```
/tmp/revisions/
├── 37829
│   └── Tools
├── 37976
│   └── Tools
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

```
python folders-creation-datetimes.py /tmp/revisions/
```

## get-possible-quiz-results

There is some online test and you want to get all the possible results. Having a results URL like `http://mindmix.ru/result?t=23147&1=3&2=3&3=2&4=3&5=4&6=2&7=2&8=2&9=3&10=4`, you can send a 1000 requests with random values.
