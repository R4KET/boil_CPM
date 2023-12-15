import tkinter as tk
from tkinter import ttk, simpledialog, filedialog
import matplotlib.pyplot as plt

class Zadanie:
    def __init__(self, nazwa, czas_trwania, poprzednicy=None):
        self.nazwa = nazwa
        self.czas_trwania = czas_trwania
        self.poprzednicy = poprzednicy if poprzednicy is not None else []
        self.wczesny_start = None
        self.wczesne_zakonczenie = None
        self.pozny_start = None
        self.pozne_zakonczenie = None
        self.rezerwa = None

def oblicz_wczesny_start(zadanie, zadania):
    if zadanie.wczesny_start is None:
        zadanie.wczesny_start = max([oblicz_wczesny_start(zadania[poprzednik], zadania) for poprzednik in zadanie.poprzednicy], default=0)
        zadanie.wczesne_zakonczenie = zadanie.wczesny_start + zadanie.czas_trwania
    return zadanie.wczesne_zakonczenie

def oblicz_pozne_zakonczenie(zadanie, zadania, czas_trwania_projektu):
    if zadanie.pozne_zakonczenie is None:
        zadanie.pozne_zakonczenie = min([oblicz_pozne_zakonczenie(zadania[poprzednik], zadania, czas_trwania_projektu) for poprzednik in zadanie.poprzednicy], default=czas_trwania_projektu)
        zadanie.pozny_start = zadanie.pozne_zakonczenie - zadanie.czas_trwania
    return zadanie.pozne_zakonczenie

def oblicz_rezerwe(zadanie):
    return zadanie.pozny_start - zadanie.wczesny_start

def sciezka_krytyczna(zadania):
    czas_trwania_projektu = max([oblicz_wczesny_start(zadanie, zadania) for zadanie in zadania.values()])
    for zadanie in zadania.values():
        oblicz_wczesny_start(zadanie, zadania)
        oblicz_pozne_zakonczenie(zadanie, zadania, czas_trwania_projektu)
        zadanie.rezerwa = oblicz_rezerwe(zadanie)

    zadania_na_sciezce_krytycznej = [zadanie for zadanie in zadania.values() if zadanie.rezerwa == 0]
    return zadania_na_sciezce_krytycznej

def oblicz_cpm(zadania):
    for zadanie in zadania.values():
        oblicz_wczesny_start(zadanie, zadania)

    czas_trwania_projektu = max([zadanie.wczesne_zakonczenie for zadanie in zadania.values()])
    for zadanie in zadania.values():
        zadanie.slack = czas_trwania_projektu - zadanie.wczesne_zakonczenie

def parsuj_dane_wejsciowe(ścieżka_pliku=None, dane_wejsciowe=None):
    zadania = {}
    if ścieżka_pliku:
        with open(ścieżka_pliku, 'r') as plik:
            dane_wejsciowe = plik.readlines()

    for linia in dane_wejsciowe:
        czesci = linia.split(',')
        nazwa = czesci[0].strip()
        czas_trwania = int(czesci[2].strip())
        poprzednicy = [] if len(czesci) < 2 or not czesci[1].strip() else czesci[1].strip().split()
        zadania[nazwa] = Zadanie(nazwa, czas_trwania, poprzednicy)
    return zadania

def wczytaj_dane_z_pliku():
    ścieżka_pliku = filedialog.askopenfilename(title="Wybierz plik", filetypes=[("Pliki tekstowe", "*.txt")])
    if ścieżka_pliku:
        zadania = parsuj_dane_wejsciowe(ścieżka_pliku=ścieżka_pliku)
        return zadania
    else:
        return None

def generuj_harmonogram_gantta(zadania):
    gantt_chart = []
    for zadanie in zadania.values():
        gantt_chart.append({
            "Zadanie": zadanie.nazwa,
            "Start": zadanie.wczesny_start,
            "Koniec": zadanie.wczesne_zakonczenie
        })
    return gantt_chart

def rysuj_harmonogram_gantta(gantt_chart):
    fig, ax = plt.subplots()
    for idx, zadanie_info in enumerate(gantt_chart):
        ax.barh(y=idx, width=zadanie_info["Koniec"] - zadanie_info["Start"], left=zadanie_info["Start"], align='center', label=zadanie_info["Zadanie"])
    ax.set_yticks(range(len(gantt_chart)))
    ax.set_yticklabels([zadanie_info["Zadanie"] for zadanie_info in gantt_chart])
    ax.set_xlabel("Czas")
    ax.set_title("Harmonogram Gantta")
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1))
    plt.show()

def rysuj_cpm(zadania):
    root_cpm = tk.Tk()
    root_cpm.title("Wyniki CPM")

    treeview_cpm = ttk.Treeview(root_cpm)
    treeview_cpm["columns"] = ("Nazwa", "Wczesny Start", "Wczesne Zakończenie", "Pozny Start", "Pozne Zakończenie", "Rezerwa", "Czynnosc Krytyczna")
    treeview_cpm.column("#0", width=0, stretch=tk.NO)
    treeview_cpm.column("Nazwa", anchor=tk.W, width=100)
    treeview_cpm.column("Wczesny Start", anchor=tk.W, width=100)
    treeview_cpm.column("Wczesne Zakończenie", anchor=tk.W, width=150)
    treeview_cpm.column("Pozny Start", anchor=tk.W, width=100)
    treeview_cpm.column("Pozne Zakończenie", anchor=tk.W, width=150)
    treeview_cpm.column("Rezerwa", anchor=tk.W, width=100)
    treeview_cpm.column("Czynnosc Krytyczna", anchor=tk.W, width=150)

    treeview_cpm.heading("#0", text="", anchor=tk.W)
    treeview_cpm.heading("Nazwa", text="Nazwa", anchor=tk.W)
    treeview_cpm.heading("Wczesny Start", text="Wczesny Start", anchor=tk.W)
    treeview_cpm.heading("Wczesne Zakończenie", text="Wczesne Zakończenie", anchor=tk.W)
    treeview_cpm.heading("Pozny Start", text="Pozny Start", anchor=tk.W)
    treeview_cpm.heading("Pozne Zakończenie", text="Pozne Zakończenie", anchor=tk.W)
    treeview_cpm.heading("Rezerwa", text="Rezerwa", anchor=tk.W)
    treeview_cpm.heading("Czynnosc Krytyczna", text="Czynnosc Krytyczna", anchor=tk.W)

    for zadanie in zadania.values():
        czynnosc_krytyczna = "Tak" if zadanie.rezerwa == 0 else "Nie"
        rezerwa = zadanie.rezerwa if zadanie.rezerwa is not None else ""
        treeview_cpm.insert("", "end", values=(zadanie.nazwa, zadanie.wczesny_start, zadanie.wczesne_zakonczenie,
                                               zadanie.pozny_start, zadanie.pozne_zakonczenie, rezerwa, czynnosc_krytyczna))

    treeview_cpm.pack(pady=10)
    root_cpm.mainloop()

class GanttChartApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Harmonogram Gantta")

        self.zadania = {}
        self.treeview = ttk.Treeview(self.master)
        self.treeview["columns"] = ("Nazwa", "Czas Trwania", "Poprzednicy")
        self.treeview.column("#0", width=0, stretch=tk.NO)
        self.treeview.column("Nazwa", anchor=tk.W, width=100)
        self.treeview.column("Czas Trwania", anchor=tk.W, width=100)
        self.treeview.column("Poprzednicy", anchor=tk.W, width=150)

        self.treeview.heading("#0", text="", anchor=tk.W)
        self.treeview.heading("Nazwa", text="Nazwa", anchor=tk.W)
        self.treeview.heading("Czas Trwania", text="Czas Trwania", anchor=tk.W)
        self.treeview.heading("Poprzednicy", text="Poprzednicy", anchor=tk.W)

        self.treeview.pack(pady=10)

        self.button_dodaj = tk.Button(self.master, text="Dodaj nowe zadanie", command=self.dodaj_nowe_zadanie)
        self.button_dodaj.pack(pady=10)

        self.button_wczytaj = tk.Button(self.master, text="Wczytaj zadania z pliku", command=self.wczytaj_zadania_z_pliku)
        self.button_wczytaj.pack(pady=10)

        self.button_generuj = tk.Button(self.master, text="Generuj Harmonogram Gantta", command=self.rysuj_harmonogram_gantta)
        self.button_generuj.pack(pady=10)

        self.button_cpm = tk.Button(self.master, text="Oblicz CPM", command=self.rysuj_cpm)
        self.button_cpm.pack(pady=10)

    def wczytaj_zadania_z_pliku(self):
        zadania = wczytaj_dane_z_pliku()
        if zadania:
            self.zadania = zadania
            self.odswiez_treeview()

    def odswiez_treeview(self):
        self.treeview.delete(*self.treeview.get_children())
        for zadanie in self.zadania.values():
            self.treeview.insert("", "end", values=(zadanie.nazwa, zadanie.czas_trwania, ", ".join(zadanie.poprzednicy)))

    def dodaj_nowe_zadanie(self):
        nazwa = simpledialog.askstring("Dodaj nowe zadanie", "Podaj nazwę zadania:")
        czas_trwania = simpledialog.askinteger("Dodaj nowe zadanie", f"Podaj czas trwania zadania {nazwa}:")
        poprzednicy_str = simpledialog.askstring("Dodaj nowe zadanie", f"Podaj poprzedników zadania {nazwa} (oddziel spacją):")
        poprzednicy = [] if not poprzednicy_str else poprzednicy_str.split()
        zadanie = Zadanie(nazwa, czas_trwania, poprzednicy)
        self.zadania[nazwa] = zadanie
        self.odswiez_treeview()

    def rysuj_harmonogram_gantta(self):
        for zadanie in self.zadania.values():
            oblicz_wczesny_start(zadanie, self.zadania)
            oblicz_pozne_zakonczenie(zadanie, self.zadania, max([oblicz_wczesny_start(z, self.zadania) for z in self.zadania.values()]))

        gantt_chart = generuj_harmonogram_gantta(self.zadania)
        rysuj_harmonogram_gantta(gantt_chart)

    def rysuj_cpm(self):
        oblicz_cpm(self.zadania)
        rysuj_cpm(self.zadania)

def main():
    root = tk.Tk()
    app = GanttChartApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

