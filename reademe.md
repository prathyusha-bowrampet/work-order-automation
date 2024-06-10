# **Overview**
The CitySharepoint class helps you interact with a SharePoint site. You can use it to create folders, upload files, and retrieve data for specific cities.

See [Readme](https://dev.azure.com/SNOSoftwareEngineering/Mergin%20maps%20and%20QGIS%20scripts/_git/work-order-automation?path=/reademe.md&_a=preview) in repo

## Initialization
__init__():
- Description: Initializes the class by reading SharePoint settings from a config.ini file and setting up authentication.
- Configuration:
- [ ] Reads SharePoint URL, user credentials, and base directories from config.ini.
- [ ] Sets up user credentials and creates a ClientContext object.

def __init__(self):

    config = configparser.ConfigParser()
    config.read('config.ini')
    self.sharepoint_config = config['SharePoint']
    user_credentials = UserCredential(self.sharepoint_config['user'], self.sharepoint_config['pass'])
    self.ctx = ClientContext(self.sharepoint_config['url']).with_credentials(user_credentials)
    self.city_feeders_list = None
    self.city_feeder_segs_list = None
    self.city_chambers_list = None

## Methods:
### **'create_sharepoint_directory(city)':**
Description: Creates a folder in SharePoint for the specified city.

**Parameters:**
- [ ] city (str): The name of the city.
- [ ] Returns: The created folder object or False if the folder creation fails.

def create_sharepoint_directory(self, city):

    base_dir = "{base}{city}".format(base=self.sharepoint_config['base_dir'], city=city)
    folder = self.ctx.web.folders.add(f'{base_dir}').execute_query()
    if folder.exists:
        return folder
    else:
        print("Folder not found")
        return False
## 'upload_to_sharepoint(city, file_name, file_content)':
Description: Uploads a file to the specified city's folder in SharePoint.

**Parameters:**
- [ ] city (str): The name of the city.
- [ ] file_name (str): The name of the file to upload.
- [ ] file_content: The content of the file to upload.

def upload_to_sharepoint(self, city: str, file_name: str, file_content):

    target_folder = self.create_sharepoint_directory(city)
    if target_folder:
        try:
            target_folder.upload_file(file_name, file_content).execute_query()
        except ClientRequestException as e:
            print("File did not save.")
            print(e)
## 'get_feeder_list()':
Description: Retrieves the "Feeder List.csv" file from SharePoint.
Returns: The text content of the file.

def get_feeder_list(self):

    file_name = "{base}Feeder List.csv".format(base=self.sharepoint_config['base_dir'])
    file_response = File.open_binary(self.ctx, file_name)
    txt_file = file_response.content.decode('utf-8-sig', 'surrogatepass') or '\0'
    return txt_file
## 'get_city_feeders(city, reset=False)':
Description: Retrieves a CSV file with feeder information for a specific city.

**Parameters:**
- [ ] city (str): The name of the city.
- [ ] reset (bool): If True, resets the cached data and fetches it again.
- [ ] Returns: A list of dictionaries representing the feeder data.

def get_city_feeders(self, city, reset=False):

    if not self.city_feeders_list or reset:
        file_name = "{base}feeder/feeder_{city}.csv".format(base=self.sharepoint_config['qgis_base_dir'], city=city)
        file_response = File.open_binary(self.ctx, file_name)
        txt_file = file_response.content.decode('utf-8-sig', 'surrogatepass') or '\0'
        self.city_feeders_list = txt_file.splitlines()
    feeders = csv.DictReader(self.city_feeders_list)
    return feeders

## 'get_city_feeder_seg(city, reset=False)':
Description: Retrieves a CSV file with feeder segment information for a specific city.

**Parameters:**
- [ ] city (str): The name of the city.
- [ ] reset (bool): If True, resets the cached data and fetches it again.
- [ ] Returns: A list of dictionaries representing the feeder segment data.

def get_city_feeder_seg(self, city, reset=False):

    if not self.city_feeder_segs_list or reset:
        file_name = "{base}feeder_seg/feeder_seg_{city}.csv".format(base=self.sharepoint_config['qgis_base_dir'], city=city)
        file_response = File.open_binary(self.ctx, file_name)
        txt_file = file_response.content.decode('utf-8-sig', 'surrogatepass') or '\0'
        self.city_feeder_segs_list = txt_file.splitlines()
    feeder_segs = csv.DictReader(self.city_feeder_segs_list)
    return feeder_segs
**'get_city_chambers(city, reset=False)':**

Description: Retrieves a CSV file with chamber information for a specific city.

**Parameters**:
- [ ] city (str): The name of the city.
- [ ] reset (bool): If True, resets the cached data and fetches it again.
- [ ] Returns: A list of dictionaries representing the chamber data.

def get_city_chambers(self, city, reset=False):

    if not self.city_chambers_list or reset:
        file_name = "{base}chamber/chamber_{city}.csv".format(base=self.sharepoint_config['qgis_base_dir'], city=city)
        file_response = File.open_binary(self.ctx, file_name)
        txt_file = file_response.content.decode('utf-8-sig', 'surrogatepass') or '\0'
        self.city_chambers_list = txt_file.splitlines()
    chambers = csv.DictReader(self.city_chambers_list)
    return chambers





