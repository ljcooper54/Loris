import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox


def choose_file(title):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=[('CSV Files', '*.csv'), ('All Files', '*.*')]
    )
    root.destroy()
    return file_path


def load_pricelist(path):
    pricelist = {}
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            item = row.get('Item')
            if not item:
                continue
            price = row.get('Unit Price', '').strip()
            try:
                price_value = float(price)
            except ValueError:
                continue
            pricelist[item.strip()] = price_value
    return pricelist


def normalize_cost(value):
    value = value.replace('$', '').replace(',', '').strip()
    try:
        return float(value)
    except ValueError:
        return None


def main():
    order_file = choose_file('Select Order CSV file')
    if not order_file:
        return
    pricelist_file = choose_file('Select Pricelist CSV file')
    if not pricelist_file:
        return

    pricelist = load_pricelist(pricelist_file)

    mismatches = []
    errors = []

    with open(order_file, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ['Pricelist'] if reader.fieldnames else None
        for line_number, row in enumerate(reader, start=2):  # account for header row
            sku = row.get('Vendor Item Code', '').strip()
            unit_cost = normalize_cost(row.get('Unit Cost', ''))
            price = pricelist.get(sku)
            if price is None:
                errors.append(f"SKU {sku} on line {line_number} in order file does not exist in pricelist file {os.path.basename(pricelist_file)}")
                row['Pricelist'] = ''
                mismatches.append(row)
            else:
                if unit_cost != price:
                    row['Pricelist'] = str(price)
                    mismatches.append(row)

    if not mismatches and not errors:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo('Check complete', 'Unit costs match Pricelist')
        root.destroy()
    else:
        base = os.path.splitext(os.path.basename(order_file))[0]
        error_csv = base + '_errors.csv'
        with open(error_csv, 'w', newline='', encoding='utf-8-sig') as out_csv:
            writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
            writer.writeheader()
            for row in mismatches:
                writer.writerow(row)
        error_txt = base + '_errors.txt'
        with open(error_txt, 'w', encoding='utf-8') as out_txt:
            for msg in errors:
                out_txt.write(msg + '\n')


if __name__ == '__main__':
    main()
