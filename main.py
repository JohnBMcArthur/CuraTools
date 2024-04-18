import streamlit as st
import time
import os
import datetime
from MSA import blast_protein_sequence, clustal_align, muscle_align

# Setting page config
st.set_page_config(page_title="Homepage", page_icon="🏠", layout="wide")

# Main title on the page
st.title('Curie Co. Tool Suite')

# Caption under the title
st.caption('Python scripts for Curie Co. data processing and bioinformatics')

# Welcome subheader
st.subheader('Welcome to the Curie Co. R&D tool app! Please select a tool to run from the sidebar.')

# Divider
st.divider()

# Sidebar for tool selection
st.sidebar.title("Tools")
tool = st.sidebar.radio("Select a Tool", ('BLAST/Alignments', 'Data Processing', 'Statistical Analysis'))

# Main page content changes based on sidebar selection
if tool == 'BLAST/Alignments':
    with st.form('BLAST_form'):
        st.header("BLAST and Alignment Tool")
        st.divider()
        query_name = st.text_input("Query name:")
        st.subheader("Sequence Input")
        sequence_from_textbox = st.text_input("Add your sequence with no additional characters:")
        sequence_from_uploader = st.file_uploader("Or choose a fasta formatted sequence file:")
        
        st.subheader('BLAST options:')
        max_hits = st.slider('Maximum number of results:', min_value=1, max_value=5000, value=1000)
        min_identity = st.slider('Minimum identity to query:', min_value=0, max_value=100, value=30)
        max_identity = st.slider('Maximum identity between any pair of sequences:', min_value=0, max_value=100, value=100)
        min_query_coverage = st.slider('Minimum coverage:', min_value=0, max_value=100, value=70)
        
        st.subheader('Alignment options:')
        alignment_type = st.selectbox("What type of alignment do you want to run?", ['None', 'Clustal', 'MUSCLE'])
        
        blast_submit = st.form_submit_button("Run")
        
    if blast_submit:
        if sequence_from_textbox and sequence_from_uploader:
            st.error("Please provide only one type of input: either through the textbox or the file upload.")
        elif sequence_from_textbox or sequence_from_uploader:
            sequence_input = sequence_from_textbox if sequence_from_textbox else sequence_from_uploader
            st.session_state.blast_output = blast_protein_sequence(sequence_input, max_hits, min_identity, max_identity, min_query_coverage)       
            if alignment_type == "Clustal":
                st.session_state.align_output = clustal_align(st.session_state.blast_output)
            elif alignment_type == 'MUSCLE':
                st.session_state.align_output = muscle_align(st.session_state.blast_output)
            st.success("Analysis complete.")
        else:
            st.error("No sequence input provided. Please enter a sequence or upload a file.")
            
        # Download buttons should only be visible after processing
        if 'blast_output' in st.session_state and st.session_state.blast_output:
            st.download_button('Download BLAST results', st.session_state.blast_output, f'{query_name}_BLAST.fasta')
        if 'align_output' in st.session_state and st.session_state.align_output:
            st.download_button('Download Alignment results', st.session_state.align_output, f'{query_name}_align.fasta')

            

        #blast_protein_sequence(sequence, max_hits=1000, min_identity=30, max_identity=95, min_query_coverage=70):
        # Add your functions or calls to other scripts for the Bioinformatics tool
elif tool == 'Data Processing':
    st.write("Data Processing Tool")
    # Add your functions or calls to other scripts for the Data Processing tool
elif tool == 'Statistical Analysis':
    st.write("Statistical Analysis Tool")
    # Add your functions or calls to other scripts for the Statistical Analysis tool

