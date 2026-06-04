import csv
from datetime import datetime
from tabulate import tabulate

# Global oversættelse af initialer til fulde navne
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


def gem_saet_til_csv(filnavn, dato, kamp_id, s1, s2, p1, p2):
    with open(filnavn, mode="a", encoding="utf-8", newline="") as fil:
        feltnavne = ["dato", "kamp_id", "spiller_1", "spiller_2", "point_1", "point_2"]
        csv_skriver = csv.DictWriter(fil, fieldnames=feltnavne)

        if fil.tell() == 0:
            csv_skriver.writeheader()

        csv_skriver.writerow(
            {
                "dato": dato,
                "kamp_id": kamp_id,
                "spiller_1": s1,
                "spiller_2": s2,
                "point_1": p1,
                "point_2": p2,
            }
        )


def analyser_data(saet_liste, filter_spiller_a=None, filter_spiller_b=None):
    stats = {
        spiller: {"kampe_vundet": 0, "saet_vundet": 0, "point_ialt": 0}
        for spiller in NAVNE_MAP.keys()
    }

    samlet_til_30 = 0
    samlet_overtid = 0
    storste_forskel = -1
    storste_forskel_detaljer = ""
    kampe_saet_taeller = {}

    for saet in saet_liste:
        s1, s2 = saet["spiller_1"], saet["spiller_2"]
        p1, p2 = saet["point_1"], saet["point_2"]

        if filter_spiller_a and filter_spiller_b:
            if not (
                (s1 == filter_spiller_a and s2 == filter_spiller_b)
                or (s1 == filter_spiller_b and s2 == filter_spiller_a)
            ):
                continue

        stats[s1]["point_ialt"] += p1
        stats[s2]["point_ialt"] += p2

        saet_vinder = s1 if p1 > p2 else s2
        saet_taber = s2 if p1 > p2 else s1
        vinder_point = max(p1, p2)
        taber_point = min(p1, p2)

        stats[saet_vinder]["saet_vundet"] += 1

        if p1 == 30 or p2 == 30:
            samlet_til_30 += 1
        elif vinder_point >= 22:
            samlet_overtid += 1

        nuvaerende_forskel = vinder_point - taber_point
        if nuvaerende_forskel > storste_forskel:
            storste_forskel = nuvaerende_forskel
            storste_forskel_detaljer = f"{nuvaerende_forskel} point ({NAVNE_MAP[saet_vinder]} mod {NAVNE_MAP[saet_taber]}: {vinder_point}-{taber_point})"

        kamp_noegle = (saet["dato"], saet["kamp_id"])
        if kamp_noegle not in kampe_saet_taeller:
            kampe_saet_taeller[kamp_noegle] = {s1: 0, s2: 0}
        kampe_saet_taeller[kamp_noegle][saet_vinder] += 1

    for kamp_data in kampe_saet_taeller.values():
        spillere_i_kamp = list(kamp_data.keys())
        if len(spillere_i_kamp) == 2:
            if kamp_data[spillere_i_kamp[0]] > kamp_data[spillere_i_kamp[1]]:
                stats[spillere_i_kamp[0]]["kampe_vundet"] += 1
            else:
                stats[spillere_i_kamp[1]]["kampe_vundet"] += 1

    return stats, samlet_til_30, samlet_overtid, storste_forskel_detaljer


def vis_samlet_statistik(saet_liste):
    stats, til_30, overtid, forskel_tekst = analyser_data(saet_liste)

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

    print(f"\n🔥 Gysersæt (Gået til præcis 30 point): {til_30}")
    print(f"📈 Sæt i overtid (Vundet med 22+ point): {overtid}")
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


def modtag_heltal(ledetekst):
    while True:
        try:
            return int(input(ledetekst))
        except ValueError:
            print("⚠ Fejl: Indtast venligst et gyldigt tal.")


def modtag_spiller_initialer(ledetekst, ekskluder_spiller=None):
    while True:
        init = input(ledetekst).strip().upper()
        if init not in NAVNE_MAP:
            print(f"⚠ Fejl: Ukendt spiller. Vælg mellem: {', '.join(NAVNE_MAP.keys())}")
        elif ekskluder_spiller and init == ekskluder_spiller:
            print(
                "⚠ Fejl: En spiller kan ikke spille mod sig selv. Vælg en anden modstander."
            )
        else:
            return init


def tilfoej_fuld_kamp(filnavn, saet_liste):
    print("\n--- REGISTRER NY KAMP (3 SÆT) ---")

    # Sæt standarddatoen til i dag, men tillad brugeren at trykke Enter
    idag_str = datetime.now().strftime("%d-%m-%b")  # Retter sig mod 2026 formatet
    idag_str = datetime.now().strftime("%d-%m-%Y")
    dato = input(f"Indtast dato ({idag_str}): ").strip()
    if not dato:
        dato = idag_str

    spiller_1 = modtag_spiller_initialer("Indtast Spiller 1 (TH/KH/KP): ")
    spiller_2 = modtag_spiller_initialer(
        "Indtast Spiller 2 (TH/KH/KP): ", ekskluder_spiller=spiller_1
    )

    # Find automatisk næste kamp_id for denne specifikke dato
    samme_dato_kampe = [s["amp_id"] for s in saet_liste if s["dato"] == dato]
    # Korrektion af variabelnavn: s["amp_id"] -> s["kamp_id"]
    samme_dato_kampe = [s["kamp_id"] for s in saet_liste if s["dato"] == dato]
    naeste_kamp_id = max(samme_dato_kampe) + 1 if samme_dato_kampe else 1

    print(
        f"\nOpretter Kamp ID {naeste_kamp_id} d. {dato}: {NAVNE_MAP[spiller_1]} vs {NAVNE_MAP[spiller_2]}"
    )
    print("-" * 50)

    # Loop igennem de faste 3 sæt
    for saet_nr in range(1, 4):
        print(f"\n[Sæt {saet_nr}]")
        p1 = modtag_heltal(f"Point til {NAVNE_MAP[spiller_1]}: ")
        p2 = modtag_heltal(f"Point til {NAVNE_MAP[spiller_2]}: ")

        # Gem sættet med det samme i filen
        gem_saet_til_csv(filnavn, dato, naeste_kamp_id, spiller_1, spiller_2, p1, p2)

    print(f"\n✔ Alle 3 sæt for Kamp {naeste_kamp_id} er gemt succesfuldt i {filnavn}!")


def main():
    filnavn = "kampe.csv"

    while True:
        saet_liste = indlaes_saet_fra_csv(filnavn)

        print("\n" + "=" * 35)
        print("    KJP-LAB ADVANCED BADMINTON    ")
        print("=================================")
        print("1. Vis samlet klub-statistik")
        print("2. Vis indbyrdes statistik (Opgør)")
        print("3. Registrer en ny kamp (3 sæt)")
        print("4. Luk programmet")

        valg = input("Vælg en mulighed (1-4): ").strip()

        if valg == "1":
            vis_samlet_statistik(saet_liste)
        elif valg == "2":
            vis_indbyrdes_statistik(saet_liste)
        elif valg == "3":
            tilfoej_fuld_kamp(filnavn, saet_liste)
        elif valg == "4":
            print("\nSystemet lukkes. Hav en fantastisk tirsdag/fredag i hallen!")
            break
        else:
            print("⚠ Ugyldigt valg. Prøv igen.")


if __name__ == "__main__":
    main()
