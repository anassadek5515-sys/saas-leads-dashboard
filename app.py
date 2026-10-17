import streamlit as st
import smtplib
import imaplib
import email
import time
import random
import re
import logging
import pandas as pd
import matplotlib.pyplot as plt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# إعداد ملف تسجيل الأنشطة والأخطاء
logging.basicConfig(
    filename="outreach.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

st.set_page_config(page_title="Autonomous B2B SaaS Engine", page_icon="⚡", layout="wide")

# 1. العنوان الرئيسي
st.title("⚡ منصة المبيعات الذاتية والتحليلات (B2B SaaS Engine)")

# الحسابات الفعلية
if "accounts" not in st.session_state:
    st.session_state.accounts = [
        {"provider": "gmail", "email": "Anassadek5525@gmail.com", "password": "atig ffwp ddxd vgcf", "sent_today": 0, "status": "active"},
        {"provider": "gmail", "email": "Anassadek5535@gmail.com", "password": "mdfz guvt hqdv navv", "sent_today": 0, "status": "active"},
        {"provider": "outlook", "email": "Anassadek5565@outlook.com", "password": "Anas#$@()501093083973=55", "sent_today": 0, "status": "active"},
        {"provider": "outlook", "email": "Anassadek5585@outlook.com", "password": "Anas#$@()501093083973", "sent_today": 0, "status": "active"},
        {"provider": "outlook", "email": "Anassadek5575@outlook.com", "password": "Anas#$@()501093083973=55", "sent_today": 0, "status": "active"}
    ]

# العدادات الفعلية تبدأ من الصفر
if "crm_stats" not in st.session_state:
    st.session_state.crm_stats = {
        "sent": 0,
        "no_reply": 0,
        "replied": 0,
        "demo": 0,
        "closed": 0
    }

def is_valid_email(email_str):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email_str) is not None

def auto_discover_200_leads(niche):
    raw_leads = [f"contact@{niche}store{i}.com" for i in range(1, 201)]
    return [e for e in raw_leads if is_valid_email(e)]

# قارئ الردود الفعلي من الـ Inbox
def fetch_and_classify_replies():
    replied_count = 0
    demo_count = 0
    closed_count = 0

    for acc in st.session_state.accounts:
        p = acc["provider"]
        e = acc["email"]
        pwd = acc["password"]
        
        imap_srv = "imap.gmail.com" if p == "gmail" else "outlook.office365.com"
        
        try:
            mail = imaplib.IMAP4_SSL(imap_srv)
            mail.login(e, pwd)
            mail.select("inbox")
            
            status, messages = mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()
            
            for e_id in email_ids:
                _, msg_data = mail.fetch(e_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        body_text = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body_text += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        else:
                            body_text = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                        
                        body_lower = body_text.lower()
                        
                        if any(w in body_lower for w in ["demo", "ديمو", "تجربة", "شرح", "try"]):
                            demo_count += 1
                            replied_count += 1
                        elif any(w in body_lower for w in ["subscribe", "buy", "شراء", "اشتراك", "موافق", "deal", "invoice", "200$"]):
                            closed_count += 1
                            replied_count += 1
                        else:
                            replied_count += 1

            mail.logout()
        except Exception as ex:
            logging.error(f"IMAP Read Error on {e}: {ex}")

    st.session_state.crm_stats['replied'] += replied_count
    st.session_state.crm_stats['demo'] += demo_count
    st.session_state.crm_stats['closed'] += closed_count
    st.session_state.crm_stats['no_reply'] = max(0, st.session_state.crm_stats['sent'] - st.session_state.crm_stats['replied'])

# -------------------------------------------------------------
# 🛡️ 2. حالة الحسابات الخمسة (في شريط علوي صغير بدون زحمة)
# -------------------------------------------------------------
active_count = sum(1 for a in st.session_state.accounts if a["status"] == "active")
with st.expander(f"🛡️ حالة الحسابات والإرسال اليومي (الحسابات النشطة: {active_count}/{len(st.session_state.accounts)})"):
    for acc in st.session_state.accounts:
        st.write(f"• **{acc['email']}** ➔ المرسل اليوم: `{acc['sent_today']}/40` | الحالة: `{acc['status']}`")

st.markdown("---")

# -------------------------------------------------------------
# 📊 3. لوحة تحكم المبيعات والصفقات (معدلة خصيصاً للموبايل)
# -------------------------------------------------------------
st.subheader("🎯 لوحة المبيعات والصفقات الفعلية (Live Sales Dashboard)")

crm = st.session_state.crm_stats

# عرض الأرقام بطريقة متجاوبة جداً
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("إجمالي الإيميلات", f"{crm['sent']}")
m2.metric("في انتظار الرد ⏳", f"{crm['no_reply']}")
m3.metric("ردود فعلية 📩", f"{crm['replied']}")
m4.metric("طلبات الديمو 💻", f"{crm['demo']}")
m5.metric("عقود مؤكدة 🎯", f"{crm['closed']}", f"${crm['closed']*200}/شهرياً")

st.write("")
if st.button("🔄 فحص الـ Inbox وتحديث الردود الحقيقية"):
    with st.spinner("جاري فحص الحسابات وقراءة الرسائل الجديدة..."):
        fetch_and_classify_replies()
    st.success("تم تحديث البيانات بنجاح!")

# رسم بياني واضح ومناسب للموبايل
fig, ax = plt.subplots(figsize=(8, 4))
categories = ['المرسل', 'لم يردوا', 'ردوا', 'الديمو', 'مغلقة']
values = [crm['sent'], crm['no_reply'], crm['replied'], crm['demo'], crm['closed']]
colors = ['#2980B9', '#7F8C8D', '#F39C12', '#D35400', '#27AE60']

ax.bar(categories, values, color=colors, width=0.5)
ax.set_title('مسار المبيعات الفعلي (Conversion Funnel)', fontsize=12, fontweight='bold')
ax.grid(axis='y', linestyle='--', alpha=0.4)
st.pyplot(fig)

st.markdown("---")

# -------------------------------------------------------------
# 🚀 4. إعدادات الحملة والتشغيل
# -------------------------------------------------------------
st.subheader("🚀 إعدادات حملة الاستحواذ الآلي")

target_niche = st.text_input("مجال الشركات المستهدفة (مثال: ecommerce):", "ecommerce")
subject = st.text_input("عنوان الرسالة البريدية", "تحليل مخزون متجرك وزيادة أرباحك بنسبة 30%")

c_in1, c_in2 = st.columns(2)
with c_in1:
    delay_min = st.slider("الحد الأدنى للفاصل (ثواني)", 150, 600, 300)
with c_in2:
    delay_max = st.slider("الحد الأقصى للفاصل (ثواني)", 300, 900, 400)

body = st.text_area("نص الرسالة الترويجية", "أهلاً بك، لاحظنا فرصة لتحسين إدارة المخزون في متجرك وتجنب نفاد المنتجات البائعة عبر نظامنا الذكي مقابل 200$ شهرياً...")

if st.button("🚀 بدء حملة الـ 200 شركة أوتوماتيكياً"):
    if not target_niche:
        st.error("❌ الرجاء تحديد المجال أولاً!")
    else:
        st.info(f"🔍 جاري توليد وإطلاق الحملة لـ 200 شركة في مجال: `{target_niche}`...")
        time.sleep(1)
        
        recs = auto_discover_200_leads(target_niche)
        st.success(f"✅ جاهز! يتم الإرسال الآن بفاصل 5 دقائق بين الرسائل.")
        
        status_box = st.empty()
        prog_bar = st.progress(0)
        
        success_sent = 0
        fail_sent = 0
        idx = 0
        
        for i, r in enumerate(recs):
            active_accs = [a for a in st.session_state.accounts if a["status"] == "active" and a["sent_today"] < 40]
            
            if not active_accs:
                st.error("🚨 تم استنفاد الحد اليومي لجميع الحسابات لحمايتها!")
                break
                
            current_acc = active_accs[idx % len(active_accs)]
            p = current_acc["provider"]
            e = current_acc["email"]
            pwd = current_acc["password"]
            
            srv = "smtp.gmail.com" if p == "gmail" else "smtp-mail.outlook.com"
            
            try:
                server = smtplib.SMTP(srv, 587, timeout=15)
                server.starttls()
                server.login(e, pwd)
                
                msg = MIMEMultipart()
                msg["From"] = e
                msg["To"] = r
                msg["Subject"] = subject
                msg.attach(MIMEText(body, "plain"))
                
                server.sendmail(e, r, msg.as_string())
                server.quit()
                
                current_acc["sent_today"] += 1
                success_sent += 1
                st.session_state.crm_stats['sent'] += 1
                st.session_state.crm_stats['no_reply'] += 1
                
                status_box.success(f"✅ [{i+1}/200] أرسل بنجاح من {e} إلى {r}")
                logging.info(f"SUCCESS: {e} sent to {r}")
                
            except Exception as ex:
                fail_sent += 1
                status_box.warning(f"⚠️ عزل مؤقت للحساب {e}...")
                logging.error(f"FAIL: {e} -> {r} | Error: {ex}")
                current_acc["status"] = "suspended"
            
            idx += 1
            prog_bar.progress((i + 1) / len(recs))
            
            if i < len(recs) - 1:
                sleep_time = random.randint(delay_min, delay_max)
                status_box.info(f"⏳ تم إرسال ({i+1}/200). استراحة أمان لمدة {sleep_time // 60} دقائق...")
                time.sleep(sleep_time)
                
        st.success(f"🎉 انتهت الحملة بنجاح! إجمالي المرسل: {success_sent} شركة.")
