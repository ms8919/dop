import argparse


def build_parser():
    parser = argparse.ArgumentParser(
        prog="dop-gallery",
        description="Build an offline HTML gallery of NRW digital orthophoto (DOP) "
        "cutouts from a CSV of addresses.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    stage = sub.add_parser("stage", help="download geodata once (requires internet)")
    run = sub.add_parser("run", help="build the gallery (fully offline)")

    for sp in (stage, run):
        sp.add_argument("--addresses", required=True, help="CSV file with the addresses")
        sp.add_argument("--data-dir", default="data", help="staged data directory (default: data)")
        sp.add_argument("--col-street", default="street", help="CSV column with the street (default: street)")
        sp.add_argument("--col-house-number", default="house_number", help="CSV column with the house number (default: house_number)")
        sp.add_argument("--col-zip", default="zip", help="CSV column with the ZIP code (default: zip)")
        sp.add_argument("--col-city", default="city", help="CSV column with the city (default: city)")

    run.add_argument("--out", default="dop-gallery", help="output gallery directory (default: dop-gallery)")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "stage":
        from . import stage

        return stage.run_stage(args)
    from . import run

    return run.run_gallery(args)
