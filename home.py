import streamlit as st
# import google_auth_httplib2
# import httplib2
# import pandas as pd
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.http import HttpRequest

def home():
    st.title('Welcome to *project***ADIRA**')
    st.caption('### Published May 2, 2023, by Chris Casad.')
    
    # # https://blog.streamlit.io/create-a-search-engine-with-streamlit-and-google-sheets/
    # # Use a text_input to get the keywords to filter the dataframe
    # text_search = st.text_input("Search videos by title or speaker", value="")
    # # Filter the dataframe using masks
    # m1 = df["Autor"].str.contains(text_search)
    # m2 = df["Título"].str.contains(text_search)
    # df_search = df[m1 | m2]
    # # Show the results, if you have a text_search
    # if text_search:
    #     st.write(df_search)    
    # # Another way to show the filtered results
    # # Show the cards
    # N_cards_per_row = 3
    # if text_search:
    #     for n_row, row in df_search.reset_index().iterrows():
    #         i = n_row%N_cards_per_row
    #         if i==0:
    #             st.write("---")
    #             cols = st.columns(N_cards_per_row, gap="large")
    #         # draw the card
    #         with cols[n_row%N_cards_per_row]:
    #             st.caption(f"{row['Evento'].strip()} - {row['Lugar'].strip()} - {row['Fecha'].strip()} ")
    #             st.markdown(f"**{row['Autor'].strip()}**")
    #             st.markdown(f"*{row['Título'].strip()}*")
    #             st.markdown(f"**{row['Video']}**")
        
    st.write('The **A**utomated **Di**rectional **R**esponse **A**nalysis, **ADIRA**, tool is designed to make data evaluation quick and simple.')
    st.write('Focused on drilling and geologic data known as EDR and RSA, respectively, these datasets can be large and difficult to use in traditional data processing tools.') 
    st.write('ADIRA handles the heavy lifting of these large datasets and includes advances modules for data clean-up, channel organization and recognition, and plotting.')
    st.write('### Getting Started')
    st.write('To get started, click on the page in the sidebar to the left. **Drag and drop** to Upload your own dataset, or click **View Demo Data** to immediately see the power of ADIRA.')
    st.write('### Sections')
    st.write('**Home:** The homepage and knowledge center for ADIRA with news, descriptions, settings and future updates.')
    st.write('**EDR:** Primary Drilling Data visualisation and reportings tool. This first version can handle up to 4 sets of EDR data to analyze multiple wells. Requires .csv or .xlsx files.')
    st.write('**RSA:** Rock Strength Analysis visualisation and bit recommendation. Requires .las file.')
    st.write('### Feedback')
    st.write('Please use the feedback tool to share your thoughts and recommend any future improvements.')    
    with st.expander('More Info'): 
        st.write('The Automated Directional Response Analysis, **ADIRA**, tool was created to expedite finding value and key insights in drilling data.')
    
    with st.expander('Feature Roadmap'): 
        st.write('A roadmap of upcoming features to **ADIRA** will be coming soon.')
        # https://github.com/streamlit/example-app-bug-report
        # import google_auth_httplib2
        # import httplib2
        # import pandas as pd
        # import streamlit as st
        # from google.oauth2 import service_account
        # from googleapiclient.discovery import build
        # from googleapiclient.http import HttpRequest

        # SCOPE = "https://www.googleapis.com/auth/spreadsheets"
        # SPREADSHEET_ID = "1QlPTiVvfRM82snGN6LELpNkOwVI1_Mp9J9xeJe-QoaA"
        # SHEET_NAME = "Database"
        # GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"


        # @st.experimental_singleton()
        # def connect_to_gsheet():
        #     # Create a connection object.
        #     credentials = service_account.Credentials.from_service_account_info(
        #         st.secrets["gcp_service_account"],
        #         scopes=[SCOPE],
        #     )

        #     # Create a new Http() object for every request
        #     def build_request(http, *args, **kwargs):
        #         new_http = google_auth_httplib2.AuthorizedHttp(
        #             credentials, http=httplib2.Http()
        #         )
        #         return HttpRequest(new_http, *args, **kwargs)

        #     authorized_http = google_auth_httplib2.AuthorizedHttp(
        #         credentials, http=httplib2.Http()
        #     )
        #     service = build(
        #         "sheets",
        #         "v4",
        #         requestBuilder=build_request,
        #         http=authorized_http,
        #     )
        #     gsheet_connector = service.spreadsheets()
        #     return gsheet_connector


        # def get_data(gsheet_connector) -> pd.DataFrame:
        #     values = (
        #         gsheet_connector.values()
        #         .get(
        #             spreadsheetId=SPREADSHEET_ID,
        #             range=f"{SHEET_NAME}!A:E",
        #         )
        #         .execute()
        #     )

        #     df = pd.DataFrame(values["values"])
        #     df.columns = df.iloc[0]
        #     df = df[1:]
        #     return df


        # def add_row_to_gsheet(gsheet_connector, row) -> None:
        #     gsheet_connector.values().append(
        #         spreadsheetId=SPREADSHEET_ID,
        #         range=f"{SHEET_NAME}!A:E",
        #         body=dict(values=row),
        #         valueInputOption="USER_ENTERED",
        #     ).execute()


        # st.set_page_config(page_title="Bug report", page_icon="🐞", layout="centered")

        # st.title("🐞 Bug report!")

        # gsheet_connector = connect_to_gsheet()

        # st.sidebar.write(
        #     f"This app shows how a Streamlit app can interact easily with a [Google Sheet]({GSHEET_URL}) to read or store data."
        # )

        # st.sidebar.write(
        #     f"[Read more](https://docs.streamlit.io/knowledge-base/tutorials/databases/public-gsheet) about connecting your Streamlit app to Google Sheets."
        # )

        # form = st.form(key="annotation")

        # with form:
        #     cols = st.columns((1, 1))
        #     author = cols[0].text_input("Report author:")
        #     bug_type = cols[1].selectbox(
        #         "Bug type:", ["Front-end", "Back-end", "Data related", "404"], index=2
        #     )
        #     comment = st.text_area("Comment:")
        #     cols = st.columns(2)
        #     date = cols[0].date_input("Bug date occurrence:")
        #     bug_severity = cols[1].slider("Bug severity:", 1, 5, 2)
        #     submitted = st.form_submit_button(label="Submit")


        # if submitted:
        #     add_row_to_gsheet(
        #         gsheet_connector,
        #         [[author, bug_type, comment, str(date), bug_severity]],
        #     )
        #     st.success("Thanks! Your bug was recorded.")
        #     st.balloons()

        # expander = st.expander("See all records")
        # with expander:
        #     st.write(f"Open original [Google Sheet]({GSHEET_URL})")
        #     st.dataframe(get_data(gsheet_connector))
        
    st.caption('### All rights reserved. &copy;')
  
