import streamlit as st
import openai
import base64

# Configurazione login semplice
PASSWORD = "skipper2025"

# Funzione login
def check_password():
    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Inserisci password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Inserisci password:", type="password", on_change=password_entered, key="password")
        st.error("Password errata.")
        return False
    else:
        return True

# App principale
if check_password():

    st.title("Estrazione Tabelle PDF Skipper")
    st.write("Versione 1.0 - Luglio 2025")

    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    uploaded_file = st.file_uploader("Carica il PDF della richiesta d'offerta:", type=["pdf"])

    if uploaded_file:
        file_bytes = uploaded_file.read()
        base64_pdf = base64.b64encode(file_bytes).decode('utf-8')

        prompt = """
        Ricevi un PDF di una richiesta d'offerta.
        Estrai la tabella materiali seguendo queste regole:
        1. Prima riga: R. OFF. N.[numero richiesta] – [nome gestore]
        2. Intestazione: Posizione\tCodice Prodotto\tQuantità\tDescrizione Materiale\tData Consegna
        3. Righe materiali tabulate pronte per Excel
        4. Se non ci sono materiali, scrivi: ⚠ Nessuna riga materiali trovata.

        Restituisci il risultato pronto per copia/incolla in Excel.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sei un assistente esperto di estrazione tabelle da PDF."},
                {"role": "user", "content": prompt},
                {"role": "user", "content": f"PDF base64: {base64_pdf}"}
            ],
            max_tokens=2000,
            temperature=0.2,
        )

        tabella_estratta = response.choices[0].message.content

        st.success("Tabella estratta correttamente!")
        st.text_area("Tabella (copia e incolla in Excel):", tabella_estratta, height=400)

        txt_download = tabella_estratta.encode('utf-8')
        st.download_button("Scarica Tabella (.txt)", txt_download, file_name="tabella_estratta.txt")
