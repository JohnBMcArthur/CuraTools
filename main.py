import streamlit as st
from plotting import parse_excel_paste, calc_hill
from MSA import blast_protein_sequence, clustal_align, muscle_align
from pixelcount import count_pixels_in_range, process_image
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import io

st.set_page_config(page_title="Homepage", page_icon="🏠", layout="wide")
st.title('Curie Co. Tool Suite')
st.caption('Python scripts for Curie Co. data processing and bioinformatics')
st.subheader('Welcome to the Curie Co. R&D tool app! Please select a tool to run from the sidebar.')
st.divider()
st.sidebar.title("Tools")
tool = st.sidebar.radio("Select a Tool", ('BLAST/Alignments', 'Data Processing', 'Statistical Analysis', 'Pixel Counts'))

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
        trim_choice = st.checkbox('Trim the alignment to the input sequence?')
        blast_submit = st.form_submit_button("Run")
        
    if blast_submit:
        if sequence_from_textbox and sequence_from_uploader:
            st.error("Please provide only one type of input: either through the textbox or the file upload.")
        elif sequence_from_textbox or sequence_from_uploader:
            sequence_input = sequence_from_textbox if sequence_from_textbox else sequence_from_uploader
            st.session_state.blast_output = blast_protein_sequence(sequence_input, max_hits, min_identity, max_identity, min_query_coverage)       
            if alignment_type == "Clustal":
                st.session_state.align_output = clustal_align(st.session_state.blast_output, trim_choice)
            elif alignment_type == 'MUSCLE':
                st.session_state.align_output = muscle_align(st.session_state.blast_output, trim_choice)
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

    # Create a text area for input with auto-updating
    user_input = st.text_area("Paste Excel data here:", height=100)

    # Auto-update the output when the input changes
    if user_input:
        df = parse_excel_paste(user_input)
        if df is not None:
            st.dataframe(df)  # Use st.dataframe to display the DataFrame properly
        else:
            st.write("Please paste valid Excel data.")

    if df is not None:
        st.write("DataFrame Loaded. Select X and Y columns:")
        x_column = st.selectbox("Select the X column:", df.columns)
        y_columns = st.multiselect("Select the Y columns:", df.columns, default=df.columns[1])

        if st.button('Transpose DataFrame'):
            df = df.T  # Transpose the DataFrame
            st.write("DataFrame transposed.")
            x_column = st.selectbox("Re-select the X column after transpose:", df.columns)
            y_columns = st.multiselect("Re-select the Y columns after transpose:", df.columns, default=df.columns[1])

        if st.button('Process Data'):
            min_val = 140000  # Define your minimum value
            max_val = df[y_columns].max().max()  # You might adjust this based on your data scaling needs
            calc_hill(df, x_column, y_columns, min_val, max_val)
    else:
        st.write("Please paste data and press enter.")
        # Add your functions or calls to other scripts for the Data Processing tool
elif tool == 'Statistical Analysis':
    st.write("Statistical Analysis Tool")
    # Add your functions or calls to other scripts for the Statistical Analysis tool
elif tool == 'Pixel Counts':
    st.write("Pixel Counting Tool")
    uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        file_names = [file.name for file in uploaded_files]
        selected_file = st.selectbox("Select an image to process", file_names)

        if selected_file:
            image = Image.open(next(file for file in uploaded_files if file.name == selected_file))

            st.image(image, caption=f"Original Image: {selected_file}", use_column_width=True)

            st.write("### Grayscale Image")
            lower,upper = st.slider("Lower grayscale value", 0, 255, (0, 255))
            highlight = st.checkbox("Highlight pixels in the selected range")

            processed_image = process_image(image, lower, upper, highlight)
            st.image(processed_image, caption="Processed Image", use_column_width=True)

            if st.button("Count Pixels in Range"):
                pixel_counts = []
                for file in uploaded_files:
                    image = Image.open(file)
                    in_range, total_pixels = count_pixels_in_range(image, lower, upper)
                    percent_pixels = in_range/total_pixels*100
                    pixel_counts.append({"File Name": file.name, "Pixel Count": in_range, "Total Pixels (%)": total_pixels, "Percentage": percent_pixels})

                pixel_df = pd.DataFrame(pixel_counts)
                st.write(pixel_df)

                # Download as CSV
                csv = pixel_df.to_csv(index=False)
                st.download_button("Download CSV", data=csv, file_name="pixel_counts.csv", mime="text/csv")

