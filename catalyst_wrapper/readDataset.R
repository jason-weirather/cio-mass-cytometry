read_json <- function(sample_objs,use_marker_list) {
    # Iterate over the samples and get the list of FCS files to read
    #
    # Inputs: object from of the sample json which is a list
    # Outputs: 1) A list of sample files and sample names
    #          2) A Dataframe of annotations
    input_files <- list()
    annotations <- list()
    for (sample_obj in sample_objs) {
        if (sample_obj$include_sample == FALSE) {
            warning(paste("skipping sample ",sample_obj$sample_name," marked for exclusion"))
            next
        }
        sample_name <- sample_obj$sample_name
        fcs_path <- sample_obj$fcs_file$file_path
    
        if (grepl( prefix_to_drop, fcs_path, fixed = TRUE)) {
            # Fix the path if we have a prefix we need to drop
            fcs_path <- str_replace(fcs_path, prefix_to_drop, "")
        }

        # Pull out the annotations
        tannot <- as_tibble(do.call("rbind",sample_obj$sample_annotations))
        tvals <- tannot$annotation_value
        names(tvals) <- tannot$annotation_group
        tvals[["sample_name"]]<-sample_name
        annotations[[sample_name]] <- tvals
    
        # Iterate over the files and make sure the shape of the FCS file meets
        # the data model requirements
        temp_fcs <- read.FCS(fcs_path,truncate_max_range=FALSE)
        temp_markers <- markernames(temp_fcs)
        for (channel_name in names(use_marker_list)) {
            # Iterate over our list of required channels
            if (!(channel_name %in% names(temp_markers))) {
                # Throw an error if the required channel is not present
                stop(paste0("Error channel name ",channel_name," not defeined."))
            }
            if (use_marker_list[[channel_name]] != temp_markers[[channel_name]]) {
                stop(paste0("Error sample ", sample_name,
                         " has a marker name ", temp_markers[[channel_name]], 
                         " for channel name ",channel_name,
                           " that doesnt match for expected marker name ",use_marker_list[[channel_name]]))
            }
        
        }
    
        input_files[[sample_name]] <- fcs_path
    }

    # Set annotations up
    annotations <- as_tibble(do.call("rbind",annotations))
    annotations$sample_name <- as.factor(unlist(annotations$sample_name))
    for (cname in colnames(annotations)) {
        annotations[[cname]] <- as.factor(unlist(annotations[[cname]]))    
    }
    myval <- list(input_files=input_files,annotations=annotations)
    return (myval)
}
create_single_cell_experiment <- function(data_obj) {
    panel <- data_obj$panel$markers
    panel <- as_tibble(do.call("rbind",panel))
    samples_json <- data_obj$samples
    
    tempdf <- panel %>% filter(include_marker==TRUE) %>% select(channel_name,marker_name,marker_display_name)
    use_marker_list = tempdf$marker_name
    names(use_marker_list) <- tempdf$channel_name
    rename_marker_list <- tempdf$marker_display_name
    names(rename_marker_list)  <- tempdf$channel_name
    
    # Make sure all samples are readable
    myval <- read_json(samples_json,use_marker_list)
    input_files <- myval$input_files
    annotations <- myval$annotations

    annotation_levels <- as_tibble(do.call("rbind",json_data$annotation_levels)) %>% filter(annotation_include == TRUE)
    annotation_levels

    for (my_annotation_group in unique(unlist(annotation_levels$annotation_group))) {
        my_factors <- annotation_levels %>% filter(annotation_group==my_annotation_group) %>% arrange(annotation_order)
        my_factor_labels <- unlist(my_factors$annotation_name)
        #my_factor_levels <- unlist(my_factors$annotation_order)
        annotations[[my_annotation_group]] <- factor(annotations[[my_annotation_group]],levels=my_factor_labels)
    }
    
    # Create the large flowset
    fs <- read.flowSet(unlist(input_files),truncate_max_range=FALSE,transformation="linearize")
    # Set sample names according to the input file list order
    sampleNames(fs) <- names(input_files)
    # Subset to just the channels we will be using
    fs <- fs[,names(rename_marker_list)]
    markernames(fs) <- unlist(rename_marker_list)
    
    
    # Now read in the single cell experiment
    # construct SingleCellExperiment
    sub_panel <- panel %>% filter(include_marker==TRUE) %>% select(channel_name, marker_display_name, marker_classification)
    #    This does our default transformation
    sce <- prepData(fs, 
                sub_panel, 
                annotations,
                panel_cols = list(channel = "channel_name", antigen = "marker_display_name", class = "marker_classification"),
                md_cols = list(file = "sample_name", id = "sample_name", factors = unique(unlist(annotation_levels$annotation_group))),
                transform = TRUE,
                cofactor = 5
               )
    return(sce)
}
