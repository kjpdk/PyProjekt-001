from tabulate import tabulate


def beregn_statistik(kampe):
    samlet_vundet = 0
    samlet_point_vundet = 0
    samlet_point_tabt = 0

    # Loop igennem alle kampe og tæl samlet_vundet
    for kamp in kampe:
        samlet_point_vundet += kamp["egne_point"]
        samlet_point_tabt += kamp["modstander_point"]

        if kamp["egne_point"] > kamp["modstander_point"]:
            samlet_vundet += 1

    # Beregn procenter
    antal_kampe = len(kampe)
    win_rate = (samlet_vundet / antal_kampe) * 100 if antal_kampe > 0 else 0

    return {
        "antal_kampe": antal_kampe,
        "vundet": samlet_vundet,
        "win_rate": win_rate,
        "point_vundet": samlet_point_vundet,
        "point_tabt": samlet_point_tabt,
    }


def main():
    # Vores badminton data (Test-kampe i KJP-Lab)
    badminton_kampe = [
        {"modstander": "Thomas", "egne_point": 21, "modstander_point": 18},
        {"modstander": "Kim H", "egne_point": 19, "modstander_point": 21},
        {"modstander": "Kim P", "egne_point": 21, "modstander_point": 15},
        {"modstander": "Thomas", "egne_point": 22, "modstander_point": 20},
    ]

    # Kør beregningen
    stats = beregn_statistik(badminton_kampe)

    # Forbered data til vores smukke tabel
    tabel_data = [
        ["Antal Kampe Spillet", stats["antal_kampe"]],
        ["Kampe Vundet", stats["vundet"]],
        ["Sejsprocent (Win Rate)", f"{stats['win_rate']:.1f}%"],
        ["Point Scoret (Egne)", stats["point_vundet"]],
        ["Point Tabt (Modstander)", stats["point_tabt"]],
    ]

    # Print resultatet ud i terminalen
    print("\n=== KJP-LAB BADMINTON STATISTIK ===")
    print(tabulate(tabel_data, headers=["Metrik", "Resultat"], tablefmt="fancy_grid"))


if __name__ == "__main__":
    main()
