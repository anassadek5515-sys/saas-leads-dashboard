import streamlit as st
import pandas as pd

# إعدادات صفحة لوحة التحكم
st.set_page_config(
    page_title="SaaS Lead Gen Dashboard",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 لوحة تحكم استهداف العملاء (SaaS 1M EGP)")
st.markdown("موقعك السحابي المخصص لجمع ومتابعة لستات الشركات الأجنبية المستهدفة.")

# مؤشرات الأداء الرئيسية (KPIs)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="الهدف المنشود", value="100 شركة", delta="هدف المليون جنيه")
with col2:
    st.metric(label="الشركات المتعاقدة حالياً", value="0 شركة", delta="+0 هذا الأسبوع")
with col3:
    st.metric(label="إجمالي الداتا المجمعة", value="0 شركة", delta="جاهزة للتواصل")

st.markdown("---")

# قسم عرض الداتا والتحكم
st.subheader("📋 قائمة الشركات والمتاجر المستهدفة")

# محاكاة لجدول البيانات (هنا هيربط لاحقاً بـ Google Sheets أو قاعدة البيانات)
data = {
    "اسم المتجر / الشركة": ["(مثال) Glow Skincare Store", "(مثال) TechGear UK", "..."],
    "رابط الموقع": ["glowstore.com", "techgear.co.uk", "..."],
    "الإيميل الحقيقي": ["contact@glowstore.com", "hello@techgear.co.uk", "..."],
    "حالة التواصل": ["جاهز للإرسال", "تم الإرسال (إيميل)", "تم التواصل (واتساب)"],
}

df = pd.DataFrame(data)

# عرض الجدول بشكل تفاعلي
st.dataframe(df, use_container_width=True)

# زرار تشغيل الماكينة الوهمي للتجربة
if st.button("🔄 تشغيل ماكينة جمع البيانات الآن"):
    st.success("تم إرسال أمر التشغيل للسيرفر السحابي بنجاح! جاري جلب الشركات...")

st.sidebar.header("⚙️ إعدادات التحكم")
st.sidebar.info("الحسابات النشطة: 3 إيميلات + 3 لينكد إن + واتساب")
