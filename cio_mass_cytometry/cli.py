""" 
Create and modify and read the mass cytometry data
""" 

import argparse, logging, os
from cio_mass_cytometry.utilities import get_validator, get_version

from cio_mass_cytometry.templates.generate import create_template
from cio_mass_cytometry.templates.ingest import read_excel_template


logging.basicConfig(level=logging.WARN)
logger = logging.getLogger()

def cmd_validate(args):
   # If we valdiate, its's easymode. Just read it
   print("validate")
def cmd_add_samples(args):
   # If we add to it, we modify it.
   print("add samples")
def cmd_create(args):
   # If we create, make a new file at the template path
   logger.info("Started creation of the template")
   if os.path.exists(args.template_path) and args.overwrite is False:
      raise ValueError("Cannot overwrite without --overwrite option")
   create_template(args.template_path,logger)
   logger.info("Finished creating the template")
def cmd_ingest(args):
   # Read in and write out json
   data = read_excel_template(args.template_path,logger)

def main():
   parser = argparse.ArgumentParser(
            description = "Process templates",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   subparsers = parser.add_subparsers(help='Choose how to work with the tempate')

   parser_create = subparsers.add_parser('create', help='Create a new template')
   parser_create.add_argument("--overwrite",action="store_true",help="Allow file overwriting on creation")
   parser_create.set_defaults(func=cmd_create)

   parser_add = subparsers.add_parser('add_samples', help='Add samples to a template.')
   parser_add.add_argument("--sample_path",help="Path where samples are stored")
   parser_add.set_defaults(func=cmd_add_samples)

   parser_validate = subparsers.add_parser('validate', help='Validate an existing template.')
   parser_validate.set_defaults(func=cmd_validate)

   parser_ingest = subparsers.add_parser('ingest', help='Read an existing template.')
   parser_ingest.set_defaults(func=cmd_ingest)

   parser.add_argument('-v','--verbose',action='store_true')
   parser.add_argument('template_path',help="Path to write the template")

   args = parser.parse_args()

   if args.verbose:
      logger.setLevel(level=logging.INFO)
      for handler in logger.handlers:
         handler.setLevel(logging.INFO)

   args.func(args)
   return 

if __name__ == "__main__":
	main()