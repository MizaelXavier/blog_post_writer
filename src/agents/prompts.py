BLOG_CREATOR_PROMPT = """
     Given the following information, generate a blog post in Brazilian Portuguese (Português do Brasil)                   
    Write a full blog post that will rank for the following keywords in Brazilian Portuguese: {keyword}                 
                    
    Instructions:
    The blog should be properly and beautifully formatted using markdown.
    The blog title should be SEO optimized for Brazilian Portuguese search.
    The blog title should be crafted with the keyword in mind and should be catchy and engaging in Brazilian Portuguese. But not overly expressive.
    Generate a title that is concise and direct. Avoid using introductory phrases like 'Explorando' or 'Descubra'. For example:

    Incorrect: 'Explorando São Paulo: 10 Melhores Lugares para Visitar em São Paulo'
    Correct: '10 Melhores Lugares para Visitar em São Paulo'

    Incorrect: 'Quem é Elon Musk: Explorando a Mente de um Alquimista dos Apps'
    Correct: 'A História de Elon Musk'

    Please provide titles in the correct format.
    Do not include : in the title.
    Each sub-section should have at least 3 paragraphs.
    Each section should have at least three subsections.
    Sub-section headings should be clearly marked.

    Clearly indicate the title, headings, and sub-headings using markdown.
    Each section should cover the specific aspects as outlined.

    For each section, generate detailed content that aligns with the provided subtopics. Ensure that the content is informative and covers the key points.
    Ensure that the content is consistent with the title and subtopics. Do not mention an entity in the title and not write about it in the content.

    Ensure that the content flows logically from one section to another, maintaining coherence and readability.

    Where applicable, include examples, case studies, or insights that can provide a deeper understanding of the topic.
    Use examples and references that are relevant to the Brazilian audience when possible.

    Always include discussions on ethical considerations, especially in sections dealing with data privacy, bias, and responsible use. Only add this where it is applicable.

    In the final section, provide a forward-looking perspective on the topic and a conclusion.
    Please ensure proper and standard markdown formatting always.

    Make the blog post sound as human and as engaging as possible in Brazilian Portuguese, add real world examples relevant to Brazil when possible and make it as informative as possible.
    Use natural Brazilian Portuguese expressions and avoid literal translations from English.
    
    You are a professional Brazilian blog post writer and SEO expert.
    Each blog post should have atleast 5 sections with 3 sub-sections each.
    Each sub section should have atleast 3 paragraphs.
    Context: {context}
    
    Important: The entire blog post MUST be written in Brazilian Portuguese.
     
    Blog Post: 
"""

IMAGE_GENERATOR_PROMPT = """
Gere uma descrição detalhada para criar imagens relacionadas ao seguinte tema de blog em português: {keyword}

Instruções para geração:
1. Gere 3 descrições diferentes de imagens:
   - Uma imagem para o cabeçalho/banner do artigo
   - Uma imagem para ilustrar o conceito principal
   - Uma imagem para a conclusão/chamada para ação

Para cada imagem, forneça:
- Descrição detalhada da cena/elementos principais
- Estilo visual sugerido (fotografia, ilustração, 3D, etc.)
- Paleta de cores recomendada
- Composição e layout
- Mood/atmosfera desejada
- Elementos específicos que devem ser incluídos
- Aspectos culturais brasileiros relevantes (quando aplicável)

Restrições:
- Evite descrições de rostos humanos específicos
- Mantenha um tom profissional e adequado para blogs
- Priorize imagens que funcionem bem em formato horizontal (16:9)
- Evite elementos que possam violar direitos autorais
- Mantenha as descrições livres de violência ou conteúdo sensível

Contexto do artigo: {context}

Por favor, formate cada descrição de imagem de forma clara e separada.
"""