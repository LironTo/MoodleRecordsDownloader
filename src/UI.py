import asyncio
import os
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from playwright.async_api import async_playwright

USERNAME = ""
PASSWORD = ""
MOODLE_LOGIN_URL = "https://moodle.bgu.ac.il/moodle/login/index.php"
PROFILE_URL = "https://moodle.bgu.ac.il/moodle/user/profile.php"
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class BGUTubeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BGU Tube")
        self.root.resizable(False, False)
        self.course_vars = []

        # Logo
        try:
            self.logo_img = ImageTk.PhotoImage(Image.open("../Media/Logo.png").resize((180, 180)))
            self.logo = Label(root, image=self.logo_img)
            self.logo.pack(pady=10)
        except:
            self.logo = Label(root, text="BGU Tube", font=("Arial", 24, "bold"))
            self.logo.pack(pady=10)

        # Login fields
        self.user_label = Label(root, text="שם משתמש", font=("Arial", 12), anchor="w")
        self.user_entry = Entry(root, font=("Arial", 14))
        self.pass_label = Label(root, text="סיסמה", font=("Arial", 12), anchor="w")
        self.pass_entry = Entry(root, show="•", font=("Arial", 14))

        try:
            from Media.LoginInfo import USERNAME, PASSWORD
            self.user_entry.insert(0, USERNAME)
            self.pass_entry.insert(0, PASSWORD)
        except:
            pass

        self.login_btn = Button(root, text="התחבר", font=("Arial", 14), command=self.on_login)

        # Scrollable Checkbutton list
        self.course_frame = Frame(root)
        self.canvas = Canvas(self.course_frame)
        self.scrollbar = Scrollbar(self.course_frame, orient=VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)
        self.canvas.configure(bg="white")
        self.scrollable_frame.configure(bg="white")
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # Labels and buttons
        self.log_out = Button(self.root, text="התנתק", font=("Arial", 14), command=self.logout)
        self.your_courses = Label(self.root, text="הקורסים שלך:", font=("Arial", 16))
        self.course_count = Label(self.root, text="", font=("Arial", 12))

        self.select_all_var = IntVar()
        self.select_all_chk = Checkbutton(
            self.root,
            text="בחר/י את כל הקורסים",
            variable=self.select_all_var,
            font=("Arial", 12),
            command=self.toggle_select_all
        )

        self.show_selected_btn = Button(
            self.root,
            text="הצג קורסים שנבחרו",
            font=("Arial", 12),
            command=self.show_selected_courses,
            state=DISABLED
        )

        self.login_page()

    def login_page(self):
        self.user_label.pack(fill="x", padx=50)
        self.user_entry.pack(pady=5, padx=50, fill="x")
        self.pass_label.pack(fill="x", padx=50)
        self.pass_entry.pack(pady=5, padx=50, fill="x")
        self.login_btn.pack(pady=20)

    def clean_up(self):
        self.user_label.pack_forget()
        self.user_entry.pack_forget()
        self.pass_label.pack_forget()
        self.pass_entry.pack_forget()
        self.login_btn.pack_forget()
        self.course_frame.pack_forget()
        self.course_count.pack_forget()
        self.log_out.pack_forget()
        self.your_courses.pack_forget()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.course_vars.clear()
        self.select_all_chk.pack_forget()
        self.show_selected_btn.pack_forget()
        self.select_all_var.set(0)
        print("[DEBUG] clean_up called, disabling show_selected_btn")

    def on_login(self):
        global USERNAME, PASSWORD
        USERNAME = self.user_entry.get()
        PASSWORD = self.pass_entry.get()
        self.login_btn.config(state=DISABLED)
        self.root.after(100, lambda: asyncio.run(self.login_and_fetch_courses()))

    async def login_and_fetch_courses(self):
        async with async_playwright() as p:
            print("[INFO] Launching browser...")
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                print("[INFO] Navigating to login page...")
                await page.goto(MOODLE_LOGIN_URL)
                await page.fill('#login_username', USERNAME)
                await page.fill('#login_password', PASSWORD)
                await page.click("input[type='submit']")
                await page.wait_for_timeout(3000)

                print("[INFO] Navigating to public profile...")
                await page.goto(PROFILE_URL)
                await page.wait_for_timeout(1000)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)

                print("[INFO] Collecting course links...")
                links = await page.locator("a[href*='user/view.php'][href*='course=']").all()
                seen = set()
                course_urls = []

                for a in links:
                    title = (await a.inner_text()).strip()
                    href = await a.get_attribute("href")

                    if not href or not title or "course=" not in href:
                        continue

                    course_id = href.split("course=")[-1].split("&")[0]
                    course_url = f"https://moodle.bgu.ac.il/moodle/course/view.php?id={course_id}"

                    if course_url in seen:
                        continue

                    seen.add(course_url)
                    course_urls.append((title, course_url))

                print(f"[INFO] Total courses found: {len(course_urls)}")

                self.clean_up()
                self.your_courses.pack(fill="x", padx=50)
                self.select_all_chk.pack()
                self.course_frame.pack(pady=10, padx=20, fill=BOTH, expand=True)

                for title, url in course_urls:
                    var = IntVar()
                    chk = Checkbutton(
                        self.scrollable_frame,
                        text=title.strip(),
                        variable=var,
                        font=("Arial", 12),
                        anchor="w",
                        command=self.update_download_button_state
                    )
                    chk.pack(fill="x", padx=10, pady=2, anchor="w")
                    self.course_vars.append((var, (title, url)))

                self.course_count.config(text=f"סה\"כ קורסים שנמצאו: {len(course_urls)}")
                self.course_count.pack(pady=5)
                self.log_out.pack(pady=10)


                self.show_selected_btn.pack(pady=5)

            except Exception as e:
                print("[ERROR] Failed to login or fetch courses:", e)
                messagebox.showerror("שגיאה", f"התחברות נכשלה: {e}")

            await browser.close()
            self.login_btn.config(state=NORMAL)

    def logout(self):
        print("[INFO] User logged out")
        self.clean_up()
        self.login_page()

    def update_download_button_state(self):
        # הפעלת הכפתור רק אם יש קורס אחד לפחות מסומן
        any_selected = any(var.get() for var, _ in self.course_vars)
        if any_selected:
            self.show_selected_btn.config(state=NORMAL)
        else:
            self.show_selected_btn.config(state=DISABLED)

    def show_selected_courses(self):
        selected = [title for var, (title, _) in self.course_vars if var.get()]
        if not selected:
            messagebox.showinfo("לא נבחרו קורסים", "לא נבחרו קורסים להורדה.")
            return

        # יצירת טקסט להצגה
        selected_text = "\n".join(selected)
        messagebox.showinfo("קורסים שנבחרו", f"הקורסים שנבחרו:\n\n{selected_text}")

    def toggle_select_all(self):
        new_state = self.select_all_var.get()
        for var, _ in self.course_vars:
            var.set(new_state)
        self.update_download_button_state()


if __name__ == '__main__':
    root = Tk()
    app = BGUTubeApp(root)
    root.mainloop()
