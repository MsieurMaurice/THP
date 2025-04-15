import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta
import numpy as np

# 💾 Paramètres
MEASURE_INTERVAL_SECONDS = 10  # En secondes


# 📥 Lecture des données
def read_log_file(filename):
    df = pd.read_csv(filename, header=None, names=["timestamp", "temp", "pressure", "humidity", "battery"])
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
    df.set_index("datetime", inplace=True)
    return df


# 🧠 Injection des NaN en cas de données manquantes
def fill_missing_data_resample(df, interval_seconds=10):
    """
    Recrée les échantillons manquants en reséchantillonnant la série à intervalle régulier.
    Les valeurs absentes seront remplacées par NaN.
    """
    df_resampled = df.resample(f"{interval_seconds}s").mean()
    return df_resampled


# 📊 Affichage graphique avec infobulle de date et heure
def plot_data(df):
    """
    Affiche les 4 paramètres (temp, press, hum, batt) dans une grille 2x2.
    Les NaN dans les données créent automatiquement des coupures dans les courbes.
    Affiche aussi une infobulle avec la date et l'heure au passage de la souris.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharex=True)
    fig.suptitle("Mesures environnementales", fontsize=16)

    # Subplots
    df["temp"].plot(ax=axes[0, 0], color='red', label='Température (°C)')
    axes[0, 0].set_ylabel("Temp (°C)")
    axes[0, 0].legend()

    df["pressure"].plot(ax=axes[0, 1], color='blue', label='Pression (hPa)')
    axes[0, 1].set_ylabel("Pression (hPa)")
    axes[0, 1].legend()

    df["humidity"].plot(ax=axes[1, 0], color='green', label='Humidité (%)')
    axes[1, 0].set_ylabel("Humidité (%)")
    axes[1, 0].legend()

    df["battery"].plot(ax=axes[1, 1], color='orange', label='Batterie (V)')
    axes[1, 1].set_ylabel("Tension (V)")
    axes[1, 1].legend()

    # X-axis formatting
    for ax in axes[1, :]:
        ax.set_xlabel("")

    date_text = fig.text(.5, 0.93, "", ha="center", va="center", fontsize=9)
    fig.autofmt_xdate()

    # Ajouter un tooltip (infobulle) qui s'affiche lorsque la souris passe sur les graphiques
    # annotation = axes[0, 0].annotate("", xy=(0, 0), xytext=(0, 0),
    #                                  textcoords="offset points", ha="center", va="center", fontsize=10,
    #                                  bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5"),
    #                                  arrowprops=dict(arrowstyle="->", color="black"))
    #
    # annotation.set_visible(False)

    def on_move(event):
        # Si la souris est en dehors des axes, on ignore
        # if event.inaxes not in axes:
        #     annotation.set_visible(False)
        #     return

        # On récupère la position de la souris
        x_pos = event.xdata
        if x_pos is None:
            return

        # Trouver la date la plus proche
        # Calculer la différence absolue entre x_pos et toutes les dates de l'index
        closest_index = abs(df.index.values.astype(np.int64) - np.int64(x_pos) * 1000000000).argmin()
        closest_date = df.index[closest_index]

        # Mettre à jour le texte de l'annotation
        # annotation.xy = (x_pos, df.loc[closest_date, 'temp'])  # Utilisation de la température comme exemple
        # annotation.set_text(f"{closest_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # Rendre visible l'annotation
        # annotation.set_visible(True)
        date_text.set_text(f"{closest_date.strftime('%Y-%m-%d %H:%M:%S')}")
        fig.canvas.draw_idle()

    # Connecter l'événement de la souris au callback
    for ax in axes.flatten():
        fig.canvas.mpl_connect("motion_notify_event", on_move)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


def generate_fake_dat_file(filename="test3days.dat", days=3, interval_sec=10, missing_ratio=0.02):
    """
    Génère un fichier .dat simulant les mesures Arduino sur plusieurs jours.
    """
    start_time = datetime.now()
    total_points = int((days * 24 * 60 * 60) / interval_sec)
    current_time = start_time

    with open(filename, "w") as f:
        for i in range(total_points):
            if random.random() < missing_ratio:
                # Simule une mesure manquante
                current_time += timedelta(seconds=interval_sec)
                continue

            timestamp = int(current_time.timestamp())
            temp = round(random.uniform(18, 25), 2)
            press = round(random.uniform(1005, 1025), 2)
            hum = round(random.uniform(40, 60), 2)
            batt = round(random.uniform(3.5, 4.1), 2)
            line = f"{timestamp},{temp},{press},{hum},{batt}\n"
            f.write(line)

            current_time += timedelta(seconds=interval_sec)

    print(f"Fichier généré : {filename} ({days} jour(s), intervalle {interval_sec}s)")


# 🚀 Programme principal
if __name__ == "__main__":
    # Générer un fichier de test
    generate_fake_dat_file(filename="test3days.dat", days=3, interval_sec=10, missing_ratio=0.02)

    # Lire les données et appliquer le resampling
    df = read_log_file("test3days.dat")
    df = fill_missing_data_resample(df, MEASURE_INTERVAL_SECONDS)

    # Afficher les graphiques avec infobulle de date
    plot_data(df)
