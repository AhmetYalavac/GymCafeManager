import tkinter as tk
from tkinter import messagebox, simpledialog
import datetime
import pandas as pd
from PIL import Image, ImageTk



#TODO:Fazla ürünü çıkar
class GymApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spor Salonu Takip Uygulaması")
        self.geometry("800x600")
        self.resizable(False, False)  # Pencere boyutunu sabit yap
        self.background_image = self.load_background()  # Arka planı yükle
        self.create_excel_file()
        self.load_prices_from_file()

        # Günlük ve aylık satış etiketlerini oluştur
        self.daily_sales_label = tk.Label(self, text="Günlük Satış: 0 TL", fg="black", bg="yellow")
        self.daily_sales_label.grid(row=0, column=4, padx=10, pady=5, sticky="w")
        self.monthly_sales_label = tk.Label(self, text="Aylık Satış: 0 TL", fg="black", bg="yellow")
        self.monthly_sales_label.grid(row=1, column=4, padx=10, pady=5, sticky="w")

        self.load_sales_data()
        self.create_widgets()

    def load_background(self):
        # Arka plan resmini yükle ve boyutlandır
        img = Image.open("background.png")
        img = img.resize((800, 600))
        background_image = ImageTk.PhotoImage(img)
        background_label = tk.Label(self, image=background_image)
        background_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        return background_image

    def create_excel_file(self):
        # Eğer dosya yoksa, sütun başlıklarıyla birlikte yeni bir Excel dosyası oluştur
        try:
            pd.read_excel("sales_log.xlsx")
        except FileNotFoundError:
            df = pd.DataFrame(columns=["Tarih", "Ürün", "Fiyat", "Günlük Satış", "Aylık Satış"])
            df.to_excel("sales_log.xlsx", index=False)

    def load_sales_data(self):
        df = pd.read_excel("sales_log.xlsx")
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        this_month = datetime.datetime.now().strftime("%Y-%m")
        daily_sales = df[df["Tarih"].str.startswith(today)]
        monthly_sales = df[df["Tarih"].str.startswith(this_month)]
        self.daily_total = daily_sales["Fiyat"].sum()
        self.monthly_total = monthly_sales["Fiyat"].sum()
        self.update_sales_labels()

    def load_prices_from_file(self):
        try:
            product_df = pd.read_excel("products_prices.xlsx")
            self.products = dict(zip(product_df["Ürün"], product_df["Fiyat"]))
        except FileNotFoundError:
            messagebox.showerror("Hata", "Ürün fiyatları dosyası bulunamadı.")
            self.products = {
                "0.5l Su": 2.50,
                "1.5l Su": 3.50,
                "Meyveli Soda": 3.50,
                "Sade Soda": 3.00,
                "Kahve": 4.00,
                "Filtre Kahve": 5.00,
                "Protein Tozu": 50.00
            }
            self.save_prices_to_file()

        try:
            membership_df = pd.read_excel("memberships_prices.xlsx")
            self.memberships = dict(zip(membership_df["Üyelik"], membership_df["Fiyat"]))
        except FileNotFoundError:
            messagebox.showerror("Hata", "Üyelik fiyatları dosyası bulunamadı.")
            self.memberships = {
                "Bronze Üyelik": 100.00,
                "Silver Üyelik": 150.00,
                "Gold Üyelik": 200.00
            }
            self.save_prices_to_file()

    def update_sales_labels(self):
        # Günlük ve aylık satış etiketlerini güncelle
        self.daily_sales_label.config(text=f"Günlük Satış: {self.daily_total} TL")
        self.monthly_sales_label.config(text=f"Aylık Satış: {self.monthly_total} TL")

    def create_widgets(self):
        self.product_buttons = {}
        self.membership_buttons = {}

        # Günlük ve aylık satışları göstermek için etiketler
        self.daily_sales_label = tk.Label(self, text="Günlük Satış: 0 TL", fg="black", bg="yellow")
        self.daily_sales_label.place(x=20,y=550)
        self.monthly_sales_label = tk.Label(self, text="Aylık Satış: 0 TL", fg="black", bg="yellow")
        self.monthly_sales_label.place(x=20,y=575)

        # Günlük ve aylık satışları güncelle
        self.update_sales_labels()

        # İçecek butonları
        row = 1
        for product, price in self.products.items():
            button = tk.Button(self, text=f"{product} - {price} TL", bg="yellow", fg="black",
                               command=lambda p=product, pr=price: self.record_sale(p, pr))
            button.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
            self.product_buttons[product] = button

            undo_button = tk.Button(self, text=f"Geri Al {product}", bg="black", fg="yellow",
                                    command=lambda p=product: self.undo_sale(p))
            undo_button.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

            row += 1

        # Üyelik butonları
        row = 1
        for membership, price in self.memberships.items():
            button = tk.Button(self, text=f"{membership} - {price} TL", bg="yellow", fg="black",
                               command=lambda m=membership, pr=price: self.record_sale(m, pr))
            button.grid(row=row, column=2, padx=10, pady=5, sticky="ew")
            self.membership_buttons[membership] = button

            undo_button = tk.Button(self, text=f"Geri Al {membership}", bg="black", fg="yellow",
                                    command=lambda m=membership: self.undo_sale(m))
            undo_button.grid(row=row, column=3, padx=10, pady=5, sticky="ew")

            row += 1

        # Yeni ürün ekleme butonu
        add_product_button = tk.Button(self, text="Yeni Ürün Ekle", bg="yellow", fg="black",
                                       command=self.add_product)
        add_product_button.grid(row=0, column=4, padx=10, pady=10, sticky="ew")

        # Rastgele ürün satışı için buton
        random_sale_button = tk.Button(self, text="Rastgele Ürün Satışı", bg="yellow", fg="black",
                                       command=self.random_sale)
        random_sale_button.grid(row=1, column=4, padx=10, pady=5, sticky="ew")

        # Fiyatları değiştirme butonu
        self.change_prices_button = tk.Button(self, text="Fiyatları Değiştir", bg="yellow", fg="black",
                                              command=self.change_prices)
        self.change_prices_button.place(x=20,y=520)

    def undo_sale(self, item):
        now = datetime.datetime.now()
        df = pd.read_excel("sales_log.xlsx")
        # Son eklenen satırı sil
        last_index = df[df['Ürün'] == item].index.max()
        if pd.notna(last_index):
            df = df.drop(last_index)
            df.to_excel("sales_log.xlsx", index=False)

            self.load_sales_data()
        else:
            messagebox.showinfo("Bilgi", f"{item} için geri alınacak satış bulunamadı.")

    def add_product(self):
        # Yeni ürün eklemek için bir pencere aç
        product_name = simpledialog.askstring("Ürün Ekle", "Ürün Adı:")
        if product_name:
            product_price = simpledialog.askfloat("Ürün Ekle", "Ürün Fiyatı:")
            if product_price:
                self.products[product_name] = product_price
                self.save_prices_to_file()
                self.create_widgets()  # Yeni ürünü ekleyerek widget'ları yeniden oluştur

    def random_sale(self):
        # Rastgele ürün satışı için bir pencere aç
        product_name = simpledialog.askstring("Rastgele Ürün Satışı", "Ürün Adı:")
        if product_name:
            product_price = simpledialog.askfloat("Rastgele Ürün Satışı", "Ürün Fiyatı:")
            if product_price:
                self.record_sale(product_name, product_price)

    def change_prices(self):
        # Fiyatları değiştirme işlemi için yeni bir pencere aç
        price_change_window = tk.Toplevel(self)
        price_change_window.title("Fiyatları Değiştir")
        price_change_window.geometry("600x400")  # Pencere boyutunu değiştir
        price_change_window.resizable(False, False)


        # İçecek butonları
        frame1 = tk.Frame(price_change_window)
        frame1.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        product_entries = []
        for i, (product, price) in enumerate(self.products.items()):
            label = tk.Label(frame1, text=product, fg="black", bg="yellow")
            label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(frame1)
            entry.insert(0, str(price))
            entry.grid(row=i, column=1, padx=5, pady=5)
            product_entries.append(entry)

        # Üyelik butonları
        frame2 = tk.Frame(price_change_window)
        frame2.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        membership_entries = []
        for i, (membership, price) in enumerate(self.memberships.items()):
            label = tk.Label(frame2, text=membership, fg="black", bg="yellow")
            label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(frame2)
            entry.insert(0, str(price))
            entry.grid(row=i, column=1, padx=5, pady=5)
            membership_entries.append(entry)

        # Kaydet butonu
        save_button = tk.Button(price_change_window, text="Kaydet", bg="yellow", fg="black",
                                command=lambda: self.save_prices(price_change_window, product_entries,
                                                                 membership_entries))
        save_button.grid(row=1, column=0, columnspan=2, pady=10)



    def save_prices(self, window, product_entries, membership_entries):
        # Fiyatları kaydetme işlemi
        for entry, (product, button) in zip(product_entries, self.product_buttons.items()):
            new_price = float(entry.get())
            self.products[product] = new_price
            button.config(text=f"{product} - {new_price} TL")

        for entry, (membership, button) in zip(membership_entries, self.membership_buttons.items()):
            new_price = float(entry.get())
            self.memberships[membership] = new_price
            button.config(text=f"{membership} - {new_price} TL")

        # Fiyatları dosyaya kaydet
        self.save_prices_to_file()
        window.destroy()

    def save_prices_to_file(self):
        # Fiyatları dosyaya kaydetme işlemi
        df = pd.DataFrame(list(self.products.items()), columns=["Ürün", "Fiyat"])
        df.to_excel("products_prices.xlsx", index=False)

        df = pd.DataFrame(list(self.memberships.items()), columns=["Üyelik", "Fiyat"])
        df.to_excel("memberships_prices.xlsx", index=False)

    def record_sale(self, item, price):
        now = datetime.datetime.now()
        df = pd.read_excel("sales_log.xlsx")
        new_row = {"Tarih": now.strftime('%Y-%m-%d %H:%M:%S'), "Ürün": item, "Fiyat": price}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel("sales_log.xlsx", index=False)

        self.load_sales_data()


if __name__ == "__main__":
    app = GymApp()
    app.mainloop()
