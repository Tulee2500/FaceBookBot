"""
=====================================================================
FACEBOOK AUTO SCHEDULER BOT v2.0 - HỖ TRỢ HÌNH ẢNH & XUỐNG DÒNG
=====================================================================
✅ Comment có hình ảnh
✅ Xuống dòng (dùng ký tự | trong text để xuống dòng)
✅ Đã điền sẵn 15 nhóm và 5 comment mặc định
✅ Giới hạn tối đa: 25 nhóm
=====================================================================
HƯỚNG DẪN XUỐNG DÒNG:
  Dùng ký tự | để xuống dòng trong ô comment
  Ví dụ: "Dòng 1|Dòng 2|Dòng 3"
  Sẽ thành:
    Dòng 1
    Dòng 2
    Dòng 3
=====================================================================
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
import time
import random
import threading
from datetime import datetime
import schedule
import queue
import os


# =====================================================================
# DỮ LIỆU MẶC ĐỊNH
# =====================================================================

DEFAULT_GROUPS = [
    "https://www.facebook.com/groups/HOILAIXEVIETNAM",
    "https://www.facebook.com/groups/1118760058801951",
    "https://www.facebook.com/groups/3622280321363659",
    "https://www.facebook.com/groups/1495396794007206",
    "https://www.facebook.com/groups/323225114948660",
    "https://www.facebook.com/groups/dochoixegiare",
    "https://www.facebook.com/groups/2335385660000110",
    "https://www.facebook.com/groups/234656999212139",
    "https://www.facebook.com/groups/1428967671376047"
]

# Dùng ký tự | để xuống dòng trong comment
DEFAULT_COMMENTS = [
    """ 
    Bộ cứu sinh thoát hiểm xe hơi Elephant 3 trong 1
    Có tem kiểm định của Bộ Công An
    Gồm 3 chức năng:
    •	Phá kính thoát hiểm
    •	Cắt dây an toàn
    •	Đèn pin khẩn cấp
    Nhỏ gọn, để trên xe rất tiện, cần thiết cho mọi gia đình có ô tô.
    Liên hệ: 0834244983
    """,
    """
    Trên xe ô tô nên trang bị ngay bộ cứu sinh Elephant 3 trong 1.
    Sản phẩm có tem kiểm định của Bộ Công An.
    Tích hợp phá kính, cắt dây an toàn và đèn pin trong cùng một thiết bị.
    Dễ sử dụng trong các tình huống khẩn cấp như tai nạn hoặc ngập nước.
    Gọi/Zalo: 0834244983
    """,
    """
    Bộ cứu sinh Elephant 3 trong 1 cho xe hơi.
    Có tem kiểm định Bộ Công An.
    Thiết kế nhỏ gọn nhưng cực kỳ cần thiết khi gặp sự cố:
    Phá kính nhanh, cắt dây an toàn gọn, có đèn pin hỗ trợ ban đêm.
    Ai cần inbox hoặc liên hệ: 0834244983

    """,
    """
    Bộ cứu sinh thoát hiểm xe hơi Elephant 3 trong 1, sản phẩm nên có sẵn trên mọi xe ô tô.
    Có tem kiểm định của Bộ Công An.
    Tích hợp 3 chức năng trong 1 thiết bị: phá kính, cắt dây an toàn và đèn pin chiếu sáng.
    Thiết kế nhỏ gọn, dễ cất trong hộc xe hoặc taplo, sử dụng nhanh khi cần.
    Liên hệ: 0834244983

    """,
    """
    Elephant 3 trong 1 – Bộ cứu sinh chuyên dụng cho xe hơi.
    Sản phẩm có tem kiểm định Bộ Công An, đảm bảo chất lượng.
    Hỗ trợ thoát hiểm khi gặp sự cố kẹt cửa, tai nạn hoặc ngập nước.
    Phá kính nhanh, cắt dây an toàn sắc bén, có đèn pin dùng ban đêm.
    Ai quan tâm gọi/Zalo: 0834244983
    """,
]


# =====================================================================
# CLASS FACEBOOKBOT
# =====================================================================

class FacebookBot:
    def __init__(self, config, log_queue):
        self.config = config
        self.log_queue = log_queue
        self.driver = None
        self.wait = None
        self.is_logged_in = False
        self.should_stop = False

    def log(self, message, log_type='info'):
        try:
            timestamp = time.strftime("%H:%M:%S")
            self.log_queue.put({
                'timestamp': timestamp,
                'message': message,
                'type': log_type
            })
            print(f"[{timestamp}] {message}")
        except:
            pass

    def random_delay(self, min_sec, max_sec):
        time.sleep(random.uniform(min_sec, max_sec))

    def slow_type(self, element, text):
        for char in text:
            if self.should_stop:
                return
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def setup_driver(self):
        try:
            self.log("🔧 Đang khởi tạo Chrome driver...", 'info')

            chrome_options = Options()
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--lang=vi')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)

            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            self.log("✅ Chrome driver đã sẵn sàng!", 'success')
            return True

        except Exception as e:
            self.log(f"❌ Lỗi khởi tạo driver: {str(e)}", 'error')
            return False

    def login_facebook(self):
        if self.is_logged_in:
            self.log("✅ Đã đăng nhập từ trước", 'info')
            return True

        try:
            self.log("🔐 Đang đăng nhập Facebook...", 'step')
            self.driver.get("https://www.facebook.com")
            self.random_delay(5, 8)

            if self.should_stop:
                return False

            email_input = None
            email_selectors = [
                (By.ID, "email"),
                (By.NAME, "email"),
                (By.XPATH, "//input[@type='email']"),
                (By.XPATH, "//input[@placeholder='Email or phone number']"),
                (By.XPATH, "//input[@placeholder='Email hoặc số điện thoại']"),
            ]

            for by, selector in email_selectors:
                try:
                    email_input = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    if email_input:
                        self.log("✅ Tìm thấy ô email", 'info')
                        break
                except:
                    continue

            if not email_input:
                self.log("❌ Không tìm thấy ô email!", 'error')
                return False

            self.driver.execute_script("arguments[0].click();", email_input)
            self.random_delay(0.5, 1)
            email_input.clear()
            self.slow_type(email_input, self.config['email'])
            self.log("✅ Đã nhập email", 'info')
            self.random_delay(1, 2)

            if self.should_stop:
                return False

            password_input = None
            pass_selectors = [
                (By.ID, "pass"),
                (By.NAME, "pass"),
                (By.XPATH, "//input[@type='password']"),
            ]

            for by, selector in pass_selectors:
                try:
                    password_input = self.driver.find_element(by, selector)
                    if password_input:
                        self.log("✅ Tìm thấy ô mật khẩu", 'info')
                        break
                except:
                    continue

            if not password_input:
                self.log("❌ Không tìm thấy ô mật khẩu!", 'error')
                return False

            self.driver.execute_script("arguments[0].click();", password_input)
            self.random_delay(0.5, 1)
            password_input.clear()
            self.slow_type(password_input, self.config['password'])
            self.log("✅ Đã nhập mật khẩu", 'info')
            self.random_delay(1, 2)

            password_input.send_keys(Keys.RETURN)

            self.log("⏳ Đang chờ Facebook xử lý...", 'info')
            self.random_delay(10, 15)

            if self.should_stop:
                return False

            current_url = self.driver.current_url
            login_success = False

            if "login" not in current_url.lower():
                login_success = True

            try:
                self.driver.find_element(By.XPATH, "//input[@type='search']")
                login_success = True
            except:
                pass

            if "checkpoint" in current_url.lower():
                self.log("⚠️ Facebook yêu cầu xác minh! Có 60 giây...", 'warning')
                for i in range(60):
                    if self.should_stop:
                        return False
                    time.sleep(1)
                    new_url = self.driver.current_url
                    if "checkpoint" not in new_url.lower() and "login" not in new_url.lower():
                        self.log("✅ Đã xác minh thành công!", 'success')
                        login_success = True
                        break

            if login_success:
                self.log("✅ Đăng nhập thành công!", 'success')
                self.is_logged_in = True
                self.random_delay(2, 3)
                return True
            else:
                self.log("❌ Đăng nhập thất bại!", 'error')
                return False

        except Exception as e:
            self.log(f"❌ Lỗi đăng nhập: {str(e)}", 'error')
            return False

    def open_group_and_scroll(self, group_url, post_count=2):
        try:
            self.log(f"📂 Đang mở nhóm...", 'info')
            self.driver.get(group_url)
            self.random_delay(5, 7)

            if self.should_stop:
                return 0

            max_scrolls = 20
            target_forms = post_count

            for i in range(max_scrolls):
                if self.should_stop:
                    return 0

                current_forms = len(self.driver.find_elements(By.TAG_NAME, "form"))

                if current_forms >= target_forms:
                    self.log(f"✅ Đã load đủ {current_forms} form", 'success')
                    break

                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.random_delay(2, 3)

                if (i + 1) % 5 == 0:
                    self.log(f"   📊 Scroll lần {i+1}, có {current_forms} form", 'info')

            self.driver.execute_script("window.scrollTo(0, 0);")
            self.random_delay(1, 2)
            self.driver.execute_script("window.scrollTo(0, 300);")
            self.random_delay(1, 2)

            final_forms = len(self.driver.find_elements(By.TAG_NAME, "form"))
            self.log(f"✅ Load được {final_forms} bài để thử comment", 'success')
            return final_forms

        except Exception as e:
            self.log(f"❌ Lỗi mở nhóm: {str(e)}", 'error')
            return 0

    def find_and_click_comment_area(self, post_index):
        try:
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            if post_index >= len(forms):
                return None

            form = forms[post_index]
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", form
            )
            self.random_delay(1.5, 2)

            click_selectors = [
                (By.XPATH, ".//div[contains(@aria-label, 'Write a comment')]"),
                (By.XPATH, ".//div[contains(@aria-label, 'Viết bình luận')]"),
            ]

            for by, selector in click_selectors:
                try:
                    element = form.find_element(by, selector)
                    if element.is_displayed():
                        self.driver.execute_script("arguments[0].click();", element)
                        self.random_delay(1, 1.5)
                        return form
                except:
                    continue

            self.driver.execute_script("arguments[0].click();", form)
            self.random_delay(1, 1.5)
            return form

        except:
            return None

    def find_comment_box(self, post_index):
        try:
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            if post_index >= len(forms):
                return None

            form = forms[post_index]

            selectors = [
                (By.XPATH, ".//p[@contenteditable='true']"),
                (By.XPATH, ".//div[@contenteditable='true' and @role='textbox']"),
            ]

            for by, selector in selectors:
                try:
                    element = form.find_element(by, selector)
                    if element.is_displayed() and element.is_enabled():
                        return element
                except:
                    continue
            return None

        except:
            return None

    def type_multiline_comment(self, comment_box, text):
        """
        Ghi text co xuong dong vao Facebook comment box.
        Dung | de xuong dong.
        Chien luoc: click vao comment box, sau do dung pyperclip paste.
        Facebook xu ly newline tu clipboard khac voi keyboard events.
        """
        import pyperclip

        # Doi | thanh newline thuc su
        final_text = text.replace('|', '\n')

        self.log("Dang paste comment vao box...", 'info')

        # Click chinh xac vao comment box
        self.driver.execute_script("arguments[0].click();", comment_box)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].focus();", comment_box)
        time.sleep(0.3)

        # Xoa noi dung cu neu co
        comment_box.send_keys(Keys.CONTROL + 'a')
        time.sleep(0.2)
        comment_box.send_keys(Keys.DELETE)
        time.sleep(0.2)

        try:
            # Copy text vao clipboard va paste
            pyperclip.copy(final_text)
            time.sleep(0.2)

            # Click lai de dam bao focus
            self.driver.execute_script("arguments[0].click();", comment_box)
            time.sleep(0.3)

            # Paste bang Ctrl+V
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(0.8)

            # Kiem tra xem da co text chua
            current_text = self.driver.execute_script(
                "return arguments[0].innerText || arguments[0].textContent || '';",
                comment_box
            )
            if current_text and current_text.strip():
                self.log("Paste thanh cong: " + current_text[:30].replace('\n', ' '), 'success')
                return
            else:
                self.log("Paste khong co text, thu cach khac...", 'warning')
        except Exception as e:
            self.log("Loi paste: " + str(e), 'warning')

        # Fallback: Go tung dong bang send_keys thong thuong (khong xuong dong)
        # Neu khong paste duoc thi go het tren 1 dong
        self.log("Fallback: go text mot dong...", 'warning')
        self.driver.execute_script("arguments[0].click();", comment_box)
        time.sleep(0.3)
        fallback_text = text.replace('|', ' ')
        for char in fallback_text:
            if self.should_stop:
                return
            comment_box.send_keys(char)
            time.sleep(0.04)


    def upload_image_to_comment(self, post_index, image_path):
        """
        Upload hình ảnh vào comment box.
        Tìm nút đính kèm ảnh trong form và upload file.
        """
        try:
            if not image_path or not os.path.exists(image_path):
                self.log(f"⚠️ File ảnh không tồn tại: {image_path}", 'warning')
                return False

            forms = self.driver.find_elements(By.TAG_NAME, "form")
            if post_index >= len(forms):
                return False

            form = forms[post_index]

            # Tìm input file ẩn trong form comment
            image_input_selectors = [
                (By.XPATH, ".//input[@type='file' and contains(@accept,'image')]"),
                (By.XPATH, ".//input[@type='file']"),
            ]

            file_input = None
            for by, selector in image_input_selectors:
                try:
                    inputs = form.find_elements(by, selector)
                    for inp in inputs:
                        file_input = inp
                        break
                    if file_input:
                        break
                except:
                    continue

            # Nếu không tìm thấy trong form, tìm nút ảnh rồi click để hiện input
            if not file_input:
                self.log("🔍 Tìm nút đính kèm ảnh...", 'info')
                photo_btn_selectors = [
                    (By.XPATH, ".//div[@aria-label='Photo/video']"),
                    (By.XPATH, ".//div[@aria-label='Ảnh/video']"),
                    (By.XPATH, ".//div[contains(@aria-label,'Photo')]"),
                    (By.XPATH, ".//div[contains(@aria-label,'photo')]"),
                    (By.XPATH, ".//div[contains(@aria-label,'Ảnh')]"),
                    (By.XPATH, ".//i[contains(@class,'photo')]/../.."),
                ]

                for by, selector in photo_btn_selectors:
                    try:
                        btn = form.find_element(by, selector)
                        if btn.is_displayed():
                            self.driver.execute_script("arguments[0].click();", btn)
                            self.random_delay(1, 2)
                            self.log("✅ Đã click nút thêm ảnh", 'info')
                            break
                    except:
                        continue

                # Thử tìm lại input sau khi click
                try:
                    file_input = self.driver.find_element(
                        By.XPATH, "//input[@type='file' and contains(@accept,'image')]"
                    )
                except:
                    try:
                        file_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
                    except:
                        pass

            if file_input:
                # Đảm bảo input có thể nhận file (bỏ ẩn nếu cần)
                self.driver.execute_script(
                    "arguments[0].style.display='block'; arguments[0].style.visibility='visible';",
                    file_input
                )
                file_input.send_keys(image_path)
                self.log(f"✅ Đã upload ảnh: {os.path.basename(image_path)}", 'success')
                self.random_delay(2, 4)  # Chờ ảnh upload
                return True
            else:
                self.log("⚠️ Không tìm thấy input file để upload ảnh", 'warning')
                return False

        except Exception as e:
            self.log(f"⚠️ Lỗi upload ảnh: {str(e)}", 'warning')
            return False

    def comment_on_group(self, group_url, post_count=2):
        try:
            available_posts = self.open_group_and_scroll(group_url, post_count * 2)
            if available_posts == 0:
                self.log("⚠️ Không tìm thấy bài viết", 'warning')
                return 0

            comments = self.config['comments']
            image_paths = self.config.get('image_paths', [])
            delay_minutes = self.config['delayMinutes']
            success_count = 0
            post_index = 0
            comment_index = 0

            while success_count < post_count and post_index < available_posts:
                if self.should_stop:
                    break

                comment_data = comments[comment_index % len(comments)]
                comment_text = comment_data['text']
                comment_image = comment_data.get('image', '')

                # Kiểm tra xem có hình ảnh chung không (từ danh sách ảnh chung)
                if not comment_image and image_paths:
                    comment_image = image_paths[comment_index % len(image_paths)]

                has_image = bool(comment_image and os.path.exists(comment_image))

                display_text = comment_text[:40].replace('|', ' ') + "..." if len(comment_text) > 40 else comment_text.replace('|', ' ')
                img_info = f" + 🖼️ ảnh" if has_image else ""
                self.log(f"📝 Thử bài {post_index+1} (đã comment: {success_count}/{post_count}): {display_text}{img_info}", 'info')

                form = self.find_and_click_comment_area(post_index)
                if not form:
                    self.log(f"⚠️ Không thể click bài {post_index+1}, chuyển bài tiếp...", 'warning')
                    post_index += 1
                    continue

                comment_box = self.find_comment_box(post_index)
                if not comment_box:
                    self.log(f"⚠️ Không tìm thấy ô comment bài {post_index+1}, chuyển bài tiếp...", 'warning')
                    post_index += 1
                    continue

                try:
                    # Upload ảnh trước nếu có
                    if has_image:
                        self.log(f"🖼️ Đang upload ảnh...", 'info')
                        img_uploaded = self.upload_image_to_comment(post_index, comment_image)
                        if img_uploaded:
                            self.log("✅ Upload ảnh thành công, chờ Facebook xử lý...", 'success')
                            self.random_delay(3, 5)  # Chờ ảnh upload xong hoàn toàn
                        else:
                            self.log("⚠️ Upload ảnh thất bại, tiếp tục với text", 'warning')

                    # Tim lai comment box sau upload anh
                    comment_box = self.find_comment_box(post_index)
                    if not comment_box:
                        self.log(f"Khong tim thay comment box, chuyen bai tiep...", 'warning')
                        post_index += 1
                        continue

                    # Paste text vao comment box (co xuong dong neu co |)
                    if comment_text:
                        self.type_multiline_comment(comment_box, comment_text)
                        self.random_delay(1.5, 2.5)

                    if self.should_stop:
                        break

                    # Kiem tra text da co trong box chua truoc khi Enter
                    try:
                        box_content = self.driver.execute_script(
                            "return arguments[0].innerText || arguments[0].textContent || '';",
                            comment_box
                        )
                        self.log("Noi dung box: " + (box_content[:30] if box_content else "(trong)"), 'info')
                    except:
                        pass

                    # Gui comment - chi 1 lan Enter duy nhat
                    if comment_box:
                        self.driver.execute_script("arguments[0].focus();", comment_box)
                        time.sleep(0.3)
                        comment_box.send_keys(Keys.RETURN)
                        self.random_delay(2, 3)
                        success_count += 1
                        comment_index += 1
                        img_status = " + ảnh" if has_image else ""
                        self.log(f"✅ Đã comment bài {post_index+1}{img_status} - Tổng: {success_count}/{post_count}", 'success')

                        if success_count < post_count and not self.should_stop:
                            self.log(f"⏱️ Chờ {delay_minutes} phút trước bài tiếp...", 'info')
                            for _ in range(delay_minutes * 60):
                                if self.should_stop:
                                    break
                                time.sleep(1)
                    else:
                        self.log(f"⚠️ Mất ô comment sau khi gõ, chuyển bài tiếp...", 'warning')

                except Exception as e:
                    self.log(f"⚠️ Lỗi comment bài {post_index+1}: {str(e)}", 'warning')

                post_index += 1

            if success_count > 0:
                self.log(f"📊 Kết quả: {success_count}/{post_count} bài thành công", 'success')
            else:
                self.log(f"⚠️ Không comment được bài nào trong nhóm này", 'warning')

            return success_count

        except Exception as e:
            self.log(f"❌ Lỗi comment nhóm: {str(e)}", 'error')
            return 0

    def run_session(self, session_name):
        try:
            self.log(f"{'='*50}", 'step')
            self.log(f"🎯 BẮT ĐẦU PHIÊN {session_name.upper()}", 'step')
            self.log(f"{'='*50}", 'step')

            groups = self.config['groups']
            group_delay = self.config['groupDelayMinutes']
            total_success = 0

            for idx, group_url in enumerate(groups):
                if self.should_stop:
                    break

                self.log(f"\n📍 Nhóm {idx+1}/{len(groups)}", 'step')

                success = self.comment_on_group(group_url, post_count=2)
                total_success += success

                if idx < len(groups) - 1 and not self.should_stop:
                    self.log(f"⏱️ Chờ {group_delay} phút trước nhóm tiếp...", 'info')
                    for _ in range(group_delay * 60):
                        if self.should_stop:
                            break
                        time.sleep(1)

            self.log(f"\n{'='*50}", 'success')
            self.log(f"✅ HOÀN THÀNH {session_name.upper()}", 'success')
            self.log(f"   → Thành công: {total_success} bài", 'success')
            self.log(f"{'='*50}", 'success')

        except Exception as e:
            self.log(f"❌ Lỗi: {str(e)}", 'error')

    def cleanup(self):
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass


# =====================================================================
# WIDGET COMMENT: Text đa dòng + Upload ảnh
# =====================================================================

class CommentWidget(ttk.Frame):
    """
    Widget một comment gồm:
    - Text area đa dòng (dùng | để xuống dòng)
    - Nút chọn ảnh
    - Hiển thị tên ảnh đã chọn
    """
    def __init__(self, parent, index, **kwargs):
        super().__init__(parent, **kwargs)
        self.index = index
        self.image_path = tk.StringVar(value="")
        self._build()

    def _build(self):
        # Số thứ tự
        ttk.Label(self, text=f"{self.index}.", width=3, font=("Arial", 8, "bold")).grid(
            row=0, column=0, sticky='nw', padx=(0, 2), pady=2
        )

        # Frame bên phải chứa text + ảnh
        right_f = ttk.Frame(self)
        right_f.grid(row=0, column=1, sticky='ew')
        right_f.columnconfigure(0, weight=1)

        # Text area
        self.text_widget = tk.Text(right_f, width=35, height=4, wrap='word',
                                   font=("Arial", 9), relief='solid', borderwidth=1)
        self.text_widget.grid(row=0, column=0, columnspan=3, sticky='ew', pady=(0, 3))

        # Placeholder hint
        hint = ttk.Label(right_f,
            text="↵ Dùng | để xuống dòng  (VD: Dòng 1|Dòng 2|Dòng 3)",
            font=("Arial", 7), foreground="#888"
        )
        hint.grid(row=1, column=0, columnspan=3, sticky='w', pady=(0, 2))

        # Row ảnh
        img_row = ttk.Frame(right_f)
        img_row.grid(row=2, column=0, columnspan=3, sticky='ew')

        ttk.Button(img_row, text="🖼️ Chọn ảnh", command=self._choose_image, width=12).pack(side='left')
        self.img_label = ttk.Label(img_row, text="Chưa chọn ảnh", foreground="#888",
                                    font=("Arial", 8))
        self.img_label.pack(side='left', padx=5)
        ttk.Button(img_row, text="✖", command=self._clear_image, width=3).pack(side='left')

    def _choose_image(self):
        path = filedialog.askopenfilename(
            title="Chọn ảnh cho comment",
            filetypes=[
                ("Hình ảnh", "*.jpg *.jpeg *.png *.gif *.webp *.bmp"),
                ("Tất cả", "*.*")
            ]
        )
        if path:
            self.image_path.set(path)
            fname = os.path.basename(path)
            display = fname if len(fname) <= 25 else fname[:22] + "..."
            self.img_label.config(text=f"✅ {display}", foreground="#00aa00")

    def _clear_image(self):
        self.image_path.set("")
        self.img_label.config(text="Chưa chọn ảnh", foreground="#888")

    def get_text(self):
        return self.text_widget.get("1.0", 'end').strip()

    def get_image(self):
        return self.image_path.get().strip()

    def set_text(self, text):
        self.text_widget.delete("1.0", 'end')
        self.text_widget.insert("1.0", text)


# =====================================================================
# CLASS GUI
# =====================================================================

class FacebookSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Facebook Auto Scheduler Bot v2.0 - Hỗ trợ ảnh & Xuống dòng")
        self.root.geometry("1100x800")
        self.root.resizable(True, True)

        self.bot_running = False
        self.scheduler_running = False
        self.bot_instance = None
        self.log_queue = queue.Queue()

        self.setup_ui()
        self.process_log_queue()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Scrollable main
        main_canvas = tk.Canvas(self.root)
        main_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        main_frame = ttk.Frame(main_canvas, padding="10")

        main_canvas.create_window((0, 0), window=main_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)

        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Mouse wheel scroll
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # HEADER
        header = ttk.Frame(main_frame)
        header.grid(row=0, column=0, columnspan=2, pady=(0, 8), sticky='ew')

        ttk.Label(header, text="🤖 Facebook Auto Scheduler Bot v2.0",
                 font=("Arial", 15, "bold"), foreground="#667eea").pack()
        ttk.Label(header,
            text="✅ Hỗ trợ: Comment có hình ảnh  |  Xuống dòng bằng ký tự |  |  Sáng & Chiều tự động",
            font=("Arial", 9), foreground="#333"
        ).pack()

        # INFO
        info = ttk.LabelFrame(main_frame, text="📅 Lịch trình & Hướng dẫn", padding="8")
        info.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 8))

        ttk.Label(info,
            text="• Sáng (9:30) & Chiều (14:00): 2 bài/nhóm  |  Ký tự | trong comment = xuống dòng mới  |  Mỗi comment có thể có ảnh riêng",
            foreground="#333", font=("Arial", 9)
        ).pack()

        # =========================================================
        # TRÁI
        # =========================================================
        left = ttk.Frame(main_frame)
        left.grid(row=2, column=0, sticky='nsew', padx=(0, 5))

        # Email
        ttk.Label(left, text="📧 Email/SĐT:", font=("Arial", 9, "bold")).pack(anchor='w')
        self.email_var = tk.StringVar()
        ttk.Entry(left, textvariable=self.email_var, width=42).pack(anchor='w', pady=(2, 8))

        # Password
        ttk.Label(left, text="🔐 Mật khẩu:", font=("Arial", 9, "bold")).pack(anchor='w')
        self.password_var = tk.StringVar()
        ttk.Entry(left, textvariable=self.password_var, show="*", width=42).pack(anchor='w', pady=(2, 8))

        # Time
        time_f = ttk.LabelFrame(left, text="⏰ Thời gian tự động", padding="8")
        time_f.pack(fill='x', pady=(0, 8))

        t1 = ttk.Frame(time_f)
        t1.pack(fill='x')
        ttk.Label(t1, text="Sáng:").pack(side='left')
        self.morning_var = tk.StringVar(value="09:30")
        ttk.Entry(t1, textvariable=self.morning_var, width=10).pack(side='left', padx=5)

        t2 = ttk.Frame(time_f)
        t2.pack(fill='x', pady=(5, 0))
        ttk.Label(t2, text="Chiều:").pack(side='left')
        self.afternoon_var = tk.StringVar(value="14:00")
        ttk.Entry(t2, textvariable=self.afternoon_var, width=10).pack(side='left', padx=5)

        # Groups
        grp_f = ttk.LabelFrame(left, text="🔗 Nhóm Facebook (tối đa 25 nhóm)", padding="8")
        grp_f.pack(fill='both', expand=True, pady=(0, 8))

        grp_canvas = tk.Canvas(grp_f, height=120, bg="white")
        grp_scroll = ttk.Scrollbar(grp_f, orient="vertical", command=grp_canvas.yview)
        self.groups_inner = ttk.Frame(grp_canvas)

        grp_canvas.create_window((0, 0), window=self.groups_inner, anchor="nw")
        grp_canvas.configure(yscrollcommand=grp_scroll.set)

        grp_canvas.pack(side='left', fill='both', expand=True)
        grp_scroll.pack(side='right', fill='y')

        self.group_entries = []
        for default_group in DEFAULT_GROUPS:
            self.add_group_entry(default_value=default_group)

        grp_btn = ttk.Frame(grp_f)
        grp_btn.pack(fill='x', pady=(5, 0))
        ttk.Button(grp_btn, text="➕ Thêm nhóm", command=lambda: self.add_group_entry(), width=14).pack(side='left', padx=(0, 3))
        ttk.Button(grp_btn, text="➖ Xóa cuối", command=self.remove_group_entry, width=12).pack(side='left')

        self.groups_inner.bind("<Configure>", lambda e: grp_canvas.configure(scrollregion=grp_canvas.bbox("all")))

        # =========================================================
        # COMMENTS - Mỗi comment có Text + Ảnh
        # =========================================================
        cmt_f = ttk.LabelFrame(left,
            text="💬 Danh sách Comment (hỗ trợ xuống dòng | và đính kèm ảnh)",
            padding="8"
        )
        cmt_f.pack(fill='both', expand=True, pady=(0, 8))

        # Hint box
        hint_frame = tk.Frame(cmt_f, bg="#fffbe6", bd=1, relief='solid')
        hint_frame.pack(fill='x', pady=(0, 6))
        ttk.Label(hint_frame,
            text="💡 Dùng ký tự | để xuống dòng trong comment\n"
                 "   Ví dụ: Bộ dụng cụ thoát hiểm xe|Gồm 3 chức năng:|* Phá kính|* Cắt dây|Liên hệ: 0xxx",
            font=("Courier New", 8), justify='left', background="#fffbe6", foreground="#664d00"
        ).pack(anchor='w', padx=5, pady=3)

        cmt_canvas = tk.Canvas(cmt_f, height=280, bg="white")
        cmt_scroll = ttk.Scrollbar(cmt_f, orient="vertical", command=cmt_canvas.yview)
        self.comments_inner = ttk.Frame(cmt_canvas)

        cmt_canvas.create_window((0, 0), window=self.comments_inner, anchor="nw")
        cmt_canvas.configure(yscrollcommand=cmt_scroll.set)

        cmt_canvas.pack(side='left', fill='both', expand=True)
        cmt_scroll.pack(side='right', fill='y')

        self.comment_widgets = []
        for default_comment in DEFAULT_COMMENTS:
            self.add_comment_widget(default_value=default_comment)

        cmt_btn = ttk.Frame(cmt_f)
        cmt_btn.pack(fill='x', pady=(5, 0))
        ttk.Button(cmt_btn, text="➕ Thêm comment", command=lambda: self.add_comment_widget(), width=16).pack(side='left', padx=(0, 3))
        ttk.Button(cmt_btn, text="➖ Xóa cuối", command=self.remove_comment_widget, width=12).pack(side='left')

        self.comments_inner.bind("<Configure>", lambda e: cmt_canvas.configure(scrollregion=cmt_canvas.bbox("all")))

        # Delay
        delay_f = ttk.Frame(left)
        delay_f.pack(fill='x', pady=(0, 8))

        ttk.Label(delay_f, text="⏱️ Delay bài:").pack(side='left')
        self.delay_var = tk.StringVar(value="2")
        ttk.Entry(delay_f, textvariable=self.delay_var, width=5).pack(side='left', padx=3)
        ttk.Label(delay_f, text="phút  |  Delay nhóm:").pack(side='left', padx=(5, 0))
        self.group_delay_var = tk.StringVar(value="5")
        ttk.Entry(delay_f, textvariable=self.group_delay_var, width=5).pack(side='left', padx=3)
        ttk.Label(delay_f, text="phút").pack(side='left')

        # Buttons
        btn_f = ttk.Frame(left)
        btn_f.pack(fill='x', pady=(10, 0))

        self.start_btn = ttk.Button(btn_f, text="🚀 BẮT ĐẦU", command=self.start_scheduler)
        self.start_btn.pack(side='left', fill='x', expand=True, padx=(0, 3))

        self.stop_btn = ttk.Button(btn_f, text="⏹️ DỪNG", command=self.stop_scheduler, state='disabled')
        self.stop_btn.pack(side='left', fill='x', expand=True)

        # Nút test ngay
        ttk.Button(btn_f, text="▶ CHẠY NGAY (TEST)",
                   command=self.run_now_test).pack(side='left', fill='x', expand=True, padx=(3, 0))

        # =========================================================
        # PHẢI - Status + Log
        # =========================================================
        right = ttk.Frame(main_frame)
        right.grid(row=2, column=1, sticky='nsew', padx=(5, 0))

        stat = ttk.LabelFrame(right, text="📊 Trạng thái", padding="8")
        stat.pack(fill='x', pady=(0, 8))

        s1 = ttk.Frame(stat)
        s1.pack(fill='x')
        ttk.Label(s1, text="Trạng thái:", font=("Arial", 9, "bold")).pack(side='left')
        self.status_label = ttk.Label(s1, text="Chờ", foreground="#ff4444")
        self.status_label.pack(side='left', padx=(10, 0))

        s2 = ttk.Frame(stat)
        s2.pack(fill='x', pady=(3, 0))
        ttk.Label(s2, text="Phiên tiếp:", font=("Arial", 9, "bold")).pack(side='left')
        self.next_session_label = ttk.Label(s2, text="-")
        self.next_session_label.pack(side='left', padx=(10, 0))

        s3 = ttk.Frame(stat)
        s3.pack(fill='x', pady=(3, 0))
        ttk.Label(s3, text="Tổng nhóm:", font=("Arial", 9, "bold")).pack(side='left')
        self.total_groups_label = ttk.Label(s3, text=str(len(DEFAULT_GROUPS)))
        self.total_groups_label.pack(side='left', padx=(10, 0))

        s4 = ttk.Frame(stat)
        s4.pack(fill='x', pady=(3, 0))
        ttk.Label(s4, text="Tổng comment:", font=("Arial", 9, "bold")).pack(side='left')
        self.total_comments_label = ttk.Label(s4, text=str(len(DEFAULT_COMMENTS)))
        self.total_comments_label.pack(side='left', padx=(10, 0))

        log_f = ttk.LabelFrame(right, text="📋 Nhật ký hoạt động", padding="8")
        log_f.pack(fill='both', expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_f, width=48, height=32,
            bg="#1e1e1e", fg="#00ff00",
            font=("Courier New", 8), wrap='word'
        )
        self.log_text.pack(fill='both', expand=True)

        self.log_text.tag_config("info", foreground="#00bfff")
        self.log_text.tag_config("success", foreground="#00ff00")
        self.log_text.tag_config("warning", foreground="#ffa500")
        self.log_text.tag_config("error", foreground="#ff4444")
        self.log_text.tag_config("step", foreground="#ffff00")

        main_frame.update_idletasks()
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))

    # =========================================================
    # GROUP METHODS
    # =========================================================

    def add_group_entry(self, default_value=""):
        if len(self.group_entries) >= 25:
            messagebox.showwarning("Cảnh báo", "Tối đa 25 nhóm!")
            return

        f = ttk.Frame(self.groups_inner)
        f.pack(fill='x', pady=1)

        ttk.Label(f, text=f"{len(self.group_entries)+1}.", width=3).pack(side='left')
        e = ttk.Entry(f, width=42)
        e.pack(side='left', fill='x', expand=True)
        if default_value:
            e.insert(0, default_value)
        self.group_entries.append(e)

    def remove_group_entry(self):
        if len(self.group_entries) <= 1:
            messagebox.showwarning("Cảnh báo", "Cần ít nhất 1 nhóm!")
            return
        self.group_entries.pop().master.destroy()

    # =========================================================
    # COMMENT WIDGET METHODS
    # =========================================================

    def add_comment_widget(self, default_value=""):
        if len(self.comment_widgets) >= 20:
            messagebox.showwarning("Cảnh báo", "Tối đa 20 comment!")
            return

        idx = len(self.comment_widgets) + 1
        separator = ttk.Separator(self.comments_inner, orient='horizontal')
        separator.pack(fill='x', pady=2)

        widget = CommentWidget(self.comments_inner, index=idx)
        widget.pack(fill='x', pady=2, padx=2)

        if default_value:
            widget.set_text(default_value)

        self.comment_widgets.append(widget)
        if hasattr(self, 'total_comments_label'):
            self.total_comments_label.config(text=str(len(self.comment_widgets)))

    def remove_comment_widget(self):
        if len(self.comment_widgets) <= 1:
            messagebox.showwarning("Cảnh báo", "Cần ít nhất 1 comment!")
            return
        w = self.comment_widgets.pop()
        # Xóa widget và separator
        w.master.destroy() if w.master != self.comments_inner else w.destroy()
        w.destroy()
        self.total_comments_label.config(text=str(len(self.comment_widgets)))

    # =========================================================
    # LOG
    # =========================================================

    def add_log(self, log_data):
        ts = log_data.get('timestamp', '')
        msg = log_data.get('message', '')
        typ = log_data.get('type', 'info')
        self.log_text.insert('end', f"[{ts}] {msg}\n", typ)
        self.log_text.see('end')

    def process_log_queue(self):
        try:
            while True:
                self.add_log(self.log_queue.get_nowait())
        except queue.Empty:
            pass
        self.root.after(100, self.process_log_queue)

    # =========================================================
    # VALIDATION & CONFIG
    # =========================================================

    def validate_inputs(self):
        if not self.email_var.get().strip():
            messagebox.showerror("Lỗi", "Nhập Email/SĐT!")
            return False
        if not self.password_var.get().strip():
            messagebox.showerror("Lỗi", "Nhập mật khẩu!")
            return False

        groups = [e.get().strip() for e in self.group_entries if e.get().strip()]
        if not groups:
            messagebox.showerror("Lỗi", "Nhập ít nhất 1 nhóm!")
            return False

        comments = [
            {'text': w.get_text(), 'image': w.get_image()}
            for w in self.comment_widgets
            if w.get_text()
        ]
        if not comments:
            messagebox.showerror("Lỗi", "Nhập ít nhất 1 comment!")
            return False

        try:
            int(self.delay_var.get())
            int(self.group_delay_var.get())
        except:
            messagebox.showerror("Lỗi", "Delay phải là số!")
            return False

        return True

    def build_config(self):
        groups = [e.get().strip() for e in self.group_entries if e.get().strip()]
        comments = [
            {'text': w.get_text(), 'image': w.get_image()}
            for w in self.comment_widgets
            if w.get_text()
        ]

        return {
            'email': self.email_var.get().strip(),
            'password': self.password_var.get().strip(),
            'groups': groups,
            'comments': comments,
            'image_paths': [],  # Ảnh chung (không dùng nếu mỗi comment có ảnh riêng)
            'morningTime': self.morning_var.get().strip(),
            'afternoonTime': self.afternoon_var.get().strip(),
            'delayMinutes': int(self.delay_var.get()),
            'groupDelayMinutes': int(self.group_delay_var.get())
        }

    # =========================================================
    # START / STOP / TEST
    # =========================================================

    def start_scheduler(self):
        if not self.validate_inputs():
            return

        config = self.build_config()

        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="Đang chạy", foreground="#00ff00")
        self.total_groups_label.config(text=str(len(config['groups'])))

        self.bot_running = True
        threading.Thread(target=self.run_scheduler, args=(config,), daemon=True).start()

    def run_now_test(self):
        """Chạy ngay 1 lần để test (không cần đợi lịch)"""
        if self.bot_running:
            messagebox.showwarning("Cảnh báo", "Bot đang chạy! Dừng trước khi test.")
            return
        if not self.validate_inputs():
            return

        config = self.build_config()

        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="Đang test...", foreground="#ffa500")

        self.bot_running = True

        def test_run():
            bot = FacebookBot(config, self.log_queue)
            self.bot_instance = bot

            if not bot.setup_driver():
                self.root.after(0, self.reset_ui)
                return
            if not bot.login_facebook():
                bot.cleanup()
                self.root.after(0, self.reset_ui)
                return

            bot.run_session("TEST - Chạy ngay")
            bot.cleanup()
            self.bot_running = False
            self.root.after(0, self.reset_ui)

        threading.Thread(target=test_run, daemon=True).start()

    def stop_scheduler(self):
        if messagebox.askyesno("Xác nhận", "Dừng bot?"):
            self.bot_running = False
            self.scheduler_running = False

            if self.bot_instance:
                self.bot_instance.should_stop = True

            schedule.clear()

            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.status_label.config(text="Đã dừng", foreground="#ff4444")

            self.log_queue.put({
                'timestamp': time.strftime("%H:%M:%S"),
                'message': '⏹️ Đã dừng bot',
                'type': 'warning'
            })

    def run_scheduler(self, config):
        self.scheduler_running = True
        self.bot_instance = FacebookBot(config, self.log_queue)

        if not self.bot_instance.setup_driver():
            self.scheduler_running = False
            self.root.after(0, self.reset_ui)
            return

        if not self.bot_instance.login_facebook():
            self.scheduler_running = False
            self.bot_instance.cleanup()
            self.root.after(0, self.reset_ui)
            return

        morning = config['morningTime']
        afternoon = config['afternoonTime']

        def morning_job():
            if self.bot_running and not self.bot_instance.should_stop:
                self.bot_instance.run_session("Buổi sáng")

        def afternoon_job():
            if self.bot_running and not self.bot_instance.should_stop:
                self.bot_instance.run_session("Buổi chiều")

        schedule.every().day.at(morning).do(morning_job)
        schedule.every().day.at(afternoon).do(afternoon_job)

        self.bot_instance.log(f"📅 Lịch đã đặt: Sáng {morning} | Chiều {afternoon}", 'info')
        self.bot_instance.log(f"📌 {len(config['groups'])} nhóm | {len(config['comments'])} loại comment", 'info')

        has_images = any(c.get('image') for c in config['comments'])
        if has_images:
            self.bot_instance.log("🖼️ Phát hiện comment có ảnh đính kèm", 'success')

        self.root.after(0, lambda: self.update_next_session(config))

        while self.bot_running and self.scheduler_running:
            schedule.run_pending()
            time.sleep(1)

        self.bot_instance.log("🛑 Đã dừng scheduler", 'warning')
        self.bot_instance.cleanup()

    def update_next_session(self, config):
        try:
            now = datetime.now()
            morning = datetime.strptime(config['morningTime'], "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            afternoon = datetime.strptime(config['afternoonTime'], "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )

            if now.time() < morning.time():
                txt = f"Sáng {config['morningTime']}"
            elif now.time() < afternoon.time():
                txt = f"Chiều {config['afternoonTime']}"
            else:
                txt = f"Sáng {config['morningTime']} (ngày mai)"

            self.next_session_label.config(text=txt)
        except:
            pass

    def reset_ui(self):
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Sẵn sàng", foreground="#888")

    def on_closing(self):
        if self.bot_running:
            if messagebox.askokcancel("Thoát", "Bot đang chạy. Thoát?"):
                self.bot_running = False
                if self.bot_instance:
                    self.bot_instance.should_stop = True
                    self.bot_instance.cleanup()
                self.root.destroy()
        else:
            self.root.destroy()


# =====================================================================
# MAIN
# =====================================================================

def main():
    print("=" * 65)
    print("🤖 FACEBOOK AUTO SCHEDULER BOT v2.0")
    print("=" * 65)
    print("✅ Khởi động thành công!")
    print("🆕 Tính năng mới:")
    print("   🖼️  Comment có hình ảnh đính kèm")
    print("   ↵   Xuống dòng bằng ký tự | trong text")
    print("   ▶   Nút 'Chạy ngay' để test nhanh")
    print("📌 Ví dụ comment xuống dòng:")
    print("   Bộ dụng cụ thoát hiểm|Gồm 3 chức năng:|* Phá kính|* Cắt dây|Liên hệ: 0xxx")
    print("=" * 65)

    root = tk.Tk()
    app = FacebookSchedulerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()