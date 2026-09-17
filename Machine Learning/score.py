import json
import os
import joblib
import numpy as np

FEATURES = [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age"
]


def init():
    global model

    model_dir = os.environ["AZUREML_MODEL_DIR"]

    for root, _, files in os.walk(model_dir):
        for file_name in files:
            if file_name.endswith(".pkl"):
                model_path = os.path.join(root, file_name)
                model = joblib.load(model_path)
                print(f"Loaded model: {model_path}")
                return

    raise FileNotFoundError("No .pkl model file found")


def run(raw_data):
    try:
        request = json.loads(raw_data)

        # Extract Azure ML input_data
        input_data = request.get("input_data", request)

        # Handle columns + data format
        if isinstance(input_data, dict):
            columns = input_data.get("columns")
            rows = input_data.get("data")

            if columns is None or rows is None:
                raise ValueError(
                    "input_data must contain 'columns' and 'data'"
                )

            # Reorder each row according to required feature order
            column_positions = {
                column: index for index, column in enumerate(columns)
            }

            missing = [
                feature
                for feature in FEATURES
                if feature not in column_positions
            ]

            if missing:
                raise ValueError(f"Missing columns: {missing}")

            values = [
                [
                    row[column_positions[feature]]
                    for feature in FEATURES
                ]
                for row in rows
            ]

        # Handle plain list of numeric rows
        elif isinstance(input_data, list):
            values = input_data

        else:
            raise ValueError("Unsupported input format")

        # Force a clean 2D numeric array
        model_input = np.asarray(values, dtype=np.float64)

        if model_input.ndim != 2:
            raise ValueError(
                f"Input must be two-dimensional. "
                f"Received shape: {model_input.shape}"
            )

        if model_input.shape[1] != 8:
            raise ValueError(
                f"Expected 8 features but received "
                f"{model_input.shape[1]}"
            )

        predictions = model.predict(model_input)

        response = {
            "predictions": predictions.tolist()
        }

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(model_input)

            response["probabilities"] = probabilities.tolist()
            response["diabetes_probabilities"] = (
                probabilities[:, 1].tolist()
            )

        return response

    except Exception as error:
        return {
            "error": str(error),
            "error_type": type(error).__name__
        }