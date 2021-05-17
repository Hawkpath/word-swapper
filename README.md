# Word Swapper

[![release](https://img.shields.io/github/v/release/hawkpath/word-swapper)](https://github.com/Hawkpath/word-swapper/releases)
[![license](https://img.shields.io/github/license/hawkpath/word-swapper)](LICENSE)

Word Swapper is a Discord bot that uses a trained language model to swap words
in a message with similar words.

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [Config](#config)
- [License](#license)

## Install

To get started, clone the repo.

```shell script
git clone https://github.com/hawkpath/word-swapper.git
cd word-swapper
```

[Install Pipenv](https://pipenv.pypa.io/en/latest/install/#installing-pipenv).
After installing for the first time, you may have to do some extra steps to
be able to use the `pipenv` command in your shell. Read the note in the
Pipenv installation page for more info.

```shell
python -m pip install --user pipenv
```

Install the dependencies with Pipenv. Word Swapper requires Python 3.8.

```shell
# If Python 3.8 is your default version:
pipenv sync

# If Python 3.8 is NOT your default version, you should specify the path to
# your Python 3.8 executable
pipenv sync --python "/usr/bin/python3.8"
pipenv sync --python "C:\Miniconda3\envs\python38\python.exe"
```

## Usage

### Set up configuration

Create a json file `word_swapper/config.json` (or copy [word_swapper/config_example.json](word_swapper/config_example.json)).
The only value you need to set is the `bot_token`.

```json
{
    "bot_token": "<YOUR_BOT_TOKEN>"
}
```

### Running Word Swapper

#### Basic

In the top level directory, simply run Word Swapper as a Python module with
Pipenv.

```shell script
pipenv run python -m word_swapper
```

### Inviting Word Swapper to your Discord server

Word Swapper requires the following permissions to run normally:

- View Channels
- Send Messages
- Manage Messages (to delete reactions)
- Embed Links
- Read Message History (to re-run commands)
- Add Reactions

These correspond to the permission integer `93248`.

## Commands and features

Command | Description | Example
------- | ----------- | -------
`$pun <phrase...>` | Swap a word in the phrase with a similar word | $pun jimmy neutron

## License

[MIT © Hawkpath.](LICENSE)
