import flet as ft
import csv
import os
import pandas as pd

# Ruta al archivo CSV para usuarios y productos
user_csv = "db/db.csv"
product_csv = "db/products.csv"

# Asegúrate de que el archivo CSV de usuarios existe
if not os.path.exists(user_csv):
    with open(user_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["admin", "admin"])  # Usuario por defecto

# Asegúrate de que el archivo CSV de productos existe
if not os.path.exists(product_csv):
    with open(product_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Producto", "Precio", "Cantidad"])

# Función para validar el inicio de sesión
def validate_login(username, password):
    with open(user_csv, newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username and row[1] == password:
                return True
    return False

# Función principal para la interfaz de punto de ventas
def main(page: ft.Page):
    page.title = "Sistema de Punto de Ventas"
    page.window_width = 800
    page.window_height = 600

    def load_products():
        if os.path.exists(product_csv) and os.path.getsize(product_csv) > 0:
            return pd.read_csv(product_csv)
        else:
            return pd.DataFrame(columns=["Producto", "Precio", "Cantidad"])

    # Interfaz de inicio de sesión
    def login_view():
        page.views.clear()
        page.views.append(
            ft.View(
                "/login",
                [
                    ft.Text("Iniciar Sesión", style="headlineMedium"),
                    ft.TextField(label="Usuario", width=300),
                    ft.TextField(label="Contraseña", width=300, password=True),
                    ft.ElevatedButton("Entrar", on_click=handle_login)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
            )
        )
        page.update()

    def handle_login(e):
        username = page.views[-1].controls[1].value
        password = page.views[-1].controls[2].value
        if validate_login(username, password):
            pos_view()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Usuario o Contraseña Incorrectos"), open=True)
            page.update()

    # Interfaz del sistema de punto de ventas
    def pos_view():
        page.views.clear()

        def add_product(e):
            product = product_input.value
            price = float(price_input.value)
            quantity = int(quantity_input.value)

            products_df = load_products()
            new_product = pd.DataFrame([[product, price, quantity]], columns=["Producto", "Precio", "Cantidad"])
            products_df = pd.concat([products_df, new_product], ignore_index=True)
            products_df.to_csv(product_csv, index=False)
            load_products_to_ui()

        def delete_product(e):
            selected_items = [row for row in product_list.rows if row.selected]
            if not selected_items:
                return
            products_df = load_products()
            products_df = products_df[~products_df["Producto"].isin([item.cells[0].content.value for item in selected_items])]
            products_df.to_csv(product_csv, index=False)
            load_products_to_ui()

        def load_products_to_ui():
            products_df = load_products()
            product_list.rows.clear()
            for _, row in products_df.iterrows():
                product_list.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(row["Producto"])),
                            ft.DataCell(ft.Text(f"{row['Precio']}")),
                            ft.DataCell(ft.Text(f"{row['Cantidad']}"))
                        ]
                    )
                )
            page.update()

        product_input = ft.TextField(label="Producto", width=200)
        price_input = ft.TextField(label="Precio", width=100)
        quantity_input = ft.TextField(label="Cantidad", width=100)
        product_list = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Cantidad")),
            ],
            rows=[]
        )
        add_product_button = ft.ElevatedButton("Añadir Producto", on_click=add_product)
        delete_product_button = ft.ElevatedButton("Eliminar Producto", on_click=delete_product)

        page.views.append(
            ft.View(
                "/pos",
                [
                    ft.Text("Sistema de Punto de Ventas", style="headlineMedium"),
                    ft.Row([product_input, price_input, quantity_input]),
                    ft.Row([add_product_button, delete_product_button]),
                    product_list
                ],
                horizontal_alignment=ft.CrossAxisAlignment.START,
                vertical_alignment=ft.MainAxisAlignment.START,
                padding=20
            )
        )

        load_products_to_ui()
        page.update()

    # Inicia la aplicación con la vista de inicio de sesión
    login_view()

# Ejecutar la aplicación Flet como una aplicación web
ft.app(target=main, view=ft.WEB_BROWSER)
