import flet as ft
from datetime import datetime

# Global History List
app_history = []


# ==========================================
# CATEGORY A: Time-Based Equipment Card (WITH MULTIPLE SESSIONS)
# ==========================================
class TimeEquipmentCard(ft.Container):
    def __init__(self, page, name, rate):
        super().__init__()
        self.my_page = page
        self.name = name
        self.rate = rate

        # Memory variables
        self.accumulated_seconds = 0
        self.current_start_dt = None
        self.current_end_dt = None

        # UI Elements
        self.start_text = ft.Text("Not set", color="#64748B", size=13)
        self.end_text = ft.Text("Not set", color="#64748B", size=13)
        self.status_text = ft.Text("", color="#10B981", size=12, italic=True)

        self.logged_total_text = ft.Text("Total: 0h 0m", color="#1E3A8A", weight=ft.FontWeight.BOLD)
        self.bill_text = ft.Text("0.00 Tk", color="#0F172A", weight=ft.FontWeight.BOLD, size=16)

        self.date_picker = ft.DatePicker(on_change=self.on_date_picked)
        self.time_picker = ft.TimePicker(on_change=self.on_time_picked)

        self.my_page.overlay.extend([self.date_picker, self.time_picker])
        self.picking_for = None
        self.temp_date = None

        # Premium Light Card Design
        self.bgcolor = "#FFFFFF"
        self.border_radius = 15
        self.padding = 15
        self.margin = ft.margin.only(bottom=15)
        self.shadow = ft.BoxShadow(spread_radius=1, blur_radius=10, color="#E2E8F0", offset=ft.Offset(0, 4))

        self.content = ft.Column([
            ft.Row([
                ft.Text(f"{self.name} ({self.rate} Tk/hr)", size=16, weight=ft.FontWeight.BOLD, color="#1E3A8A"),
                ft.ElevatedButton("🗑 Clear", color="#A4161A", bgcolor="#FEE2E2", height=30,
                                  on_click=self.clear_sessions)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            ft.Row([
                ft.ElevatedButton("▶ Start", bgcolor="#10B981", color="white",
                                  on_click=lambda _: self.open_date_picker("start")),
                self.start_text,
            ]),
            ft.Row([
                ft.ElevatedButton("⏹ Stop", bgcolor="#A4161A", color="white",
                                  on_click=lambda _: self.open_date_picker("end")),
                self.end_text,
            ]),

            ft.Row([
                ft.ElevatedButton("➕ Save Session", bgcolor="#1E3A8A", color="white", on_click=self.save_session),
                self.status_text
            ]),

            ft.Divider(color="#F1F5F9"),
            ft.Row([self.logged_total_text, self.bill_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ])

    def open_date_picker(self, target):
        self.picking_for = target
        self.date_picker.open = True
        self.my_page.update()

    def on_date_picked(self, _):
        if self.date_picker.value:
            self.temp_date = self.date_picker.value
            self.time_picker.open = True
            self.my_page.update()

    def on_time_picked(self, _):
        if self.time_picker.value and self.temp_date:
            t = self.time_picker.value
            dt = datetime(self.temp_date.year, self.temp_date.month, self.temp_date.day, t.hour, t.minute)

            if self.picking_for == "start":
                self.current_start_dt = dt
                self.start_text.value = dt.strftime("%d-%b %I:%M %p")
            elif self.picking_for == "end":
                self.current_end_dt = dt
                self.end_text.value = dt.strftime("%d-%b %I:%M %p")

            self.status_text.value = ""
            self.update()

    def save_session(self, _):
        if self.current_start_dt and self.current_end_dt:
            diff = self.current_end_dt - self.current_start_dt
            secs = diff.total_seconds()
            if secs > 0:
                self.accumulated_seconds += secs
                self.current_start_dt = None
                self.current_end_dt = None
                self.start_text.value = "Not set"
                self.end_text.value = "Not set"
                self.status_text.value = "Session Added!"
                self.status_text.color = "#10B981"
                self.update_totals()
            else:
                self.status_text.value = "Invalid Time!"
                self.status_text.color = "#A4161A"
                self.update()

    def clear_sessions(self, _):
        self.accumulated_seconds = 0
        self.current_start_dt = None
        self.current_end_dt = None
        self.start_text.value = "Not set"
        self.end_text.value = "Not set"
        self.status_text.value = "Cleared"
        self.status_text.color = "#A4161A"
        self.update_totals()

    def update_totals(self):
        m, s = divmod(self.accumulated_seconds, 60)
        h, m = divmod(m, 60)
        hours_decimal = self.accumulated_seconds / 3600

        self.logged_total_text.value = f"Total: {int(h)}h {int(m)}m"
        self.bill_text.value = f"{(hours_decimal * self.rate):.2f} Tk"
        self.update()

    def get_bill_amount(self):
        return (self.accumulated_seconds / 3600) * self.rate

    def reset(self):
        self.clear_sessions(None)


# ==========================================
# CATEGORY B: Fixed/Quantity Equipment Card
# ==========================================
class FixedEquipmentCard(ft.Container):
    def __init__(self, name, rate):
        super().__init__()
        self.name = name
        self.rate = rate
        self.qty = 0

        self.qty_text = ft.Text(str(self.qty), size=20, weight=ft.FontWeight.BOLD, color="#0F172A")
        self.bill_text = ft.Text("0.00 Tk", color="#0F172A", weight=ft.FontWeight.BOLD, size=16)

        self.bgcolor = "#FFFFFF"
        self.border_radius = 15
        self.padding = 15
        self.margin = ft.margin.only(bottom=15)
        self.shadow = ft.BoxShadow(spread_radius=1, blur_radius=10, color="#E2E8F0", offset=ft.Offset(0, 4))

        self.content = ft.Column([
            ft.Text(f"{self.name} ({self.rate} Tk)", size=16, weight=ft.FontWeight.BOLD, color="#1E3A8A"),
            ft.Row([
                ft.ElevatedButton("-", bgcolor="#A4161A", color="white", width=50, on_click=self.decrease),
                self.qty_text,
                ft.ElevatedButton("+", bgcolor="#10B981", color="white", width=50, on_click=self.increase),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(color="#F1F5F9"),
            ft.Row([ft.Text("Item Total:", color="#64748B"), self.bill_text],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ])

    def increase(self, _):
        self.qty += 1
        self.update_ui()

    def decrease(self, _):
        if self.qty > 0:
            self.qty -= 1
            self.update_ui()

    def update_ui(self):
        self.qty_text.value = str(self.qty)
        self.bill_text.value = f"{(self.qty * self.rate):.2f} Tk"
        self.update()

    def get_bill_amount(self):
        return self.qty * self.rate

    def reset(self):
        self.qty = 0
        self.update_ui()


# ==========================================
# MAIN APP ARCHITECTURE
# ==========================================
def main(page: ft.Page):
    page.title = "NICU Smart Bill"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F8FAFC"
    page.padding = 20
    page.window_width = 450
    page.window_height = 800
    page.scroll = ft.ScrollMode.AUTO

    history_listview = ft.ListView(spacing=10, padding=10, auto_scroll=True, height=300)
    history_dialog = ft.AlertDialog(
        title=ft.Text("Recent Patients (Last 20)", weight=ft.FontWeight.BOLD),
        content=history_listview,
        actions=[ft.TextButton("Close", on_click=lambda _: close_history())]
    )
    page.overlay.append(history_dialog)

    def open_history(_):
        history_listview.controls.clear()
        if not app_history:
            history_listview.controls.append(ft.Text("No history found.", italic=True))
        else:
            for entry in app_history:
                history_listview.controls.append(ft.Text(entry, size=14, color="#0F172A"))
        history_dialog.open = True
        page.update()

    def close_history():
        history_dialog.open = False
        page.update()

    page.appbar = ft.AppBar(
        title=ft.Text("NICU Billing", color="#FFFFFF", weight=ft.FontWeight.BOLD),
        bgcolor="#1E3A8A",
        center_title=True,
        actions=[
            ft.Container(
                content=ft.ElevatedButton("🕒 History", color="#1E3A8A", bgcolor="#FFFFFF", on_click=open_history),
                padding=ft.padding.only(right=10)
            )
        ]
    )

    hospital_header = ft.Column([
        ft.Text("Mahbubur Rahman Memorial Hospital", size=18, weight=ft.FontWeight.BOLD, color="#1E3A8A",
                text_align=ft.TextAlign.CENTER),
        ft.Text("Rupasdi, Bancharampur, Brahmanbaria", size=12, color="#64748B", text_align=ft.TextAlign.CENTER),
        ft.Divider(height=10, color="transparent")
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    patient_name_input = ft.TextField(
        label="Patient Name & ID",
        border_color="#1E3A8A",
        cursor_color="#1E3A8A",
        focused_border_color="#10B981",
        bgcolor="#FFFFFF",
        border_radius=10
    )

    time_services = [
        TimeEquipmentCard(page, "Cott", 62.5),
        TimeEquipmentCard(page, "Warmer", 125),
        TimeEquipmentCard(page, "Syringe Pump", 50),
        TimeEquipmentCard(page, "Infusion Pump", 50),
        TimeEquipmentCard(page, "Monitor", 100),
        TimeEquipmentCard(page, "Oxygen (Single)", 350),
        TimeEquipmentCard(page, "Oxygen (Double)", 700),
        TimeEquipmentCard(page, "Photo Therapy (Single)", 150),
        TimeEquipmentCard(page, "Photo Therapy (Double)", 300),
        TimeEquipmentCard(page, "C-PAP", 700),
        TimeEquipmentCard(page, "Ventilator", 500)
    ]

    fixed_services = [
        FixedEquipmentCard("IV Cannula (1/V)", 500),
        FixedEquipmentCard("NGT/OGT", 500),
        FixedEquipmentCard("CBG", 100),
        FixedEquipmentCard("Catheterization", 500),
        FixedEquipmentCard("Umbilical Catheter", 500),
        FixedEquipmentCard("Nebulization", 200),
        FixedEquipmentCard("Suction", 200),
        FixedEquipmentCard("ET Tube", 1000),
        FixedEquipmentCard("Duty Doctor Visit", 500),
        FixedEquipmentCard("Consultant Visit", 800)
    ]

    # Custom Inputs with Investigation added
    medicine_input = ft.TextField(label="Medicine Bill (Tk)", value="", keyboard_type=ft.KeyboardType.NUMBER,
                                  border_color="#1E3A8A", bgcolor="#FFFFFF", border_radius=10)
    investigation_input = ft.TextField(label="Investigation Bill (Tk)", value="", keyboard_type=ft.KeyboardType.NUMBER,
                                       border_color="#1E3A8A", bgcolor="#FFFFFF", border_radius=10)
    others_input = ft.TextField(label="Others Bill (Tk)", value="", keyboard_type=ft.KeyboardType.NUMBER,
                                border_color="#1E3A8A", bgcolor="#FFFFFF", border_radius=10)

    grand_total_display = ft.Text("TOTAL: 0.00 Tk", size=24, weight=ft.FontWeight.BOLD, color="#1E3A8A")

    def calculate_and_save(_):
        total = 0
        for item in time_services:
            total += item.get_bill_amount()

        for item in fixed_services:
            total += item.get_bill_amount()

        try:
            med_bill = float(medicine_input.value) if medicine_input.value else 0
        except ValueError:
            med_bill = 0

        try:
            inv_bill = float(investigation_input.value) if investigation_input.value else 0
        except ValueError:
            inv_bill = 0

        try:
            oth_bill = float(others_input.value) if others_input.value else 0
        except ValueError:
            oth_bill = 0

        # Add all custom bills to total
        total += med_bill + inv_bill + oth_bill

        grand_total_display.value = f"TOTAL: {total:.2f} Tk"

        if total > 0:
            name = patient_name_input.value if patient_name_input.value else "Unknown"
            now = datetime.now().strftime("%d %b, %I:%M %p")
            entry = f"👤 {name} | 📅 {now} | 💰 {total:.2f} Tk"
            app_history.insert(0, entry)
            if len(app_history) > 20:
                app_history.pop()

        page.update()

    def reset_for_new_patient(_):
        patient_name_input.value = ""
        medicine_input.value = ""
        investigation_input.value = ""
        others_input.value = ""
        for item in time_services:
            item.reset()
        for item in fixed_services:
            item.reset()
        grand_total_display.value = "TOTAL: 0.00 Tk"
        page.update()

    calc_btn = ft.ElevatedButton("GENERATE & SAVE BILL", bgcolor="#1E3A8A", color="white", height=50, width=400,
                                 on_click=calculate_and_save)
    reset_btn = ft.ElevatedButton("NEW PATIENT (RESET)", bgcolor="#FEE2E2", color="#A4161A", height=50, width=400,
                                  on_click=reset_for_new_patient)

    credit_text = ft.Text("Design and developed by MH-TOHA | TEX-IT", color="#64748B", italic=True, size=12)

    page.add(
        hospital_header,
        patient_name_input,
        ft.Divider(height=20, color="transparent"),

        ft.Text("⏳ Time-Based Services", size=18, weight=ft.FontWeight.BOLD, color="#64748B"),
        *time_services,

        ft.Divider(height=10, color="transparent"),
        ft.Text("🔢 Fixed / Quantity Services", size=18, weight=ft.FontWeight.BOLD, color="#64748B"),
        *fixed_services,

        ft.Divider(height=10, color="transparent"),
        ft.Text("📋 Custom Bills", size=18, weight=ft.FontWeight.BOLD, color="#64748B"),
        medicine_input,
        investigation_input,
        others_input,

        ft.Divider(height=20, color="transparent"),
        ft.Container(
            bgcolor="#FFFFFF",
            padding=20,
            border_radius=15,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color="#E2E8F0", offset=ft.Offset(0, 4)),
            content=ft.Column([
                grand_total_display,
                ft.Divider(color="transparent", height=10),
                calc_btn,
                reset_btn
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ),

        ft.Divider(height=20, color="transparent"),
        ft.Row([credit_text], alignment=ft.MainAxisAlignment.CENTER)
    )


if __name__ == "__main__":
    ft.app(target=main)