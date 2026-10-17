import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import streamlit as st

# إعدادات صفحة الـ Dashboard وتنسيق الواجهة
st.set_page_config(
    page_title="SaaS Leads Dashboard", page_icon="🦅", layout="wide"
)

st.title("🦅 لوحة تحكم إرسال الحملات البريدية - SaaS Engine")
st.markdown(
    "**منظومة أسطول الإيميلات المخصصة للوصول للـ 250+ عميل وتأمين الـ Obsidian Black.**"
)
st.markdown("---")

with st.sidebar:
  st.header("⚙️ إعدادات الخادم (SMTP)")
  smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
  smtp_port = st.number_input("SMTP Port", value=587)
  sender_email = st.text_input("البريد المرسل", value="")
  sender_password = st.text_input("كلمة المرور / App Password", type="password")

col1, col2 = st.columns(2)

with col1:
  st.header("📋 قائمة العملاء المستهدفين")
  default_leads = (
      "client1@example.com\nclient2@example.com\nclient3@example.com"
  )
  leads_input = st.text_area(
      "أدخل الإيميلات (كل إيميل في سطر جديد):", value=default_leads, height=200
  )

with col2:
  st.header("✉️ محتوى البريد الإلكتروني")
  email_subject = st.text_input(
      "عنوان الرسالة:", value="حل ذكي لمنع خسائر توقف المخزون (Stockouts)"
  )
  email_body = st.text_area(
      "نص الرسالة:",
      value="مرحباً،\n\nلاحظنا أن شركتكم قد تستفيد من نظامنا الآلي لتوقع وفلترة المخزون لمنع أي توقف مفاجئ...\n\nتحياتي،\nفريق العمل",
      height=135,
  )

st.markdown("---")
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
      # شريط التقدم المرئي
      progress_bar = st.progress(0)
      status_text = st.empty()

      total_leads = len(leads_list)
      success_count = 0

      try:
        status_text.text("🔄 جاري الاتصال بسيرفر الإيميل...")
        server_conn = smtplib.SMTP(smtp_server, int(smtp_port))
        server_conn.starttls()
        server_conn.login(sender_email, sender_password)

        for i, lead in enumerate(leads_list):
          status_text.text(
              f"📤 جاري إرسال الإيميل ({i+1}/{total_leads}) إلى: {lead}"
          )

          try:
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = lead
            msg["Subject"] = email_subject
            msg.attach(MIMEText(email_body, "plain"))

            server_conn.sendmail(sender_email, lead, msg.as_string())
            success_count += 1
            time.sleep(1)  # فاصل زمني أمان
          except Exception as ex:
            st.warning(f"فشل إرسال إلى {lead}: {ex}")

          # تحديث شريط التقدم
          progress_bar.progress((i + 1) / total_leads)

        server_conn.quit()
        status_text.empty()
        progress_bar.empty()
        st.success(
            f"🎉 تم الانتهاء بنجاح! تم إرسال {success_count} إيميل من أصل"
            f" {total_leads} عميل."
        )

      except Exception as e:
        st.error(f"حدث خطأ أثناء الاتصال أو الإرسال: {e}")
