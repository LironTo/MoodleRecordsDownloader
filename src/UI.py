# BGU Tube - ממשק גרפי עם Playwright

import asyncio
import os
import subprocess
from tkinter import *
from tkinter import messagebox
from playwright.async_api import async_playwright
from PIL import Image, ImageTk

USERNAME = ""
PASSWORD = ""
MOODLE_LOGIN_URL = "https://moodle.bgu.ac.il/moodle/login/index.php"
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ממשק גרפי
class BGUTubeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BGU Tube")
        self.root.geometry("400x700")
        self.root.resizable(False, False)
        self.logo_img = ImageTk.PhotoImage(Image.open("../Media/Logo.png").resize((180, 180)))
        try:
            self.logo = Label(root, image=self.logo_img)
            self.logo.pack(pady=10)
        except:
            self.logo = Label(root, text="BGU Tube", font=("Arial", 24, "bold"))
            self.logo.pack(pady=10)
        self.user_label = Label(root, text="שם משתמש", font=("Arial", 12), anchor="w")
        self.user_entry = Entry(root, font=("Arial", 14))
        self.pass_label = Label(root, text="סיסמה", font=("Arial", 12), anchor="w")
        self.pass_entry = Entry(root, show="•" , font=("Arial", 14))
        self.login_btn = Button(root, text="התחבר", font=("Arial", 14), command=self.on_login)
        self.courses_box = Listbox(root, font=("Arial", 12), width=800)
        self.log_out = Button(self.root, text="התנתק", font=("Arial", 14), command=self.logout)
        self.your_courses = Label(self.root, text="הקורסים שלך:", font=("Arial", 16))
        self.login_page()

    def login_page(self):
        self.root.geometry("400x400")
        # תיבות טקסט
        # תווית לשם משתמש
        self.user_label.pack(fill="x", padx=50)
        self.user_entry.pack(pady=5, padx=50, fill="x")

        # תווית לסיסמה
        self.pass_label.pack(fill="x", padx=50)
        self.pass_entry.pack(pady=5, padx=50, fill="x")

        self.login_btn.pack(pady=20)


    def clean_up(self):
        self.user_label.pack_forget()
        self.user_entry.pack_forget()
        self.pass_label.pack_forget()
        self.pass_entry.pack_forget()
        self.login_btn.pack_forget()
        self.courses_box.pack_forget()
        self.courses_box.delete(0, END)
        self.log_out.pack_forget()
        self.your_courses.pack_forget()

    def on_login(self):
        global USERNAME, PASSWORD
        USERNAME = self.user_entry.get()
        PASSWORD = self.pass_entry.get()
        self.login_btn.config(state=DISABLED)
        self.root.after(100, lambda: asyncio.run(self.login_and_fetch_courses()))

    async def login_and_fetch_courses(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            try:
                await page.goto(MOODLE_LOGIN_URL)
                await page.fill('#login_username', USERNAME)
                await page.fill('#login_password', PASSWORD)
                await page.click("input[type='submit']")
                await page.wait_for_timeout(3000)

                course_links = await page.locator("a[href*='course/view.php']").all()
                course_urls = list(set([(await a.inner_text(), await a.get_attribute("href")) for a in course_links]))

                for title, url in course_urls:
                    self.courses_box.insert(END, f"{title.strip()} | {url}")

                self.clean_up()

                self.your_courses.pack(fill="x", padx=50)
                self.courses_box.pack(pady=10)

                self.root.geometry("1000x700")

                for title, url in course_urls:
                    self.courses_box.insert(END, f"{title.strip()} | {url}")

                self.log_out.pack(pady=10)


            except Exception as e:
                messagebox.showerror("שגיאה", f"התחברות נכשלה: {e}")

            await browser.close()
            self.login_btn.config(state=NORMAL)

    def logout(self):
        self.clean_up()
        self.login_page()

# הפעלת התוכנה
if __name__ == '__main__':
    root = Tk()
    app = BGUTubeApp(root)
    root.mainloop()
