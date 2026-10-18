import email
import imaplib
import logging
import random
import re
import smtplib
import time
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logging.basicConfig(
    filename="outreach.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

st.set_page_config(
    page_title="Autonomous B2B SaaS Engine", page_icon="⚡", layout="wide"
)

st.title("⚡ منصة المبيعات الذاتية والتحليلات (B2B SaaS Engine)")

# 1. الحسابات الفعلية الخمسة
if "accounts" not in st.session_state:
  st.session_state.accounts = [
      {
          "provider": "gmail",
          "email": "Anassadek5525@gmail.com",
          "password": "atig ffwp ddxd vgcf",
          "sent_today": 0,
          "status": "active",
      },
      {
          "provider": "gmail",
          "email": "Anassadek5535@gmail.com",
          "password": "mdfz guvt hqdv navv",
          "sent_today": 0,
          "status": "active",
      },
      {
          "provider": "outlook",
          "email": "Anassadek5565@outlook.com",
          "password": "Anas#$@()501093083973=55",
          "sent_today": 0,
          "status": "active",
      },
      {
          "provider": "outlook",
          "email": "Anassadek5585@outlook.com",
          "password": "Anas#$@()501093083973",
          "sent_today": 0,
          "status": "active",
      },
      {
          "provider": "outlook",
          "email": "Anassadek5575@outlook.com",
          "password": "Anas#$@()501093083973=55",
          "sent_today": 0,
          "status": "active",
      },
  ]

if "crm_stats" not in st.session_state:
  st.session_state.crm_stats = {
      "sent": 0,
      "no_reply": 0,
      "replied": 0,
      "demo": 0,
      "closed": 0,
  }

# مؤشر القائمة لضمان عدم التكرار أو الوقوف
if "current_lead_index" not in st.session_state:
  st.session_state.current_lead_index = 0


def is_valid_email(email_str):
  pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
  return re.match(pattern, email_str) is not None


def auto_discover_200_leads(niche):
  raw_leads = [f"contact@{niche}store{i}.com" for i in range(1, 201)]
  return [e for e in raw_leads if is_valid_email(e)]


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

      status, messages = mail.search(None, "UNSEEN")
      email_ids = messages[0].split()

      for e_id in email_ids:
        _, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
          if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            body_text = ""
            if msg.is_multipart():
              for part in msg.walk():
                if part.get_content_type() == "text/plain":
                  body_text += part.get_payload(decode=True).decode(
                      "utf-8", errors="ignore"
                  )
            else:
              body_text = msg.get_payload(decode=True).decode(
                  "utf-8", errors="ignore"
              )

            body_lower = body_text.lower()
            if any(
                w in body_lower
                for w in ["demo", "ديمو", "تجربة", "شرح", "try"]
            ):
              demo_count += 1
              replied_count += 1
            elif any(
                w in body_lower
                for w in [
                    "subscribe",
                    "buy",
                    "شراء",
                    "اشتراك",
                    "موافق",
                    "deal",
                    "invoice",
                    "200$",
                ]
            ):
              closed_count += 1
              replied_count += 1
            else:
              replied_count += 1

      mail.logout()
    except Exception as ex:
      logging.error(f"IMAP Read Error on {e}: {ex}")

  st.session_state.crm_stats["replied"] += replied_count
  st.session_state.crm_stats["demo"] += demo_count
  st.session_state.crm_stats["closed"] += closed_count
  st.session_state.crm_stats["no_reply"] = max(
      0,
      st.session_state.crm_stats["sent"]
      - st.session_state.crm_stats["replied"],
  )


active_count = sum(
    1 for a in st.session_state.accounts if a["status"] == "active"
)
with st.expander(
    f"🛡️ حالة الحسابات الخمسة (النشطة: {active_count}/{len(st.session_state.accounts)})"
):
  for acc in st.session_state.accounts:
    st.write(
        f"• **{acc['email']}** ➔ المرسل اليوم: `{acc['sent_today']}/40` |"
        f" الحالة: `{acc['status']}`"
    )

st.markdown("---")

st.subheader("🎯 لوحة المبيعات والصفقات الفعلية (Live Sales Dashboard)")
crm = st.session_state.crm_stats

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("إجمالي الإيميلات", f"{crm['sent']}")
m2.metric("في انتظار الرد ⏳", f"{crm['no_reply']}")
m3.metric("ردود فعلية 📩", f"{crm['replied']}")
m4.metric("طلبات الديمو 💻", f"{crm['demo']}")
m5.metric("عقود مؤكدة 🎯", f"{crm['closed']}", f"${crm['closed']*200}/شهرياً")

if st.button("🔄 فحص الـ Inbox وتحديث الردود الحقيقية"):
  with st.spinner("جاري قراءة الرسائل الجديدة..."):
    fetch_and_classify_replies()
  st.success("تم تحديث البيانات بنجاح!")

fig, ax = plt.subplots(figsize=(8, 3))
categories = ["المرسل", "لم يردوا", "ردوا", "الديمو", "مغلقة"]
values = [
    crm["sent"],
    crm["no_reply"],
    crm["replied"],
    crm["demo"],
    crm["closed"],
]
colors = ["#2980B9", "#7F8C8D", "#F39C12", "#D35400", "#27AE60"]
ax.bar(categories, values, color=colors, width=0.4)
ax.set_title("مسار المبيعات الفعلي", fontsize=10, fontweight="bold")
st.pyplot(fig)

st.markdown("---")

st.subheader("🚀 إعدادات تشغيل أسطول الإيميلات")

target_niche = st.text_input(
    "مجال الشركات المستهدفة (مثال: ecommerce):", "ecommerce"
)
subject = st.text_input(
    "عنوان الرسالة البريدية",
    "تحليل مخزون متجرك وزيادة أرباحك بنسبة 30%",
)

c_in1, c_in2, c_in3 = st.columns(3)
with c_in1:
  delay_min = st.slider("الحد الأدنى للفاصل (ثواني)", 1, 10, 2)
with c_in2:
  delay_max = st.slider("الحد الأقصى للفاصل (ثواني)", 3, 20, 5)
with c_in3:
  batch_size = st.number_input(
      "حجم الدفعة (لتفادي حظر الـ 5 دقائق)", min_value=5, max_value=50, value=20
  )

body = st.text_area(
    "نص الرسالة الترويجية",
    "أهلاً بك، لاحظنا فرصة لتحسين إدارة المخزون في متجرك وتجنب نفاد المنتجات"
    " البائعة عبر نظامنا الذكي مقابل 200$ شهرياً...",
)

col_b1, col_b2 = st.columns(2)

with col_b1:
  if st.button(f"🚀 إرسال دفعة ({batch_size} شركة الآن)", use_container_width=True):
    recs = auto_discover_200_leads(target_niche)
    start_idx = st.session_state.current_lead_index
    end_idx = min(start_idx + batch_size, len(recs))

    if start_idx >= len(recs):
      st.success("🎉 تم إرسال الـ 200 شركة بالكامل!")
    else:
      current_batch = recs[start_idx:end_idx]

      with st.status(
          f"📤 جاري إرسال الدفعة ({start_idx + 1} إلى {end_idx}) من أصل 200...",
          expanded=True,
      ) as status:
        success_sent = 0

        for i, r in enumerate(current_batch):
          active_accs = [
              a
              for a in st.session_state.accounts
              if a["status"] == "active" and a["sent_today"] < 40
          ]

          if not active_accs:
            st.error("🚨 تم استنفاد الحد اليومي لجميع الحسابات الخمسة!")
            break

          current_acc = active_accs[
              (start_idx + i) % len(active_accs)
          ]  # تدوير عادل
          p = current_acc["provider"]
          e = current_acc["email"]
          pwd = current_acc["password"]

          srv = "smtp.gmail.com" if p == "gmail" else "smtp-mail.outlook.com"

          try:
            server = smtplib.SMTP(srv, 587, timeout=10)
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
            st.session_state.crm_stats["sent"] += 1
            st.session_state.crm_stats["no_reply"] += 1

            st.write(
                f"✅ [{start_idx + i + 1}/200] تم الإرسال من **{e}** إلى"
                f" **{r}**"
            )
          except Exception as ex:
            st.write(f"⚠️ خطأ أثناء الإرسال من {e}: {ex}")

          if i < len(current_batch) - 1:
            time.sleep(random.randint(delay_min, delay_max))

        st.session_state.current_lead_index = end_idx
        status.update(
            label=(
                f"🎉 اكتملت الدفعة! إجمالي المرسل حتى الآن:"
                f" {st.session_state.current_lead_index}/200"
            ),
            state="complete",
        )

with col_b2:
  if st.button("🔄 إعادة ضبط العداد للبداية", use_container_width=True):
    st.session_state.current_lead_index = 0
    st.info("تمت إعادة ضبط المؤشر إلى 0.")
