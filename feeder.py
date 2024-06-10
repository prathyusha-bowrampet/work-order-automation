import csv
import logging

from city_sharepoint import CitySharepoint
from create_pdf import CreatePDF
import io


def get_feeders():
    sharepoint = CitySharepoint()
    work_list = sharepoint.get_feeder_list().splitlines()
    feeders = csv.DictReader(work_list)
    workorder_creator = CreatePDF()
    workorders = {}
#    with open("error.log", "w") as e_log:
    for feeder_to_process in feeders:
        if feeder_to_process['City'] in workorders.keys():
            workorders[feeder_to_process['City']].append(WorkOrder(feeder_to_process['FG number'],
                                                        feeder_to_process['City']))
        else:
            workorders[feeder_to_process['City']] = [WorkOrder(feeder_to_process['FG number'],
                                                    feeder_to_process['City'])]

    # Output data stream
    str_file_obj = io.StringIO()

    # Create work csv
    work_csv_header = ['City', 'FG number', 'Status']
    work_csv = csv.DictWriter(str_file_obj, fieldnames=work_csv_header)
    work_csv.writeheader()
    for city in workorders:
#            e_log.write("City: {}\n".format(city))
        city_file = city.replace(" ", "_")
        city_feeders = sharepoint.get_city_feeders(city_file, True)
        city_feeder_segs = sharepoint.get_city_feeder_seg(city_file, True)
        city_chambers = sharepoint.get_city_chambers(city_file, True)
        workorder_set = workorders[city]
        for workorder in workorder_set:
            feeder_status = 'No feeder file found. {}'.format(city_file)
            for feeder in city_feeders:
                if feeder['ID'] == workorder.fg:
                    workorder.set_type(feeder['Type'])
                    workorder.set_ends(feeder['AEnd'], feeder['BEnd'])
                    workorder.length = int(float(feeder['LengthFt']))
                    workorder.set_feeder_collection(feeder['Group'])

                    if feeder['AsBuiltYN'].upper() == 'N':
                        feeder_status = "As built NO Group {}".format(workorder.fg)
                        break

                    num_segs = 0
                    seg_asbuilt = True
                    for feeder_seg in city_feeder_segs:
                        if feeder_seg['Group'] == workorder.fg:
                            workorder.add_feeder_seg(feeder_seg)
#                                e_log.write("Feeder seg: '{}', Asbuilt: '{}'\n".format(feeder_seg['ID'],
#                                                                                   feeder_seg['AsBuiltYN']))
                            if feeder_seg['AsBuiltYN'].upper() == 'N':
                                seg_asbuilt = False
                            num_segs += 1
                    # Reset segs
                    city_feeder_segs = sharepoint.get_city_feeder_seg(city_file)

                    if not seg_asbuilt:
                        feeder_status = "At least 1 segment is as built no"
                        workorder.segs = []
                        break

                    if num_segs == 0:
                        feeder_status = "No segs in Group {}".format(workorder.fg)
                        break

                    feeder_status = "Found {} segs.".format(num_segs)

                    # Get chamber list
                    current_chamber = feeder['AEnd']
                    while current_chamber:
                        chamber_found = False
                        for chamber in city_chambers:
                            if chamber['ID'] == current_chamber:
                                if chamber['WKT'] == "POINT EMPTY":
                                    feeder_status = "{} Chamber {} No Lat Long.".format(feeder_status, current_chamber)
                                    break
                                workorder.add_chamber(chamber)
                                chamber_found = True
                                break
                        # reset city_chambers
                        feeder_status = "{} {}, ".format(feeder_status, current_chamber)
                        city_chambers = sharepoint.get_city_chambers(city_file)

                        if not chamber_found:
                            feeder_status = "{} Chamber {} not found.".format(feeder_status, current_chamber)
                            break

                        current_chamber = workorder.get_next_chamber(current_chamber)

                    end_check = workorder.check_seg_ends()
                    if not end_check[0] or not end_check[1]:
                        feeder_status = "{} Feeder ends don't match feeder_seg ends.".format(feeder_status)
                        break

                    bend = workorder.get_b_chamber()
                    if not bend or bend['ID'] != workorder.b_end:
                        feeder_status = "{} Did not reach B End.".format(feeder_status, current_chamber)
                        workorder.chambers = []
                        break

            # reset city_feeders
            city_feeders = sharepoint.get_city_feeders(city_file)
            pdf_file_obj = workorder_creator.make_page(workorder, "Feeder Stage 1")

            if pdf_file_obj:
                sharepoint.upload_to_sharepoint(workorder.city, "{}.pdf".format(workorder.fg), pdf_file_obj)

            work_csv.writerow({'City': workorder.city,
                               'FG number': workorder.fg,
                               'Status': feeder_status})
#                e_log.write("City: {}, City Ref: {}, FG: {}, Found: {}\n".format(workorder.city,
#                                                                                 workorder.city_ref,
#                                                                                 workorder.fg,
#                                                                                 feeder_status))
        str_file_obj.seek(0)
        sharepoint.upload_to_sharepoint("", "Feeder List out.csv", str_file_obj)


class WorkOrder:
    def __init__(self, feeder_group: str, city: str):
        self.fg = feeder_group
        self.fc = None
        self.city = city
        feeder_parts = feeder_group.split("-")
        self.city_ref = feeder_parts[0]
        self.a_end = None
        self.b_end = None
        self.length = None
        self.feeder_type = None
        self.segs = []
        self.chambers = []

    def set_ends(self, a_end, b_end):
        self.a_end = a_end
        self.b_end = b_end

    def set_type(self, feeder_type):
        self.feeder_type = feeder_type

    def set_feeder_collection(self, fc):
        self.fc = fc

    def add_feeder_seg(self, seg_inf):
        self.segs.append(seg_inf)

    def add_chamber(self, chamber_inf):
        if chamber_inf not in self.chambers:
            self.chambers.append(chamber_inf)

    def check_seg_ends(self):
        a_end = False
        b_end = False
        for seg in self.segs:
            if seg['AEnd'] == self.a_end:
                a_end = True
            if seg['BEnd'] == self.b_end:
                b_end = True
        return [a_end, b_end]

    def get_next_chamber(self, a_end):
        for seg in self.segs:
            if seg['AEnd'] == a_end:
                return seg['BEnd']
        # A end not found
        return False

    def get_a_chamber(self):
        if len(self.chambers) > 0:
            return self.chambers[0]
        else:
            return False

    def get_b_chamber(self):
        if len(self.chambers) > 0:
            return self.chambers[-1]
        else:
            return False

    def length_inc_loops(self):
        loop_len = self.length
        num_chambers = len(self.chambers)
        if num_chambers > 2:
            loop_len = loop_len + (60 * (num_chambers-2))
        return loop_len

    def num_seals(self):
        num_seals = 0
        num_chambers = len(self.chambers)
        if num_chambers > 2:
            num_seals = (num_chambers-2) * 2
        return num_seals

    def num_couplers(self):
        num_couplers = 0
        num_chambers = len(self.chambers)
        if num_chambers > 2:
            num_couplers = num_chambers - 2
        return num_couplers

