import os
# from psychopy import visual, core, event, monitors, logging, sound
# import psychtoolbox as ptb
import serial
import numpy as np
import csv
# import random
import pandas as pd

def get_block_trialtypes(block_number: int, participant_id: str, data_dir: str = "data"):
    csv_path = os.path.join(data_dir, str(participant_id), f"{participant_id}_trials.csv")
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Trials CSV not found: {csv_path}")

    trialtypes = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        # Expect headers: block, trial, trialtype
        for row in reader:
            try:
                if int(row["block"]) == block_number:
                    trialtypes.append(int(row["trialtype"]))
            except (KeyError, ValueError) as e:
                raise ValueError(f"Malformed row in {csv_path}: {row}") from e

    return trialtypes

def get_block_cuetypes(block_number: int, participant_id: str, data_dir: str = "data"):
    csv_path = os.path.join(data_dir, str(participant_id), f"{participant_id}_trials.csv")
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Trials CSV not found: {csv_path}")
    cuetypes = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        # Expect headers: block, trial, cuetype
        for row in reader:
            try:
                if int(row["block"]) == block_number:
                    cuetypes.append(int(row["cuetype"]))
            except (KeyError, ValueError) as e:
                raise ValueError(f"Malformed row in {csv_path}: {row}") from e
        
        return cuetypes

def shuffle_blocks(participant_id, save_dir):
    """
    Shuffles the blocks from the master_blocks.csv file
    Saves to the participant directory
    """
    # Define paths
    input_csv_path = os.path.join(save_dir, "master_blocks.csv")
    participant_dir = os.path.join(save_dir, participant_id)
    output_csv_path = os.path.join(participant_dir, f"{participant_id}_trials.csv")
    
    # This creates the participant folder inside the data directory
    if not os.path.exists(participant_dir):
        os.makedirs(participant_dir)
        
    # Load the input CSV file
    df = pd.read_csv(input_csv_path)
    
    # Get unique block numbers
    unique_blocks = df['block'].unique()
    
    # Shuffle the block order
    shuffled_blocks = np.random.permutation(unique_blocks)
    
    # Create a mapping from old block numbers to new block numbers
    block_mapping = {old_block: new_block for new_block, old_block in enumerate(shuffled_blocks, start=1)}
    
    # Reorder dataframe by shuffled blocks
    df_shuffled = pd.concat([df[df['block'] == block] for block in shuffled_blocks]).reset_index(drop=True)
    
    # Update block numbers to sequential ordering (1, 2, 3, ...)
    df_shuffled['block'] = df_shuffled['block'].map(block_mapping)
    
    # Save to participant-specific file
    df_shuffled.to_csv(output_csv_path, index=False)
    print(f"Shuffled blocks successfully written to: {output_csv_path}")