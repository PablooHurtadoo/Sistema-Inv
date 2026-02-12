import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# --- CATÁLOGOS DE PRODUCTOS ---
CATALOGO = {
    "CERVEZA": [
        "Escudo (Lata 473cc)", "Cristal (Botella 330cc)", "Becker (Lata 473cc)",
        "Kunstmann Torobayo", "Kross 5", "Austral Calafate", 
        "Corona (Porrón)", "Stella Artois", "Heineken"
    ],
    "CIGARRILLOS": [
        "Pall Mall (20)", "Lucky Strike Red (20)", "Lucky Strike Click",
        "Kent Series (20)", "Belmont (20)", "Rothmans (20)",
        "Marlboro Red (20)"
    ]
}

# Precios de referencia (Lider Chile)
PRECIOS_MERCADO = {
    "CERVEZA": 1150,    # Promedio por unidad
    "CIGARRILLOS": 4700 # Promedio por cajetilla
}

# --- ESTRUCTURA DE DATOS ---
class Producto:
    def __init__(self, id_p, nombre, categoria, cantidad, precio, fecha):
        self.id = id_p
        self.nombre = nombre
        self.categoria = categoria
        self.cantidad = cantidad
        self.precio = precio
        self.fecha = fecha
        self.izquierdo = None
        self.derecho = None

class InventarioArbol:
    def __init__(self):
        self.raiz = None

    def insertar(self, id_p, nom, cat, cant, prec, fecha):
        if not self.raiz:
            self.raiz = Producto(id_p, nom, cat, cant, prec, fecha)
        else:
            self._ins(self.raiz, id_p, nom, cat, cant, prec, fecha)

    def _ins(self, n, id_p, nom, cat, cant, prec, fecha):
        if id_p < n.id:
            if not n.izquierdo: n.izquierdo = Producto(id_p, nom, cat, cant, prec, fecha)
            else: self._ins(n.izquierdo, id_p, nom, cat, cant, prec, fecha)
        elif id_p > n.id:
            if not n.derecho: n.derecho = Producto(id_p, nom, cat, cant, prec, fecha)
            else: self._ins(n.derecho, id_p, nom, cat, cant, prec, fecha)
        else:
            n.cantidad += cant # Si es el mismo producto el mismo día, suma stock

    def obtener_lista(self, n, lista):
        if n:
            self.obtener_lista(n.izquierdo, lista)
            ref = PRECIOS_MERCADO.get(n.categoria, 0)
            dif = n.precio - ref
            lista.append([n.fecha, n.categoria, n.nombre, n.cantidad, n.precio, dif])
            self.obtener_lista(n.derecho, lista)

# --- INTERFAZ GRÁFICA CORREGIDA ---
class AppInventario:
    def __init__(self, root):
        self.root = root
        self.arbol = InventarioArbol()
        self.root.title("Inventario Chile - Cervezas y Cigarros")
        self.root.geometry("1000x600")
        
        # Estilo de la tabla
        style = ttk.Style()
        style.theme_use("clam")

        # Sidebar (Color personalizado DE64b9)
        self.side = tk.Frame(root, bg="#DE64b9", width=300)
        self.side.pack(side="left", fill="y")

        # Main Area
        self.main = tk.Frame(root, bg="white")
        self.main.pack(side="right", fill="both", expand=True)

        tk.Label(self.side, text="GESTIÓN LOCAL", bg="#DE64b9", fg="white", font=("Arial", 14, "bold")).pack(pady=20)

        # Combo Categoría
        tk.Label(self.side, text="Categoría:", bg="#DE64b9", fg="white").pack(anchor="w", padx=30)
        self.cb_cat = ttk.Combobox(self.side, values=list(CATALOGO.keys()), state="readonly")
        self.cb_cat.pack(fill="x", padx=30, pady=5)
        self.cb_cat.set("CERVEZA")
        self.cb_cat.bind("<<ComboboxSelected>>", self.actualizar_opciones)

        # Combo Producto
        tk.Label(self.side, text="Seleccionar Marca:", bg="#DE64b9", fg="white").pack(anchor="w", padx=30)
        self.cb_prod = ttk.Combobox(self.side, state="readonly")
        self.cb_prod.pack(fill="x", padx=30, pady=5)

        # Entradas numéricas
        tk.Label(self.side, text="Cantidad:", bg="#DE64b9", fg="white").pack(anchor="w", padx=30)
        self.ent_cant = tk.Entry(self.side)
        self.ent_cant.pack(fill="x", padx=30, pady=5)

        tk.Label(self.side, text="Precio Costo (CLP):", bg="#DE64b9", fg="white").pack(anchor="w", padx=30)
        self.ent_pre = tk.Entry(self.side)
        self.ent_pre.pack(fill="x", padx=30, pady=5)

        # Botón Guardar
        tk.Button(self.side, text="GUARDAR EN ÁRBOL", command=self.add, bg="#27ae60", fg="white", font=("Arial", 10, "bold")).pack(pady=20, fill="x", padx=30)

        # Tabla Treeview
        cols = ("Fecha", "Tipo", "Producto", "Stock", "Precio", "Dif. Lider")
        self.tree = ttk.Treeview(self.main, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100)
        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

        # Carga inicial de productos
        self.actualizar_opciones()

    def actualizar_opciones(self, event=None):
        cat = self.cb_cat.get()
        opciones = CATALOGO[cat]
        self.cb_prod['values'] = opciones
        self.cb_prod.set(opciones[0])

    def add(self):
        try:
            cat = self.cb_cat.get()
            nom = self.cb_prod.get()
            can = int(self.ent_cant.get())
            pre = float(self.ent_pre.get())
            fecha = datetime.now().strftime("%Y-%m-%d")
            
            # Generamos un ID único basado en fecha y nombre para el Árbol
            id_p = f"{datetime.now().strftime('%Y%m%d')}-{nom[:5]}"
            
            self.arbol.insertar(id_p, nom, cat, can, pre, fecha)
            self.render()
            
            # Limpiar entradas
            self.ent_cant.delete(0, tk.END)
            self.ent_pre.delete(0, tk.END)
            messagebox.showinfo("Éxito", f"Registrado: {nom}")
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa números válidos en Cantidad y Precio.")

    def render(self):
        # Limpiar tabla
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Obtener datos del árbol (Inorden)
        lista = []
        self.arbol.obtener_lista(self.arbol.raiz, lista)
        
        # Insertar en tabla con colores
        for f in lista:
            tag = "caro" if f[5] > 0 else "barato"
            self.tree.insert("", "end", values=f, tags=(tag,))
        
        self.tree.tag_configure("caro", foreground="red")
        self.tree.tag_configure("barato", foreground="green")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppInventario(root)
    root.mainloop()