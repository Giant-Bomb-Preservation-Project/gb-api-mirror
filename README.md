# GB API Mirror

Downloads the content from the [Giant Bomb API](https://www.giantbomb.com/api/)
and stores it locally as JSON files.

## Requirements

* Python 3.12+
* An API key from Giant Bomb

## Usage

Put your API key in the `GB_API_KEY` environment variable:

```shell
export GB_API_KEY='<your api key>'
```

(Optional) Setup a virtual environment:

```shell
python -m venv env
source env/bin/activate
```

Install the dependencies:

```shell
pip install -r requirements.txt
```

Run the script:

```shell
python gb-api-mirror.py <path to save files>
```

### Options

* `--delay SECONDS` Delay between the requests (in seconds)
* `--images` Also download the images
* `--include RESOURCES` Comma-separated list of the resources to download (defaults to all)
* `--overwrite-images` Overwrite existing images (by default it doesn't download ones that exist)
* `--quiet` Suppress all output (except errors)
* `--skip-existing` Skip over resources which have already been downloaded
* `--verbose` Show verbose output

## Development

The code is type checked with [mypy](https://mypy-lang.org/) and formatted with
[Black](https://black.readthedocs.io/), so ensure they are installed:

```shell
pip install black mypy
```

Run them both to format and type check the files:

```shell
black . && mypy .
```
