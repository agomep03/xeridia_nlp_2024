import os
import subprocess
import re

def generate_portable_requirements(output_file="requirements.txt"):
    try:
        # Capturar las dependencias usando pip freeze
        result = subprocess.run(
            ["pip", "freeze"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        requirements = result.stdout.splitlines()

        # Filtrar dependencias no portables
        portable_requirements = []
        for req in requirements:
            if " @ file://" not in req:  # Excluir dependencias con rutas locales
                portable_requirements.append(req)
            else:
                # Extraer solo el nombre del paquete y buscar su versión en PyPI
                match = re.match(r"^([\w\-]+) @ file://", req)
                if match:
                    portable_requirements.append(f"{match.group(1)}")

        # Guardar en el archivo de salida
        with open(output_file, "w") as f:
            f.write("\n".join(portable_requirements))

        print(f"Archivo portable '{output_file}' generado exitosamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar pip freeze: {e.stderr}")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    output_file = "requirements.txt"
    if len(os.sys.argv) > 1:
        output_file = os.sys.argv[1]
    generate_portable_requirements(output_file)
