# blaise-ingest

Python cloud function that's triggered when a zip file is uploaded (object finalized) to the environments ingest bucket.

Call the REST API endpoint with the appropriate parameters so that it processes the file (download, extract, merge).

Be defensive, only process zip files, check the corresponding questionnaire is deployed to the environment first, the REST API may already do this? check...

Check the REST API deletes the zip after it's been processed...

##Local Setup

Clone the project locally:

```
git clone https://github.com/ONSdigital/blaise-ingest.git 
```

Install poetry:
```
pip install poetry
```

Run poetry install
```
poetry install
```

## Using Poetry
``` make format ``` will format your code to make it pretty which is the same as ```poetry run isort .```.

```make lint``` checks your coding standards and ```make test``` will run all tests.

### Troubleshooting

To give you the path to python for your virtual env run:
```
echo "$(poetry env info | grep Path | awk '{print $2}')/bin/python"
```

Run unit tests:
```shell
poetry run python -m pytest
```
