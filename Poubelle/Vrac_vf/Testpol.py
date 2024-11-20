import pandas as pd

# Charger le fichier CSV
file_path = "C:\\Users\\arthu\\Downloads\\IMOCA2019_1deg.csv"  # Remplacez par le chemin de votre fichier CSV local
imoca_data = pd.read_csv(file_path)

# Enregistrer au format .txt avec une séparation par tabulation
output_path = "IMOCA_Polar_Output.txt"
imoca_data.to_csv(output_path, sep='\t', index=False)

print(f"Fichier enregistré sous {output_path}")
