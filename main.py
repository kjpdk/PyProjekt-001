import csv
from tabulate import tabulate


def indlaes_kampe_fra_csv(filnavn):
    kampe = []
    try:
        with open(filnavn, mode="r", encoding="utf-8") as fil:
            csv_laeser = csv.DictReader(fil)
            for raekke in csv_laeser:
                kampe.append(
                    {
                        "modstander": raekke["modstander"],
                        "egne_point": int(raekke["egne_point"]),
                        "modstander_point": int(raekke["modstander_point"]),
                    }
                )
    except FileNotFoundError:
        # Hvis filen ikke findes endnu, returnerer vi bare en tom liste
        pass
    return kampe


def gem_kamp_til_csv(filnavn, modstander, egne_point, modstander_point):
    # 'a' står for append – det betyder, at vi tilføjer til bunden uden at slette det gamle
    with open(filnavn, mode="a", encoding="utf-8", newline="") as fil:
        feltnavne = ["modstander", "egne_point", "modstander_point"]
        csv_skriver = csv.DictWriter(fil, fieldnames=feltnavne)

        # Hvis filen var helt tom, skriver vi overskrifterne først
        if fil.tell() == 0:
            csv_skriver.writeheader()

        csv_skriver.writerow(
            {
                "modstander": modstander,
                "egne_point": egne_point,
                "modstander_point": modstander_point,
            }
        )


def beregn_statistik(kampe):
    if not kampe:
        return None

    samlet_vundet = 0
    samlet_point_vundet = 0
    samlet_point_tabt = 0

    for kamp in kampe:
        samlet_point_vundet += kamp["egne_point"]
        samlet_point_tabt += kamp["modstander_point"]

        if kamp["egne_point"] > kamp["modstander_point"]:
            samlet_vundet += 1

    antal_kampe = len(kampe)
    win_rate = (samlet_vundet / antal_kampe) * 100

    return {
        "antal_kampe": antal_kampe,
        "vundet": samlet_vundet,
        "win_rate": win_rate,
        "point_vundet": samlet_point_vundet,
        "point_tabt": samlet_point_tabt,
    }


def vis_statistik(filnavn):
    badminton_kampe = indlaes_kampe_fra_csv(filnavn)
    stats = beregn_statistik(badminton_kampe)

    if stats is None:
        print("\nℹ Der er ikke registreret nogen kampe i systemet endnu.")
        return

    tabel_data = [
        ["Antal Kampe Spillet", stats["antal_kampe"]],
        ["Kampe Vundet", stats["vundet"]],
        ["Sejsprocent (Win Rate)", f"{stats['win_rate']:.1f}%"],
        ["Point Scoret (Egne)", stats["point_vundet"]],
        ["Point Tabt (Modstander)", stats["point_tabt"]],
    ]

    print(f"\n=== KJP-LAB BADMINTON STATISTIK (Hentet fra {filnavn}) ===")
    print(tabulate(tabel_data, headers=["Metrik", "Resultat"], tablefmt="fancy_grid"))


def modtag_heltal(ledetekst):
    # En pædagogisk lille løkke, der sikrer, at brugeren taster et rigtigt tal
    while True:
        try:
            return int(input(ledetekst))
        except ValueError:
            print("⚠ Fejl: Du skal indtaste et gyldigt heltal. Prøv igen.")


def tilfoej_ny_kamp(filnavn):
    print("\n--- REGISTRER NY BADMINTON KAMP ---")
    modstander = input("Indtast modstanderens navn: ").strip()

    if not modstander:
        print("⚠ Fejl: Modstanderens navn må ikke være tomt.")
        return

    egne_point = modtag_heltal("Indtast dine point: ")
    modstander_point = modtag_heltal("Indtast modstanderens point: ")

    # Gem dataen i vores CSV-fil
    gem_kamp_til_csv(filnavn, modstander, egne_point, modstander_point)
    print(f"✔ Kampen mod {modstander} blev gemt i {filnavn}!")


def main():
    filnavn = "kampe.csv"

    while True:
        print("\n=================================")
        print("    KJP-LAB BADMINTON MANAGER    ")
        print("=================================")
        print("1. Vis aktuel statistik")
        print("2. Registrer et nyt kampresultat")
        print("3. Luk programmet")

        valg = input("Vælg en mulighed (1-3): ").strip()

        if valg == "1":
            vis_statistik(filnavn)
        elif valg == "2":
            tilfoej_ny_kamp(filnavn)
            # Vi viser automatisk den opdaterede statistik med det samme efter en tilføjelse
            vis_statistik(filnavn)
        elif valg == "3":
            print("\nTak for i dag! Hav en god træning i klubben.")
            break
        else:
            print("⚠ Ugyldigt valg. Tast venligst 1, 2 eller 3.")


if __name__ == "__main__":
    main()
