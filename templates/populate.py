import pathlib
import ipaddress

import jinja2


# Registry files are in this directory
MODULE_PATH = pathlib.Path(__file__).parent

# And should be dumped out in the parent directory
OUTPUT_PATH = MODULE_PATH.parent

REGISTRY_FILES = MODULE_PATH.glob('*.reg')


def write_files(plc_name, ip_address, plc_description=None):
    plc_name = plc_name.strip()

    assert len(plc_name), 'PLC name cannot be empty'

    plc_description = plc_description or plc_name
    plc_description = plc_description.strip()

    ipv4 = ipaddress.IPv4Address(ip_address)
    plc_ip_address = list(ipv4.packed)

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(MODULE_PATH)),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    settings = dict(
        plc_name=plc_name,
        plc_description=plc_description,
        plc_ip_address=plc_ip_address,
        plc_ip_address_hex=','.join('%x' % c for c in ipv4.packed),
    )

    for fn in REGISTRY_FILES:
        template = jinja_env.get_template(str(fn))
        rendered = template.render(**settings)

        print('\n\nTemplate:', fn)
        print('-------------------')
        print(rendered)
        print('-------------------')

        with open(OUTPUT_PATH / fn, 'wt') as f:
            print(rendered, file=f)


def main():
    plc_name = input('PLC name?')
    plc_description = input('PLC description?') or None
    ip_address = input('IP Address to be used for AMS NetID?')

    write_files(
        plc_name=plc_name,
        plc_description=plc_description,
        ip_address=ip_address
    )


if __name__ == '__main__':
    main()
