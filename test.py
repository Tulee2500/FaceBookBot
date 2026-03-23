"""
FB Scheduler v3.3
Fix: comment chỉ ảnh (không cần text)
Fix: upload ảnh bài đăng không hiện Windows file dialog
Fix: bỏ qua bài do chính mình đăng khi comment
UI: Glassmorphism + Dark Dashboard
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time, random, threading, queue, os
from datetime import datetime
import schedule
import pyperclip

# =====================================================================
# DỮ LIỆU MẶC ĐỊNH
# =====================================================================
DEFAULT_GROUPS = [
    "https://www.facebook.com/groups/494791101712107/",
    "https://www.facebook.com/groups/1577663229152837/",
    "https://www.facebook.com/groups/congdonggiaoviendaytieuhoc/",
    "https://www.facebook.com/groups/794046182208692/",
    "https://www.facebook.com/groups/501926661273895/",
    "https://www.facebook.com/groups/CTLGVTH/",
    "https://www.facebook.com/groups/872975716161260/",
    "https://www.facebook.com/groups/803618666681542/",
    "https://www.facebook.com/groups/498819267631822/",
    "https://www.facebook.com/groups/208114459344784/",
    "https://www.facebook.com/groups/chungtoilagiaovientieuhocc/",
    "https://www.facebook.com/groups/1163248614989196/"
]

DEFAULT_POST_CONTENTS = [
    """
    SĂN SALE ĐẦU HÈ - COMBO THỜI KHÓA BIỂU & NHÃN VỞ GIÁ CỰC ÊM 🏷️🔥
    Cơ hội F5 góc học tập với chi phí "hạt dẻ" đây rồi cả nhà ơi! Combo siêu hot nhà Perfect Packs đã sẵn sàng lên kệ Shopee với cực nhiều ưu đãi.
    ✨ Giấy siêu xịn: C300 cao cấp, viết cực êm tay. ✨ Hình ảnh sắc nét: Màu sắc chuẩn chỉnh, không phai màu theo thời gian. ✨ Giao hàng thần tốc: Đóng gói cẩn thận, gửi hàng ngay trong ngày.
    👇 Mua ngay tại đây để nhận giá hời nhất: https://vn.shp.ee/akhdhST 📞 Liên hệ trực tiếp qua Zalo để nhận báo giá ưu đãi khi mua số lượng lớn: 0982 704 995 #sale #shopeevn #phukienhocsinh #nhanvodesign #thoikhoabieu #perfectpacks
    """,
    """
    SẮM ĐỒ DÙNG HỌC TẬP CHO BÉ - CHỌN COMBO CHUẨN ĐẸP TẠI PERFECT PACKS 🎁💥
    Ba mẹ đang tìm bộ nhãn vở và thời khóa biểu vừa bền, vừa đẹp cho con chuẩn bị vào năm học mới? Ghé ngay gian hàng của Perfect Packs nhé!
    💯 Chất liệu cao cấp: Giấy đanh, dày dặn, không dễ rách hay nhàu nát. 💯 Tiện lợi cho bé: Nhãn vở bám dính chắc chắn, không bị bong tróc mép sau thời gian dài sử dụng. 💯 Mẫu mã đa dạng: Nhiều chủ đề dễ thương, tạo hứng thú cho bé mỗi khi mở sách vở.
    👉 Click ngay link Shopee để áp mã giảm giá và Freeship: https://vn.shp.ee/akhdhST 📞 Cần hỗ trợ đơn hỏa tốc hoặc tư vấn thêm, cứ hú Tú một tiếng nha: 0982 704 995 #shopeehaul #nhanvocute #thoikhoabieudep #perfectpacks #backtoschool #mevabe
    """,
    """
    GÓC HỌC TẬP "ĐỈNH CHÓP" VỚI COMBO THỜI KHÓA BIỂU & NHÃN VỞ ĐỘC QUYỀN 🎒✨
    Năm học mới sắp đến, rinh ngay bộ combo xịn xò từ Perfect Packs để mỗi ngày đi học là một ngày tràn đầy năng lượng nào!
    ✅ Thời khóa biểu giấy C300 siêu dày: Cầm cực chắc tay, viết bút dạ thoải mái không lo thấm mặt sau. ✅ Nhãn vở decal "thần thánh": Độ bám dính cực tốt, lột dán mượt mà trên mọi loại bìa sách/vở. ✅ Thiết kế độc quyền: Màu sắc tươi rói, hình ảnh sắc nét, dùng cả năm vẫn trông như mới.
    🛒 Chốt đơn ngay trên Shopee để nhận ưu đãi Freeship Extra: https://vn.shp.ee/akhdhST 💬 Các lớp cần làm mẫu riêng theo yêu cầu cứ nhắn trực tiếp cho Tú nhé! 📞 Hotline/Zalo: 0982 704 995 📍 Xem mẫu tại: 85tt3, KĐT Văn Phú, Hà Đông, Hà Nội. #thoikhoabieu #nhanvo #perfectpacks #dodunghoctap #combohoctap #backtoschool
    """
]

DEFAULT_COMMENTS = [
    """
    Combo thời khóa biểu với nhãn vở siêu xinh, chất giấy dày dặn dã man mấy bà ơi. Đang có mã Freeship Shopee rẻ bèo nè múc lẹ: https://vn.shp.ee/akhdhST
    """,
    """
    Mom nào sắm đồ dùng cho bé năm học mới thì tham khảo combo nhà em nhé, giấy dày dặn dán dính siêu chắc. Link Shopee đang sale ạ: https://vn.shp.ee/akhdhST
    """,
    """
    Perfect Packs sẵn sỉ/lẻ combo nhãn vở - thời khóa biểu thiết kế riêng. Mọi người mua lẻ trải nghiệm chất lượng qua Shopee nhà em nhé: https://vn.shp.ee/akhdhST
    """,
    """
    Góc học tập mà decor thêm bộ này là tự động có hứng học liền 😆 Hàng bao đẹp, chuẩn hình, link Shopee cho ai cần nha: https://vn.shp.ee/akhdhST
    """,
    """
    Giấy C300 siêu dày, màu sắc tươi sáng mà giá cực êm. Các bác chốt đơn qua link Shopee cho lẹ nha, bên em đóng gói gửi hàng luôn trong ngày: https://vn.shp.ee/akhdhST
    """
]

# ── DESIGN TOKENS ─────────────────────────────────────────────────────────────
G = {
    "win":      "#f5f5f7",
    "sidebar":  "#f5f5f7",
    "glass":    "#ffffff",
    "glass2":   "#f2f2f7",
    "border":   "#d1d1d6",
    "border2":  "#e5e5ea",
    "t1": "#1c1c1e",
    "t2": "#3c3c43",
    "t3": "#8e8e93",
    "t4": "#c7c7cc",
    "blue":    "#007aff",
    "blue_dk": "#0062cc",
    "blue_bg": "#e5f0ff",
    "cyan":    "#32ade6",
    "orange":  "#ff9500",
    "red":     "#ff3b30",
    "green":   "#34c759",
    "inp":     "#ffffff",
    "inp_bd":  "#d1d1d6",
    "log_bg":  "#1c1c1e",
}

import tkinter.font as _tf
def _ff(size, bold=False):
    w = "bold" if bold else "normal"
    for f in ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Arial"):
        if f in _tf.families():
            return (f, size, w)
    return ("Arial", size, w)

def _mono(s=9):
    for f in ("Cascadia Code", "SF Mono", "Consolas", "Courier New"):
        if f in _tf.families():
            return (f, s)
    return ("Consolas", s)

F = lambda s, b=False: _ff(s, b)


# ══════════════════════════════════════════════════════════════════════════════
# FACEBOOK BOT
# ══════════════════════════════════════════════════════════════════════════════
class FacebookBot:
    def __init__(self, config, log_queue):
        self.config       = config
        self.log_queue    = log_queue
        self.driver       = None
        self.wait         = None
        self.is_logged_in = False
        self.should_stop  = False
        self.my_name      = ""   # tên tài khoản đang dùng, để skip bài của mình

    # ── LOGGING ───────────────────────────────────────────────────────
    def log(self, msg, t='info'):
        try:
            self.log_queue.put({'ts': time.strftime("%H:%M:%S"), 'msg': msg, 'type': t})
            print(f"[{time.strftime('%H:%M:%S')}] {msg}")
        except: pass

    # ── UTILS ─────────────────────────────────────────────────────────
    def delay(self, a, b): time.sleep(random.uniform(a, b))

    def slow_type(self, el, text):
        for ch in text:
            if self.should_stop: return
            el.send_keys(ch); time.sleep(random.uniform(0.05, 0.13))

    def type_multiline(self, el, text):
        final = text.replace('|', '\n')
        el.send_keys(Keys.CONTROL + 'a'); time.sleep(0.15)
        el.send_keys(Keys.DELETE);        time.sleep(0.15)
        try:
            pyperclip.copy(final); time.sleep(0.2)
            self.driver.execute_script("arguments[0].click();", el); time.sleep(0.25)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(0.7)
            got = self.driver.execute_script(
                "return arguments[0].innerText||arguments[0].textContent||'';", el)
            if got and got.strip():
                self.log(f"   ✅ Paste OK: {got[:40].replace(chr(10),' ')}…", 'info')
                return
        except Exception as e:
            self.log(f"   ⚠️ Clipboard: {str(e)[:50]}, fallback…", 'warning')
        self.driver.execute_script("arguments[0].click();", el); time.sleep(0.25)
        for ch in text.replace('|', ' '):
            if self.should_stop: return
            el.send_keys(ch); time.sleep(0.04)

    # ── SETUP DRIVER ──────────────────────────────────────────────────
    def setup_driver(self):
        try:
            self.log("🔧 Khởi tạo Chrome driver…", 'info')
            opt = Options()
            opt.add_argument('--disable-blink-features=AutomationControlled')
            opt.add_experimental_option("excludeSwitches", ["enable-automation"])
            opt.add_experimental_option('useAutomationExtension', False)
            opt.add_argument('--disable-notifications')
            opt.add_argument('--start-maximized')
            opt.add_argument('--lang=vi')
            opt.add_argument('--no-sandbox')
            opt.add_argument('--disable-dev-shm-usage')
            svc = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=svc, options=opt)
            self.wait   = WebDriverWait(self.driver, 10)
            self.driver.execute_script(
                "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
            self.log("✅ Chrome sẵn sàng!", 'success')
            return True
        except Exception as e:
            self.log(f"❌ Lỗi driver: {e}", 'error'); return False

    # ── LOGIN ─────────────────────────────────────────────────────────
    def login_facebook(self):
        if self.is_logged_in:
            self.log("✅ Đã đăng nhập", 'info'); return True
        try:
            self.log("🔐 Đăng nhập Facebook…", 'step')
            self.driver.get("https://www.facebook.com"); self.delay(5, 8)
            if self.should_stop: return False

            email_el = None
            for by, sel in [(By.ID,"email"),(By.NAME,"email"),(By.XPATH,"//input[@type='email']")]:
                try:
                    email_el = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by, sel))); break
                except: continue
            if not email_el:
                self.log("❌ Không tìm thấy ô email!", 'error'); return False
            self.driver.execute_script("arguments[0].click();", email_el)
            self.delay(0.5, 1); email_el.clear()
            self.slow_type(email_el, self.config['email']); self.delay(1, 2)

            pass_el = None
            for by, sel in [(By.ID,"pass"),(By.NAME,"pass"),(By.XPATH,"//input[@type='password']")]:
                try: pass_el = self.driver.find_element(by, sel); break
                except: continue
            if not pass_el:
                self.log("❌ Không tìm thấy ô mật khẩu!", 'error'); return False
            self.driver.execute_script("arguments[0].click();", pass_el)
            self.delay(0.5, 1); pass_el.clear()
            self.slow_type(pass_el, self.config['password']); self.delay(1, 2)
            pass_el.send_keys(Keys.RETURN)

            self.log("⏳ Chờ Facebook xử lý…", 'info'); self.delay(10, 15)
            if self.should_stop: return False

            url = self.driver.current_url
            ok  = "login" not in url.lower()
            if "checkpoint" in url.lower():
                self.log("⚠️ Yêu cầu xác minh! Có 60s…", 'warning')
                for _ in range(60):
                    if self.should_stop: return False
                    time.sleep(1); u = self.driver.current_url
                    if "checkpoint" not in u.lower() and "login" not in u.lower():
                        ok = True; self.log("✅ Xác minh OK!", 'success'); break

            if ok:
                self.log("✅ Đăng nhập thành công!", 'success')
                self.is_logged_in = True
                self.delay(2, 3)
                self.my_name = self.get_my_name()  # lấy tên để skip bài của mình
                return True

            self.log("❌ Đăng nhập thất bại!", 'error'); return False
        except Exception as e:
            self.log(f"❌ Lỗi đăng nhập: {e}", 'error'); return False

    # ── LẤY TÊN TÀI KHOẢN ────────────────────────────────────────────
    def get_my_name(self):
        """
        Lấy tên hiển thị của tài khoản đang đăng nhập.
        Dùng để bỏ qua bài do chính mình đăng khi comment.
        """
        try:
            self.log("👤 Đang lấy tên tài khoản…", 'info')

            # Thử lấy tên từ trang chủ
            self.driver.get("https://www.facebook.com")
            self.delay(3, 5)

            name_el = None
            for by, sel in [
                (By.XPATH, "//div[@aria-label='Your profile']//span[string-length(text())>1]"),
                (By.XPATH, "//a[contains(@href,'/me')]//span[string-length(text())>1]"),
                (By.XPATH, "//div[@role='navigation']//a[contains(@href,'profile.php')]//span[not(*)]"),
                (By.XPATH, "//span[@data-default-value and string-length(text())>1]"),
            ]:
                try:
                    name_el = self.driver.find_element(by, sel)
                    if name_el and name_el.text.strip(): break
                    name_el = None
                except: continue

            if name_el and name_el.text.strip():
                name = name_el.text.strip()
                self.log(f"👤 Tài khoản: {name}", 'success')
                return name

            # Fallback: vào trang /me lấy H1
            self.driver.get("https://www.facebook.com/me")
            self.delay(4, 6)
            for by, sel in [
                (By.XPATH, "//h1[string-length(text())>1]"),
                (By.XPATH, "//h1//span[string-length(text())>1]"),
            ]:
                try:
                    el = self.driver.find_element(by, sel)
                    if el and el.text.strip():
                        name = el.text.strip()
                        self.log(f"👤 Tài khoản (profile): {name}", 'success')
                        return name
                except: continue

            self.log("⚠️ Không lấy được tên, sẽ comment tất cả bài", 'warning')
            return ""
        except Exception as e:
            self.log(f"⚠️ Lỗi lấy tên tài khoản: {e}", 'warning')
            return ""

    # ── FIND ELEMENT HELPER ───────────────────────────────────────────
    def _find_element_any(self, selectors, timeout=8):
        for by, sel in selectors:
            try:
                el = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, sel)))
                if el: return el
            except: continue
        return None

    # ── ĐĂNG BÀI ─────────────────────────────────────────────────────
    def post_to_group(self, group_url, post_text, post_images=None):
        post_images = post_images or []
        valid_imgs  = [p for p in post_images if p and os.path.exists(p)]
        n = len(valid_imgs)
        try:
            self.log(f"📤 Đăng bài {'+ '+str(n)+' ảnh' if n else '(text)'}…", 'step')
            self.driver.get(group_url); self.delay(6, 9)
            if self.should_stop: return False

            self.driver.execute_script("window.scrollTo(0,400);"); self.delay(2, 3)
            self.driver.execute_script("window.scrollTo(0,0);");   self.delay(1, 2)

            self.log("🔍 Tìm ô soạn bài…", 'info')
            write_box = self._find_element_any([
                (By.XPATH, "//div[@aria-label='Viết gì đó...']"),
                (By.XPATH, "//div[@aria-label='Write something...']"),
                (By.XPATH, "//div[@aria-label='Bạn đang nghĩ gì?']"),
                (By.XPATH, "//div[@aria-label=\"What's on your mind?\"]"),
                (By.XPATH, "//span[normalize-space()='Viết gì đó...']"),
                (By.XPATH, "//span[normalize-space()='Write something...']"),
                (By.XPATH, "//span[contains(text(),'Viết gì đó')]"),
                (By.XPATH, "//span[contains(text(),'Write something')]"),
                (By.XPATH, "//*[@role='button'][contains(.,'Viết gì đó')]"),
                (By.XPATH, "//*[@role='button'][contains(.,'Write something')]"),
            ], timeout=7)

            if not write_box:
                self.log("❌ Không tìm thấy ô soạn bài!", 'error'); return False
            self.log("✅ Tìm thấy ô soạn bài", 'success')
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", write_box)
            self.delay(0.8, 1.2)
            self.driver.execute_script("arguments[0].click();", write_box)
            self.delay(2, 3)

            self.log("🔍 Tìm textarea…", 'info')
            textarea = self._find_element_any([
                (By.XPATH, "//div[@role='dialog']//div[@contenteditable='true'][@role='textbox']"),
                (By.XPATH, "//div[@role='dialog']//p[@contenteditable='true']"),
                (By.XPATH, "//div[@role='dialog']//div[@data-lexical-editor='true']"),
                (By.XPATH, "//div[@role='dialog']//p[@data-lexical-editor='true']"),
                (By.XPATH, "//div[@contenteditable='true'][@aria-label='Bạn đang nghĩ gì?']"),
                (By.XPATH, "//div[@contenteditable='true'][@aria-label=\"What's on your mind?\"]"),
                (By.XPATH, "//div[@contenteditable='true'][@role='textbox']"),
                (By.XPATH, "//form//div[@contenteditable='true']"),
                (By.XPATH, "//form//p[@contenteditable='true']"),
            ], timeout=8)

            if not textarea:
                self.log("❌ Không tìm thấy textarea!", 'error'); return False
            self.log("✅ Tìm thấy textarea", 'success')
            self.driver.execute_script("arguments[0].click();", textarea)
            self.delay(0.5, 1)

            self.log("✍️ Nhập nội dung…", 'info')
            self.type_multiline(textarea, post_text); self.delay(1.5, 2.5)
            got = self.driver.execute_script(
                "return arguments[0].innerText||arguments[0].textContent||'';", textarea)
            if not got.strip():
                self.log("⚠️ Trống, thử lại…", 'warning')
                self.driver.execute_script("arguments[0].click();", textarea)
                self.delay(0.5, 1)
                self.type_multiline(textarea, post_text); self.delay(1.5, 2)

            if valid_imgs:
                self.log(f"🖼️ Upload {n} ảnh…", 'info')
                if self._upload_post_images(valid_imgs):
                    self.log(f"✅ Upload {n} ảnh OK", 'success'); self.delay(3, 5)
                else:
                    self.log("⚠️ Upload ảnh thất bại, đăng text thôi", 'warning')

            self.log("🔍 Tìm nút Đăng…", 'info')
            post_btn = self._find_element_any([
                (By.XPATH, "//div[@role='dialog']//div[@aria-label='Post']"),
                (By.XPATH, "//div[@role='dialog']//div[@aria-label='Đăng']"),
                (By.XPATH, "//div[@role='dialog']//div[@role='button'][.//span[text()='Post']]"),
                (By.XPATH, "//div[@role='dialog']//div[@role='button'][.//span[text()='Đăng']]"),
                (By.XPATH, "//div[@role='dialog']//span[text()='Post']/ancestor::div[@role='button']"),
                (By.XPATH, "//div[@role='dialog']//span[text()='Đăng']/ancestor::div[@role='button']"),
                (By.XPATH, "//form//div[@aria-label='Post']"),
                (By.XPATH, "//form//div[@aria-label='Đăng']"),
                (By.XPATH, "//form//div[@role='button'][.//span[text()='Post']]"),
                (By.XPATH, "//form//div[@role='button'][.//span[text()='Đăng']]"),
                (By.XPATH, "//form//span[text()='Post']/ancestor::div[@role='button']"),
                (By.XPATH, "//form//span[text()='Đăng']/ancestor::div[@role='button']"),
            ], timeout=8)

            if not post_btn:
                self.log("❌ Không tìm thấy nút Đăng!", 'error'); return False
            self.log("✅ Tìm thấy nút Đăng", 'success')
            self.driver.execute_script("arguments[0].click();", post_btn)
            self.log("⏳ Chờ đăng…", 'info'); self.delay(5, 8)
            try:
                WebDriverWait(self.driver, 8).until(
                    EC.invisibility_of_element_located((By.XPATH, "//div[@role='dialog']")))
                self.log("✅ Đăng bài thành công!", 'success')
            except:
                self.log("⚠️ Không xác nhận modal đóng, tiếp tục…", 'warning')
            return True
        except Exception as e:
            self.log(f"❌ Lỗi đăng bài: {e}", 'error'); return False

    # ── UPLOAD ẢNH BÀI ĐĂNG (không hiện Windows file dialog) ─────────
    def _upload_post_images(self, image_paths):
        """
        Upload nhiều ảnh vào form đăng bài mà không mở Windows file dialog.
        Bước 1: Tìm thẳng input[type=file] ẩn trong DOM.
        Bước 2: Nếu chưa có → override click để chặn dialog → click nút Photo → restore.
        Bước 3: Đẩy input ra ngoài màn hình → send_keys paths.
        """
        try:
            file_input = None

            # Bước 1: tìm input ẩn trực tiếp
            for by, sel in [
                (By.XPATH, "//div[@role='dialog']//input[@type='file']"),
                (By.XPATH, "//input[@type='file' and contains(@accept,'image')]"),
                (By.XPATH, "//input[@type='file']"),
            ]:
                try:
                    inputs = self.driver.find_elements(by, sel)
                    if inputs:
                        file_input = inputs[0]
                        self.log("   ✅ Tìm thấy file input trực tiếp", 'info')
                        break
                except: continue

            # Bước 2: click nút Photo nhưng chặn dialog native
            if not file_input:
                photo_btn = None
                for by, sel in [
                    (By.XPATH, "//div[@role='dialog']//div[@aria-label='Photo/video']"),
                    (By.XPATH, "//div[@role='dialog']//div[@aria-label='Ảnh/video']"),
                    (By.XPATH, "//div[@role='dialog']//div[contains(@aria-label,'Photo')]"),
                    (By.XPATH, "//div[@role='dialog']//div[contains(@aria-label,'Ảnh')]"),
                ]:
                    try:
                        photo_btn = self.driver.find_element(by, sel)
                        if photo_btn: break
                    except: continue

                if photo_btn:
                    # Override để chặn Windows file dialog khi FB's JS gọi input.click()
                    self.driver.execute_script("""
                        HTMLInputElement.prototype._origClick = HTMLInputElement.prototype.click;
                        HTMLInputElement.prototype.click = function() {
                            if (this.type === 'file') return;
                            this._origClick();
                        };
                    """)
                    self.driver.execute_script("arguments[0].click();", photo_btn)
                    self.delay(1, 2)

                    # Restore click bình thường
                    self.driver.execute_script("""
                        if (HTMLInputElement.prototype._origClick) {
                            HTMLInputElement.prototype.click = HTMLInputElement.prototype._origClick;
                            delete HTMLInputElement.prototype._origClick;
                        }
                    """)

                    # Tìm input vừa xuất hiện
                    for by, sel in [
                        (By.XPATH, "//div[@role='dialog']//input[@type='file']"),
                        (By.XPATH, "//input[@type='file' and contains(@accept,'image')]"),
                        (By.XPATH, "//input[@type='file']"),
                    ]:
                        try:
                            inputs = self.driver.find_elements(by, sel)
                            if inputs:
                                file_input = inputs[0]
                                self.log("   ✅ Tìm thấy file input sau click Photo", 'info')
                                break
                        except: continue
                else:
                    self.log("⚠️ Không tìm thấy nút Photo/Video", 'warning')

            if not file_input:
                self.log("⚠️ Không tìm thấy file input", 'warning')
                return False

            # Bước 3: đẩy ra ngoài màn hình → send_keys (không trigger dialog)
            self.driver.execute_script("""
                arguments[0].style.display    = 'block';
                arguments[0].style.visibility = 'visible';
                arguments[0].style.opacity    = '1';
                arguments[0].style.position   = 'fixed';
                arguments[0].style.top        = '-9999px';
                arguments[0].style.left       = '-9999px';
            """, file_input)

            file_input.send_keys("\n".join(image_paths))
            self.log(f"   📎 Đã gửi {len(image_paths)} file tới input", 'info')
            self.delay(3, 5)
            return True

        except Exception as e:
            self.log(f"⚠️ Lỗi upload ảnh bài: {e}", 'warning')
            return False

    # ── COMMENT ───────────────────────────────────────────────────────
    def open_group_and_scroll(self, group_url, post_count=2):
        try:
            self.log("📂 Mở nhóm để comment…", 'info')
            self.driver.get(group_url); self.delay(5, 7)
            if self.should_stop: return 0
            for _ in range(20):
                if self.should_stop: return 0
                if len(self.driver.find_elements(By.TAG_NAME, "form")) >= post_count: break
                self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
                self.delay(2, 3)
            self.driver.execute_script("window.scrollTo(0,0);"); self.delay(1, 2)
            self.driver.execute_script("window.scrollTo(0,300);"); self.delay(1, 2)
            n = len(self.driver.find_elements(By.TAG_NAME, "form"))
            self.log(f"✅ Load {n} form", 'success')
            return n
        except Exception as e:
            self.log(f"❌ Lỗi mở nhóm: {e}", 'error'); return 0

    def _is_my_post(self, form):
        """
        Kiểm tra bài viết này có phải do mình đăng không.
        So sánh tên tác giả với self.my_name (không phân biệt hoa/thường).
        """
        if not self.my_name:
            return False
        try:
            for by, sel in [
                (By.XPATH, ".//h2//a/span[string-length(text())>1]"),
                (By.XPATH, ".//h3//a/span[string-length(text())>1]"),
                (By.XPATH, ".//h4//a/span[string-length(text())>1]"),
                (By.XPATH, ".//strong//a/span[string-length(text())>1]"),
                (By.XPATH, ".//a[@role='link']//span[string-length(text())>1]"),
                (By.XPATH, ".//span[@dir='auto'][string-length(text())>1]"),
            ]:
                try:
                    author_el = form.find_element(by, sel)
                    author = author_el.text.strip()
                    if author and self.my_name.lower() in author.lower():
                        return True
                except: continue
        except: pass
        return False

    def _get_comment_forms(self):
        """
        Trả về danh sách form có thể comment.
        Tự động bỏ qua:
          - Form không có vùng comment (ví dụ form đăng bài)
          - Bài do chính mình đăng (dựa vào self.my_name)
        """
        all_forms    = self.driver.find_elements(By.TAG_NAME, "form")
        comment_forms = []
        skipped_mine  = 0

        for f in all_forms:
            try:
                # Bỏ qua bài của mình
                if self._is_my_post(f):
                    skipped_mine += 1
                    continue

                # Chỉ lấy form có vùng comment
                has_cmt = False
                for by, sel in [
                    (By.XPATH, ".//div[contains(@aria-label,'Write a comment')]"),
                    (By.XPATH, ".//div[contains(@aria-label,'Viết bình luận')]"),
                    (By.XPATH, ".//div[contains(@aria-label,'comment')]"),
                    (By.XPATH, ".//p[@contenteditable='true']"),
                    (By.XPATH, ".//div[@contenteditable='true' and @role='textbox']"),
                ]:
                    try:
                        el = f.find_element(by, sel)
                        if el: has_cmt = True; break
                    except: continue

                if has_cmt:
                    comment_forms.append(f)
            except: continue

        if skipped_mine > 0:
            self.log(f"   ⏭️ Bỏ qua {skipped_mine} bài của mình ({self.my_name})", 'info')

        return comment_forms

    def find_and_click_comment_area(self, idx):
        try:
            forms = self._get_comment_forms()
            if idx >= len(forms): return None
            form = forms[idx]
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", form)
            self.delay(1.5, 2)
            for by, sel in [
                (By.XPATH, ".//div[contains(@aria-label,'Write a comment')]"),
                (By.XPATH, ".//div[contains(@aria-label,'Viết bình luận')]"),
            ]:
                try:
                    el = form.find_element(by, sel)
                    if el.is_displayed():
                        self.driver.execute_script("arguments[0].click();", el)
                        self.delay(1, 1.5); return form
                except: continue
            self.driver.execute_script("arguments[0].click();", form)
            self.delay(1, 1.5); return form
        except: return None

    def find_comment_box(self, idx):
        try:
            forms = self._get_comment_forms()
            if idx >= len(forms): return None
            form = forms[idx]
            for by, sel in [
                (By.XPATH, ".//p[@contenteditable='true']"),
                (By.XPATH, ".//div[@contenteditable='true' and @role='textbox']"),
            ]:
                try:
                    el = form.find_element(by, sel)
                    if el.is_displayed() and el.is_enabled(): return el
                except: continue
            return None
        except: return None

    def upload_image_to_comment(self, idx, path):
        """Upload ảnh vào comment box."""
        try:
            if not path or not os.path.exists(path): return False
            forms = self._get_comment_forms()
            if idx >= len(forms): return False
            form = forms[idx]

            box = self.find_comment_box(idx)
            if box:
                self.driver.execute_script("arguments[0].click();", box)
                self.delay(0.5, 1)

            fi = None
            for by, sel in [
                (By.XPATH, ".//input[@type='file' and contains(@accept,'image')]"),
                (By.XPATH, ".//input[@type='file']"),
            ]:
                try:
                    inps = form.find_elements(by, sel)
                    if inps: fi = inps[0]; break
                except: continue

            if not fi:
                for by, sel in [
                    (By.XPATH, ".//div[@aria-label='Photo/video']"),
                    (By.XPATH, ".//div[@aria-label='Ảnh/video']"),
                    (By.XPATH, ".//div[contains(@aria-label,'Photo')]"),
                    (By.XPATH, ".//div[contains(@aria-label,'Ảnh')]"),
                ]:
                    try:
                        btn = form.find_element(by, sel)
                        if btn.is_displayed():
                            self.driver.execute_script("arguments[0].click();", btn)
                            self.delay(1, 2); break
                    except: continue
                try:
                    fi = self.driver.find_element(
                        By.XPATH, "//input[@type='file' and contains(@accept,'image')]")
                except:
                    try: fi = self.driver.find_element(By.XPATH, "//input[@type='file']")
                    except: pass

            if fi:
                self.driver.execute_script(
                    "arguments[0].style.display='block';"
                    "arguments[0].style.visibility='visible';", fi)
                fi.send_keys(path)
                self.log(f"✅ Upload ảnh cmt: {os.path.basename(path)}", 'success')
                self.delay(2, 4); return True
            return False
        except Exception as e:
            self.log(f"⚠️ Lỗi upload ảnh cmt: {e}", 'warning'); return False

    def comment_with_retry(self, post_idx, text, image, max_retries=3):
        """
        Comment với retry tự động.
        Hỗ trợ: text only / image only / text + image.
        """
        for attempt in range(1, max_retries+1):
            if self.should_stop: return False
            self.log(f"   🔄 Lần {attempt}/{max_retries}…", 'info')
            has_text  = bool(text and text.strip())
            has_image = bool(image and os.path.exists(image))

            if not has_text and not has_image:
                self.log("   ⚠️ Không có nội dung comment", 'warning'); return False

            try:
                form = self.find_and_click_comment_area(post_idx)
                if not form:
                    self.log("   ⚠️ Không click được comment area", 'warning')
                    self.delay(2, 4); continue

                box = self.find_comment_box(post_idx)
                if not box:
                    self.log("   ⚠️ Không tìm thấy comment box", 'warning')
                    self.delay(2, 4); continue

                img_ok = False
                if has_image:
                    self.log("   🖼️ Upload ảnh comment…", 'info')
                    img_ok = self.upload_image_to_comment(post_idx, image)
                    if img_ok:
                        self.delay(3, 5)
                        box = self.find_comment_box(post_idx)
                        if not box:
                            self.log("   ⚠️ Mất box sau upload ảnh", 'warning')
                            self.delay(2, 3); continue
                    else:
                        self.log("   ⚠️ Upload ảnh thất bại", 'warning')
                        if not has_text:
                            self.delay(2, 3); continue

                if has_text:
                    self.type_multiline(box, text); self.delay(1.5, 2.5)

                try:
                    got = self.driver.execute_script(
                        "return arguments[0].innerText||arguments[0].textContent||'';", box)
                    box_ok = bool(got and got.strip())
                except:
                    box_ok = has_text

                if not box_ok and not img_ok:
                    self.log("   ⚠️ Box trống và không có ảnh, thử lại", 'warning')
                    self.delay(2, 3); continue

                self.driver.execute_script("arguments[0].focus();", box)
                time.sleep(0.3)
                box.send_keys(Keys.RETURN)
                self.delay(2, 3)
                self.log(f"   ✅ Thành công lần {attempt}", 'success')
                return True

            except Exception as e:
                self.log(f"   ❌ Lỗi lần {attempt}: {str(e)[:80]}", 'warning')
                self.delay(3, 5)

        self.log(f"   ❌ Hết {max_retries} lần", 'error'); return False

    def comment_on_group(self, group_url, post_count=2):
        try:
            avail = self.open_group_and_scroll(group_url, post_count*2)
            if avail == 0:
                self.log("⚠️ Không có bài viết", 'warning'); return 0

            comments  = self.config['comments']
            delay_min = self.config['delayMinutes']
            success = post_idx = cmt_idx = 0

            while success < post_count and post_idx < avail:
                if self.should_stop: break
                cd    = comments[cmt_idx % len(comments)]
                ctext = cd['text']
                cimg  = cd.get('image', '')
                info  = " +🖼️" if (cimg and os.path.exists(cimg)) else ""
                only_img = not ctext.strip() and cimg
                disp  = "(Chỉ ảnh)" if only_img else (ctext[:38]+"…" if len(ctext)>38 else ctext)
                self.log(f"📝 Bài {post_idx+1} [{success+1}/{post_count}]: {disp}{info}", 'info')

                ok = self.comment_with_retry(post_idx, ctext, cimg)
                if ok:
                    success += 1; cmt_idx += 1
                    if success < post_count and not self.should_stop:
                        self.log(f"⏱️ Chờ {delay_min} phút…", 'info')
                        for _ in range(delay_min*60):
                            if self.should_stop: break
                            time.sleep(1)
                post_idx += 1

            self.log(f"📊 Comment: {success}/{post_count} OK", 'success')
            return success
        except Exception as e:
            self.log(f"❌ Lỗi comment: {e}", 'error'); return 0

    # ── RUN SESSION ───────────────────────────────────────────────────
    def run_session(self, name):
        try:
            self.log("─"*46, 'step')
            self.log(f"▶  {name.upper()}", 'step')
            self.log("─"*46, 'step')

            groups    = self.config['groups']
            grp_delay = self.config['groupDelayMinutes']
            posts     = self.config.get('post_contents', [])
            total     = 0

            for i, url in enumerate(groups):
                if self.should_stop: break
                self.log(f"📍 Nhóm {i+1}/{len(groups)}: {url.split('/')[-2]}", 'step')

                if posts:
                    pc   = posts[i % len(posts)]
                    ptxt = pc.get('text', '')
                    pimg = pc.get('images', [])
                    self.log(f"📤 Đăng {'+ '+str(len(pimg))+' ảnh' if pimg else '(text)'}…", 'step')
                    ok = self.post_to_group(url, ptxt, pimg)
                    if ok:
                        self.log("✅ Đăng xong! Chờ rồi comment…", 'success')
                        self.delay(8, 12)
                    else:
                        self.log("⚠️ Đăng thất bại, reload…", 'warning')
                        self.driver.get(url); self.delay(5, 7)
                else:
                    self.log("ℹ️ Không có nội dung đăng bài", 'info')

                total += self.comment_on_group(url, post_count=2)

                if i < len(groups)-1 and not self.should_stop:
                    self.log(f"⏱️ Chờ {grp_delay} phút…", 'info')
                    for _ in range(grp_delay*60):
                        if self.should_stop: break
                        time.sleep(1)

            self.log("─"*46, 'success')
            self.log(f"✅  {name.upper()} — {total} comment", 'success')
            self.log("─"*46, 'success')
        except Exception as e:
            self.log(f"❌ Lỗi phiên: {e}", 'error')

    def cleanup(self):
        try:
            if self.driver: self.driver.quit()
        except: pass


# ══════════════════════════════════════════════════════════════════════════════
# GLASSMORPHISM WIDGETS
# ══════════════════════════════════════════════════════════════════════════════

def _div(parent, color=None, padx=0, pady=0):
    tk.Frame(parent, bg=color or G['border2'], height=1
             ).pack(fill='x', padx=padx, pady=pady)


class GlassCard(tk.Frame):
    def __init__(self, parent, **kw):
        kw.setdefault('bg', G['glass'])
        kw.setdefault('highlightthickness', 1)
        kw.setdefault('highlightbackground', G['border'])
        super().__init__(parent, **kw)


class PostWidget(tk.Frame):
    def __init__(self, parent, index, **kw):
        super().__init__(parent, bg=G['glass'], **kw)
        self.index = index; self.image_paths = []
        self._build()

    def _build(self):
        h = tk.Frame(self, bg=G['glass2']); h.pack(fill='x')
        tk.Label(h, text=f"  ✦  Nội dung {self.index}",
                 bg=G['glass2'], fg=G['blue'], font=F(9,True), pady=5).pack(side='left')
        _div(self, color=G['border'])
        self.text_w = tk.Text(
            self, height=3, wrap='word', bg=G['glass'], fg=G['t1'], font=F(10),
            relief='flat', bd=0, insertbackground=G['blue'],
            selectbackground=G['blue_dk'], selectforeground=G['t1'],
            padx=12, pady=8)
        self.text_w.pack(fill='x')
        _div(self, color=G['border2'])
        bar = tk.Frame(self, bg=G['glass']); bar.pack(fill='x', padx=10, pady=6)
        tk.Button(bar, text="＋  Thêm ảnh", font=F(9), bg=G['blue_bg'], fg=G['blue'],
                  relief='flat', bd=0, cursor='hand2', padx=10, pady=4,
                  activebackground=G['blue_dk'], activeforeground='white',
                  command=self._add).pack(side='left')
        tk.Button(bar, text="Xóa tất cả", font=F(9), bg=G['glass'], fg=G['t3'],
                  relief='flat', bd=0, cursor='hand2', padx=8, pady=4,
                  command=self._clear).pack(side='left', padx=(6,0))
        self.count_lbl = tk.Label(bar, text="", bg=G['glass'], fg=G['cyan'], font=F(9))
        self.count_lbl.pack(side='right')
        self.img_list = tk.Frame(self, bg=G['glass']); self.img_list.pack(fill='x', padx=12)
        tk.Label(self, text="  ↵  Dùng  |  để xuống dòng",
                 bg=G['glass'], fg=G['t3'], font=F(8), pady=4).pack(anchor='w')

    def _add(self):
        ps = filedialog.askopenfilenames(
            title="Chọn ảnh bài đăng",
            filetypes=[("Ảnh","*.jpg *.jpeg *.png *.gif *.webp *.bmp"),("*","*.*")])
        for p in ps:
            if p not in self.image_paths: self.image_paths.append(p)
        self._refresh()

    def _clear(self): self.image_paths.clear(); self._refresh()

    def _remove(self, p):
        if p in self.image_paths: self.image_paths.remove(p)
        self._refresh()

    def _refresh(self):
        for w in self.img_list.winfo_children(): w.destroy()
        for p in self.image_paths:
            r = tk.Frame(self.img_list, bg=G['glass']); r.pack(fill='x', pady=1)
            fn = os.path.basename(p); disp = fn[:36]+"…" if len(fn)>36 else fn
            tk.Label(r, text=f"  ↳ {disp}", bg=G['glass'], fg=G['t2'], font=F(9)).pack(side='left')
            tk.Button(r, text="✕", font=F(9), bg=G['glass'], fg=G['t3'],
                      relief='flat', bd=0, cursor='hand2',
                      command=lambda pp=p: self._remove(pp)).pack(side='right')
        n = len(self.image_paths)
        self.count_lbl.config(text=f"{n} ảnh" if n else "")
        if n: tk.Frame(self.img_list, bg=G['glass'], height=4).pack()

    def get_text(self):   return self.text_w.get("1.0", 'end').strip()
    def get_images(self): return [p for p in self.image_paths if os.path.exists(p)]
    def set_text(self, t): self.text_w.delete("1.0",'end'); self.text_w.insert("1.0", t)


class CommentWidget(tk.Frame):
    def __init__(self, parent, index, **kw):
        super().__init__(parent, bg=G['glass'], **kw)
        self.index = index; self.img_path = tk.StringVar(value="")
        self._build()

    def _build(self):
        outer = tk.Frame(self, bg=G['glass']); outer.pack(fill='x', padx=10, pady=(8,0))
        badge = tk.Canvas(outer, bg=G['glass'], width=22, height=22, highlightthickness=0, bd=0)
        badge.create_oval(1,1,21,21, fill=G['blue_dk'], outline=G['blue'])
        badge.create_text(11,11, text=str(self.index), fill=G['blue'], font=F(8,True))
        badge.pack(side='left', anchor='n', pady=3)
        right = tk.Frame(outer, bg=G['glass']); right.pack(side='left', fill='x', expand=True, padx=(8,0))
        tk.Label(right, text="Text (để trống nếu chỉ comment ảnh)",
                 bg=G['glass'], fg=G['t3'], font=F(8)).pack(anchor='w')
        self.text_w = tk.Text(
            right, height=2, wrap='word', bg=G['glass2'], fg=G['t1'], font=F(10),
            relief='flat', bd=0, insertbackground=G['blue'],
            selectbackground=G['blue_dk'], selectforeground=G['t1'],
            padx=8, pady=6, highlightthickness=1,
            highlightbackground=G['border'], highlightcolor=G['blue'])
        self.text_w.pack(fill='x', pady=(2,4))
        img_row = tk.Frame(right, bg=G['glass']); img_row.pack(fill='x', pady=(0,8))
        tk.Button(img_row, text="📎  Chọn ảnh", font=F(9), bg=G['blue_bg'], fg=G['blue'],
                  relief='flat', bd=0, cursor='hand2', padx=8, pady=3,
                  activebackground=G['blue_dk'], activeforeground='white',
                  command=self._pick).pack(side='left')
        self.img_lbl = tk.Label(img_row, text="Chưa có ảnh", bg=G['glass'], fg=G['t3'], font=F(9))
        self.img_lbl.pack(side='left', padx=(8,4))
        self._del_btn = tk.Button(img_row, text="✕", font=F(9), bg=G['glass'], fg=G['t3'],
                                   relief='flat', bd=0, cursor='hand2', padx=4,
                                   activebackground=G['glass2'],
                                   command=self._clear_img, state='disabled')
        self._del_btn.pack(side='left')

    def _pick(self):
        p = filedialog.askopenfilename(
            title="Chọn ảnh cho comment",
            filetypes=[("Ảnh","*.jpg *.jpeg *.png *.gif *.webp *.bmp"),("Tất cả","*.*")])
        if p:
            self.img_path.set(p); fn = os.path.basename(p)
            self.img_lbl.config(text=fn[:24]+"…" if len(fn)>24 else fn, fg=G['cyan'])
            self._del_btn.config(state='normal')

    def _clear_img(self):
        self.img_path.set(""); self.img_lbl.config(text="Chưa có ảnh", fg=G['t3'])
        self._del_btn.config(state='disabled')

    def get_text(self):  return self.text_w.get("1.0", 'end').strip()
    def get_image(self): return self.img_path.get().strip()
    def set_text(self, t): self.text_w.delete("1.0",'end'); self.text_w.insert("1.0", t)


# ══════════════════════════════════════════════════════════════════════════════
# SCROLL FRAME
# ══════════════════════════════════════════════════════════════════════════════
class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg=None, **kw):
        _bg = bg or parent.cget('bg')
        super().__init__(parent, bg=_bg, **kw)
        cvs = tk.Canvas(self, bg=_bg, highlightthickness=0, bd=0)
        sb  = ttk.Scrollbar(self, orient='vertical', command=cvs.yview)
        self.inner = tk.Frame(cvs, bg=_bg)
        self._wid  = cvs.create_window((0,0), window=self.inner, anchor='nw')
        cvs.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        cvs.pack(side='left', fill='both', expand=True)
        cvs.bind('<Configure>', lambda e: cvs.itemconfigure(self._wid, width=e.width))
        self.inner.bind('<Configure>', lambda e: cvs.configure(scrollregion=cvs.bbox('all')))
        cvs.bind_all('<MouseWheel>', lambda e: cvs.yview_scroll(int(-1*(e.delta/120)), 'units'))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("FB Scheduler")
        self.root.geometry("1180x820")
        self.root.minsize(900, 640)
        self.root.configure(bg=G['win'])
        self._lock         = threading.Lock()
        self._active       = False
        self.bot_running   = False
        self.sched_running = False
        self.bot  = None
        self.q    = queue.Queue()
        self.groups = []; self.posts = []; self.comments = []
        self._sl  = {}; self._sdl = None
        self._apply_style()
        self._build()
        self._tick_logs()
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _apply_style(self):
        s = ttk.Style(); s.theme_use('clam')
        for name in ('TScrollbar','Vertical.TScrollbar'):
            s.configure(name, background=G['glass2'], troughcolor=G['win'],
                        borderwidth=0, arrowsize=0, relief='flat')
            s.map(name, background=[])

    def _build(self):
        tb = tk.Frame(self.root, bg='#ffffff', height=44)
        tb.pack(fill='x'); tb.pack_propagate(False)
        tk.Frame(tb, bg=G['border2'], height=1).place(relx=0, rely=1, relwidth=1)
        lf = tk.Frame(tb, bg='#ffffff'); lf.pack(side='left', padx=14, pady=13)
        for col in ('#ff5f57','#ffbd2e','#28c840'):
            c = tk.Canvas(lf, bg='#ffffff', width=13, height=13, highlightthickness=0, bd=0)
            c.create_oval(1,1,12,12, fill=col, outline=''); c.pack(side='left', padx=2)
        tf = tk.Frame(tb, bg='#ffffff'); tf.pack(side='left', padx=6)
        tk.Label(tf, text="FB Scheduler", bg='#ffffff', fg=G['t1'], font=F(11,True)).pack(side='left')
        tk.Label(tf, text=" v3.3 ", bg=G['blue_bg'], fg=G['blue'],
                 font=F(8,True), padx=4, pady=1).pack(side='left', padx=6)
        self._sdl = tk.Label(tb, text="● Chờ", bg='#ffffff', fg=G['t3'], font=F(10))
        self._sdl.pack(side='right', padx=18)
        body = tk.Frame(self.root, bg=G['win']); body.pack(fill='both', expand=True)
        body.columnconfigure(0, weight=55, minsize=480)
        body.columnconfigure(2, weight=45, minsize=300)
        body.rowconfigure(0, weight=1)
        lw = tk.Frame(body, bg=G['sidebar']); lw.grid(row=0, column=0, sticky='nsew')
        sf = ScrollFrame(lw, bg=G['sidebar']); sf.pack(fill='both', expand=True)
        self._sb = sf.inner
        tk.Frame(body, bg=G['border'], width=1).grid(row=0, column=1, sticky='ns')
        rw = tk.Frame(body, bg=G['log_bg']); rw.grid(row=0, column=2, sticky='nsew')
        self._build_log(rw)
        self._build_sidebar()

    def _build_sidebar(self):
        p = self._sb

        def section(icon, title):
            f = tk.Frame(p, bg=G['sidebar']); f.pack(fill='x', padx=14, pady=(12,3))
            tk.Label(f, text=f"{icon}  {title.upper()}",
                     bg=G['sidebar'], fg=G['t3'], font=F(9,True)).pack(side='left')
            tk.Frame(f, bg=G['border'], height=1).pack(
                side='left', fill='x', expand=True, padx=(8,0), pady=6)

        def card():
            c = GlassCard(p); c.pack(fill='x', padx=14, pady=(0,4)); return c

        def row(card, label, widget_fn, last=False):
            r = tk.Frame(card, bg=G['glass']); r.pack(fill='x')
            if label:
                tk.Label(r, text=label, bg=G['glass'], fg=G['t2'], font=F(10),
                         width=13, anchor='w', padx=12, pady=0).pack(side='left', ipady=8)
            w = widget_fn(r)
            w.pack(side='left', fill='x', expand=True, padx=(0,12), pady=5)
            if not last: tk.Frame(card, bg=G['border2'], height=1).pack(fill='x', padx=12)
            return w

        def entry(parent, var, show='', w=0):
            kw = {} if w==0 else {'width':w}
            return tk.Entry(parent, textvariable=var, show=show, font=F(10),
                            bg=G['inp'], fg=G['t1'], relief='flat', bd=0,
                            insertbackground=G['blue'], highlightthickness=0, **kw)

        section("⬡", "Tài khoản")
        c = card()
        self.email_var = tk.StringVar(); self.pass_var = tk.StringVar()
        row(c, "Email / SĐT", lambda r: entry(r, self.email_var))
        row(c, "Mật khẩu",    lambda r: entry(r, self.pass_var, show='•'), last=True)

        section("⏱", "Lịch & Delay")
        c2 = card()
        self.morn_v = tk.StringVar(value="09:30"); self.aftn_v = tk.StringVar(value="14:00")
        self.delay_v = tk.StringVar(value="2");    self.gdly_v = tk.StringVar(value="5")

        def time_w(r, v): return entry(r, v, w=8)
        def delay_w(r, v):
            f = tk.Frame(r, bg=G['glass'])
            entry(f, v, w=5).pack(side='left')
            tk.Label(f, text=" phút", bg=G['glass'], fg=G['t3'], font=F(10)).pack(side='left')
            return f

        row(c2, "Giờ sáng",   lambda r: time_w(r, self.morn_v))
        row(c2, "Giờ chiều",  lambda r: time_w(r, self.aftn_v))
        row(c2, "Delay bài",  lambda r: delay_w(r, self.delay_v))
        row(c2, "Delay nhóm", lambda r: delay_w(r, self.gdly_v), last=True)

        section("◈", "Nhóm Facebook")
        cg = card()
        self._gi = tk.Frame(cg, bg=G['glass']); self._gi.pack(fill='x')
        for g in DEFAULT_GROUPS: self._add_group(g)
        tk.Frame(cg, bg=G['border2'], height=1).pack(fill='x')
        gf = tk.Frame(cg, bg=G['glass']); gf.pack(fill='x', padx=10, pady=7)
        self._gbtn("＋ Thêm", lambda: self._add_group(), gf).pack(side='left')
        self._gbtn("− Xóa cuối", self._del_group, gf, ghost=True).pack(side='left', padx=(6,0))
        self._sl['groups'] = tk.Label(gf, text=f"{len(self.groups)} nhóm",
                                       bg=G['glass'], fg=G['t3'], font=F(9))
        self._sl['groups'].pack(side='right')

        section("◉", "Nội dung bài đăng")
        cp = card()
        tk.Label(cp, text="  Mỗi ô = 1 nội dung. Xoay vòng qua các nhóm. Để trống = bỏ qua.",
                 bg=G['glass'], fg=G['t3'], font=F(9), pady=5).pack(anchor='w')
        tk.Frame(cp, bg=G['border2'], height=1).pack(fill='x')
        self._pi = tk.Frame(cp, bg=G['glass']); self._pi.pack(fill='x')
        for pc in DEFAULT_POST_CONTENTS: self._add_post(pc)
        tk.Frame(cp, bg=G['border2'], height=1).pack(fill='x')
        pf = tk.Frame(cp, bg=G['glass']); pf.pack(fill='x', padx=10, pady=7)
        self._gbtn("＋ Thêm nội dung", lambda: self._add_post(), pf).pack(side='left')
        self._gbtn("− Xóa cuối", self._del_post, pf, ghost=True).pack(side='left', padx=(6,0))
        self._sl['posts'] = tk.Label(pf, text=f"{len(self.posts)} nội dung",
                                      bg=G['glass'], fg=G['t3'], font=F(9))
        self._sl['posts'].pack(side='right')

        section("◎", "Comment")
        cc = card()
        tk.Label(cc, text="  Text hoặc Ảnh (hoặc cả hai). Text trống → comment chỉ ảnh.",
                 bg=G['glass'], fg=G['t3'], font=F(9), pady=5).pack(anchor='w')
        tk.Frame(cc, bg=G['border2'], height=1).pack(fill='x')
        self._ci = tk.Frame(cc, bg=G['glass']); self._ci.pack(fill='x')
        for c in DEFAULT_COMMENTS: self._add_comment(c)
        tk.Frame(cc, bg=G['border2'], height=1).pack(fill='x')
        cf = tk.Frame(cc, bg=G['glass']); cf.pack(fill='x', padx=10, pady=7)
        self._gbtn("＋ Thêm comment", lambda: self._add_comment(), cf).pack(side='left')
        self._gbtn("− Xóa cuối", self._del_comment, cf, ghost=True).pack(side='left', padx=(6,0))
        self._sl['comments'] = tk.Label(cf, text=f"{len(self.comments)} comment",
                                         bg=G['glass'], fg=G['t3'], font=F(9))
        self._sl['comments'].pack(side='right')

        section("▷", "Điều khiển")
        bf = tk.Frame(p, bg=G['sidebar']); bf.pack(fill='x', padx=14, pady=(4,20))
        self._btn_start = tk.Button(bf, text="▶  Bắt đầu lịch",
            font=F(11,True), bg=G['blue'], fg='white',
            activebackground=G['blue_dk'], activeforeground='white',
            relief='flat', bd=0, cursor='hand2', padx=18, pady=9, command=self._start)
        self._btn_start.pack(side='left', padx=(0,8))
        self._btn_stop = tk.Button(bf, text="■  Dừng",
            font=F(11), bg=G['glass2'], fg=G['t3'],
            activebackground='#420d0c', activeforeground=G['red'],
            relief='flat', bd=0, cursor='hand2', padx=14, pady=9,
            state='disabled', command=self._stop)
        self._btn_stop.pack(side='left', padx=(0,8))
        self._btn_test = tk.Button(bf, text="⚡  Chạy ngay",
            font=F(11), bg=G['glass2'], fg=G['blue'],
            activebackground=G['border2'], activeforeground=G['blue_dk'],
            relief='flat', bd=0, cursor='hand2', padx=14, pady=9,
            highlightthickness=1, highlightbackground=G['border'], command=self._test)
        self._btn_test.pack(side='left')
        tk.Frame(p, bg=G['sidebar'], height=12).pack()

    def _gbtn(self, text, cmd, parent, ghost=False):
        if ghost:
            return tk.Button(parent, text=text, command=cmd, font=F(9),
                             bg=G['glass'], fg=G['t3'], relief='flat', bd=0,
                             cursor='hand2', padx=8, pady=4, activebackground=G['glass2'])
        return tk.Button(parent, text=text, command=cmd, font=F(9),
                         bg=G['blue_bg'], fg=G['blue'], relief='flat', bd=0,
                         cursor='hand2', padx=10, pady=4,
                         activebackground=G['blue_dk'], activeforeground='white')

    def _build_log(self, p):
        STAT_BG="#f2f2f7"; STAT_SEP="#d1d1d6"; LOG_HDR="#f9f9fb"
        LOG_BG="#1c1c1e"; LOG_FG="#e5e5ea"
        st = tk.Frame(p, bg=STAT_BG); st.pack(fill='x')
        tk.Frame(p, bg=STAT_SEP, height=1).pack(fill='x')
        for key, icon, label in [
            ('groups','◈','Nhóm'),('posts','◉','Bài đăng'),
            ('comments','◎','Comment'),('next','⏱','Phiên tiếp'),
        ]:
            sf = tk.Frame(st, bg=STAT_BG)
            sf.pack(side='left', fill='both', expand=True, padx=1, pady=1)
            tk.Label(sf, text=f"{icon}  {label}", bg=STAT_BG, fg=G['t3'], font=F(8)).pack(pady=(7,1))
            lbl = tk.Label(sf, text="—", bg=STAT_BG, fg=G['blue'], font=F(12,True))
            lbl.pack(pady=(0,7)); self._sl[key] = lbl
        self._sl['groups'].config(text=str(len(self.groups)))
        self._sl['posts'].config(text=str(len(self.posts)))
        self._sl['comments'].config(text=str(len(self.comments)))
        lh = tk.Frame(p, bg=LOG_HDR); lh.pack(fill='x')
        tk.Label(lh, text="  Nhật ký hoạt động", bg=LOG_HDR, fg=G['t3'],
                 font=F(9,True), pady=7).pack(side='left')
        tk.Button(lh, text="Xóa log", bg=LOG_HDR, fg=G['t3'], font=F(9),
                  relief='flat', bd=0, cursor='hand2', padx=10,
                  activebackground=G['border2'],
                  command=lambda: self._log.delete('1.0','end')).pack(side='right', padx=6)
        tk.Frame(p, bg=STAT_SEP, height=1).pack(fill='x')
        self._log = scrolledtext.ScrolledText(
            p, bg=LOG_BG, fg=LOG_FG, font=_mono(9), wrap='word',
            relief='flat', bd=0, insertbackground=G['blue'],
            selectbackground="#2c2c2e", padx=12, pady=10)
        self._log.pack(fill='both', expand=True)
        for tag, color in [('info','#aeaeb2'),('success','#30d158'),
                            ('warning','#ff9f0a'),('error','#ff453a'),('step','#64d2ff')]:
            self._log.tag_config(tag, foreground=color)

    def _add_group(self, default=""):
        if len(self.groups) >= 25:
            messagebox.showwarning("Giới hạn","Tối đa 25 nhóm!"); return
        row = tk.Frame(self._gi, bg=G['glass']); row.pack(fill='x', padx=10, pady=2)
        tk.Label(row, text=f"{len(self.groups)+1}.", bg=G['glass'], fg=G['t3'],
                 font=F(9), width=3).pack(side='left')
        e = tk.Entry(row, font=F(10), bg=G['inp'], fg=G['t1'], relief='flat', bd=0,
                     insertbackground=G['blue'], highlightthickness=1,
                     highlightbackground=G['border'], highlightcolor=G['blue'])
        e.pack(side='left', fill='x', expand=True, ipady=5, padx=(0,4))
        if default: e.insert(0, default)
        self.groups.append(e); self._upd('groups')

    def _del_group(self):
        if len(self.groups) <= 1:
            messagebox.showwarning("Giới hạn","Cần ít nhất 1 nhóm!"); return
        self.groups.pop().master.destroy(); self._upd('groups')

    def _add_post(self, default=""):
        if len(self.posts) >= 10:
            messagebox.showwarning("Giới hạn","Tối đa 10 nội dung!"); return
        if self.posts: tk.Frame(self._pi, bg=G['border2'], height=1).pack(fill='x')
        w = PostWidget(self._pi, len(self.posts)+1); w.pack(fill='x')
        if default: w.set_text(default)
        self.posts.append(w); self._upd('posts')

    def _del_post(self):
        if not self.posts: return
        w = self.posts.pop(); ch = self._pi.winfo_children(); i = list(ch).index(w)
        if i > 0: ch[i-1].destroy()
        w.destroy(); self._upd('posts')

    def _add_comment(self, default=""):
        if len(self.comments) >= 20:
            messagebox.showwarning("Giới hạn","Tối đa 20 comment!"); return
        if self.comments: tk.Frame(self._ci, bg=G['border2'], height=1).pack(fill='x')
        w = CommentWidget(self._ci, len(self.comments)+1); w.pack(fill='x')
        if default: w.set_text(default)
        self.comments.append(w); self._upd('comments')

    def _del_comment(self):
        if len(self.comments) <= 1:
            messagebox.showwarning("Giới hạn","Cần ít nhất 1 comment!"); return
        w = self.comments.pop(); ch = self._ci.winfo_children(); i = list(ch).index(w)
        if i > 0: ch[i-1].destroy()
        w.destroy(); self._upd('comments')

    def _upd(self, key):
        n    = len({'groups':self.groups,'posts':self.posts,'comments':self.comments}[key])
        unit = {'groups':'nhóm','posts':'nội dung','comments':'comment'}[key]
        if self._sl.get(key):
            self._sl[key].config(text=str(n) if key=='groups' else f"{n} {unit}")

    def _write_log(self, d):
        self._log.insert('end', f"[{d['ts']}]  {d['msg']}\n", d['type'])
        self._log.see('end')
        lines = int(self._log.index('end-1c').split('.')[0])
        if lines > 2000: self._log.delete('1.0','300.0')

    def _tick_logs(self):
        try:
            while True: self._write_log(self.q.get_nowait())
        except queue.Empty: pass
        self.root.after(100, self._tick_logs)

    @staticmethod
    def _nt(raw):
        t = raw.strip().replace('.', ':').replace(' ', '')
        if ':' not in t and t.isdigit():
            if len(t)==3:   t='0'+t[0]+':'+t[1:]
            elif len(t)==4: t=t[:2]+':'+t[2:]
            else: raise ValueError(raw)
        p = t.split(':')
        if len(p) < 2: raise ValueError(raw)
        hh, mm = int(p[0]), int(p[1])
        if not(0<=hh<=23 and 0<=mm<=59): raise ValueError(raw)
        return f"{hh:02d}:{mm:02d}"

    def _validate(self):
        if not self.email_var.get().strip():
            messagebox.showerror("Lỗi","Nhập Email / SĐT!"); return False
        if not self.pass_var.get().strip():
            messagebox.showerror("Lỗi","Nhập mật khẩu!"); return False
        if not [e.get().strip() for e in self.groups if e.get().strip()]:
            messagebox.showerror("Lỗi","Nhập ít nhất 1 nhóm!"); return False
        if not [w for w in self.comments if w.get_text() or w.get_image()]:
            messagebox.showerror("Lỗi","Mỗi comment cần có text hoặc ảnh!"); return False
        try: int(self.delay_v.get()); int(self.gdly_v.get())
        except: messagebox.showerror("Lỗi","Delay phải là số!"); return False
        for attr, lbl in [('morn_v','Giờ sáng'),('aftn_v','Giờ chiều')]:
            raw = getattr(self, attr).get()
            try: norm=self._nt(raw); getattr(self,attr).set(norm)
            except:
                messagebox.showerror("Lỗi giờ",f"{lbl} '{raw}' không hợp lệ!\nVí dụ: 09:30")
                return False
        return True

    def _cfg(self):
        return {
            'email':             self.email_var.get().strip(),
            'password':          self.pass_var.get().strip(),
            'groups':            [e.get().strip() for e in self.groups if e.get().strip()],
            'comments':          [{'text':w.get_text(),'image':w.get_image()}
                                  for w in self.comments if w.get_text() or w.get_image()],
            'post_contents':     [{'text':w.get_text(),'images':w.get_images()}
                                  for w in self.posts if w.get_text()],
            'morningTime':       self._nt(self.morn_v.get()),
            'afternoonTime':     self._nt(self.aftn_v.get()),
            'delayMinutes':      int(self.delay_v.get()),
            'groupDelayMinutes': int(self.gdly_v.get()),
        }

    def _dot(self, text, color):
        if self._sdl: self._sdl.config(text="● "+text, fg=color)

    def _ui_run(self, test=False):
        self._btn_start.config(state='disabled', bg=G['t4'])
        self._btn_stop.config(state='normal', bg=G['red'], fg='white')
        self._btn_test.config(state='disabled', fg=G['t3'])
        self._dot("Test…" if test else "Đang chạy", G['orange'] if test else G['green'])

    def _ui_idle(self):
        self._btn_start.config(state='normal', bg=G['blue'])
        self._btn_stop.config(state='disabled', bg=G['glass2'], fg=G['t3'])
        self._btn_test.config(state='normal', fg=G['blue'])
        self._dot("Sẵn sàng", G['t3'])
        with self._lock: self._active = False

    def _upd_next(self, cfg):
        try:
            now = datetime.now()
            mo  = datetime.strptime(cfg['morningTime'],"%H:%M").replace(
                year=now.year, month=now.month, day=now.day)
            af  = datetime.strptime(cfg['afternoonTime'],"%H:%M").replace(
                year=now.year, month=now.month, day=now.day)
            txt = cfg['morningTime'] if now.time()<mo.time() \
                else (cfg['afternoonTime'] if now.time()<af.time() \
                else cfg['morningTime']+" (mai)")
            if self._sl.get('next'): self._sl['next'].config(text=txt)
        except: pass

    def _acquire(self):
        with self._lock:
            if self._active: return False
            self._active = True; return True

    def _start(self):
        if not self._acquire():
            messagebox.showwarning("Đang chạy","Hãy dừng trước!"); return
        if not self._validate(): self._active = False; return
        cfg = self._cfg(); self._ui_run(); self.bot_running = True
        threading.Thread(target=self._sched, args=(cfg,), daemon=True).start()

    def _test(self):
        if not self._acquire():
            messagebox.showwarning("Đang chạy","Hãy dừng trước!"); return
        if not self._validate(): self._active = False; return
        cfg = self._cfg(); self._ui_run(test=True); self.bot_running = True
        def run():
            b = FacebookBot(cfg, self.q); self.bot = b
            try:
                if not b.setup_driver(): return
                if not b.login_facebook(): b.cleanup(); return
                b.run_session("TEST — Chạy ngay")
            finally:
                b.cleanup(); self.bot_running = False
                self.root.after(0, self._ui_idle)
        threading.Thread(target=run, daemon=True).start()

    def _stop(self):
        if not messagebox.askyesno("Xác nhận","Dừng bot?"): return
        self.bot_running = False; self.sched_running = False
        if self.bot: self.bot.should_stop = True
        schedule.clear()
        self.q.put({'ts':time.strftime("%H:%M:%S"),'msg':'■  Đã dừng','type':'warning'})
        self.root.after(0, self._ui_idle)

    def _sched(self, cfg):
        self.sched_running = True
        b = FacebookBot(cfg, self.q); self.bot = b
        try:
            if not b.setup_driver(): return
            if not b.login_facebook(): b.cleanup(); return
            mo = cfg['morningTime']; af = cfg['afternoonTime']
            def _m():
                if self.bot_running and not b.should_stop: b.run_session("Buổi sáng")
            def _a():
                if self.bot_running and not b.should_stop: b.run_session("Buổi chiều")
            try:
                schedule.every().day.at(mo).do(_m)
                schedule.every().day.at(af).do(_a)
            except Exception as e:
                b.log(f"❌ Lỗi đặt lịch: {e}", 'error'); b.cleanup(); return
            b.log(f"✅ Lịch: {mo}  ·  {af}", 'info')
            b.log(f"   {len(cfg['groups'])} nhóm  ·  "
                  f"{len(cfg.get('post_contents',[]))} bài đăng  ·  "
                  f"{len(cfg['comments'])} comment", 'info')
            if b.my_name:
                b.log(f"   👤 Sẽ bỏ qua bài của: {b.my_name}", 'info')
            self.root.after(0, lambda: self._upd_next(cfg))
            while self.bot_running and self.sched_running:
                schedule.run_pending(); time.sleep(1)
        finally:
            b.log("■  Đã dừng", 'warning'); b.cleanup()
            self.root.after(0, self._ui_idle)

    def _close(self):
        if self.bot_running:
            if not messagebox.askokcancel("Thoát","Bot đang chạy. Thoát?"): return
            self.bot_running = False
            if self.bot: self.bot.should_stop = True; self.bot.cleanup()
        self.root.destroy()


# ──────────────────────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    root.configure(bg=G['win'])
    App(root)
    root.mainloop()

if __name__ == '__main__':
    main()