import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import tempfile
import os


st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)


        # PDF generation function
        def generate_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)

            # Add title
            pdf.cell(0, 10, "WhatsApp Chat Analysis Report", ln=True, align='C')
            pdf.ln(10)

            # Add statistics
            pdf.cell(0, 10, f"Selected User: {selected_user}", ln=True)
            pdf.cell(0, 10, f"Total Messages: {num_messages}", ln=True)
            pdf.cell(0, 10, f"Total Words: {words}", ln=True)
            pdf.cell(0, 10, f"Media Shared: {num_media_messages}", ln=True)
            pdf.cell(0, 10, f"Links Shared: {num_links}", ln=True)
            pdf.ln(10)

            # Save images in temporary directory
            with tempfile.TemporaryDirectory() as tmpdirname:
                # Monthly Timeline Plot
                timeline = helper.monthly_timeline(selected_user, df)
                fig, ax = plt.subplots()
                ax.plot(timeline['time'], timeline['message'], color='green')
                plt.xticks(rotation='vertical')
                timeline_img_path = os.path.join(tmpdirname, "monthly_timeline.png")
                plt.savefig(timeline_img_path)
                plt.close(fig)  # Close the figure to avoid re-plotting issues

                # Add Monthly Timeline Plot to PDF
                pdf.cell(0, 10, "Monthly Timeline:", ln=True)
                pdf.image(timeline_img_path, x=10, w=180)  # Adjust x and w as needed
                pdf.ln(10)

                # Daily Timeline Plot
                daily_timeline = helper.daily_timeline(selected_user, df)
                fig, ax = plt.subplots()
                ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
                plt.xticks(rotation='vertical')
                daily_timeline_img_path = os.path.join(tmpdirname, "daily_timeline.png")
                plt.savefig(daily_timeline_img_path)
                plt.close(fig)

                # Add Daily Timeline Plot to PDF
                pdf.cell(0, 10, "Daily Timeline:", ln=True)
                pdf.image(daily_timeline_img_path, x=10, w=180)
                pdf.ln(10)

                # Most Busy Day Plot
                busy_day = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='purple')
                plt.xticks(rotation='vertical')
                busy_day_img_path = os.path.join(tmpdirname, "busy_day.png")
                plt.savefig(busy_day_img_path)
                plt.close(fig)

                # Add Most Busy Day Plot to PDF
                pdf.cell(0, 10, "Most Busy Day:", ln=True)
                pdf.image(busy_day_img_path, x=10, w=180)
                pdf.ln(10)

                # Most Busy Month Plot
                busy_month = helper.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                plt.xticks(rotation='vertical')
                busy_month_img_path = os.path.join(tmpdirname, "busy_month.png")
                plt.savefig(busy_month_img_path)
                plt.close(fig)

                # Add Most Busy Month Plot to PDF
                pdf.cell(0, 10, "Most Busy Month:", ln=True)
                pdf.image(busy_month_img_path, x=10, w=180)
                pdf.ln(10)

                # WordCloud Plot
                df_wc = helper.create_wordcloud(selected_user, df)
                fig, ax = plt.subplots()
                ax.imshow(df_wc)
                wordcloud_img_path = os.path.join(tmpdirname, "wordcloud.png")
                plt.axis('off')
                plt.savefig(wordcloud_img_path, bbox_inches='tight')
                plt.close(fig)

                # Add WordCloud Plot to PDF
                pdf.cell(0, 10, "WordCloud:", ln=True)
                pdf.image(wordcloud_img_path, x=10, w=180)
                pdf.ln(10)

                # Most Common Words Plot
                most_common_df = helper.most_common_words(selected_user, df)
                fig, ax = plt.subplots()
                ax.barh(most_common_df[0], most_common_df[1])
                plt.xticks(rotation='vertical')
                most_common_words_img_path = os.path.join(tmpdirname, "most_common_words.png")
                plt.savefig(most_common_words_img_path)
                plt.close(fig)

                # Add Most Common Words Plot to PDF
                pdf.cell(0, 10, "Most Common Words:", ln=True)
                pdf.image(most_common_words_img_path, x=10, w=180)
                pdf.ln(10)

                # Emoji Analysis Plot
                emoji_df = helper.emoji_helper(selected_user, df)
                fig, ax = plt.subplots()
                ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
                emoji_img_path = os.path.join(tmpdirname, "emoji_analysis.png")
                plt.savefig(emoji_img_path)
                plt.close(fig)

                # Add Emoji Analysis Plot to PDF
                pdf.cell(0, 10, "Emoji Analysis:", ln=True)
                pdf.image(emoji_img_path, x=10, w=180)
                pdf.ln(10)

                # Save PDF to temporary file
                temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                pdf.output(temp_pdf.name)
                return temp_pdf.name


        # Show statistics in Streamlit
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # Monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity map
        st.title('Activity Map')
        col1, col2 = st.columns(2)
        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # Weekly activity heatmap
        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # Busiest users
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)
            with col1:
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Most common words
        st.title('Most Common Words')
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Emoji analysis
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)  # Fixed: Define emoji_df before using
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
            st.pyplot(fig)

        # PDF Download Button on the Main Page
        st.title("Download Report")
        pdf_path = generate_pdf()
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Download PDF",
                data=pdf_file.read(),
                file_name="chat_analysis_report.pdf",
                mime="application/pdf"
            )