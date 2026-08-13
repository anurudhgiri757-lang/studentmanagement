import streamlit as st

from supabase_client import create_inventory_item, list_inventory


def render_inventory(user: dict) -> None:
    st.title("📦 Inventory")
    with st.form("inventory_form"):
        name = st.text_input("Item name")
        category = st.text_input("Category")
        quantity = st.number_input("Quantity", min_value=0, step=1)
        location = st.text_input("Location")
        submitted = st.form_submit_button("Save item")
        if submitted:
            create_inventory_item(name=name, category=category, quantity=int(quantity), location=location)
            st.success("Inventory item saved")

    st.subheader("Inventory items")
    st.dataframe(list_inventory(), use_container_width=True, hide_index=True)
