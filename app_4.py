import customtkinter as ctk
import requests
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os
import base64
import io

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Environment-aware API URL for container/Railway deployment
API_URL = os.getenv("API_URL", "http://localhost:5000/api")

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
            if not dialog.pin: return
            
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
            uid = id_entry.get().strip()
            amt = amt_entry.get().strip()
            if not uid or not amt:
                return messagebox.showerror("Error", "Fill all fields.", parent=popup)
            
            dialog = PinDialog(self, title="Authorize Betting Funding")
            if not dialog.pin: return

            try:
                res = requests.post(f"{API_URL}/user/betting", json={"phone": self.current_user['phone'], "provider": prov, "customerId": uid, "amount": float(amt), "pin": dialog.pin})
                data = res.json()
                if res.status_code == 200:
                    messagebox.showinfo("Success", data.get("message", "Betting account funded!"))
                    self.current_user['balance'] = data.get("newBalance", self.current_user['balance'])
                    popup.destroy()
                    self.load_overview_tab()
                else:
                    messagebox.showerror("Error", data.get("message", "Funding failed."), parent=popup)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        ctk.CTkButton(popup, text="Fund Bet Account", command=execute, fg_color="#f59e0b", hover_color="#d97706", width=350, height=44, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=25)

    def open_card_modal(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Virtual / Physical ATM Card")
        popup.geometry("440x360")
        popup.configure(fg_color="#0f172a")
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text="💳 PayDesktop Debit Card", font=ctk.CTkFont(size=18, weight="bold"), text_color="#38bdf8").pack(pady=(25, 15))

        status = self.current_user.get('cardStatus', 'NOT_REQUESTED')
        card_info_frame = ctk.CTkFrame(popup, fg_color="#1e293b", corner_radius=14, width=380, height=140)
        card_info_frame.pack(padx=30, pady=10)
        card_info_frame.pack_propagate(False)

        if status == 'ASSIGNED':
            ctk.CTkLabel(card_info_frame, text="PayDesktop Bank Debit Card", font=ctk.CTkFont(size=14, weight="bold"), text_color="#fbbf24").pack(pady=(15, 5))
            ctk.CTkLabel(card_info_frame, text="**** **** **** 8892", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff").pack(pady=2)
            ctk.CTkLabel(card_info_frame, text=f"Cardholder: {self.current_user['name']} | Status: Active", font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(pady=(5, 0))
        else:
            ctk.CTkLabel(card_info_frame, text=f"Card Status: {status}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ef4444").pack(pady=(35, 10))
            ctk.CTkLabel(card_info_frame, text="Request a card from branch admin or wait for approval.", font=ctk.CTkFont(size=12), text_color="#94a3b8").pack()

        def request_card():
            try:
                res = requests.post(f"{API_URL}/user/card/request", json={"accountNo": self.current_user['accountNo']})
                data = res.json()
                if res.status_code == 200:
                    messagebox.showinfo("Success", data.get("message", "Card requested!"), parent=popup)
                    popup.destroy()
                else:
                    messagebox.showerror("Error", data.get("message"), parent=popup)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        if status == 'NOT_REQUESTED':
            ctk.CTkButton(popup, text="Request New Card", command=request_card, fg_color="#2563eb", hover_color="#1d4ed8", width=380, height=42, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15)

    def load_transfer_tab(self):
        self.clear_tab()
        ctk.CTkLabel(self.tab_content_frame, text="Fund Transfer", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 20))

        form_card = ctk.CTkFrame(self.tab_content_frame, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=16)
        form_card.pack(fill="x", pady=5, ipady=20)

        inner = ctk.CTkFrame(form_card, fg_color="transparent")
        inner.pack(padx=30, pady=15, fill="x")

        ctk.CTkLabel(inner, text="Recipient Bank", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", pady=(5, 2))
        bank_menu = ctk.CTkComboBox(inner, values=["PayDesktop Bank", "OPay", "Kuda Bank", "Access Bank", "GTBank"], width=450, height=40)
        bank_menu.pack(anchor="w", pady=4)

        ctk.CTkLabel(inner, text="Recipient Account Number", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", pady=(10, 2))
        acc_entry = ctk.CTkEntry(inner, placeholder_text="10-digit account number", width=450, height=40)
        acc_entry.pack(anchor="w", pady=4)

        ctk.CTkLabel(inner, text="Amount (₦)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", pady=(10, 2))
        amt_entry = ctk.CTkEntry(inner, placeholder_text="5000", width=450, height=40)
        amt_entry.pack(anchor="w", pady=4)

        ctk.CTkLabel(inner, text="Narration / Note (Optional)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", pady=(10, 2))
        note_entry = ctk.CTkEntry(inner, placeholder_text="Dinner payment...", width=450, height=40)
        note_entry.pack(anchor="w", pady=4)

        def execute_transfer():
            bank = bank_menu.get()
            acc = acc_entry.get().strip()
            amt = amt_entry.get().strip()
            note = note_entry.get().strip()

            if not acc or not amt:
                return messagebox.showerror("Error", "Enter account number and amount.")

            dialog = PinDialog(self, title="Authorize Transfer")
            if not dialog.pin: return

            try:
                res = requests.post(f"{API_URL}/user/transfer", json={
                    "senderPhone": self.current_user['phone'],
                    "recipientBank": bank,
                    "recipientAccountNo": acc,
                    "amount": float(amt),
                    "note": note,
                    "pin": dialog.pin
                })
                data = res.json()
                if res.status_code == 200:
                    messagebox.showinfo("Success", data.get("message", "Transfer successful!"))
                    self.current_user['balance'] = data.get("newBalance", self.current_user['balance'])
                    acc_entry.delete(0, 'end')
                    amt_entry.delete(0, 'end')
                    note_entry.delete(0, 'end')
                    self.load_overview_tab()
                else:
                    messagebox.showerror("Error", data.get("message", "Transfer failed."))
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(inner, text="Send Money", command=execute_transfer, fg_color="#2563eb", hover_color="#1d4ed8", width=450, height=45, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(25, 5))

    def load_history_tab(self):
        self.clear_tab()
        ctk.CTkLabel(self.tab_content_frame, text="Transaction History", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 20))

        try:
            res = requests.get(f"{API_URL}/user/transactions/{self.current_user['accountNo']}")
            txs = res.json() if res.status_code == 200 else []
            if not txs:
                ctk.CTkLabel(self.tab_content_frame, text="No transactions recorded yet.", text_color="gray", font=ctk.CTkFont(size=14)).pack(pady=40)
                return

            for t in txs:
                card = ctk.CTkFrame(self.tab_content_frame, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=12, height=70)
                card.pack(fill="x", pady=6, padx=2)
                card.pack_propagate(False)

                left = ctk.CTkFrame(card, fg_color="transparent")
                left.pack(side="left", fill="y", padx=20, pady=12)
                ctk.CTkLabel(left, text=t.get('type', 'TRANSFER').upper(), font=ctk.CTkFont(size=14, weight="bold"), text_color="#38bdf8").pack(anchor="w")
                ctk.CTkLabel(left, text=t.get('note', 'No note provided'), font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w")

                right = ctk.CTkFrame(card, fg_color="transparent")
                right.pack(side="right", fill="y", padx=20, pady=12)
                ctk.CTkLabel(right, text=f"₦{t.get('amount', 0):,.2f}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff").pack(anchor="e")
                ctk.CTkLabel(right, text=t.get('date', '')[:10], font=ctk.CTkFont(size=11), text_color="#64748b").pack(anchor="e")

        except Exception as e:
            ctk.CTkLabel(self.tab_content_frame, text=f"Error loading history: {e}", text_color="red").pack(pady=20)

    def load_settings_tab(self):
        self.clear_tab()
        ctk.CTkLabel(self.tab_content_frame, text="Account Settings & KYC", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 20))

        card = ctk.CTkFrame(self.tab_content_frame, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=16)
        card.pack(fill="x", pady=5, ipady=20)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=30, pady=15, fill="x")

        ctk.CTkLabel(inner, text="Profile Picture", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", pady=(5, 2))
        
        def upload_pic():
            file_path = filedialog.askopenfilename(title="Select Profile Picture", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
            if file_path:
                try:
                    with open(file_path, "rb") as f:
                        encoded = base64.b64encode(f.read()).decode('utf-8')
                    res = requests.put(f"{API_URL}/user/profile-pic", json={"phone": self.current_user['phone'], "profilePic": encoded})
                    if res.status_code == 200:
                        self.current_user['profilePic'] = encoded
                        self.load_header_profile_pic()
                        messagebox.showinfo("Success", "Profile picture updated successfully!")
                    else:
                        messagebox.showerror("Error", "Failed to upload picture.")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        ctk.CTkButton(inner, text="Upload New Picture", command=upload_pic, fg_color="#334155", hover_color="#475569", width=250, height=38).pack(anchor="w", pady=5)

        ctk.CTkLabel(inner, text="KYC Verification Tier", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", pady=(15, 2))
        ctk.CTkLabel(inner, text=f"Current Status: {self.current_user.get('kycTier', 'Tier 1')}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#fbbf24").pack(anchor="w", pady=2)

        def request_tier3_upgrade():
            if messagebox.askyesno("Confirm", "Request upgrade to Tier 3 from Admin?"):
                try:
                    res = requests.post(f"{API_URL}/admin/request-action", json={
                        "adminPhone": "Customer",
                        "adminName": self.current_user['name'],
                        "actionType": "TIER3_UPGRADE",
                        "targetAccountNo": self.current_user['accountNo'],
                        "targetName": self.current_user['name']
                    })
                    if res.status_code == 200:
                        messagebox.showinfo("Success", "Tier 3 upgrade request submitted to admin.")
                    else:
                        messagebox.showerror("Error", "Failed to submit request.")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        ctk.CTkButton(inner, text="Request Tier 3 Upgrade", command=request_tier3_upgrade, fg_color="#7c3aed", hover_color="#6d28d9", width=250, height=38).pack(anchor="w", pady=10)

    def load_chat_tab(self):
        self.clear_tab()
        ctk.CTkLabel(self.tab_content_frame, text="Live Support Chat", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 20))

        chat_card = ctk.CTkFrame(self.tab_content_frame, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=16, height=450)
        chat_card.pack(fill="x", pady=5)
        chat_card.pack_propagate(False)

        msgs_frame = ctk.CTkScrollableFrame(chat_card, fg_color="#020617", height=340)
        msgs_frame.pack(fill="x", padx=20, pady=15)

        def refresh_chat():
            for w in msgs_frame.winfo_children(): w.destroy()
            try:
                res = requests.get(f"{API_URL}/chat/{self.current_user['phone']}")
                msgs = res.json() if res.status_code == 200 else []
                for m in msgs:
                    role = m.get('senderRole', 'user').upper()
                    text = m.get('message', '')
                    ctk.CTkLabel(msgs_frame, text=f"[{role}]: {text}", font=ctk.CTkFont(size=13), text_color="#38bdf8" if role != 'USER' else "#cbd5e1").pack(anchor="w", pady=4, padx=5)
            except Exception:
                pass

        refresh_chat()

        input_row = ctk.CTkFrame(chat_card, fg_color="transparent")
        input_row.pack(fill="x", padx=20, pady=5)

        msg_entry = ctk.CTkEntry(input_row, placeholder_text="Type message to support...", width=650, height=40)
        msg_entry.pack(side="left", padx=(0, 10))

        def send_msg():
            txt = msg_entry.get().strip()
            if not txt: return
            try:
                res = requests.post(f"{API_URL}/chat/send", json={
                    "userPhone": self.current_user['phone'],
                    "senderRole": "user",
                    "message": txt
                })
                if res.status_code == 200:
                    msg_entry.delete(0, 'end')
                    refresh_chat()
                else:
                    messagebox.showerror("Error", "Failed to send message.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(input_row, text="Send", command=send_msg, fg_color="#2563eb", hover_color="#1d4ed8", width=100, height=40, font=ctk.CTkFont(size=13, weight="bold")).pack(side="right")

if __name__ == "__main__":
    app = CustomerApp()
    app.mainloop()