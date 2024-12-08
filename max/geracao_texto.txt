from transformers import MarianMTModel, MarianTokenizer

# Carregar o tokenizer e o modelo Helsinki-NLP/opus-mt-mul-en
model_name = "Helsinki-NLP/opus-mt-mul-en"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# Exemplo de frase mais longa em português (com cerca de 50 tokens)
text_pt = """
A inteligência artificial está transformando o mundo de várias maneiras. Ela está sendo aplicada em diversos campos, como medicina, 
educação, transporte e muitas outras áreas. No setor da saúde, por exemplo, está ajudando a melhorar diagnósticos e tratamentos. 
Na educação, está personalizando o aprendizado para os estudantes. No transporte, está melhorando a segurança e a eficiência 
com veículos autônomos. De fato, a IA tem o potencial de revolucionar o modo como vivemos e trabalhamos.
"""

# Tokenizar o texto em português
batch = tokenizer([text_pt], return_tensors="pt", padding=True)

# Gerar tradução para inglês
translated = model.generate(**batch)

# Decodificar a tradução
translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
print(translated_text)
