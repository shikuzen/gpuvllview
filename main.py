import streamlit as st
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('config_path', type=str)

args = parser.parse_args()
config_path = args.config_path

with open(config_path, 'r') as f:
    config = json.loads(f.read())

st.write(
    f"""
    # Hello World! {config}
    ### I like to program stuff.
    """
)

st.balloons()