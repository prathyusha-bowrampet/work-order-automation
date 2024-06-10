from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.documentmanagement.document_set import DocumentSet
import configparser
import json


class CitySharepoint:
    """
    Access to SharePoit

    :param city: String, City name.
    :param state: String, City state.

    """
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        print(config.sections())
        self.sharepoint_config = config['SharePoint']

        # Get sharepoint credentials
        # Initialize the client credentials
        user_credentials = UserCredential(self.sharepoint_config['user'], self.sharepoint_config['pass'])

        # create client context object
        self.ctx = ClientContext(self.sharepoint_config['url']).with_credentials(user_credentials)

    def create_sharepoint_directory(self):
        """
        Creates a folder in the sharepoint directory.
        """
        # '/Shared Documents/Forms/Document/City Data/QGIS_layer/design level 1'
        # '{base}QGIS_layer/design level 1

        base_dir = "{base}QGIS_layer/design level 1".format(base=self.sharepoint_config['base_dir'])
        folder = self.ctx.web.folders.add(f'{base_dir}').execute_query()
        if folder.exists:
            return folder
        else:
            print("Folder not found")
            return False

    def upload_to_sharepoint(self, file_name: str):
        target_folder = self.create_sharepoint_directory()

        if target_folder:
            with open(file_name, 'rb') as content_file:
                file_content = content_file.read()
                try:
                    target_folder.upload_file(file_name, file_content).execute_query()
                except ClientRequestException as e:
                    print("file did not save.")
                    print(e)
