#!/usr/bin/python3
""" Genera un albaran en formato excel y lo envia
por email.
"""
import shutil
import os
import sys
import json
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from openpyxl import load_workbook
from dotenv import load_dotenv

# Carga variables de entorno desde .env — resuelve PAIN_LOG #6, #12, #13
load_dotenv()

# Directorio raíz del proyecto — resuelve PAIN_LOG #10
PROJECT_ROOT = Path(__file__).resolve().parent.parent

__author__ = "Dario Fervenza"
__copyright__ = "Copyright 2023 Dario Fervenza"
__credits__ = ["Dario Fervenza"]

__version__ = "0.5"
__maintainer__ = "Dario Fervenza"
__email__ = "dario.fervenza.garcia@gmail.com"
__status__ = "Development"

class CrearAlbaran:
    """ Recibe como argumentos los
    parametros del albaran. Los procesa y
    los inserta en un archivo excel plantilla.
    Previamente copia esa plantilla a la carpeta
    de albaranes
    """
    def __init__(self, ruta: str):
        """ Recibe la ruta de la plantilla
        y crea los atributos que se van a usar
        Ademas extrae los datos de los argumentos
        """
        self.datos = sys.argv[1]
        self.datos_json = json.loads(self.datos)
        self.productos = sys.argv[2]
        self.productos_json = json.loads(self.productos)
        self.albaranes_lineas = sys.argv[3]
        self.albaranes_lineas_json = json.loads(self.albaranes_lineas)
        self.ruta = ruta
        self.dictionary_art_descrip = {}
        self.cantidades_totales = []
        self.dict_articulo_peso_neto_unitario = {}
        valores = self.datos_json[0]["fields"]
        self.num_albaran = valores["num_albaran"]
        self.fecha_albaran = valores["fecha_albaran"]
        self.cliente = valores["cliente"]
        self.direccion_calle_numero = valores["direccion_calle_numero"]
        self.direccion_piso = valores["direccion_piso"]
        self.direccion_localidad = valores["direccion_localidad"]
        self.direccion_cp = valores["direccion_cp"]
        self.pais = valores["pais"]
        self.cif_vat = valores["cif_vat"]
        self.num_pedidos_incluidos = valores["num_pedidos_incluidos"]
        self.transportista = valores["transportista"]
        self.incoterms = valores["incoterms"]
        self.bultos = valores["bultos"]
        self.medidas = valores["medidas"]
        # Usa variable de entorno o calcula desde PROJECT_ROOT — resuelve PAIN_LOG #10, #11, #12
        albaranes_dir = os.environ.get('ALBARANES_DIR', str(PROJECT_ROOT / 'albaranes'))
        os.makedirs(albaranes_dir, exist_ok=True)
        self.nueva_ruta = os.path.join(
            albaranes_dir,
            f"albaran {self.cliente} - {self.fecha_albaran}.xlsx"
        )
        os.rename(self.ruta, self.nueva_ruta)
        self.wb=load_workbook(self.nueva_ruta)
    def gen_descript_prductos(self):
        """ Crea diccionario del estilo:
         {"producto" : "descripcion"}
        """
        productos_json = \
            [producto["fields"] for producto in self.productos_json]
        lista_art = \
            [producto["codigo_articulo"] for producto in productos_json]
        list_descripcion = \
            [producto["descripcion"] for producto in productos_json]
        self.dictionary_art_descrip = dict(zip(lista_art, list_descripcion))
    def generar_lineas_albaran(self):
        """
        Crea diccionario del estilo:
            {"producto" : "peso neto"}
        Crea lista de codigos de articulo unicos
        Calcula cuantas lineas hay que insertar en el excel de
        albaranes
        Crea lista de cantidad albaranada por cada linea
        """
        albaranes_lineas_json = \
            [albaran["fields"] for albaran in self.albaranes_lineas_json]
        list_codigo_articulo = \
            [albaran["codigo_articulo"] for albaran in albaranes_lineas_json]
        list_cantidad_servida = \
            [albaran["cantidad_servida"] for albaran in albaranes_lineas_json]
        list_peso_neto_unidad = \
            [albaran["peso_neto"] for albaran in albaranes_lineas_json]
        self.dict_articulo_peso_neto_unitario = \
            dict(zip(list_codigo_articulo, list_peso_neto_unidad))
        self.articulos_unicos = list(set(list_codigo_articulo))
        self.lineas_a_escribir = len(self.articulos_unicos)
        for unico in self.articulos_unicos:
            cant_total = 0
            for art, cant in zip(list_codigo_articulo, list_cantidad_servida):
                if unico == art:
                    cant_total += cant
            self.cantidades_totales.append(cant_total)
    def insertar_datos_en_excel(self):
        """ Inserta los datos obtenidos en un
        archivo excel
        """
        hoja = self.wb["Hoja1"]
        hoja["E12"] = self.num_albaran
        hoja["E14"] = self.fecha_albaran
        hoja["J12"] = self.cliente
        hoja["J13"] = self.direccion_calle_numero
        hoja["N13"] = self.direccion_piso
        hoja["O13"] = self.direccion_localidad
        hoja["Q13"] = self.direccion_cp
        hoja["J14"] = self.pais
        hoja["M15"] = self.cif_vat
        hoja["B19"] = self.num_pedidos_incluidos
        hoja["I19"] = self.transportista
        hoja["R19"] = self.incoterms
        hoja["E36"] = self.bultos
        hoja["E38"] = self.medidas
        hoja["A47"] = self.cliente
        hoja["A48"] = self.direccion_calle_numero
        hoja["E48"] = self.direccion_piso
        hoja["F48"] = self.direccion_localidad
        hoja["H48"] = self.direccion_cp
        hoja["A49"] = self.pais
        fila_inicial = 23
        for i in range(self.lineas_a_escribir):
            fila_actual = fila_inicial + i
            hoja["A" + str(fila_actual)] = \
                self.articulos_unicos[i]
            hoja["D" + str(fila_actual)] = \
                self.dictionary_art_descrip[self.articulos_unicos[i]]
            hoja["M" + str(fila_actual)] = \
                self.cantidades_totales[i]
            hoja["O" + str(fila_actual)] = \
                self.dict_articulo_peso_neto_unitario[self.articulos_unicos[i]]
        self.wb.save(self.nueva_ruta)
    def send_email(self):
        """ Envia el email con el excel adjunto
        """
        sender_email = "my_email@example.com"
        receiver_email = "your_email@example.com"
        subject = "Albaran - " \
                + str(self.cliente) \
                + " - " \
                + str(self.fecha_albaran)
        message = "Albaran"
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))
        file_name_only = os.path.basename(self.nueva_ruta)
        file_path = self.nueva_ruta
        part = MIMEBase("application", "octet-stream")
        with open(file_path, "rb") as attachment:
            part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {file_name_only}")
        msg.attach(part)
        smtp_server = "smtp.example.com"
        smtp_port = 587
        smtp_username = "my_email@example.com"
        smtp_password = "super_secret_smtp_password"
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()


if __name__ == "__main__":
    # Resuelve PAIN_LOG #10, #12: rutas dinámicas desde PROJECT_ROOT o .env
    RUTA_ORIGINAL = os.environ.get(
        'PLANTILLA_ALBARANES',
        str(PROJECT_ROOT / '23AKP08_PLANTILLA.xlsx')
    )
    albaranes_dir = os.environ.get('ALBARANES_DIR', str(PROJECT_ROOT / 'albaranes'))
    os.makedirs(albaranes_dir, exist_ok=True)
    RUTA = os.path.join(albaranes_dir, 'albaran_prov.xlsx')
    shutil.copy(RUTA_ORIGINAL, RUTA)
    objeto = CrearAlbaran(RUTA)
    objeto.gen_descript_prductos()
    objeto.generar_lineas_albaran()
    objeto.insertar_datos_en_excel()
    objeto.send_email()
