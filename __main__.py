import argparse
from pathlib import Path
from functools import partial

from .flutter_image_asset_helper import centimeters_to_physical_pixels_printer
from .flutter_image_asset_helper import generate_flutter_image_assets


def _argument_greater_than(value, type_, what):
    # Only argparse.ArgumentTypeError can be thrown in the type function.

    try:
        parsed_value = type_(value)
    except ValueError:
        raise argparse.ArgumentTypeError('{!s} is not a valid {!s}.'.format(value, type_.__name__))

    if not parsed_value > what:
        raise argparse.ArgumentTypeError('{!s} is not greater than {!s}.'.format(parsed_value, what))

    return parsed_value


def _centimeters_to_physical_pixels_printer_shell(args):
    centimeters_to_physical_pixels_printer(args.centimeters, list(range(1, args.resolutions+1)))


def _generate_flutter_image_assets_shell(args):
    tr = args.tr
    if args.tr is None:
        tr = args.sr

    source = Path(args.source)
    target = Path(args.target)

    if generate_flutter_image_assets(source, target, nominal_resolution_of_source=args.sr, nominal_resolution_target=tr, forcibly_rebuild=args.force, append_preferred_dimension=args.no_preferred):
        print('Flutter image assets have been successfully generated at "{!s}"".'.format(target.resolve()))
    else:
        print('The "{!s}" folder already exists.'.format(target.resolve()))


def _parse_args():
    parser = argparse.ArgumentParser(prog='flutter_image_asset_helper', description='A helper helping to design and generate Flutter image assets.')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.1.0')

    subparsers = parser.add_subparsers(dest='action', title='action', description='Which action should be executed?', help='"query": query design guidelines. "generate": generate Flutter image assets.')

    parser_query = subparsers.add_parser('query', description='Query design guidelines.')
    parser_query.add_argument('centimeters', type=partial(_argument_greater_than, type_=float, what=0), help='The dimension of the image in centimeter (decimal).')
    parser_query.add_argument('resolutions', default=3, nargs='?', type=partial(_argument_greater_than, type_=int, what=0), help='The maximum target nominal resolution (integer). Defaults to 3.')
    parser_query.set_defaults(func=_centimeters_to_physical_pixels_printer_shell)

    parser_generate = subparsers.add_parser('generate', description='Generate Flutter image assets. The generated images will be named "filename-preferred_width_in_centimeterxpreferred_height_in_centimeter.suffix". You can disable the appendant of preferred dimensions by using the "-np" option.')
    parser_generate.add_argument('source', help='The source folder.')
    parser_generate.add_argument('target', help='The target folder.')
    parser_generate.add_argument('sr', type=partial(_argument_greater_than, type_=int, what=0), help='The nominal resolution of the source images.')
    parser_generate.add_argument('tr', nargs='?', type=partial(_argument_greater_than, type_=int, what=0), help='The maximum  nominal resolution of the generated target images. Defaults to "sr".')
    parser_generate.add_argument('-f', '--force', action='store_true', help='Forcibly rebuild the target folder even it already exists.')
    parser_generate.add_argument('-np', '--no-preferred', action='store_false', help='Do not append prederred dimensions to the file names.')
    parser_generate.set_defaults(func=_generate_flutter_image_assets_shell)

    return parser, parser.parse_args()


if __name__ == '__main__':
    (parser, args) = _parse_args()

    if args.action is None:
        parser.print_help()
        exit(0)

    args.func(args)
