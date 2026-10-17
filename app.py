import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import streamlit as st

# إعدادات صفحة الـ Dashboard وتنسيق الواجهة
st.set_page_config(
    page_title="SaaS Leads Dashboard", page_icon="🦅", layout="wide"
)

st.title("🦅 لوحة تحكم أسطول الإيميلات والبحث الآلي - SaaS Engine")
st.markdown(
    "**منظومة استخراج العملاء وإرسال الحملات للوصول للـ 250+ عميل وتأمين الـ"
    " Obsidian Black.**"
)
st.markdown("---")

with st.sidebar:
  st.header("⚙️ إعدادات الخادم (SMTP)")
  smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
  smtp_port = st.number_input("SMTP Port", value=587)
  sender_email = st.text_input("البريد المرسل", value="")
  sender_password = st.text_input("كلمة المرور / App Password", type="password")

# --- قسم البحث الآلي عن الشركات والـ Leads ---
st.header("🔍 محرك البحث الآلي عن الشركات والمخازن")
col_search1, col_search2 = st.columns([3, 1])

with col_search1:
  search_query = st.text_input(
      "أدخل مجال البحث أو المدينة (مثلاً: شركات اللوجستيات والمخازن في القاهرة):",
      value="مديري المخازن واللوجستيات",
  )

with col_search2:
  st.markdown("<br>", unsafe_allow_html=True)
  search_btn = st.button("بحث آلي عن الشركات 🔎", use_container_width=True)

# محاكاة / جلب النتائج الآلية للشركات
if search_btn:
  with st.spinner("جاري مسح الويب والبحث عن الشركات المستهدفة..."):
    time.sleep(2)  # محاكاة وقت البحث
    # هنا هينزل الشركات اللي تم جلبها أوتوماتيك (قاعدة بيانات افتراضية ذكية كمرحلة أولى)
    fetched_leads = (
        "manager1@logistics-eg.com\noperations@supplychain-me.com\n"
        "info@cairo-warehouses.com\nstock@delta-storage.com"
    )
    st.session_state["generated_leads"] = fetched_leads
    st.success(
        "تم العثور على الشركات المستهدفة وإضافتها للقائمة أدناه بنجاح! 🎯"
    )

# العرض الرئيسي (العملاء ومحتوى البريد)
col1, col2 = st.columns(2)

with col1:
  st.header("📋 قائمة العملاء المستهدفين (المستخرجة آلياً)")
  # استخدام البيانات المستخرجة أوتوماتيك لو موجودة، أو القائمة الافتراضية
  default_leads = st.session_state.get(
      "generated_leads", "client1@example.com\nclient2@example.com"
  )
  leads_input = st.text_area(
      "الإيميلات التي سيتم المراسلة عليها:", value=default_leads, height=200
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
st.subheader("🚀 تشغيل الحملة")

if st.button("إطلاق الحملة البريدية للشركات المستخرجة الآن", use_container_width=True):
  if not sender_email or not sender_password:
    st.error(
        "الرجاء إدخال البريد الإلكتروني وكلمة المرور الخاصة بالـ SMTP في القائمة"
        " الجانبية أولاً!"
    )
  else:
    leads_list = leads_input.split("\n")
    leads_list = [l.strip() for l in leads_list if l.strip()]

    if not leads_list:
      st.warning("الرجاء التأكد من وجود إيميلات في القائمة.")
    else:
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
            time.sleep(1)
          except Exception as ex:
            st.warning(f"فشل إرسال إلى {lead}: {ex}")

          progress_bar.progress((i + 1) / total_leads)

        server_conn.quit()
        status_text.empty()
        progress_bar.empty()
        st.success(
            f"🎉 تم الانتهاء بنجاح! تم إرسال {success_count} إيميل للشركات المستهدفة"
            f" من أصل {total_leads}."
        )

      except Exception as e:
        st.error(f"حدث خطأ أثناء الاتصال أو الإرسال: {e}")
