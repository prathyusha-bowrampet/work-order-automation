import azure.functions as func
from feeder import get_feeders, WorkOrder
import csv
from city_sharepoint import CitySharepoint
from create_pdf import CreatePDF

app = func.FunctionApp()


@app.function_name(name="GenWorkOrder")
@app.route(route="create")
def create_function(req: func.HttpRequest) -> func.HttpResponse:
    #my_doc = CreatePDF()
    #sections = []
    #for i in range(100):
    #    sections.append(("This is Paragraph number %s. " % i) * 20)
    #bytes_file_obj = my_doc.make_page('<b>Feeder Stage 1 Work Order –</b> aaaaa (bbbbbbb)', sections)

    #sharepoint.upload_to_sharepoint("Simi Valley", "test.pdf", bytes_file_obj)
    get_feeders()
    return func.HttpResponse("HttpExample function processed a request!")
