# IA Generativa com LangChain, Streamlit, Milvus e OpenAI

## Sobre a Aplicação

Esta aplicação inovadora permite que você envie documentos para o Milvus e interaja com eles através de um assistente
virtual inteligente. Utilizando técnicas avançadas de IA, fornecidas pelo LangChain e OpenAI, você pode fazer perguntas
aos seus documentos e obter respostas rápidas e precisas. Esta funcionalidade transforma a maneira como você acessa e
utiliza informações, tornando o processo mais eficiente e intuitivo.

### Exemplos de Uso

- Consultar Documentos Técnicos: Pergunte sobre especificações, datas de lançamento ou detalhes técnicos de qualquer
  documento técnico armazenado.

- Análise de Relatórios: Extraia insights chave de relatórios financeiros ou operacionais. Pergunte sobre métricas
  específicas ou tendências ao longo do tempo.

- Revisar Contratos: Consulte cláusulas específicas ou termos de contratos legais armazenados no sistema.

## Instalar Docker no Ubuntu

https://docs.docker.com/engine/install/ubuntu/

## Iniciando a Aplicação

`docker-compose up -d`
`docker-compose ps`

## Parando a Aplicação

`docker-compose down`

## Inspecionando a Rede do Docker

`docker network inspect milvus`

## Corrigir no Docker: Got permission denied issue

### Adicione seu usuário ao grupo do Docker

`sudo usermod -aG docker $USER`
`exec su -l $USER`

### Erros de versão

Versão depreciada:

```
    # The class `LLMChain` was deprecated in LangChain 0.1.17 and will be removed in 0.3.0.
    # Use RunnableSequence, e.g., `prompt | llm` instead.
    chain = LLMChain(llm=llm, prompt=chat_template, output_key="answer")
```

Nova versão:

```
chain = chat_template | llm | {"resposta": StrOutputParser()}
```