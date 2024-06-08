from PyPDF2 import PdfReader
import re

def scrappe_data(filename):
    reader = PdfReader(filename)
    page = reader.pages[0]
    text = page.extract_text()
    lineas = text.split("\n")

    # Definir el patrón regex correcto
    #patron_horas = r'((\bHORAS|\bHORA|\d{1,2}h\d{2}\s*-\s*\d{1,2}h\d{2})\b]'
    #patron = r'([\w\s\'"-]+)'


    for page in reader.pages:
        text = page.extract_text()
        lineas = text.split("\n")
        print(lineas)

        for line in lineas:
            # Búsqueda insensible a mayúsculas y minúsculas
            match_horas = re.search(r"(\bHORAS|\bHORA|\d{1,2}h\d{2}\s*-\s*\d{1,2}h\d{2})[A-Za-z0-9\s,\"']+", line)
            if match_horas:
                resultado_horas = match_horas.group(0).strip()
                resultado_L = match_horas.group(1).strip()

                print(f"{resultado_horas} |  {resultado_L}")
           

if __name__ == "__main__":
    scrappe_data("HORARIO.pdf")


def test():
    pdf = open("HORARIO.pdf", "rb")

    reader = PyPDF2.PdfReader(pdf)
    page = reader._get_page(0)
    content = page.extract_text()
    print(content)