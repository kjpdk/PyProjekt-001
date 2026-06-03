import csv
from tabulate import tabulate


def indlaes_kampe_fra_csv(filnavn):
    kampe = []
    try:
        with open(filnavn, mode="r", encoding="utf-8") as fil:
            # DictReader bruger den første linje i CSV-filen som overskrifter (nøgler)
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
        print(f"⚠ Fejl: Kunne ikke finde datafilen '{filnavn}'.")
    return kampe


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


def main():
    filnavn = "kampe.csv"

    # Indlæs data eksternt i stedet for at hårdkode det
    badminton_kampe = indlaes_kampe_fra_csv(filnavn)

    # Beregn statistikken
    stats = beregn_statistik(badminton_kampe)

    if stats is None:
        print("Ingen data tilgængelig for beregning.")
        return

    # Forbered data til tabellen
    tabel_data = [
        ["Antal Kampe Spillet", stats["antal_kampe"]],
        ["Kampe Vundet", stats["vundet"]],
        ["Sejsprocent (Win Rate)", f"{stats['win_rate']:.1f}%"],
        ["Point Scoret (Egne)", stats["point_vundet"]],
        ["Point Tabt (Modstander)", stats["point_tabt"]],
    ]

    # Print resultatet i terminalen
    print(f"\n=== KJP-LAB BADMINTON STATISTIK (Hentet fra {filnavn}) ===")
    print(tabulate(tabel_data, headers=["Metrik", "Resultat"], tablefmt="fancy_grid"))


if __name__ == "__main__":
    main()
