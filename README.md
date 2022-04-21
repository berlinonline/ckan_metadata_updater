# CKAN Metadata Updater

This is a Python tool to update a CKAN dataset's metadata by:

- Getting the current metadata through CKAN's API.
- Modifying the metadata locally by executing a series of steps.
- Pushing the metadata back to CKAN.

The updater can be used to automate updating the metadata of a dataset at specific moments.
If the dataset lives in a git repository, the updater could be part of a workflow that is triggered (via [GitHub Actions](https://github.com/features/actions) or [GitLab CI](https://docs.gitlab.com/ee/ci/)) when a new commit is made to a specific branch, or a release has been tagged.

## Requirements

- CKAN Metadata Updater has been developed for Python 3.
- It relies on the [ckanapi](https://github.com/ckan/ckanapi) module.

## Installation

The easiest way to install the updater is directly from this repository via `pip`.
You might want to do this in a dedicated virtual Python environment (_venv_), depending on your circumstances.
If you want to use the updater locally on a machine that runs many different applications, using a venv is recommended.
If you want to use the updater in a throwaway container (such as in a GitHub Actions workflow), the venv might not be necessary.
The following example uses a venv.

```shell
# Create a Python venv (virtual environment):
% python -m venv updater

# Activate the venv:
% . updater/bin/activate

# Install the updater and its dependencies into the venv:
(updater) % pip install git+https://github.com/berlinonline/ckan_metadata_updater.git
```

## Using the Metadata Updater

### Prerequisites

To work, the updater has a few prerequisites:

#### Config File

By default, all configuration is located in a JSON file located at `conf/ckan_updater.json` (relative to where the updater is run).
The config information in the file is grouped into different sections:

```json
{
    "dataset": {
        ...
    },
    "connection": {
        ...
    }
}
```

#### Patch Metadata

We need the dataset metadata that we want to patch over the existing metadata.
By default, this patch metadata comes from the config file's `dataset` object.
The data needs to conform to the format accepted by the [package_create](http://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.create.package_create "Documentation for the 'package_create' method from CKAN's Action API") method of the CKAN API, and needs to at least have the `id` field set.
Other metadata can be set as needed.

```json
{
    "dataset": {
        "id": "name_or_id_of_the_dataset",
        "berlin_source": "api-gitaction"
    },
    "connection": {
        ...
    }
}
```

Each attribute in the dataset's metadata that is also present in the patch metadata will be replaced by it. 

#### Other Configuration

We also need some additional configuration settings.
By default, these settings come from the config file's `connection` object.
At the least, this needs to contain the base URL of the CKAN installation we want to connect to.
Other configuration can be added if needed.

```json
{
    "dataset": {
        ...
    },
    "connection": {
        "ckan_base": "https://url.of.ckan.net"
    }
}
```

#### API Token

Because writing to CKAN usually requires authentication, we need an environment variable `CKAN_TOKEN` with a CKAN API token that grants write access to the dataset we want to change.

### Running the Updater

The simplest way to run the CKAN Metadata Updater is to run the `metadata_updater` command line tool that comes with the installation:

```
(updater) % metadata_updater --help
usage: metadata_updater [-h] [-p PATCH] [-c CONFIG] [-d DATE]

Get the current metadata of a dataset from CKAN, modify it locally and write it back to CKAN.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to the JSON file containing all settings. Default is `conf/ckan_updater.json`.
  -d DATE, --date DATE  The date to be used as `date_updated`. Default is today.
```

If the config file is present at the default location, `metadata_updater` can be run without any arguments:

```
(updater) berlin_dataportal_usage % metadata_updater
INFO:root: reading patch data from metadata/dataset.json
INFO:root: reading config from conf/ckan_settings.json
INFO:root: setting up CKAN connector at https://url.of.ckan.net (as 'berlin_dataset_updater/1.0 (+https://github.com/berlinonline/berlin_dataset_updater)')
INFO:root: reading remote metadata for name_or_id_of_the_dataset
INFO:root: running <function apply_patch at 0x10fd1b5e0>
INFO:root: apply_patch - id: name_or_id_of_the_dataset
INFO:root: apply_patch - berlin_source: api-gitaction
INFO:root: running <function set_date_updated at 0x10fdc38b0>
INFO:root: setting `date_updated` to 2022-04-06
INFO:root: writing metadata
```

This will:

- get the current metadata from CKAN
- run two steps to update the metadata:
    - apply the patch metadata
    - set the attribute `date_updated` to today's date
- upload the updated metadata to CKAN

If these steps are all that is required, nothing else needs to be done.
However, if there are additional changes that need to be applied to the metadata, these can be implemented as custom steps as described in the following section.

#### Custom Steps

Each step consists of a function and some input.
To define custom steps, we need to write a Python script that extends the updater.
Let's call the script `custom_updater.py`.
This script (see below) then replaces the command line tool `metadata_updater`.
The basic structure of the script looks like this:

```python
import logging
from berlinonline.ckan_metadata_updater import CKANMetadataUpdater

# custom step functions:
# ...

# instantiate the updater
updater = CKANMetadataUpdater()

# run the updater
updater.run()
```

##### Step Functions

To be used as part of a step, a function needs to take a `dataset_metadata` dict as its first parameter.
This dict contains the dataset's metadata as defined in [package_create](http://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.create.package_create "Documentation for the 'package_create' method from CKAN's Action API"), which is being manipulated further in each step.
In addition to `dataset_metadata`, a step function can have any number of additional parameters.

The default step functions can be found in [steps.py](berlinonline/ckan_metadata_updater/steps.py "The 'steps.py' source code file").

The following is an example for a new custom step function that sets the `temporal_coverage_to` field to the last day of the previous month.

```python
from datetime import date, timedelta

def update_temporal_coverage_to(dataset_metadata: dict):
    '''Set `temporal_coverage_to` to the last day of the previous month.'''
    today = date.today()
    first = today.replace(day=1)
    lastMonth = (first - timedelta(days=1)).isoformat()
    logging.info(f" setting `temporal_coverage_to` to {lastMonth}")
    dataset_metadata['temporal_coverage_to'] = lastMonth
    return dataset_metadata
```


##### Adding Steps

To use a step function as a step in the updater, it needs to be added to the updater's `steps` attribute.
`steps` contains a list of steps, where each step is a dict which contains the `function` reference and a list of `parameters` for the additional input data.
As an example, the step dict for the apply patch step looks like this:

```python
{
    "function": berlinonline.ckan_metadata_updater.steps.apply_patch, 
    "parameters": [self.patch_data]
}
```


To add custom steps, we add the new step function to our `custom_updater.py` script.
Then, we can simply add or insert a step dict into `steps` as follows (`update_temporal_coverage_to()` doesn't need any additional input data, so `parameters` is an empty list):

```python
updater.steps.append({
    "function": update_temporal_coverage_to,
    "parameters": []
})
```

Finally, the complete `custom_updater.py` would look like this:

```python
from datetime import date, timedelta
import logging
from berlinonline.ckan_metadata_updater import CKANMetadataUpdater

# custom step functions:
def update_temporal_coverage_to(dataset_metadata: dict):
    # calculate the last day of the previous month
    today = date.today()
    first = today.replace(day=1)
    lastMonth = (first - timedelta(days=1)).isoformat()
    logging.info(f" setting `temporal_coverage_to` to {lastMonth}")
    dataset_metadata['temporal_coverage_to'] = lastMonth
    return dataset_metadata

# instantiate the updater
updater = CKANMetadataUpdater()

# add a custom step
updater.steps.append({
    "function": update_temporal_coverage_to,
    "parameters": []
})

# run the updater
updater.run()
```

## License

This material is copyright ©[BerlinOnline Stadtportal GmbH & Co. KG]( https://www.berlinonline.net/).

All software in this repository is published under the [MIT License](LICENSE).
