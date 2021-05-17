""" 
Create and modify and read the mass cytometry data
""" 

import argparse, logging, os
from cio_mass_cytometry.utilities import get_validator, get_version

from cio_mass_cytometry.templates.generate import create_template
from cio_mass_cytometry.templates.ingest import read_excel_template
from cio_mass_cytometry.templates.add_samples import add_samples


logging.basicConfig(level=logging.WARN)
logger = logging.getLogger()

def cmd_validate(args):
   # If we valdiate, its's easymode. Just read it
   print("validate")
def cmd_add_samples(args):
   # If we add to it, we modify it.
   if not os.path.exists(args.template_path):
      raise ValueError("Template path must exist: "+str(args.template_path))
   if not os.path.exists(args.samples_path) or not os.path.isdir(args.samples_path):
      raise ValueError("Sample path must be an existing directory: "+str(args.samples_path))
   logger.info("Trying to add additional samples")
   add_samples(args.template_path, args.samples_path, args.template_path if args.inplace else args.output_path, args.sample_name_regex, logger)
   logger.info("Finished adding samples")
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

   # CREATE A NEW TEMPLATE
   parser_create = subparsers.add_parser('create', help='Create a new template')
   parser_create.add_argument("--overwrite",action="store_true",help="Allow file overwriting on creation")
   parser_create.set_defaults(func=cmd_create)

   # ADD SAMPLES TO AN EXISTING TEMPLATE
   parser_add = subparsers.add_parser('add_samples', help='Add samples to a template.')
   parser_add.add_argument("--samples_path",help="Path where samples are stored",required=True)
   grp = parser_add.add_mutually_exclusive_group(required=True)
   grp.add_argument('--inplace',action='store_true',help="Save the results to ")
   grp.add_argument('--output_path',help="Save the results to a new Excel file")
   parser_add.add_argument("--sample_name_regex",help="Regular expression string for the sample name")
   parser_add.set_defaults(func=cmd_add_samples)

   # INGEST A TEMPLATE
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