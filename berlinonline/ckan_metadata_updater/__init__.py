import argparse
from datetime import date
import json
import logging
import os
from pathlib import Path
import sys
from ckanapi import RemoteCKAN

from berlinonline.ckan_metadata_updater.steps import apply_patch, set_date_updated


class CKANMetadataUpdater:

    def read_json(self, path: str):
        try:
            return json.load(open(path))
        except FileNotFoundError as err:
            logging.exception(err)
            sys.exit(1)
        except json.decoder.JSONDecodeError as err:
            logging.exception(err)
            sys.exit(1)
        except BaseException as err:
            print(f"Unexpected {err}, {type(err)}")
            raise

    def init_parser(self):
        parser = argparse.ArgumentParser(
            description="Get the current metadata of a dataset from CKAN, modify it locally and write it back to CKAN.")
        parser.add_argument('-p', '--patch',
                            default=Path('metadata/dataset.json'),
                            type=Path,
                            help="Path to the JSON file containing the new (partial) metadata. Default is `metadata/dataset.json`.")
        parser.add_argument('-c', '--config',
                            default=Path('conf/ckan_settings.json'),
                            type=Path,
                            help="Path to the JSON file containing the settings for connecting to CKAN. Default is `conf/ckan_settings.json`.")
        parser.add_argument('-d', '--date',
                            default=date.today().isoformat(),
                            help="The date to be used as `date_updated`. Default is today.")

        return parser

    def __init__(self, config=None):
        logging.basicConfig(level=logging.INFO)
        parser = self.init_parser()
        args = parser.parse_args()
        if not config:
            logging.info(f" reading patch data from {args.patch}")
            self.patch_data = self.read_json(args.patch)

            logging.info(f" reading config from {args.config}")
            self.conf_data = self.read_json(args.config)
        else:
            self.patch_data = config['patch_data']
            self.conf_data = config['conf_data']

        datenregister_base = self.conf_data['ckan_base']

        api_token = os.environ['CKAN_TOKEN']
        ua_string = 'berlin_dataset_updater/1.0 (+https://github.com/berlinonline/berlin_dataset_updater)'

        logging.info(f" setting up CKAN connector at {datenregister_base} (as '{ua_string}')")
        self.connector = RemoteCKAN(datenregister_base, apikey=api_token, user_agent=ua_string)

        self.steps = [
            {"function": apply_patch, "parameters": [self.patch_data]},
            {"function": set_date_updated, "parameters": [args.date]}
        ]

    def get_remote_metadata(self, dataset_id: str):
        logging.info(f" reading remote metadata for {dataset_id}")
        self.dataset_metadata = self.connector.action.package_show(id=dataset_id)

    def write_remote_metadata(self):
        logging.info(f" writing metadata")

    def run(self):
        # get metadata from CKAN
        self.get_remote_metadata(self.patch_data['id'])

        # execute steps to modify metadata
        for step in self.steps:
            logging.info(f" running {step['function']}")
            _function = step['function']
            params = step['parameters']
            _function(self.dataset_metadata, *params)

        # write metadata back to CKAN
        self.write_remote_metadata()
