import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
import time
import streamlit as st

# إعدادات صفحة الـ Dashboard
st.set_page_config(page_title="SaaS Leads Dashboard", page_icon="🦅", layout="wide")

st.title("🦅 لوحة تحكم إرسال الحملات البريدية - SaaS Engine")
st.write(
    "مرحباً بك يا أنس. هذه المنظومة مخصصة لإدارة أسطول الإيميلات والوصول للـ 250+ عميل."
)

# --- إعدادات الإيميل (يمكنك ربطها بالـ Secrets لاحقاً للأمان) ---
st.sidebar.header("⚙️ إعدادات الخادم (SMTP)")
smtp_server = st.sidebar.text_input("SMTP Server", value="smtp.gmail.com")
smtp_port = st.sidebar.number_input("SMTP Port", value=587)
sender_email = st.sidebar.text_input("البريد المرسل", value="")
sender_password = st.sidebar.text_input(
    "كلمة المرور / App Password", type="password"
)

# --- قائمة العملاء المستهدفين (Leads) ---
st.header("📋 قائمة العملاء المستهدفين (مديري المخازن والعمليات)")

# قائمة تجريبية (يمكنك تعديلها أو قراءتها من ملف أو قاعدة بيانات لاحقاً)
default_leads = "client1@example.com\nclient2@example.com\nclient3@example.com"
leads_input = st.text_area(
    "أدخل الإيميلات (كل إيميل في سطر جديد):", value=default_leads
)

# --- محتوى الرسالة ---
st.header("✉️ محتوى البريد الإلكتروني")
email_subject = st.text_input(
    "عنوان الرسالة:", value="حل ذكي لمنع خسائر توقف المخزون (Stockouts)"
)
email_body = st.text_area(
    "نص الرسالة:",
    value="مرحباً،\n\nلاحظنا أن شركتكم قد تستفيد من نظامنا الآلي لتوقع وفلترة المخزون لمنع أي توقف مفاجئ...\n\nتحياتي،\nفريق العمل",
    height=150,
)


# --- دالة الإرسال الفعلية (تعمل في الخلفية لضمان عدم توقف الـ UI) ---
def send_email_background(leads, server, port, email, password, subject, body):
    try:
        # الاتصال بسيرفر الـ SMTP
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
                print(f"تم إرسال الإيميل بنجاح إلى: {lead}")

                # فاصل زمني ثانيتين بين كل إيميل وإيميل لحماية الحساب من الحظر
                time.sleep(2)
            except Exception as e:
                print(f"فشل إرسال الإيميل إلى {lead}: {e}")

        server_conn.quit()
        print("اكتملت الحملة بنجاح!")
    except Exception as e:
        print(f"خطأ في الاتصال بسيرفر الـ SMTP: {e}")


# --- زر إطلاق الحملة ---
st.markdown("---")
if st.button("🚀 إطلاق الحملة الآن"):
    if not sender_email or not sender_password:
        st.error("الرجاء إدخال البريد الإلكتروني وكلمة المرور الخاصة بالـ SMTP أولاً!")
    else:
        leads_list = leads_input.split("\n")
        leads_list = [l.strip() for l in leads_list if l.strip()]

        if not leads_list:
            st.warning("الرجاء إدخال إيميل واحد على الأقل في القائمة.")
        else:
            # تشغيل الإرسال في Thread منفصل (وهو السر في حل مشكلة التوقف بعد الإيميل الأول)
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
                f"🎉 تم بدء إرسال الحملة إلى {len(leads_list)} عميل في الخلفية بنجاح! يمكنك متابعة العمل."
            )
