#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image
from io import BytesIO

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Material Ordering Dashboard", layout="wide")

# -------------------------
# Load materials data
# -------------------------
materials_file = os.path.join("data", "materials.csv")
if not os.path.exists(materials_file):
    st.error(f"Materials CSV not found: {materials_file}")
    st.stop()

materials = pd.read_csv(materials_file)

st.title("📦 Material Ordering Dashboard")

# -------------------------
# Order form
# -------------------------
with st.form("order_form"):
    st.subheader("Order Information")
    ordered_by = st.text_input("Ordered By (Your Name)")
    project_code = st.text_input("Project Code")

    st.markdown("---")

    # Material category selection
    category = st.selectbox(
        "Select Material Category",
        materials["category"].unique()
    )

    filtered = materials[materials["category"] == category]
    order_list = []

    # Display materials
    for _, row in filtered.iterrows():
        col1, col2, col3 = st.columns([2, 3, 2])

        image_path = os.path.join("images", row["image"])
        with col1:
            if os.path.exists(image_path):
                try:
                    img = Image.open(image_path)
                    img.thumbnail((150, 150))
                    st.image(img)
                except:
                    st.warning(f"Cannot open image: {image_path}")
            else:
                st.warning(f"Image not found: {image_path}")

        with col2:
            st.markdown(f"**{row['name']}**")
            st.caption(f"Code: {row['code']}")
            st.caption(f"Unit: {row['unit']}")

        with col3:
            qty = st.number_input("Qty", min_value=0, step=1, key=row["code"])
            if qty > 0:
                order_list.append({
                    "code": row["code"],
                    "name": row["name"],
                    "quantity": qty,
                    "unit": row["unit"]
                })

        st.divider()

    # -------------------------
    # Submit order
    # -------------------------
    submitted = st.form_submit_button("✅ Generate Order File")
    if submitted:
        if not ordered_by or not project_code:
            st.warning("Please enter both Ordered By and Project Code.")
        elif not order_list:
            st.warning("No material selected.")
        else:
            # Prepare order DataFrame
            order_df = pd.DataFrame(order_list)
            order_df["ordered_by"] = ordered_by
            order_df["project_code"] = project_code
            order_df["category"] = category
            order_df["time"] = datetime.now().strftime("%Y-%m-%d %H:%M")

            # -------------------------
            # Download as CSV
            # -------------------------
            csv_data = order_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Order as CSV",
                data=csv_data,
                file_name=f"material_order_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

            # -------------------------
            # Download as Excel
            # -------------------------
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                order_df.to_excel(writer, index=False, sheet_name="Order")
            excel_data = output.getvalue()

            st.download_button(
                label="📥 Download Order as Excel",
                data=excel_data,
                file_name=f"material_order_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.success("Order file ready for download 👍")

