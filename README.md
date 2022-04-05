# CKAN Metadata Updater

This is a Python tool to update a CKAN dataset's metadata by:

- Getting the current metadata through CKAN's API.
- Modifying the metadata locally by executing a series of steps.
- Pushing the metadata back to CKAN.

The updater can be used to automate updating the metadata of a dataset at specific moments, e.g. when the data has been updated.
If the dataset lives in a git repository, the updater could be part of a workflow that is triggered (via [GitHub Actions](https://github.com/features/actions) or [GitLab CI](https://docs.gitlab.com/ee/ci/)) when a new commit is made to a specific branch, or a release has been tagged.

## Requirements

- CKAN Metadata Updater has been developed for Python 3.
- It relies on the [ckanapi](https://github.com/ckan/ckanapi) module.

## Installation

```shell
# Check out the repository:
% git checkout https://github.com/berlinonline/ckan_metadata_updater.git

# Create a Python venv (virtual environment) in the new directory:
% cd ckan_metadata_updater
ckan_metadata_updater % python -m venv updater

# Activate the venv:
ckan_metadata_updater % . updater/bin/activate

# Install the dependencies into the venv:
(updater) ckan_metadata_updater % pip install -r requirements.txt
```

## Using the Metadata Updater

### Prerequisites

To work, the updater has a few prerequisites:

#### Patch Metadata

We need a JSON file with the dataset metadata that we want to patch over the existing metadata.
The default location where the updater is looking is `metadata/dataset.json`.
The file needs to conform to the format accepted by the `package_update` method of the CKAN API, and needs to at least have the `id` field set:

```json
{
    "id": "name_or_id_of_the_dataset"
}
```

#### Config File

We also need a JSON file with configuration settings.
The default location is `conf/ckan_settings.json`.
At the least, this needs to contain the base URL of the CKAN installation we want to connect to.
Other configuration can be added if needed.

```json
{
    "ckan_base": "https://url.of.ckan.net"
}
```

#### API Token

Because writing to CKAN usually requires authentication, we need an environment variable `CKAN_TOKEN` with a CKAN API token that grants write access to the dataset we want to change.

### Running the Updater

The simplest way to run the CKAN Metadata Updater is as follows:

```python
from berlinonline.ckan_tools.ckan_metadata_updater import CKANMetadataUpdater

updater = CKANMetadataUpdater()
updater.run()
```

This will:

- get the current metadata from CKAN
- run two steps to update the metadata:
    - apply the patch metadata
    - set the attribute `date_updated` to today's date
- upload the updated metadata to CKAN

#### Custom Steps

The actual steps that the updater will run are defined in its `steps` attribute.

## License

This material is copyright ©[BerlinOnline Stadtportal GmbH & Co. KG]( https://www.berlinonline.net/).

All software in this repository is published under the [MIT License](LICENSE).
