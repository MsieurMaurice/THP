import subprocess
import tkinter as tk
import shutil
import serial
import serial.tools.list_ports
from os.path import expanduser

# Variables
arduino_library_path = "C:/Users/antoine.douchin/Documents/Arduino/libraries"
local_library_path = "../arduino/Lib"
arduino_cli_path = "../exec/arduino-cli/arduino-cli.exe"  # Assurez-vous que arduino-cli est dans le PATH ou spécifiez le chemin complet
# Variables
home_dir = expanduser("~")
arduino_cli_path = "arduino-cli"  # Assurez-vous que arduino-cli est dans le PATH ou ajustez le chemin complet


# arduino_board = "arduino:avr:mega"  # Identifiant de la carte Arduino Mega 2560
# arduino_board = "adafruit:avr:protrinket5ftdi" # Identifiant pour la carte Trinket Pro 5V
arduino_board="adafruit:samd:adafruit_feather_m0"

port = "/dev/ttyACM0"  # Port série où est connecté le module FTDI
# port = "COM3"  # Port COM où est connectée la carte

# sketch_path = f"../arduino/cinema/cinema.ino"
# sketch_path = f"../arduino/cinema_simple/cinema_simple.ino"
sketch_path = f"../arduino/thp/thp.ino"

def check_and_close_serial_port(port_name):
    # Obtenir la liste des ports série disponibles
    available_ports = serial.tools.list_ports.comports()

    # Rechercher le port spécifié
    for port in available_ports:
        if port.device == port_name:
            try:
                # Essayer d'ouvrir le port pour vérifier s'il est déjà ouvert
                ser = serial.Serial(port_name)
                if ser.is_open:
                    print(f"{port_name} est déjà ouvert. Fermeture du port.")
                    ser.close()
                else:
                    print(f"{port_name} n'est pas ouvert.")
                return
            except serial.SerialException as e:
                print(f"Erreur lors de l'accès à {port_name}: {e}")
                return

    print(f"{port_name} n'est pas disponible.")

def update_library():
    shutil.copytree(local_library_path, arduino_library_path,dirs_exist_ok=True)


def compile(sketch_path, arduino_board):
    # Compilation du sketch
    compile_command = [arduino_cli_path, "compile", "--fqbn", arduino_board, sketch_path]
    try:
        subprocess.run(compile_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(e.stderr.decode("utf-8"))
        return False
    else:
        print("Compilation réussie.")
        return True

def upload(sketch_path, arduino_board, port):
    # Téléchargement du sketch sur la carte
    upload_command = [arduino_cli_path, "upload", "-p", port, "--fqbn", arduino_board, sketch_path]
    try:
        result = subprocess.run(upload_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(e.stderr.decode('latin-1'))
    else:
        print("Téléchargement réussi.")


def on_button_click(value):
    global update_launch
    update_launch = value
    root.destroy()  # Ferme la fenêtre après le clic
def ask_update_launch():
    global root
    root = tk.Tk()
    root.withdraw()  # Cache la fenêtre principale

    # Création d'une nouvelle fenêtre de dialogue
    dialog = tk.Toplevel()
    dialog.title("Action")

    # Définition de la taille de la fenêtre
    dialog_width = 222
    dialog_height = 100

    # Récupération des dimensions de l'écran
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()

    # Calcul des coordonnées pour centrer la fenêtre
    pos_x = (screen_width - dialog_width) // 2
    pos_y = (screen_height - dialog_height) // 2

    # Appliquer la position et la taille
    dialog.geometry(f"{dialog_width}x{dialog_height}+{pos_x}+{pos_y}")

    # Interface
    tk.Label(dialog, text="Choisissez une action :").pack(pady=10)

    frame = tk.Frame(dialog)
    frame.pack(pady=5)

    tk.Button(frame, text="Compile", command=lambda: on_button_click(1)).pack(side=tk.LEFT, padx=5)
    tk.Button(frame, text="Upload", command=lambda: on_button_click(0)).pack(side=tk.LEFT, padx=5)
    tk.Button(frame, text="C&U", command=lambda: on_button_click(-1)).pack(side=tk.LEFT, padx=5)

    dialog.mainloop()


if __name__ == "__main__":
    only_upload = False
    update_launch = 0
    ask_update_launch()
    if update_launch == -1:
        # update_library()
        if compile(sketch_path, arduino_board):
            upload(sketch_path, arduino_board, port)
    if update_launch == 0:
        upload(sketch_path, arduino_board, port)
    if update_launch == 1:
        # update_library()
        compile(sketch_path, arduino_board)