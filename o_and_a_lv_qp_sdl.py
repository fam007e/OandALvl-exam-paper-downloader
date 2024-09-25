"""
This script downloads exam papers and mark schemes from the xtremepapers' website
for CAIE and Edexcel boards and organizes them into directories based on the 
exam board and subject.
"""
import os
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://papers.xtremepape.rs/'

def get_exam_board():
    """Prompt user to choose the examination board."""
    while True:
        print("\nChoose the examination board:")
        print("1. Cambridge (CAIE)")
        print("2. Edexcel")
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice == '1':
            return 'CAIE'
        if choice == '2':
            return 'Edexcel'
        print("Invalid choice. Please enter 1 or 2.")

def get_exam_level(exam_board):
    """Prompt user to choose the examination level based on the selected board."""
    while True:
        print("\nChoose the examination level:")
        if exam_board == 'CAIE':
            print("1. O Level")
            print("2. AS and A Level")
        else:  # Edexcel
            print("1. International GCSE")
            print("2. Advanced Level")
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice == '1':
            return 'O+Level' if exam_board == 'CAIE' else 'International+GCSE'
        if choice == '2':
            return 'AS+and+A+Level' if exam_board == 'CAIE' else 'Advanced+Level'
        print("Invalid choice. Please enter 1 or 2.")

def get_subjects(exam_board, exam_level):
    """Fetch subjects for the selected exam board and level."""
    if exam_board == 'CAIE':
        url = f'{BASE_URL}index.php?dirpath=./CAIE/{exam_level}/&order=0'
    else:  # Edexcel
        url = f'{BASE_URL}index.php?dirpath=./Edexcel/{exam_level}/&order=0'

    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    subject_links = soup.find_all('a', class_='directory')

    subjects = {}
    for link in subject_links:
        subject_name = link.text.strip('[]')
        if subject_name != '..':  # Skip the parent directory link
            subjects[subject_name] = BASE_URL + link['href']
    return subjects

def get_pdfs(subject_url, exam_board):
    """Fetch PDF links for the selected subject."""
    response = requests.get(subject_url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    if exam_board == 'Edexcel':
        return get_edexcel_pdfs(subject_url)

    pdf_links = soup.find_all('a', class_='file', href=re.compile(r'\.pdf$'))
    return {link.text.strip(): BASE_URL + link['href'] for link in pdf_links}

def get_edexcel_pdfs(subject_url):
    """Fetch PDF links for Edexcel subjects."""
    pdfs = {}
    response = requests.get(subject_url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    year_links = soup.find_all('a', class_='directory')

    for year_link in year_links:
        if year_link.text.strip('[]') != '..':
            year_url = BASE_URL + year_link['href']
            year_response = requests.get(year_url, timeout=10)
            year_soup = BeautifulSoup(year_response.text, 'html.parser')

            qp_link = year_soup.find('a', class_='directory', text='[Question-paper]')
            ms_link = year_soup.find('a', class_='directory', text='[Mark-scheme]')

            if qp_link:
                qp_url = BASE_URL + qp_link['href']
                qp_pdfs = get_pdfs_from_page(qp_url)
                pdfs.update(qp_pdfs)

            if ms_link:
                ms_url = BASE_URL + ms_link['href']
                ms_pdfs = get_pdfs_from_page(ms_url)
                pdfs.update(ms_pdfs)

    return pdfs

def get_pdfs_from_page(url):
    """Fetch all PDF links from a specific page."""
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    pdf_links = soup.find_all('a', class_='file', href=re.compile(r'\.pdf$'))
    return {link.text.strip(): BASE_URL + link['href'] for link in pdf_links}

def download_pdf(url, filename, subject_dir, exam_board):
    """Download a PDF and save it in the appropriate directory."""
    response = requests.get(url, timeout=10)
    subdir = categorize_pdf(filename, exam_board)

    dir_path = os.path.join(subject_dir, subdir)
    os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, filename)
    with open(file_path, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded: {filename}")

def categorize_pdf(filename, exam_board):
    """Categorize the PDF as question paper, mark scheme, or miscellaneous."""
    if exam_board == 'CAIE':
        if '_ms_' in filename:
            return 'ms'
        if '_qp_' in filename:
            return 'qp'
        return 'misc'
    # Edexcel
    if 'question' in filename.lower():
        return 'qp'
    if 'mark' in filename.lower() or 'ms' in filename.lower():
        return 'ms'
    return 'misc'

def print_subjects_in_columns(subjects):
    """Print the available subjects in multiple columns."""
    terminal_width = os.get_terminal_size().columns
    max_width = max(len(f"{i}. {subject}") for i, subject in enumerate(subjects, 1))
    num_columns = max(1, terminal_width // (max_width + 2))
    subject_list = [f"{i}. {subject}" for i, subject in enumerate(subjects, 1)]
    for i in range(0, len(subject_list), num_columns):
        row = subject_list[i:i + num_columns]
        print("  ".join(item.ljust(max_width) for item in row))

def main():
    """Main function to run the script."""
    exam_board = get_exam_board()
    exam_level = get_exam_level(exam_board)
    subjects = get_subjects(exam_board, exam_level)

    print(f"\nAvailable subjects for {exam_board} {exam_level.replace('+', ' ')}:")
    print_subjects_in_columns(subjects)

    choices = input("\nEnter the numbers of the subjects you want to download (space-separated): ")
    selected_indices = [int(x.strip()) for x in choices.split()]

    selected_subjects = list(subjects.keys())
    for index in selected_indices:
        subject = selected_subjects[index - 1]
        subject_url = subjects[subject]
        print(f"\nProcessing {subject}...")

        pdfs = get_pdfs(subject_url, exam_board)
        subject_dir = os.path.join(
            exam_board,
            exam_level.replace('+', ' '),
            subject.replace('/', '_').replace('&', 'and')
        )
        os.makedirs(subject_dir, exist_ok=True)

        for filename, pdf_url in pdfs.items():
            download_pdf(pdf_url, filename, subject_dir, exam_board)

if __name__ == "__main__":
    main()
