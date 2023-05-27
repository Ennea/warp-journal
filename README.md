# Warp Journal

Warp Journal is a lightweight gacha tracker for Honkai: Star Rail.

### Runs on your PC

Unlike other tools with a similar function, Warp Journal runs on your own PC. No data ever leaves your computer.

### Feature overview

- Save your gacha history locally
- View your pity for all banners
- Browse your gacha history quickly, including some simple filters
- Check out some nifty statistics about your gacha history
- Support for multiple accounts/UIDs

## Frequently asked questions

### How do I use this?

Just download the installer, run it and follow the instructions. After launching it, hit the big button and you should be all set :)

### Why does it open a website? How does that work?

Warp Journal will open in your browser, simply because it's a lot easier (and prettier!) to present the data like that. Once you close the Warp Journal tab (or your browser), Warp Journal will also exit.

### Can I bookmark the page Warp Journal opens in my browser?

Sadly no. Because Warp Journal exits once you close its tab and cannot simply detect when you want to open it from within the browser, you can only start it by running the program.

### How do I use Warp Journal for multiple accounts?

Just use Warp Journal like you normally would. The warps that are being fetched depend on which account you've opened the in-game history with last. Once Warp Journal has data for multiple UIDs, it will allow you to select the UID you want to view the statistics and warp history for.

### How does Warp Journal get my gacha history?

The same way the game does! It just automates it all and then stores the history locally. That way, you can browse it much faster.

### Where is my warp history stored?

On your computer! Your warp history is stored in `%APPDATA\warp-journal`.

### Can I use this with a Chinese account?

Chinese accounts are not currently supported. If there's enough interest for this, I can add support for Chinese accounts.

### Are platforms besides Windows supported?

Linux is supported. I suggest creating a virtual environment first via `python3 -m venv .venv`, then activating it via `source .venv/bin/activate`. Then install all requirements via `pip install -r requirements.txt`. Then you can launch Warp Journal with `python warp-journal.py`. If you're dual booting Windows, you can even point Warp Journal to the location of the game, so that the automatic extraction of the history URL works on Linux, too. For now, this requires setting the path to the game as an environment variable. For example: `GAME_PATH=/mnt/windows/Users/Ennea/Games/HSR python warp-journal.py`.

If you're not dual booting, you can still manually enter the history URL in Warp Journal's UI.

Mac OS is also supported, at least technically; I have no way to test this personally, but if you can, I'd love to hear if it's working :)

## Warp Journal uses

- [Alpine.js](https://github.com/alpinejs/alpine) - [License](3rd-party-licenses/LICENSE_alpinejs)
- [bottle.py](https://github.com/bottlepy/bottle) - [License](3rd-party-licenses/LICENSE_bottlepy)
- [gevent](https://github.com/gevent/gevent) - [License](3rd-party-licenses/LICENSE_gevent)
- [Nuitka](https://github.com/Nuitka/Nuitka) - [License](3rd-party-licenses/LICENSE_Nuitka)

---
Warp Journal is not affiliated with HoYoverse. Honkai: Star Rail is a trademark of HoYoverse.
