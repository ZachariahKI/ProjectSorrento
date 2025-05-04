# pages/02_Portfolio_Management.py
import streamlit as st
import pandas as pd
import numpy as np # Used by pandas/plotly implicitly sometimes
import os # To construct file path
from datetime import datetime # For date handling

# --- Page Configuration (Good practice per page) ---
# Sets the title shown in the browser tab for this specific page
st.set_page_config(page_title="Portfolio Management", layout="wide")

# --- Data Loading Function ---
@st.cache_data # Cache the data loading to avoid reading file repeatedly
def load_loan_data():
    """Loads the pre-generated loan data from the Parquet file."""
    # Construct the path relative to the main app directory
    # Assumes 'data' folder is at the same level as 'Home.py'
    data_file_path = os.path.join('.', 'data', 'loan_data.parquet')

    try:
        df = pd.read_parquet(data_file_path)
        # Ensure Date column is datetime type
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except FileNotFoundError:
        st.error(f"Error: Data file not found at '{data_file_path}'")
        st.error("Ensure the 'data' folder exists in your main app directory and contains 'loan_data.parquet'.")
        st.error("You may need to run the `create_data.py` script first.")
        return pd.DataFrame() # Return empty dataframe to avoid further errors
    except ImportError:
         st.error("Module 'pyarrow' not installed. Cannot read Parquet file.")
         st.error("Please install it (`pip install pyarrow` in your venv) and restart the app.")
         return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred loading the data file: {e}")
        return pd.DataFrame()

# --- Session State Initialization for View Switching ---
# This runs only once per session unless the key is deleted
if 'pm_view' not in st.session_state:
    st.session_state.pm_view = 'main' # Default view is 'main'

# --- Function to change the view ---
def set_view(view_name):
    """Updates the session state to change the view."""
    st.session_state.pm_view = view_name

# --- Main Page Title ---
st.markdown("<h1 style='text-align: center;'>Portfolio Management</h1>", unsafe_allow_html=True)
st.write("---") # Add a horizontal rule for separation

# --- View Switching Logic ---

# If the current view is 'main' (the default PM landing view)
if st.session_state.pm_view == 'main':
    st.subheader("Main Portfolio Overview")
    st.write("This is the main landing area for Portfolio Management.")
    st.write("Select a sub-section below or using the sidebar filters (when available).")

    # Add a button to switch to the 'Total Book view'
    # Use the 'on_click' argument to call our function when the button is pressed
    st.button("View Total Book", on_click=set_view, args=('total_book',), key='view_total_book_btn', use_container_width=True)

    # Add placeholders for other potential sub-sections later
    # Example: st.button("View Sector Analysis", on_click=set_view, args=('sector_view',), key='view_sector_btn')

# Else if the current view is 'total_book'
elif st.session_state.pm_view == 'total_book':
    st.subheader("Total Book View")

    # --- Load Full Dataset ---
    # Call the loading function (uses cache)
    df_full = load_loan_data()

    # Proceed only if data was loaded successfully
    if not df_full.empty:

        # --- Month Selection Filter ---
        st.sidebar.header("Filters")
        # Get unique months, format them nicely for display, sort descending
        available_months = sorted(df_full['Date'].dt.to_period('M').unique(), reverse=True)
        month_display_list = [m.strftime('%Y-%m') for m in available_months] # Format like "2025-03"
        # Selectbox default to the most recent month
        selected_month_str = st.sidebar.selectbox(
            "Select Month",
            month_display_list,
            index=0 # Default to the first item (most recent month)
        )
        # Convert selected string back to Period for filtering
        selected_month_period = pd.Period(selected_month_str, freq='M')

        # --- Filter Data by Selected Month ---
        # Create a dataframe containing only the data for the selected month
        df_monthly = df_full[df_full['Date'].dt.to_period('M') == selected_month_period].copy()

        # --- "Picture of the Data" - Summary Stats for Selected Month (Before other filters) ---
        st.markdown("#### Monthly Snapshot Summary")
        if not df_monthly.empty:
            total_balance = df_monthly['Balance'].sum()
            total_rwa = df_monthly['RWA'].sum()
            total_nii = df_monthly['Net Interest Income'].sum()
            total_fees = df_monthly['Fee Income'].sum()
            facility_count = len(df_monthly)
            # Calculate weighted average margin (WAM)
            if total_balance > 0:
                 avg_margin = np.average(df_monthly['Margin'], weights=df_monthly['Balance'])
            else:
                 avg_margin = 0

            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric("Total Balance", f"£{total_balance:,.0f}")
            mcol1.metric("Facility Count", f"{facility_count}")
            mcol2.metric("Total RWA", f"£{total_rwa:,.0f}")
            mcol2.metric("W. Avg. Margin", f"{avg_margin:.2%}") # Display WAM
            mcol3.metric("Total NII (Month)", f"£{total_nii:,.0f}")
            mcol3.metric("Total Fees (Month)", f"£{total_fees:,.0f}")
        else:
            st.info(f"No data available for {selected_month_str} to calculate summaries.")
        st.write("---") # Separator

        # --- Other Interactive Filters (Apply to Monthly Data) ---
        if not df_monthly.empty: # Check if there's data for the selected month before creating filters
            # Define base ratings list for consistent sort order
            rating_options_all = ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC']
            # Get options available in the current monthly data
            franchise_options = sorted(df_monthly['Franchise'].unique())
            sector_options = sorted(df_monthly['Sector'].unique())
            rating_options = [r for r in rating_options_all if r in df_monthly['Credit Rating'].unique()]
            product_options = sorted(df_monthly['Product'].unique())

            # Create filter widgets in the sidebar
            selected_franchises = st.sidebar.multiselect("Franchise", franchise_options, default=franchise_options)
            selected_sectors = st.sidebar.multiselect("Sector", sector_options, default=sector_options)
            selected_ratings = st.sidebar.multiselect("Credit Rating", rating_options, default=rating_options)
            selected_products = st.sidebar.multiselect("Product", product_options, default=product_options)

            # Slider for Balance (use monthly min/max)
            min_balance, max_balance = int(df_monthly['Balance'].min()), int(df_monthly['Balance'].max())
            # Handle case where min and max are the same for the slider
            step_val = max(1, (max_balance - min_balance) // 100) # Ensure step is at least 1
            if min_balance >= max_balance: # Prevent slider error if only one value or min > max somehow
                max_balance = min_balance + step_val

            balance_range = st.sidebar.slider(
                "Balance Range (£)",
                min_value=min_balance,
                max_value=max_balance,
                value=(min_balance, max_balance), # Default to full range for the month
                step=step_val,
                format="£%,d" # Format slider display with commas
            )
            # Display selected range clearly
            st.sidebar.caption(f"Selected Balance: £{balance_range[0]:,} - £{balance_range[1]:,}")

            # --- Apply Filters ---
            # Filter the monthly dataframe based on selections
            df_filtered = df_monthly[
                (df_monthly['Franchise'].isin(selected_franchises)) &
                (df_monthly['Sector'].isin(selected_sectors)) &
                (df_monthly['Credit Rating'].isin(selected_ratings)) &
                (df_monthly['Product'].isin(selected_products)) &
                (df_monthly['Balance'] >= balance_range[0]) &
                (df_monthly['Balance'] <= balance_range[1])
            ].copy() # Copy to ensure we work with a distinct dataframe

            # --- "Picture of the Data" - Visualizations (Based on Filtered Data) ---
            if not df_filtered.empty:
                st.markdown("#### Filtered Data Visuals")
                try:
                    # Use Plotly for better interactive charts
                    import plotly.express as px

                    vcol1, vcol2 = st.columns(2)
                    with vcol1:
                        # Bar chart: Sum of Balance by Sector
                        balance_by_sector = df_filtered.groupby('Sector', observed=False)['Balance'].sum().reset_index().sort_values(by='Balance', ascending=False)
                        fig_sec = px.bar(balance_by_sector, x='Sector', y='Balance', title='Total Balance by Sector', height=350)
                        fig_sec.update_layout(yaxis_title="Total Balance (£)", margin=dict(t=30, b=0, l=0, r=0))
                        st.plotly_chart(fig_sec, use_container_width=True)

                    with vcol2:
                         # Pie chart: Facility Count by Credit Rating
                        rating_counts = df_filtered['Credit Rating'].value_counts().reset_index()
                        # Ensure consistent ordering based on rating quality
                        rating_counts['Credit Rating'] = pd.Categorical(rating_counts['Credit Rating'], categories=rating_options_all, ordered=True)
                        rating_counts = rating_counts.sort_values('Credit Rating')
                        fig_rat = px.pie(rating_counts, names='Credit Rating', values='count', title='Facility Count by Credit Rating', height=350) # Changed column name from value_counts
                        fig_rat.update_layout(margin=dict(t=30, b=0, l=0, r=0))
                        st.plotly_chart(fig_rat, use_container_width=True)

                except ImportError:
                     st.warning("Plotly library not found. Skipping charts. Install using: `pip install plotly`")
                except Exception as e:
                     st.error(f"An error occurred generating charts: {e}")

                st.write("---") # Separator before table
            else:
                 st.info("No data matching current filters to display visuals.")


            # --- Display Filtered Data Table ---
            st.markdown("#### Filtered Data Table")
            st.write(f"Displaying {len(df_filtered)} facilities matching filters for {selected_month_str}.")

            # Create a copy specifically for display formatting
            df_display = df_filtered.copy()

            # Format columns for display
            try:
                # Apply formatting (use £ for currency)
                for col in ['Balance', 'EAD', 'RWA', 'Interest Income', 'Interest Costs', 'Net Interest Income', 'Fee Income']:
                     if col in df_display.columns:
                         df_display[col] = df_display[col].map('£{:,.0f}'.format) # Add £ sign
                for col in ['Margin', 'RAROE']:
                     if col in df_display.columns:
                         df_display[col] = pd.to_numeric(df_display[col]).map('{:.2%}'.format)
                for col in ['PD']:
                     if col in df_display.columns:
                         df_display[col] = pd.to_numeric(df_display[col]).map('{:.4%}'.format)
                for col in ['LGD']:
                     if col in df_display.columns:
                         df_display[col] = pd.to_numeric(df_display[col]).map('{:.1%}'.format)
                # Format Date to show only YYYY-MM-DD
                df_display['Date'] = pd.to_datetime(df_display['Date']).dt.strftime('%Y-%m-%d')

                # Reorder columns for better display (optional)
                display_cols = [
                    'Date', 'Facility ID', 'Customer Name', 'Franchise', 'Sector', 'Product',
                    'Balance', 'Margin', 'Net Interest Income', 'Fee Income', 'RAROE', 'Credit Rating', 'PD', 'LGD',
                    'EAD', 'RWA', 'Interest Income', 'Interest Costs' # Added new cols
                ]
                # Keep only columns that actually exist in the dataframe
                display_cols = [col for col in display_cols if col in df_display.columns]
                df_display = df_display[display_cols]

            except Exception as e:
                st.error(f"Error formatting display data: {e}")
                df_display = df_filtered # Fallback to unformatted data if formatting fails

            # Display the interactive dataframe
            st.dataframe(df_display, use_container_width=True, height=500, hide_index=True) # Hide default index

        else:
            # Handle case where monthly data exists but is fully filtered out
            st.warning(f"No data matches the selected filters for {selected_month_str}.")

    else:
        # Handle case where data loading failed at the start
         st.warning("Could not display Portfolio data as the data file failed to load.")


    # --- Add back button ---
    # Placed outside the 'if not df_full.empty:' check so it always shows in this view
    st.button("Back to Portfolio Overview", on_click=set_view, args=('main',), key='back_to_main_pm_btn')

# --- (End of file) ---