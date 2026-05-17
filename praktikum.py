# --- NASTAVENIA ---------------------
vstupny_subor = 'tab.csv'
#-------------------------------------
import numpy as np
import uncertainties.unumpy as unp
from uncertainties import ufloat
#-------------------------------------
#"""OBSAH modulu:
# Data(start_row,end_row): 
#       modul na načítanie dát z tbuľky s globálnym vstupny_subor do py arrayu

# nezavisle(x): 
#       zbaví sa matíck kovariancie

# to_sci(val, latex=True): 
#       zmení na exponenciáloví zápis kompatibilný s csv(False) resp. latex(True)

# Write(x, naz, jed, subor="tab_vystup.csv", prepisat=False, latex_format=True): 
#       zapíše hodnoty z x 
#       názov veličiny naz 
#       jednotkách jed 
#       výstupny súbor
#       prepíše resp. neprepíše tabuľku
#       latex formát

# Write_Universal(data, nazov="velicina", jednotka="-", subor="vystup.csv", prepisat=True, latex=True):
#       -//-

# Tex_table(vstupny_subor, start_row,end_row, vystupny_subor):
#       zoberie csv tabuľku a prepíše ju na latex tabuľku
# """
#-------------------------------------
#načítanie dát
def Data(start_row, end_row):
    """
    Načíta riadky od start_row po end_row (vrátane).
    Automaticky čistí úvodzovky, čiarky a prázdne bunky.
    """
    start_row=start_row-1
    data = []
    global vstupny_subor
    
    try:
        with open(vstupny_subor, 'r', encoding="utf-8") as f:
            vsetky_riadky = f.readlines()
    except FileNotFoundError:
        print(f"Súbor {vstupny_subor} nebol nájdený.")
        return []

    # Slicing v Pythone končí pred end_row, preto +1, aby to bolo "vrátane"
    vyber = vsetky_riadky[start_row : end_row + 1]

    for riadok in vyber:
        # 1. Rozdelíme podľa bodkočiarky
        bunky = riadok.strip().split(';')
        
        spracovany_riadok = []
        for b in bunky:
            # 2. Odstránime úvodzovky, medzery a symboly
            cista_hodnota = b.replace('"', '').replace('±', '').strip()
            
            if cista_hodnota == "":
                continue
                
            # 3. Prevedieme desatinnú čiarku na bodku
            finalna_string_hodnota = cista_hodnota.replace(',', '.')
            
            try:
                spracovany_riadok.append(float(finalna_string_hodnota))
            except ValueError:
                # Ak to nie je číslo (napr. hlavička "t/s"), preskočíme bunku
                continue
        
        # Pridáme riadok len ak obsahuje nejaké čísla
        if spracovany_riadok:
            data.append(spracovany_riadok)
            
    return data


#reset nezávislých hodnôt
def nezavisle(x):
    """
    pouzitie:
    r = nezavisle(d / 2000) ... tj na
    t_unc = nezavisle(t_unco)
    """
    if isinstance(x, np.ndarray): # pre polia (uarray)
        return unp.uarray(unp.nominal_values(x), unp.std_devs(x))
    return ufloat(x.n, x.s) # pre jednotlivé čísla (ufloat)



#premena na hodnoty 10^k pre čítanie v latexu resp. v .csv
def to_sci(val, latex=True):
    """Prevedie číslo na vedecký formát. 
    latex=True: vráti formát pre LaTeX ($... \times 10^{n}$)
    latex=False: vráti formát pre Excel/CSV (napr. 1.23E+02)
    """
    if val == 0: return "0"
    
    if latex:
        s = f"{val:.4e}"
        base, expo = s.split('e')
        return f"${base} \\times 10^{{{int(expo)}}}$"
    else:
        return f"{val:.4e}".replace('.', ',') # Excel v SK/CZ verzii vyžaduje čiarku

#zápis dát latex resp. .csv
def Write(x, naz, jed, subor="tab_vystup.csv", prepisat=False, latex_format=True):
    """
    x: dáta (uarray)
    naz: názov veličiny 
    jed: jednotka
    prepisat: ak True, zmaže starý súbor. Ak False, pridá na koniec.
    latex_format: ak True, zapíše s $ \times 10^n $, ak False, zapíše ako čisté čísla.
    """
    mod = "w" if prepisat else "a"
    
    # Získanie hodnôt a neistôt
    vals = unp.nominal_values(x)
    errs = unp.std_devs(x)
    
    with open(subor, mod, encoding="utf-8") as t:
        # Ak pridávame do existujúceho súboru, vložíme prázdny riadok pre oddelenie tabuliek
        if not prepisat:
            t.write("\n")
            
        # Hlavička tabuľky
        t.write(f"Index;{naz} / {jed};Chyba / {jed}\n")
        
        for i in range(len(x)):
            v_str = to_sci(vals[i], latex=latex_format)
            e_str = to_sci(errs[i], latex=latex_format)
            
            # Formátovanie riadku
            line = f"{naz}_{{{i+1}}};{v_str};{e_str}\n"
            t.write(line)
            print(line.strip()) # Výpis do konzoly pre kontrolu

def Write_Universal(data, nazov="velicina", jednotka="-", subor="vystup.csv", prepisat=True, latex=True):
    mod = "w" if prepisat else "a"
    
    with open(subor, mod, encoding="utf-8") as f:
        # 1. PRÍPAD: Poslal si len jednoduché pole (uarray) - správaj sa ako starý kód
        if not isinstance(data[0], (list, np.ndarray)):
            f.write(f"Index;{nazov} / {jednotka};Chyba / {jednotka}\n")
            for i, val in enumerate(data):
                v_s = to_sci(val.n, latex)
                e_s = to_sci(val.s, latex)
                f.write(f"{nazov}_{{{i+1}}};{v_s};{e_s}\n")
        
        # 2. PRÍPAD: Poslal si maticu (zoznam zoznamov) - správaj sa ako nový kód
        else:
            for row in data:
                line_parts = []
                for item in row:
                    if hasattr(item, 'nominal_value'): # Je to ufloat
                        line_parts.append(to_sci(item.n, latex))
                        line_parts.append(to_sci(item.s, latex))
                    else:
                        line_parts.append(str(item))
                f.write(";".join(line_parts) + "\n")

#export z tabuľky do latexu
def Tex_table(vstupny_subor, start_row,end_row, vystupny_subor):
    """
    vstup od kade do kade do výstupu
    """
    data = []
    start_row = start_row -1
    with open(vstupny_subor, 'r', encoding="utf-8") as f:
        vsetky_riadky = f.readlines()

    vyber = vsetky_riadky[start_row:end_row]

    for riadok in vyber:
        bunky = riadok.strip().split(';')
        ciste_bunky = [b.strip() for b in bunky if b.strip() != "" and b.strip() != "±"]
        if not ciste_bunky: continue
        spracovany_riadok = []
        for b in ciste_bunky:
            hodnota = b.replace(',', '.')
            try:
                spracovany_riadok.append(float(hodnota))
            except ValueError:
                spracovany_riadok.append(b)
        data.append(spracovany_riadok)
    if data:
        pocet_stĺpcov = len(data[0])
        with open(vystupny_subor, 'w', encoding="utf-8-sig") as t:
            t.write(r"\begin{table}[H]" + "\n")
            t.write(r"  \centering" + "\n")
            t.write(r"  \caption{Tabuľka nameraných hodnôt.}" + "\n")
            t.write("   \label{tab:}\n")
            align = "|c|" + "c|" * (pocet_stĺpcov - 1)
            t.write(r"  \begin{tabular}{" + align + "}" + "\n")
            t.write(r"      \hline" + "\n")
            for i, riadok in enumerate(data):
                # Ak chceš v PDF desatinné čiarky, zmeň .replace('.', ',') na konci
                riadok_string = " & ".join([
                    f"{val:.3f}".replace('.', ',') if isinstance(val, float) else str(val).replace('.', ',') 
                    for val in riadok
                ])
                t.write(f"      {riadok_string} \\\\" + "\n")
                if i == 0:
                    t.write(r"      \hline" + "\n")
                else:
                    t.write(r"      \hline" + "\n")   
            t.write(r"  \end{tabular}" + "\n")
            t.write(r"\end{table}" + "\n")


#-//- podľa pleskota
class Table:
    """
    Used to create a table in latex format.

    The class Table is created by adding columns with the add_column method and
    the table is printed to a file with the print_table method.
    """

    def __init__(self, file_name, label, caption, encoding = 'utf-8'):
        """
        The constructor of the class.

        Parameters
        ----------
        file_name : str
            Name of the file where the table will be printed.
        label : str
            Label of the table.
        caption : str
            Caption of the table.
        encoding : str
            Encoding of the file (default is 'utf-8').

        Attributes
        ----------
        file_name : str
            Name of the file where the table will be printed.
        label : str
            Label of the table.
        caption : str
            Caption of the table.
        encoding : str
            Encoding of the file (default is 'utf-8').
        columns : list
            List of columns in the table. Each column is a dictionary with the following keys:
                - values: list or numpy.ndarray
                - name: str
                - unit: str
                - format: str
                - n_digits: int or None
                - n_significant: int or None
        """
        self.file_name = file_name
        self.label = label
        self.caption = caption
        self.encoding = encoding
        self.columns = []

    def add_column(self, values, name, unit = '', format = 'c', n_digits = None, n_significant = None):
        """ 
        Add one column to the table.

        The column is added to the list of columns in the table.
        The column is stored as a dictionary with the keys described in `__init__`.

        Parameters
        ----------
        values : list or numpy.ndarray
            List of values in the column.
        name : str
            Name of the column.
        unit : str
            Unit of the values in the column.
        format : str
            Format of the column (default is 'c').
        n_digits : int
            For rounding. Numbers of digits after the decimal point.
        n_significant :int
            Another rounding option. Number of significant figures.
        """
        self.columns.append({"values":values, "name":name, "unit":unit, "format":format, "n_digits":n_digits, "n_significant":n_significant })
    def print_table(self):
        """
        The print_table method prints the table in latex format.

        The table is printed in the file specified in the constructor.
        The file content is overwritten if the file already exists.
        The columns are printed in the order they were added with the add_column method.
        The output file starts like this:
        
        ```
        \begin{table}
          \centering
          \begin{tabular}{|format1|format2|...|}
            \hline
            name1 [unit1] & name2 [unit2] & ... \\
            \hline
        ```
        
        where format1, format2, ... are the formats of the columns specified in the add_column method,
        and name1 [unit1], name2 [unit2], ... are the names and units of the columns.
        If the unit of a column is an empty string, only the name of the column is printed in the header row.
        The values in the columns are printed in the following lines,
        where the values in each line are separated by an ampersand (&)
        and the line ends with a double backslash (\\).
        If n_digits or n_significant is specified for a column,
        the values in that column are rounded accordingly before printing.
        The file ends with the lines:
        
        ```
          \hline
          \end{tabular}
          \caption{self.caption}
          \label{self.label}
        \end{table}
        ```

        where self.label and self.caption are the values of label and caption specified in the constructor.
        """
        with open(self.file_name, 'w', encoding=self.encoding) as t:
            t.write(r"\begin{table}" + "\n")
            t.write(r"  \centering" + "\n")
            
            ps = "|".join(k["format"] for k in self.columns)
            t.write(f"  \\begin{{tabular}}{{|{ps}|}}\n") 
            t.write(r"    \hline" + "\n") 
            
            header = []       
            for p in self.columns:
                text = p["name"]
                if p["unit"]:
                    text += f" [{p['unit']}]"
                header.append(text)                
            t.write(f"    {' & '.join(header)} \\\\\n")
            t.write(r"    \hline" + "\n")
            
            dlzka = len(self.columns[0]["values"])
            for i in range(dlzka):
                row = []
                for p in self.columns:
                    k = p["values"][i]
                    if p["n_significant"] is not None:
                        hodnota = f"{k:.{p['n_significant']}g}"
                    elif p["n_digits"] is not None:
                        hodnota = f"{k:.{p['n_digits']}f}"
                    else:
                        hodnota = str(k)
                    row.append(hodnota)
                t.write(f"    {' & '.join(row)} \\\\\n") 
                
            t.write(r"    \hline" + "\n")
            t.write(r"  \end{tabular}" + "\n")
            t.write(f"  \\caption{{{self.caption}}}\n")
            t.write(f"  \\label{{{self.label}}}\n")
            t.write(r"\end{table}" + "\n")


