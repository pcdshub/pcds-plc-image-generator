import argparse
import ipaddress
import os
import pathlib
import shutil
import sys
import urllib.request
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
IMAGE_ROOT = pathlib.Path.cwd()

DOWNLOAD_USER_AGENT = os.environ.get("DOWNLOAD_USER_AGENT", "Mozilla/5.0")
MODEL_TO_URL = {
    "cx20x0": "https://download.beckhoff.com/download/Software/embPC-Control/CX20xx/CX20x0/CE/TC3/_History/CBx055_CBx056_WEC7_HPS_v608g_TC31_B4024.10.zip",   # noqa: E501
    "cx50xx": "https://download.beckhoff.com/download/Software/embPC-Control/C6915/0000/CE/TC3/_History/CBx053_CE600_HPS_v408g_TC31_B4024.10.zip",   # noqa: E501
    "cx51xx": "https://download.beckhoff.com/download/Software/embPC-Control/CX51xx/CX51x0/CE/TC3/_History/CBxx63_WEC7_HPS_v608g_TC31_B4024.10.zip",  # noqa: E501
}


def write_files(regfiles_path, plc_name, ip_address, plc_description=None):
    """
    Fill in templated reg files (in ``TEMPLATE_PATH``) with the provided
    settings.

    Parameters
    ----------
    regfiles_path : pathlib.Path
        The destination path for the generated files.

    plc_name : str
        The PLC name.

    ip_address : str
        The PLC IP address.

    description : str, optional
        The PLC description, defaulting to plc_name.
    """
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
    """Extract ``image_zipfile`` to ``destination``."""
    with zipfile.ZipFile(image_zipfile, "r") as zf:
        zf.extractall(destination)


def get_plc_image(plc_model: str) -> pathlib.Path:
    """
    Download (or use a cached version of) the PLC image for the given model.

    As Beckhoff CDNs may block certain user agents, this function will use
    the environment variable ``DOWNLOAD_USER_AGENT`` to allow runtime
    customization of the reported user agent.

    Parameters
    ----------
    plc_model : str
        The model number of the PLC (according to MODEL_TO_URL).

    Returns
    -------
    pathlib.Path
        The local path to the downloaded image.
    """
    try:
        image_url = MODEL_TO_URL[plc_model]
    except KeyError:
        raise ValueError(
            f"Invalid PLC model; choose from {tuple(MODEL_TO_URL)}"
        )

    source_image_path = IMAGE_ROOT / pathlib.Path(image_url).name
    if source_image_path.exists():
        print(f"Using already-downloaded {source_image_path}")
        return source_image_path

    print(f"{source_image_path} does not exist; downloading from {image_url}")
    req = urllib.request.Request(image_url)
    req.add_header("User-Agent", DOWNLOAD_USER_AGENT)

    try:
        with urllib.request.urlopen(req) as fp:
            contents = fp.read()
    except Exception as ex:
        raise RuntimeError(
            f"Unable to download {image_url} : the download URL may have changed "
            f"or Beckhoff may have restricted the user agent '{DOWNLOAD_USER_AGENT}'. "
            f"Try downloading from the above link manually and saving the file "
            f"in this directory, and report the issue to the ecs-pd team."
        ) from ex
    with open(source_image_path, "wb") as fp:
        fp.write(contents)
    return source_image_path


def generate_image(
    plc_model: str,
    plc_name: str,
    ip_address: str,
    plc_description: str,
    auto_delete: bool = False,
):
    """
    Fill in templated reg files (in ``TEMPLATE_PATH``) with the provided
    settings.

    Parameters
    ----------
    plc_model : str
        PLC generic model (see ``MODEL_TO_URL``).

    plc_name : str
        The PLC name.

    ip_address : str
        The PLC IP address.

    plc_description : str
        The PLC description, defaulting to plc_name.

    auto_delete : bool, optional
        Automatically delete old generated image files.  Defaults to False.
    """
    source_image_path = get_plc_image(plc_model)
    dest_image_root = pathlib.Path("images").resolve()
    plc_root = dest_image_root / plc_name

    if plc_root.exists():
        question = f"Remove {plc_root} first? [yN] "
        if auto_delete or input(question).lower() in ("y", "yes"):
            shutil.rmtree(plc_root)

    print(f"* Creating {plc_root}")
    plc_root.mkdir(exist_ok=True, parents=True)

    print(f"* Extracting {source_image_path} to {dest_image_root}")
    extract_plc_image(source_image_path, dest_image_root)

    print(f"* Copying {source_image_path} to {plc_root}")
    shutil.copytree(
        dest_image_root / source_image_path.stem,
        plc_root,
        dirs_exist_ok=True
    )

    print(f"* Removing default RegFiles in {plc_root/'RegFiles'}")
    shutil.rmtree(plc_root / "RegFiles")

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
    """Build the console argparse.ArgumentParser."""
    parser = argparse.ArgumentParser()

    parser.description = "PLC image creator"
    parser.formatter_class = argparse.RawTextHelpFormatter

    parser.add_argument("plc_name", type=str, help="PLC Name")

    parser.add_argument(
        "ip_address", type=str, help="PLC IP Address to use for AMS Net ID"
    )

    parser.add_argument(
        "--model",
        type=str,
        help="PLC model",
        dest="plc_model",
        default="cx50xx",
        choices=tuple(MODEL_TO_URL)
    )

    parser.add_argument("plc_description", type=str, help="PLC Description")

    return parser


if __name__ == "__main__":
    parser = _build_argparser()
    args = parser.parse_args()
    generate_image(**vars(args))
