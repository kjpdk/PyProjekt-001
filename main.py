import csv
from tabulate import tabulate

# En global ordbog til at oversætte initialer til fulde navne
NAVNE_MAP = {"TH": "Thomas Heidelbach", "KH": "Kim Heidelbach", "KP": "Kim Petersen"}


def indlaes_saet_fra_csv(filnavn):
    saet_liste = []
    try:
        with open(filnavn, mode="r", encoding="utf-8") as fil:
            csv_laeser = csv.DictReader(fil)
            for raekke in csv_laeser:
                saet_liste.append(
                    {
                        "dato": raekke["dato"],
                        "kamp_id": int(raekke["kamp_id"]),
                        "spiller_1": raekke["spiller_1"],
                        "spiller_2": raekke["spiller_2"],
                        "point_1": int(raekke["point_1"]),
                        "point_2": int(raekke["point_2"]),
                    }
                )
    except FileNotFoundError:
        pass
    return saet_liste


def analyser_data(saet_liste, filter_spiller_a=None, filter_spiller_b=None):
    # Initialisér statistik-strukturen for alle spillere
    stats = {
        spiller: {"kampe_vundet": 0, "saet_vundet": 0, "point_ialt": 0}
        for spiller in NAVNE_MAP.keys()
    }

    samlet_til_30 = 0
    samlet_overtid_22 = 0
    storste_forskel = -1
    storste_forskel_detaljer = ""

    # Midlertidig struktur til at finde kamp-vinderen (da en kamp består af 3 sæt)
    # Nøgle: (dato, kamp_id), Værdi: {spiller: vundne_saet}
    kampe_saet_taeller = {}

    for saet in saet_liste:
        s1, s2 = saet["spiller_1"], saet["spiller_2"]
        p1, p2 = saet["point_1"], saet["point_2"]

        # Hvis vi kører indbyrdes filter, skal vi sortere uvelkomne sæt fra
        if filter_spiller_a and filter_spiller_b:
            if not (
                (s1 == filter_spiller_a and s2 == filter_spiller_b)
                or (s1 == filter_spiller_b and s2 == filter_spiller_a)
            ):
                continue

        # 1. Tæl point
        stats[s1]["point_ialt"] += p1
        stats[s2]["point_ialt"] += p2

        # Find sættets vinder og taber
        saet_vinder = s1 if p1 > p2 else s2
        saet_taber = s2 if p1 > p2 else s1
        vinder_point = max(p1, p2)
        taber_point = min(p1, p2)

        stats[saet_vinder]["saet_vundet"] += 1

        # 2. Tjek gysersæt (præcis 30) og overtid (22+)
        if vinder_point == 30:
            samlet_til_30 += 1
        elif vinder_point >= 22:
            samlet_overtid_22 += 1

        # 3. Find største point-forskel i et sæt
        nuvaerende_forskel = vinder_point - taber_point
        if nuvaerende_forskel > storste_forskel:
            storste_forskel = nuvaerende_forskel
            storste_forskel_detaljer = f"{nuvaerende_forskel} point ({NAVNE_MAP[saet_vinder]} mod {NAVNE_MAP[saet_taber]}: {vinder_point}-{taber_point})"

        # 4. Forbered optælling af vundne kampe
        kamp_noegle = (saet["dato"], saet["kamp_id"])
        if kamp_noegle not in kampe_saet_taeller:
            kampe_saet_taeller[kamp_noegle] = {s1: 0, s2: 0}
        kampe_saet_taeller[kamp_noegle][saet_vinder] += 1

    # 5. Beregn hvem der vandt kampene (flest sæt ud af de 3 spillet)
    for kamp_data in kampe_saet_taeller.values():
        # kamp_data er f.eks. {"TH": 2, "KH": 1}
        spillere_i_kamp = list(kamp_data.keys())
        # Håndter hvis en spiller har vundet flest sæt i kampen
        if kamp_data[spillere_i_kamp[0]] > kamp_data[spillere_i_kamp[1]]:
            stats[spillere_i_kamp[0]]["kampe_vundet"] += 1
        else:
            stats[spillere_i_kamp[1]]["kampe_vundet"] += 1

    return stats, samlet_til_30, samlet_overtid_22, storste_forskel_detaljer


def vis_samlet_statistik(saet_liste):
    stats, til_30, overtid_22, forskel_tekst = analyser_data(saet_liste)

    tabel_data = []
    for init, data in stats.items():
        tabel_data.append(
            [
                NAVNE_MAP[init],
                data["kampe_vundet"],
                data["saet_vundet"],
                data["point_ialt"],
            ]
        )

    print("\n" + "=" * 50)
    print("         KJP-LAB SAMLET SPILSTATUS (I ALT)")
    print("=" * 50)
    print(
        tabulate(
            tabel_data,
            headers=["Spiller", "Kampe Vundet", "Sæt Vundet", "Point Ialt"],
            tablefmt="fancy_grid",
        )
    )

    print(f"\n🔥 Gysersæt (Gået til præcis 30): {til_30}")
    print(f"📈 Sæt i overtid (Vundet med 22+ point): {overtid_22}")
    print(f"🎯 Største point-forskel i et sæt: {forskel_tekst}")


def vis_indbyrdes_statistik(saet_liste):
    print("\n--- VÆLG INDBYRDES OPGØR ---")
    print("1. Thomas Heidelbach mod Kim Heidelbach")
    print("2. Thomas Heidelbach mod Kim Petersen")
    print("3. Kim Petersen mod Kim Heidelbach")

    valg = input("Vælg opgør (1-3): ").strip()

    if valg == "1":
        pa, pb = "TH", "KH"
    elif valg == "2":
        pa, pb = "TH", "KP"
    elif valg == "3":
        pa, pb = "KP", "KH"
    else:
        print("⚠ Ugyldigt valg.")
        return

    stats, _, _, _ = analyser_data(saet_liste, filter_spiller_a=pa, filter_spiller_b=pb)

    tabel_data = [
        [
            NAVNE_MAP[pa],
            stats[pa]["kampe_vundet"],
            stats[pa]["saet_vundet"],
            stats[pa]["point_ialt"],
        ],
        [
            NAVNE_MAP[pb],
            stats[pb]["kampe_vundet"],
            stats[pb]["saet_vundet"],
            stats[pb]["point_ialt"],
        ],
    ]

    print("\n" + "=" * 50)
    print(f"    INDBYRDES STATUS: {NAVNE_MAP[pa]} vs {NAVNE_MAP[pb]}")
    print("=" * 50)
    print(
        tabulate(
            tabel_data,
            headers=["Spiller", "Kampe Vundet", "Sæt Vundet", "Point Ialt"],
            tablefmt="fancy_grid",
        )
    )


def main():
    filnavn = "kampe.csv"

    while True:
        saet_liste = indlaes_saet_fra_csv(filnavn)

        print("\n" + "=" * 35)
        print("    KJP-LAB ADVANCED BADMINTON    ")
        print("=================================")
        print("1. Vis samlet klub-statistik")
        print("2. Vis indbyrdes statistik (Opgør)")
        print("3. Luk programmet")

        valg = input("Vælg en mulighed (1-3): ").strip()

        if valg == "1":
            vis_samlet_statistik(saet_liste)
        elif valg == "2":
            vis_indbyrdes_statistik(saet_liste)
        elif valg == "3":
            print("\nSystemet lukkes. Hav en fantastisk tirsdag/fredag i hallen!")
            break
        else:
            print("⚠ Ugyldigt valg. Prøv igen.")


if __name__ == "__main__":
    main()
