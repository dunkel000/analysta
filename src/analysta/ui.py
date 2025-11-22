"""
Analysta Data Studio - Advanced DataFrame Toolkit
Launch with: analysta ui
"""
import streamlit as st
import pandas as pd
import io
from analysta import Delta, trim_whitespace, audit_dataframe, duplicates

# -----------------------------------------------------------------------------
# Page Configuration & Custom CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Analysta Data Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Dark Theme
st.markdown("""
    <style>
    /* Main fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Card Styling */
    .stCard {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #3b82f6;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f8fafc;
        font-weight: 600;
    }
    
    h1 { letter-spacing: -0.025em; }
    
    /* Custom Buttons */
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    
    /* Success/Error Messages */
    .stAlert {
        border-radius: 8px;
    }
    
    /* DataFrames */
    .stDataFrame {
        border: 1px solid #334155;
        border-radius: 8px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# State Management
# -----------------------------------------------------------------------------
if 'df_a' not in st.session_state:
    st.session_state.df_a = None
if 'df_b' not in st.session_state:
    st.session_state.df_b = None
if 'filename_a' not in st.session_state:
    st.session_state.filename_a = None
if 'filename_b' not in st.session_state:
    st.session_state.filename_b = None

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def load_file(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        else:
            return pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# -----------------------------------------------------------------------------
# Modules
# -----------------------------------------------------------------------------

def render_home():
    st.title("⚡ Analysta Data Studio")
    st.markdown("### Import & Prepare Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="stCard">
            <h3>📄 Dataset A (Primary)</h3>
        </div>
        """, unsafe_allow_html=True)
        file_a = st.file_uploader("Upload CSV or Excel", type=['csv', 'xlsx'], key="up_a")
        
        if file_a:
            df = load_file(file_a)
            if df is not None:
                st.session_state.df_a = df
                st.session_state.filename_a = file_a.name
                st.success(f"Loaded {file_a.name}")
                
        if st.session_state.df_a is not None:
            st.dataframe(st.session_state.df_a.head(), use_container_width=True)
            st.caption(f"{st.session_state.df_a.shape[0]} rows × {st.session_state.df_a.shape[1]} columns")

    with col2:
        st.markdown("""
        <div class="stCard">
            <h3>📄 Dataset B (Comparison)</h3>
        </div>
        """, unsafe_allow_html=True)
        file_b = st.file_uploader("Upload CSV or Excel", type=['csv', 'xlsx'], key="up_b")
        
        if file_b:
            df = load_file(file_b)
            if df is not None:
                st.session_state.df_b = df
                st.session_state.filename_b = file_b.name
                st.success(f"Loaded {file_b.name}")
                
        if st.session_state.df_b is not None:
            st.dataframe(st.session_state.df_b.head(), use_container_width=True)
            st.caption(f"{st.session_state.df_b.shape[0]} rows × {st.session_state.df_b.shape[1]} columns")

    if st.session_state.df_a is not None:
        st.divider()
        st.subheader("🛠️ Quick Actions")
        if st.button("✨ Trim Whitespace from All Data", use_container_width=True):
            st.session_state.df_a = trim_whitespace(st.session_state.df_a)
            if st.session_state.df_b is not None:
                st.session_state.df_b = trim_whitespace(st.session_state.df_b)
            st.success("Whitespace trimmed from all text columns!")


def render_compare():
    st.title("🔍 Delta Comparison")
    
    if st.session_state.df_a is None or st.session_state.df_b is None:
        st.warning("Please load both Dataset A and Dataset B in the Home tab first.")
        return

    df_a = st.session_state.df_a
    df_b = st.session_state.df_b

    # Settings
    with st.expander("⚙️ Comparison Settings", expanded=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            common_cols = list(set(df_a.columns) & set(df_b.columns))
            keys = st.multiselect("Primary Key(s)", common_cols, default=common_cols[:1] if common_cols else [])
        with col2:
            abs_tol = st.number_input("Abs. Tolerance", value=0.0, step=0.01)
        with col3:
            rel_tol = st.number_input("Rel. Tolerance", value=0.0, step=0.01)

    if not keys:
        st.info("Select at least one key column to start comparison.")
        return

    if st.button("🚀 Run Comparison", type="primary", use_container_width=True):
        with st.spinner("Crunching numbers..."):
            delta = Delta(df_a, df_b, keys=keys, abs_tol=abs_tol, rel_tol=rel_tol)
            
            # Metrics
            st.markdown("### Results Overview")
            m1, m2, m3 = st.columns(3)
            m1.metric("Rows Only in A", len(delta.unmatched_a), delta_color="off")
            m2.metric("Rows Only in B", len(delta.unmatched_b), delta_color="off")
            m3.metric("Mismatches", len(delta.mismatches), delta_color="inverse")
            
            st.divider()
            
            # Tabs
            t1, t2, t3, t4 = st.tabs(["🔴 Only in A", "🟢 Only in B", "🟡 Mismatches", "📄 Report"])
            
            with t1:
                st.dataframe(delta.unmatched_a, use_container_width=True)
            with t2:
                st.dataframe(delta.unmatched_b, use_container_width=True)
            with t3:
                st.dataframe(delta.mismatches, use_container_width=True)
            with t4:
                html = delta.to_html()
                st.download_button("📥 Download HTML Report", html, "report.html", "text/html")
                st.components.v1.html(html, height=600, scrolling=True)


def render_audit():
    st.title("📋 Quality Audit")
    
    if st.session_state.df_a is None:
        st.warning("Please load Dataset A in the Home tab.")
        return
        
    target_df = st.session_state.df_a
    st.markdown(f"**Auditing:** `{st.session_state.filename_a}`")
    
    if st.button("Run Audit"):
        issues = audit_dataframe(target_df)
        
        if issues.empty:
            st.success("✨ No obvious quality issues found!")
        else:
            # Group by column for cleaner display
            for col in issues['column'].unique():
                col_issues = issues[issues['column'] == col]
                with st.expander(f"🚩 Issues in '{col}'", expanded=True):
                    for _, row in col_issues.iterrows():
                        st.write(f"**{row['issue']}**: {row['details']}")


def render_duplicates():
    st.title("👯 Duplicate Finder")
    
    if st.session_state.df_a is None:
        st.warning("Please load Dataset A in the Home tab.")
        return

    target_df = st.session_state.df_a
    st.markdown(f"**Checking:** `{st.session_state.filename_a}`")
    
    cols = st.multiselect("Check for duplicates based on:", target_df.columns, default=list(target_df.columns))
    
    if cols:
        dups = duplicates(target_df, column=cols, counts=True)
        count = len(dups)
        
        if count > 0:
            st.error(f"Found {count} duplicate groups!")
            st.dataframe(dups, use_container_width=True)
        else:
            st.success("✅ No duplicates found.")

# -----------------------------------------------------------------------------
# Main App Layout
# -----------------------------------------------------------------------------

# Sidebar Navigation
with st.sidebar:
    st.title("Analysta")
    st.caption("v0.0.7")
    st.divider()
    
    page = st.radio(
        "Navigation",
        ["🏠 Home", "🔍 Compare", "📋 Audit", "👯 Duplicates"],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.info("💡 **Tip:** Use the Home tab to load your datasets first.")

# Router
if "Home" in page:
    render_home()
elif "Compare" in page:
    render_compare()
elif "Audit" in page:
    render_audit()
elif "Duplicates" in page:
    render_duplicates()

