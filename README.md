# BetBot

BetBot é um bot de Discord automatizado que permite aos usuários realizar apostas esportivas de forma fácil e interativa.

----

## Instalação

Siga os passos abaixo para configurar o ambiente e instalar as dependências do BetBot.

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/betbot.git
   ```

2. Navegue até o diretório do projeto:

   ```bash
   cd betbot
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Crie o schema do banco de dados:

   Execute o script SQL `apostas_db.sql` para criar as tabelas necessárias no banco de    dados. 

---

## Executando o BetBot

1. Crie um arquivo sobre o nome `.env` no diretório principal do repositório

2. Certifique-se de que o arquivo `.env` está configurado corretamente com as variáveis de ambiente necessárias. O arquivo `.env` deve conter:

   ```bash
   DISCORD_TOKEN=seu_token_do_discord
   BOT_ID=seu_bot_id
   HOST=seu_host_mysql
   USER=seu_usuario_mysql
   PASSWORD=sua_senha_mysql
   DATABASE=seu_banco_de_dados_mysql
   ```

3. Inicie o bot:

   ```bash
   python bot.py
   ```

---

#### Exemplo de `.env`
   
   ```bash
   DISCORD_TOKEN=abcd1234efgh5678ijkl
   BOT_ID=123456789012345678
   HOST=localhost
   USER=bot_user
   PASSWORD=secure_password
   DATABASE=betbot
   ```

---

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## Autores

- **Thiago Ferreira dos Santos** - *Autor principal e desenvolvimento completo* - [GitHub](https://github.com/haterkkj)

---