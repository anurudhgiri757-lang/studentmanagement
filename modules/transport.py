import streamlit as st

from supabase_client import (
    create_transport_route,
    list_transport,
)


def render_transport(user: dict) -> None:
    st.title("🚌 Transport")

    with st.form("transport_form"):
        name = st.text_input("Route name")
        driver = st.text_input("Driver")
        route = st.text_input("Route")

        capacity = st.number_input(
            "Capacity",
            min_value=1,
            step=1,
        )

        submitted = st.form_submit_button(
            "Save route"
        )

        if submitted:

            if not name.strip():
                st.error("Route name is required.")
                return

            try:
                create_transport_route(
                    name=name.strip(),
                    driver=driver.strip(),
                    route=route.strip(),
                    capacity=int(capacity),
                )

                st.success(
                    "Transport route saved successfully!"
                )

                st.rerun()

            except Exception as e:
                st.error(
                    "Failed to save transport route to Supabase."
                )
                st.code(str(e))

    st.subheader("Routes")

    try:
        routes = list_transport()

        if routes:
            st.dataframe(
                routes,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No transport routes found.")

    except Exception as e:
        st.error(
            "Could not load transport routes from Supabase."
        )
        st.code(str(e))
