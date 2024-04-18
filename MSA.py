from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
from Bio import pairwise2
from Bio.Seq import Seq
import numpy as np
import requests
import time

def blast_protein_sequence(sequence, max_hits=1000, min_identity=30, max_identity=95, min_query_coverage=70):

    result_handle = NCBIWWW.qblast("blastp", "nr", sequence, hitlist_size=max_hits, alignments=1, descriptions=max_hits)
    blast_records = NCBIXML.parse(result_handle)

    fasta_format_sequences = f">query\n{sequence}\n"
    sequences_collected = []  # To store sequences for identity checks
    results_collected = 0
    for record in blast_records:
        for alignment in record.alignments:
            for hsp in alignment.hsps:
                identity_percent = (hsp.identities / hsp.align_length) * 100
                query_coverage = (hsp.align_length / record.query_length) * 100

                # Filter based on identity and query coverage criteria
                if min_identity <= identity_percent <= max_identity and query_coverage >= min_query_coverage:
                    sequence_to_check = Seq(hsp.sbjct)

                    # Check against all previously collected sequences to ensure identity is not above max_identity
                    if not any((pairwise2.align.globalxx(sequence_to_check, seq)[0][2] / len(seq)) * 100 > max_identity for seq in sequences_collected):
                        # Create FASTA formatted entry for this sequence
                        header = f">{alignment.hit_id}"
                        fasta_format_sequences += f"{header}\n{sequence_to_check}\n"

                        # Add to collected sequences and update counter
                        sequences_collected.append(sequence_to_check)
                        results_collected += 1

                        if results_collected >= max_hits:
                            return fasta_format_sequences

    return fasta_format_sequences


def clustal_align(sequences):
    url = "https://www.ebi.ac.uk/Tools/services/rest/clustalo/run"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'email': 'john.mcarthur@curieco.com',
        'sequence': sequences,
        'title': 'My Alignment'
    }
    # Submitting the job
    response = requests.post(url, headers=headers, data=data)
    job_id = response.text
    # Checking the status
    status_url = f"https://www.ebi.ac.uk/Tools/services/rest/clustalo/status/{job_id}"
    while requests.get(status_url).text != 'FINISHED':
        pass  # You can implement better handling with time.sleep()
    # Fetching the result
    result_url = f"https://www.ebi.ac.uk/Tools/services/rest/clustalo/result/{job_id}/fa"
    result = requests.get(result_url).text
    return result



def muscle_align(sequences):
    # Endpoint for submitting MUSCLE jobs
    url = "https://www.ebi.ac.uk/Tools/services/rest/muscle/run"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'email': 'john.mcarthur@curieco.com',
        'sequence': sequences,
        'title': 'My Alignment'
    }
    # Submitting the job
    response = requests.post(url, headers=headers, data=data)
    job_id = response.text

    # Checking the status
    status_url = f"https://www.ebi.ac.uk/Tools/services/rest/muscle/status/{job_id}"
    while requests.get(status_url).text != 'FINISHED':
        time.sleep(5)  # Adding a sleep to avoid hammering the server too frequently

    # Fetching the result
    result_url = f"https://www.ebi.ac.uk/Tools/services/rest/muscle/result/{job_id}/al"
    result = requests.get(result_url).text
    return result