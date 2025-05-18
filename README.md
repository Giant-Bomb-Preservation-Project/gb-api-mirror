# GB API Mirror

Downloads the content from the [Giant Bomb API](https://www.giantbomb.com/api/)
and stores it locally as JSON files.

![Screenshot of the script downloading video shows, videos, promos, and reviews](https://github.com/Giant-Bomb-Preservation-Project/gb-api-mirror/blob/main/screenshot.png?raw=true)

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

* `--download-images` Also download the image files
* `--include RESOURCES` Comma-separated list of the resources to download (defaults to all)
* `--overwrite-images` Overwrite existing images (by default it doesn't download ones that exist)
* `--quiet` Suppress all output (except errors)
* `--skip-existing` Skip over resources which have already been downloaded
* `--verbose` Show verbose output

## Image Files

If the `--download-images` option is passed in the script will attempt to download
the images associated with each resource. The script does a bunch of URL mapping and
other changes to download the largest possible version of the image, even if the
resource has linked to a smaller version.

## Special Resources

Some of the available resources are "special" in the sense that they aren't just
requests to a paginated endpoint. These include:

### Articles

There is no API endpoint for articles, so this resource is downloaded by scraping
the actual website. The resulting JSON file is formatted to look vaguely like what
would come out of an API but could be inconsisten in terms of field naming and such.

### Images

Not to be confused with the image data (below) or image files (above), this is 
essentially galleries which are attached to the different resources. For example
screenshots for a game.

We can only determine which images to download once the other resources have been
downloaded, so leave this for last.

### Image Data

There is no real endpoint to get image data, but there is a JSON endpoint which
is used by the site's frontend to populate a resource's library when you look
at it. This is scraped by just incrementing the resource ID from 0 to 1,999,999.

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
