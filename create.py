import argparse
import ipaddress
import pathlib
import shutil
import sys
import zipfile

import jinja2

if getattr(sys, "frozen", False):
    MODULE_PATH = pathlib.Path(sys._MEIPASS)
else:
    MODULE_PATH = pathlib.Path(__file__).parent


# Registry files are in this directory / template
TEMPLATE_PATH = (MODULE_PATH / "src" / "templates").absolute()
TO_COPY_PATH = (MODULE_PATH / "src" / "to_copy").absolute()

REGISTRY_FILES = TEMPLATE_PATH.glob("*.reg")


def write_files(regfiles_path, plc_name, ip_address, plc_description=None):
    plc_name = plc_name.strip()

    assert len(plc_name), "PLC name cannot be empty"

    plc_description = plc_description or plc_name
    plc_description = plc_description.strip()

    ipv4 = ipaddress.IPv4Address(ip_address)
    plc_ip_address = list(ipv4.packed)

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_PATH)),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    settings = dict(
        plc_name=plc_name,
        plc_description=plc_description,
        plc_ip_address=plc_ip_address,
        plc_ip_address_hex=",".join("%x" % c for c in ipv4.packed),
    )

    for fn in REGISTRY_FILES:
        fn = str(fn.parts[-1])
        template = jinja_env.get_template(fn)
        rendered = template.render(**settings)

        print("\n\nTemplate:", fn)
        print("-------------------")
        print(rendered)
        print("-------------------")

        with open(regfiles_path / fn, "wt") as f:
            print(rendered, file=f)


def extract_plc_image(image_zipfile, destination):
    with zipfile.ZipFile(image_zipfile, "r") as zf:
        zf.extractall(destination)


def interactive_main():
    plc_name = input("PLC name? ")
    plc_description = input("PLC description? ") or None
    ip_address = input("IP Address to be used for AMS NetID? ")
    return generate_image(plc_name, ip_address, plc_description)


def generate_image(plc_name, ip_address, plc_description):
    image_root = pathlib.Path("images").resolve()
    plc_root = image_root / plc_name

    if plc_root.exists():
        if input(f"Remove {plc_root} first? [yN] ").lower() in ("y", "yes"):
            shutil.rmtree(plc_root)

    print(f"* Creating {plc_root}")
    plc_root.mkdir(exist_ok=True, parents=True)

    image_name = "CBxx63_WEC7_HPS_v608g_TC31_B4024.10"
    print(f"* Extracting {image_name} to {image_root}")
    extract_plc_image(MODULE_PATH / f"{image_name}.zip", image_root)

    print(f"* Copying {image_root/image_name} to {plc_root}")
    shutil.copytree(image_root / image_name, plc_root, dirs_exist_ok=True)

    print(f"* Copying {TO_COPY_PATH} to {plc_root}")
    shutil.copytree(TO_COPY_PATH, plc_root, dirs_exist_ok=True)

    print(f"* Writing templates to {plc_root/'RegFiles'}")
    write_files(
        regfiles_path=plc_root / "RegFiles",
        plc_name=plc_name,
        plc_description=plc_description,
        ip_address=ip_address,
    )


def _build_argparser():
    parser = argparse.ArgumentParser()

    parser.description = "PLC image creator"
    parser.formatter_class = argparse.RawTextHelpFormatter

    parser.add_argument("plc_name", type=str, help="PLC Name")

    parser.add_argument(
        "ip_address", type=str, help="PLC IP Address to use for AMS Net ID"
    )

    parser.add_argument("plc_description", type=str, help="PLC Description")

    return parser


if __name__ == "__main__":
    parser = _build_argparser()
    args = parser.parse_args()
    generate_image(**vars(args))
