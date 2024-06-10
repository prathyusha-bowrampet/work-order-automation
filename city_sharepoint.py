from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.files.file import File
from office365.sharepoint.documentmanagement.document_set import DocumentSet
import codecs
import configparser
import csv
import json
import urllib.parse


def int2byte(i):
    hex_string = ''

class CitySharepoint:
    """
    Access to SharePoit

    :param city: String, City name.
    :param state: String, City state.

    """
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.sharepoint_config = config['SharePoint']

        # Get sharepoint credentials
        # Initialize the client credentials
        user_credentials = UserCredential(self.sharepoint_config['user'], self.sharepoint_config['pass'])

        # create client context object
        self.ctx = ClientContext(self.sharepoint_config['url']).with_credentials(user_credentials)
        self.city_feeders_list = None
        self.city_feeder_segs_list = None
        self.city_chambers_list = None

    def create_sharepoint_directory(self, city):
        """
        Creates a folder in the sharepoint directory.
        """
        # '/Shared Documents/Forms/Document/City Data/QGIS_layer/design level 1'
        # '{base}QGIS_layer/design level 1

        base_dir = "{base}{city}".format(base=self.sharepoint_config['base_dir'], city=city)
        folder = self.ctx.web.folders.add(f'{base_dir}').execute_query()
        if folder.exists:
            return folder
        else:
            print("Folder not found")
            return False

    def upload_to_sharepoint(self, city: str, file_name: str, file_content):
        target_folder = self.create_sharepoint_directory(city)

        if target_folder:
            try:
                target_folder.upload_file(file_name, file_content).execute_query()
            except ClientRequestException as e:
                print("file did not save.")
                print(e)

    # Get the list of feeders to process
    def get_feeder_list(self):
        file_name = "{base}Feeder List.csv".format(base=self.sharepoint_config['base_dir'])
        file_response = File.open_binary(self.ctx, file_name)
        txt_file = file_response.content.decode('utf-8-sig', 'surrogatepass') or '\0'
        return txt_file

    def get_city_feeders(self, city, reset=False):
        if not self.city_feeders_list or reset:
            file_name = "{base}feeder/feeder_{city}.csv".format(base=self.sharepoint_config['qgis_base_dir'],
                                                                city=city)
            file_response = File.open_binary(self.ctx, file_name)
            txt_file = file_response.content.decode('utf-8-sig', 'surrogatepass') or '\0'
            self.city_feeders_list = txt_file.splitlines()
        feeders = csv.DictReader(self.city_feeders_list)
        return feeders

    def get_city_feeder_seg(self, city, reset=False):
        if not self.city_feeder_segs_list or reset:
            file_name = "{base}feeder_seg/feeder_seg_{city}.csv".format(base=self.sharepoint_config['qgis_base_dir'],
                                                                        city=city)
            file_response = File.open_binary(self.ctx, file_name)
            txt_file = file_response.content.decode('utf-8-sig', 'surrogatepass') or '\0'
            self.city_feeder_segs_list = txt_file.splitlines()
        feeder_segs = csv.DictReader(self.city_feeder_segs_list)
        return feeder_segs

    def get_city_chambers(self, city, reset=False):
        if not self.city_chambers_list or reset:
            file_name = "{base}chamber/chamber_{city}.csv".format(base=self.sharepoint_config['qgis_base_dir'],
                                                                        city=city)
            file_response = File.open_binary(self.ctx, file_name)
            txt_file = file_response.content.decode('utf-8-sig', 'surrogatepass') or '\0'
            self.city_chambers_list = txt_file.splitlines()
        chambers = csv.DictReader(self.city_chambers_list)
        return chambers
