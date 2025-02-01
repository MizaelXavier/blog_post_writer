import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
import requests
from datetime import datetime

# Encontra o arquivo .env no diretório raiz do projeto
root_dir = Path(__file__).parent.parent.parent
env_path = root_dir / '.env'

# Carrega as variáveis de ambiente
load_dotenv(dotenv_path=env_path)

# Configuração do cliente OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def salvar_imagem(url, nome):
    response = requests.get(url)
    if response.status_code == 200:
        directory = "blogs/images"
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        filepath = os.path.join(directory, f"{nome}.png")
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Imagem salva como {filepath}")
    else:
        print(f"Erro ao baixar imagem: {response.status_code}")

def gerar_imagem(descricao):
    try:
        response = client.images.generate(
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

def gerar_descricoes_e_imagens(keyword, context):
    prompt = f"""
    Gere uma descrição curta e objetiva em inglês para criar uma imagem relacionada ao seguinte tema: {keyword}

    A descrição deve ser focada em elementos visuais concretos, evitando conceitos abstratos.
    Mantenha a descrição em até 3 linhas.
    Foque em uma cena única e clara.

    Contexto do artigo: {context}
    """

    try:
        # Gera a descrição
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        descricao = response.choices[0].message.content
        print("\nDescrição gerada:", descricao)
        
        # Gera a imagem usando a descrição
        url_imagem = gerar_imagem(descricao)
        if url_imagem:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"deepseek_{timestamp}"
            salvar_imagem(url_imagem, nome_arquivo)
            print("\nURL da imagem:", url_imagem)
        
    except Exception as e:
        print(f"Erro ao gerar descrições e imagens: {e}")

if __name__ == "__main__":
    keyword = "DeepSeek R1: Inovação em Inteligência Artificial"
    context = """DeepSeek R1 é uma solução avançada em IA agora disponível no Azure AI Foundry e GitHub. 
    É um modelo de raciocínio que utiliza múltiplas passagens de inferência para gerar respostas, 
    demonstrando capacidades avançadas de processamento e análise."""
    
    gerar_descricoes_e_imagens(keyword, context) 