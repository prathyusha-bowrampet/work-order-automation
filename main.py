from create_pdf import CreatePDF

from pathlib import Path
if __name__ == '__main__':
    my_doc = CreatePDF()
    sections = []
    for i in range(100):
        sections.append(("This is Paragraph number %s. " % i) * 20)
    my_doc.make_page('<b>Feeder Stage 1 Work Order –</b> aaaaa (bbbbbbb)', sections)
