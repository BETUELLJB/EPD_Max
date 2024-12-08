from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

# Carregar o modelo e o tokenizador
model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")

# Texto em Português
text_pt = """
A inteligência artificial está mudando rapidamente a maneira como vivemos e trabalhamos. As inovações tecnológicas estão transformando setores inteiros, desde a medicina até a educação, criando novas oportunidades e desafios. No entanto, com esse avanço, surgem questões éticas e sociais que precisam ser discutidas e resolvidas. A implementação da IA pode trazer benefícios, mas também pode gerar impactos negativos, como o desemprego e a desigualdade. Portanto, é importante encontrar um equilíbrio entre os benefícios e os riscos dessa tecnologia para garantir que ela seja usada de maneira responsável e justa.
"""

# Traduzir de Português para Inglês
tokenizer.src_lang = "pt_XX"  # Idioma de origem: Português
encoded_pt = tokenizer(text_pt, return_tensors="pt")

generated_tokens_pt_to_en = model.generate(
    **encoded_pt,
    forced_bos_token_id=tokenizer.lang_code_to_id["en_XX"]  # Forçar idioma de destino: Inglês
)
translation_pt_to_en = tokenizer.batch_decode(generated_tokens_pt_to_en, skip_special_tokens=True)
print("Tradução do Português para o Inglês:", translation_pt_to_en[0])

# Traduzir de volta de Inglês para Português
tokenizer.src_lang = "en_XX"  # Idioma de origem: Inglês
encoded_en = tokenizer(translation_pt_to_en[0], return_tensors="pt")

generated_tokens_en_to_pt = model.generate(
    **encoded_en,
    forced_bos_token_id=tokenizer.lang_code_to_id["pt_XX"]  # Forçar idioma de destino: Português
)
translation_en_to_pt = tokenizer.batch_decode(generated_tokens_en_to_pt, skip_special_tokens=True)
print("Tradução de volta do Inglês para o Português:", translation_en_to_pt[0])
