from matplotlib.pyplot import get
# import streamlit as st
from get_gpu_info import get_server_info
# st.title("GPU cluster VLL visualization")
username = 'nakorn'
password = 'ice100235'

server_stat = get_server_info(username, password)
print(server_stat)