import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL                 import Image
from io                  import BytesIO
import timeit


# Set no tema do seaborn para melhorar o visual dos plots
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data


@st.cache_data(show_spinner=True)
def load_data(file_name):
    try:
        return pd.read_excel(file_name)
    except:
        return pd.read_csv(file_name, sep=';')

@st.cache_data()
def multiselect_filter(df, col, selecionados):
    if 'all' in selecionados:
        return df
    else:
        return df[df[col].isin(selecionados)].reset_index(drop=True)


def main():
    st.set_page_config(page_title='Marketing Analysis',
    page_icon=r"telmarketing_icon.png",
    layout='wide',
    initial_sidebar_state='expanded'
    )


    st.write('Bank Marketing Analysis')
    st.markdown('---')


    image = Image.open(r"Bank-Branding.jpg")
    st.sidebar.image(image)
    st.sidebar.write("Upload the file:")
    data_file1 = st.sidebar.file_uploader('Bank marketing data', type = ['csv', 'xlsx'])


    if (data_file1 is not None):
        start = timeit.default_timer()
        bank_data = load_data(data_file1)
        bank = bank_data.copy()

        
        st.write("Data before filters: ")
        st.write(bank_data.head())
        st.write("Exec. time was:", timeit.default_timer() - start)
        

        with st.sidebar.form(key="My form"):
            graph_type =  st.radio('Tipo de gráfico: ', ('Barras', 'Pizza'))
        
        
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider(label = 'Idade',
                            min_value=min_age,
                            max_value=max_age,
                            value=(min_age, max_age),
                            step=1)
            

            jobslist = bank.job.unique().tolist()
            jobslist.append('all')
            jobs_selected = st.multiselect('Profissão: ', jobslist, ['all'])

            marital_list = bank.marital.unique().tolist()
            marital_list.append('all')
            marital_selected = st.multiselect('Estado civil: ', marital_list, ['all'])

            education_list = bank.education.unique().tolist()
            education_list.append('all')
            education_selected = st.multiselect('Education: ', education_list, ['all'])

            default_list = bank.default.unique().tolist()
            default_list.append('all')
            default_selected = st.multiselect('Estado do default: ', default_list, ['all'])

            housing_list = bank.housing.unique().tolist()
            housing_list.append('all')
            housing_selected = st.multiselect('Tipo de moradia: ', housing_list, ['all'])

            loan_list = bank.loan.unique().tolist()
            loan_list.append('all')
            loan_selected = st.multiselect('Empréstimo ativo: ', loan_list, ['all'])

            contact_list = bank.contact.unique().tolist()
            contact_list.append('all')
            contact_selected = st.multiselect('Tipo de contato: ', contact_list, ['all'])

            month_list = bank.month.unique().tolist()
            month_list.append('all')
            month_selected = st.multiselect('Mês de contato: ', month_list, ['all'])

            day_list = bank.day_of_week.unique().tolist()
            day_list.append('all')
            day_selected = st.multiselect('Dia de contato: ', day_list, ['all'])

            bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                        .pipe(multiselect_filter, 'job', jobs_selected)
                        .pipe(multiselect_filter, 'marital', marital_selected)
                        .pipe(multiselect_filter, 'default', default_selected)
                        .pipe(multiselect_filter, 'housing', housing_selected)
                        .pipe(multiselect_filter, 'loan', loan_selected)
                        .pipe(multiselect_filter, 'contact', contact_selected)
                        .pipe(multiselect_filter, 'month', month_selected)
                        .pipe(multiselect_filter, 'day_of_week', day_selected)
            )

            submit_button  = st.form_submit_button(label="Aplicar")
        
        st.write('After filter:')
        st.write(bank.head())


        df_xlsx = to_excel(bank)

        st.download_button(label='📥 Download tabela filtrada em EXCEL',
                                data=df_xlsx ,
                                file_name= 'bank_filtered.xlsx')
        st.markdown('---')

        # Fig_plots:
        fig, ax = plt.subplots(1,2, figsize = (5,3))
        bank_raw_target_perc = bank_data.y.value_counts(normalize=True).to_frame()*100
        bank_raw_target_perc = bank_raw_target_perc.reset_index()

        try:
            bank_target_perc = bank.y.value_counts(normalize=True).to_frame()*100
            bank_target_perc = bank_target_perc.reset_index()
        except:
            st.error('Erro no filtro')

        # Divisão em colunas:
        col1, col2 = st.columns(2)
        df_xlsx = to_excel(bank_raw_target_perc)
        col1.write('### Proporção original: ')
        col1.write(bank_raw_target_perc)
        col1.download_button(label = 'Download ',
                            data = df_xlsx,
                            file_name='bank_raw_y.xlsx')

        df_xlsx = to_excel(bank_target_perc)
        col2.write('### Proporção pós filtros: ')
        col2.write(bank_target_perc)
        col2.download_button(label = 'Download',
                            data = df_xlsx,
                            file_name='bank_y.xlsx')

        st.markdown('---')


        # Gráficos:

        if graph_type == 'Pizza':
            bank_raw_target_perc.plot(kind='pie', ax=ax[0], legend=False,
                labels = bank_raw_target_perc.y, y='proportion')
            ax[0].set_title('Dados brutos')
            bank_target_perc.plot(kind='pie', ax=ax[1], legend=False,
                labels = bank_target_perc.y, y = 'proportion')
            ax[1].set_title('Dados filtrados')
        else:
            sns.barplot(x=bank_raw_target_perc.y, y = 'proportion', ax = ax[0], data=bank_raw_target_perc)
            ax[0].bar_label(ax[0].containers[0])
            ax[0].set_title('Dados brutos')

            sns.barplot(x=bank_target_perc.y, y = 'proportion', ax = ax[1], data=bank_target_perc)
            ax[1].bar_label(ax[1].containers[0])
            ax[1].set_title('Dados filtrados')

        plt.tight_layout()
        st.pyplot(plt)

if __name__ == '__main__':
    main()

