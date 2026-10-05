import customtkinter as ctk
import requests
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os
import base64
import io

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

API_URL = "http://localhost:5000/api"

class PinDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Authorize Transaction"):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x240")
        self.resizable(False, False)
        ctk.set_appearance_mode("Dark")
        
        self.pin = None
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (400 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (240 // 2)
        self.geometry(f"+{x}+{y}")

        ctk.CTkLabel(self, text="🔒 Security Verification", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Please enter your 4-digit PIN to proceed:", font=ctk.CTkFont(size=13), text_color="gray").pack(pady=(0, 15))

        self.pin_entry = ctk.CTkEntry(self, placeholder_text="••••", show="*", width=300, height=45, justify="center", font=ctk.CTkFont(size=18, weight="bold"))
        self.pin_entry.pack(pady=10)
        self.pin_entry.focus()
        self.pin_entry.bind("<Return>", lambda e: self.confirm())

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Cancel", fg_color="#64748b", hover_color="#475569", width=130, height=40, font=ctk.CTkFont(size=13, weight="bold"), command=self.destroy).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Authorize", fg_color="#10b981", hover_color="#059669", width=130, height=40, font=ctk.CTkFont(size=13, weight="bold"), command=self.confirm).pack(side="left", padx=10)

        parent.wait_window(self)

    def confirm(self):
        val = self.pin_entry.get().strip()
        if not val:
            messagebox.showerror("Error", "PIN cannot be empty.")
            return
        self.pin = val
        self.destroy()

class CustomerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PayDesktop Bank - Customer Portal")
        self.geometry("1300x800")
        self.current_user = None
        self.profile_pic_path = None
        self.show_auth_screen()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_auth_screen(self):
        self.clear_window()
        self.configure(fg_color="#020617")

        auth_frame = ctk.CTkFrame(self, width=480, height=560, fg_color="#0f172a", corner_radius=16, border_width=1, border_color="#1e293b")
        auth_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(auth_frame, text="PayDesktop Bank", font=ctk.CTkFont(size=26, weight="bold"), text_color="#60a5fa").pack(pady=(30, 5))
        ctk.CTkLabel(auth_frame, text="Secure Digital Banking Portal", font=ctk.CTkFont(size=13), text_color="#94a3b8").pack(pady=(0, 15))

        self.auth_tabview = ctk.CTkTabview(auth_frame, width=420, height=390, fg_color="#1e293b", segmented_button_fg_color="#0f172a")
        self.auth_tabview.pack(padx=30, pady=10)

        tab_login = self.auth_tabview.add("Customer Login")
        tab_reg = self.auth_tabview.add("Open Account")

        # Login Tab
        ctk.CTkLabel(tab_login, text="Phone Number", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", pady=(10, 2))
        self.login_phone = ctk.CTkEntry(tab_login, placeholder_text="08012345678", width=360, height=40, fg_color="#0f172a", border_color="#334155")
        self.login_phone.pack(pady=4)

        ctk.CTkLabel(tab_login, text="4-Digit Security PIN", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", pady=(10, 2))
        self.login_pin = ctk.CTkEntry(tab_login, placeholder_text="••••", show="*", width=360, height=40, fg_color="#0f172a", border_color="#334155")
        self.login_pin.pack(pady=4)

        ctk.CTkButton(tab_login, text="Secure Login", command=self.handle_login, width=360, height=44, fg_color="#2563eb", hover_color="#1d4ed8", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=25)

        # Register Tab
        ctk.CTkLabel(tab_reg, text="Full Name", font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w", pady=(2, 1))
        self.reg_name = ctk.CTkEntry(tab_reg, placeholder_text="John Doe", width=360, height=34, fg_color="#0f172a", border_color="#334155")
        self.reg_name.pack(pady=2)

        ctk.CTkLabel(tab_reg, text="Phone Number", font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w", pady=(2, 1))
        self.reg_phone = ctk.CTkEntry(tab_reg, placeholder_text="08012345678", width=360, height=34, fg_color="#0f172a", border_color="#334155")
        self.reg_phone.pack(pady=2)

        ctk.CTkLabel(tab_reg, text="Email Address", font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w", pady=(2, 1))
        self.reg_email = ctk.CTkEntry(tab_reg, placeholder_text="customer@paydesktop.com", width=360, height=34, fg_color="#0f172a", border_color="#334155")
        self.reg_email.pack(pady=2)

        ctk.CTkLabel(tab_reg, text="Create 4-Digit PIN", font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w", pady=(2, 1))
        self.reg_pin = ctk.CTkEntry(tab_reg, placeholder_text="••••", show="*", width=360, height=34, fg_color="#0f172a", border_color="#334155")
        self.reg_pin.pack(pady=2)

        ctk.CTkButton(tab_reg, text="Register Account", command=self.handle_register, width=360, height=40, fg_color="#059669", hover_color="#047857", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15)

    def handle_login(self):
        phone, pin = self.login_phone.get().strip(), self.login_pin.get().strip()
        if not phone or not pin: return messagebox.showerror("Error", "Enter phone and PIN.")
        try:
            res = requests.post(f"{API_URL}/user/login", json={"phone": phone, "pin": pin})
            data = res.json()
            if res.status_code == 200:
                self.current_user = data
                self.show_dashboard()
            else:
                messagebox.showerror("Error", data.get("message", "Login failed."))
        except Exception as e: messagebox.showerror("Connection Error", str(e))

    def handle_register(self):
        name, phone, email, pin = self.reg_name.get().strip(), self.reg_phone.get().strip(), self.reg_email.get().strip(), self.reg_pin.get().strip()
        if not name or not phone or not pin: return messagebox.showerror("Error", "Fill required fields.")
        try:
            res = requests.post(f"{API_URL}/user/register", json={"name": name, "phone": phone, "email": email, "pin": pin})
            data = res.json()
            if res.status_code in [200, 201]:
                messagebox.showinfo("Success", f"Account created! Pending Admin approval. Acc No: {data.get('accountNo', 'N/A')}")
                self.auth_tabview.set("Customer Login")
            else: messagebox.showerror("Error", data.get("message"))
        except Exception as e: messagebox.showerror("Error", str(e))

    def show_dashboard(self):
        self.clear_window()
        self.configure(fg_color="#020617")

        # Header
        header = ctk.CTkFrame(self, height=75, fg_color="#0f172a", corner_radius=0, border_width=1, border_color="#1e293b")
        header.pack(fill="x")
        header.pack_propagate(False)

        logo_lbl = ctk.CTkLabel(header, text="PayDesktop Bank", font=ctk.CTkFont(size=20, weight="bold"), text_color="#60a5fa")
        logo_lbl.pack(side="left", padx=30)

        user_info_frame = ctk.CTkFrame(header, fg_color="transparent")
        user_info_frame.pack(side="right", padx=30)

        # Header Profile Picture / Avatar Display
        self.header_pic_lbl = ctk.CTkLabel(user_info_frame, text="", width=45, height=45, fg_color="#334155", corner_radius=22)
        self.header_pic_lbl.pack(side="left", padx=10)
        self.load_header_profile_pic()

        ctk.CTkLabel(user_info_frame, text=self.current_user['name'], font=ctk.CTkFont(size=14, weight="bold"), text_color="#cbd5e1").pack(side="left", padx=10)
        ctk.CTkButton(user_info_frame, text="Logout", command=self.show_auth_screen, fg_color="#dc2626", hover_color="#b91c1c", width=90, height=36, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)

        # Tab navigation bar
        nav_bar = ctk.CTkFrame(self, height=60, fg_color="#0f172a", corner_radius=0)
        nav_bar.pack(fill="x", pady=(1, 0))

        btn_style = {"width": 150, "height": 42, "fg_color": "transparent", "hover_color": "#1e293b", "text_color": "#cbd5e1", "font": ctk.CTkFont(size=13, weight="bold")}
        
        self.nav_buttons = {}
        tabs = [
            ("Overview", self.load_overview_tab),
            ("OPay Services", self.load_opay_tab),
            ("Transfer", self.load_transfer_tab),
            ("History", self.load_history_tab),
            ("Settings", self.load_settings_tab),
            ("Support Chat", self.load_chat_tab)
        ]

        for name, cmd in tabs:
            btn = ctk.CTkButton(nav_bar, text=name, command=lambda c=cmd, n=name: [self.set_active_tab(n), c()], **btn_style)
            btn.pack(side="left", padx=8, pady=9)
            self.nav_buttons[name] = btn

        self.tab_content_frame = ctk.CTkScrollableFrame(self, fg_color="#020617")
        self.tab_content_frame.pack(fill="both", expand=True, padx=30, pady=25)

        self.load_overview_tab()
        self.set_active_tab("Overview")

    def load_header_profile_pic(self):
        pic_data = self.current_user.get('profilePic', '')
        if pic_data:
            try:
                img_data = base64.b64decode(pic_data)
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((45, 45), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.header_pic_lbl.configure(image=photo, text="")
                self.header_pic_lbl.image = photo
            except Exception:
                self.header_pic_lbl.configure(text=self.current_user['name'][0].upper())
        else:
            self.header_pic_lbl.configure(text=self.current_user['name'][0].upper(), font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff")

    def set_active_tab(self, active_name):
        for name, btn in self.nav_buttons.items():
            if name == active_name:
                btn.configure(fg_color="#2563eb", text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color="#cbd5e1")

    def clear_tab(self):
        for w in self.tab_content_frame.winfo_children(): w.destroy()

    def load_overview_tab(self):
        self.clear_tab()
        
        try:
            ann_res = requests.get(f"{API_URL}/announcements/latest")
            ann_data = ann_res.json()
            ann_text = "   ***   ".join([a.get('text', '') for a in ann_data]) if isinstance(ann_data, list) else ann_data.get('text', 'Welcome to PayDesktop Bank')
        except Exception:
            ann_text = "Welcome to PayDesktop Bank - Secure Digital Banking Portal"

        notice_card = ctk.CTkFrame(self.tab_content_frame, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=12, height=55)
        notice_card.pack(fill="x", pady=(0, 20))
        notice_card.pack_propagate(False)
        ctk.CTkLabel(notice_card, text=f"📢 NOTICE: {ann_text}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#38bdf8").pack(anchor="w", padx=20, pady=16)

        card = ctk.CTkFrame(self.tab_content_frame, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=20, height=260)
        card.pack(fill="x", pady=5)
        card.pack_propagate(False)

        tier = self.current_user.get('kycTier', 'Tier 1')
        max_b = "₦500,000" if tier == 'Tier 2' else ("Unlimited" if tier == 'Tier 3' else "₦300,000")
        daily_l = "₦490,000" if tier == 'Tier 2' else ("₦5,000,000" if tier == 'Tier 3' else "₦290,000")

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=30, pady=(25, 5))

        ctk.CTkLabel(top_row, text="AVAILABLE BALANCE", font=ctk.CTkFont(size=13, weight="bold"), text_color="#94a3b8").pack(side="left")
        ctk.CTkLabel(top_row, text=tier, font=ctk.CTkFont(size=13, weight="bold"), text_color="#fbbf24", fg_color="#78350f", corner_radius=8, width=80, height=30).pack(side="right")

        ctk.CTkLabel(card, text=f"₦{self.current_user.get('balance', 0):,.2f}", font=ctk.CTkFont(size=44, weight="bold"), text_color="#ffffff").pack(anchor="w", padx=30, pady=10)
        
        details_row = ctk.CTkFrame(card, fg_color="transparent")
        details_row.pack(fill="x", padx=30, pady=(20, 0))

        ctk.CTkLabel(details_row, text=f"Account No: {self.current_user.get('accountNo', 'N/A')}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#38bdf8").pack(side="left", padx=(0, 25))
        ctk.CTkLabel(details_row, text=f"Max Balance Limit: {max_b}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#34d399").pack(side="left", padx=(0, 25))
        ctk.CTkLabel(details_row, text=f"Daily Limit: {daily_l}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#60a5fa").pack(side="left")

        refresh_btn = ctk.CTkButton(self.tab_content_frame, text="🔄 Refresh Balance", command=self.refresh_user_data, fg_color="#1e293b", hover_color="#334155", width=200, height=44, font=ctk.CTkFont(size=14, weight="bold"))
        refresh_btn.pack(anchor="w", pady=20)

    def refresh_user_data(self):
        try:
            res = requests.post(f"{API_URL}/user/login", json={"phone": self.current_user['phone'], "pin": self.current_user['pin']})
            if res.status_code == 200:
                self.current_user = res.json()
                self.load_overview_tab()
                messagebox.showinfo("Success", "Balance updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_opay_tab(self):
        self.clear_tab()
        ctk.CTkLabel(self.tab_content_frame, text="OPay Services & Quick Actions", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 20))

        grid_frame = ctk.CTkFrame(self.tab_content_frame, fg_color="transparent")
        grid_frame.pack(fill="x", pady=15)

        services = [
            ("🔄 Transfers", "Send to Bank Accounts", lambda: [self.set_active_tab("Transfer"), self.load_transfer_tab()]),
            ("📱 Airtime & Data", "Instant Recharge", self.open_airtime_modal),
            ("⚽ Betting", "Fund Bet Accounts", self.open_betting_modal),
            ("💳 ATM Card", "Request & View Card", self.open_card_modal)
        ]

        for title, desc, cmd in services:
            btn_card = ctk.CTkButton(grid_frame, text=f"{title}\n\n{desc}", command=cmd, fg_color="#0f172a", hover_color="#1e293b", border_width=1, border_color="#1e293b", corner_radius=16, width=280, height=140, font=ctk.CTkFont(size=16, weight="bold"))
            btn_card.pack(side="left", padx=12, expand=True, fill="x")

    def open_airtime_modal(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Buy Airtime & Data")
        popup.geometry("420x420")
        popup.configure(fg_color="#0f172a")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text="📱 Instant Airtime", font=ctk.CTkFont(size=18, weight="bold"), text_color="#60a5fa").pack(pady=(25, 15))

        ctk.CTkLabel(popup, text="Network Provider", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=35, pady=2)
        net_menu = ctk.CTkComboBox(popup, values=["MTN", "Airtel", "Glo", "9mobile"], width=350, height=40)
        net_menu.pack(padx=35, pady=5)

        ctk.CTkLabel(popup, text="Phone Number", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=35, pady=2)
        phone_entry = ctk.CTkEntry(popup, placeholder_text="08012345678", width=350, height=40)
        phone_entry.pack(padx=35, pady=5)

        ctk.CTkLabel(popup, text="Amount (₦)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=35, pady=2)
        amt_entry = ctk.CTkEntry(popup, placeholder_text="1000", width=350, height=40)
        amt_entry.pack(padx=35, pady=5)

        def execute():
            net = net_menu.get()
            ph = phone_entry.get().strip()
            amt = amt_entry.get().strip()
            if not ph or not amt:
                return messagebox.showerror("Error", "Fill all fields.", parent=popup)
            
            dialog = PinDialog(self, title="Authorize Airtime")
            if not dialog.pin:
                return
            
            try:
                res = requests.post(f"{API_URL}/user/airtime", json={"phone": self.current_user['phone'], "network": net, "bumberOrPhone": ph, "amount": float(amt), "pin": dialog.pin})
                data = res.json()
                if res.status_code == 200:
                    messagebox.showinfo("Success", data.get("message", "Airtime purchased!"))
                    self.current_user['balance'] = data.get("newBalance", self.current_user['balance'])
                    popup.destroy()
                    self.load_overview_tab()
                else:
                    messagebox.showerror("Error", data.get("message", "Failed."), parent=popup)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Purchase Airtime", command=execute, fg_color="#059669", hover_color="#047857", width=350, height=44, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=25)

    def open_betting_modal(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Fund Betting Account")
        popup.geometry("420x420")
        popup.configure(fg_color="#0f172a")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text="⚽ Betting Funding", font=ctk.CTkFont(size=18, weight="bold"), text_color="#f59e0b").pack(pady=(25, 15))

        ctk.CTkLabel(popup, text="Betting Provider", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=35, pady=2)
        prov_menu = ctk.CTkComboBox(popup, values=["Bet9ja", "SportyBet", "1xBet"], width=350, height=40)
        prov_menu.pack(padx=35, pady=5)

        ctk.CTkLabel(popup, text="Customer / User ID", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=35, pady=2)
        id_entry = ctk.CTkEntry(popup, placeholder_text="Enter ID", width=350, height=40)
        id_entry.pack(padx=35, pady=5)

        ctk.CTkLabel(popup, text="Amount (₦)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=35, pady=2)
        amt_entry = ctk.CTkEntry(popup, placeholder_text="2000", width=350, height=40)
        amt_entry.pack(padx=35, pady=5)

        def execute():
            prov = prov_menu.get()
            cid = id_entry.get().strip()
            amt = amt_entry.get().strip()
            if not cid or not amt:
                return messagebox.showerror("Error", "Fill all fields.", parent=popup)
            
            dialog = PinDialog(self, title="Authorize Betting Funding")
            if not dialog.pin:
                return
            
            try:
                res = requests.post(f"{API_URL}/user/betting", json={"phone": self.current_user['phone'], "provider": prov, "customerId": cid, "amount": float(amt), "pin": dialog.pin})
                data = res.json()
                if res.status_code == 200:
                    messagebox.showinfo("Success", data.get("message", "Betting account funded!"))
                    self.current_user['balance'] = data.get("newBalance", self.current_user['balance'])
                    popup.destroy()
                    self.load_overview_tab()
                else:
                    messagebox.showerror("Error", data.get("message", "Failed."), parent=popup)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Fund Bet Account", command=execute, fg_color="#d97706", hover_color="#b45309", width=350, height=44, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=25)

    def open_card_modal(self):
        popup = ctk.CTkToplevel(self)
        popup.title("PayDesktop ATM Card")
        popup.geometry("420x320")
        popup.configure(fg_color="#0f172a")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text="💳 ATM Card Management", font=ctk.CTkFont(size=18, weight="bold"), text_color="#38bdf8").pack(pady=(25, 20))

        status = self.current_user.get('cardStatus', 'NOT_REQUESTED')
        
        if status == 'ASSIGNED':
            card_info = self.current_user.get('cardDetails', {})
            ctk.CTkLabel(popup, text=f"Card Number:\n{card_info.get('cardNumber', 'N/A')}", font=ctk.CTkFont(size=16, weight="bold"), text_color="#10b981").pack(pady=10)
            ctk.CTkLabel(popup, text=f"Expiry: {card_info.get('expiry', 'N/A')} | CVV: {card_info.get('cvv', 'N/A')}", font=ctk.CTkFont(size=14), text_color="#cbd5e1").pack(pady=10)
        else:
            ctk.CTkLabel(popup, text=f"Card Status: {status}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#f59e0b").pack(pady=15)
            
            def request_card():
                try:
                    res = requests.post(f"{API_URL}/user/request-card", json={"phone": self.current_user['phone']})
                    data = res.json()
                    if res.status_code == 200:
                        messagebox.showinfo("Success", "ATM Card request submitted successfully!")
                        self.current_user['cardStatus'] = 'PENDING'
                        popup.destroy()
                    else:
                        messagebox.showerror("Error", data.get("message", "Failed."))
                except Exception as e:
                    messagebox.showerror("Error", str(e))

            ctk.CTkButton(popup, text="Request Physical / Virtual Card", command=request_card, fg_color="#2563eb", width=320, height=44, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=20)

    def load_transfer_tab(self):
        self.clear_tab()
        
        container = ctk.CTkFrame(self.tab_content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True)

        left_frame = ctk.CTkFrame(container, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=16)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))

        ctk.CTkLabel(left_frame, text="Send Money & Other Banks Transfer", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(anchor="w", padx=30, pady=(25, 20))

        # Destination Bank Selection (15-20 banks list)
        ctk.CTkLabel(left_frame, text="Select Bank", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=30, pady=2)
        self.banks_list = [
            "PayDesktop Bank", "OPay Digital Service", "Moniepoint MFB", "PalmPay", 
            "Access Bank", "Zenith Bank", "Guaranty Trust Bank (GTB)", "First Bank of Nigeria", 
            "United Bank for Africa (UBA)", "Ecobank Nigeria", "Fidelity Bank", "Stanbic IBTC Bank", 
            "Sterling Bank", "Union Bank of Nigeria", "Unity Bank", "Wema Bank", 
            "Keystone Bank", "Providus Bank", "Globus Bank", "FCMB"
        ]
        self.tr_bank = ctk.CTkComboBox(left_frame, values=self.banks_list, width=460, height=42, command=self.on_bank_select)
        self.tr_bank.set("PayDesktop Bank")
        self.tr_bank.pack(anchor="w", padx=30, pady=5)

        ctk.CTkLabel(left_frame, text="Recipient Account Number", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=30, pady=(10, 2))
        self.tr_acc = ctk.CTkEntry(left_frame, placeholder_text="10-digit account no", width=460, height=42, fg_color="#020617")
        self.tr_acc.pack(anchor="w", padx=30, pady=5)
        self.tr_acc.bind("<KeyRelease>", self.verify_recipient)

        # Verification frame with Name and Profile Picture together
        ver_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        ver_frame.pack(anchor="w", padx=30, pady=5)

        self.ver_pic_lbl = ctk.CTkLabel(ver_frame, text="", width=40, height=40, fg_color="#334155", corner_radius=20)
        self.ver_pic_lbl.pack(side="left", padx=(0, 12))

        self.tr_recipient_name = ctk.CTkLabel(ver_frame, text="", font=ctk.CTkFont(size=14, weight="bold"), text_color="#34d399")
        self.tr_recipient_name.pack(side="left")

        ctk.CTkLabel(left_frame, text="Amount (₦)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=30, pady=(10, 2))
        self.tr_amt = ctk.CTkEntry(left_frame, placeholder_text="0.00", width=460, height=42, fg_color="#020617")
        self.tr_amt.pack(anchor="w", padx=30, pady=5)

        ctk.CTkLabel(left_frame, text="Transfer Note (Optional)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=30, pady=(10, 2))
        self.tr_note = ctk.CTkEntry(left_frame, placeholder_text="For payment / services", width=460, height=42, fg_color="#020617")
        self.tr_note.pack(anchor="w", padx=30, pady=5)

        ctk.CTkButton(left_frame, text="Transfer Funds Now", command=self.prompt_transaction_pin, fg_color="#059669", hover_color="#047857", width=460, height=46, font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=30, pady=25)

        right_frame = ctk.CTkFrame(container, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=16, width=360)
        right_frame.pack(side="right", fill="y", padx=(15, 0))
        right_frame.pack_propagate(False)

        ctk.CTkLabel(right_frame, text="Saved Beneficiaries", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff").pack(anchor="w", padx=25, pady=(25, 15))

        self.beneficiaries_scroll = ctk.CTkScrollableFrame(right_frame, fg_color="transparent", height=400)
        self.beneficiaries_scroll.pack(fill="both", expand=True, padx=12, pady=5)
        self.load_beneficiaries()

    def on_bank_select(self, choice):
        self.verify_recipient()

    def verify_recipient(self, event=None):
        acc = self.tr_acc.get().strip()
        bank = self.tr_bank.get()
        if len(acc) == 10 and bank == "PayDesktop Bank":
            try:
                res = requests.get(f"{API_URL}/user/verify/{acc}")
                data = res.json()
                if data.get("found"):
                    name = data.get('fullName')
                    self.tr_recipient_name.configure(text=f"Verified: {name}", text_color="#34d399")
                    pic = data.get('profilePic', '')
                    if pic:
                        try:
                            img_data = base64.b64decode(pic)
                            img = Image.open(io.BytesIO(img_data)).resize((40, 40), Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(img)
                            self.ver_pic_lbl.configure(image=photo, text="")
                            self.ver_pic_lbl.image = photo
                        except Exception:
                            self.ver_pic_lbl.configure(text=name[0].upper(), image="")
                    else:
                        self.ver_pic_lbl.configure(text=name[0].upper(), font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff", image="")
                else:
                    self.tr_recipient_name.configure(text="Account not found", text_color="#ef4444")
                    self.ver_pic_lbl.configure(text="❌", image="")
            except Exception:
                self.tr_recipient_name.configure(text="")
        elif len(acc) == 10:
            self.tr_recipient_name.configure(text=f"External Bank ({bank})", text_color="#38bdf8")
            self.ver_pic_lbl.configure(text="🏦", image="")
        else:
            self.tr_recipient_name.configure(text="")
            self.ver_pic_lbl.configure(text="", image="")

    def prompt_transaction_pin(self):
        acc = self.tr_acc.get().strip()
        amt = self.tr_amt.get().strip()
        if not acc or not amt:
            return messagebox.showerror("Error", "Please fill recipient account and amount.")

        dialog = PinDialog(self, title="Authorize Transfer")
        if not dialog.pin:
            return
        self.execute_transfer(dialog.pin)

    def execute_transfer(self, pin):
        acc = self.tr_acc.get().strip()
        amt = self.tr_amt.get().strip()
        note = self.tr_note.get().strip()
        bank = self.tr_bank.get()

        try:
            res = requests.post(f"{API_URL}/user/transfer", json={
                "senderPhone": self.current_user['phone'],
                "recipientAccount": acc,
                "recipientBank": bank,
                "amount": float(amt),
                "pin": pin,
                "note": note
            })
            data = res.json()
            if res.status_code == 200:
                tx_id = data.get('tx_id', 'TXN' + str(int(requests.compat.time.time())))
                msg = data.get('message', 'Transfer successful!')
                
                # Automatically save as beneficiary
                recipient_name = self.tr_recipient_name.cget("text").replace("Verified: ", "")
                requests.post(f"{API_URL}/user/beneficiaries", json={
                    "phone": self.current_user['phone'],
                    "name": recipient_name if recipient_name else f"Acc: {acc}",
                    "accountNumber": acc,
                    "bankName": bank
                })
                self.load_beneficiaries()

                # Receipt download prompt (Yes/No buttons)
                if messagebox.askyesno("Download Receipt", f"{msg}\n\nDo you want to download the transaction receipt?"):
                    self.save_receipt(tx_id, acc, bank, amt, note)

                self.current_user['balance'] = data.get('newBalance', self.current_user['balance'])
                self.load_overview_tab()
            else:
                messagebox.showerror("Error", data.get("message", "Transfer failed."))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_receipt(self, tx_id, acc, bank, amt, note):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], initialfile=f"Receipt_{tx_id}.txt")
            if not file_path:
                return
            receipt_content = f"""========================================
       PAYDESKTOP BANK - E-RECEIPT
========================================
Transaction ID : {tx_id}
Sender Name    : {self.current_user['name']}
Sender Account : {self.current_user['accountNo']}
Recipient Acc  : {acc}
Recipient Bank : {bank}
Amount         : ₦{float(amt):,.2f}
Note           : {note if note else 'N/A'}
Date           : {requests.compat.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status         : SUCCESSFUL
========================================
       Thank you for banking with us!
========================================
"""
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(receipt_content)
            messagebox.showinfo("Success", "Receipt downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save receipt: {e}")

    def load_beneficiaries(self):
        try:
            res = requests.get(f"{API_URL}/user/beneficiaries/{self.current_user['phone']}")
            list_b = res.json() if res.status_code == 200 else []
            for w in self.beneficiaries_scroll.winfo_children(): w.destroy()
            if not list_b:
                ctk.CTkLabel(self.beneficiaries_scroll, text="No beneficiaries saved.", text_color="gray", font=ctk.CTkFont(size=13)).pack(pady=20)
                return
            for b in list_b:
                b_card = ctk.CTkFrame(self.beneficiaries_scroll, fg_color="#1e293b", corner_radius=10)
                b_card.pack(fill="x", pady=6, padx=5, ipady=8)
                ctk.CTkLabel(b_card, text=b.get('name'), font=ctk.CTkFont(size=13, weight="bold"), text_color="#cbd5e1").pack(anchor="w", padx=12)
                ctk.CTkLabel(b_card, text=f"{b.get('accountNumber')} ({b.get('bankName', 'PayDesktop Bank')})", font=ctk.CTkFont(size=12, family="Courier"), text_color="#38bdf8").pack(anchor="w", padx=12)
        except Exception:
            pass

    def load_history_tab(self):
        self.clear_tab()
        
        top_bar = ctk.CTkFrame(self.tab_content_frame, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=14, height=70)
        top_bar.pack(fill="x", pady=10)
        top_bar.pack_propagate(False)

        ctk.CTkLabel(top_bar, text="Transaction History & Statements", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(side="left", padx=25)
        ctk.CTkButton(top_bar, text="📄 Export Statement (TXT)", command=self.download_statement, fg_color="#2563eb", hover_color="#1d4ed8", width=200, height=40, font=ctk.CTkFont(size=13, weight="bold")).pack(side="right", padx=25)

        self.history_scroll = ctk.CTkScrollableFrame(self.tab_content_frame, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=14, height=500)
        self.history_scroll.pack(fill="both", expand=True, pady=5)

        try:
            res = requests.get(f"{API_URL}/user/transactions/{self.current_user['phone']}")
            txs = res.json() if res.status_code == 200 else []
            self.cached_transactions = txs
            if not txs:
                ctk.CTkLabel(self.history_scroll, text="No transactions found.", text_color="gray", font=ctk.CTkFont(size=15)).pack(pady=60)
                return
            for tx in txs:
                card = ctk.CTkFrame(self.history_scroll, fg_color="#1e293b", corner_radius=10)
                card.pack(fill="x", pady=8, padx=12, ipady=10)
                
                txt = f"Date: {tx.get('date', '')[:10]} | TX ID: {tx.get('tx_id', 'N/A')} | Type: {tx.get('type')} | Bank: {tx.get('recipientBank', 'PayDesktop Bank')} | Amount: ₦{tx.get('amount', 0):,.2f} | Note: {tx.get('note', '')}"
                ctk.CTkLabel(card, text=txt, font=ctk.CTkFont(size=13, weight="bold"), text_color="#cbd5e1").pack(anchor="w", padx=18)
        except Exception as e:
            ctk.CTkLabel(self.history_scroll, text=f"Error loading transactions: {e}", text_color="red").pack(pady=20)

    def download_statement(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], initialfile="Statement.txt")
            if not file_path:
                return
            content = f"STATEMENT FOR {self.current_user['name']} (Account: {self.current_user['accountNo']})\n" + "="*60 + "\n\n"
            for tx in getattr(self, 'cached_transactions', []):
                content += f"Date: {tx.get('date', '')[:10]} | Type: {tx.get('type')} | Bank: {tx.get('recipientBank', 'PayDesktop Bank')} | Amount: ₦{tx.get('amount', 0):,.2f} | Note: {tx.get('note', '')}\n"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Success", "Statement exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_settings_tab(self):
        self.clear_tab()
        
        settings_card = ctk.CTkFrame(self.tab_content_frame, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=18, width=650)
        settings_card.pack(anchor="w", pady=10, fill="x", padx=10, ipady=25)

        ctk.CTkLabel(settings_card, text="Account Settings & Profile Picture", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ffffff").pack(anchor="w", padx=30, pady=(25, 20))

        pic_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        pic_frame.pack(anchor="w", padx=30, pady=10)

        self.pic_label = ctk.CTkLabel(pic_frame, text="📷 No Picture", font=ctk.CTkFont(size=12), width=110, height=110, fg_color="#334155", corner_radius=55)
        self.pic_label.pack(side="left", padx=(0, 25))
        self.load_current_profile_pic_preview()

        btn_pic_frame = ctk.CTkFrame(pic_frame, fg_color="transparent")
        btn_pic_frame.pack(side="left")

        ctk.CTkButton(btn_pic_frame, text="Upload Profile Picture", command=self.upload_profile_picture, width=200, height=40, font=ctk.CTkFont(size=13, weight="bold")).pack(pady=5)
        ctk.CTkLabel(btn_pic_frame, text="Supports JPG, PNG formats. Persists across logins.", font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w")

        tier = self.current_user.get('kycTier', 'Tier 1')
        ctk.CTkLabel(settings_card, text=f"KYC Tier Status: {tier}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#fbbf24").pack(anchor="w", padx=30, pady=10)

        ctk.CTkLabel(settings_card, text="Phone Number", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=30, pady=(10, 2))
        self.set_phone = ctk.CTkEntry(settings_card, width=460, height=42, fg_color="#020617")
        self.set_phone.insert(0, self.current_user['phone'])
        self.set_phone.pack(anchor="w", padx=30, pady=5)

        ctk.CTkLabel(settings_card, text="Email Address", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=30, pady=(10, 2))
        self.set_email = ctk.CTkEntry(settings_card, width=460, height=42, fg_color="#020617")
        self.set_email.insert(0, self.current_user.get('email', ''))
        self.set_email.pack(anchor="w", padx=30, pady=5)

        ctk.CTkLabel(settings_card, text="New Security PIN (Optional)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=30, pady=(10, 2))
        self.set_pin = ctk.CTkEntry(settings_card, placeholder_text="••••", show="*", width=460, height=42, fg_color="#020617")
        self.set_pin.pack(anchor="w", padx=30, pady=5)

        ctk.CTkButton(settings_card, text="Save Changes", command=self.update_profile, fg_color="#2563eb", hover_color="#1d4ed8", width=460, height=46, font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=30, pady=25)

    def load_current_profile_pic_preview(self):
        pic_data = self.current_user.get('profilePic', '')
        if pic_data:
            try:
                img_data = base64.b64decode(pic_data)
                img = Image.open(io.BytesIO(img_data)).resize((110, 110), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.pic_label.configure(image=photo, text="")
                self.pic_label.image = photo
            except Exception:
                pass

    def upload_profile_picture(self):
        file_path = filedialog.askopenfilename(title="Select Profile Picture", filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.profile_pic_path = file_path
            try:
                with open(file_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                self.profile_pic_base64 = encoded_string

                img = Image.open(file_path).resize((110, 110), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.pic_label.configure(image=photo, text="")
                self.pic_label.image = photo
                messagebox.showinfo("Success", "Profile picture loaded! Click 'Save Changes' to update profile.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def update_profile(self):
        new_phone = self.set_phone.get().strip()
        new_email = self.set_email.get().strip()
        new_pin = self.set_pin.get().strip()
        pic_to_send = getattr(self, 'profile_pic_base64', self.current_user.get('profilePic', ''))

        try:
            res = requests.post(f"{API_URL}/user/profile/update", json={
                "currentPhone": self.current_user['phone'],
                "newPhone": new_phone,
                "newEmail": new_email,
                "newPin": new_pin if new_pin else None,
                "profilePic": pic_to_send
            })
            data = res.json()
            if res.status_code == 200:
                messagebox.showinfo("Success", "Profile updated successfully!")
                self.current_user = data.get('user', self.current_user)
                self.load_header_profile_pic()
            else:
                messagebox.showerror("Error", data.get("message", "Failed to update profile."))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_chat_tab(self):
        self.clear_tab()
        
        chat_card = ctk.CTkFrame(self.tab_content_frame, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=18)
        chat_card.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(chat_card, text="Live Support Chat", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(anchor="w", padx=25, pady=(20, 15))

        self.chat_box = ctk.CTkScrollableFrame(chat_card, fg_color="#020617", height=450, corner_radius=12)
        self.chat_box.pack(fill="both", expand=True, padx=25, pady=5)

        self.refresh_chat_messages()

        input_frame = ctk.CTkFrame(chat_card, fg_color="transparent")
        input_frame.pack(fill="x", padx=25, pady=20)

        self.chat_inp = ctk.CTkEntry(input_frame, placeholder_text="Type your message to support...", height=46, fg_color="#020617", font=ctk.CTkFont(size=13))
        self.chat_inp.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.chat_inp.bind("<Return>", lambda e: self.send_chat_msg())

        ctk.CTkButton(input_frame, text="Send", command=self.send_chat_msg, fg_color="#2563eb", hover_color="#1d4ed8", width=120, height=46, font=ctk.CTkFont(size=14, weight="bold")).pack(side="right")

    def refresh_chat_messages(self):
        for w in self.chat_box.winfo_children(): w.destroy()
        try:
            res = requests.get(f"{API_URL}/chat/{self.current_user['phone']}")
            msgs = res.json() if res.status_code == 200 else []
            if not msgs:
                ctk.CTkLabel(self.chat_box, text="No messages yet. Start a conversation with support!", text_color="gray", font=ctk.CTkFont(size=13)).pack(pady=40)
                return
            for m in msgs:
                role = m.get('senderRole', 'user')
                msg_text = f"{role.upper()}: {m.get('message')}"
                align_anchor = "e" if role == 'user' else "w"
                color = "#2563eb" if role == 'user' else "#334155"
                
                msg_lbl = ctk.CTkLabel(self.chat_box, text=msg_text, font=ctk.CTkFont(size=13), fg_color=color, corner_radius=10, padx=15, pady=10, text_color="#ffffff")
                msg_lbl.pack(anchor=align_anchor, pady=6, padx=12)
        except Exception as e:
            ctk.CTkLabel(self.chat_box, text=f"Error loading chat: {e}", text_color="red").pack(pady=20)

    def send_chat_msg(self):
        msg = self.chat_inp.get().strip()
        if not msg: return
        try:
            res = requests.post(f"{API_URL}/chat/send", json={
                "userPhone": self.current_user['phone'],
                "senderRole": "user",
                "message": msg
            })
            if res.status_code == 200:
                self.chat_inp.delete(0, "end")
                self.refresh_chat_messages()
            else:
                messagebox.showerror("Error", "Failed to send message.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = CustomerApp()
    app.mainloop()