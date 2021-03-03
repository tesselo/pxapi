# Training data sectoin.
TRAINING_DATA_PARSE_FUNCTION = "pixels.stac.parse_training_data"
TRAINING_DATA_CATALOG_LOCATION = "stac/catalog.json"
# Pixels data section.
CONFIG_FILE_NAME = "config.json"
COLLECT_PIXELS_FUNCTION = "pixels.stac.collect_from_catalog_subsection"
CREATE_CATALOG_FUNCTION = "pixels.stac.create_x_catalog"
PIXELS_DATA_COLLECTION_LOCATION = "data/collection.json"

# Keras model section.
TRAIN_MODEL_FUNCTION = "pixels.stac_training.train_model_function"
MODEL_CONFIGURATION_FILE_NAME = "model.json"
MODEL_COMPILE_ARGUMENTS_FILE_NAME = "compile_arguments.json"
MODEL_FIT_ARGUMENTS_FILE_NAME = "fit_arguments.json"
MODEL_H5_FILE_NAME = "model.h5"
# Training section.
GENERATOR_ARGUMENTS_FILE_NAME = "generator_arguments.json"
# Prediction section.
PREDICTION_GENERATOR_ARGUMENTS_FILE_NAME = "generator_arguments.json"
PREDICTION_FUNCTION = "pixels.stac_training.predict"
PREDICTION_CREATE_CATALOG_FUNCTION = "pixels.stac.create_x_catalog"
