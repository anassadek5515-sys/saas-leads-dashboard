import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
import time
import streamlit as st

# إعدادات صفحة الـ Dashboard وتنسيق الواجهة
st.set_page_config(
    page_title="SaaS Leads Dashboard", page_icon="🦅", layout="wide"
)

# تصميم العنوان الرئيسي بشكل فخم
st.title("🦅 لوحة تحكم إرسال الحملات البريدية - SaaS Engine")
st.markdown(
    "**منظومة أسطول الإيميلات المخصصة للوصول للـ 250+ عميل وتأمين الـ Obsidian Black.**"
)
st.markdown("---")

# تقسيم الشاشة إلى عمودين لتنسيق نظيف ومرتب (Sidebar للإعدادات والمحتوى للعمليات)
with st.sidebar:
    st.header("⚙️ إعدادات الخادم (SMTP)")
    smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
    smtp_port = st.number_input("SMTP Port", value=587)
    sender_email = st.text_input("البريد المرسل", value="")
    sender_password = st.text_input(
        "كلمة المرور / App Password", type="password"
    )

# العرض الرئيسي في الصفحة
col1, col2 = st.columns(2)

with col1:
    st.header("📋 قائمة العملاء المستهدفين")
    default_leads = (
        "client1@example.com\nclient2@example.com\nclient3@example.com"
    )
    leads_input = st.text_area(
        "أدخل الإيميلات (كل إيميل في سطر جديد):",
        value=default_leads,
        height=200,
    )

with col2:
    st.header("✉️ محتوى البريد الإلكتروني")
    email_subject = st.text_input(
        "عنوان الرسالة:",
        value="حل ذكي لمنع خسائر توقف المخزون (Stockouts)",
    )
    email_body = st.text_area(
        "نص الرسالة:",
        value="مرحباً،\n\nلاحظنا أن شركتكم قد تستفيد من نظامنا الآلي لتوقع وفلترة المخزون لمنع أي توقف مفاجئ...\n\nتحياتي،\nفريق العمل",
        height=135,
    )

st.markdown("---")


# --- دالة الإرسال في الخلفية (Threading) ---
def send_email_background(leads, server, port, email, password, subject, body):
  try:
    server_conn = smtplib.SMTP(server, port)
    server_conn.starttls()
    server_conn.login(email, password)

    for lead in leads:
      lead = lead.strip()
      if not lead:
        continue

      try:
        msg = MIMEMultipart()
        msg["From"] = email
        msg["To"] = lead
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server_conn.sendmail(email, lead, msg.as_string())
        time.sleep(2)  # فاصل زمني لحماية الحساب من الحظر
      except Exception as e:
        print(f"فشل إرسال الإيميل إلى {lead}: {e}")

    server_conn.quit()
  except Exception as e:
    print(f"خطأ في الاتصال بسيرفر الـ SMTP: {e}")


# --- زر إطلاق الحملة بتنسيق عريض واضح ---
st.subheader("🚀 تشغيل العمليات")
if st.button("إطلاق الحملة البريدية الآن", use_container_width=True):
  if not sender_email or not sender_password:
    st.error(
        "الرجاء إدخال البريد الإلكتروني وكلمة المرور الخاصة بالـ SMTP في القائمة"
        " الجانبية أولاً!"
    )
  else:
    leads_list = leads_input.split("\n")
    leads_list = [l.strip() for l in leads_list if l.strip()]

    if not leads_list:
      st.warning("الرجاء إدخال إيميل واحد على الأقل في القائمة.")
    else:
      campaign_thread = threading.Thread(
          target=send_email_background,
          args=(
              leads_list,
              smtp_server,
              smtp_port,
              sender_email,
              sender_password,
              email_subject,
              email_body,
          ),
      )
      campaign_thread.start()

      st.success(
          f"🎉 تم بدء إرسال الحملة إلى {len(leads_list)} عميل في الخلفية بنجاح!"
          " الماكينة تعمل بكفاءة."
      )
