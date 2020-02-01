# Fujiwara Filter

## A Discord bot that takes action against rampant meme abuse


Is your Discord server's meme channel a mess of low-quality content?

Is your server filled to the brim with people who can't bother cropping out their Reddit or iFunny watermark?

Are you involved in a meme war started by [someone](https://soundcloud.com/someone2639) who cannot stop posting the same [image macro](https://imgur.com/a/8Tfj0MX) with the same [caption](https://imgur.com/a/8Tfj0MX) featuring the same [anime girl](https://imgur.com/a/8Tfj0MX)?

Then this project is for you!

Fujiwara Filter works (or at least _will_ work) in a 3-phase system:

 1. First, the bot checks against a known list of banned images (and eventually watermarks).
 2. Next, the bot detects any faces based on how you modify `bot.py`, and will react to when a certain color is prominent in the image (This works unexpectedly well with anime characters' hair)
 3. If both of these check fail, the bot will use OCR to detect banned phrases that you can configure (eventually)
 
## Roadmap
  - Face & color detection: **Working**
  - Image Matching
  - OCR
  - Addition of configuration files for phrases and face detection parameters
  - Actions the bot can take against offending users
  - some easy way to install/set up the bot


# Setup

```bash
git submodule init
<idk the command after this lol>
```
After getting the anime face detection model, put any images you want to explicitly target in the bannedImages folder.

After adding the bot to your server, run

```bash
python3 bot.py
```

And you should be good to go! Try it out by posting images and seeing how it reacts (currently the bot does not actually ban/kick users, look out here for a specific section on configuring/testing the bot when those features are complete!)

# FAQ

## What inspired this project?

I have been "that guy" on many servers. This is for people like you who aren't willing to put up with people like me

## Can I get some bot result images?

Once I figure out how to embed images in this file I'll let you know (not really, but check back sometime!)

## Are you stupid?

IM

STUPID
