# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/arnoldswingtaiger/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/arnoldswingtaiger/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

One image summing up the world news of Thursday 19 November 2026: the rare Trump–Xi–Putin trilateral talks at the APEC summit in Shenzhen, the global rollout of Grand Theft Auto VI after a 13-year wait, Hakeem Jeffries' nomination as the first Black Speaker of the US House, the Pew projection that Islam will be the world's largest religion by 2035, Cyclone Akvan nearing India, the explanation for Earth's missing billion years, and the EU's proposed €45 billion loan for Ukraine.

`main.py` draws the 1024×1024 image from scratch in pure Python 3 standard library — its own PNG encoder and a built-in 5×7 bitmap font, no network, no installed packages — and writes it to `/output/entry.png`. Deterministic: no clock, no randomness, so two runs write the same bytes.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

Entered on [make.fun](https://make.fun/?ref=zv5hc3pw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards
