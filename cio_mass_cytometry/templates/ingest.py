import logging, os, json
import pandas as pd
from openpyxl import load_workbook
from cio_mass_cytometry.utilities import get_validator, get_version, sha256sum
from importlib_resources import files
from collections import OrderedDict
from datetime import datetime


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
    panel_json = parse_panel(pd.read_excel(template_path,sheet_name=required_sheets['panel_parameters']),
                        pd.read_excel(template_path,sheet_name=required_sheets['panel_definition'],keep_default_na=False,na_values=[''])
            )

    logger.info("Read the samples")
    samples_json = parse_samples(pd.read_excel(template_path,sheet_name=required_sheets['sample_manifest']),
                            pd.read_excel(template_path,sheet_name=required_sheets['sample_annotations'])
              )

    # Now put together the final analysis json
    logger.info("Put together a final analysis file")


    logger.info("Read the meta data")
    meta_df = pd.read_excel(template_path,sheet_name=required_sheets['meta']).set_index('Parameter')

    output = {
        "panel":panel_json,
        "annotation_levels":samples_json["annotation_levels"],
        "samples":samples_json["samples"],
        "meta":{
            "template_generation_pipeline_version":str(meta_df.loc['Pipeline Version']['Value']),
            "template_ingestion_pipeline_version":str(get_version()),            
        }
    }

    logger.info("Validate the constructed analysis inputs")

    _validator = get_validator(files('schemas').joinpath('inputs.json'))
    _validator.validate(output)

    return output


def parse_panel(panel_parameters,panel_definition):
    #print([type(x) for x in panel_definition.iloc[:,4]])
    # break
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
            df.loc[~df[column_name].isna(),column_name] = df.loc[~df[column_name].isna(),column_name].astype(bool)
    for column_name in df.columns:
        if '(default TRUE)' not in column_name:
            df[column_name] = df[column_name].apply(lambda x: None if x!=x else x)
            df[column_name] = df[column_name].apply(lambda x: x if x is None else str(x))
    
    # Now lets add some custom code for things with default values
    #print(panel_definition.iloc[0:4,4:])

    df.columns = list(_conv.values())
    df = df.applymap(lambda x: None if x!=x else x)

    #print(df.iloc[:,3:])
    panel_definition_json = [row.to_dict() for i,row in df.iterrows()]
    print(json.dumps(panel_definition_json,indent=2))
    #print([type(x) for x in df['compartment']])
    output = {
        'parameters':panel_parameters_json,
        'markers':panel_definition_json
    }
    logger.info("Validating panel json schema")
    _validator.validate(output)

    return output
def parse_samples(sample_manifest,sample_annotations):
    def _do_fcs_file(path):
        if not os.path.exists(path):
            raise ValueError("Path does not exist: "+str(path))
        return {
            'file_path':path,
            'creation_timestamp':datetime.fromtimestamp(os.path.getctime(path)).strftime("%m/%d/%Y, %H:%M:%S"),
            'last_modified_timestamp':datetime.fromtimestamp(os.path.getmtime(path)).strftime("%m/%d/%Y, %H:%M:%S"),
            'sha256_hash':sha256sum(path)
        }

    # Get the json schema
    _validator = get_validator(files('schemas').joinpath('samples.json'))
    _schema = _validator.schema 

    # Lets the the sample annotation table
    # Get the samples
    _annot_def = _schema['properties']['annotation_levels']['items']['properties']
    _conv2 = OrderedDict([(x[1]['title'],x[0]) for x in _annot_def.items() if 'title' in x[1]])
    df2 = sample_annotations.loc[:,list(_conv2.keys())]
    # Go through and fill in default values
    for column_name in df2.columns:
        if '(default TRUE)' in column_name:
            df2.loc[df2[column_name].isna(),column_name] = True
            df2.loc[~df2[column_name].isna(),column_name] = df2.loc[~df2[column_name].isna(),column_name].astype(bool)
    # THe annotation_name needs to be strings
    df2['Label'] = df2['Label'].astype(str)
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
            df1.loc[~df1[column_name].isna(),column_name] = df1.loc[~df1[column_name].isna(),column_name].astype(bool)



    # Make sure our titles are all in the dataframe
    for title in _conv.keys():
        if title not in sample_manifest.columns:
            raise ValueError("expected panel definition title not found "+str(title))
    
    df0 = sample_manifest.loc[:,list(_conv.keys())]
    # Go through and fill in default values
    for column_name in df0.columns:
        if '(default TRUE)' in column_name:
            df0.loc[df0[column_name].isna(),column_name] = True
            df0.loc[~df0[column_name].isna(),column_name] = df0.loc[~df0[column_name].isna(),column_name].astype(bool)
    # Go through and cast strings
    for column_name in df0.columns:
        if '(default TRUE)' not in column_name:
            df0[column_name] = df0[column_name].apply(lambda x: x if x is None else str(x))
    # Now lets add some custom code for things with default values
    df0.columns = list(_conv.values())

    samples_json = [row.to_dict() for i,row in df0.iterrows()]
    # Fix the filenames
    for i,sample_row in enumerate(samples_json):
        samples_json[i]['fcs_file'] = _do_fcs_file(samples_json[i]['fcs_file'])

    # collect up the annotations .. a little hard coded
    df1 = sample_manifest.set_index('Sample Name').loc[:,[x for x in set(sample_manifest.columns)-set(_conv.keys()) if 'Unnamed:' not in x]]
    df1 = df1.applymap(lambda x: str(x))
    df1.index.name = 'sample_name'

    # Get the sample annotations, but still missing some information about the sample annotations
    df1lf = df1.stack().reset_index().rename(columns={'level_1':'annotation_group',0:'annotation_value'})
    print(df1lf[0:4])
    print(df2[0:4])
    _combo = df1lf.merge(df2,left_on=['annotation_group','annotation_value'],right_on=['annotation_group','annotation_name'],how='left')
    print(_combo)
    if _combo.loc[_combo['annotation_order'].isna(),:].shape[0] > 0:
        raise ValueError("Undefined annotation group "+str(_combo.loc[df1['annotation_order'].isna(),'annotation_group'].unique()))
    _combo = _combo.drop(columns=['annotation_order','annotation_name','annotation_include','annotation_type'])
    #annotations = OrderedDict([(sample_name,OrderedDict(row.to_dict())) for sample_name, row in _combo.set_index('sample_name').iterrows()])

    annotations = _combo.set_index('sample_name')
    for i, sample_object in enumerate(samples_json):
        sample_name = sample_object['sample_name']
        _annots = annotations.loc[sample_name]
        _annots = [row.to_dict() for sample_name, row in _annots.iterrows()]
        samples_json[i]['sample_annotations'] = _annots

    outputs = {
        "annotation_levels":annotation_levels_json,
        "samples":samples_json
    }
    #print(json.dumps(annotation_levels_json,indent=2))
    _validator.validate(outputs)

    return outputs

def parse_annotations(sample_annotations):
    return

def parse_meta(meta):
    return



