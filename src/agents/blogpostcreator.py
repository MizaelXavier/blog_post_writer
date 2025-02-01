import os
import re
from dotenv import load_dotenv
import requests
from datetime import datetime
from pathlib import Path
from openai import OpenAI
import time

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .prompts import BLOG_CREATOR_PROMPT


class BlogPostCreator:
    def __init__(self, keyword, number_of_web_references):
        self.keyword = keyword
        self.number_of_web_references = number_of_web_references
        # Usa a chave da API do arquivo .env
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def parse_links(self, search_results: str):
        print("-----------------------------------")
        print("Parsing links ...")
        return re.findall(r'link:\s*(https?://[^\],\s]+)', search_results)

    def save_file(self, content: str, filename: str):
        print("-----------------------------------")
        print("Saving file in blogs ...")
        directory = "blogs"
        if not os.path.exists(directory):
            os.makedirs(directory)
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f" 🥳 File saved as {filepath}")

    def get_links(self):
        try:
            print("-----------------------------------")
            print("Getting links ...")

            max_retries = 3
            delay_seconds = 2
            links = []

            for attempt in range(max_retries):
                try:
                    wrapper = DuckDuckGoSearchAPIWrapper(max_results=self.number_of_web_references)
                    search = DuckDuckGoSearchResults(api_wrapper=wrapper)
                    results = search.run(tool_input=self.keyword)

                    links = self.parse_links(results)
                    if links:
                        return links

                except Exception as e:
                    print(f"Tentativa {attempt + 1} falhou: {e}")
                    if attempt < max_retries - 1:
                        print(f"Aguardando {delay_seconds} segundos antes da próxima tentativa...")
                        time.sleep(delay_seconds)
                        delay_seconds *= 2  # Aumenta o tempo de espera a cada tentativa
                    continue

            # Se não conseguiu links após todas as tentativas, use um contexto padrão
            if not links:
                print("Não foi possível obter links. Usando contexto padrão...")
                return ["https://en.wikipedia.org/wiki/" + self.keyword.replace(" ", "_")]

            return links

        except Exception as e:
            print(f"Erro ao obter links: {e}")
            return ["https://en.wikipedia.org/wiki/" + self.keyword.replace(" ", "_")]

    def create_blog_post(self):
        try:
            print("-----------------------------------")
            print("Creating blog post ...")

            # Define docs variable
            docs = []

            # Define splitter variable
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=400,
                add_start_index=True,
            )

            # Load documents
            bs4_strainer = bs4.SoupStrainer(('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'))

            links = self.get_links()
            if not links:
                raise Exception("Não foi possível obter links para pesquisa")

            document_loader = WebBaseLoader(
                web_path=links
            )
            
            docs = document_loader.load()

            # Split documents
            splits = splitter.split_documents(docs)

            # step 3: Indexing and vector storage
            vector_store = FAISS.from_documents(documents=splits, embedding=OpenAIEmbeddings())

            # step 4: retrieval
            retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

            # Obtém o contexto para a geração da imagem
            context_docs = retriever.get_relevant_documents(self.keyword)
            context = "\n".join(doc.page_content for doc in context_docs)

            # Gera e salva a imagem primeiro
            print("Generating image description...")
            descricao = self.gerar_descricao_imagem(context)
            
            imagem_markdown = ""
            if descricao:
                print("Generating image from description...")
                url_imagem = self.gerar_imagem(descricao)
                
                if url_imagem:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nome_arquivo = f"cover_{timestamp}"
                    imagem_path = self.salvar_imagem(url_imagem, nome_arquivo)
                    
                    if imagem_path:
                        # Usa o caminho completo da imagem
                        imagem_markdown = f"![Capa do artigo]({imagem_path})\n\n"

            # Atualiza o retriever para usar mais documentos para o conteúdo do blog
            retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 10})

            # step 5 : Generation
            prompt = PromptTemplate.from_template(template=BLOG_CREATOR_PROMPT)

            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)

            chain = (
                    {"context": retriever | format_docs, "keyword": RunnablePassthrough()}
                    | prompt
                    | self.llm
                    | StrOutputParser()
            )
            
            # Gera o conteúdo do blog
            blog_content = chain.invoke(input=self.keyword)
            
            # Adiciona a imagem no início do conteúdo
            if imagem_markdown:
                blog_content = imagem_markdown + blog_content

            return blog_content

        except Exception as e:
            print(f"Erro detalhado: {str(e)}")
            return e

    def gerar_imagem(self, descricao):
        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=descricao,
                size="1792x1024",
                quality="standard",
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            print(f"Erro ao gerar imagem: {e}")
            return None

    def salvar_imagem(self, url, nome):
        response = requests.get(url)
        if response.status_code == 200:
            # Cria o diretório de imagens dentro da pasta blogs
            directory = "blogs/images"
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            filepath = os.path.join(directory, f"{nome}.png")
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Retorna o caminho relativo para uso no markdown
            return filepath
        return None

    def gerar_descricao_imagem(self, context):
        prompt = f"""
        Carefully analyze the provided context and generate a description for a minimalist and impactful image.

        IMAGE STRUCTURE:
        1. A single central symbolic element that represents the essence of the theme
        2. Solid contrasting background
        3. Clean composition without text

        DESIGN GUIDELINES:
        - Extreme simplicity: one symbol, one message
        - Golden ratio positioning
        - Abundant negative space (at least 40% of composition)
        - Dramatic scale of main element
        - NO text or typography elements

        VISUAL TREATMENT:
        - Colors: exactly 2 high-impact colors
        - Primary color: for the main symbol
        - Secondary color: for the background
        - Texture: none
        - Finish: clean and professional
        - Lighting: dramatic and clear

        HIERARCHY:
        1. Symbolic element (80% of visual focus)
        2. Background color (20% of impact)

        REFERENCE STYLE:
        - Modern editorial (The Economist)
        - Corporate minimalism
        - Conceptual design
        - Apple-style simplicity

        Keyword: {self.keyword}
        
        Article context: {context}

        CRITICAL RULES:
        - Choose only ONE symbolic element
        - NO text or typography
        - NO decorative elements
        - NO gradients or complex effects
        - Maintain generous negative space
        - Use only 2 contrasting colors
        - Create clear figure-ground relationship
        - Ensure the symbol is immediately recognizable
        - Make the meaning obvious at first glance

        Additional instructions:
        - Create a photorealistic 3D render
        - Use dramatic lighting with clear shadows
        - Ensure professional quality
        - Make it suitable for editorial use
        - Keep the composition balanced but slightly asymmetrical
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a minimalist art director specialized in high-impact editorial covers, focusing on symbolic imagery without text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating description: {e}")
            return None
