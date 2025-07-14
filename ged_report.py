import argparse
import csv
from typing import Dict, List, Optional

class Individual:
    def __init__(self, ident: str):
        self.id = ident
        self.name: str = ""
        self.birth: str = ""
        self.famc: Optional[str] = None
        self.father_id: Optional[str] = None
        self.mother_id: Optional[str] = None

    @property
    def firstname(self) -> str:
        parts = self.name.split('/')
        return parts[0].strip() if parts else ""

    @property
    def surname(self) -> str:
        parts = self.name.split('/')
        return parts[1].strip() if len(parts) > 1 else ""

class Family:
    def __init__(self, ident: str):
        self.id = ident
        self.father: Optional[str] = None
        self.mother: Optional[str] = None
        self.children: List[str] = []


def parse_ged(filepath: str):
    individuals: Dict[str, Individual] = {}
    families: Dict[str, Family] = {}

    current_ind: Optional[Individual] = None
    current_fam: Optional[Family] = None
    in_birth = False

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line:
                continue
            parts = line.split(' ', 2)
            if len(parts) < 2:
                continue
            level = int(parts[0])
            if len(parts) >=3 and parts[1].startswith('@') and parts[1].endswith('@'):
                xref = parts[1]
                tag = parts[2]
            else:
                xref = None
                tag = parts[1]
                data = parts[2] if len(parts)==3 else ''

            if level == 0:
                in_birth = False
                if xref and tag == 'INDI':
                    current_ind = Individual(xref)
                    individuals[xref] = current_ind
                    current_fam = None
                    continue
                elif xref and tag == 'FAM':
                    current_fam = Family(xref)
                    families[xref] = current_fam
                    current_ind = None
                    continue
                else:
                    current_ind = None
                    current_fam = None
                continue

            data = parts[2] if len(parts)==3 else ''
            if current_ind is not None:
                if tag == 'NAME':
                    current_ind.name = data
                elif tag == 'FAMC':
                    current_ind.famc = data
                elif tag == 'BIRT':
                    in_birth = True
                elif tag == 'DATE' and in_birth:
                    current_ind.birth = data
                    in_birth = False
            elif current_fam is not None:
                if tag == 'HUSB':
                    current_fam.father = data
                elif tag == 'WIFE':
                    current_fam.mother = data
                elif tag == 'CHIL':
                    current_fam.children.append(data)

    # resolve parents
    for ind in individuals.values():
        fam_id = ind.famc
        if fam_id and fam_id in families:
            fam = families[fam_id]
            ind.father_id = fam.father
            ind.mother_id = fam.mother

    return individuals, families


def debug_output(individuals: Dict[str, Individual], families: Dict[str, Family], csv_path: str):
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Name', 'Father', 'Mother', 'Sibling Count'])
        for ind in individuals.values():
            fam = families.get(ind.famc) if ind.famc else None
            siblings = len(fam.children) - 1 if fam and ind.id in fam.children else 0
            father_name = individuals[ind.father_id].name if ind.father_id and ind.father_id in individuals else ''
            mother_name = individuals[ind.mother_id].name if ind.mother_id and ind.mother_id in individuals else ''
            writer.writerow([ind.id, ind.name, father_name, mother_name, siblings])


def surname_search(individuals: Dict[str, Individual], families: Dict[str, Family], surname: str, csv_path: str):
    matches = [ind for ind in individuals.values() if ind.surname.lower() == surname.lower()]
    for ind in matches:
        fam_id = ind.famc
        if fam_id and fam_id in families:
            fam = families[fam_id]
            ind.father_id = fam.father
            ind.mother_id = fam.mother
    incomplete = [ind for ind in matches if not (ind.father_id and ind.mother_id)]

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Firstname', 'Lastname', 'Date of Birth', 'Father', 'Mother'])
        for ind in incomplete:
            father_name = individuals[ind.father_id].name if ind.father_id and ind.father_id in individuals else ''
            mother_name = individuals[ind.mother_id].name if ind.mother_id and ind.mother_id in individuals else ''
            writer.writerow([ind.id, ind.firstname, ind.surname, ind.birth, father_name, mother_name])
    print(f"Found {len(matches)} individuals with surname '{surname}'.")


def main():
    parser = argparse.ArgumentParser(description='GEDCOM reporting tool')
    parser.add_argument('gedfile', help='GED file to parse')
    parser.add_argument('surname', help='Surname to search for')
    parser.add_argument('--d', action='store_true', help='Debug mode')
    parser.add_argument('--output', default='report.csv', help='Output CSV file name')
    args = parser.parse_args()

    individuals, families = parse_ged(args.gedfile)

    if args.d:
        debug_output(individuals, families, args.output)
    else:
        surname_search(individuals, families, args.surname, args.output)

if __name__ == '__main__':
    main()
