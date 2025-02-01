import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path
import base64

def get_image_as_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Configuração para servir arquivos estáticos
st.set_page_config(
    page_title="✍️ Gerador de Posts para Blog",
    layout="wide"
)

# Configura o diretório de arquivos estáticos
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

from agents.blogpostcreator import BlogPostCreator

with st.sidebar:
    "## ✍️ Gerador de Posts para Blog"

    "### Como usar"

    """
    1. Digite o número de referências web que você deseja usar (Máximo 10).
    2. Digite a palavra-chave para gerar o post do blog.
    3. Clique no botão "Gerar post do blog".
    """
            
    web_references = st.number_input(
        label="Número de referências web",
        max_value=10,
        min_value=1,
        value=3,
    )

    st.divider()

    """
    ### Sobre

    ✍️ O Gerador de Posts para Blog permite que você gere posts otimizados para SEO a partir de palavras-chave. 
    Ele usa referências web de artigos bem ranqueados para gerar seu post. 
    Você pode especificar o número de links web a serem usados, com um máximo de 10.

    Este projeto está em desenvolvimento contínuo.
    """

    st.divider()

    """
    ### Perguntas Frequentes

    #### Como funciona?
    O Gerador de Posts usa referências web dos principais artigos ranqueados para gerar seu post.

    #### As informações geradas são precisas?
    O agente gera informações baseadas nas referências web fornecidas. Recomenda-se verificar as informações geradas.

    #### Quantas referências web posso usar?
    Você pode usar no máximo 10 referências web.
    """

    st.divider()

st.title(" ✍️ Gerador de Posts para Blog ")

with st.form(key="generate_blog_post"):
    keyword = st.text_input(label="Digite uma palavra-chave", placeholder="")
    submitted = st.form_submit_button("Gerar post do blog")
        
if submitted and not keyword:
    st.warning("Por favor, digite uma palavra-chave", icon="⚠️")
        
elif submitted:
    creator = BlogPostCreator(keyword, web_references)       
    response = creator.create_blog_post()

    if response is None or not response:
        st.status("Gerando ... ")    
    elif isinstance(response, Exception):
        st.warning("Ocorreu um erro. Por favor, tente novamente!")
        st.error(response, icon="🚨")
    else:
        if isinstance(response, str):
            # Se houver uma imagem no post, converte para base64
            if "![Capa do artigo]" in response:
                img_path = response.split("![Capa do artigo](")[1].split(")")[0]
                if os.path.exists(img_path):
                    img_base64 = get_image_as_base64(img_path)
                    response = response.replace(
                        f"![Capa do artigo]({img_path})", 
                        f'<img src="data:image/png;base64,{img_base64}" alt="Capa do artigo" style="width:100%"/>'
                    )
            
            st.write("### Post gerado")
            st.markdown(response, unsafe_allow_html=True)
            st.snow()

