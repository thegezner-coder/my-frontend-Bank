import customtkinter as ctk
import requests
from tkinter import messagebox
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Environment-aware API URL for container/Railway deployment
API_URL = os.getenv("API_URL", "http://localhost:5000/api")

class PayDesktopAdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PayDesktop Bank - Admin Portal")
        self.geometry("1350x850")
        self.current_admin = None
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
        ctk.CTkLabel(auth_frame, text="Admin & Super Admin Portal", font=ctk.CTkFont(size=13), text_color="#94a3b8").pack(pady=(0, 15))

        self.auth_tabview = ctk.CTkTabview(auth_frame, width=420, height=390, fg_color="#1e293b", segmented_button_fg_color="#0f172a")
        self.auth_tabview.pack(padx=30, pady=10)

        tab_login = self.auth_tabview.add("Admin Login")
        tab_reg = self.auth_tabview.add("Create Admin")

        # Login Tab
        ctk.CTkLabel(tab_login, text="Admin Phone Number", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", pady=(10, 2))
        self.login_phone = ctk.CTkEntry(tab_login, placeholder_text="08000000000", width=360, height=40, fg_color="#0f172a", border_color="#334155")
        self.login_phone.pack(pady=4)

        ctk.CTkLabel(tab_login, text="PIN / Password", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", pady=(10, 2))
        self.login_pin = ctk.CTkEntry(tab_login, placeholder_text="••••", show="*", width=360, height=40, fg_color="#0f172a", border_color="#334155")
        self.login_pin.pack(pady=4)

        ctk.CTkButton(tab_login, text="Login to Portal", command=self.handle_login, width=360, height=44, fg_color="#2563eb", hover_color="#1d4ed8", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=25)

        # Register Tab
        ctk.CTkLabel(tab_reg, text="Full Name", font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w", pady=(2, 1))
        self.reg_name = ctk.CTkEntry(tab_reg, placeholder_text="Admin Name", width=360, height=34, fg_color="#0f172a", border_color="#334155")
        self.reg_name.pack(pady=2)

        ctk.CTkLabel(tab_reg, text="Phone Number", font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w", pady=(2, 1))
        self.reg_phone = ctk.CTkEntry(tab_reg, placeholder_text="Phone Number", width=360, height=34, fg_color="#0f172a", border_color="#334155")
        self.reg_phone.pack(pady=2)

        ctk.CTkLabel(tab_reg, text="PIN", font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w", pady=(2, 1))
        self.reg_pin = ctk.CTkEntry(tab_reg, placeholder_text="••••", show="*", width=360, height=34, fg_color="#0f172a", border_color="#334155")
        self.reg_pin.pack(pady=2)

        ctk.CTkLabel(tab_reg, text="Admin Role", font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w", pady=(2, 1))
        self.reg_role = ctk.CTkComboBox(tab_reg, values=["admin", "super_admin"], width=360, height=34)
        self.reg_role.set("admin")
        self.reg_role.pack(pady=2)

        ctk.CTkButton(tab_reg, text="Register Admin Account", command=self.handle_register, width=360, height=40, fg_color="#059669", hover_color="#047857", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15)

    def handle_login(self):
        phone, pin = self.login_phone.get().strip(), self.login_pin.get().strip()
        if not phone or not pin:
            return messagebox.showerror("Error", "Enter phone and PIN.")
        try:
            res = requests.post(f"{API_URL}/admin/login", json={"phone": phone, "pin": pin})
            data = res.json()
            if res.status_code == 200:
                self.current_admin = data
                self.show_dashboard()
            else:
                messagebox.showerror("Error", data.get("message", "Login failed."))
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def handle_register(self):
        name = self.reg_name.get().strip()
        phone = self.reg_phone.get().strip()
        pin = self.reg_pin.get().strip()
        role = self.reg_role.get().strip()
        if not name or not phone or not pin:
            return messagebox.showerror("Error", "Fill all fields.")
        try:
            res = requests.post(f"{API_URL}/admin/register", json={"name": name, "phone": phone, "pin": pin, "role": role})
            data = res.json()
            if res.status_code in [200, 201]:
                messagebox.showinfo("Success", "Admin registered successfully!")
                self.auth_tabview.set("Admin Login")
            else:
                messagebox.showerror("Error", data.get("message", "Registration failed."))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_dashboard(self):
        self.clear_window()
        self.configure(fg_color="#020617")

        sidebar = ctk.CTkFrame(self, width=280, fg_color="#0f172a", corner_radius=0, border_width=1, border_color="#1e293b")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="PayDesktop Admin", font=ctk.CTkFont(size=20, weight="bold"), text_color="#60a5fa").pack(pady=(30, 15), padx=20, anchor="w")
        
        role_text = "⭐ Super Admin" if self.current_admin['role'] == 'super_admin' else "🛡️ Branch Admin"
        ctk.CTkLabel(sidebar, text=role_text, font=ctk.CTkFont(size=12, weight="bold"), text_color="#fbbf24", fg_color="#78350f", corner_radius=8, width=240, height=34).pack(pady=(0, 20), padx=20)

        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15)

        self.nav_buttons = {}
        tabs = [
            ("Live Analytics", self.load_analytics_tab),
            ("Pending Approvals", self.load_pending_tab),
            ("Manage Customers", self.load_customers_tab),
            ("Transactions", self.load_transactions_tab),
            ("Broadcasts", self.load_broadcast_tab),
            ("Support Chats", self.load_chats_tab)
        ]

        if self.current_admin['role'] == 'super_admin':
            tabs.append(("Admin Requests", self.load_requests_tab))

        for name, cmd in tabs:
            btn = ctk.CTkButton(nav_frame, text=name, command=lambda c=cmd, n=name: [self.set_active_tab(n), c()], fg_color="transparent", hover_color="#1e293b", text_color="#cbd5e1", anchor="w", font=ctk.CTkFont(size=13, weight="bold"), height=42, width=250)
            btn.pack(pady=4)
            self.nav_buttons[name] = btn

        logout_btn = ctk.CTkButton(sidebar, text="Logout", command=self.show_auth_screen, fg_color="#dc2626", hover_color="#b91c1c", height=42, width=240, font=ctk.CTkFont(size=13, weight="bold"))
        logout_btn.pack(side="bottom", pady=25)

        right_container = ctk.CTkFrame(self, fg_color="#020617")
        right_container.pack(side="right", fill="both", expand=True)

        header = ctk.CTkFrame(right_container, height=75, fg_color="#0f172a", corner_radius=0, border_width=1, border_color="#1e293b")
        header.pack(fill="x")
        header.pack_propagate(False)

        self.page_title_lbl = ctk.CTkLabel(header, text="Live System Analytics & Overview", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ffffff")
        self.page_title_lbl.pack(side="left", padx=30)

        admin_info = ctk.CTkFrame(header, fg_color="transparent")
        admin_info.pack(side="right", padx=30)
        ctk.CTkLabel(admin_info, text=self.current_admin['name'], font=ctk.CTkFont(size=14, weight="bold"), text_color="#cbd5e1").pack(side="left", padx=12)

        self.content_scroll = ctk.CTkScrollableFrame(right_container, fg_color="#020617")
        self.content_scroll.pack(fill="both", expand=True, padx=30, pady=25)

        self.load_analytics_tab()
        self.set_active_tab("Live Analytics")

    def set_active_tab(self, active_name):
        self.page_title_lbl.configure(text=active_name)
        for name, btn in self.nav_buttons.items():
            if name == active_name:
                btn.configure(fg_color="#2563eb", text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color="#cbd5e1")

    def clear_content(self):
        for w in self.content_scroll.winfo_children():
            w.destroy()

    def load_analytics_tab(self):
        self.clear_content()
        try:
            users_res = requests.get(f"{API_URL}/admin/users")
            tx_res = requests.get(f"{API_URL}/admin/transactions")
            users = users_res.json() if users_res.status_code == 200 else []
            txs = tx_res.json() if tx_res.status_code == 200 else []

            active_count = len([u for u in users if u.get('status') == 'ACTIVE'])
            pending_count = len([u for u in users if u.get('status') == 'PENDING'])
            total_vol = sum([t.get('amount', 0) for t in txs])

            metrics_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
            metrics_frame.pack(fill="x", pady=15)

            cards_data = [
                ("Total Customers", str(len(users)), f"{active_count} Active Accounts", "#38bdf8"),
                ("Pending Approvals", str(pending_count), "Require admin review", "#fbbf24"),
                ("Total Volume", f"₦{total_vol:,.2f}", f"{len(txs)} transactions processed", "#34d399")
            ]

            for title, val, sub, color in cards_data:
                card = ctk.CTkFrame(metrics_frame, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=18, height=150, width=340)
                card.pack(side="left", padx=12, expand=True, fill="x")
                card.pack_propagate(False)
                ctk.CTkLabel(card, text=title.upper(), font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=25, pady=(25, 5))
                ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=32, weight="bold"), text_color=color).pack(anchor="w", padx=25)
                ctk.CTkLabel(card, text=sub, font=ctk.CTkFont(size=12), text_color="#64748b").pack(anchor="w", padx=25, pady=(8, 0))

        except Exception as e:
            ctk.CTkLabel(self.content_scroll, text=f"Error loading analytics: {e}", text_color="red", font=ctk.CTkFont(size=14)).pack(pady=25)

    def load_pending_tab(self):
        self.clear_content()
        ctk.CTkLabel(self.content_scroll, text="Pending Account Requests", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 20))
        try:
            res = requests.get(f"{API_URL}/admin/pending-users")
            users = res.json() if res.status_code == 200 else []
            if not users:
                ctk.CTkLabel(self.content_scroll, text="No pending account requests at the moment.", text_color="gray", font=ctk.CTkFont(size=14)).pack(pady=40)
                return
            for u in users:
                card = ctk.CTkFrame(self.content_scroll, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=14)
                card.pack(fill="x", pady=8, padx=5, ipady=12)

                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=25)
                ctk.CTkLabel(info_frame, text=u.get('name'), font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff").pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"Phone: {u.get('phone')} | Email: {u.get('email', 'N/A')} | Acc No: {u.get('accountNo')}", font=ctk.CTkFont(size=13), text_color="#94a3b8").pack(anchor="w")

                btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                btn_frame.pack(side="right", padx=25)
                ctk.CTkButton(btn_frame, text="Approve", command=lambda acc=u.get('accountNo'): self.approve_user(acc), fg_color="#059669", hover_color="#047857", width=100, height=38, font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=8)
                ctk.CTkButton(btn_frame, text="Reject", command=lambda acc=u.get('accountNo'): self.reject_user(acc), fg_color="#dc2626", hover_color="#b91c1c", width=100, height=38, font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=8)
        except Exception as e:
            ctk.CTkLabel(self.content_scroll, text=f"Error: {e}", text_color="red").pack(pady=20)

    def approve_user(self, acc_no):
        try:
            res = requests.post(f"{API_URL}/admin/user/approve", json={"accountNumber": acc_no})
            if res.status_code == 200:
                messagebox.showinfo("Success", "Account approved successfully!")
                self.load_pending_tab()
            else:
                messagebox.showerror("Error", "Failed to approve.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reject_user(self, acc_no):
        try:
            res = requests.post(f"{API_URL}/admin/user/reject", json={"accountNumber": acc_no})
            if res.status_code == 200:
                messagebox.showinfo("Success", "Account rejected.")
                self.load_pending_tab()
            else:
                messagebox.showerror("Error", "Failed to reject.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_customers_tab(self):
        self.clear_content()
        ctk.CTkLabel(self.content_scroll, text="Customer Management & Card Assignments", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 20))
        try:
            res = requests.get(f"{API_URL}/admin/users")
            users = res.json() if res.status_code == 200 else []
            if not users:
                ctk.CTkLabel(self.content_scroll, text="No customers found.", text_color="gray", font=ctk.CTkFont(size=14)).pack(pady=40)
                return
            for u in users:
                card = ctk.CTkFrame(self.content_scroll, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=14)
                card.pack(fill="x", pady=8, padx=5, ipady=12)

                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=25)
                ctk.CTkLabel(info_frame, text=f"{u.get('name')} (Acc: {u.get('accountNo')})", font=ctk.CTkFont(size=15, weight="bold"), text_color="#ffffff").pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"Balance: ₦{u.get('balance', 0):,.2f} | KYC: {u.get('kycTier', 'Tier 1')} | Card: {u.get('cardStatus', 'NOT_REQUESTED')} | Status: {u.get('status')}", font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(anchor="w")

                btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                btn_frame.pack(side="right", padx=20)

                ctk.CTkButton(btn_frame, text="Card", command=lambda acc=u.get('accountNo'): self.assign_card(acc), fg_color="#0284c7", hover_color="#0369a1", width=75, height=32, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=4)
                ctk.CTkButton(btn_frame, text="Credit", command=lambda ph=u.get('phone'): self.adjust_balance(ph, "CREDIT"), fg_color="#059669", hover_color="#047857", width=75, height=32, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=4)
                ctk.CTkButton(btn_frame, text="Freeze", command=lambda acc=u.get('accountNo'), st=u.get('status'): self.toggle_freeze(acc, st), fg_color="#475569", hover_color="#334155", width=75, height=32, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=4)
                
                if self.current_admin['role'] == 'super_admin':
                    ctk.CTkButton(btn_frame, text="Delete", command=lambda acc=u.get('accountNo'): self.super_delete_user(acc), fg_color="#dc2626", hover_color="#b91c1c", width=75, height=32, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=4)
                else:
                    ctk.CTkButton(btn_frame, text="Del Req", command=lambda acc=u.get('accountNo'), nm=u.get('name'): self.apply_action("DELETE_CUSTOMER", acc, nm), fg_color="#b45309", hover_color="#92400e", width=75, height=32, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=4)
        except Exception as e:
            ctk.CTkLabel(self.content_scroll, text=f"Error loading customers: {e}", text_color="red").pack(pady=20)

    def assign_card(self, account_no):
        try:
            res = requests.post(f"{API_URL}/admin/assign-card", json={"accountNo": account_no})
            data = res.json()
            if res.status_code == 200:
                messagebox.showinfo("Success", data.get("message", "Card assigned successfully!"))
                self.load_customers_tab()
            else:
                messagebox.showerror("Error", data.get("message", "Failed to assign card."))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def adjust_balance(self, phone, type_str):
        dialog = ctk.CTkInputDialog(text=f"Enter amount to {type_str}:", title=f"Balance {type_str}")
        amt_str = dialog.get_input()
        if not amt_str:
            return
        try:
            amount = float(amt_str)
            res = requests.post(f"{API_URL}/admin/balance-adjust", json={"phone": phone, "amount": amount, "type": type_str})
            data = res.json()
            if res.status_code == 200:
                messagebox.showinfo("Success", data.get("message", "Balance adjusted successfully!"))
                self.load_customers_tab()
            else:
                messagebox.showerror("Error", data.get("message", "Adjustment failed."))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def toggle_freeze(self, account_no, current_status):
        new_status = "ACTIVE" if current_status == "FROZEN" else "FROZEN"
        try:
            res = requests.put(f"{API_URL}/admin/users/{account_no}/status", json={"status": new_status})
            if res.status_code == 200:
                messagebox.showinfo("Success", f"Account status updated to {new_status}")
                self.load_customers_tab()
            else:
                messagebox.showerror("Error", "Failed to update status.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def super_delete_user(self, account_no):
        if messagebox.askyesno("Confirm", "Are you sure you want to permanently delete this customer?"):
            try:
                res = requests.delete(f"{API_URL}/admin/user/{account_no}")
                if res.status_code == 200:
                    messagebox.showinfo("Success", "Customer deleted.")
                    self.load_customers_tab()
                else:
                    messagebox.showerror("Error", "Failed to delete.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def apply_action(self, action_type, account_no, name):
        if messagebox.askyesno("Confirm", "Submit request to Super Admin?"):
            try:
                res = requests.post(f"{API_URL}/admin/request-action", json={
                    "adminPhone": self.current_admin['phone'],
                    "adminName": self.current_admin['name'],
                    "actionType": action_type,
                    "targetAccountNo": account_no,
                    "targetName": name
                })
                if res.status_code == 200:
                    messagebox.showinfo("Success", "Request sent to Super Admin.")
                else:
                    messagebox.showerror("Error", "Failed to send request.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_transactions_tab(self):
        self.clear_content()
        ctk.CTkLabel(self.content_scroll, text="Transactions & Statements", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 20))
        try:
            res = requests.get(f"{API_URL}/admin/transactions")
            txs = res.json() if res.status_code == 200 else []
            if not txs:
                ctk.CTkLabel(self.content_scroll, text="No transactions found.", text_color="gray", font=ctk.CTkFont(size=14)).pack(pady=40)
                return
            for t in txs:
                card = ctk.CTkFrame(self.content_scroll, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=12)
                card.pack(fill="x", pady=6, padx=5, ipady=8)
                ctk.CTkLabel(card, text=f"{t.get('type')} ({t.get('recipientBank', 'PayDesktop Bank')}) - ₦{t.get('amount', 0):,.2f} ({t.get('note', 'No note')})", font=ctk.CTkFont(size=13, weight="bold"), text_color="#38bdf8").pack(anchor="w", padx=20, pady=8)
        except Exception as e:
            ctk.CTkLabel(self.content_scroll, text=f"Error loading transactions: {e}", text_color="red").pack(pady=20)

    def load_broadcast_tab(self):
        self.clear_content()
        ctk.CTkLabel(self.content_scroll, text="Dynamic Broadcast Management", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 20))
        
        input_frame = ctk.CTkFrame(self.content_scroll, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=14)
        input_frame.pack(fill="x", pady=8, padx=5, ipady=15)
        
        ctk.CTkLabel(input_frame, text="Post New Marquee Broadcast Banner", font=ctk.CTkFont(size=14, weight="bold"), text_color="#cbd5e1").pack(anchor="w", padx=20, pady=(15, 8))
        self.broadcast_box = ctk.CTkTextbox(input_frame, height=100, width=650, fg_color="#020617", border_color="#334155", border_width=1, font=ctk.CTkFont(size=13))
        self.broadcast_box.pack(padx=20, pady=8, anchor="w")
        ctk.CTkButton(input_frame, text="Publish Banner", command=self.send_broadcast, fg_color="#059669", hover_color="#047857", width=180, height=40, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=15)

    def send_broadcast(self):
        text = self.broadcast_box.get("1.0", "end-1c").strip()
        if not text:
            return messagebox.showerror("Error", "Broadcast text cannot be empty.")
        try:
            res = requests.post(f"{API_URL}/admin/broadcast", json={"text": text})
            if res.status_code in [200, 201]:
                messagebox.showinfo("Success", "Broadcast published successfully!")
                self.broadcast_box.delete("1.0", "end")
            else:
                messagebox.showerror("Error", "Failed to publish broadcast.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_chats_tab(self):
        self.clear_content()
        ctk.CTkLabel(self.content_scroll, text="Live Support Chats", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 20))
        try:
            res = requests.get(f"{API_URL}/admin/chats")
            chat_map = res.json() if res.status_code == 200 else {}
            if not chat_map:
                ctk.CTkLabel(self.content_scroll, text="No active support chats.", text_color="gray", font=ctk.CTkFont(size=14)).pack(pady=40)
                return
            for phone, msgs in chat_map.items():
                card = ctk.CTkFrame(self.content_scroll, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=14)
                card.pack(fill="x", pady=8, padx=5, ipady=12)
                ctk.CTkLabel(card, text=f"Customer Phone: {phone}", font=ctk.CTkFont(size=15, weight="bold"), text_color="#60a5fa").pack(anchor="w", padx=20, pady=8)
                
                for m in msgs:
                    ctk.CTkLabel(card, text=f"[{m.get('senderRole').upper()}]: {m.get('message')}", font=ctk.CTkFont(size=13), text_color="#cbd5e1").pack(anchor="w", padx=30, pady=3)
        except Exception as e:
            ctk.CTkLabel(self.content_scroll, text=f"Error loading chats: {e}", text_color="red").pack(pady=20)

    def load_requests_tab(self):
        self.clear_content()
        ctk.CTkLabel(self.content_scroll, text="Pending Admin Requests", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 20))
        try:
            res = requests.get(f"{API_URL}/admin/requests")
            requests_list = res.json() if res.status_code == 200 else []
            if not requests_list:
                ctk.CTkLabel(self.content_scroll, text="No pending admin requests.", text_color="gray", font=ctk.CTkFont(size=14)).pack(pady=40)
                return
            for r in requests_list:
                card = ctk.CTkFrame(self.content_scroll, fg_color="#0f172a", border_width=1, border_color="#1e293b", corner_radius=14)
                card.pack(fill="x", pady=8, padx=5, ipady=12)
                
                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=25)
                ctk.CTkLabel(info_frame, text=f"Admin: {r.get('adminName')} ({r.get('adminPhone')})", font=ctk.CTkFont(size=15, weight="bold"), text_color="#ffffff").pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"Action: {r.get('actionType')} on customer: {r.get('targetName')} (Acc: {r.get('targetAccountNo')})", font=ctk.CTkFont(size=13), text_color="#fbbf24").pack(anchor="w")

                btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                btn_frame.pack(side="right", padx=25)
                ctk.CTkButton(btn_frame, text="Approve", command=lambda rid=r.get('_id'): self.resolve_request(rid, "APPROVED"), fg_color="#059669", hover_color="#047857", width=100, height=38, font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=8)
                ctk.CTkButton(btn_frame, text="Reject", command=lambda rid=r.get('_id'): self.resolve_request(rid, "REJECTED"), fg_color="#dc2626", hover_color="#b91c1c", width=100, height=38, font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=8)
        except Exception as e:
            ctk.CTkLabel(self.content_scroll, text=f"Error loading requests: {e}", text_color="red").pack(pady=20)

    def resolve_request(self, req_id, decision):
        try:
            res = requests.post(f"{API_URL}/admin/requests/{req_id}/resolve", json={"decision": decision})
            if res.status_code == 200:
                messagebox.showinfo("Success", f"Request {decision.lower()}.")
                self.load_requests_tab()
            else:
                messagebox.showerror("Error", "Failed to resolve request.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = PayDesktopAdminApp()
    app.mainloop()