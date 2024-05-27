import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os

from streamlit_extras.add_vertical_space import add_vertical_space
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Milvus

from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback

from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# Carregando variáveis de ambiente primeiro
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', default='')
OPENAI_ID_ORGANIZATION = os.getenv('OPENAI_ORGANIZATION', default='')

MILVUS_HOST = os.getenv('MILVUS_HOST', default='')
MILVUS_PORT = os.getenv('MILVUS_PORT', default='')
MILVUS_COLLECTION = os.getenv('MILVUS_COLLECTION', default='')
MILVUS_DB = os.getenv('MILVUS_DB', default='default')
MILVUS_USER = os.getenv('MILVUS_USER', default='')
MILVUS_PASS = os.getenv('MILVUS_PASS', default='')
MILVUS_URL = os.getenv('MILVUS_URL', default='')

# Configurações de conexão com o Milvus
connection_args = {'uri': f'http://{MILVUS_HOST}:{MILVUS_PORT}', 'token': f'{MILVUS_USER}:{MILVUS_PASS}',
                   'db_name': MILVUS_DB}

# Definição do LLM e criação da instância para embeddings
embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY, openai_organization=OPENAI_ID_ORGANIZATION)

# Descrição na barra lateral
with st.sidebar:
    st.title('IA Generativa')
    st.markdown('''
    ## Sobre
    - **LangChain**: Uma biblioteca para construir aplicativos de linguagem com componentes de linguagem conectáveis.
    - **OpenAI**: Fornece poderosas APIs de IA, incluindo modelos de linguagem como GPT.
    - **Milvus**: Uma plataforma de banco de dados vetorial de alta performance projetada para lidar com grandes volumes de dados vetoriais. 
    Aqui estão os principais motivos pelos quais o MinIO é utilizado como sistema de armazenamento de objetos no Milvus.
    ''')
    add_vertical_space(5)
    st.write('Todos os direitos reservados.')


def db_connect() -> Milvus:
    vector_store = Milvus(
        embedding_function=embeddings,
        connection_args=connection_args,
        collection_name=MILVUS_COLLECTION,
        drop_old=False,
    )

    return vector_store


def get_response(db: Milvus, query: str, k=2):
    docs = db.similarity_search(query=query, k=k)
    docs_page_content = " ".join([d.page_content for d in docs])

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.3,
        api_key=OPENAI_API_KEY,
        openai_organization=OPENAI_ID_ORGANIZATION,
    )

    chat_template = ChatPromptTemplate.from_messages(
        [
            ("user",
             """Você é um assistente especializado em responder perguntas com base em documentos PDF fornecidos.

             Responda à seguinte pergunta: {pergunta}
             Procurando nas seguintes transcrições de PDFs: {docs}

             Use somente informações dos documentos fornecidos para responder à pergunta. Se você não souber a resposta, responda com "Eu não sei".

             Suas respostas devem ser detalhadas, claras e concisas, proporcionando uma experiência de usuário excelente. Se solicitado, simplifique a resposta.
             """
             ),
        ]
    )

    chain = chat_template | llm | {"resposta": StrOutputParser()}

    response = chain.invoke({"pergunta": query, "docs": docs_page_content})

    return response, docs


def main():
    db = db_connect()

    # Título principal
    st.title('CHAT - Converse com seus Documentos!')

    # Descrição motivacional e exemplos de uso
    st.markdown('''
    ### Fale com seus Documentos Armazenados no Milvus

    Utilize nosso assistente virtual para conversar diretamente com seus documentos enviados para nossa base de dados vetorial. Extraia informações importantes e obtenha respostas rápidas e precisas com base nos dados que você forneceu. Aqui estão alguns exemplos de como você pode usar essa funcionalidade:

    - **Consultar Documentos Técnicos**: Pergunte sobre especificações, datas de lançamento ou detalhes técnicos de qualquer documento técnico armazenado.
    - **Análise de Relatórios**: Extraia insights chave de relatórios financeiros ou operacionais. Pergunte sobre métricas específicas ou tendências ao longo do tempo.
    - **Revisar Contratos**: Consulte cláusulas específicas ou termos de contratos legais armazenados no sistema.

    Experimente fazer perguntas como:
    - "Quais são as especificações do produto XYZ mencionadas no documento técnico?"
    - "Qual foi o lucro bruto no relatório financeiro do último trimestre?"
    - "Quais são os principais termos do contrato com o fornecedor ABC?"

    Nosso assistente virtual está aqui para ajudar você a navegar e extrair o máximo valor de seus documentos armazenados no Milvus.
    ''')
    pdf = st.file_uploader('Upload PDF', type='pdf')

    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = "".join(
            page.extract_text() or '' for page in pdf_reader.pages)  # Ajuste para lidar com páginas sem texto
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
        chunks = text_splitter.split_text(text=text)
        db.from_texts(chunks, embedding=embeddings, collection_name=MILVUS_COLLECTION,
                      connection_args=connection_args)

    query = st.text_input('Faça uma pergunta')
    if query:
        with get_openai_callback() as cb:
            response, docs = get_response(db, query)

        st.write(response["resposta"])
        with st.expander("Busca similaridade"):
            st.write(docs)

        st.write('Custo total do uso:')
        st.write(cb)


if __name__ == '__main__':
    main()
