#!/usr/bin/env python
"""Script to register the trained model in the database"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models_db import ModelsDatabase
import json

def main():
    db = ModelsDatabase()

    # Check if model already exists
    models = db.get_models()
    if models:
        print("Models already in database:")
        for m in models:
            print(f"  ID: {m[0]}, Name: {m[1]}, Type: {m[4]}, Active: {m[7]}")
        return

    # Add the trained model
    db.add_model(
        name='Traffic Vehicle Classifier',
        model_path='models/traffic_model.keras',
        encoder_path='models/label_encoder.pkl',
        model_type='classification',
        classes=['ambulance', 'fire_truck', 'police', 'car', 'bus', 'truck', 'bicycle', 'motorcycle']
    )

    # Get all models
    models = db.get_models()
    print('Models in database:')
    for m in models:
        print(f'  ID: {m[0]}, Name: {m[1]}, Type: {m[4]}, Active: {m[7]}')

    # Set as active
    db.set_active_model(1)
    print('\nModel set as active!')

if __name__ == '__main__':
    main()

