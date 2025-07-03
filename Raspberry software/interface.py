
import sys
from PyQt5.QtGui import QFont
from datetime import datetime
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame, QSizePolicy, QSpacerItem, QToolButton, QStackedLayout,
    QMenu, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QIcon, QColor, QPalette
from datetime import datetime, timedelta
import pymysql
import pymysql.cursors


# Utility function to scale pixel values based on current screen resolution
def scaled(val):
    return int(val * SCALE)


# Utility function to generate a scaled QFont based on current DPI scaling
def scaled_font(pt):
    f = QFont()
    f.setPointSizeF(pt * SCALE)
    return f


# Selected Room
room_name = 'H102'


# List of all PC rooms 
ALL_PC_ROOMS = [
    "E204", "H101", "H201", "H203", "H204","H207","H209", "N101", "N102",
]


# List of all lecture rooms
ALL_LECTURE_ROOMS = [
    "E001", "E009", "E010", "E101", "E107", "E108", "E109",
    "H002", "H003", "H004", "H008", "H030", "H031",
    "H102", "H103", "H104","H108b", "H130", "H131", "H202", "H210","H213a","H213b","H215",
    "H222", "H318", "N001", "N002", "N003", "N004", "N103","N104",
    "N111", "N112", "N113", "N114", "N117", "N118", "N119"
]


# Managing database connection and queries related to the lesson schedule
class DatabaseManager:

    def __init__(self):
        self.conn = pymysql.connect(
            host="49.13.235.112",
            user="DHBWTABLETTE",
            password="DHBW2025internationals#",
            database="EDT",
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()

        
        #  Query the schedule for a given room on the current day.
    def get_schedule_for_room(self, room_name: str):
        now = datetime.now().date()

        query = """
        SELECT startDate, endDate, location, summary, category
        FROM lessons
        WHERE DATE(startDate) = %s AND location LIKE %s;
        """
        self.cursor.execute(query, (now, f"%{room_name}%"))
        raw_results = self.cursor.fetchall()

        schedule = []
        for row in raw_results:
            print(row)
            start = row["startDate"]
            end = row["endDate"]
            summary = row["summary"]

            # Extract course title and professor info from summary
            summary_parts = summary.split('[')
            if len(summary_parts) > 1:
                title = summary_parts[0].strip()
                prof = summary_parts[1].strip(']').replace('\\', '').replace(',', '')
            else:
                title = summary
                prof = "Unknown"

            schedule.append({
                "date": start.strftime("%Y-%m-%d"),
                "time": f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}",
                "title": title,
                "prof": prof
            })

        return schedule
    


        # Query all rooms that are currently occupied at the moment.
    def get_currently_busy_rooms(self):
        now = datetime.now()

        query = """
            SELECT DISTINCT location
            FROM lessons
            WHERE %s BETWEEN startDate AND endDate;
        """
        self.cursor.execute(query, (now,))
        results = self.cursor.fetchall()

        busy_rooms = set()
        for row in results:
            loc = row["location"] or ""
            room_names = self.extract_room_names(loc)
            busy_rooms.update(room_names)   
        return busy_rooms 



        # Extract valid room codes (e.g., H202, N117) from the given location string.
    def extract_room_names(self, location_str):
        import re
        return re.findall(r"\b[A-Z]\d{3}[a-zA-Z]?\b", location_str)


        # Close the database cursor and connection.
    def close(self):
        self.cursor.close()
        self.conn.close()




# Custom QWidget to display a room as a card with name label.
class RoomCard(QWidget):
    def __init__(self, room_name):
        super().__init__()
        self.setFixedHeight(scaled(100))
        self.setStyleSheet(f"""
            background-color: white;
            border-radius: {scaled(10)}px;
            border: 1px solid #ccc;
            margin: {scaled(5)}px;
            padding: {scaled(10)}px;
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(scaled(20), scaled(15), scaled(20), scaled(15))
        self.label = QLabel(room_name)
        self.label.setStyleSheet(f"font-weight: bold; font-size: {scaled(16)}px;")
        layout.addWidget(self.label)



# SidePanel: Slide-in panel for selecting available rooms
class SidePanel(QWidget):
    def __init__(self, parent=None, stack=None, detail_page=None):
        super().__init__(parent)
        self.stack = stack
        self.detail_page = detail_page

        # Room list UI for available rooms
        self.room_list_widget = QListWidget()
        self.room_list_widget.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
            }}
            QListWidget::item {{
                background-color: transparent;
                margin: {scaled(5)}px;
            }}
            QListWidget::item:selected {{
                background-color: #a0c4ff;
                color: black;
            }}
        """)

        # Ensure detail_page has a layout and room list
        if self.detail_page.layout() is None:
            self.detail_page.setLayout(QVBoxLayout())
        self.detail_page.layout().addWidget(self.room_list_widget)

        # General styling
        self.setMinimumWidth(scaled(300))
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setStyleSheet("background-color: #f9f9f9; color: #222;")

        # Stack with two pages: main (select type) and detail (room list)
        self.stack = QStackedLayout(self)
        self.main_page = QWidget()
        self.detail_page = QWidget()

        self.build_main_page()
        self.build_detail_page()

        self.stack.addWidget(self.main_page)
        self.stack.addWidget(self.detail_page)


    # Adjust font sizes dynamically on resize
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_font_sizes()

    def adjust_font_sizes(self):
        base_width = self.width()
        font_large = base_width // 10
        font_medium = base_width // 15
        font_small = base_width // 25

        self.pc_button.setStyleSheet(f"font-size: {scaled(font_medium)}px; padding: {scaled(20)}px; background-color: #ddd; color: black; border-radius: {scaled(10)}px;")
        self.lecture_button.setStyleSheet(f"font-size: {scaled(font_medium)}px; padding: {scaled(20)}px; background-color: #ddd; color: black; border-radius: {scaled(10)}px;")
        self.close_button.setStyleSheet(f"font-size: {scaled(font_small)}px;padding: {scaled(15)}px;")
        self.room_list_title.setStyleSheet(f"font-size: {scaled(font_large)}px;")
        self.back_button.setStyleSheet(f"font-size: {scaled(font_small)}px;padding: {scaled(15)}px;")
        self.title.setStyleSheet(f"font-size: {scaled(font_large)}px;")


    # Build the main page: choose between PC room or Lecture room
    def build_main_page(self):
        layout = QVBoxLayout(self.main_page)
        layout.setContentsMargins(scaled(30), scaled(30), scaled(30), scaled(30))
        layout.setSpacing(scaled(20))

        self.title = QLabel("Choose room type")
        self.title.setFont(scaled_font(28))
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        self.pc_button = QPushButton("PC Room")
        layout.addWidget(self.pc_button)
        self.pc_button.clicked.connect(lambda: self.show_available_rooms("PC"))


        self.lecture_button = QPushButton("Lecture Room")
        layout.addWidget(self.lecture_button)
        layout.addSpacing(scaled(30))
        self.lecture_button.clicked.connect(lambda: self.show_available_rooms("Lecture"))


        self.close_button = QPushButton("X")
        layout.addWidget(self.close_button, alignment=Qt.AlignBottom)



    # Build the detail page that lists available rooms
    def build_detail_page(self):
        layout = QVBoxLayout(self.detail_page)
        layout.setContentsMargins(scaled(20), scaled(20), scaled(20), scaled(20))
        layout.setSpacing(scaled(15))

        self.room_list_title = QLabel("Available Rooms")
        self.room_list_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.room_list_title)

        self.room_list_widget = QListWidget()
        layout.addWidget(self.room_list_widget)

        self.back_button = QPushButton("← Back")
        layout.addWidget(self.back_button)

        self.back_button.clicked.connect(self.back_to_main)

    # Query and display available rooms based on type
    def show_available_rooms(self, room_type):
        self.room_list_widget.clear()
    
        from main import DatabaseManager
        db = DatabaseManager()
        busy_rooms = db.get_currently_busy_rooms()
        db.close()

        # Filter available rooms            
        if room_type == "PC":
            available = sorted(room for room in ALL_PC_ROOMS if room not in busy_rooms)
        else:
            available = sorted(room for room in ALL_LECTURE_ROOMS if room not in busy_rooms)
        

        # Display room cards or fallback message
        if not available:
            item = QListWidgetItem("No available rooms at the moment.")
            self.room_list_widget.addItem(item)
        else:
            for room in available:
                item = QListWidgetItem()
                card = RoomCard(room)
                item.setSizeHint(card.sizeHint())
                self.room_list_widget.addItem(item)
                self.room_list_widget.setItemWidget(item, card)
        self.stack.setCurrentWidget(self.detail_page)



    # Go back to the room type selection page
    def back_to_main(self):
        self.stack.setCurrentWidget(self.main_page)


# MenuPanel: Slide-in side menu for Login / Settings
class MenuPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(scaled(300))
        self.setAutoFillBackground(True)

        # Background styling
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#ffffff"))
        self.setPalette(palette)
        self.setStyleSheet("background-color: #ffffff; color: #222;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(scaled(20), scaled(20), scaled(20), scaled(20))
        layout.setSpacing(scaled(15))

        # Title label
        title = QLabel("Menu")
        title.setMinimumHeight(scaled(70))
        title.setFont(scaled_font(40))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Buttons: login and settings
        self.login_button = QPushButton("Login")
        self.settings_button = QPushButton("Settings")
        for btn in [self.login_button, self.settings_button]:
            btn.setMinimumHeight(scaled(50))
            btn.setFont(scaled_font(28))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #dddddd;
                    border-radius: {scaled(8)}px;
                    color: black;
                }}
                QPushButton:hover {{
                    background-color: #cccccc;
                }}
            """)
            layout.addWidget(btn)

        layout.addStretch()


        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.setFont(scaled_font(25))
        self.close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #ffffff;
                border: none;
                color: #555;
            }}
            QPushButton:hover {{
                color: #000;
            }}
        """)
        layout.addWidget(self.close_button, alignment=Qt.AlignBottom)



class RoomUI(QWidget):


        # Update footer background color based on busy status
    def update_footer_style(self, is_busy):
        if is_busy:
            self.footer_frame.setStyleSheet("background-color: #aa0000;")
        else:
            self.footer_frame.setStyleSheet("background-color: #004400;")

    def __init__(self, scale=1.0):
            self.scale = scale
            super().__init__()

            # Main stacked layout for switching views
            self.stack = QStackedLayout()

            # A shared detail page used in side panel
            self.detail_page = QWidget()

            # Side panel for extra room details
            self.side_panel = SidePanel(stack=self.stack, detail_page=self.detail_page)

            self.setWindowTitle("Room Display Panel v3")
            self.dark_mode_enabled = True
            
            # Base layout setup
            self.setLayout(self.stack)  
            self.base_container = QWidget()
            self.stack.addWidget(self.base_container)

            # Semi-transparent dark overlay for modal effects
            self.overlay = QWidget()
            self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 100);")
            self.overlay.hide()
            self.stack.addWidget(self.overlay)

            # Add side panel to the stack
            self.side_panel = SidePanel(stack=self.stack, detail_page=self.detail_page)
            self.side_panel.hide()
            self.stack.addWidget(self.side_panel)

            # Add menu panel for settings or navigation
            self.menu_panel = MenuPanel()
            self.menu_panel.hide()
            self.stack.addWidget(self.menu_panel)

            # Load schedule data on startup
            self.schedule_data = []
            self.refresh_schedule_from_db()

            # Build UI layout and initialize styles
            self.build_ui()
            self.set_dark_mode()
            self.refresh_ui()

            # Timer to refresh time and status every second
            self.timer = QTimer()
            self.timer.timeout.connect(self.refresh_ui)
            self.timer.start(1000)

            # Timer to refresh DB every 5 minutes
            self.db_refresh_timer = QTimer()
            self.db_refresh_timer.timeout.connect(self.refresh_schedule_from_db)
            self.db_refresh_timer.start(300000)

            # Hook up UI interaction events
            self.side_panel.close_button.clicked.connect(self.hide_side_panel)
            self.overlay.mousePressEvent = self.handle_overlay_click
            self.menu_panel.close_button.clicked.connect(self.hide_menu_panel)

            # Fullscreen display
            self.showFullScreen()

    # Build the main UI layout and widgets
    def build_ui(self):
        # Main layout for the entire screen
        self.main_layout = QVBoxLayout(self.base_container)
        self.main_layout.setContentsMargins(scaled(30), scaled(30), scaled(30), scaled(30))
        self.main_layout.setSpacing(scaled(20))

        # Top row: clock, date, gear button 
        top_row = QHBoxLayout()

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignLeft)

        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignLeft)
        self.date_label.setStyleSheet(f"font-size: {scaled(26)}px;")

        time_box = QVBoxLayout()
        time_box.addWidget(self.time_label)
        time_box.addWidget(self.date_label)
        time_box.addSpacing(scaled(30))

        self.gear_button = QToolButton()
        self.gear_button.setText("☰")
        self.gear_button.setAutoRaise(True)
        self.gear_button.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.gear_button.setStyleSheet(f"font-size: {scaled(30)}px;")
        self.gear_button.clicked.connect(self.show_menu_panel)

        top_row.addLayout(time_box)
        top_row.addSpacing(scaled(30))
        top_row.addWidget(self.gear_button, 0, Qt.AlignTop)
        self.main_layout.addLayout(top_row)

        # Middle row: room info (left) and schedule (right)
        middle_row = QHBoxLayout()

        # Left side: room status, prof, time
        left_content = QVBoxLayout()
        self.room_title_label = QLabel(f"{room_name}")
        self.room_title_label.setAlignment(Qt.AlignLeft)
        self.room_title_label.setStyleSheet(f"font-size: {scaled(100)}px; font-weight: bold;")
        
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignLeft)
        font_size = self.width() // 20
        self.status_label.setWordWrap(True)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.prof_label = QLabel()

        self.time_range_label = QLabel()

        self.prof_info_row = QHBoxLayout()
        self.prof_info_row.addWidget(self.prof_label)
        self.prof_info_row.addSpacing(scaled(5))
        self.prof_info_row.addWidget(self.time_range_label)

        left_content.addWidget(self.room_title_label)
        left_content.addSpacing(scaled(20))
        left_content.addWidget(self.status_label)
        left_content.addSpacing(scaled(10))
        left_content.addLayout(self.prof_info_row)
        left_content.addSpacing(scaled(30))

        left_container = QFrame()
        left_container.setLayout(left_content)
        left_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        middle_row.addWidget(left_container, 3)

        # Right side: coming up courses list
        right_section = QVBoxLayout()
        self.coming_up_label = QLabel("Coming up next:")
        self.coming_up_label.setStyleSheet(f"font-size: {scaled(32)}px; font-weight: bold;")
        right_section.addWidget(self.coming_up_label)
        right_section.addSpacing(15)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scroll_content = QWidget()
        self.schedule_layout = QVBoxLayout(self.scroll_content)
        self.schedule_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        right_section.addWidget(self.scroll_area)

        right_container = QWidget()
        right_container.setLayout(right_section)
        right_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        middle_row.addWidget(right_container, 1)

        self.main_layout.addLayout(middle_row)

        # Footer row: neighbor room info + find button
        self.footer_frame = QFrame()
        self.footer_frame.setMinimumHeight(scaled(100))
        self.footer_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.footer_layout = QHBoxLayout(self.footer_frame)
        self.footer_layout.setContentsMargins(scaled(30), scaled(10), scaled(30), scaled(10))

        # Left side: left neighbor room
        left_layout = QVBoxLayout()
        left_layout.setSpacing(scaled(5))
        self.left_label = QLabel("")
        self.left_label.setStyleSheet(f"color: black;font-size: {scaled(36)}px;")
        left_layout.addWidget(self.left_label)

        self.status_left = QLabel("")
        self.status_left.setStyleSheet(f"color: black;font-size: {scaled(20)}px;")
        self.status_left.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.status_left)

        self.footer_layout.addLayout(left_layout)

        self.footer_layout.addStretch(1)


        # Center: find another space button 
        self.find_button = QPushButton("Find another space")
        self.find_button.setStyleSheet(f"background: none; border: none; font-size: {scaled(30)}px; color: black;")
        self.find_button.setCursor(Qt.PointingHandCursor)
        self.footer_layout.addWidget(self.find_button)

        self.footer_layout.addStretch(1)


        # Right side: right neighbor room
        right_layout = QVBoxLayout()
        right_layout.setSpacing(scaled(5))
        
        self.right_label = QLabel("")
        self.right_label.setStyleSheet(f"color: black;font-size: {scaled(36)}px;")
        right_layout.addWidget(self.right_label)
        self.status_right = QLabel("")
        self.status_right.setStyleSheet(f"color: black;font-size: {scaled(20)}px;")
        right_layout.addWidget(self.status_right)
        self.footer_layout.addLayout(right_layout)

        # Populate neighbor info
        self.update_footer_neighbors(f"{room_name}")

        self.main_layout.addWidget(self.footer_frame)

        self.find_button.clicked.connect(self.show_side_panel)


    # Database: fetch today's schedule
    def refresh_schedule_from_db(self):
        from main import DatabaseManager  
        db = DatabaseManager()
        self.schedule_data = db.get_schedule_for_room(room_name)
        db.close()

    # Slide-in Side Panel
    def show_side_panel(self):
        self.side_panel.back_to_main()  
        self.side_panel.show()
        self.overlay.show()
        self.animate_panel(True)
        self.side_panel.back_to_main() 


    def hide_side_panel(self, event=None):
        self.animate_panel(False)

    def animate_panel(self, showing):
        full_width = self.geometry().width()  
        full_height = self.geometry().height()
        start_x = full_width if showing else full_width - 400
        end_x = full_width - 400 if showing else full_width

        self.animation = QPropertyAnimation(self.side_panel, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(start_x, 0, 400, full_height))
        self.animation.setEndValue(QRect(end_x, 0, 400, full_height))
        self.animation.start()

        if showing:
            self.side_panel.show()
            self.overlay.show()
            self.overlay.raise_()
            self.side_panel.raise_()
        else:
            def after_hide():
                self.side_panel.hide()
                self.overlay.hide()
            self.animation.finished.connect(after_hide)            
 
    # Slide-in Menu Panel
    def show_menu_panel(self):
        self.menu_panel.show()
        self.overlay.show()
        self.animate_menu_panel(True)
        self.menu_panel.raise_()
        self.menu_panel.setFocus()

    def hide_menu_panel(self, event=None):
        self.animate_menu_panel(False)

    def animate_menu_panel(self, showing):
        full_width = self.geometry().width()
        full_height = self.geometry().height()
        start_x = full_width if showing else full_width - self.menu_panel.width()
        end_x = full_width - self.menu_panel.width() if showing else full_width

        self.menu_animation = QPropertyAnimation(self.menu_panel, b"geometry")
        self.menu_animation.setDuration(300)
        self.menu_animation.setStartValue(QRect(start_x, 0, self.menu_panel.width(), full_height))
        self.menu_animation.setEndValue(QRect(end_x, 0, self.menu_panel.width(), full_height))
        self.menu_animation.start()

        if showing:
            self.menu_panel.raise_()
            self.overlay.raise_()
        else:
            def after_hide():
                self.menu_panel.hide()
                self.overlay.hide()
            self.menu_animation.finished.connect(after_hide)


        # UI refresh logic: handle current/upcoming courses
    def refresh_ui(self):
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        now_minutes = now.hour * 60 + now.minute

        
        # Update clock and date
        self.time_label.setText(now.strftime("%H:%M"))
        self.date_label.setText(now.strftime("%d/%m/%Y"))

        # Filter today's schedule
        today_courses = [c for c in self.schedule_data if c.get("date") == today_str]

        # Sort courses by start time
        def extract_start_minutes(course):
            start_str = course["time"].split(" - ")[0]
            h, m = map(int, start_str.split(":"))
            return h * 60 + m

        today_courses.sort(key=extract_start_minutes)

        current_course = None
        upcoming_courses = []

        for course in today_courses:
            start_str, end_str = course["time"].split(" - ")
            start_h, start_m = map(int, start_str.split(":"))
            end_h, end_m = map(int, end_str.split(":"))
            start_min = start_h * 60 + start_m
            end_min = end_h * 60 + end_m

            if start_min <= now_minutes < end_min:
                current_course = course
            elif now_minutes < start_min:
                upcoming_courses.append(course)

        # Display course info or room available
        if current_course:
            title = current_course["title"]
            is_exam = "KLAUSUR" in title.upper()

            if is_exam:
                # Exam mode: distinct styling
                exam_name = title.split("KLAUSUR")[-1].strip(":：").strip()
                self.setStyleSheet("background-color: #f38686; color: black;")
                self.status_label.setText(f" {exam_name}")
                self.status_label.setStyleSheet(f"color: black; font-weight: bold;; font-size: {scaled(100)}px")
                self.prof_label.hide()
                self.time_range_label.setText(current_course["time"])
                self.time_range_label.setStyleSheet(f"color: black;; font-size: {scaled(100)}px")
                self.footer_frame.hide()
                self.coming_up_label.hide()
                self.scroll_area.hide()
                while self.schedule_layout.count():
                    item = self.schedule_layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
            else:
                # Normal course
                self.status_label.setText(title)
                self.prof_label.setText(current_course.get("prof", ""))
                self.time_range_label.setText(current_course["time"])
                self.footer_frame.setStyleSheet("background-color: #c83232;")
                self.scroll_area.show()
                self.coming_up_label.show()
            
        

        else:
            # No current class
            self.status_label.setText("Room Available")
            self.prof_label.setText("")
            self.time_range_label.setText("")
            self.footer_frame.setStyleSheet("background-color: #ddffdd;")


        if not current_course and not upcoming_courses and today_courses:
            self.status_label.setText("Room Available")
            self.prof_label.setText("")
            self.time_range_label.setText("")
            self.footer_frame.setStyleSheet("background-color: #ddffdd;")
            self.clear_schedule_area()
            return

        # Populate upcoming courses panel
        self.clear_schedule_area()
        for item in upcoming_courses:
            box = QFrame()
            box.setFrameShape(QFrame.StyledPanel)
            layout = QVBoxLayout()
            layout.addWidget(QLabel(f"🕒 {item['time']}"))
            title_label = QLabel(f"📚 {item['title']}")
            title_label.setFont(scaled_font(20))
            title_label.setWordWrap(True)
            title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            layout.addWidget(title_label)

            layout.addWidget(QLabel(f"👤 {item['prof']}"))
            box.setLayout(layout)
            self.schedule_layout.addWidget(box)

        self.schedule_layout.addItem(QSpacerItem(10, 50, QSizePolicy.Minimum, QSizePolicy.Expanding))



    # Resize hook: adjust font sizes and layout
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_font_sizes()
        self.overlay.setGeometry(self.rect())   
        if self.side_panel.isVisible():
            self.side_panel.setGeometry(QRect(self.width() - 400, 0, 400, self.height()))

        
        base_width = self.width()
        self.time_label.setStyleSheet(f"font-size: {base_width//30}px; font-weight: bold;")
        self.status_label.setStyleSheet(f"font-size: {base_width//20}px; font-weight: bold;")
        self.prof_label.setStyleSheet(f"font-size: {base_width//40}px;")
        self.time_range_label.setStyleSheet(f"font-size: {base_width//40}px;")

    # Handle overlay click: close menu or side panel
    def handle_overlay_click(self, event):
        if self.menu_panel.isVisible():
            self.hide_menu_panel()
        elif self.side_panel.isVisible():
            if self.side_panel.stack.currentWidget() == self.side_panel.detail_page:
                self.side_panel.back_to_main()
            else:
                self.hide_side_panel()


     # Clear all widgets from the scroll area           
    def clear_schedule_area(self):
        while self.schedule_layout.count():
            item = self.schedule_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                del item  


    # Dynamically adjust font sizes (currently unused)
    def adjust_font_sizes(self):
        base_width = self.width()
        font_large = base_width // 20
        font_medium = base_width // 30
        font_small = base_width // 40


    # Get neighbor rooms and their statuses
    def get_neighbors_status(self, room_name, busy_rooms):
        if room_name in ALL_PC_ROOMS:
            room_list = ALL_PC_ROOMS
        elif room_name in ALL_LECTURE_ROOMS:
            room_list = ALL_LECTURE_ROOMS
        else:
            return (None, None), (None, None)

        idx = room_list.index(room_name)

        left_neighbor = room_list[idx - 1] if idx > 0 else None
        right_neighbor = room_list[idx + 1] if idx < len(room_list) - 1 else None

        left_status = "Busy" if left_neighbor in busy_rooms else "Available" if left_neighbor else ""
        right_status = "Busy" if right_neighbor in busy_rooms else "Available" if right_neighbor else ""

        return (left_neighbor, left_status), (right_neighbor, right_status)
    

    # Update footer with neighbor room info
    def update_footer_neighbors(self, room_name):
        from main import DatabaseManager
        db = DatabaseManager()
        busy_rooms = db.get_currently_busy_rooms()
        db.close()
        (left_room, left_status), (right_room, right_status) = self.get_neighbors_status(room_name, busy_rooms)

        self.left_label.setText(f"← {left_room if left_room else 'N/A'}")
        self.status_left.setText(left_status)

        self.right_label.setText(f"{right_room if right_room else 'N/A'} →")
        self.status_right.setText(right_status)


    # Toggle between light and dark UI themes
    def toggle_theme(self):
        self.dark_mode_enabled = not self.dark_mode_enabled
        if self.dark_mode_enabled:
            self.set_dark_mode()
        else:
            self.set_light_mode()


    # Apply dark mode style
    def set_dark_mode(self):
        self.setStyleSheet(f"""
            QWidget {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #1e1e1e, stop:1 #2e2e2e);
        color: #e0e0e0;
        font-size: {int(24 * SCALE)}px;
    }}
            QScrollArea {{
                background-color: #1e1e1e;
            }}
            QFrame[frameShape="StyledPanel"] {{
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: {scaled(8)}px;
            }}
            QLabel {{
                color: #f0f0f0;
            }}
            QPushButton {{
                color: #cccccc;
                background-color: transparent;
                border: none;
            }}
            QPushButton:hover {{
                color: #ffffff;
                text-decoration: underline;
            }}
            QToolButton {{
                font-size: {int(28 * SCALE)}px;
                color: #aaaaaa;
                border: none;
            }}
            QToolButton:hover {{
                color: #ffffff;
            }}
        """)


    # Apply light mode style
    def set_light_mode(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #000000;
                font-size: 24 * SCALE px;
            }
            QScrollArea {
                background-color: #f5f5f5;
            }
            QFrame[frameShape="StyledPanel"] {
                background-color: #eeeeee;
                border: 1px solid #ccc;
                border-radius: {scaled(8)}px;
            }
            QLabel {
                color: #000000;
            }
            QPushButton {
                color: #000000;
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                color: #222222;
                text-decoration: underline;
            }
            QToolButton {
                font-size: 28 * SCALE px;
                color: #222222;
                border: none;
            }
            QToolButton:hover {
                color: #000000;
            }
        """)

if __name__ == "__main__":

    # Initialize the Qt application
    app = QApplication(sys.argv)

    # Get screen resolution to support responsive scaling
    screen = app.primaryScreen()
    size = screen.size()
    screen_width, screen_height = size.width(), size.height()

    # Define baseline resolution for scaling reference
    BASE_WIDTH = 1920
    BASE_HEIGHT = 1080

    # Compute scale factor (whichever dimension is smaller)
    scale_w = screen_width / BASE_WIDTH
    scale_h = screen_height / BASE_HEIGHT
    SCALE = min(scale_w, scale_h)

    # Instantiate the main UI and show in full screen
    ui = RoomUI()
    ui.showFullScreen()

    # Start the Qt event loop
    sys.exit(app.exec())
