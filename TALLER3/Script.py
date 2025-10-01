import os
import csv
import json
import xml.etree.ElementTree as ET

# Archivo CSV de entrada
csv_file = "Usuarios.csv"

# Archivos de salida
json_file = "Usuarios.json"
xml_file = "Usuarios.xml"

# Leer datos del CSV
datos = []
print("\n------- CSV -------")
with open(csv_file, newline="", encoding="utf-8") as file:
    lector = csv.reader(file, delimiter=";")
    encabezado = next(lector)  # Ignorar encabezado
    for fila in lector:
        datos.append({
            "Nombre": fila[1],
            "Apellido": fila[2],
            "CampoExtra": fila[4],
            "UltimoCampo": fila[-1],
            "Columnas": len(fila)
        })
        print(fila[1], fila[2], fila[4], fila[-1], "Columnas:", len(fila))

print("\n------- JSON -------")
if not os.path.exists(json_file):
    with open(json_file, "w", encoding="utf-8") as jf:
        json.dump(datos, jf, indent=4, ensure_ascii=False)
        print(f"Exportado a {json_file}")
else:
    with open(json_file, "r", encoding="utf-8") as jf:
        print(jf.read())

print("\n------- XML ------")
if not os.path.exists(xml_file):
    root = ET.Element("Usuarios")
    for d in datos:
        usuario = ET.SubElement(root, "Usuario")
        for k, v in d.items():
            ET.SubElement(usuario, k).text = str(v)

    tree = ET.ElementTree(root)
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)
    print(f"Exportado a {xml_file}")
else:
    with open(xml_file, "r", encoding="utf-8") as xf:
        print(xf.read())
