import tkinter as tk
from tkinter import ttk
import requests
import json
from datetime import datetime
import threading

class ConversorMonedas:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Conversor de Monedas Ultra")
        self.root.geometry("600x700")
        self.root.configure(bg='#121212')
        
        self.api_key = "su api key "
        self.base_url = "https://v6.exchangerate-api.com/v6/"
        
        self.monedas = ["USD", "EUR", "GBP", "JPY", "CHF", "MXN", "CAD", "ARS", "BRL", "CNY", "AUD", "NZD", "SGD", "HKD", "KRW"]
        self.tasas = {}
        
        self.setup_ui()
        self.actualizar_tasas()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background='#121212')
        style.configure("TLabel", background='#121212', foreground='#FFFFFF', font=('Arial', 12))
        style.configure("TButton", padding=10, background='#0D47A1', foreground='#FFFFFF', font=('Arial', 12, 'bold'))
        style.configure("Treeview", background='#1E1E1E', foreground='#FFFFFF', fieldbackground='#1E1E1E', font=('Arial', 10))
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))
        style.map("Treeview", background=[('selected', '#0D47A1')])

        frame = ttk.Frame(self.root)
        frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="De:", font=('Arial', 14, 'bold')).grid(row=0, column=0, pady=10, sticky='w')
        self.combo_de = ttk.Combobox(frame, values=self.monedas, state='readonly', width=25, font=('Arial', 12))
        self.combo_de.set("USD")
        self.combo_de.grid(row=0, column=1, pady=10, padx=10)

        ttk.Label(frame, text="A:", font=('Arial', 14, 'bold')).grid(row=1, column=0, pady=10, sticky='w')
        self.combo_a = ttk.Combobox(frame, values=self.monedas, state='readonly', width=25, font=('Arial', 12))
        self.combo_a.set("EUR")
        self.combo_a.grid(row=1, column=1, pady=10, padx=10)

        ttk.Label(frame, text="Cantidad:", font=('Arial', 14, 'bold')).grid(row=2, column=0, pady=10, sticky='w')
        self.entrada_cantidad = ttk.Entry(frame, width=25, font=('Arial', 12))
        self.entrada_cantidad.insert(0, "1")
        self.entrada_cantidad.grid(row=2, column=1, pady=10, padx=10)

        self.boton_convertir = ttk.Button(frame, text="Convertir", command=self.convertir)
        self.boton_convertir.grid(row=3, column=0, columnspan=2, pady=20)

        self.etiqueta_resultado = ttk.Label(frame, text="", font=('Arial', 16, 'bold'))
        self.etiqueta_resultado.grid(row=4, column=0, columnspan=2, pady=10)

        self.tabla = ttk.Treeview(frame, columns=("Moneda", "Tasa", "Inversa"), show="headings", height=15)
        self.tabla.heading("Moneda", text="Moneda")
        self.tabla.heading("Tasa", text="Tasa vs USD")
        self.tabla.heading("Inversa", text="USD vs Moneda")
        self.tabla.column("Moneda", width=100, anchor="center")
        self.tabla.column("Tasa", width=150, anchor="center")
        self.tabla.column("Inversa", width=150, anchor="center")
        self.tabla.grid(row=5, column=0, columnspan=2, pady=10, sticky='nsew')

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tabla.yview)
        scrollbar.grid(row=5, column=2, sticky='ns')
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.etiqueta_actualizacion = ttk.Label(frame, text="", font=('Arial', 10))
        self.etiqueta_actualizacion.grid(row=6, column=0, columnspan=2, pady=5)

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(5, weight=1)

    def obtener_tasas(self):
        try:
            response = requests.get(f"{self.base_url}{self.api_key}/latest/USD")
            data = json.loads(response.text)
            if data["result"] == "success":
                self.tasas = {moneda: data["conversion_rates"][moneda] for moneda in self.monedas}
                return True
            else:
                print("Error al obtener tasas de cambio")
                return False
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False

    def actualizar_tasas(self):
        if self.obtener_tasas():
            self.actualizar_tabla()
            self.etiqueta_actualizacion.config(text=f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            self.etiqueta_actualizacion.config(text="Error al actualizar tasas. Reintentando...")
        
        self.root.after(60000, self.actualizar_tasas)

    def convertir(self):
        try:
            de = self.combo_de.get()
            a = self.combo_a.get()
            cantidad = float(self.entrada_cantidad.get())
            
            if de == a:
                resultado = cantidad
            else:
                tasa_de = self.tasas[de]
                tasa_a = self.tasas[a]
                resultado = (cantidad / tasa_de) * tasa_a
            
            formato_resultado = f"{cantidad:.2f} {de} = {resultado:.2f} {a}"
            self.etiqueta_resultado.config(text=formato_resultado)
            
            # Mostrar tasa de cambio
            tasa_cambio = resultado / cantidad
            tasa_inversa = cantidad / resultado
            self.etiqueta_resultado.config(text=f"{formato_resultado}\n1 {de} = {tasa_cambio:.4f} {a}\n1 {a} = {tasa_inversa:.4f} {de}")
            
        except ValueError:
            self.etiqueta_resultado.config(text="Error: Ingrese un número válido")
        except KeyError:
            self.etiqueta_resultado.config(text="Error: Moneda no disponible")

    def actualizar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for moneda, tasa in self.tasas.items():
            inversa = 1 / tasa
            self.tabla.insert("", "end", values=(moneda, f"{tasa:.4f}", f"{inversa:.4f}"))

    def iniciar(self):
        self.actualizar_tasas()
        self.root.mainloop()

if __name__ == "__main__":
    app = ConversorMonedas()
    app.iniciar()
