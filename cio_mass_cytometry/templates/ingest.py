import logging
import pandas as pd
from openpyxl import load_workbook
from cio_mass_cytometry.utilities import get_validator
from importlib_resources import files
from collections import OrderedDict


logging.basicConfig(level=logging.WARN)
logger = logging.getLogger()

required_sheets = {
    'panel_parameters':'Panel Parameters',
    'panel_definition':'Panel Definition',
    'sample_manifest':'Sample Manifest',
    'sample_annotations':'Sample Annotations',
    'meta':'Meta'
}



def read_excel_template(template_path,mylogger):
    logger = mylogger
    # Read in each part of the spreadsheet

    logger.info("Read the sheet names")
    observed_sheet_names = load_workbook(template_path)
    for sheet_name in required_sheets.values():
        if sheet_name not in observed_sheet_names:
            raise ValueError("Missing required sheet "+str(sheet_name))

    logger.info("Read the panel and panel parameters")
    panel = parse_panel(pd.read_excel(template_path,sheet_name=required_sheets['panel_parameters']),
                        pd.read_excel(template_path,sheet_name=required_sheets['panel_definition'])
            )

    logger.info("Read the samples")
    samples = parse_samples(pd.read_excel(template_path,sheet_name=required_sheets['sample_manifest']),
                            pd.read_excel(template_path,sheet_name=required_sheets['sample_annotations'])
              )

    logger.info("Read the meta data")
    meta = parse_meta(pd.read_excel(template_path,sheet_name=required_sheets['meta']))

def parse_panel(panel_parameters,panel_definition):
    # Get the json schema
    _validator = get_validator(files('schemas').joinpath('panel.json'))
    _schema = _validator.schema 

    # Read the first two columns that are in "Parameter" "Value" format
    df = panel_parameters.iloc[:,0:2].set_index('Parameter')['Value'].to_dict()

    # Get the parameters
    _params = _schema['properties']['parameters']['properties']
    #print([x for x in _params.items()])
    _conv = OrderedDict([(x[1]['title'],x[0]) for x in _params.items()])

    # Make sure our titles are all in the dataframe
    for title in _conv.keys():
        if title not in df.keys():
            raise ValueError("expected panel parameter title not found "+str(title))

    # Replace the title with the json_schema properties
    panel_parameters_json = OrderedDict([(_conv[x[0]],x[1]) for x in df.items()])
    
    # Get the panel

    _panel_def = _schema['properties']['markers']['items']['properties']
    _conv = OrderedDict([(x[1]['title'],x[0]) for x in _panel_def.items()])

    # Make sure our titles are all in the dataframe
    for title in _conv.keys():
        if title not in panel_definition.columns:
            raise ValueError("expected panel definition title not found "+str(title))
    
    df = panel_definition.loc[:,list(_conv.keys())]
    # Go through and fill in default values
    for column_name in df.columns:
        if '(default TRUE)' in column_name:
            df.loc[df[column_name].isna(),column_name] = True

    # Now lets add some custom code for things with default values

    df.columns = list(_conv.values())
    panel_definition_json = [row.to_dict() for i,row in df.iterrows()]
    return {
        'parameters':panel_parameters_json,
        'markers':panel_definition_json
    }

def parse_samples(sample_manifest,sample_annotations):

    # Get the json schema
    _validator = get_validator(files('schemas').joinpath('files.json'))
    _schema = _validator.schema 

    # Lets the the sample annotation table
    # Get the samples
    _annot_def = _schema['definitions']['annotation_type']['properties']
    _conv2 = OrderedDict([(x[1]['title'],x[0]) for x in _annot_def.items() if 'title' in x[1]])
    df2 = sample_annotations.loc[:,list(_conv2.keys())]
    # Go through and fill in default values
    for column_name in df2.columns:
        if '(default TRUE)' in column_name:
            df2.loc[df2[column_name].isna(),column_name] = True
    df2.columns = list(_conv2.values())

    annotation_levels_json = [row.to_dict() for i,row in df2.iterrows()]


    # Get the samples
    _sample_def = _schema['properties']['samples']['items']['properties']
    _conv = OrderedDict([(x[1]['title'],x[0]) for x in _sample_def.items() if 'title' in x[1]])

    # Make sure our titles are all in the dataframe
    for title in _conv.keys():
        if title not in sample_manifest.columns:
            raise ValueError("expected panel definition title not found "+str(title))
    
    df1 = sample_manifest.loc[:,list(_conv.keys())]
    # Go through and fill in default values
    for column_name in df1.columns:
        if '(default TRUE)' in column_name:
            df1.loc[df1[column_name].isna(),column_name] = True



    # Make sure our titles are all in the dataframe
    for title in _conv.keys():
        if title not in sample_manifest.columns:
            raise ValueError("expected panel definition title not found "+str(title))
    
    df0 = sample_manifest.loc[:,list(_conv.keys())]
    # Go through and fill in default values
    for column_name in df0.columns:
        if '(default TRUE)' in column_name:
            df0.loc[df0[column_name].isna(),column_name] = True
    # Now lets add some custom code for things with default values
    df0.columns = list(_conv.values())

    samples_json = [row.to_dict() for i,row in df0.iterrows()]

    # collect up the annotations .. a little hard coded
    df1 = sample_manifest.set_index('Sample Name').loc[:,set(sample_manifest.columns)-set(_conv.keys())]
    df1.index.name = 'sample_name'

    # Get the sample annotations, but still missing some information about the sample annotations
    df1 = df1.stack().reset_index().rename(columns={'level_1':'annotation_group',0:'annotation_value'}).\
        merge(df2,on=['annotation_group'],how='left')
    if df1.loc[df1['annotation_order'].isna(),:].shape[0] > 0:
        raise ValueError("Undefined annotation group "+str(df1.loc[df1['annotation_order'].isna(),'annotation_group'].unique()))
    annotations = OrderedDict([(sample_name,OrderedDict(row.to_dict())) for sample_name, row in df1.set_index('sample_name').iterrows()])
    for i, sample_object in enumerate(samples_json):
        sample_name = sample_object['sample_name']
        samples_json[i]['sample_annotations'] = annotations[sample_name]
    return {
        "annotation_levels":annotation_levels_json,
        "samples":samples_json
    }

def parse_annotations(sample_annotations):
    return

def parse_meta(meta):
    return



