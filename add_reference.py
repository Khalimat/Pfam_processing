#!/usr/bin/env python

"""Add reference to a DESC file or CLANDESC file
Dump to stdout if there isn't a desc file"""

import sys
import os
import textwrap
import argparse
import shutil
from Bio import Entrez

class PfamReference:
    def __init__(self):
        self.pubmed = ""
        self.title = ""
        self.authors = ""
        self.location = ""

    def get_ref_by_pubmed(self, pmid, email="anonymous@example.com"):
        if not email or "@" not in email:
            raise ValueError("NCBI requires a valid email address")
        Entrez.email = email
        try:
            handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
            record = Entrez.read(handle)
        except Exception as e:
            print(f"PubMed fetch failed: {e}", file=sys.stderr)
            sys.exit(1)
        handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        record = Entrez.read(handle)
        handle.close()

        article = record['PubmedArticle'][0]['MedlineCitation']['Article']
        self.pubmed = pmid
        self.title = article['ArticleTitle']
        self.authors = "; ".join(
            f"{author['LastName']} {author['Initials']}"
            for author in article['AuthorList']
        )

        journal = article['Journal']
        vol = article.get('Journal', {}).get('Volume', '')
        issue = article.get('Journal', {}).get('Issue', '')
        pages = article.get('Pagination', {}).get('MedlinePgn', '')
        year = journal['JournalIssue']['PubDate'].get('Year', '')

        journal_title = journal['Title']
        self.location = f"{journal_title} {year};{vol}({issue}):{pages}"

def main():
    parser = argparse.ArgumentParser(description="Add references to DESC/CLANDESC files")
    parser.add_argument("-n", "--nodesc", action="store_true", help="Write to stdout instead of file")
    parser.add_argument("-rn", type=int, help="Override last RN number")
    parser.add_argument("pmids", nargs="+", help="PubMed IDs to add")
    parser.add_argument("--email", help="NCBI-required email address")
    args = parser.parse_args()

    file_path = None
    already_in = set()
    rn = args.rn if args.rn else 0

    if not args.nodesc:
        if os.path.exists("DESC") and not os.path.exists("CLANDESC"):
            file_path = "DESC"
        elif not os.path.exists("DESC") and os.path.exists("CLANDESC"):
            file_path = "CLANDESC"
        elif os.path.exists("DESC") and os.path.exists("CLANDESC"):
            sys.exit("\nFound both a DESC file and CLANDESC file!! Delete the incorrect one and re-run!\n")
        else:
            print("Could not find a DESC or CLANDESC file", file=sys.stderr)
            print("Writing to STDOUT ......", file=sys.stderr)
            print("--------------------------------------", file=sys.stderr)
            args.nodesc = True

    if not args.nodesc:
        with open(file_path, 'r') as desc_file:
            for line in desc_file:
                if line.startswith("RM"):
                    pmid = line.split()[1]
                    already_in.add(pmid)
                elif line.startswith("RN") and not args.rn:
                    rn = int(line.split()[1].strip("[]"))

    refs = []
    for pmid in args.pmids:
        if pmid in already_in:
            print(f"PMID [{pmid}] is already in the DESC file, not adding")
            continue
        ref = PfamReference()
        ref.get_ref_by_pubmed(pmid)
        refs.append(ref)

    pushback = []
    if not args.nodesc:
        desc_new = open(file_path + "NEW", 'w')
        with open(file_path, 'r') as desc_file:
            for line in desc_file:
                if line.startswith("CC") or line.startswith("**"):
                    pushback.append(line)
                    break
                desc_new.write(line)
            else:
                pushback = None
            # Write remaining lines if we broke early
            if pushback:
                for line in desc_file:
                    pushback.append(line)

    wrapper = textwrap.TextWrapper(width=75, subsequent_indent="RT   ")

    for ref in refs:
        title = ref.title.strip('"')
        blurb = f"RN   [{rn + 1}]\n"
        blurb += f"RM   {ref.pubmed}\n"
        blurb += wrapper.fill(f"RT   {title}.") + "\n"
        blurb += textwrap.fill(f"RA   {ref.authors};",
                              width=75,
                              initial_indent="RA   ",
                              subsequent_indent="RA   ") + "\n"
        blurb += f"RL   {ref.location}\n"

        if args.nodesc:
            print(blurb)
        else:
            desc_new.write(blurb)
        rn += 1

    if not args.nodesc:
        if pushback:
            desc_new.writelines(pushback)
        desc_new.close()

        shutil.copy(file_path, "OLD" + file_path)
        shutil.copy(file_path + "NEW", file_path)

if __name__ == "__main__":
    main()
