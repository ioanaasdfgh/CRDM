# Numele fisierului de intrare si de iesire
nume_fisier_intrare = 'fisier_intrare.txt'
nume_fisier_iesire = 'fisier_iesire.txt'

# Citirea datelor din fisierul de intrare
with open(nume_fisier_intrare, 'r') as fisier_intrare:
    continut_intrare = fisier_intrare.read()

# Salvarea datelor în fisierul de iesire
with open(nume_fisier_iesire, 'w') as fisier_iesire:
    fisier_iesire.write(continut_intrare)
